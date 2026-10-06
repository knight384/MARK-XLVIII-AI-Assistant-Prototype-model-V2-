# Phase 2 Developer Integrations

## Architecture Overview

The V2 Developer Subsystem (`core/developer`) replaces the legacy, donor-derived tooling from V1. It provides bounded, isolated, and policy-compliant abstractions for source code and repository management.

- **`models.py`**: Defines structured types (`GitStatus`, `GitCommit`, `ProjectIndex`, `SearchResult`) avoiding ad-hoc dictionaries.
- **`git.py`**: A strict wrapper around Git subprocess invocation. Never uses `shell=True`. Bounds execution timeouts, redacts URL credentials dynamically, and enforces strict boundary containment to prevent traversal escapes. Exposes `READ`, `WRITE` operations distinctly.
- **`github.py`**: A clean API client using `urllib.request`. Fetches tokens exclusively from MARK's `ConfigService`. Never logs tokens or full request/response bodies that might leak authorization boundaries.
- **`project.py`**: Provides repository scanning to identify structure and languages. Restricts scale via `MAX_FILES = 10_000` to prevent deep recursion DOS.
- **`search.py`**: Implements code search with bounds on file size (`1MB`) and result count. Includes timeboxing to fail safe on huge repos.
- **`context.py`**: A secure context extractor returning snippets around specific file lines, preventing path traversal and massive file loads.
- **`tools.py`**: Connects the abstraction to the `ToolExecutor`. Classifies `WRITE` actions like git commit/push and github repository creation with `RiskLevel.HIGH` or `RiskLevel.MEDIUM`, requiring strict confirmation in the Policy Engine.

## Security Model

The subsystem enforces strict boundaries:
- **No Arbitrary Shell**: `git` operations invoke binaries directly via array arguments. There is no `git <arbitrary_string>`.
- **Policy Enforcement**: Write actions flow into the Agent Tool registry where they are subjected to standard V2 PolicyEngine scrutiny. No bypass exists. 
- **Path Traversal Protection**: Every repository operation validates that its working paths reside within the requested workspace.
- **Sandbox Integration**: The developer tools themselves execute on the host (as they manipulate host workspace files) but they *cannot execute arbitrary project code*. Tests or builds must be routed through the dedicated execution sandbox mechanism established in Phase 1.

## Windows Considerations

The subsystem leverages standard `pathlib.Path` ensuring backslashes and drive letters are safely processed and compared. Subprocess calls are cross-platform compatible.

## Limitations

- **Git Subprocess Dependency**: Requires a host `git` installation. Fallback to `GitPython` or `pygit2` is intentionally avoided to minimize unreviewed C-bindings/dependencies.
- **Token Injection**: Push/Pull using HTTPS requires native git credentials or credential helpers. The `github.py` abstraction handles API actions but `git.py` does not currently inject ephemeral tokens into `.git/config`.
