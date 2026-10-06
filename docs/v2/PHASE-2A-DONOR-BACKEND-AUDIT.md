# Phase 2A Donor Backend Audit

## Overview
The `jarvis-main` donor backend is a monolithic daemon written in TypeScript running on Bun (`src/daemon/index.ts`). It handles everything from API routing, WebSockets, background tasks, to database access and integrations.

## Architecture & Stack
- **Language**: TypeScript
- **Runtime**: Bun
- **HTTP/Routing**: `Bun.serve()` with manual route prefix matching (`api-routes.ts`)
- **WebSockets**: Custom WS service + `socket.io`
- **Database**: SQLite (via `bun:sqlite` or similar)
- **Sidecar/Desktop**: Go (in `sidecar/`)

## Subsystem Audit

### `src/daemon/api-routes.ts`
- **Purpose**: Provides a massive REST API surface (e.g., `/api/vault/entities`, `/api/calendar`, `/api/agents/tasks`).
- **V2 equivalent**: `core.api` (FastAPI) or `core.runtime`.
- **Decision**: **REBUILD-CLEAN-ROOM** (Class C). V2 is firmly committed to Python as the core orchestration language. The endpoint structures (request/response schemas) should be mapped and re-implemented in FastAPI.

### `src/daemon/ws-service.ts`
- **Purpose**: WebSocket streaming for real-time chat, voice, and room actions.
- **V2 equivalent**: `core.runtime.channels`.
- **Decision**: **REBUILD-CLEAN-ROOM** (Class C). V2's `ChannelManager` is already designed to handle this in Python. We will adapt the specific message formats (e.g., `room_action`, `chat_message`) to V2's schemas.

### `src/workflows/`
- **Purpose**: Database-backed job queue and trigger execution.
- **Decision**: **REFERENCE ONLY** (Class C). As stipulated by Phase 2 rules, we must not import the donor workflow engine. It will serve as requirements input for Phase 3.

### `src/llm/`
- **Purpose**: LLM provider integrations (OpenAI, Anthropic, Gemini, Groq, etc.).
- **V2 equivalent**: `core.llm.gateway`.
- **Decision**: **REJECT/DEFER** (Class D). V2 already has a robust ModelGateway in Python.

### `src/sidecar/` (Go)
- **Purpose**: Native OS daemon (macOS/Windows) for system tray, autostart, and desktop integrations.
- **Language**: Go
- **Decision**: **DEFER** (Class E). As instructed, do not implement it in this phase, but it will be reused/modified later when desktop native capabilities are needed.

### `src/authority/` & `src/roles/`
- **Purpose**: Policy, roles, and approval logic.
- **V2 equivalent**: `core.security.policy` and `ApprovalManager`.
- **Decision**: **REJECT** (Class D). V2's security architecture (Phase 1/6) is strictly authoritative.

### `src/vault/`
- **Purpose**: SQLite database repositories for entities, facts, commitments, observations.
- **V2 equivalent**: `core.memory.knowledge`.
- **Decision**: **ADAPT/REBUILD** (Class C). The schema is useful, but it must be ported to Python (SQLAlchemy/SQLModel or raw sqlite3) to integrate with V2.

## Recommendation
Unlike the frontend, the **donor backend will NOT be reused as code**. The architectural differences (Bun/TS vs Python) and security guarantees (V2 Sandbox, V2 PolicyEngine) mandate that the backend remains purely Pythonic. The API contracts (URLs, JSON payloads) established by the frontend will dictate what we build in FastAPI to satisfy the UI.
