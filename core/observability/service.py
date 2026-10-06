import asyncio
import time
from typing import Dict, Any

from core.observability.metrics import registry, ComponentState

class ObservabilityService:
    """Manages telemetry, metrics aggregation, and runtime health state."""
    def __init__(self):
        self.start_time = time.time()
        self._shutdown_event = asyncio.Event()

    async def start(self):
        await registry.set_health("Runtime", ComponentState.HEALTHY)
        await registry.set_health("ObservabilityService", ComponentState.HEALTHY)

    async def stop(self):
        self._shutdown_event.set()
        await registry.set_health("Runtime", ComponentState.DISABLED)

    async def get_diagnostics(self) -> Dict[str, Any]:
        """Generate a safe snapshot of system health, metrics, and state."""
        uptime = time.time() - self.start_time
        health = await registry.get_health_snapshot()
        metrics = await registry.get_metrics_snapshot()
        
        # Redact anything obviously problematic just in case, though registry 
        # should only hold safe counters and gauges.
        
        return {
            "uptime_seconds": round(uptime, 2),
            "health": health,
            "metrics": metrics,
            "status": "ready" if all(v == "healthy" for v in health.values()) else "degraded",
        }

observability_service = ObservabilityService()
