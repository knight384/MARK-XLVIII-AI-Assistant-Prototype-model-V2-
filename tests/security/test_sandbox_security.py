import pytest
from core.sandbox.manager import SandboxManager
from core.sandbox.errors import SandboxUnavailableError
from core.tools.metadata import RiskLevel

@pytest.mark.asyncio
async def test_sandbox_unavailable_fallback():
    manager = SandboxManager()
    
    # We simulate Docker being unavailable
    manager._docker_available = False
    manager._docker_last_check = 2000000000.0 # Future time to skip probe
    
    try:
        # Should raise SandboxUnavailableError since docker is unavailable and fallback forbidden
        result = manager.execute_command(
            command=["echo", "test"],
            risk_level=RiskLevel.HIGH,
            base_workspace_dir=None
        )
        assert False, "Should have failed to create sandbox"
    except SandboxUnavailableError as e:
        assert "fallback is forbidden in V2" in str(e) or "Docker unavailable" in str(e)
    except Exception as e:
        assert False, f"Unexpected exception: {e}"
