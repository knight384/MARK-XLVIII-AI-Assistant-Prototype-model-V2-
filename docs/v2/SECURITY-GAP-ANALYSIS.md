# Security Gap Analysis

This document identifies security architecture gaps in the V1 baseline and outlines improvements for V2.

## 1. Sandbox Isolation (Critical)
**Current State**: V1 implements a `SandboxManager` that picks Docker if available, but falls back to a `HostRestrictedSandbox` for non-critical risks when Docker is absent.
**Gap**: As documented in `core/sandbox/command.py`, the `HostRestrictedSandbox` provides NO filesystem isolation, NO network isolation, and NO memory/CPU containment on Windows. It merely strips environment variables. This is a severe capability boundary failure.
**V2 Improvement**: 
- Eliminate the `HostRestrictedSandbox` for untrusted code execution.
- Implement strict containerized sandboxing (e.g., Docker, Podman, or microVMs). 
- If no true sandbox is available, the system MUST refuse to execute code that carries arbitrary side effects.

## 2. Capability Boundaries & ToolExecutor (High)
**Current State**: Tools are executed within the main process or delegated to the sandbox.
**Gap**: Some tools (like Git/GitHub interactions) run in the host process and use stored tokens. A confused-deputy attack via LLM hallucination or prompt injection could cause the agent to execute malicious git commands or leak tokens.
**V2 Improvement**:
- Move high-risk tools into isolated subprocesses or containers.
- Enforce strict Least Privilege Principles on tool credentials (e.g., use scoped, short-lived tokens instead of persistent PATs).
- Explicit approval boundaries must be fortified against SSRF and injection risks.

## 3. Sidecar and Device Authentication (Medium)
**Current State**: Remote devices authenticate and register capabilities.
**Gap**: Replay attacks or compromised sidecars might exploit the remote policy profile.
**V2 Improvement**:
- Implement robust JWT lifecycle management with short expiries and strict audience (`aud`) validation.
- Introduce device trust scoring and mutual TLS (mTLS) for remote execution endpoints.
- Capability versioning to prevent downgrade attacks.

## 4. Secret Management (Medium)
**Current State**: Secrets are managed in `core/config`.
**Gap**: Potential leakage of secrets into logs or memory dumps.
**V2 Improvement**:
- Implement memory-safe secret zeroing.
- Add robust log-scrubbing for API keys and tokens before writing to `core/logging_setup.py`.

## 5. Denial-of-Service / Resource Exhaustion (Medium)
**Current State**: The `WorkflowWorker` polls SQLite and executes steps, with some exponential backoff.
**Gap**: Concurrency limits and memory bounds on the main process are not strongly enforced. An infinite loop in an agent's reasoning could exhaust resources.
**V2 Improvement**:
- Implement strict timeouts and circuit breakers in `core/workflows`.
- Enforce strict memory limits for the agent runtime.
