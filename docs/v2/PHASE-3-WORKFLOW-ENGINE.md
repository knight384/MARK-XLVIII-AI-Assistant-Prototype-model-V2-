# V2 Event-Driven Workflow Engine

## Architecture

The V2 Workflow Engine replaces the V1 database-polling model with a true asynchronous, event-driven architecture. 

### Core Components
1. **Event Bus (core.workflows.events.EventBus)**: An in-memory, asyncio-based event dispatcher. It uses bounded queues with timeout backpressure to ensure slow subscribers (e.g., websocket broadcasters) do not crash the runtime or block critical paths.
2. **Workflow Engine (core.workflows.engine.WorkflowEngine)**: The central orchestrator. It subscribes to events (WORKFLOW_STARTED, STEP_QUEUED, etc.) and transitions workflow/step states. It runs a bounded pool of asyncio tasks (_worker_loop) to process queued steps.
3. **Workflow Store (core.workflows.store.WorkflowStore)**: SQLite-backed durable persistence. Handles saving state transitions. Implements the Outbox pattern for durable event delivery.

## Execution Flow (Idempotency & Durability)

1. **Trigger**: An API call or Mission schedules a workflow.
2. **Initialization**: The Engine creates a WorkflowRun and saves it to the Store alongside a WORKFLOW_STARTED event in the Outbox.
3. **Event Delivery**: The Engine's Outbox Pump pulls the event from the DB and publishes it to the Event Bus.
4. **Resolution**: The Engine catches WORKFLOW_STARTED, resolves dependencies, and queues steps with no dependencies by saving WorkflowStepRun (state: QUEUED) and a STEP_QUEUED outbox event.
5. **Execution**: The STEP_QUEUED event is placed on the Engine's internal bounded queue. A worker pops it, transitions the step to RUNNING, and executes the node.
6. **Completion**: The node returns a result. The state updates to COMPLETED, emitting STEP_COMPLETED. The Engine evaluates dependencies and queues downstream steps.

## Security & Effect Boundary
- **Tool Node**: Explicitly passes through PolicyEngine (verifying tool execution limits/rules) *before* ToolExecutor runs.
- **Agent Node**: Passes execution to the V2 Orchestrator, keeping prompt isolation native.
- **Condition Node**: Uses safe st traversal and eval with tightly restricted globals to evaluate logic, preventing arbitrary code execution.
- **Wait Node**: Returns a waiting=True signal instead of executing syncio.sleep(). The worker is freed immediately.

## Recovery
On Engine start, it scans for RUNNING or QUEUED steps and resubmits them as QUEUED, ensuring recovery of incomplete work across restarts.
