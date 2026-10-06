# MARK XLVIII V2 — PHASE 10 RELEASE NOTES

## Release Summary
The Phase 10 Release Candidate solidifies MARK XLVIII V2 into a deployable, hardened autonomous agent. It verifies execution boundaries, standardizes deployment flows across platforms, and guarantees complete detachment from V1 legacy architectures. 

## Major Architecture Characteristics
- **Core Security**: Strong Python execution boundary utilizing localized Docker sandboxes with path isolation. No `eval()` escapes or raw OS execution bypasses.
- **REST Surface**: API strictly bound to `127.0.0.1:8000` requiring explicit authentication. No unauthenticated broad-network exposure.
- **Sidecar Capabilities**: Hardened remote device abstraction written in Go. Mandates explicit device enrollment, verified by cryptographic JWTs mapped to the central Registry.
- **Headless & UI Degradation**: Degrades gracefully to CLI if UI (PyQt6/React) is unavailable. PyQt6 remains strictly optional and excluded from core packaging dependencies to respect open-source licensings (GPLv3).

## Security Hardening Completed
- Complete scrubbing of V1 donor code and `.bundle` backups. No accidental distribution of previous runtime.
- Removal of any unauthenticated bypasses from WebSocket Sidecar endpoints.
- Strict event execution and queue tracking in event-driven workflow engine.
- Bounded OS/File operations explicitly prohibiting `shell=True` and enforcing directory traversal limitations in Sandboxes.

## Known Issues and Limitations
- **Environment Limited**: The Go Sidecar could not be natively compiled within the test environment due to a missing Go toolchain (`ENVIRONMENT-LIMITED`).
- **UI Degradation**: UI fallback operates entirely on standard output/terminal rendering if Vite React bundles are not properly served or if PyQt6 is uninstalled.

## Supported Deployment Paths
- Local execution via standard python runtime: `python main.py`
- Background daemon deployment on isolated instances.

## Unsupported Scenarios
- Hosting Core API on `0.0.0.0` for web access. The dashboard LAN control is distinct and uses specialized one-time keys over AES-256 for network access.
- Deployments requiring execution of untrusted code without an available Docker runtime (System will "fail-closed" instead).
