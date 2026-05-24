import subprocess
import json
import sys
import os
import shutil
import time

def run_benchmark(script_path, interpreter, framework_arg):
    print(f"  -> Running {os.path.basename(script_path)} with {framework_arg}...")
    try:
        result = subprocess.run(
            [interpreter, script_path, framework_arg],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {script_path}: {e}")
        print(f"Raw Output: {result.stdout}")
        return None
    except FileNotFoundError:
        print(f"Interpreter {interpreter} not found.")
        return None

def main():
    benchmarks_dir = os.path.dirname(os.path.abspath(__file__))
    suite_dir = os.path.join(benchmarks_dir, "suite")
    
    suites = [
        "scenario_game_loop.py",
        "scenario_particles.py",
        "scenario_pixel_buffer.py",
        "scenario_audio_mixer.py"
    ]
    
    # Detect Interpreters
    if os.name == "nt":
        local_pypy = os.path.join(benchmarks_dir, "..", ".venv_pypy", "Scripts", "pypy3.exe")
        local_cpython = os.path.join(benchmarks_dir, "..", ".venv_cpython", "Scripts", "python.exe")
    else:
        local_pypy = os.path.join(benchmarks_dir, "..", ".venv_pypy", "bin", "pypy3")
        local_cpython = os.path.join(benchmarks_dir, "..", ".venv_cpython", "bin", "python")

    effy_interpreter = local_pypy if os.path.exists(local_pypy) else (shutil.which("pypy3") or sys.executable)
    pygame_interpreter = local_cpython if os.path.exists(local_cpython) else sys.executable
    
    all_results = {}
    
    print("\n" + "="*80)
    print(" EFFY VS PYGAME BENCHMARK SUITE ".center(80, "="))
    print("="*80 + "\n")
    
    for suite in suites:
        script_path = os.path.join(suite_dir, suite)
        print(f"--- Suite: {suite} ---")
        
        p_res = run_benchmark(script_path, effy_interpreter, "effy")
        g_res = run_benchmark(script_path, pygame_interpreter, "pygame")
        
        if p_res and g_res:
            all_results[suite] = {
                "effy": p_res,
                "pygame": g_res
            }
            
            # Print console table
            print("\n" + "-"*110)
            print(f"{'Test':<30} | {'Effy FPS':<10} | {'Pygame FPS':<10} | {'1% Low (E/P)':<15} | {'0.1% Low (E/P)':<15}")
            print("-" * 110)
            
            for test in p_res["results"]:
                if test not in g_res["results"]: continue
                pt = p_res["results"][test]
                gt = g_res["results"][test]
                
                effy_fps = 1.0 / pt["avg_time"] if pt["avg_time"] > 0 else 0
                pygame_fps = 1.0 / gt["avg_time"] if gt["avg_time"] > 0 else 0
                
                e_p99 = pt["p99_time"] * 1000
                g_p99 = gt["p99_time"] * 1000
                e_p999 = pt["p999_time"] * 1000
                g_p999 = gt["p999_time"] * 1000
                
                p99_str = f"{e_p99:.1f} / {g_p99:.1f}"
                p999_str = f"{e_p999:.1f} / {g_p999:.1f}"
                
                print(f"{test:<30} | {effy_fps:<10.0f} | {pygame_fps:<10.0f} | {p99_str:<15} | {p999_str:<15}")
            print("-" * 110 + "\n")
            
    # Generate Markdown Report
    report_path = os.path.join(benchmarks_dir, "COMPREHENSIVE_REPORT.md")
    with open(report_path, "w") as f:
        f.write("# Effy vs Pygame Performance Report\n\n")
        f.write(f"**Generated at:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Environment\n\n")
        f.write(f"- **Effy Interpreter**: `{effy_interpreter}`\n")
        f.write(f"- **Pygame Interpreter**: `{pygame_interpreter}`\n\n")
        
        if effy_interpreter == sys.executable and "pypy" not in sys.implementation.name.lower():
            f.write("> [!WARNING]\n")
            f.write("> Effy was run on CPython because PyPy3 was not found. Pure Python implementations like Effy perform much better on PyPy.\n\n")
            
        for suite, res in all_results.items():
            f.write(f"### Scenario: `{suite}`\n\n")
            p_data = res["effy"]
            g_data = res["pygame"]
            
            f.write(f"- Effy: {p_data['interpreter']} {p_data['version']}\n")
            f.write(f"- Pygame: {g_data['interpreter']} {g_data['version']}\n\n")
            
            f.write("| Workload | Effy Avg FPS | Pygame Avg FPS | Speedup | Effy 1% Low | Pygame 1% Low | Effy 0.1% Low | Pygame 0.1% Low | Mem Peak (E/P) |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
            
            tests = p_data["results"].keys()
            for test in tests:
                if test not in g_data["results"]: continue
                
                pt = p_data["results"][test]
                gt = g_data["results"][test]
                
                e_fps = 1.0 / pt["avg_time"] if pt["avg_time"] > 0 else 0
                g_fps = 1.0 / gt["avg_time"] if gt["avg_time"] > 0 else 0
                speedup = e_fps / g_fps if g_fps > 0 else float('inf')
                
                e_p99 = pt["p99_time"] * 1000
                g_p99 = gt["p99_time"] * 1000
                e_p999 = pt["p999_time"] * 1000
                g_p999 = gt["p999_time"] * 1000
                
                e_mem = pt["mem_peak_mb"]
                g_mem = gt["mem_peak_mb"]
                
                f.write(f"| {test} | {e_fps:.0f} | {g_fps:.0f} | **{speedup:.2f}x** | {e_p99:.2f}ms | {g_p99:.2f}ms | {e_p999:.2f}ms | {g_p999:.2f}ms | {e_mem:.1f}MB / {g_mem:.1f}MB |\n")
            f.write("\n")
            
    print(f"\nReport generated at {report_path}")

if __name__ == "__main__":
    main()
