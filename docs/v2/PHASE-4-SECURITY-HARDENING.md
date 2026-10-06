# Phase 4: Security Hardening

## Policy Duplication Review
During the initial Phase 3 implementation, ToolNode independently invoked PolicyEngine. We identified this as a duplicate authorization boundary since ToolExecutor already natively implements a strict PolicyEngine evaluation chain. 
**Resolution:** The redundant check in ToolNode was removed. ToolExecutor is now the single, authoritative point of validation for all tool effects, ensuring uniform auditing and decision enforcement regardless of how the tool is invoked (Workflow, Agent, API, or Sidecar).

## API & WebSocket Boundaries
The WebSocket endpoints were reviewed. A strict 1MB message size limit was implemented in pi.py to prevent memory exhaustion from oversized JSON payloads. Unrecognized messages are safely dropped.

## Sandbox & Host Fallback
We verified that SandboxManager is completely locked down against host fallback in V2. If the Docker backend is unavailable and a HIGH risk tool is executed, it deterministicly fails with SandboxUnavailableError. No hidden host execution paths remain.

## Secret Auditing
The codebase leverages SecretStore. Secrets are actively redacted via Phase 1 mechanisms and ToolExecutor argument redaction before reaching the database, the logs, or the EventBus payloads.

## Dependency Review
No new dependencies were added in Phase 4. pytest and syncio cover the entirety of the execution verification scope.
