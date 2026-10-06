# V2 Roadmap

This roadmap proposes the phased implementation plan for MARK XLVIII V2, driven by the Phase 0 architecture gap analysis.

## Phase 0: Architecture & Gap Analysis (Current)
- Complete audit of the V1 repository.
- Subsystem classification and provenance mapping.
- Finalization of target architecture and security improvements.
- *Status: Completed*

## Phase 1: Security Foundation & Hardening
- **Objective**: Establish strict boundaries before rebuilding features.
- **Tasks**:
  - Delete `HostRestrictedSandbox` and ensure `SandboxManager` enforces true containerization.
  - Implement basic JWT/Auth middleware for the API boundary.
  - Fortify `PolicyEngine` against execution bypasses.
  
## Phase 2: Clean-Room Workflow Engine
- **Objective**: Replace donor-derived `core/workflows` with an original design.
- **Tasks**:
  - Design the new state machine and persistence schema.
  - Implement a Pythonic, async-native worker loop without polling lock contention.
  - Establish clear interfaces for the agent capability effects.

## Phase 3: Clean-Room Developer Subsystem
- **Objective**: Replace donor-derived `core/developer` modules.
- **Tasks**:
  - Architect new Git integration using robust subprocess wrappers or GitPython.
  - Architect new GitHub integration via strict REST API wrappers and `pydantic`.
  - Migrate dependent tools to the new interfaces.

## Phase 4: V2 Foundation / Architecture Corrections
- **Objective**: Refine retained systems.
- **Tasks**:
  - Update `core/config` to support secure secret wiping.
  - Revise the `ToolRegistry` to enforce strict typing and explicit isolation markers.

## Phase 5: Advanced Multimodal Channels
- **Objective**: Introduce rich streaming and I/O.
- **Tasks**:
  - Upgrade `core/llm` routing to handle multimodal inputs natively.
  - Overhaul `core/channels` for audio/video streaming interfaces.

## Phase 6: Advanced Device / Sidecar Platform
- **Objective**: Enable secure, remote task execution.
- **Tasks**:
  - Enhance `core/devices` to support remote capability negotiation.
  - Implement mTLS / trust scoring for sidecars.
  - Sync remote policy profiles dynamically.

## Phase 7: Performance / Scalability
- **Objective**: Eliminate bottlenecks.
- **Tasks**:
  - Optimize SQLite I/O for `core/memory` vector operations.
  - Transition event bus to high-throughput implementations if needed.

## Phase 8: Observability / Reliability
- **Objective**: Improve crash recovery and monitoring.
- **Tasks**:
  - Enhance `core/runtime` graceful shutdowns.
  - Implement extensive error reporting and tracing across process boundaries.

## Phase 9: Full Security & Provenance Audit
- **Objective**: Final check before release.
- **Tasks**:
  - Verify all donor-derived code remains excluded.
  - Perform penetration testing on the sandbox boundary and API endpoints.

## Phase 10: V2 Release Candidate
- **Objective**: Prepare `v2.0.0-rc1`.
- **Tasks**:
  - Final documentation update.
  - Baseline tests pass with 100% boundary enforcement.
