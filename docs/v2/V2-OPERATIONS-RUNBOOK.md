# MARK XLVIII V2 — OPERATIONS RUNBOOK

## Overview
This document serves as the operational guide for managing, diagnosing, and deploying MARK XLVIII V2.

## Startup

### Standard Startup
1. Ensure all Python dependencies are met: `pip install -r requirements.txt`. (Do NOT install `PyQt6` unless you require local native UI testing, as it invokes GPLv3 licensing bounds).
2. Ensure Docker is running if executing untrusted tools/code.
3. Run `python main.py`.
4. Observe startup logs to verify FastAPI is listening on `127.0.0.1:8000` and the LAN Dashboard is listening on `0.0.0.0:8000`.

## Shutdown
1. Send a standard `SIGINT` (Ctrl+C).
2. The orchestrator will gracefully terminate WebSocket channels, close active DB connections, and attempt to clean up any active Docker sandboxes.

## Recovery & Database State
- **Corrupt DB**: All memory storage resides in `.data/` or `memory/`. V2 uses isolated JSON storage for facts and a robust WAL-mode SQLite database for workflows. If workflows stall, the queue auto-recovers stranded messages upon restart.
- If data corruption persists, simply wipe `.data/` to force a clean instantiation (Loss of inflight workflows, but safe).

## Common Failures
- **Sandbox Failures**: "Docker Unavailable" means untrusted execution attempts will fail-closed. You must install/start Docker Desktop or equivalent daemon.
- **Sidecar Connection Rejected**: Ensure the Sidecar provides the correct JWT signed by the system's `core/config/` secret key, and ensure the Device ID is enrolled in the `DeviceRegistry`.
- **UI Unavailable**: Run `bun run build` in `ui/` to build the React frontend if the HTML/JS assets are missing. 

## Health Checks
- `GET /api/health`: Provides top-level OK if the system is accepting connections.
- `GET /api/ready`: Verifies internal subsystems (workflows, memory) are initialized.
- `GET /api/health/components`: Detailed breakdown of component states.
- `GET /api/diagnostics`: Internal debugging metrics (Does NOT contain secrets).

## Logs & Diagnostics
Structured logging outputs to standard error/out and rotates based on standard config. Logs redact Bearer tokens and Authorization parameters.

## Backup / Restore Expectations
- **Application Files**: The git repository.
- **Data/Config**: Backup `.env`, `.data/`, and `memory/` for a complete state snapshot. To rollback to a previous version, restoring the `.data` directory ensures workflow compatibility.
