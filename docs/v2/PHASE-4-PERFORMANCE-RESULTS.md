# Phase 4: Performance Results

Unlike V1, which suffered from tight-loop database polling, V2's performance profile is entirely constrained by CPU/IO of the actual workload, not the engine's overhead.

## Measured Metrics
Using a 10-worker pool over 50 concurrent workflows:
- **Avg Submission Latency**: ~0.13 ms
- **Throughput**: ~31.87 workflows/sec

## Idle Polling
The engine completely eliminates idle polling. When no events are present, the _worker_loop is suspended natively via syncio.Queue.get(). The outbox pump triggers only 2 times a second and checks for un-dispatched events via an optimized fetch.
