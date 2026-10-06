# V2 Feature Catalog

This catalog outlines capabilities targeted for MARK XLVIII V2 based on the donor extraction.

## FC-001: Golang Cross-Platform Sidecar
- **Source**: `jarvis-main/sidecar/*`
- **V1 status**: Absent.
- **V2 disposition**: ADAPT.
- **Priority**: HIGH.
- **Target subsystem**: `core/devices` & External Sidecar Binary.
- **Target language**: GO (for the daemon), PYTHON (for the control plane).
- **Dependencies**: Go compiler, OS-native webview libraries.
- **Security requirements**: mTLS and JWT enrollment.
- **Phase target**: Phase 6

## FC-002: Native Event-Driven Workflow Engine
- **Source**: Concept inspired by `src/workflows/queue/worker.ts`, but heavily flawed by DB polling.
- **V1 status**: Partial / Flawed (Donor-derived).
- **V2 disposition**: REBUILD-CLEAN-ROOM.
- **Priority**: CRITICAL.
- **Target subsystem**: `core/workflows`.
- **Target language**: PYTHON.
- **Dependencies**: None (Native `asyncio`).
- **Security requirements**: Strict cancellation boundaries for runaway tasks.
- **Phase target**: Phase 3

## FC-003: Clean-Room Developer Integrations
- **Source**: `src/sites/git-manager.ts` and `github-manager.ts`.
- **V1 status**: Flawed (Donor-derived).
- **V2 disposition**: REBUILD-CLEAN-ROOM.
- **Priority**: HIGH.
- **Target subsystem**: `core/developer`.
- **Target language**: PYTHON.
- **Dependencies**: `GitPython` or subprocess wrappers.
- **Security requirements**: Strict execution boundaries for Git commands to prevent command injection.
- **Phase target**: Phase 2
