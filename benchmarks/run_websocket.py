import asyncio
from benchmarks.harness import harness

async def run_websocket_benchmarks():
    from core.channels.manager import ChannelManager
    from core.channels.websocket import WebSocketChannel
    
    manager = ChannelManager()
    
    # We will simulate registering channels
    async def add_remove():
        channel_id = "client_1"
        # Channel is abstract, we should use a concrete implementation or mock
        # But we'll just test the manager's lock contention
        from unittest.mock import MagicMock
        from core.channels.base import Channel, ChannelType
        
        mock_chan = MagicMock(spec=Channel)
        mock_chan.channel_id = channel_id
        mock_chan.channel_type = ChannelType.WEBSOCKET
        
        manager.register_channel(mock_chan)
        manager.unregister_channel(channel_id)
        
    await harness.run_concurrent_benchmark("WebSocket_AddRemove_100_Workers", add_remove, concurrency=100, iterations_per_task=10)

async def main():
    print("Starting Additional Benchmarks...")
    import core.runtime.app
    from core.runtime.mode import RuntimeMode
    runtime = core.runtime.app.MarkRuntime(mode=RuntimeMode.HEADLESS)
    await runtime.initialize()
    
    await run_websocket_benchmarks()
    
    harness.dump_report("benchmarks/ws.json")

if __name__ == '__main__':
    asyncio.run(main())
