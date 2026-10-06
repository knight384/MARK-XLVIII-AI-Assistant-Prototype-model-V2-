import asyncio
from benchmarks.harness import harness

async def run_eventbus_benchmarks():
    from core.runtime.events import EventBus, RuntimeEvent
    import uuid
    bus = EventBus()
    
    # 1. Scaling subscribers
    for sub_count in [1, 10, 100, 500]:
        bus = EventBus() # Reset
        calls = [0]
        for _ in range(sub_count):
            bus.subscribe(lambda e: calls.append(1))
            
        async def publish_event():
            bus.publish(RuntimeEvent(event_type="test", payload={}))
            
        await harness.run_benchmark(f"EventBus_{sub_count}_Subs_Publish", publish_event, iterations=500)

async def run_sqlite_concurrency():
    from core.workflows.store import WorkflowStore
    from core.workflows.models import WorkflowRun, WorkflowState
    import uuid
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "bench_concurrent.sqlite"
    store = WorkflowStore(db_path=db_path)
    
    async def concurrent_write():
        # SQLite underlying driver in Python handles locks, but we want to measure contention.
        # We will use asyncio.to_thread since standard sqlite3 is synchronous and blocking.
        def write():
            run = WorkflowRun(run_id=str(uuid.uuid4()), workflow_id="wf", status=WorkflowState.READY, inputs={})
            store.save_run(run)
        await asyncio.to_thread(write)
        
    await harness.run_concurrent_benchmark("SQLite_Concurrent_Writes_10_Workers", concurrent_write, concurrency=10, iterations_per_task=50)

async def run_api_benchmarks():
    from fastapi.testclient import TestClient
    from core.runtime.api import app
    client = TestClient(app)
    
    def get_health():
        client.get("/api/health")
        
    harness.run_sync_benchmark("API_Health_Sync", get_health, iterations=200)

async def main():
    print("Starting Upgraded V2 Benchmarks...")
    import core.runtime.app
    from core.runtime.mode import RuntimeMode
    from core.runtime.api import set_runtime
    runtime = core.runtime.app.MarkRuntime(mode=RuntimeMode.HEADLESS)
    set_runtime(runtime)
    await runtime.initialize()
    
    await run_eventbus_benchmarks()
    await run_sqlite_concurrency()
    await run_api_benchmarks()
    
    harness.dump_report("benchmarks/baseline.json")

if __name__ == '__main__':
    asyncio.run(main())
