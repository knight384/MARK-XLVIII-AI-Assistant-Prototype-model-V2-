import pytest
import asyncio
import os
import shutil
from pathlib import Path
from core.workflows.models import (
    WorkflowDefinition, WorkflowStepDef, WorkflowStepConfig, NodeType, WorkflowState
)
from core.workflows.store import WorkflowStore
from core.workflows.events import EventBus
from core.workflows.engine import WorkflowEngine

@pytest.fixture
async def workflow_engine():
    db_path = Path("test_workflows.sqlite")
    if db_path.exists():
        os.remove(db_path)
        
    store = WorkflowStore(db_path)
    event_bus = EventBus()
    engine = WorkflowEngine(store, event_bus, worker_count=2)
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
async def test_workflow_engine_execution(workflow_engine):
    engine, store = workflow_engine
    
    wf = WorkflowDefinition(
        name="test_wf",
        steps=[
            WorkflowStepDef(
                step_id="step1",
                name="step1",
                configuration=WorkflowStepConfig(
                    node_type=NodeType.CONDITION,
                    config={"expression": "1 + 1 == 2"}
                )
            ),
            WorkflowStepDef(
                step_id="step2",
                name="step2",
                dependencies=["step1"],
                configuration=WorkflowStepConfig(
                    node_type=NodeType.NOTIFICATION,
                    config={"message": "done"}
                )
            )
        ]
    )
    
    store.save_workflow_def(wf)
    run_id = await engine.submit_workflow(wf.workflow_id, {})
    assert run_id is not None
    
    # Wait for completion
    for _ in range(50):
        run = store.get_run(run_id)
        if run.state == WorkflowState.COMPLETED:
            break
        await asyncio.sleep(0.1)
        
    run = store.get_run(run_id)
    assert run.state == WorkflowState.COMPLETED
    
@pytest.mark.asyncio
async def test_workflow_condition_malicious(workflow_engine):
    engine, store = workflow_engine
    
    wf = WorkflowDefinition(
        name="malicious_wf",
        steps=[
            WorkflowStepDef(
                step_id="step1",
                name="step1",
                configuration=WorkflowStepConfig(
                    node_type=NodeType.CONDITION,
                    config={"expression": "__import__('os').system('echo pwned')"}
                )
            )
        ]
    )
    
    store.save_workflow_def(wf)
    run_id = await engine.submit_workflow(wf.workflow_id, {})
    
    # Wait for completion
    for _ in range(50):
        run = store.get_run(run_id)
        if run.state in [WorkflowState.COMPLETED, WorkflowState.FAILED]:
            break
        await asyncio.sleep(0.1)
        
    run = store.get_run(run_id)
    assert run.state == WorkflowState.FAILED
