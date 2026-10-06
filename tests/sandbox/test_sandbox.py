"""
tests/sandbox/test_sandbox.py
V2 True Isolation Sandbox Tests
"""
from __future__ import annotations

import shutil
import pytest

from core.sandbox.docker import DockerSandbox
from core.sandbox.errors import SandboxUnavailableError
from core.sandbox.limits import ResourceLimits
from core.sandbox.manager import SandboxManager
from core.sandbox.workspace import SandboxWorkspace
from core.tools.metadata import RiskLevel

DOCKER_AVAILABLE = shutil.which("docker") is not None

# -- workspace tests ----------------------------------------------------

def test_workspace_creates_unique_directory(tmp_path):
    ws1 = SandboxWorkspace(base_dir=tmp_path)
    ws2 = SandboxWorkspace(base_dir=tmp_path)
    assert ws1.path != ws2.path
    assert ws1.path.exists()
    ws1.cleanup()
    ws2.cleanup()

def test_workspace_path_traversal_blocked(tmp_path):
    """spec Part 28/54: attempt path traversal must be refused."""
    with SandboxWorkspace(base_dir=tmp_path) as ws:
        with pytest.raises(ValueError):
            ws.resolve("../../etc/passwd")

def test_workspace_nested_path_traversal_blocked(tmp_path):
    with SandboxWorkspace(base_dir=tmp_path) as ws:
        with pytest.raises(ValueError):
            ws.resolve("subdir/../../outside.txt")

# -- Manager logic ------------------------------------------------------

def test_manager_prefers_docker_when_available(monkeypatch):
    manager = SandboxManager()
    monkeypatch.setattr(manager, "docker_available", lambda force_recheck=False: True)
    backend = manager.select_backend(RiskLevel.LOW)
    assert backend.backend_name == "docker"

def test_manager_fails_closed_without_docker(monkeypatch):
    """V2 Requirement: if Docker is unavailable, everything fails closed."""
    manager = SandboxManager()
    monkeypatch.setattr(manager, "docker_available", lambda force_recheck=False: False)
    
    for risk in (RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL):
        assert manager.select_backend(risk) is None
        
        with pytest.raises(SandboxUnavailableError):
            manager.execute_command(["echo", "x"], risk_level=risk)

def test_docker_sandbox_reports_real_isolation():
    assert DockerSandbox().is_real_isolation is True

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker binary not found — ENVIRONMENT-LIMITED")
def test_docker_real_execution_smoke():
    sandbox = DockerSandbox()
    if not sandbox.is_available():
        pytest.skip("Docker binary present but daemon not reachable — ENVIRONMENT-LIMITED")
    with SandboxWorkspace() as ws:
        result = sandbox.execute_command(["echo", "hello from docker"], ws, ResourceLimits(timeout_seconds=30))
    assert result.success is True
    assert "hello from docker" in result.stdout

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="ENVIRONMENT-LIMITED")
def test_docker_sandbox_timeout(tmp_path):
    sandbox = DockerSandbox()
    if not sandbox.is_available():
        pytest.skip("ENVIRONMENT-LIMITED")
    with SandboxWorkspace(base_dir=tmp_path) as ws:
        result = sandbox.execute_command(
            ["python3", "-c", "import time; time.sleep(30)"], ws,
            ResourceLimits(timeout_seconds=0.5),
        )
    assert result.timed_out is True
    assert result.success is False

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="ENVIRONMENT-LIMITED")
def test_docker_output_limit(tmp_path):
    sandbox = DockerSandbox()
    if not sandbox.is_available():
        pytest.skip("ENVIRONMENT-LIMITED")
    with SandboxWorkspace(base_dir=tmp_path) as ws:
        result = sandbox.execute_command(
            ["python3", "-c", "print('x' * 1000)"], ws,
            ResourceLimits(output_limit_bytes=100),
        )
    assert len(result.stdout) <= 100
