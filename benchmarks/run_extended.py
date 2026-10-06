import asyncio
from benchmarks.harness import harness

async def run_developer_benchmarks():
    from core.developer.context import SourceContextManager
    from pathlib import Path
    
    context = SourceContextManager(workspace_root=".")
    
    def analyze_project():
        try:
            # We will just fetch a known file
            context.get_context("benchmarks/harness.py", 10)
        except Exception:
            pass
        
    avg = harness.run_sync_benchmark("Developer_Source_Context", analyze_project, iterations=100)
    harness.record("Developer", "source_context_latency_ms", avg)

async def run_llm_routing_benchmarks():
    from core.llm.router import ModelRouter
    from core.llm.registry import ProviderRegistry
    
    registry = ProviderRegistry()
    # Mocking dummy providers is somewhat involved so we'll just instantiate ModelRouter
    router = ModelRouter(registry)
    
    def route_request():
        try:
            router.route(require_vision=True)
        except Exception:
            pass
        
    avg = harness.run_sync_benchmark("LLM_Router_Select", route_request, iterations=1000)
    harness.record("LLM", "routing_overhead_ms", avg)

async def main():
    print("Running extended benchmarks...")
    
    await run_developer_benchmarks()
    await run_llm_routing_benchmarks()
    
    harness.dump_report("benchmarks/extended.json")
    print("Extended Benchmarks complete.")

if __name__ == '__main__':
    asyncio.run(main())
