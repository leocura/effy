import time
import json
import sys

try:
    import tracemalloc
    HAS_TRACEMALLOC = True
except ImportError:
    HAS_TRACEMALLOC = False

class BenchmarkRunner:
    def __init__(self, framework_name):
        self.framework_name = framework_name
        self.tests = {}

    def register(self, name, func, setup_func=None, teardown_func=None, iterations=100, warmup=10):
        self.tests[name] = {
            "func": func,
            "setup_func": setup_func,
            "teardown_func": teardown_func,
            "iterations": iterations,
            "warmup": warmup
        }

    def run_all(self):
        results = {}
        for name, config in self.tests.items():
            sys.stderr.write(f"Starting {name}...\n")
            sys.stderr.flush()
            func = config["func"]
            setup_func = config["setup_func"]
            teardown_func = config["teardown_func"]
            iterations = config["iterations"]
            warmup = config["warmup"]
            
            context = None
            if setup_func:
                context = setup_func()
                
            # Warmup
            if warmup > 0:
                sys.stderr.write(f"  Warmup ({warmup} frames)...\n")
                sys.stderr.flush()
                for _ in range(warmup):
                    if context is not None:
                        func(context)
                    else:
                        func()
                
            times = []
            mem_peak = 0
            
            if HAS_TRACEMALLOC:
                tracemalloc.start()
                tracemalloc.clear_traces()
                
            sys.stderr.write(f"  Running ({iterations} frames)...\n")
            sys.stderr.flush()
            
            for i in range(iterations):
                start = time.perf_counter_ns()
                if context is not None:
                    func(context)
                else:
                    func()
                end = time.perf_counter_ns()
                times.append((end - start) / 1_000_000_000.0) # Convert ns to seconds
                
            if HAS_TRACEMALLOC:
                _, peak = tracemalloc.get_traced_memory()
                mem_peak = peak
                tracemalloc.stop()
                
            if teardown_func:
                teardown_func(context)
                
            times.sort()
            avg_time = sum(times) / len(times)
            
            p99_idx = int(len(times) * 0.99)
            if p99_idx >= len(times):
                p99_idx = len(times) - 1
            p99_time = times[p99_idx]
            
            p999_idx = int(len(times) * 0.999)
            if p999_idx >= len(times):
                p999_idx = len(times) - 1
            p999_time = times[p999_idx]
                
            results[name] = {
                "avg_time": avg_time,
                "p99_time": p99_time,
                "p999_time": p999_time,
                "mem_peak_mb": mem_peak / 1024 / 1024,
                "iterations": iterations
            }
            
        return results

    def dump_json(self):
        output = {
            "framework": self.framework_name,
            "interpreter": sys.implementation.name,
            "version": ".".join(map(str, sys.version_info[:3])),
            "results": self.run_all()
        }
        print(json.dumps(output))
