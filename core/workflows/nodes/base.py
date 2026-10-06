import abc
from typing import Any, Dict
from core.workflows.models import WorkflowStepRun, WorkflowRun

class NodeExecutionResult:
    def __init__(self, ok: bool, outputs: Dict[str, Any] = None, error: str = None, waiting: bool = False):
        self.ok = ok
        self.outputs = outputs or {}
        self.error = error
        self.waiting = waiting

class BaseNode(abc.ABC):
    @abc.abstractmethod
    async def execute(self, run: WorkflowRun, step_run: WorkflowStepRun, config: Dict[str, Any]) -> NodeExecutionResult:
        pass
