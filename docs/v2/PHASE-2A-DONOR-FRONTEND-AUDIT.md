# Phase 2A Donor Frontend Audit

## Overview
The donor repository (`jarvis-main`) uses a React-based frontend built on modern web primitives. The source resides in `jarvis-main/ui/src/`. It does not rely on heavy meta-frameworks like Next.js for routing; instead, it uses a lightweight hash-based router (`router.ts`) and a shell-and-room architecture (`AppShellV2.tsx`).

## Architecture & Stack
- **Framework**: React 19 (`react`, `react-dom`)
- **Language**: TypeScript (`.tsx`)
- **Build Tool**: Bun (`bun build`)
- **Styling**: Tailwind CSS v4 (`tailwindcss`) and raw CSS (`v2.css`, `primitives.css`, `pebble.css`)
- **State/Routing**: Custom hash router (`router.ts`), Context APIs (`RoomActionBusProvider`)
- **Editor**: CodeMirror (`@codemirror/view`, etc.)
- **Icons**: Lucide React (`lucide-react`)
- **Flow/Graph Visualization**: React Flow (`@xyflow/react`)
- **Realtime**: Socket.IO client (`socket.io-client`)
- **Markdown**: `react-markdown`, `remark-gfm`

## Core Modules & Decisions

### `ui/src/v2/AppShellV2.tsx`
- **Purpose**: Main application shell providing the global structure, `BootSplash`, `ConfirmHost`, `OnboardingGate`, and handling different rendering modes (panel, kit, states, billing).
- **V2 equivalent**: None. V2 is completely missing a frontend.
- **Decision**: **REUSE** (Class A). The app shell layout is solid, lightweight, and specifically designed for the JARVIS paradigm (persistent thread + rooms).

### `ui/src/v2/router.ts`
- **Purpose**: Hash-based router mapping `#/_room_<key>` to specific overlays.
- **Dependencies**: React hooks.
- **Decision**: **REUSE** (Class A). Very lightweight; prevents dragging in `react-router-dom` for a single-page app.

### `ui/src/v2/shell/`
- **Purpose**: The chrome of the application (Thread, Rail, Composer).
- **Decision**: **REUSE** (Class A). Core UI components.

### `ui/src/v2/rooms/`
- **Purpose**: The "Room" overlays (workflows, memory, tools, agents, logs, calendar).
- **Decision**: **MODIFY** (Class B). The UI layers are reusable, but they will need to be rewired to point to the new V2 Python FastAPI backends instead of the Bun APIs.

### `ui/src/v2/ambient/Pebble.tsx`
- **Purpose**: Floating desktop widget for voice interaction.
- **Decision**: **REUSE/MODIFY** (Class B). Crucial for the ambient voice experience, but relies on specific WebSocket and WebRTC signaling that must be replicated in V2's `VoiceChannel`.

### `ui/src/v2/onboarding/`
- **Purpose**: Initial setup gate.
- **Decision**: **MODIFY** (Class B). Needs to map to V2's Python onboarding states.

### `ui/src/v2/palette/`
- **Purpose**: Command palette / fuzzy finder (`Ctrl+K`).
- **Decision**: **REUSE** (Class A). The UI is self-contained.

### WebSockets & API Clients
- **Location**: Scattered throughout `useFetch`, `socket.io` hooks, or direct `fetch()` calls.
- **Decision**: **ADAPT** (Class B). The data fetching layer in the frontend must be unified and pointed at the V2 Python backend (e.g., `http://localhost:8000/api` instead of `http://localhost:3142/api`).

## Recommendation
The entire `jarvis-main/ui` tree should be copied into V2 as the canonical frontend, retaining React + Bun/Vite for the build. The major work will be modifying the network boundaries (fetch/WS) to talk to the V2 Python core rather than the original Bun daemon.
