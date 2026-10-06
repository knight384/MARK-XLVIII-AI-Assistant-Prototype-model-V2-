from typing import Any, Dict
from core.workflows.nodes.base import BaseNode, NodeExecutionResult
from core.workflows.models import WorkflowStepRun, WorkflowRun
import logging

logger = logging.getLogger(__name__)

class NotificationNode(BaseNode):
    async def execute(self, run: WorkflowRun, step_run: WorkflowStepRun, config: Dict[str, Any]) -> NodeExecutionResult:
        message = config.get("message", "")
        for k, v in step_run.inputs.items():
            message = message.replace(f"{{{{{k}}}}}", str(v))
        
        logger.info(f"[Workflow Notification] {message}")
        return NodeExecutionResult(ok=True, outputs={"delivered": True})
