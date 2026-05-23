import subprocess
import json
import sys
import os
import shutil
import time

def run_benchmark(script_path, interpreter, framework_arg):
    print(f"  -> Running {script_path} with {interpreter} as {framework_arg}...")
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
        "test_primitives.py",
        "test_surfaces.py",
        "test_particles.py",
        "test_triangles.py",
        "test_shader.py",
        "test_audio.py",
        "test_geometry.py",
        "test_events.py",
        "test_image.py"
    ]
    
    # Detect PyPy3
    if os.name == "nt":
        local_pypy = os.path.join(benchmarks_dir, "..", ".venv_pypy", "Scripts", "pypy3.exe")
    else:
        local_pypy = os.path.join(benchmarks_dir, "..", ".venv_pypy", "bin", "pypy3")

    if os.path.exists(local_pypy):
        effy_interpreter = local_pypy
    else:
        effy_interpreter = "pypy3"
        if not shutil.which(effy_interpreter):
            fallback_path = r"C:\Users\Leonardo de Araujo\AppData\Local\Microsoft\WinGet\Packages\PyPy.PyPy.3.11_Microsoft.Winget.Source_8wekyb3d8bbwe\pypy3.11-v7.3.20-win64\pypy3.exe"
            if os.path.exists(fallback_path):
                effy_interpreter = fallback_path
            else:
                print("Warning: pypy3 not found. Falling back to CPython for Effy.")
                effy_interpreter = sys.executable
            
    if os.name == "nt":
        local_cpython = os.path.join(benchmarks_dir, "..", ".venv_cpython", "Scripts", "python.exe")
    else:
        local_cpython = os.path.join(benchmarks_dir, "..", ".venv_cpython", "bin", "python")

    if os.path.exists(local_cpython):
        pygame_interpreter = local_cpython
    else:
        pygame_interpreter = sys.executable
    
    all_results = {}
    
    for suite in suites:
        script_path = os.path.join(suite_dir, suite)
        print(f"\nRunning suite: {suite}")
        
        # Run Effy on PyPy
        p_res = run_benchmark(script_path, effy_interpreter, "effy")
        
        # Run Pygame on CPython
        g_res = run_benchmark(script_path, pygame_interpreter, "pygame")
        
        if p_res and g_res:
            all_results[suite] = {
                "effy": p_res,
                "pygame": g_res
            }
            
    # Generate report
    report_path = os.path.join(benchmarks_dir, "COMPREHENSIVE_REPORT.md")
    with open(report_path, "w") as f:
        f.write("# Effy vs Pygame Comprehensive Benchmark Report\n\n")
        f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Environment\n")
        
        if effy_interpreter == sys.executable and "pypy" not in sys.implementation.name.lower():
            f.write("> [!WARNING]\n")
            f.write("> Effy was run on CPython because PyPy3 was not found. Pure Python implementations like Effy perform much better on PyPy.\n\n")
        
        for suite, res in all_results.items():
            f.write(f"## Suite: `{suite}`\n\n")
            
            p_data = res["effy"]
            g_data = res["pygame"]
            
            f.write(f"- Effy version string: {p_data['interpreter']} {p_data['version']}\n")
            f.write(f"- Pygame version string: {g_data['interpreter']} {g_data['version']}\n\n")
            
            f.write("| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
            
            tests = p_data["results"].keys()
            for test in tests:
                if test not in g_data["results"]:
                    continue
                
                # convert to milliseconds for readability
                p_test = p_data["results"][test]
                g_test = g_data["results"][test]
                
                p_avg_ms = p_test['avg_time'] * 1000
                g_avg_ms = g_test['avg_time'] * 1000
                p_p99_ms = p_test['p99_time'] * 1000
                g_p99_ms = g_test['p99_time'] * 1000
                
                speedup = g_test['avg_time'] / p_test['avg_time'] if p_test['avg_time'] > 0 else 0
                
                f.write(f"| {test} | {p_avg_ms:.4f} | {g_avg_ms:.4f} | {speedup:.2f}x | {p_p99_ms:.4f} | {g_p99_ms:.4f} | {p_test['mem_peak_mb']:.2f} | {g_test['mem_peak_mb']:.2f} |\n")
            
            f.write("\n")
            
    print(f"\nReport generated at {report_path}")

if __name__ == "__main__":
    main()
