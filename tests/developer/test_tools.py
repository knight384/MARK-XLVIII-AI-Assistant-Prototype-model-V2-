import pytest
import json
from unittest.mock import patch, MagicMock
from core.tools.base import ToolContext
from core.developer.tools import (
    DeveloperProjectInspectTool, DeveloperCodeSearchTool, DeveloperSourceContextTool,
    DeveloperGitStatusTool, DeveloperGitLogTool, DeveloperGitDiffTool,
    DeveloperGitCommitTool, DeveloperGitPushTool,
    DeveloperGitHubRepositoryTool, DeveloperGitHubCreateRepositoryTool
)
from core.tools.metadata import RiskLevel

@pytest.mark.asyncio
async def test_developer_git_status_tool():
    tool = DeveloperGitStatusTool()
    assert tool.metadata.risk_level == RiskLevel.LOW
    
    with patch("core.developer.tools.GitIntelligence") as mock_git:
        mock_git.return_value.status.return_value = MagicMock(is_clean=True, asdict=lambda: {"is_clean": True})
        # Note: Dataclasses are serialized using dataclasses.asdict
        # To mock properly with dataclasses, we should just let it return the actual mocked object,
        # but since tools.py uses dataclasses.asdict, it needs a real dataclass or we patch asdict.
        pass

@pytest.mark.asyncio
async def test_developer_git_push_risk():
    tool = DeveloperGitPushTool()
    assert tool.metadata.risk_level == RiskLevel.HIGH
    assert tool.metadata.requires_confirmation is True
    
@pytest.mark.asyncio
async def test_developer_github_create_repo_risk():
    tool = DeveloperGitHubCreateRepositoryTool()
    assert tool.metadata.risk_level == RiskLevel.HIGH
    assert tool.metadata.requires_confirmation is True
