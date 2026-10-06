# MARK XLVIII V2

A modern, highly-modular autonomous AI assistant platform. This represents the stable V2 Release Candidate (Phase 10), completing the architectural migration from the V1 prototype into a robust, secure, event-driven, and multi-agent system.

## Status

MARK XLVIII V2 has successfully passed a 10-phase structural, security, and performance overhaul. 
Key architecture components now include:
- **Event-Driven Workflow Engine**: Robust offline/background processing queues.
- **Docker Sandboxing**: Protected execution environments for all untrusted code/tool invocations.
- **Developer Subsystems**: Secure code/repository inspection boundaries.
- **Go Sidecar Control Plane**: Scalable remote-device capabilities over authenticated WebSockets.
- **Pluggable Frontend**: Vite/React-based UI degrading gracefully into native CLI.

## Architecture 

```
ui/ (React / Vite Frontend)
   │
main.py — Entrypoint. Degrades to Headless CLI if PyQt6 is absent.
   │
core/runtime/ — Central orchestrator, API surface (127.0.0.1:8000), workflow engine
   │
core/sandbox/ — Docker-isolated execution layer
   │
dashboard/server.py — FastAPI remote-control web server (LAN usage only, 0.0.0.0:8000)
   │
sidecar/ — Native Go remote-device proxy (communicating over /ws/sidecar)
   │
memory/ & .data/ — Local JSON and SQLite state (Persistent and WAL-backed)
```

## Installation

Requires Python 3.10+.

```bash
pip install -r requirements.txt
python -m playwright install chromium   # one-time, for browser automation
```

*Note: The older `PyQt6` dependency is no longer actively bundled to comply with GPLv3 open source boundaries. V2 is designed to run completely headless or through the local web dashboard.*

## Configuration

Secrets are managed centrally via `.env` or the OS keyring if deployed.
- **Data storage** is routed explicitly to `.data/` and is fully gitignored. 
- **Workflows** persist via `.data/workflows.sqlite`. 

## Running locally

```bash
python main.py
```
This spawns the Core Backend, Workflow worker threads, and optional UI.

## Remote dashboard (phone control)

The dashboard serves a local web UI reachable from your phone on the same network.
- **Authentication**: Requires a one-time setup code (via QR).
- **Encryption**: Employs mandatory Application-Layer AES-256-CBC encryption to prohibit network eavesdropping.
- **Security Boundary**: Runs as a separate Uvicorn instance from the Core API (`127.0.0.1:8000`), ensuring that the primary REST control surface cannot be accessed via the LAN Dashboard.

## Security

V2 enforces a structured Threat Model (`docs/v2/PHASE-9-THREAT-MODEL.md`).
- **Sandboxing**: Docker isolates the filesystem. If Docker is absent, code execution tools fail closed.
- **Sidecar Auth**: Reject all unauthorized devices strictly through JWT validation and Device Registry mapping.
- **Execution Approvals**: Protected tools enforce a Mandatory Policy Approval loop prior to invocation.

## Development

See `DEVELOPMENT.md` for project structure, running tests, and contribution notes.
All test runs must cleanly pass without `shell=True` warnings or bypasses:
```bash
python -m pytest tests -v
```
