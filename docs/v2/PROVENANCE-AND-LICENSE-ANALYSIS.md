# Provenance and License Analysis

This document identifies donor-derived components in the V1 baseline and outlines the clean-room replacement strategy for V2.

## Provenance Map

### A. Original MARK Implementation (KEEP/IMPROVE)
- `core/agent/*`: Core multi-agent runtime and logic.
- `core/sandbox/*` (excluding the insecure fallback): True sandboxing concepts (Docker execution).
- `core/policy/*`: Policy engine and approval boundaries.
- `core/memory/*`: Layered memory and knowledge graph concepts.
- `core/mission/*`, `core/awareness/*`, `core/goals/*`, `core/personality/*`.

### B. Donor-Adapted Implementation (REPLACE)
These components were explicitly marked as adapted from an RSALv2-derived donor project (`jarvis-main`). They contain direct translations of donor logic into Python and MUST NOT be carried over to V2.

1. **`core/developer/git.py`** (from `jarvis-main/src/sites/git-manager.ts`)
2. **`core/developer/github.py`** (from `jarvis-main/src/sites/github-manager.ts`)
3. **`core/workflows/*`** (implied origin, specifically `worker.py` and state machine concepts mapped to SQLite).

### C. Generic Architectural Concepts (KEEP)
- Use of SQLite for local state.
- Event bus architecture (`core/runtime/events`).
- The Model Gateway abstraction.

### D. Third-Party Dependencies
- V1 `requirements.txt` relies on standard open-source Python packages (e.g., `requests`, `pydantic`). These are safe, but must be explicitly audited and version-pinned in V2.

## Clean-Room Candidates & Strategy

To remove unnecessary licensing constraints from V2 while retaining useful capabilities, the following subsystems require clean-room engineering:

### 1. Developer Git Integration
- **Identify Requirements**: Inspect current repository status, branches, log, diff, merge, and remote pushing/pulling.
- **V2 Strategy**: Replace `git.py` with an implementation utilizing a robust underlying Python library like `GitPython` or standard subprocess abstractions without mirroring the donor's method signatures or workflow logic. Ensure independent testing and structure.

### 2. Developer GitHub Integration
- **Identify Requirements**: Issue tracking, PR fetching, and repo creation via GitHub API.
- **V2 Strategy**: Replace `github.py` with an implementation utilizing `PyGithub` or a freshly designed REST API wrapper with an entirely original object model that focuses on strict typing via `pydantic`.

### 3. Workflow Engine
- **Identify Requirements**: Asynchronous node execution, retries, exponential backoff, state persistence, agent/tool execution boundaries.
- **V2 Strategy**: The current SQLite-polling `WorkflowWorker` is primitive and donor-derived. V2 will introduce an independently designed, native Python async task queue (potentially utilizing `asyncio.Queue` + durable storage or a recognized workflow library if permissible). The schema and state transitions must be designed from scratch based purely on MARK's requirements, not translating the donor's `WorkflowRun` logic.
