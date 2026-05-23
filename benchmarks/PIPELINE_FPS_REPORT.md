# Effy Pipeline FPS and Allocation Report

Generated at: 2026-05-22 16:46:52

## Performance Metrics

| Metric | Value |
| :--- | :--- |
| **Frames Per Second (FPS)** | **27.30** |
| **Mean Frame Time** | 36.6308 ms |
| **Min Frame Time** | 16.4110 ms |
| **Max Frame Time** | 569.2423 ms |
| **StdDev Frame Time** | 39.9846 ms |
| **1% Low (99th Percentile)** | 64.0415 ms |
| **Peak Memory Allocation** | N/A (tracemalloc not supported on this interpreter/OS) |

## Benchmark Architecture

- **Load profile**: 50 drawing commands (Alternating `fill_rect` and `draw_rect`) + 1 stereo `AudioBuffer` mixing operations per frame.
- **Warm-up**: 200 frames executed prior to tracing to fully trigger PyPy's JIT trace compiler.
- **Memory Tracing**: Not supported/disabled on this environment.
