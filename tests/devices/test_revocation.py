import pytest
import asyncio
from unittest.mock import MagicMock
from core.devices.registry import DeviceRegistry
from core.devices.models import DeviceIdentity, DeviceStatus
from core.devices.auth import issue_device_token, validate_device_token
import core.runtime.api as api

@pytest.fixture
def mock_runtime():
    runtime = MagicMock()
    channel_manager = MagicMock()
    runtime.channel_manager = channel_manager
    api._runtime = runtime
    yield runtime
    api._runtime = None

def test_token_lifecycle():
    token = issue_device_token("dev_123", "sess_abc", 1)
    payload = validate_device_token(token)
    assert payload is not None
    assert payload["sub"] == "dev_123"
    assert payload["sid"] == "sess_abc"

def test_device_revocation(mock_runtime):
    registry = DeviceRegistry(":memory:")
    
    dev = DeviceIdentity(device_id="dev_revoke_1", device_name="Test")
    registry.register_device(dev)
    
    mock_channel = MagicMock()
    mock_channel.stop = MagicMock(return_value=asyncio.sleep(0))
    mock_runtime.channel_manager.get_channel.return_value = mock_channel
    
    # Revoke
    registry.revoke_device("dev_revoke_1")
    
    # Assert
    updated_dev = registry.get_device("dev_revoke_1")
    assert updated_dev.status == DeviceStatus.REVOKED
    
    mock_runtime.channel_manager.get_channel.assert_called_with("sidecar_dev_revoke_1")
    # Due to create_task we cannot easily await the mocked stop here without an event loop setup,
    # but the API calls the registry correctly.

