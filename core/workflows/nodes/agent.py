import asyncio
from typing import Any, Dict
from core.workflows.nodes.base import BaseNode, NodeExecutionResult
from core.workflows.models import WorkflowStepRun, WorkflowRun
from core.agent.orchestrator import get_default_orchestrator
from core.agent.task import Task
from core.tools.base import CancellationToken

class AgentNode(BaseNode):
    async def execute(self, run: WorkflowRun, step_run: WorkflowStepRun, config: Dict[str, Any]) -> NodeExecutionResult:
        prompt = config.get("prompt", "")
        # Resolve inputs
        for k, v in step_run.inputs.items():
            prompt = prompt.replace(f"{{{{{k}}}}}", str(v))
            
        task = Task(goal=prompt)
        token = CancellationToken()
        orchestrator = get_default_orchestrator()
        
        try:
            await orchestrator._run_task_impl(task, task.goal, token)
            outputs = {"summary": task.summary(), "status": task.status.value}
            return NodeExecutionResult(ok=True, outputs=outputs)
        except Exception as e:
            return NodeExecutionResult(ok=False, error=str(e))
