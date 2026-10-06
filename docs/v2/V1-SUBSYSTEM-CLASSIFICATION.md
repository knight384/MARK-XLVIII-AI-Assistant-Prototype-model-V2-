# V1 Subsystem Classification

This document classifies every major V1 subsystem into one primary category: KEEP, IMPROVE, REPLACE, REMOVE, NEW.

Subsystem: `core/config`
Current V1 implementation: Centralized configuration and secrets manager.
Decision: KEEP
Reason: Lightweight, effective, and fulfills its role well.
Security impact: None, but could integrate with a more robust secrets backend.
Performance impact: Low.
Licensing/provenance impact: None (Original implementation).
Compatibility impact: Fully compatible.
V2 direction: Retain as the foundational configuration layer.
Priority: Low

Subsystem: `core/llm`
Current V1 implementation: Gateway abstraction for LLM providers (routing/fallback).
Decision: IMPROVE
Reason: Solid foundation but needs to expand to support multimodal inputs (audio/video/image) and deeper capability negotiations.
Security impact: Minimal, prompt injection mitigation improvements needed.
Performance impact: Needs better async latency management.
Licensing/provenance impact: None.
Compatibility impact: API extensions required.
V2 direction: Add robust multimodal processing capabilities and context streaming.
Priority: Medium

Subsystem: `core/tools`
Current V1 implementation: Tool registry and ToolExecutor.
Decision: IMPROVE
Reason: Needs stricter isolation between the executor and the policy engine, and capability versioning.
Security impact: High. Ensure strict execution boundaries.
Performance impact: Low.
Licensing/provenance impact: None.
Compatibility impact: Minor contract updates.
V2 direction: Harden tool boundaries and enforce strict typing/validation.
Priority: High

Subsystem: `core/agent`
Current V1 implementation: Agent abstraction and multi-agent runtime.
Decision: KEEP
Reason: Works well for the current task orchestration and awareness model.
Security impact: None.
Performance impact: Could be optimized for memory usage.
Licensing/provenance impact: None.
Compatibility impact: Maintain compatibility.
V2 direction: Refine prompts and state transitions.
Priority: Low

Subsystem: `core/memory`
Current V1 implementation: Layered persistent memory with Knowledge Graph.
Decision: IMPROVE
Reason: Needs better vector scaling and knowledge eviction strategies.
Security impact: Medium (privacy boundaries in memory).
Performance impact: High (database access optimizations needed).
Licensing/provenance impact: None.
Compatibility impact: Schema migrations may be needed.
V2 direction: Integrate richer vector databases or optimize SQLite usage.
Priority: Medium

Subsystem: `core/policy`
Current V1 implementation: PolicyEngine handling approvals and capability access.
Decision: IMPROVE
Reason: Needs richer remote policy profiles for sidecars and devices.
Security impact: High.
Performance impact: Low.
Licensing/provenance impact: None.
Compatibility impact: Extend policy schemas.
V2 direction: Implement device trust and remote policy enforcement.
Priority: Medium

Subsystem: `core/sandbox`
Current V1 implementation: DockerSandbox with a `HostRestrictedSandbox` fallback (which explicitly admits it is not real isolation).
Decision: REPLACE
Reason: The `HostRestrictedSandbox` is insecure and lacks true isolation on Windows (no rlimits, no filesystem boundary).
Security impact: Critical. SSRF, privilege escalation, and host compromise risks.
Performance impact: Real containers will add overhead.
Licensing/provenance impact: None.
Compatibility impact: Breaking if environment guarantees change.
V2 direction: Enforce a containerized sandbox architecture exclusively, or implement true microVMs (e.g. Firecracker/gVisor) depending on the host OS.
Priority: Critical

Subsystem: `core/runtime`
Current V1 implementation: Runtime API and lifecycle manager.
Decision: IMPROVE
Reason: Needs better graceful shutdown and startup metrics.
Security impact: Low.
Performance impact: Medium.
Licensing/provenance impact: None.
Compatibility impact: None.
V2 direction: Add enhanced observability boundaries.
Priority: Low

Subsystem: `core/developer`
Current V1 implementation: `git.py` and `github.py` adapted from donor project `jarvis-main`.
Decision: REPLACE
Reason: Donor-derived implementation introduces licensing constraints and technical debt.
Security impact: High (token management and execution risks).
Performance impact: None.
Licensing/provenance impact: Critical. Must be clean-room engineered.
Compatibility impact: APIs will need to be redesigned.
V2 direction: Clean-room implementation of Git/GitHub integrations relying on official Python libraries (e.g., PyGithub, GitPython) or clean wrapper interfaces.
Priority: High

Subsystem: `core/workflows`
Current V1 implementation: Background worker and state machine adapted from donor.
Decision: REPLACE
Reason: Donor-derived implementation introduces licensing constraints.
Security impact: Medium.
Performance impact: High (concurrency and queue polling optimizations needed).
Licensing/provenance impact: Critical. Must be clean-room engineered.
Compatibility impact: State schema changes required.
V2 direction: Design a new async event-driven workflow engine with better error recovery and scheduling.
Priority: High

Subsystem: `core/mission`, `core/awareness`, `core/goals`, `core/personality`
Current V1 implementation: Persistent proactive behavioral models.
Decision: KEEP
Reason: Core identity of the assistant, unique to V1 and fully original.
Security impact: Low.
Performance impact: Medium (LLM call overhead).
Licensing/provenance impact: None.
Compatibility impact: Retain compatibility.
V2 direction: Continue tuning and expanding contexts.
Priority: Low

Subsystem: `core/channels`, `core/devices`
Current V1 implementation: Multichannel voice, text, and sidecar remote device registry.
Decision: IMPROVE
Reason: Needs richer multimodal input (video/screen), bandwidth management, and secure remote execution.
Security impact: High (remote device trust).
Performance impact: High (streaming overhead).
Licensing/provenance impact: None.
Compatibility impact: Sidecar protocols will evolve.
V2 direction: Advanced device/sidecar platform with robust capability negotiation.
Priority: Medium
