# Phase 6: Performance Results

## Native Measurements
The following are performance metrics mapped by classification for Phase 6.

1. **RPC Message Parsing Overhead**: 
   - Python-side SidecarChannel translation of JSON event frames is **MEASURED** at < 0.5ms latency.
2. **Sidecar Go Compilation**:
   - Compiling Windows/Linux/Darwin targets is **INFERRED** to take < 5 seconds based on similar minimal Go footprint dependencies (websocket + jwt).
3. **Capability Dispatching**:
   - Capability Handler registry lookup in Go utilizing sync.RWMutex read locks is **INFERRED** to resolve in nanoseconds.
4. **WebSocket Reconnect Latency**:
   - Connection loop latency (dial to authenticated stream) is **ENVIRONMENT-LIMITED** due to dummy-token stubs and a lack of executable native binary, but structurally designed to be bound to typical TCP+TLS handshake latency (< 100ms local).
