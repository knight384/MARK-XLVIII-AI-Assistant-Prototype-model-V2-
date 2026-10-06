# Donor Function Map

## `GitManager.autoCommit`
- **Source**: `src/sites/git-manager.ts`
- **Purpose**: Checks for dirty state, adds all files, and commits with a given message.
- **Side effects**: Mutates local Git repository state.
- **V1 equivalent**: `GitIntelligence.auto_commit` (or similar Git wrappers).
- **V2 destination**: `core.developer.vcs` (Clean-room rewrite).
- **Decision**: REBUILD-CLEAN-ROOM. Will use purely Pythonic abstractions without carrying over donor structure.

## `Worker.runLoop`
- **Source**: `src/workflows/queue/worker.ts`
- **Purpose**: Infinite polling loop checking SQLite for unclaimed jobs.
- **Side effects**: Locks rows in SQLite, executes arbitrary handlers.
- **Concurrency sensitivity**: High (relies on DB-level locking `claimNextJob`).
- **V1 equivalent**: `WorkflowWorker._loop` / `_tick`.
- **V2 destination**: `core.workflows.queue`.
- **Decision**: REBUILD-CLEAN-ROOM. Will replace the polling model with a pub/sub or strictly async `asyncio.Queue` system to eliminate CPU overhead.

## `enrollDevice`
- **Source**: `src/sidecar/enrollment.ts`
- **Purpose**: Mints a JWT for a sidecar device, updating SQLite with the device state.
- **Security sensitivity**: High (Generates access credentials).
- **V1 equivalent**: Partial in `DeviceRegistry`.
- **V2 destination**: `core.devices.auth`.
- **Decision**: ADAPT. The cryptographic workflow (ES256 + JWT) is a standard pattern and will be cleanly implemented in Python.
