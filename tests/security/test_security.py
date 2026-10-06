"""
tests/security/test_security.py
V2 True Isolation Security Tests
"""
from __future__ import annotations

import os
import shutil
import pytest

from core.sandbox.docker import DockerSandbox
from core.sandbox.limits import ResourceLimits
from core.sandbox.workspace import SandboxWorkspace

DOCKER_AVAILABLE = shutil.which("docker") is not None

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="ENVIRONMENT-LIMITED")
def test_network_isolation_disabled_by_default(tmp_path):
    """Verify that the container cannot reach the internet by default."""
    sandbox = DockerSandbox()
    if not sandbox.is_available():
        pytest.skip("ENVIRONMENT-LIMITED")
    with SandboxWorkspace(base_dir=tmp_path) as ws:
        result = sandbox.execute_command(
            ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://1.1.1.1', timeout=3)"], 
            ws, ResourceLimits(network_enabled=False)
        )
    assert result.success is False
    assert "timeout" in result.stderr.lower() or "unreachable" in result.stderr.lower() or "name or service not known" in result.stderr.lower() or "urllib.error.URLError" in result.stderr

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="ENVIRONMENT-LIMITED")
def test_no_secret_injection(tmp_path):
    """Verify host secrets do not leak into the container."""
    sandbox = DockerSandbox()
    if not sandbox.is_available():
        pytest.skip("ENVIRONMENT-LIMITED")
    
    os.environ["V2_SECRET_TEST"] = "SHOULD_NOT_LEAK"
    try:
        with SandboxWorkspace(base_dir=tmp_path) as ws:
            result = sandbox.execute_command(
                ["python3", "-c", "import os; print(os.environ.get('V2_SECRET_TEST', 'SAFE'))"], 
                ws, ResourceLimits()
            )
        assert result.success is True
        assert "SHOULD_NOT_LEAK" not in result.stdout
        assert "SAFE" in result.stdout
    finally:
        del os.environ["V2_SECRET_TEST"]

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="ENVIRONMENT-LIMITED")
def test_concurrent_execution_isolation(tmp_path):
    """Verify two concurrent executions do not interfere."""
    import threading
    sandbox = DockerSandbox()
    if not sandbox.is_available():
        pytest.skip("ENVIRONMENT-LIMITED")
        
    def run_sandbox(marker: str, results: list):
        with SandboxWorkspace(base_dir=tmp_path) as ws:
            ws.write_file("marker.txt", marker)
            # Sleep slightly to increase chance of overlap if they shared state
            res = sandbox.execute_command(
                ["python3", "-c", "import time; time.sleep(1); print(open('marker.txt').read())"], 
                ws, ResourceLimits()
            )
            results.append(res.stdout.strip())

    results1 = []
    results2 = []
    t1 = threading.Thread(target=run_sandbox, args=("ONE", results1))
    t2 = threading.Thread(target=run_sandbox, args=("TWO", results2))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    assert results1[0] == "ONE"
    assert results2[0] == "TWO"

def test_symlink_escape_blocked(tmp_path):
    """Ensure symlinks escaping the workspace fail resolution."""
    with SandboxWorkspace(base_dir=tmp_path) as ws:
        import os
        target = tmp_path / "outside.txt"
        target.write_text("secret")
        
        link = ws.path / "link.txt"
        try:
            os.symlink(target, link)
            with pytest.raises(ValueError, match="escapes"):
                ws.resolve("link.txt")
        except OSError:
            # Windows requires privilege for symlinks sometimes
            pytest.skip("ENVIRONMENT-LIMITED: Symlink creation failed on Windows")

