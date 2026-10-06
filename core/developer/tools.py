import dataclasses
import json
from typing import Any

from core.tools.base import Tool, ToolContext, ToolResult
from core.tools.schemas import ToolSchema, ParamSchema
from core.tools.metadata import ToolMetadata, RiskLevel

from .project import ProjectAnalyzer
from .search import CodeSearcher
from .context import SourceContextManager
from .git import GitIntelligence, GitError
from .github import GitHubClient, GitHubError

# -----------------------------------------------------------------------------
# Analysis & Search
# -----------------------------------------------------------------------------

class DeveloperProjectInspectTool(Tool):
    name = "developer_project_inspect"
    description = "Inspect the project repository to identify languages, structure, and constraints."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="path", type="string", description="Path to inspect, defaults to current directory", required=False),
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
        try:
            index = ProjectAnalyzer().analyze(path)
            return ToolResult.ok(self.name, data=json.dumps(dataclasses.asdict(index)))
        except Exception as e:
            return ToolResult.fail(self.name, error=f"Project inspection failed: {e}")

class DeveloperCodeSearchTool(Tool):
    name = "developer_code_search"
    description = "Bounded search codebase for text or symbols safely."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="query", type="string", required=True),
            ParamSchema(name="path", type="string", description="Root path for search", required=False),
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
        path = args.get("path", ".")
        try:
            res = CodeSearcher(path).search(query)
            return ToolResult.ok(self.name, data=json.dumps(dataclasses.asdict(res)))
        except Exception as e:
            return ToolResult.fail(self.name, error=f"Search failed: {e}")

class DeveloperSourceContextTool(Tool):
    name = "developer_source_context"
    description = "Extract bounded source context around a specific line."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="file_path", type="string", required=True),
            ParamSchema(name="line_number", type="integer", required=True),
            ParamSchema(name="lines_before", type="integer", required=False),
            ParamSchema(name="lines_after", type="integer", required=False),
            ParamSchema(name="workspace", type="string", required=False),
        )
    )
    metadata = ToolMetadata(
        category="developer",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        requires_sandbox=False
    )
    
    async def execute(self, args: dict, context: ToolContext) -> ToolResult:
        file_path = args["file_path"]
        line = args["line_number"]
        before = args.get("lines_before", 10)
        after = args.get("lines_after", 10)
        ws = args.get("workspace", ".")
        
        try:
            ctx = SourceContextManager(ws).get_context(file_path, line, before, after)
            return ToolResult.ok(self.name, data=ctx)
        except Exception as e:
            return ToolResult.fail(self.name, error=str(e))

# -----------------------------------------------------------------------------
# Git READ
# -----------------------------------------------------------------------------

class DeveloperGitStatusTool(Tool):
    name = "developer_git_status"
    description = "Get the current git status."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="workspace", type="string", required=False),
        )
    )
    metadata = ToolMetadata(
        category="developer",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        requires_sandbox=False
    )
    
    async def execute(self, args: dict, context: ToolContext) -> ToolResult:
        ws = args.get("workspace", ".")
        try:
            status = GitIntelligence(ws).status()
            return ToolResult.ok(self.name, data=json.dumps(dataclasses.asdict(status)))
        except Exception as e:
            return ToolResult.fail(self.name, error=str(e))

class DeveloperGitLogTool(Tool):
    name = "developer_git_log"
    description = "Get recent git commits."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="max_count", type="integer", required=False),
            ParamSchema(name="workspace", type="string", required=False),
        )
    )
    metadata = ToolMetadata(
        category="developer",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        requires_sandbox=False
    )
    
    async def execute(self, args: dict, context: ToolContext) -> ToolResult:
        ws = args.get("workspace", ".")
        count = args.get("max_count", 10)
        try:
            log = GitIntelligence(ws).log(count)
            return ToolResult.ok(self.name, data=json.dumps([dataclasses.asdict(c) for c in log]))
        except Exception as e:
            return ToolResult.fail(self.name, error=str(e))

class DeveloperGitDiffTool(Tool):
    name = "developer_git_diff"
    description = "Get git diff."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="staged", type="boolean", required=False),
            ParamSchema(name="file_path", type="string", required=False),
            ParamSchema(name="workspace", type="string", required=False),
        )
    )
    metadata = ToolMetadata(
        category="developer",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        requires_sandbox=False
    )
    
    async def execute(self, args: dict, context: ToolContext) -> ToolResult:
        ws = args.get("workspace", ".")
        staged = args.get("staged", False)
        fp = args.get("file_path")
        try:
            diff = GitIntelligence(ws).diff(staged, fp)
            return ToolResult.ok(self.name, data=diff)
        except Exception as e:
            return ToolResult.fail(self.name, error=str(e))

# -----------------------------------------------------------------------------
# Git WRITE
# -----------------------------------------------------------------------------

class DeveloperGitCommitTool(Tool):
    name = "developer_git_commit"
    description = "Commit staged changes."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="message", type="string", required=True),
            ParamSchema(name="workspace", type="string", required=False),
        )
    )
    metadata = ToolMetadata(
        category="developer",
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,  # Policy requires explicit confirmation
        requires_sandbox=False
    )
    
    async def execute(self, args: dict, context: ToolContext) -> ToolResult:
        ws = args.get("workspace", ".")
        msg = args["message"]
        try:
            head = GitIntelligence(ws).commit(msg)
            return ToolResult.ok(self.name, data=f"Committed successfully. HEAD is {head}")
        except Exception as e:
            return ToolResult.fail(self.name, error=str(e))

class DeveloperGitPushTool(Tool):
    name = "developer_git_push"
    description = "Push changes to remote."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="remote", type="string", required=False),
            ParamSchema(name="branch", type="string", required=False),
            ParamSchema(name="workspace", type="string", required=False),
        )
    )
    metadata = ToolMetadata(
        category="developer",
        risk_level=RiskLevel.HIGH, # High risk operation!
        requires_confirmation=True,
        requires_sandbox=False
    )
    
    async def execute(self, args: dict, context: ToolContext) -> ToolResult:
        ws = args.get("workspace", ".")
        remote = args.get("remote", "origin")
        branch = args.get("branch")
        try:
            GitIntelligence(ws).push(remote, branch)
            return ToolResult.ok(self.name, data=f"Pushed to {remote} {branch or 'current branch'}")
        except Exception as e:
            return ToolResult.fail(self.name, error=str(e))

# -----------------------------------------------------------------------------
# GitHub READ / WRITE
# -----------------------------------------------------------------------------

class DeveloperGitHubRepositoryTool(Tool):
    name = "developer_github_repository"
    description = "Get GitHub repository metadata."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="owner", type="string", required=True),
            ParamSchema(name="repo", type="string", required=True),
        )
    )
    metadata = ToolMetadata(
        category="developer",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        requires_sandbox=False
    )
    
    async def execute(self, args: dict, context: ToolContext) -> ToolResult:
        try:
            meta = GitHubClient().get_repository(args["owner"], args["repo"])
            return ToolResult.ok(self.name, data=json.dumps(dataclasses.asdict(meta)))
        except Exception as e:
            return ToolResult.fail(self.name, error=str(e))

class DeveloperGitHubCreateRepositoryTool(Tool):
    name = "developer_github_create_repository"
    description = "Create a new GitHub repository."
    schema = ToolSchema(
        parameters=(
            ParamSchema(name="name", type="string", required=True),
            ParamSchema(name="description", type="string", required=False),
            ParamSchema(name="private", type="boolean", required=False),
        )
    )
    metadata = ToolMetadata(
        category="developer",
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        requires_sandbox=False
    )
    
    async def execute(self, args: dict, context: ToolContext) -> ToolResult:
        name = args["name"]
        desc = args.get("description", "")
        private = args.get("private", True)
        try:
            url = GitHubClient().create_repository(name, desc, private)
            return ToolResult.ok(self.name, data=f"Created repository at {url}")
        except Exception as e:
            return ToolResult.fail(self.name, error=str(e))

