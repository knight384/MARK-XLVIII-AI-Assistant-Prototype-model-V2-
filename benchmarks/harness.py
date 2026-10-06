import time
import asyncio
import os
import platform
import json

class BenchmarkHarness:
    def __init__(self):
        self.results = {}
        self.environment = {
            "os": platform.system(),
            "os_release": platform.release(),
            "cpu": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count()
        }

    def record(self, category: str, metric: str, value: float, unit: str = "ms"):
        if category not in self.results:
            self.results[category] = {}
        self.results[category][metric] = {"value": value, "unit": unit}

    def dump_report(self, path="benchmarks/baseline.json"):
        report = {
            "environment": self.environment,
            "results": self.results
        }
        with open(path, "w") as f:
            json.dump(report, f, indent=2)

    async def run_benchmark(self, name, async_func, *args, iterations=100, **kwargs):
        start = time.perf_counter()
        for _ in range(iterations):
            await async_func(*args, **kwargs)
        end = time.perf_counter()
        avg_ms = ((end - start) / iterations) * 1000
        print(f"Benchmark [{name}]: {avg_ms:.3f} ms / op over {iterations} ops")
        return avg_ms

    def run_sync_benchmark(self, name, func, *args, iterations=100, **kwargs):
        start = time.perf_counter()
        for _ in range(iterations):
            func(*args, **kwargs)
        end = time.perf_counter()
        avg_ms = ((end - start) / iterations) * 1000
        print(f"Benchmark [{name}]: {avg_ms:.3f} ms / op over {iterations} ops")
        return avg_ms

harness = BenchmarkHarness()
