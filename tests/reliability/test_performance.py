import pytest
import asyncio
import time
import os
from pathlib import Path
from core.workflows.models import (
    WorkflowDefinition, WorkflowStepDef, WorkflowStepConfig, NodeType, WorkflowState
)
from core.workflows.store import WorkflowStore
from core.workflows.events import EventBus
from core.workflows.engine import WorkflowEngine

@pytest.fixture
async def workflow_engine():
    db_path = Path("test_perf_workflows.sqlite")
    if db_path.exists():
        os.remove(db_path)
        
    store = WorkflowStore(db_path)
    event_bus = EventBus()
    engine = WorkflowEngine(store, event_bus, worker_count=10)
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
async def test_performance_metrics(workflow_engine):
    engine, store = workflow_engine
    
    wf = WorkflowDefinition(
        name="perf_wf",
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
    
    start_time = time.time()
    
    # Measure submission latency
    run_ids = []
    for _ in range(50):
        t0 = time.time()
        run_id = await engine.submit_workflow(wf.workflow_id, {})
        run_ids.append(run_id)
        
    submission_time = time.time() - start_time
    avg_submission_latency = submission_time / 50
    
    # Wait for completion
    completed = 0
    while completed < 50:
        completed = sum(1 for run_id in run_ids if store.get_run(run_id).state == WorkflowState.COMPLETED)
        await asyncio.sleep(0.01)
        
    total_time = time.time() - start_time
    throughput = 50 / total_time
    
    print(f"\n--- Performance Results ---")
    print(f"Avg Submission Latency: {avg_submission_latency*1000:.2f} ms")
    print(f"Total Workflow Throughput: {throughput:.2f} workflows/sec")
    print(f"Total Time for 50 Workflows: {total_time:.2f} s")
    
