# Donor Capability Inventory

This document extracts significant capabilities from the `jarvis-main` donor repository and analyzes their relevance to MARK XLVIII V2.

## DC-001: Developer Git Management
- **Description**: Wraps Git CLI commands for version control, branch management, logs, commits, diffs.
- **Source files**: `src/sites/git-manager.ts`
- **Important classes**: `GitManager`
- **Important functions**: `init`, `autoCommit`, `getBranches`, `getLog`, `getDiff`, `merge`, `rebase`
- **Dependencies**: Host OS `git` executable (via `Bun.spawn`)
- **External integrations**: Git
- **V1 equivalent**: `core/developer/git.py` (direct Python translation)
- **V2 relevance**: Essential for developer agent functionality.
- **Recommended disposition**: REBUILD-CLEAN-ROOM
- **Recommended language**: PYTHON
- **Implementation notes**: Rebuild using standard Python subprocess wrappers or `GitPython` to eliminate TS-derived provenance.
- **Provenance classification**: A (Original donor implementation) -> F (Candidate clean-room requirement)

## DC-002: Workflow Polling Queue
- **Description**: In-process worker that polls a SQLite job queue and dispatches jobs to registered handlers.
- **Source files**: `src/workflows/queue/worker.ts`
- **Important classes**: `Worker`
- **Important functions**: `start`, `stop`, `runLoop`, `handle`
- **Concurrency behavior**: Runs parallel polling loops via configurable `concurrency`.
- **V1 equivalent**: `core/workflows/worker.py` (Python equivalent)
- **V2 relevance**: Needed for asynchronous task execution.
- **Recommended disposition**: REBUILD-CLEAN-ROOM
- **Recommended language**: PYTHON
- **Implementation notes**: V2 needs a native `asyncio` or structured queue rather than relying on synchronous database polling.
- **Provenance classification**: A -> F

## DC-003: Sidecar Device Enrollment
- **Description**: Standalone sidecar enrollment creating JWTs and managing ES256 keypairs for device trust.
- **Source files**: `src/sidecar/enrollment.ts`
- **Important functions**: `loadOrGenerateSidecarKeys`, `enrollDevice`, `buildEnrollmentUrls`
- **Security assumptions**: Relies on file permissions (`chmod 600`) for private keys and JWTs for device identity.
- **V1 equivalent**: `core/devices/registry.py` (Partial overlap)
- **V2 relevance**: Highly relevant for the remote device execution architecture.
- **Recommended disposition**: ADAPT
- **Recommended language**: PYTHON (Control Plane) / GO (Sidecar daemon)
- **Implementation notes**: The Go sidecar components are excellent for cross-platform deployment. V2 should build its own Python control plane to interact with Go sidecars.
- **Provenance classification**: A

## DC-004: Multimodal Browser Tooling
- **Description**: High-level proxy and dev-server managers.
- **Source files**: `src/sites/proxy.ts`, `dev-server-manager.ts`
- **V1 equivalent**: Absent. V1 sandbox does not have advanced browser streaming proxies.
- **V2 relevance**: Useful for web UI previewing.
- **Recommended disposition**: DEFER
- **Recommended language**: N/A
- **Provenance classification**: A

## DC-005: Golang Desktop Sidecar
- **Description**: Cross-platform desktop sidecar running a webview UI and background daemon, written in Go.
- **Source files**: `sidecar/internal/*`, `sidecar/installer/*`
- **V1 equivalent**: Absent (V1 only has mock or partial device stubs).
- **V2 relevance**: High. Needed for native Windows/macOS/Linux system integration (audio/vision).
- **Recommended disposition**: KEEP-V1 / ADAPT
- **Recommended language**: GO
- **Implementation notes**: Go is the correct choice here for native OS integration and single-binary distribution. Python is too heavy for a lightweight background OS daemon.
- **Provenance classification**: A
