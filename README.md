# Effy

A pure-Python 2D graphics, audio, and windowing library inspired by SDL2. 

Effy is built with minimal external dependencies. It talks directly to your operating system's windowing subsystem via standard library `ctypes`.

We respect Pygame, but Effy is designed to be a complete, modern alternative built on clean functional principles.

## Features

- **Windowing & OS Events:** Creation, styling, and management of OS windows. Events like mouse, keyboard, touch, and gamepad inputs are processed through a clean, immutable queue.
- **2D Software Rasterizer:** Out-of-the-box rendering functions for rectangles, circles, lines, and filled triangles directly in memory or onto an active window.
- **Direct Pixel Buffers:** Fast off-screen surface manipulation using standard `array` structures with nearest-neighbor and bilinear filtering.
- **Custom Shader Pipelines:** Build visual effects with functional Signed Distance Field (SDF) shaders running directly in Python.
- **Audio Mixing & Resampling:** Multi-channel mixing, playback, and automatic sample format conversion. Supports ALSA, PulseAudio, WASAPI, and standard core audio loops.

## Requirements

- **PyPy 3.10+ (Required)**
  PyPy3 is a requirement. Effy's pure-Python rendering and audio mixing pipelines are deeply optimized specifically for PyPy's JIT compiler to deliver real-time performance.
- **CPython 3.10+ (Development Only)**
  CPython is supported only for running static analysis, type-checkers (`mypy`), or linters (`ruff`). Running Effy applications on CPython will emit a performance warning, as CPython's interpreter is not fast enough for real-time software rasterization.
- **Minimal External Dependencies**
  Effy relies heavily on standard libraries (`ctypes`, `array`, `struct`, etc.). The other dependencies are for dev tools (`pytest`, `mypy`, `ruff`).

---

## Quick Start: Bouncing Box

Here is a simple example of drawing a bouncing box on a 60 FPS update loop.

```python
import time
from Effy.init import init, quit, InitFlag
from Effy.video.window import create_window, destroy_window, WindowFlags
from Effy.render.renderer import (
    create_renderer, render_clear, render_set_draw_color,
    render_fill_rect, render_present, RendererFlags
)
from Effy.video.rect import Rect
from Effy.events import poll_event, QuitEvent
from Effy._internal.result import Ok

def main() -> None:
    # 1. Initialize video system
    init_res = init(InitFlag.VIDEO).run()
    if not isinstance(init_res, Ok):
        print("Failed to initialize Effy")
        return
    init_ctx = init_res.value

    # 2. Open an OS window and spin up a software renderer
    win_res = create_window("Effy Quick Start", 100, 100, 640, 480, WindowFlags.SHOWN).run()
    if not isinstance(win_res, Ok):
        return
    window = win_res.value

    renderer_res = create_renderer(window, flags=RendererFlags.SOFTWARE).run()
    if not isinstance(renderer_res, Ok):
        return
    renderer = renderer_res.value

    # Box coordinates and velocity
    x, y = 100, 100
    dx, dy = 4, 3
    size = 60

    running = True
    while running:
        # 3. Pull events
        event = poll_event().run()
        while event is not None:
            if isinstance(event, QuitEvent):
                running = False
            event = poll_event().run()

        # 4. Update simple box physics
        x += dx
        y += dy
        if x <= 0 or x + size >= 640:
            dx = -dx
        if y <= 0 or y + size >= 480:
            dy = -dy

        # 5. Build render pass (pure functional transformations)
        renderer = render_set_draw_color(renderer, 20, 20, 30)
        renderer = render_clear(renderer)
        
        renderer = render_set_draw_color(renderer, 240, 100, 100)
        renderer = render_fill_rect(renderer, Rect(x, y, size, size))
        
        # 6. Rasterize and display
        renderer = render_present(renderer).run()
        time.sleep(1 / 60)

    # 7. Clean up
    destroy_window(window).run()
    quit(init_ctx).run()

if __name__ == "__main__":
    main()
```

Run this with PyPy:
```bash
PYTHONPATH=. .venv_pypy/bin/pypy3 quickstart.py
```

---

## Standing Proud: Effy vs Pygame

We aim for Effy to be a complete, viable replacement for Pygame. 

Because Effy runs on pure Python optimized for **PyPy**, it avoids standard interop overhead and unlocks incredible execution speeds. While Pygame offloads basic drawing loops to native C libraries, Effy is highly capable and is **more than good enough for almost all 2D game and application needs** on any system equipped with a modest integrated GPU (iGPU).

### The Benchmarks

Here is a performance comparison of average execution times (in milliseconds) for rendering, audio, and physics operations under **Effy (PyPy 3.11)** vs. **Pygame (CPython 3.13)**:

| Operation | Effy (PyPy) | Pygame (CPython) | Speedup / Slowdown |
| :--- | :--- | :--- | :--- |
| **Audio Specification Conversion** | **0.27 ms** | 212.69 ms | **~780x faster** (Effy JIT) |
| **Multi-Stream Audio Mix** | **1.10 ms** | 98.53 ms | **~89x faster** (Effy JIT) |
| **SDF CSG Shader (500x500)** | **73.24 ms** | 13,455.13 ms | **~180x faster** (Effy JIT) |
| **2000 Particle Physics Simulation** | **5.21 ms** | 14.09 ms | **~2.7x faster** (Effy JIT) |
| **Draw Diagonal Line** | 13.52 ms | 16.10 ms | ~1.2x faster |
| **Small Rectangle Fills** | 2.73 ms | 9.50 ms | ~3.4x faster |
| **Large Rectangle Fills** | 2.83 ms | 2.08 ms | ~0.73x slower |
| **Draw Rectangle Outline** | 29.65 ms | 7.51 ms | ~0.25x slower |
| **Fill Triangles** | 249.82 ms | 61.06 ms | ~0.24x slower |
| **Bilinear Blit Scale** | 75.16 ms | 9.06 ms | ~0.12x slower |
| **Standard 1:1 Surface Blits** | 41.23 ms | 2.79 ms | ~0.07x slower |

### Realities and Strengths

- **Where Effy dominates:** Pure Python audio mixing, custom functional CPU-shaders, complex mathematical/physics updates, and generative coordinate rendering. PyPy's JIT compiles these mathematical transformations directly to CPU machine code, removing C interop bottlenecks.
- **Where Pygame has a temporary edge:** Raw surface blitting and rasterizing large polygons. Since Pygame uses highly mature C-level optimized SDL2 surface loops, direct pixel-copy operations are faster.
- **A Modern Choice:** Instead of Pygame's stateful, imperative, and mutable model, Effy provides a highly predictable, clean functional design. If you want a modern, pure-Python architecture that is scalable, easy to reason about, and fully optimized for PyPy, Effy is the solution.

---

## Architectural Details

If you are looking to build or contribute to Effy, or want to understand how its pure functional graphics pipeline and lazy effect wrappers are put together, check out the [Core Architecture README](file:///home/leocura/antigravity/effy/Effy/README.md).

## License

See the LICENSE file for details.
