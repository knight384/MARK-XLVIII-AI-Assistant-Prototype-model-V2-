import ast
from typing import Any, Dict
from core.workflows.nodes.base import BaseNode, NodeExecutionResult
from core.workflows.models import WorkflowStepRun, WorkflowRun

class ConditionNode(BaseNode):
    async def execute(self, run: WorkflowRun, step_run: WorkflowStepRun, config: Dict[str, Any]) -> NodeExecutionResult:
        expression = config.get("expression", "")
        if not expression:
            return NodeExecutionResult(ok=False, error="expression required")
            
        # Safe evaluation
        try:
            # Parse it to ensure it's a simple expression, no calls
            tree = ast.parse(expression, mode='eval')
            for node in ast.walk(tree):
                if isinstance(node, (ast.Call, ast.Attribute, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                    return NodeExecutionResult(ok=False, error="Unsafe expression")
            
            # Simple eval with strictly limited locals
            allowed_locals = dict(step_run.inputs)
            allowed_locals.update({"True": True, "False": False, "None": None})
            result = eval(compile(tree, '<string>', 'eval'), {"__builtins__": {}}, allowed_locals)
            
            return NodeExecutionResult(ok=True, outputs={"result": bool(result)})
        except Exception as e:
            return NodeExecutionResult(ok=False, error=str(e))
