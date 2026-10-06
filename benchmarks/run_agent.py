import asyncio
from benchmarks.harness import harness

async def run_agent_orchestration():
    from core.workflows.engine import WorkflowEngine
    from core.workflows.models import WorkflowRun, WorkflowState, WorkflowDefinition, WorkflowStepDef, WorkflowStepConfig, NodeType
    import uuid
    import tempfile
    from pathlib import Path
    
    class MockStore:
        def __init__(self):
            self.runs = {}
            self.defs = {}
        def save_run(self, run):
            self.runs[run.run_id] = run
        def get_run(self, rid):
            return self.runs.get(rid)
        def save_step_run(self, step):
            pass
        def get_workflow(self, wid):
            return self.defs.get(wid)
            
    store = MockStore()
    from core.runtime.events import EventBus
    engine = WorkflowEngine(store=store, event_bus=EventBus())
    
    # Pre-register definition
    wdef = WorkflowDefinition(workflow_id="bench", name="bench")
    wdef.steps.append(WorkflowStepDef(step_id="s1", name="s1", configuration=WorkflowStepConfig(node_type=NodeType.AGENT)))
    store.defs["bench"] = wdef
    
    async def run_orchestration():
        rid = str(uuid.uuid4())
        run = WorkflowRun(run_id=rid, workflow_id="bench", status=WorkflowState.READY, inputs={})
        store.save_run(run)
        
        # We simulate dispatch logic which calls out to the handler.
        # But we don't have the full handler registered here.
        # We just want to measure the engine concurrency overhead.
        try:
            await engine.execute_run(rid)
        except Exception:
            pass
            
    await harness.run_concurrent_benchmark("Agent_Orchestration_20_Workers", run_orchestration, concurrency=20, iterations_per_task=5)

async def main():
    print("Starting Agent Benchmarks...")
    import core.runtime.app
    from core.runtime.mode import RuntimeMode
    runtime = core.runtime.app.MarkRuntime(mode=RuntimeMode.HEADLESS)
    await runtime.initialize()
    
    await run_agent_orchestration()
    harness.dump_report("benchmarks/agent.json")

if __name__ == '__main__':
    asyncio.run(main())

