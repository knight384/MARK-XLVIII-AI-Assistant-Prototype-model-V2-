import asyncio
from benchmarks.harness import harness

async def run_eventbus_benchmarks():
    from core.runtime.events import EventBus, RuntimeEvent
    bus = EventBus()
    
    # 1. 1 Subscriber
    calls_1 = [0]
    def sub_1(e): calls_1[0] += 1
    bus.subscribe(sub_1)
    
    async def publish_event():
        bus.publish(RuntimeEvent(event_type="test.event", payload={"msg": "hello"}))
        
    avg = await harness.run_benchmark("EventBus_1_Subscriber_Publish", publish_event, iterations=1000)
    harness.record("EventBus", "1_sub_latency_ms", avg)
    
    # 2. 50 Subscribers
    for i in range(49):
        bus.subscribe(lambda e: None)
        
    avg = await harness.run_benchmark("EventBus_50_Subscribers_Publish", publish_event, iterations=1000)
    harness.record("EventBus", "50_sub_latency_ms", avg)

async def run_workflow_db_benchmarks():
    from core.workflows.store import WorkflowStore
    from core.workflows.models import WorkflowRun, WorkflowState
    import uuid
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "bench.sqlite"
    store = WorkflowStore(db_path=db_path)
    
    def insert_run():
        run_id = str(uuid.uuid4())
        run = WorkflowRun(run_id=run_id, workflow_id="test_wf", status=WorkflowState.READY, inputs={})
        store.save_run(run)
        
    avg = harness.run_sync_benchmark("WorkflowDB_Insert", insert_run, iterations=500)
    harness.record("Persistence", "insert_latency_ms", avg)

async def run_api_benchmarks():
    from fastapi.testclient import TestClient
    from core.runtime.api import app
    client = TestClient(app)
    
    def get_health():
        client.get("/api/health")
        
    avg = harness.run_sync_benchmark("API_Health", get_health, iterations=500)
    harness.record("API", "health_latency_ms", avg)

async def main():
    print("Starting V2 Benchmarks...")
    import core.runtime.app
    runtime = core.runtime.app.MarkRuntime()
    await runtime.initialize()
    
    await run_eventbus_benchmarks()
    await run_workflow_db_benchmarks()
    await run_api_benchmarks()
    
    harness.dump_report()
    print("Benchmarks complete. Baseline saved to benchmarks/baseline.json")

if __name__ == '__main__':
    asyncio.run(main())
