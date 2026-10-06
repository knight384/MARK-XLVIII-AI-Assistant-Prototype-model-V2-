# Phase 1 Security Foundation

## Architecture & Trust Boundaries
The V2 Architecture enforces strict isolation boundaries. The primary focus of Phase 1 is the elimination of the flawed `HostRestrictedSandbox` from the V1 codebase. All sandbox execution is now strictly containerized (via Docker). The core orchestrator runs as a trusted Python process, while untrusted tool execution, generated code, and arbitrary commands execute securely within an ephemeral container boundary. 

If the container runtime is unavailable, execution fails closed.

## Sandbox Model
The `SandboxManager` is the orchestrator for execution. It dynamically selects the `DockerSandbox` backend. If Docker is unavailable, it immediately returns a `SandboxUnavailableError` for all execution requests regardless of risk level.

## Container Model
- **Non-Root Execution**: Handled via standard Docker configuration.
- **No Privileged Mode**: Containers run without added capabilities (`--cap-drop ALL`, `--security-opt no-new-privileges`).
- **Filesystem Isolation**: Bounded to the dynamically generated `SandboxWorkspace` path.

## Network Model
- **Network Disabled by Default**: Uses `--network none` unless explicitly overridden (and approved via PolicyEngine).

## Filesystem Model
The `SandboxWorkspace` handles path resolution defensively. It refuses to resolve paths containing `..` or absolute path escapes that resolve outside the designated temporary directory. This is enforced via `pathlib.Path.resolve()`.

## Resource Model
Resource limits are strictly enforced using native Docker CLI flags:
- CPU Limits (`--cpus`)
- Memory Limits (`--memory`)
- PIDs Limits (`--pids-limit`)
- Execution Timeout (via Python `subprocess` communicating with the Docker process)
- Output bounds are enforced on stdout/stderr collection.

## Secret Model
Host environment variables and secrets are NOT passed into the Docker container. Only explicitly declared `env` mapping via `ResourceLimits` (if ever supported) would be passed.

## Policy & Approval Integration
The security chain remains unchanged:
`Request -> PolicyEngine -> ApprovalManager -> SandboxManager`
The `SandboxManager` is not a bypass; it is simply the execution backend called by the `ToolExecutor` after policies are cleared.

## Failure Model
The sandbox is designed to fail-closed:
- `SandboxUnavailableError`: Runtime not found.
- `SandboxTimeoutError`: Container execution exceeded the allowed duration.
- `SandboxCancelledError`: The execution was interrupted cleanly.

## Concurrency
Concurrent jobs run in separate Docker containers with dynamically generated GUID workspace directories. There is zero state shared between concurrent sandbox executions.

## Windows Behavior
The Docker CLI wrapper approach correctly handles Windows paths since Docker Desktop transparently handles the `C:\` mounts mapping to the Linux VM workspace volume.

## Environment Requirements
Docker must be installed, running, and accessible by the host process. If absent, the system operates in a degraded (but secure) state where tasks requiring the sandbox are refused.
