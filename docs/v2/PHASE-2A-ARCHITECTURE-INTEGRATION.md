# Phase 2A Architecture Integration Plan

## Core Philosophy
The V2 Architecture stands authoritative. We are replacing the V1 CLI-only or minimal interface with the rich React frontend from the `jarvis-main` donor. However, the donor backend (TypeScript/Bun) is entirely discarded in favor of V2's Python orchestration, policy, and security engine.

## The Integration Strategy

1. **Frontend Porting**: The `jarvis-main/ui/` folder will be copied into V2 as `ui/`. We will configure `npm` or `bun` scripts within V2 to build it.
2. **Backend API Emulation**: The V2 FastAPI server (`core.api`) will be expanded to serve the exact JSON endpoint contracts that the React frontend expects (e.g., `/api/health`, `/api/vault/entities`, `/api/agents/tasks`).
3. **WebSocket Bridge**: The V2 `ChannelManager` will implement the `socket.io` or raw WebSocket protocols expected by `ui/src/v2/AppShellV2.tsx` and the `RoomActionBus`.

## Recommended Technology Stack

### Frontend (Adopted from Donor)
- React 19 + TypeScript
- Bun or Vite for bundling
- Tailwind CSS
- (No language changes here. It stays JS/TS).

### Backend (Native V2)
- **Language**: Python 3.11+
- **Framework**: FastAPI (for HTTP and WS).
- **Security Engine**: V2 `PolicyEngine` and `SandboxManager`.
- **Reasoning**: We do not adopt the TS/Bun backend because Python is V2's mandated orchestration language, providing better ecosystem alignment for AI/ML and allowing us to keep the rigorous Phase 1/Phase 2 Sandbox security boundaries.

### Go Sidecar (Deferred)
- **Language**: Go
- **Reasoning**: Go is the optimal choice for cross-platform system tray, OS-native windowing, and low-level global hotkeys. Python is too heavy to distribute as a silent background daemon on Windows/macOS. We defer this implementation to a future phase.

## API Integration Plan

1. **Phase 2A-1: UI Shell Initialization**
   - Copy `jarvis-main/ui/` to `ui/`.
   - Setup FastAPI to serve static files (`ui/dist/`) on the root `/` path.
   - Implement `/api/health` and basic configuration endpoints so the React AppShell can boot without crashing.

2. **Phase 2A-2: Identity & Security Mapping**
   - The UI assumes certain authorization models. We will wire UI actions (like terminal execution or file deletion) through the V2 `ApprovalManager`. 
   - The UI's "Confirm" dialogs must trigger V2 `PolicyEngine` approval flows.

3. **Phase 2A-3: Database / Vault API Integration**
   - Implement the `core.memory` SQLAlchemy models mimicking the donor's `src/vault/` schemas (Entities, Facts, Commitments).
   - Implement the REST CRUD endpoints in FastAPI.

4. **Phase 2A-4: Agent Task API Integration**
   - Expose the V2 `AgentRegistry` and `ToolExecutor` task statuses via the `/api/agents/tasks` polling endpoints.
   - Map V2's `AgentTask` states to the frontend's expected status enums.

5. **Phase 2A-5: WebSocket Realtime Channels**
   - Connect FastAPI WebSockets to the UI for streaming LLM responses and handling `room_action` pushes.

6. **Phase 2A-6: Developer Subsystem Wiring**
   - Wire the React UI's developer tools (if any) to the clean-room `core.developer` implementation created in Phase 2.

## Conflict Resolution: V2 Architecture Wins
- **No `jarvis-main` daemon**: We will not run `bun run src/daemon/index.ts`. V2 runs purely on `python main.py`.
- **No `jarvis-main` workflow engine**: The UI's workflow builder will temporarily be stubbed or read-only until Phase 3 builds the V2 Workflow Engine.
