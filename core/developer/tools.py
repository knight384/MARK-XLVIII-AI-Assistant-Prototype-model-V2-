from typing import Any
from core.tools.base import Tool, ToolContext, ToolResult
from core.tools.schemas import ToolSchema, ParamSchema
from core.tools.metadata import ToolMetadata, RiskLevel
from core.runtime.events import get_default_bus, RuntimeEvent, EventPriority

from core.developer.project import ProjectAnalyzer

class DeveloperProjectInspectTool(Tool):
    name = "developer_project_inspect"
    description = "Inspect the project repository to identify languages, structure, and test commands."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="path", type="string", description="Path to inspect, defaults to current directory"),
        )
    )
    metadata = ToolMetadata(
        category="developer",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        requires_sandbox=False
    )
    
    async def execute(self, args: dict, context: ToolContext) -> ToolResult:
        path = args.get("path", ".")
        analyzer = ProjectAnalyzer()
        try:
            index = analyzer.analyze(path)
            return ToolResult.ok(self.name, data=str(index.__dict__))
        except Exception as e:
            return ToolResult.fail(self.name, error=f"Project inspection failed: {e}")



class DeveloperCodeSearchTool(Tool):
    name = "developer_code_search"
    description = "Search codebase for text or symbols safely."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="query", type="string", required=True),
        )
    )
    metadata = ToolMetadata(
        category="developer",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        requires_sandbox=False
    )
    
    async def execute(self, args: dict, context: ToolContext) -> ToolResult:
        query = args["query"]
        import os
        results = []
        for root, dirs, files in os.walk("."):
            if any(part in root for part in [".git", "node_modules", "venv", "__pycache__"]):
                continue
            for file in files:
                if file.endswith((".py", ".ts", ".js", ".json", ".md", ".txt", ".java", ".go")):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            for i, line in enumerate(f):
                                if query in line:
                                    results.append(f"{path}:{i+1}: {line.strip()}")
                                    if len(results) >= 50: # Bounded search
                                        results.append("... [Search truncated at 50 results]")
                                        return ToolResult.ok(self.name, data="\n".join(results))
                    except Exception:
                        pass
        return ToolResult.ok(self.name, data="\n".join(results) if results else "No results found.")
