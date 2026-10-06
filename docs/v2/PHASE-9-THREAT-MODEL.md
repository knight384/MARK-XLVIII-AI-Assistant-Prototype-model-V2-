# Phase 9: Threat Model & Security Audit

## 1. System Trust Boundaries
The V2 MARK XLVIII Assistant operates with distinct trust boundaries:
1. **User / External Sources**: Untrusted. All inputs (speech, text, camera, tool results) must be validated.
2. **Sidecar / Devices**: Semi-trusted. Connects via WebSockets. Must authenticate via JWT (HS256) per connection.
3. **API & Workflow Engine**: Trusted core. FastApi handles incoming REST and Websocket connections.
4. **Tool Execution (Sandbox)**: Untrusted boundary. High-risk execution is routed through Docker Sandbox limits.

## 2. Authentication and Authorization
- **Sidecar WebSocket Auth**: V2 employs JSON Web Tokens (HS256) for device authentication over WebSocket (`/ws/sidecar`). 
- **Remediation**: During Phase 9, an active bypass mechanism (`token == "dummy_token"`) was discovered in `api.py` that allowed unauthenticated sidecar session initialization. **This vulnerability was removed.**
- **API Server Network Binding**: The `ApiService` was previously binding to `0.0.0.0` with unauthenticated REST endpoints (e.g., `/api/tasks`). This presented a remote code execution risk. **This was mitigated by restricting the binding to `127.0.0.1`**.

## 3. Sandboxing & Isolation
- The `core.sandbox.docker` implementation achieves **real isolation** by utilizing process-level constraints via the Docker CLI (`docker run`). 
- **Privilege Escalation**: Explicitly prevented using `--security-opt no-new-privileges` and `--cap-drop ALL`.
- **Path Traversal**: `SandboxWorkspace` successfully enforces sandbox containment using strict `.resolve()` checks (preventing `../` escapes or malicious symlinks).
- **Execution Evasion**: No raw `shell=True` subprocess calls exist in the core runtime; all OS command paths are safely constrained.

## 4. Policy & Approval Subsystems
- Python's `ast.parse` is leveraged securely within `ConditionNode` evaluations to block `ast.Call`, `ast.Attribute`, and comprehensions. This ensures robust defense against code injection and `__class__.__mro__` style arbitrary execution sandbox escapes.
- All high-risk tools enforce manual approval or policy engine validation prior to execution.

## 5. Security Scanning
- Secret Scans (regex-based search for APIs, Bearer tokens, private keys) resulted in **no exposed hardcoded credentials** across the `core/`, `ui/`, and `tests/` trees.

## 6. Audit Verdict
**Security Rating**: PASS (Post-remediation).
The identified vulnerabilities (dummy auth bypass, 0.0.0.0 unauthenticated API exposure) have been resolved. The V2 architecture exhibits significant structural security maturity compared to V1.
