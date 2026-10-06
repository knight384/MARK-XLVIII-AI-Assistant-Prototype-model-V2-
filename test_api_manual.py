import pytest
from fastapi.testclient import TestClient
from core.runtime.api import app, set_runtime
from core.runtime.app import MarkRuntime
from core.runtime.mode import RuntimeMode

client = TestClient(app)

runtime = MarkRuntime(mode=RuntimeMode.HEADLESS)
set_runtime(runtime)
response = client.get("/health")
print(response.status_code)
print(response.text)
