import time
import asyncio
import numpy as np
import json
from pathlib import Path

class BenchmarkHarness:
    def __init__(self):
        self.results = {}

    async def run_benchmark(self, name: str, async_func, iterations: int = 100):
        latencies = []
        # warmup
        for _ in range(max(1, iterations // 10)):
            await async_func()
            
        for _ in range(iterations):
            t0 = time.perf_counter()
            await async_func()
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)
            
        self.record_raw(name, latencies)
        return np.mean(latencies)

    def run_sync_benchmark(self, name: str, sync_func, iterations: int = 100):
        latencies = []
        # warmup
        for _ in range(max(1, iterations // 10)):
            sync_func()
            
        for _ in range(iterations):
            t0 = time.perf_counter()
            sync_func()
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)
            
        self.record_raw(name, latencies)
        return np.mean(latencies)

    async def run_concurrent_benchmark(self, name: str, async_func, concurrency: int, iterations_per_task: int):
        latencies = []
        async def worker():
            for _ in range(iterations_per_task):
                t0 = time.perf_counter()
                await async_func()
                t1 = time.perf_counter()
                latencies.append((t1 - t0) * 1000.0)

        tasks = [worker() for _ in range(concurrency)]
        await asyncio.gather(*tasks)
        
        self.record_raw(name, latencies)
        return np.mean(latencies)

    def record_raw(self, name: str, latencies: list):
        count = len(latencies)
        mean = np.mean(latencies)
        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        val_min = np.min(latencies)
        val_max = np.max(latencies)
        
        print(f"Benchmark [{name}]: N={count} | Mean: {mean:.3f}ms | p50: {p50:.3f}ms | p95: {p95:.3f}ms | p99: {p99:.3f}ms")
        
        self.results[name] = {
            "count": count,
            "mean_ms": mean,
            "p50_ms": p50,
            "p95_ms": p95,
            "p99_ms": p99,
            "min_ms": val_min,
            "max_ms": val_max,
        }

    def dump_report(self, path: str = "benchmarks/baseline.json"):
        Path(path).parent.mkdir(exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2)

harness = BenchmarkHarness()
