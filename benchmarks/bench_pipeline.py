"""Effy Pipeline FPS, Frame Latency, and Allocation Benchmark.

This benchmark measures rendering latency, frame times, and audio mixing latency
under a heavy pipeline load, tracking frames-per-second (FPS) and memory allocation overhead.
"""

from __future__ import annotations
import os
import sys
import time
import math
import statistics
try:
    import tracemalloc
    # Try a dummy call to verify PyPy sub-module availability
    tracemalloc.start()
    tracemalloc.stop()
    tracemalloc_available = True
except (ImportError, ModuleNotFoundError, AttributeError):
    tracemalloc_available = False

# Ensure Effy is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Effy.init import init, quit, InitFlag
from Effy.video import create_window, destroy_window, WindowFlags
from Effy.render import (
    create_renderer, render_clear, render_set_draw_color,
    render_fill_rect, render_draw_rect, render_present,
)
from Effy.video.rect import Rect, Point
from Effy.types import Color, Ok
from Effy.audio.types import AudioSpec, AudioFormat, AudioBuffer
from Effy.audio.stream import mix_buffers

def run_pipeline_benchmark() -> None:
    print("======================================================================")
    print("Starting Effy Pipeline FPS and Allocation Benchmark...")
    print("======================================================================")
    
    # 1. Initialize Subsystems
    init_res = init(InitFlag.VIDEO | InitFlag.AUDIO).run()
    if not isinstance(init_res, Ok):
        print(f"Error: Subsystem initialization failed: {init_res}")
        return
    init_ctx = init_res.value
    
    # 2. Setup window and renderer
    win_res = create_window("Benchmark Window", 0, 0, 1024, 768, WindowFlags.HIDDEN).run()
    if not isinstance(win_res, Ok):
        print(f"Error: Window creation failed: {win_res}")
        return
    win = win_res.value
    
    renderer_res = create_renderer(win).run()
    if not isinstance(renderer_res, Ok):
        print(f"Error: Renderer creation failed: {renderer_res}")
        return
    ctx = renderer_res.value

    # 3. Setup Audio buffers
    audio_spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=1024)
    buf_a = AudioBuffer.create(audio_spec)
    buf_b = AudioBuffer.create(audio_spec)
    
    # Pre-generate coordinates to eliminate random generation overhead from timing
    draw_rects = [
        Rect((i * 17) % 900, (i * 23) % 650, 40 + (i % 80), 30 + (i % 60))
        for i in range(100)
    ]
    draw_colors = [
        Color((i * 45) % 256, (i * 95) % 256, (i * 125) % 256, 255)
        for i in range(100)
    ]
    
    # JIT Warm-up runs (200 frames)
    print("Warming up PyPy's JIT compiler (200 frames)...")
    for frame_idx in range(200):
        # Heavy drawing loop (50 drawing commands per frame)
        frame_ctx = render_clear(ctx)
        for i in range(50):
            r = draw_rects[(frame_idx + i) % 100]
            c = draw_colors[(frame_idx + i) % 100]
            frame_ctx = render_set_draw_color(frame_ctx, c.r, c.g, c.b, c.a)
            frame_ctx = render_fill_rect(frame_ctx, r)
            frame_ctx = render_draw_rect(frame_ctx, r)
        
        # Audio mixing
        mix_res = mix_buffers(buf_a, buf_b).unwrap()
        
        # Present and resolve commands
        render_present(frame_ctx).run()
        
    print("Warm-up complete. Starting measurement...")
    
    # Start tracing memory allocations
    if tracemalloc_available:
        tracemalloc.start()
        tracemalloc.clear_traces()
    
    frame_times_ns: list[int] = []
    total_frames = 500
    
    start_bench_time = time.perf_counter()
    
    for frame_idx in range(total_frames):
        frame_start = time.perf_counter_ns()
        
        # Game Loop Logic: Accumulate 50 shape drawing commands
        frame_ctx = render_clear(ctx)
        for i in range(50):
            r = draw_rects[(frame_idx + i) % 100]
            c = draw_colors[(frame_idx + i) % 100]
            frame_ctx = render_set_draw_color(frame_ctx, c.r, c.g, c.b, c.a)
            frame_ctx = render_fill_rect(frame_ctx, r)
            frame_ctx = render_draw_rect(frame_ctx, r)
            
        # Audio mixing step
        mix_res = mix_buffers(buf_a, buf_b).unwrap()
        
        # Present step: flushes commands, performs single pixel buffer rasterization allocation
        render_present(frame_ctx).run()
        
        frame_end = time.perf_counter_ns()
        frame_times_ns.append(frame_end - frame_start)
        
    end_bench_time = time.perf_counter()
    
    # Retrieve memory allocation statistics
    if tracemalloc_available:
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    else:
        current_mem, peak_mem = 0, 0
    
    # 4. Process Statistics
    total_time_seconds = end_bench_time - start_bench_time
    fps = total_frames / total_time_seconds
    
    frame_times_ms = [t / 1_000_000.0 for t in frame_times_ns]
    mean_time = statistics.mean(frame_times_ms)
    min_time = min(frame_times_ms)
    max_time = max(frame_times_ms)
    stddev_time = statistics.stdev(frame_times_ms)
    
    # Calculate 1% low (99th percentile)
    sorted_times = sorted(frame_times_ms)
    percentile_99_idx = int(len(sorted_times) * 0.99)
    p99_time = sorted_times[percentile_99_idx]
    
    mem_str = f"{peak_mem / 1024.0 / 1024.0:.3f} MB" if tracemalloc_available else "N/A (tracemalloc not supported on this interpreter/OS)"
    print("\n---------------- Benchmark Results ----------------")
    print(f"Total Measured Frames : {total_frames}")
    print(f"Total Elapsed Time    : {total_time_seconds:.4f} seconds")
    print(f"Frames Per Second (FPS): {fps:.2f}")
    print(f"Mean Frame Time       : {mean_time:.4f} ms")
    print(f"Min Frame Time        : {min_time:.4f} ms")
    print(f"Max Frame Time        : {max_time:.4f} ms")
    print(f"StdDev Frame Time     : {stddev_time:.4f} ms")
    print(f"1% Low (99th Percentile): {p99_time:.4f} ms")
    print(f"Peak Memory Traced     : {mem_str}")
    print("---------------------------------------------------")
    
    # 5. Write Report File
    report_path = os.path.join(os.path.dirname(__file__), "PIPELINE_FPS_REPORT.md")
    with open(report_path, "w") as f:
        f.write("# Effy Pipeline FPS and Allocation Report\n\n")
        f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Performance Metrics\n\n")
        f.write("| Metric | Value |\n")
        f.write("| :--- | :--- |\n")
        f.write(f"| **Frames Per Second (FPS)** | **{fps:.2f}** |\n")
        f.write(f"| **Mean Frame Time** | {mean_time:.4f} ms |\n")
        f.write(f"| **Min Frame Time** | {min_time:.4f} ms |\n")
        f.write(f"| **Max Frame Time** | {max_time:.4f} ms |\n")
        f.write(f"| **StdDev Frame Time** | {stddev_time:.4f} ms |\n")
        f.write(f"| **1% Low (99th Percentile)** | {p99_time:.4f} ms |\n")
        f.write(f"| **Peak Memory Allocation** | {mem_str} |\n\n")
        
        f.write("## Benchmark Architecture\n\n")
        f.write("- **Load profile**: 50 drawing commands (Alternating `fill_rect` and `draw_rect`) + 1 stereo `AudioBuffer` mixing operations per frame.\n")
        f.write("- **Warm-up**: 200 frames executed prior to tracing to fully trigger PyPy's JIT trace compiler.\n")
        f.write(f"- **Memory Tracing**: {'Enabled via `tracemalloc` to isolate active buffer construction and disposal overhead.' if tracemalloc_available else 'Not supported/disabled on this environment.'}\n")

    print(f"Report successfully saved to: {report_path}\n")
    
    # 6. Cleanup
    destroy_window(win).run()
    quit(init_ctx).run()

if __name__ == "__main__":
    run_pipeline_benchmark()
