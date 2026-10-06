import asyncio
from benchmarks.harness import harness

async def run_websocket_benchmarks():
    from core.channels.manager import ChannelManager
    
    manager = ChannelManager()
    
    # Simulate a websocket connection (using a mock object)
    class MockWebSocket:
        async def accept(self): pass
        async def send_text(self, text): pass
        async def send_bytes(self, b): pass
        async def receive_text(self): return "mock"
    
    # We will just test connection addition/removal overhead
    async def add_remove():
        ws = MockWebSocket()
        await manager.connect(ws, "client_1", "device_1", "group_1")
        await manager.disconnect("client_1")
        
    avg = await harness.run_benchmark("WebSocket_AddRemove", add_remove, iterations=1000)
    harness.record("WebSocket", "add_remove_latency_ms", avg)

async def main():
    print("Running WebSocket benchmarks...")
    await run_websocket_benchmarks()
    harness.dump_report("benchmarks/ws.json")
    print("WebSocket Benchmarks complete.")

if __name__ == '__main__':
    asyncio.run(main())
