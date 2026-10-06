# Phase 6: Native Go Sidecar Architecture

## Overview
The V2 Native Go Sidecar operates as an external edge process designed to provide native OS and device capabilities to the Python MARK core over an authenticated, encrypted, and multiplexed WebSocket connection.

## Process Architecture
- **Language**: Go 1.21+
- **Location**: sidecar/ module
- **Roles**: Extends OS access capabilities without granting implicit trust. 
- **Security Boundary**: The sidecar CANNOT execute Python tools directly, CANNOT authorize its own requests, and CANNOT bypass the V2 PolicyEngine or ApprovalManager.

## Transport & Protocol
- **Transport**: WebSockets (WSS + TLS).
- **Authentication**: JWT Bearer tokens utilizing HS256 signatures for edge-to-core validation.
- **Protocol**: Versioned (1.0.0) JSON-RPC messages mapping capabilities to strict payloads.

## Enrollment & Identity
- Devices are registered in the Python core DeviceRegistry.
- Sidecars generate an ephemeral or permanent device identity (stored in identity.json or .config depending on OS permissions).
- A short-lived JWT token is issued to the Sidecar, allowing authenticated WebSocket access for bounded durations (e.g. 24 hours). 

## Capabilities Model
The capability model exposes abstractions over OS-specific interfaces:
1. sidecar/platform/windows (Windows 10.0+ implementation capabilities).
2. sidecar/platform/linux (Subset implementation capabilities).
3. sidecar/platform/darwin (macOS capabilities dependent on explicit permissions).

## Multimodal Integration
The Sidecar feeds natively into the Phase 5 Multimodal boundaries via SidecarChannel. All raw capabilities (like Camera/Mic streams) are sent via websocket.send_bytes, which the V2 core converts into constrained MultimodalContext payloads.
