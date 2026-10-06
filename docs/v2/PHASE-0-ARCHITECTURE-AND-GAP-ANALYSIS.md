# Phase 0 Architecture and Gap Analysis

**Date**: 2026-10-06
**Objective**: Perform a complete MARK XLVIII V2 Architecture & Gap Analysis before writing new V2 implementation code. 

## 1. V1 Audit Summary
The V1 repository (`v1.0.0-rc1` at commit `17a4e180928d`) was fully audited. V1 establishes a robust foundation with its Model Gateway, Tool Registry, Multi-Agent Runtime, Policy Engine, and Memory systems. However, critical gaps were identified in sandbox isolation, scalability of the workflow engine, and the provenance of certain developer modules.

## 2. Complete Subsystem Classification
Refer to [V1-SUBSYSTEM-CLASSIFICATION.md](./V1-SUBSYSTEM-CLASSIFICATION.md) for the detailed classification (KEEP/IMPROVE/REPLACE/REMOVE/NEW) of all V1 subsystems.

## 3. Biggest Architectural Weaknesses
- **Capability Boundaries**: Tools are executed without sufficient isolation from the main process, allowing potential confused-deputy attacks.
- **Workflow Engine Limitations**: The current SQLite-polling worker (`core/workflows/worker.py`) is rudimentary, lacking true asynchronous event handling.
- **Tight Coupling in Core Developer**: Developer integrations (`git` and `github`) rely heavily on specific execution environments and tokens, without standard Pythonic abstraction.

## 4. Biggest Security Weaknesses
- **Sandbox Failure**: The `HostRestrictedSandbox` is explicitly insecure on Windows, failing to provide network, memory, or filesystem boundaries. This is the system's most severe vulnerability.
- **Credential Handling**: Unscoped API tokens and lack of secure memory wiping for secrets.
- Refer to [SECURITY-GAP-ANALYSIS.md](./SECURITY-GAP-ANALYSIS.md) for details.

## 5. Biggest Scalability Weaknesses
- **Workflow Polling**: The coarse `SELECT` and lock polling mechanism in the workflow engine limits concurrency and scales poorly under load.
- **Vector Operations**: SQLite vector operations might bottleneck as the `core/memory` Knowledge Graph grows.

## 6. Licensing / Provenance Risks
- Code derived from the `jarvis-main` donor project (specifically within `core/workflows` and `core/developer`) introduces RSALv2-derived constraints. These sections MUST be replaced to ensure MARK V2 remains unencumbered.
- Refer to [PROVENANCE-AND-LICENSE-ANALYSIS.md](./PROVENANCE-AND-LICENSE-ANALYSIS.md) for details.

## 7. Clean-Room Replacement Candidates
- `core/workflows/*` (Workflow Engine, State Machine, Poller)
- `core/developer/git.py` (Git Integration)
- `core/developer/github.py` (GitHub Integration)

## 8. Proposed V2 Architecture
Refer to [V2-TARGET-ARCHITECTURE.md](./V2-TARGET-ARCHITECTURE.md) for details on process boundaries, security boundaries, and API interfaces.

## 9. Proposed V2 Roadmap
Refer to [V2-ROADMAP.md](./V2-ROADMAP.md) for the step-by-step transition plan to V2.

## 10. Explicit List of Items NOT to Change
- **Core Runtime Language**: Python remains the core language. No other languages are introduced.
- **Original Architecture Concepts**: The underlying agent abstractions, memory structures, policy engine concepts, and configuration models will be retained and extended.
- **V1 Baseline**: V1 remains completely untouched.

## 11. Explicit List of Items that MUST Change
- The `HostRestrictedSandbox` fallback must be eliminated.
- Donor-derived implementation files (`git.py`, `github.py`, and `workflows`) must be completely clean-room engineered.
- Stricter Least-Privilege boundaries must be enforced around `ToolExecutor`.

## 12. Open Architectural Decisions
- The exact container technology for sandboxing (Docker vs. microVMs).
- The underlying database engine choice for the new async workflow queue (SQLite vs. external broker).
- Refer to [PHASE-0-DECISIONS.md](./PHASE-0-DECISIONS.md) for a complete list.

## 13. Recommended Implementation Order
1. Security Foundation & Sandbox Hardening
2. Clean-Room Workflow Engine redesign
3. Clean-Room Developer Subsystem redesign
4. Architecture Corrections and extensions (Channels, Devices, Performance)

## 14. Risks and Dependencies
- **Clean-room strictness**: Ensuring the new engineering does not accidentally duplicate donor implementation.
- **Operational Overhead**: Forcing containerization as a strict requirement will raise the minimum deployment dependencies.

## 15. Definition of Done for Phase 0
- V1 has been audited across all core subsystems.
- V1 remains completely untouched.
- V2 repository identity is established.
- Subsystems classified, gaps identified, provenance mapped.
- Clean-room candidates identified.
- Target architecture and roadmap documented.
- Explicit lists of required and prohibited changes created.
- **No speculative implementation has been introduced.**

Phase 0 is complete.
