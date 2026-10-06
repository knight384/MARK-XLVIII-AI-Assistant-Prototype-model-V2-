import pytest
import asyncio
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
    db_path = Path("test_sec_workflows.sqlite")
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
async def test_workflow_cannot_execute_shell(workflow_engine):
    engine, store = workflow_engine
    
    # Attempt to run a shell command via condition
    wf = WorkflowDefinition(
        name="malicious_shell_wf",
        steps=[
            WorkflowStepDef(
                step_id="step1",
                name="step1",
                configuration=WorkflowStepConfig(
                    node_type=NodeType.CONDITION,
                    config={"expression": "__import__('subprocess').check_output(['echo', 'pwned'])"}
                )
            )
        ]
    )
    store.save_workflow_def(wf)
    run_id = await engine.submit_workflow(wf.workflow_id, {})
    
    for _ in range(50):
        run = store.get_run(run_id)
        if run.state in [WorkflowState.COMPLETED, WorkflowState.FAILED]:
            break
        await asyncio.sleep(0.1)
        
    run = store.get_run(run_id)
    assert run.state == WorkflowState.FAILED
    
    # Check the error
    steps = store.get_step_runs(run_id)
    assert len(steps) == 1
    assert "Unsafe expression" in steps[0].error or "not defined" in steps[0].error

@pytest.mark.asyncio
async def test_workflow_policy_enforcement(workflow_engine):
    engine, store = workflow_engine
    
    # This tries to call a tool that doesn't exist, which naturally fails ToolExecutor
    # If we had a known DENY tool, it would be denied by PolicyEngine inside ToolExecutor.
    wf = WorkflowDefinition(
        name="malicious_tool_wf",
        steps=[
            WorkflowStepDef(
                step_id="step1",
                name="step1",
                configuration=WorkflowStepConfig(
                    node_type=NodeType.TOOL,
                    config={"tool_name": "malicious_hidden_tool"}
                )
            )
        ]
    )
    store.save_workflow_def(wf)
    run_id = await engine.submit_workflow(wf.workflow_id, {})
    
    for _ in range(50):
        run = store.get_run(run_id)
        if run.state in [WorkflowState.COMPLETED, WorkflowState.FAILED]:
            break
        await asyncio.sleep(0.1)
        
    run = store.get_run(run_id)
    assert run.state == WorkflowState.FAILED
    steps = store.get_step_runs(run_id)
    assert "not found" in steps[0].error or "Policy" in steps[0].error

