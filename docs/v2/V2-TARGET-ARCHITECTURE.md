# V2 Target Architecture

After auditing the V1 baseline, the target architecture for V2 will refine boundaries, enforce stricter security guarantees, and eliminate donor-derived logic through clean-room implementations.

## Architectural Boundaries

### 1. Process Boundaries
- **Core Runtime**: The main Python process handling orchestration, policy, and memory.
- **Sandbox Boundary**: Strict Subprocess/Container separation. V2 will completely remove the insecure `HostRestrictedSandbox`. Untrusted code MUST run in a container (Docker/Podman) or a secure microVM boundary. The boundary crosses IPC/RPC interfaces.
- **Go Sidecar Boundary**: Remote sidecars (written in Go) operate entirely out-of-process. They act as edge devices connecting via mTLS/WSS and authenticating via JWT. The Core Runtime considers the Sidecar an untrusted external entity restricted to its registered capabilities.
- **Tool Boundary**: High-risk tools (e.g., executing system commands, modifying the filesystem outside the workspace) will operate strictly outside the sandbox but under intense PolicyEngine scrutiny. Low-risk generated code executes *only* in the sandbox.

### 2. Package & Module Boundaries
- `core.llm`: Gateway abstractions. (Trusted, in-process)
- `core.agent`: Orchestration and prompting. (Trusted, in-process)
- `core.workflows`: Clean-room event-driven async task engine. (Trusted, in-process logic + durable database)
- `core.developer`: Clean-room source control logic. (Trusted, interacts with external network APIs)
- `core.sandbox`: Security boundary manager. (Trusted manager, untrusted container payloads)

### 3. LLM / Provider Boundary
- **Network/Service Boundary**: The system communicates with external LLMs over HTTPS.
- **Security Check**: Responses crossing back from the LLM boundary must be treated as untrusted input. Prompt injection checks and strict JSON validation (via `pydantic`) act as the first line of defense before passing data to the ToolExecutor or Workflow Engine.

### 4. Memory / Knowledge Boundary
- Local SQLite/Vector database.
- Data written here is considered internal, but PII/secrets must not be leaked into persistent knowledge graphs without scrubbing.

### 5. API & MCP Boundary
- **MCP (Model Context Protocol)**: Exposes tool and resource contracts to standard clients.
- **Security Check**: The API boundary must employ strict authentication (JWT) and authorize actions via the `PolicyEngine` before reaching the `ToolExecutor`.

## Compatibility Strategy

- **Retain Compatibility**: 
  - The fundamental `Agent` and `Mission` concepts.
  - The Configuration structures (with minor extensions).
- **Breaking Changes**:
  - The Sandbox API. Fallback host execution is removed. If Docker is missing, sandboxed tools fail closed.
  - Workflow database schema and states (necessitated by clean-room rewrite).
  - Developer APIs (`GitIntelligence` / `GitHubIntelligence` will have new, Pythonic contracts).

## Testing Strategy
- **Unit Testing**: Focus heavily on the new clean-room implementations (Workflows, Git, GitHub).
- **Security & Sandbox Testing**: Rigorous testing to ensure the container boundary cannot be bypassed, and that the absence of Docker properly fails securely.
- **Concurrency Testing**: For the new async workflow engine.
- **Licensing Validation**: Automated checks to ensure no donor modules are reintroduced.
