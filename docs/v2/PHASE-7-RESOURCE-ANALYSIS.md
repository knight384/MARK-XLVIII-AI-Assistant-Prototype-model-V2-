# Phase 7: Resource Analysis

## Limits Evaluation
- MAX_FILE_SIZE (1MB) bounds memory during context extraction.
- ASGI connection limits protect WebSocket starvation.
- ThreadPoolExecutors restrict native/blocking code (e.g. SQLite blocking writes) from halting the syncio event loop.

## Idle Behavior
EventBus architecture natively prevents idle polling. CPU drops to ~0% during system idle states.
