import time
import json
import os

try:
    import tracemalloc
    HAS_TRACEMALLOC = True
except ImportError:
    HAS_TRACEMALLOC = False

class BenchmarkRunner:
    def __init__(self, framework_name):
        self.framework_name = framework_name
        self.tests = {}

    def register(self, name, func, iterations=10, warmup=2):
        self.tests[name] = {
            "func": func,
            "iterations": iterations,
            "warmup": warmup
        }

    def run_all(self):
        import sys
        results = {}
        for name, config in self.tests.items():
            sys.stderr.write(f"Starting {name}...\n")
            sys.stderr.flush()
            func = config["func"]
            iterations = config["iterations"]
            warmup = config["warmup"]
            
            # Warmup
            sys.stderr.write(f"  Warmup ({warmup} iterations)...\n")
            sys.stderr.flush()
            for _ in range(warmup):
                func()
                
            times = []
            mem_peak = 0
            
            if HAS_TRACEMALLOC:
                tracemalloc.start()
                
            sys.stderr.write(f"  Running ({iterations} iterations)...\n")
            sys.stderr.flush()
            
            for i in range(iterations):
                if i % 10 == 0:
                    sys.stderr.write(f"    Iteration {i}/{iterations}...\n")
                    sys.stderr.flush()
                start = time.perf_counter()
                func()
                end = time.perf_counter()
                times.append(end - start)
                
            if HAS_TRACEMALLOC:
                _, peak = tracemalloc.get_traced_memory()
                mem_peak = peak
                tracemalloc.stop()
                
            times.sort()
            avg_time = sum(times) / len(times)
            min_time = times[0]
            max_time = times[-1]
            
            p99_idx = int(len(times) * 0.99)
            if p99_idx >= len(times):
                p99_idx = len(times) - 1
            p99_time = times[p99_idx]
                
            results[name] = {
                "avg_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "p99_time": p99_time,
                "mem_peak_mb": mem_peak / 1024 / 1024,
                "iterations": iterations
            }
            
        return results

    def dump_json(self):
        import sys
        output = {
            "framework": self.framework_name,
            "interpreter": sys.implementation.name,
            "version": ".".join(map(str, sys.version_info[:3])),
            "results": self.run_all()
        }
        print(json.dumps(output))
