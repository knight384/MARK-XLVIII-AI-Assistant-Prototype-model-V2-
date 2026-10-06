# Phase 3: Event-Driven Workflow Engine - Provenance

## Independence Declaration
The workflow engine for MARK XLVIII V2 has been completely and independently implemented from scratch. The donor workflow engine (jarvis-main) was used only as a reference for capability and behavior requirements (as documented in the Phase 0.5 extraction documentation).

**No donor source code was copied, imported, or translated.**

## Component Provenance

### 1. Workflow Models (core.workflows.models)
- **V2 Requirement:** Need strongly typed workflow and step definitions.
- **Architectural Basis:** Pydantic models for deterministic serialization and schema validation.
- **Implementation Origin:** Clean-room V2 implementation.
- **Donor Reference:** src/workflows/runtime/types (for understanding required state enums like RUNNING, WAITING).

### 2. Event Bus (core.workflows.events)
- **V2 Requirement:** Asynchronous event dispatcher with bounded queues and backpressure.
- **Architectural Basis:** asyncio.Queue with timeout handling to prevent slow consumers from crashing the dispatcher.
- **Implementation Origin:** Clean-room V2 implementation.
- **Donor Reference:** None directly; donor used a synchronous or global queue model which was prone to blocking.

### 3. Workflow Engine (core.workflows.engine)
- **V2 Requirement:** Event-driven orchestration of workflows and steps.
- **Architectural Basis:** Async tasks subscribing to the event bus, queuing ready steps, and processing them via a bounded worker pool.
- **Implementation Origin:** Clean-room V2 implementation.
- **Donor Reference:** src/workflows/runtime/engine (to understand node dependencies and completion conditions).

### 4. Workflow Store (core.workflows.store)
- **V2 Requirement:** Durable persistence for workflows, runs, and outbox events.
- **Architectural Basis:** SQLite with WAL mode, avoiding tight-loop SELECT polling.
- **Implementation Origin:** Clean-room V2 implementation.
- **Donor Reference:** src/workflows/db (for understanding the necessary tables).

### 5. Node Executors (core.workflows.nodes.*)
- **V2 Requirement:** Execution nodes for Agent, Tool, Condition, Wait, and Notification operations.
- **Architectural Basis:** Safe Python AST evaluation (Condition), V2 Orchestrator integration (Agent), V2 ToolExecutor (Tool) with pre-execution PolicyEngine checks.
- **Implementation Origin:** Clean-room V2 implementation.
- **Donor Reference:** src/workflows/runtime/nodes.
