# Phase 2A Reuse Matrix

| ID | Donor Path | Feature | Frontend/Backend | Language | V2 Equivalent | Decision | Target V2 Location | Dependencies | Security Impact | License/Provenance | Implementation Phase |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RM-001 | `jarvis-main/ui/src/` | Entire Web App UI | Frontend | TS/React | None | REUSE / MODIFY | `ui/` | React, Tailwind, Lucide | LOW (Runs in browser) | Class B (Modify) | Phase 2A-1 |
| RM-002 | `jarvis-main/src/daemon/api-routes.ts` | REST API | Backend | TS | `core.api` (FastAPI) | REBUILD | `core/api/` | FastAPI | HIGH (API auth surface) | Class C (Reference) | Phase 2A-2 |
| RM-003 | `jarvis-main/src/daemon/ws-service.ts` | WebSocket Server | Backend | TS | `core.runtime.channels` | REBUILD | `core/runtime/channels/` | FastAPI WS | HIGH (Realtime input) | Class C (Reference) | Phase 2A-3 |
| RM-004 | `jarvis-main/src/workflows/` | Workflow Engine | Backend | TS | None (Phase 3 target) | DEFER / REFERENCE | `core/workflows/` | N/A | MEDIUM | Class E (Defer) | Phase 3 |
| RM-005 | `jarvis-main/src/authority/` | Security Engine | Backend | TS | `PolicyEngine`, `ApprovalManager` | REJECT | N/A | N/A | CRITICAL | Class D (Reject) | N/A |
| RM-006 | `jarvis-main/src/sidecar/` | Desktop Sidecar | Backend | Go | None | DEFER | `sidecar/` | Go runtime | HIGH (Local OS access) | Class E (Defer) | Future Phase |
| RM-007 | `jarvis-main/src/llm/` | LLM Gateway | Backend | TS | `core.llm.gateway` | REJECT | N/A | N/A | MEDIUM | Class D (Reject) | N/A |
| RM-008 | `jarvis-main/src/vault/` | Vault DB schema | Backend | TS | `core.memory` | ADAPT | `core/memory/` | SQLAlchemy / SQLite | HIGH (Data persistence) | Class B (Modify) | Phase 2A-2 |

## Donor Code Classes

- **CLASS A (Approved direct reuse)**: `jarvis-main/ui/` components (shell, palette, styles).
- **CLASS B (Approved for modification)**: The UI data-fetching hooks (rewiring endpoints), `vault` DB schema concepts.
- **CLASS C (Reference/behavior only)**: `api-routes.ts`, `ws-service.ts` (API schemas used for FastAPI rebuilding).
- **CLASS D (Reject)**: `src/authority/`, `src/llm/`, `src/sites/git-manager.ts` (Already replaced in V2).
- **CLASS E (Defer)**: Go sidecar (`src/sidecar/`), Workflow runtime (`src/workflows/`).
