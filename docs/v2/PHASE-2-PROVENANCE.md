# Phase 2 Provenance

## Developer Subsystem (`core/developer`)

This phase completely rebuilds the developer intelligence capabilities for MARK XLVIII V2. The donor implementation from `jarvis-main` has been entirely discarded and not copied, per the Phase 2 requirements. 

### Module: `models.py`
- **Requirement Source**: V2 Feature Catalog / Phase 2 Objectives
- **V1 Relationship**: None directly. Replaces untyped dictionaries from V1.
- **Donor capability reference**: Inspired by `git-manager.ts` and `github-manager.ts` returning structured state.
- **Implementation origin**: Independently authored for V2 using standard Python `dataclasses`.
- **Security review**: Data structures only. Safe by default.
- **Tests**: Implicitly tested by subsystem integration tests.

### Module: `git.py`
- **Requirement Source**: V2 Feature Catalog / Phase 2 Objectives (Git repository intelligence and operations).
- **V1 Relationship**: Replaces `core/developer/git.py` from V1, which was a donor-derived implementation.
- **Donor capability reference**: `git-manager.ts`
- **Implementation origin**: Independently authored for V2. Uses `subprocess.run` with `shell=False`.
- **Security review**: No shell injection possible. Paths are validated to prevent traversal outside the workspace boundary. Bounded output sizes to prevent memory DOS. Implicit secret redaction applied to git command string representation for error logs.
- **Tests**: `tests/developer/test_git.py`

### Module: `github.py`
- **Requirement Source**: V2 Feature Catalog / Phase 2 Objectives (GitHub operations).
- **V1 Relationship**: Replaces `core/developer/github.py` from V1, which was donor-derived.
- **Donor capability reference**: `github-manager.ts`
- **Implementation origin**: Independently authored for V2. Uses standard library `urllib.request`.
- **Security review**: Tokens are fetched dynamically from `ConfigService`. No hardcoded tokens. Tokens are passed exclusively via Authorization headers, never in URLs. Error handling catches and prevents logging raw HTTP responses that could contain sensitive request data.
- **Tests**: `tests/developer/test_github.py`

### Module: `project.py`
- **Requirement Source**: Phase 2 Objectives (Project Inspection).
- **V1 Relationship**: Replaces previous `ProjectAnalyzer` in V2 with a bounded version.
- **Implementation origin**: Independently authored for V2.
- **Security review**: Introduced `MAX_FILES` limit to prevent deep scanning DOS. Safe path resolution.
- **Tests**: `tests/developer/test_project.py`

### Module: `search.py`
- **Requirement Source**: Phase 2 Objectives (Bounded Code Search).
- **V1 Relationship**: Replaces the V1 `DeveloperCodeSearchTool` internal logic.
- **Implementation origin**: Independently authored for V2.
- **Security review**: Implemented time constraints, max file sizes (1MB), and max result limits.
- **Tests**: `tests/developer/test_search.py`

### Module: `context.py`
- **Requirement Source**: Phase 2 Objectives (Source Context).
- **V1 Relationship**: New to V2 developer toolkit abstraction.
- **Implementation origin**: Independently authored for V2.
- **Security review**: Strict path traversal checks, file size constraints, and line bounds.
- **Tests**: `tests/developer/test_context.py`

### Module: `tools.py`
- **Requirement Source**: Phase 2 Objectives (Developer Tool Contracts).
- **V1 Relationship**: Defines standard `Tool` subclasses replacing V1 equivalents.
- **Implementation origin**: Independently authored for V2.
- **Security review**: Correctly assigns `RiskLevel` (e.g. `HIGH` for git push and repo creation). Write tools explicitly require confirmation.
- **Tests**: `tests/developer/test_tools.py`

**Donor code:** NOT copied.
