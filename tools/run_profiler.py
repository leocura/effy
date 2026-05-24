import cProfile
import pstats
import sys
import runpy
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python profile.py <script_to_run.py> [args...]")
        sys.exit(1)

    script_path = sys.argv[1]
    
    # Adjust sys.argv so the target script sees its own arguments
    sys.argv = sys.argv[1:]
    
    # Prepend the root directory to PYTHONPATH so it finds Effy easily
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    script_dir = os.path.dirname(os.path.abspath(script_path))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    print(f"Profiling {script_path}...")

    profiler = cProfile.Profile()
    profiler.enable()

    try:
        runpy.run_path(script_path, run_name="__main__")
    except SystemExit:
        pass
    except KeyboardInterrupt:
        print("\nInterrupted by user. Dumping stats...")

    profiler.disable()

    prof_file = "effy_profile.prof"
    profiler.dump_stats(prof_file)

    print("\n" + "="*50)
    print(" PROFILING RESULTS ".center(50, "="))
    print("="*50)
    
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    # Filter out a lot of standard library noise if needed, but for now just print top 25 cumulative
    stats.sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats(25)

    print(f"\nSaved full profile to {os.path.abspath(prof_file)}.")
    print(f"You can visualize it by running: python -m pip install snakeviz && snakeviz {prof_file}")

if __name__ == "__main__":
    main()
