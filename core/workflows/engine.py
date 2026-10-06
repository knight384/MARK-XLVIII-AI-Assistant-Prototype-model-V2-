import asyncio
import time
import logging
from typing import Dict, List, Optional
from core.workflows.models import (
    WorkflowDefinition, WorkflowRun, WorkflowStepRun, WorkflowEvent,
    WorkflowState, StepState, EventType, NodeType, WorkflowStepDef
)
from core.workflows.store import WorkflowStore
from core.workflows.events import EventBus
from core.workflows.nodes.base import BaseNode
from core.workflows.nodes.agent import AgentNode
from core.workflows.nodes.tool import ToolNode
from core.workflows.nodes.condition import ConditionNode
from core.workflows.nodes.wait import WaitNode
from core.workflows.nodes.notification import NotificationNode

logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(self, store: WorkflowStore, event_bus: EventBus, worker_count: int = 4):
        self.store = store
        self.event_bus = event_bus
        self.worker_count = worker_count
        self._running = False
        self._workers: List[asyncio.Task] = []
        self._work_queue = asyncio.Queue(maxsize=1000)
        self._nodes: Dict[NodeType, BaseNode] = {
            NodeType.AGENT: AgentNode(),
            NodeType.TOOL: ToolNode(),
            NodeType.CONDITION: ConditionNode(),
            NodeType.WAIT: WaitNode(),
            NodeType.NOTIFICATION: NotificationNode()
        }

    async def start(self):
        self._running = True
        
        # Subscribe to events
        self.event_bus.subscribe(self._on_workflow_started, EventType.WORKFLOW_STARTED)
        self.event_bus.subscribe(self._on_step_queued, EventType.STEP_QUEUED)
        self.event_bus.subscribe(self._on_step_completed, EventType.STEP_COMPLETED)
        self.event_bus.subscribe(self._on_step_failed, EventType.STEP_FAILED)
        
        # Start workers
        for i in range(self.worker_count):
            task = asyncio.create_task(self._worker_loop(i))
            self._workers.append(task)
            
        # Start outbox pump
        self._outbox_task = asyncio.create_task(self._outbox_pump())
        
        # Recover state
        await self._recover()
        logger.info("[WorkflowEngine] Started.")

    async def stop(self):
        self._running = False
        self._outbox_task.cancel()
        for t in self._workers:
            t.cancel()
        await asyncio.gather(self._outbox_task, *self._workers, return_exceptions=True)
        logger.info("[WorkflowEngine] Stopped.")

    async def _recover(self):
        # Identify orphaned RUNNING steps
        running_steps = self.store.get_step_runs_by_state([StepState.RUNNING, StepState.QUEUED])
        for step in running_steps:
            logger.info(f"Recovering orphaned step {step.step_run_id}")
            # Requeue
            step.state = StepState.QUEUED
            ev = WorkflowEvent(workflow_run_id=step.workflow_run_id, step_run_id=step.step_run_id, event_type=EventType.STEP_QUEUED)
            self.store.save_step_run(step, [ev])

    async def _outbox_pump(self):
        while self._running:
            try:
                events = self.store.pop_outbox_events()
                for ev in events:
                    await self.event_bus.publish(ev)
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Outbox pump error: {e}")
                await asyncio.sleep(2)

    async def submit_workflow(self, workflow_id: str, inputs: Dict[str, Any]) -> Optional[str]:
        wf = self.store.get_workflow_def(workflow_id)
        if not wf or not wf.enabled:
            return None
            
        run = WorkflowRun(workflow_id=workflow_id, inputs=inputs, state=WorkflowState.RUNNING, started_at=time.time())
        ev = WorkflowEvent(workflow_run_id=run.run_id, event_type=EventType.WORKFLOW_STARTED, payload={"inputs": inputs})
        self.store.save_run(run, [ev])
        return run.run_id

    async def _on_workflow_started(self, event: WorkflowEvent):
        run = self.store.get_run(event.workflow_run_id)
        wf = self.store.get_workflow_def(run.workflow_id)
        
        # Find steps with no dependencies
        ready_steps = [s for s in wf.steps if not s.dependencies]
        for s in ready_steps:
            self._queue_step(run, wf, s)

    def _queue_step(self, run: WorkflowRun, wf: WorkflowDefinition, step_def: WorkflowStepDef, step_inputs: Dict = None):
        if step_inputs is None:
            step_inputs = run.inputs # Simple passthrough for now
        
        step_run = WorkflowStepRun(
            workflow_run_id=run.run_id,
            step_id=step_def.step_id,
            state=StepState.QUEUED,
            inputs=step_inputs
        )
        ev = WorkflowEvent(
            workflow_run_id=run.run_id, 
            step_run_id=step_run.step_run_id,
            event_type=EventType.STEP_QUEUED
        )
        self.store.save_step_run(step_run, [ev])

    async def _on_step_queued(self, event: WorkflowEvent):
        await self._work_queue.put(event.step_run_id)

    async def _on_step_completed(self, event: WorkflowEvent):
        # Check dependents
        run = self.store.get_run(event.workflow_run_id)
        if run.state != WorkflowState.RUNNING:
            return
            
        wf = self.store.get_workflow_def(run.workflow_id)
        all_step_runs = self.store.get_step_runs(run.run_id)
        completed_step_ids = {sr.step_id for sr in all_step_runs if sr.state == StepState.COMPLETED}
        
        # Check if workflow is done
        if len(completed_step_ids) == len(wf.steps):
            run.state = WorkflowState.COMPLETED
            run.completed_at = time.time()
            ev = WorkflowEvent(workflow_run_id=run.run_id, event_type=EventType.WORKFLOW_COMPLETED)
            self.store.save_run(run, [ev])
            return

        # Queue new steps
        queued_step_ids = {sr.step_id for sr in all_step_runs}
        for s in wf.steps:
            if s.step_id not in queued_step_ids:
                if all(d in completed_step_ids for d in s.dependencies):
                    # Gather outputs from dependencies
                    step_inputs = dict(run.inputs)
                    for sr in all_step_runs:
                        if sr.step_id in s.dependencies:
                            step_inputs.update(sr.outputs)
                    self._queue_step(run, wf, s, step_inputs)

    async def _on_step_failed(self, event: WorkflowEvent):
        run = self.store.get_run(event.workflow_run_id)
        if run.state == WorkflowState.RUNNING:
            run.state = WorkflowState.FAILED
            run.completed_at = time.time()
            ev = WorkflowEvent(workflow_run_id=run.run_id, event_type=EventType.WORKFLOW_FAILED)
            self.store.save_run(run, [ev])

    async def _worker_loop(self, worker_id: int):
        while self._running:
            try:
                step_run_id = await self._work_queue.get()
                try:
                    await self._execute_step(step_run_id)
                finally:
                    self._work_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Worker {worker_id}] Error: {e}", exc_info=True)

    async def _execute_step(self, step_run_id: str):
        step_run = self.store.get_step_run(step_run_id)
        if not step_run or step_run.state != StepState.QUEUED:
            return
            
        run = self.store.get_run(step_run.workflow_run_id)
        wf = self.store.get_workflow_def(run.workflow_id)
        step_def = next((s for s in wf.steps if s.step_id == step_run.step_id), None)
        if not step_def:
            return
            
        step_run.state = StepState.RUNNING
        step_run.started_at = time.time()
        step_run.attempt += 1
        ev_start = WorkflowEvent(workflow_run_id=run.run_id, step_run_id=step_run.step_run_id, event_type=EventType.STEP_STARTED)
        self.store.save_step_run(step_run, [ev_start])
        
        node = self._nodes.get(step_def.configuration.node_type)
        if not node:
            step_run.state = StepState.FAILED
            step_run.error = f"Unknown node type {step_def.configuration.node_type}"
            step_run.completed_at = time.time()
            ev = WorkflowEvent(workflow_run_id=run.run_id, step_run_id=step_run.step_run_id, event_type=EventType.STEP_FAILED, payload={"error": step_run.error})
            self.store.save_step_run(step_run, [ev])
            return
            
        try:
            result = await node.execute(run, step_run, step_def.configuration.config)
            step_run.completed_at = time.time()
            
            if result.waiting:
                step_run.state = StepState.WAITING
                ev = WorkflowEvent(workflow_run_id=run.run_id, step_run_id=step_run.step_run_id, event_type=EventType.WORKFLOW_WAITING)
                self.store.save_step_run(step_run, [ev])
            elif result.ok:
                step_run.state = StepState.COMPLETED
                step_run.outputs = result.outputs
                ev = WorkflowEvent(workflow_run_id=run.run_id, step_run_id=step_run.step_run_id, event_type=EventType.STEP_COMPLETED, payload=result.outputs)
                self.store.save_step_run(step_run, [ev])
            else:
                step_run.state = StepState.FAILED
                step_run.error = result.error
                ev = WorkflowEvent(workflow_run_id=run.run_id, step_run_id=step_run.step_run_id, event_type=EventType.STEP_FAILED, payload={"error": result.error})
                self.store.save_step_run(step_run, [ev])
        except Exception as e:
            step_run.state = StepState.FAILED
            step_run.error = str(e)
            step_run.completed_at = time.time()
            ev = WorkflowEvent(workflow_run_id=run.run_id, step_run_id=step_run.step_run_id, event_type=EventType.STEP_FAILED, payload={"error": str(e)})
            self.store.save_step_run(step_run, [ev])
