# Phase 2A Frontend → Backend Map

This document explicitly maps the expected donor frontend actions to the new V2 Python backend equivalents.

## Health & Boot Sequence

| Donor Frontend Action | Expected Donor Endpoint | V2 Target API | V2 Security Boundary |
|---|---|---|---|
| App Boot Status | `GET /api/health` | `GET /api/health` | Unauthenticated / Public local |
| Load Config | `GET /api/system/external-origin` | `GET /api/system/external-origin` | Unauthenticated |

## Agent & Orchestration

| Donor Frontend Action | Expected Donor Endpoint | V2 Target API | V2 Security Boundary |
|---|---|---|---|
| Load Agent List | `GET /api/agents` | `core.api.agents.list_agents` | Authenticated (Local token) |
| Spawn Agent Task | `POST /api/agents/tasks` | `core.api.tasks.spawn_task` | Triggers `PolicyEngine` evaluation if tool risk is high. |
| View Task Result | `GET /api/agents/tasks/:id` | `core.api.tasks.get_task` | Read-only |

## Vault / Memory (CRUD)

| Donor Frontend Action | Expected Donor Endpoint | V2 Target API | V2 Security Boundary |
|---|---|---|---|
| Search Entities | `GET /api/vault/search` | `core.memory.api.search` | Read-only |
| Create Fact | `POST /api/vault/entities/:id/facts`| `core.memory.api.create_fact` | Read/Write (Low Risk) |
| Manage Commitments| `GET /api/vault/commitments`| `core.memory.api.list_commitments`| Read-only |

## Realtime / WebSocket

| Donor Frontend Action | Expected Donor WS Event | V2 Target Channel | V2 Security Boundary |
|---|---|---|---|
| Voice Stream Open | `ws://.../ws` (audio) | `core.runtime.channels.VoiceChannel`| WebSocket Auth |
| Chat Message Sent | `ws://.../ws` (chat) | `core.runtime.channels.ChatChannel` | WebSocket Auth |
| Room Action Push | Server -> Client `room_action` | `ChannelManager.broadcast` | Internal server push only |

## Developer Subsystem

| Donor Frontend Action | Expected Donor Endpoint | V2 Target API | V2 Security Boundary |
|---|---|---|---|
| Inspect Git Status | `GET /api/developer/git/status` (example) | `core.developer.git.GitIntelligence.status` via API | Bounded to Sandbox Workspace limits. |
| Commit / Push | `POST /api/developer/git/push` (example)| `core.developer.tools.DeveloperGitPushTool` | **HIGH RISK**. Triggers `ApprovalManager` prompt in UI. |
| Inspect Project | `GET /api/developer/project` (example) | `core.developer.project.ProjectAnalyzer.analyze` via API | Traversal limits enforced. |

## Workflow Engine (Deferred to Phase 3)

| Donor Frontend Action | Expected Donor Endpoint | V2 Target API | V2 Security Boundary |
|---|---|---|---|
| View Workflows | `GET /api/workflows` | STUB (Phase 3) | N/A |
| Save Workflow | `POST /api/workflows` | STUB (Phase 3) | N/A |

## Mapping Strategy
The V2 FastAPI application will expose routers (e.g., `router = APIRouter(prefix="/api/vault")`) that perfectly align with these paths. We will rely on Pydantic models to deserialize the frontend requests and serialize the SQLAlchemy responses, ensuring strict type safety across the boundary.
