# MARK XLVIII V2 — PHASE 10 RELEASE MANIFEST

## Overview
This manifest details the deployable components and architectural boundaries of MARK XLVIII V2 as prepared in the Phase 10 release candidate.

## Components

### 1. Core Python Runtime (Backend & AI Orchestration)
- **Purpose**: Execution engine for autonomous agents, memory retrieval, workflow processing, and multimodal integration. Serves the local FastApi REST surface.
- **Source**: `core/`, `actions/`, `memory/`, `main.py`
- **Runtime Binding**: `127.0.0.1:8000`
- **Authentication**: JWT-based for Sidecar interactions; REST APIs are intentionally bound only to `localhost` to rely on OS/network-layer boundaries.
- **Packaging Status**: Packaged directly via standard python interpreter. Dependencies resolved via `requirements.txt`.

### 2. Frontend Application (Local UI)
- **Purpose**: Developer-facing visual interface (React/Vite).
- **Source**: `ui/`
- **Build**: Built into static files (`dist/`) using `bun run build`.
- **Runtime/Serving**: Served via standard static file serving or embedded rendering mechanisms.
- **Packaging Status**: Bundled via Vite (ESBuild). No secrets are exposed in the bundle.

### 3. Native Go Sidecar (Remote Device Proxy)
- **Purpose**: Remote execution agent (e.g. mobile devices, edge devices) providing capabilities to the Core Runtime through an authenticated WebSocket channel.
- **Source**: `sidecar/`
- **Build**: Standard Go module build (`go build`).
- **Packaging Status**: Natively compiled binary independent of Python ecosystem.

### 4. LAN Dashboard (Phone Remote Control)
- **Purpose**: Headless local administration interface designed for remote network access via mobile devices (e.g., QR pairing).
- **Source**: `dashboard/server.py`
- **Runtime Binding**: `0.0.0.0:8000` (and `8001` for HTTPS fallback)
- **Security Boundary**: Not part of the `core/runtime` FastAPI instance. Relies on its own isolated Uvicorn server, one-time authentication keys (via QR pairing), and application-layer AES-256-CBC encryption for all communications.

## Ephemeral & Configured State
- **Persistent Data**: Handled in `.data/` (Workflows, Caches) and `memory/` (JSON). Ignored by Git.
- **Configuration & Secrets**: Managed via `.env` or `core/config/`. Secrets are strictly redacted from logs and diagnostic traces.

## Packaging Restrictions
- No `node_modules` or `.git` files included in distributed bundles.
- No `dummy_token` or hardcoded bypasses remain.
- All GPL-conflicting libraries (`PyQt6`) have been isolated and are optional fallbacks.
