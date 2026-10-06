import asyncio
from typing import Any, Dict
from core.workflows.nodes.base import BaseNode, NodeExecutionResult
from core.workflows.models import WorkflowStepRun, WorkflowRun
from core.tools import get_default_registry, ToolContext, ToolExecutor
from core.tools.base import CancellationToken
from core.policy.engine import get_default_policy_engine
from core.policy.models import PolicyContext, PolicyDecision
from core.channels.manager import ChannelManager
from core.config.secrets import SecretStore

class ToolNode(BaseNode):
    async def execute(self, run: WorkflowRun, step_run: WorkflowStepRun, config: Dict[str, Any]) -> NodeExecutionResult:
        tool_name = config.get("tool_name")
        if not tool_name:
            return NodeExecutionResult(ok=False, error="tool_name is required")
            
        registry = get_default_registry()
        tool = registry.get_tool(tool_name)
        if not tool:
            return NodeExecutionResult(ok=False, error=f"Tool {tool_name} not found")
            
        # Security Boundary: Evaluate policy BEFORE execution
        policy = get_default_policy_engine()
        req = PolicyContext(
            tool_name=tool_name,
            risk_level=tool.risk_level
        )
        decision = policy.evaluate(req)
        if decision.decision == PolicyDecision.DENY:
            return NodeExecutionResult(ok=False, error=f"Policy denial: {decision.reason}")
        if decision.decision == PolicyDecision.APPROVAL_REQUIRED:
            # For now, we fail. Ideally, we pause and wait for ApprovalManager.
            return NodeExecutionResult(ok=False, error="Approval required (not supported inline yet)")
            
        executor = ToolExecutor(registry)
        ctx = ToolContext(
            memory_service=None,
            channel_manager=ChannelManager(),
            secret_store=SecretStore(),
            goal_service=None,
            token=CancellationToken()
        )
        
        try:
            result = await executor.execute(tool_name, step_run.inputs, ctx)
            if result.error:
                return NodeExecutionResult(ok=False, error=result.error)
            return NodeExecutionResult(ok=True, outputs={"result": result.data})
        except Exception as e:
            return NodeExecutionResult(ok=False, error=str(e))
