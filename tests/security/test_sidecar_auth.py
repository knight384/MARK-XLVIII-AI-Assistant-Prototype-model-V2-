import pytest
import jwt
import uuid
import asyncio
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect

from core.runtime.api import app
from core.devices.auth import issue_device_token, _JWT_SECRET
from core.devices.registry import get_default_device_registry
from core.devices.models import DeviceIdentity, DeviceStatus, ConnectionState

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_registry():
    reg = get_default_device_registry()
    # Clear registry for tests
    reg._init_db() # Ensure db is ready
    with reg._get_conn() as conn:
        conn.execute("DELETE FROM devices")
    
    # Add a valid device
    reg.register_device(DeviceIdentity(
        device_id="test_device_valid",
        device_name="Valid Test Device",
        device_type="PHONE",
        platform="android",
        client_version="1.0",
        capabilities=[],
        status=DeviceStatus.ENROLLED,
        connection_state=ConnectionState.DISCONNECTED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    ))
    
    # Add a revoked device
    reg.register_device(DeviceIdentity(
        device_id="test_device_revoked",
        device_name="Revoked Test Device",
        device_type="PHONE",
        platform="android",
        client_version="1.0",
        capabilities=[],
        status=DeviceStatus.REVOKED,
        connection_state=ConnectionState.DISCONNECTED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    ))
    
    yield reg

from core.runtime.app import MarkRuntime
from core.runtime.mode import RuntimeMode
from core.runtime.api import set_runtime

@pytest.fixture(autouse=True)
def setup_runtime():
    rt = MarkRuntime(mode=RuntimeMode.HEADLESS)
    set_runtime(rt)
    yield rt
    set_runtime(None)

def test_sidecar_rejects_invalid_token():
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/sidecar") as websocket:
            websocket.send_json({"token": "not_a_real_token", "device_id": "test_device_valid"})
            websocket.receive_text()
    assert exc.value.code == 1008
    assert "Invalid or expired token" in exc.value.reason

def test_sidecar_rejects_expired_token():
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "test_device_valid",
        "sid": "session123",
        "jti": str(uuid.uuid4()),
        "aud": "mark_v2_core",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
        "iss": "mark_v2_core"
    }
    expired_token = jwt.encode(payload, _JWT_SECRET, algorithm="HS256")
    
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/sidecar") as websocket:
            websocket.send_json({"token": expired_token, "device_id": "test_device_valid"})
            websocket.receive_text()
    assert exc.value.code == 1008

def test_sidecar_rejects_missing_token():
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/sidecar") as websocket:
            websocket.send_json({"device_id": "test_device_valid"})
            websocket.receive_text()
    assert exc.value.code == 1008
    assert "Invalid or expired token" in exc.value.reason

def test_sidecar_rejects_device_id_mismatch():
    token = issue_device_token("test_device_valid", "session123", duration_hours=24)
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/sidecar") as websocket:
            websocket.send_json({"token": token, "device_id": "some_other_device"})
            websocket.receive_text()
    assert exc.value.code == 1008
    assert "Token device mismatch" in exc.value.reason

def test_sidecar_rejects_unknown_device():
    token = issue_device_token("unknown_device", "session123", duration_hours=24)
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/sidecar") as websocket:
            websocket.send_json({"token": token, "device_id": "unknown_device"})
            websocket.receive_text()
    assert exc.value.code == 1008
    assert "Unknown device" in exc.value.reason

def test_sidecar_rejects_revoked_device():
    token = issue_device_token("test_device_revoked", "session123", duration_hours=24)
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/sidecar") as websocket:
            websocket.send_json({"token": token, "device_id": "test_device_revoked"})
            websocket.receive_text()
    assert exc.value.code == 1008
    assert "Device revoked" in exc.value.reason

def test_sidecar_accepts_valid_matching_device(setup_runtime):
    token = issue_device_token("test_device_valid", "session123", duration_hours=24)
    
    rt = setup_runtime
    import threading
    
    # We will connect and immediately close to verify it got registered
    def _client_thread():
        try:
            with client.websocket_connect("/ws/sidecar") as websocket:
                websocket.send_json({"token": token, "device_id": "test_device_valid"})
                # Wait briefly so server registers it
                import time
                time.sleep(0.5)
        except Exception:
            pass

    t = threading.Thread(target=_client_thread)
    t.start()
    
    # Poll for registration
    import time
    registered = False
    for _ in range(10):
        ch = rt.channel_manager.get_channel("sidecar_test_device_valid")
        if ch:
            registered = True
            break
        time.sleep(0.1)
        
    t.join()
    assert registered, "Authenticated channel was not successfully registered in ChannelManager"
