import pytest
import asyncio
from core.channels.sidecar import SidecarChannel
from core.channels.base import ChannelEvent, ChannelMessage

class MockWebSocket:
    def __init__(self):
        self.sent = []
        self.received = []
        self.closed = False
        
    async def receive(self):
        if not self.received:
            await asyncio.sleep(0.1)
            raise Exception("Disconnected")
        return self.received.pop(0)
        
    async def send_json(self, data):
        self.sent.append(data)
        
    async def send_bytes(self, data):
        self.sent.append(data)
        
    async def close(self, code=1000, reason=""):
        self.closed = True

class MockManager:
    def __init__(self):
        self.messages = []
    
    async def _handle_channel_message(self, msg):
        self.messages.append(msg)

@pytest.mark.asyncio
async def test_sidecar_channel_lifecycle():
    ws = MockWebSocket()
    channel = SidecarChannel("device_1", ws, None)
    
    manager = MockManager()
    channel.set_on_message(manager._handle_channel_message)
    
    await channel.start()
    assert channel.state == "READY"
    assert len(ws.sent) > 0 # Initial event sent maybe
    
    await channel.send_text("Hello sidecar")
    assert ws.sent[-1] == {"type": "text_message", "text": "Hello sidecar"}
    
    await channel.send_rpc_response("req_123", result={"ok": True})
    assert ws.sent[-1] == {"type": "rpc_response", "id": "req_123", "result": {"ok": True}}
    
    await channel.stop()
    assert channel.state == "DISCONNECTED"
    assert ws.closed == True
