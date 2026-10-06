import time
import asyncio
from typing import Dict, Any, List
from collections import deque
from enum import Enum

class ComponentState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"
    UNKNOWN = "unknown"

class MetricRegistry:
    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, deque] = {}
        self._components_health: Dict[str, ComponentState] = {}
        self._lock = asyncio.Lock()
        
    async def inc(self, name: str, amount: int = 1):
        async with self._lock:
            self._counters[name] = self._counters.get(name, 0) + amount

    async def set_gauge(self, name: str, value: float):
        async with self._lock:
            self._gauges[name] = value

    async def observe(self, name: str, value: float, max_samples: int = 1000):
        async with self._lock:
            if name not in self._histograms:
                self._histograms[name] = deque(maxlen=max_samples)
            self._histograms[name].append(value)

    async def set_health(self, component: str, state: ComponentState):
        async with self._lock:
            self._components_health[component] = state
            
    async def get_health_snapshot(self) -> Dict[str, str]:
        async with self._lock:
            return {k: v.value for k, v in self._components_health.items()}

    async def get_metrics_snapshot(self) -> Dict[str, Any]:
        async with self._lock:
            snapshot = {
                "counters": self._counters.copy(),
                "gauges": self._gauges.copy(),
                "histograms": {}
            }
            
            # Compute lightweight percentiles for histograms
            for name, values in self._histograms.items():
                if not values:
                    continue
                sorted_vals = sorted(list(values))
                n = len(sorted_vals)
                snapshot["histograms"][name] = {
                    "count": n,
                    "min": sorted_vals[0],
                    "max": sorted_vals[-1],
                    "p50": sorted_vals[int(n * 0.50)],
                    "p95": sorted_vals[int(n * 0.95)],
                    "p99": sorted_vals[int(n * 0.99)],
                }
            return snapshot

# Global registry instance for in-memory metrics
registry = MetricRegistry()
