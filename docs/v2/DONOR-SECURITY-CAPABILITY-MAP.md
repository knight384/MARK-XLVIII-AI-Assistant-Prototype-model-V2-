# Donor Security Capability Map

## JWT-based Device Enrollment
- **What it does**: Mints ES256 JSON Web Tokens (JWTs) for sidecar authentication (`src/sidecar/enrollment.ts`). Uses a locally generated keypair.
- **Security value**: Strong, stateless verification of connected devices. Prevents unauthorized edge devices from joining the network.
- **Security weaknesses**: If the `private.pem` file is compromised, an attacker can mint valid tokens. No hardware-backed enclave is used.
- **V1 equivalent**: V1 Sidecar authentication has partial/dummy implementations.
- **V2 decision**: ADAPT. V2 will adopt standard JWT verification using a robust Python cryptography library.

## File Permission Enforcement
- **What it does**: `secureKeyFilePermissions` enforces `chmod 600` on private keys.
- **Security value**: Prevents other unprivileged local users from stealing the assistant's keys.
- **Security weaknesses**: Windows support for `chmod 600` equivalents (ACLs) is often poorly mapped in cross-platform tools.
- **V1 equivalent**: V1 config sets file permissions, but could be stricter.
- **V2 decision**: ADAPT. Ensure Windows ACLs are properly applied using `icacls` or Python's `win32security` bindings.

## WebSocket RPC Security
- **What it does**: Encapsulates RPC calls over WebSocket (`src/sidecar/protocol.ts`).
- **Security value**: Isolates command payloads and enforces structured JSON/Binary limits.
- **Security weaknesses**: Relies entirely on the outer TLS/WSS layer for confidentiality. If WSS is downgraded to WS, interception is trivial.
- **V1 equivalent**: Unknown/Absent.
- **V2 decision**: ADAPT. V2 will enforce WSS/mTLS strictly for remote devices.
