import pytest
import asyncio
import logging
import json
from io import StringIO
from unittest.mock import patch, MagicMock
from collections import deque
import sqlite3

from core.observability import TraceContext
from core.observability.logger import StructuredFormatter, configure_structured_logging
from core.observability.metrics import registry, ComponentState
from core.observability.service import observability_service
from core.workflows.store import track_sqlite
from core.logging_setup import _sensitive_filter

@pytest.fixture
def clean_registry():
    # Clear registry manually for tests
    registry._counters.clear()
    registry._gauges.clear()
    registry._histograms.clear()
    registry._components_health.clear()
    yield registry

@pytest.mark.asyncio
async def test_trace_context():
    TraceContext.initialize()
    ctx = TraceContext.get_context_dict()
    assert "trace_id" in ctx
    
    # Test setting values
    TraceContext.initialize(request_id="req-1", trace_id=ctx["trace_id"])
    assert TraceContext.get_context_dict()["request_id"] == "req-1"

    # Test clearing
    TraceContext.clear()
    assert "request_id" not in TraceContext.get_context_dict()
    assert "trace_id" not in TraceContext.get_context_dict()

@pytest.mark.asyncio
async def test_structured_logging_redaction():
    # Setup structured logging to a string buffer
    logger = logging.getLogger("test_structured")
    logger.setLevel(logging.INFO)
    
    buffer = StringIO()
    handler = logging.StreamHandler(buffer)
    formatter = StructuredFormatter()
    handler.setFormatter(formatter)
    
    # Crucial: attach the redaction filter to the handler just like logging_setup
    handler.addFilter(_sensitive_filter)
    logger.addHandler(handler)
    
    TraceContext.initialize()
    ctx = TraceContext.get_context_dict()
    trace_id = ctx.get("trace_id")
    
    _sensitive_filter.add_secret("sk-live-1234567890abcdef")
    logger.info("Connecting with token=sk-live-1234567890abcdef")
    
    output = buffer.getvalue().strip()
    assert output
    
    log_dict = json.loads(output)
    assert log_dict["level"] == "INFO"
    assert log_dict["name"] == "test_structured"
    assert "sk-live-1234567890abcdef" not in log_dict["message"]
    assert "***REDACTED***" in log_dict["message"]
    assert log_dict["trace_id"] == trace_id
    
    logger.removeHandler(handler)

@pytest.mark.asyncio
async def test_registry_metrics(clean_registry):
    await clean_registry.inc("test_counter", 5)
    await clean_registry.set_gauge("test_gauge", 42.0)
    await clean_registry.observe("test_hist", 10.0)
    await clean_registry.observe("test_hist", 20.0)
    
    snapshot = await clean_registry.get_metrics_snapshot()
    assert snapshot["counters"]["test_counter"] == 5
    assert snapshot["gauges"]["test_gauge"] == 42.0
    
    hist = snapshot["histograms"]["test_hist"]
    assert hist["count"] == 2
    assert hist["min"] == 10.0
    assert hist["max"] == 20.0
    
@pytest.mark.asyncio
async def test_observability_service(clean_registry):
    await observability_service.start()
    
    diag = await observability_service.get_diagnostics()
    assert diag["status"] == "ready"
    assert diag["health"]["ObservabilityService"] == "healthy"
    
    await observability_service.stop()

@pytest.mark.asyncio
async def test_sqlite_contention_metrics(clean_registry):
    with pytest.raises(sqlite3.OperationalError):
        with track_sqlite("test_write"):
            raise sqlite3.OperationalError("database is locked")
            
    # Give the async fire-and-forget task a tiny moment to run
    await asyncio.sleep(0.01)
    
    snapshot = await clean_registry.get_metrics_snapshot()
    assert snapshot["counters"].get("sqlite_contention_errors") == 1

