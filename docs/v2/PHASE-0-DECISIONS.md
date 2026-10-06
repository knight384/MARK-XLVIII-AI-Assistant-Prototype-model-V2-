# Phase 0 Decisions

This document records the explicit decisions made during Phase 0 regarding the transition from V1 to V2.

## Explicit List of Items NOT to Change
1. **Core Runtime Language**: Python remains the core language for V2. No other language will be introduced in the core architecture without strict justification.
2. **Configuration Manager (`core/config`)**: The foundational logic works well and will not be rewritten, only extended.
3. **Agent and Mission Paradigms (`core/agent`, `core/mission`)**: The overarching multi-agent structure and persistent mission architectures are original and fundamental to MARK's design. They remain structurally intact.
4. **V1 Repository**: The V1 repository (`knight384/MARK-XLVIII-AI-Assistant-Prototype-model-V1-`) is permanently frozen as an immutable reference baseline. It will not receive patches.

## Explicit List of Items that MUST Change
1. **Host-Restricted Sandbox**: The `HostRestrictedSandbox` in `core/sandbox/command.py` MUST be removed. It provides false security on Windows and violates strict isolation requirements.
2. **Donor-Derived Developer Tools**: `core/developer/git.py` and `github.py` MUST be completely redesigned in a clean-room environment to drop licensing restrictions.
3. **Workflow Engine**: `core/workflows/*` MUST be redesigned in a clean-room environment to avoid licensing constraints and to address concurrency limitations in the current polling model.

## Open Architectural Decisions
- **Sandbox Container Tech Stack**: Should V2 rely solely on Docker/Podman, or should it integrate native microVMs (like Firecracker on Linux) for enhanced security at the cost of setup complexity? *Decision deferred to Phase 1.*
- **Database Engine for Workflows**: Can the new async workflow engine safely continue using SQLite via asynchronous drivers, or does the workload require a dedicated broker (like Redis or PostgreSQL) for reliability? *Decision deferred to Phase 2.*
- **Vector Search Strategy**: Should the knowledge graph vectors stay in SQLite, or is it time to introduce a dedicated lightweight vector DB (like ChromaDB or Qdrant) in-process? *Decision deferred to Phase 7.*

## Recommended Implementation Order
1. Eliminate insecure sandbox boundaries (Phase 1).
2. Clean-room redesign of the Workflow Engine (Phase 2).
3. Clean-room redesign of Developer tools (Phase 3).
4. Iterate and expand on capabilities (Phases 4-10).

## Risks and Dependencies
- **Clean-room execution risk**: It requires careful design to ensure no accidental duplication of the donor logic occurs, which requires strict test-driven development based only on the external requirements.
- **Docker dependency**: Failing closed when Docker is unavailable heavily restricts the assistant's capability on hosts that cannot run containers. We accept this capability reduction in exchange for guaranteed security.
