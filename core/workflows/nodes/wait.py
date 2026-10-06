from typing import Any, Dict
from core.workflows.nodes.base import BaseNode, NodeExecutionResult
from core.workflows.models import WorkflowStepRun, WorkflowRun

class WaitNode(BaseNode):
    async def execute(self, run: WorkflowRun, step_run: WorkflowStepRun, config: Dict[str, Any]) -> NodeExecutionResult:
        # Instead of sleeping, we return waiting=True so the engine can persist it
        # and schedule a wakeup event if needed.
        return NodeExecutionResult(ok=True, waiting=True)
