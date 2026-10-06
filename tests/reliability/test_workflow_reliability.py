import pytest
import asyncio
import os
from pathlib import Path
from core.workflows.models import (
    WorkflowDefinition, WorkflowStepDef, WorkflowStepConfig, NodeType, WorkflowState, StepState
)
from core.workflows.store import WorkflowStore
from core.workflows.events import EventBus
from core.workflows.engine import WorkflowEngine

@pytest.fixture
async def workflow_engine():
    db_path = Path("test_rel_workflows.sqlite")
    if db_path.exists():
        os.remove(db_path)
        
    store = WorkflowStore(db_path)
    event_bus = EventBus()
    engine = WorkflowEngine(store, event_bus, worker_count=4)
    event_bus.start()
    await engine.start()
    
    yield engine, store
    
    await engine.stop()
    await event_bus.stop()
    store.close()
    if db_path.exists():
        try:
            os.remove(db_path)
        except Exception:
            pass
        try:
            os.remove(f"{db_path}-wal")
            os.remove(f"{db_path}-shm")
        except Exception:
            pass

@pytest.mark.asyncio
async def test_workflow_concurrency(workflow_engine):
    engine, store = workflow_engine
    
    wf = WorkflowDefinition(
        name="concurrent_wf",
        steps=[
            WorkflowStepDef(
                step_id="step1",
                name="step1",
                configuration=WorkflowStepConfig(
                    node_type=NodeType.CONDITION,
                    config={"expression": "True"}
                )
            )
        ]
    )
    store.save_workflow_def(wf)
    
    # Submit 10 concurrent workflows
    run_ids = []
    for _ in range(10):
        run_id = await engine.submit_workflow(wf.workflow_id, {})
        run_ids.append(run_id)
        
    # Wait for all to complete
    completed = 0
    for _ in range(100):
        completed = 0
        for run_id in run_ids:
            run = store.get_run(run_id)
            if run.state == WorkflowState.COMPLETED:
                completed += 1
        if completed == 10:
            break
        await asyncio.sleep(0.1)
        
    assert completed == 10

@pytest.mark.asyncio
async def test_workflow_recovery():
    db_path = Path("test_rel_rec_workflows.sqlite")
    if db_path.exists():
        os.remove(db_path)
        
    store = WorkflowStore(db_path)
    
    wf = WorkflowDefinition(
        name="rec_wf",
        steps=[
            WorkflowStepDef(
                step_id="step1",
                name="step1",
                configuration=WorkflowStepConfig(
                    node_type=NodeType.CONDITION,
                    config={"expression": "True"}
                )
            )
        ]
    )
    store.save_workflow_def(wf)
    
    # Simulate a crash where a step is stuck in RUNNING
    from core.workflows.models import WorkflowRun, WorkflowStepRun, WorkflowEvent, EventType
    run = WorkflowRun(workflow_id=wf.workflow_id, inputs={}, state=WorkflowState.RUNNING)
    store.save_run(run, [])
    step = WorkflowStepRun(workflow_run_id=run.run_id, step_id="step1", state=StepState.RUNNING, inputs={})
    store.save_step_run(step, [])
    store.close()
    
    # Now start engine, it should recover the step and complete it
    store2 = WorkflowStore(db_path)
    event_bus = EventBus()
    engine = WorkflowEngine(store2, event_bus, worker_count=2)
    event_bus.start()
    await engine.start()
    
    for _ in range(50):
        r = store2.get_run(run.run_id)
        if r.state == WorkflowState.COMPLETED:
            break
        await asyncio.sleep(0.1)
        
    r = store2.get_run(run.run_id)
    assert r.state == WorkflowState.COMPLETED
    
    await engine.stop()
    await event_bus.stop()
    store2.close()
    if db_path.exists():
        try:
            os.remove(db_path)
        except Exception:
            pass
        try:
            os.remove(f"{db_path}-wal")
            os.remove(f"{db_path}-shm")
        except Exception:
            pass

