# Effy

A pure-Python reimplementation of SDL2 built on functional programming principles.

## What Is This

Effy provides windowing, 2D software rendering, audio mixing, input handling, and clipboard access — all implemented in pure Python with zero external dependencies. The only non-Python interaction is via `ctypes` for direct OS system calls (X11, Win32, Quartz), isolated inside dedicated platform adapter modules.

The codebase follows a strict **functional core / imperative shell** architecture:
- **Functional core:** All logic is expressed as pure functions over frozen dataclasses. Drawing commands are accumulated as an immutable sequence of command objects. Large pixel and audio buffers are manipulated via a high-performance copy-on-write model.
- **Imperative shell:** Side effects (window creation, buffer presentation, audio device I/O, event polling) are wrapped in `Effect[T]` values that are composed lazily and executed once at the application boundary.

## Requirements

- **Python 3.11+** (for `match` statements and modern typing)
- **PyPy 3.10+** (recommended — rendering and audio pipelines are highly optimized for PyPy's JIT compiler)
- CPython is supported for development, testing, and static analysis (ruff, mypy strict) but will emit a performance warning at import time.

### Zero Dependencies

Effy has **no external pip-installable dependencies**. It uses only the standard library (`array`, `memoryview`, `struct`, `ctypes`, etc.). The dev toolchain is the only thing you install.

## Quick Start

```bash
# Clone
git clone https://github.com/leocura/effy.git
cd effy

# Set up dev environments
pypy3 -m venv .venv_pypy
python3 -m venv .venv_cpython

# Install dev tools
.venv_pypy/bin/pip install pytest hypothesis
.venv_cpython/bin/pip install mypy ruff

# Run tests
PYTHONPATH=. .venv_pypy/bin/pytest tests/ -x --tb=short

# Type check
PYTHONPATH=. .venv_cpython/bin/mypy --strict Effy/

# Lint
.venv_cpython/bin/ruff check Effy/ tests/
```

## Hello Window

```python
from Effy.init import init
from Effy.init.flags import InitFlag
from Effy.video.window import create_window, destroy_window, WindowFlags
from Effy.render.renderer import (
    create_renderer, render_clear, render_set_draw_color,
    render_fill_rect, render_draw_line, render_present
)
from Effy.video.rect import Rect, Point
from Effy.events import poll_event
from Effy.events.types import QuitEvent
from Effy._internal.result import Ok

def main() -> None:
    # 1. Initialize systems
    ctx_result = init(InitFlag.VIDEO).run()
    if not isinstance(ctx_result, Ok):
        print("Failed to initialize")
        return

    # 2. Create Window
    win_result = create_window("Hello Effy", 100, 100, 640, 480, WindowFlags.SHOWN).run()
    if not isinstance(win_result, Ok):
        print("Failed to create window")
        return
    window = win_result.value

    # 3. Create Renderer
    renderer_result = create_renderer(window).run()
    if not isinstance(renderer_result, Ok):
        print("Failed to create renderer")
        return
    renderer = renderer_result.value

    running = True
    while running:
        # 4. Pump and poll events
        event = poll_event().run()
        while event is not None:
            if isinstance(event, QuitEvent):
                running = False
            event = poll_event().run()

        # 5. Build rendering pipeline (pure functional transformations)
        renderer = render_set_draw_color(renderer, 40, 40, 80)
        renderer = render_clear(renderer)
        renderer = render_set_draw_color(renderer, 240, 100, 100)
        renderer = render_fill_rect(renderer, Rect(100, 100, 200, 150))
        renderer = render_set_draw_color(renderer, 255, 255, 255)
        renderer = render_draw_line(renderer, Point(50, 50), Point(300, 50))
        
        # 6. Execute presentation (flush & rasterize to OS window in a single pass)
        renderer = render_present(renderer).run()

    destroy_window(window).run()

if __name__ == "__main__":
    main()
```

## Architecture

```
Effy/
├── _internal/       Effect[T] monad, Result[T,E] type, FP utilities, registry, buffer pools
├── types.py         Color, WindowID, TextureID, Ticks, TimerID
├── error.py         SDLError
├── init/            Initialization and shutdown
├── video/           PixelBuffer (array-backed), Window, Rect, Point, display queries
├── render/          Deferred command pipeline, in-place rasterizer (Bresenham, midpoint circle)
├── audio/           AudioBuffer (array-backed), mixing, resampling, device WASAPI/ALSA/stubs
├── events/          Event types, immutable queue, filter/map/fold
├── input/           Keyboard, mouse, touch, gamepad, sensors, haptics
├── clipboard/       System clipboard access
├── timer/           High-resolution timers, ClockState
├── filesystem/      RWops byte buffer, path utilities
├── platform/        OS adapters (Linux X11, Windows GDI, macOS Quartz stub, Headless)
└── compat/          SDL2-style SDL_ prefixed aliases
```

## Functional Rendering API

Effy features two rendering interfaces, both driven by pure functional pipelines:

### 1. `RenderContext` (Renderer-Based, Target Presentation)
Used for presenting graphics to a window. Accumulates O(1) drawing commands and flushes them to the OS screen in a single highly-optimized rasterization pass during `render_present`.
* `create_renderer(window, index, flags)`: Return an `Effect` creating the context.
* `render_clear(ctx)`: Clear the command queue and set background.
* `render_set_draw_color(ctx, r, g, b, a)`: Return updated context with the draw color.
* `render_fill_rect(ctx, rect)`: Enqueue a solid rectangle fill.
* `render_draw_rect(ctx, rect)`: Enqueue a rectangle outline.
* `render_draw_line(ctx, p1, p2)`: Enqueue a line from point p1 to p2.
* `render_draw_circle(ctx, center, radius)`: Enqueue a circle outline.
* `render_fill_circle(ctx, center, radius)`: Enqueue a filled circle.
* `render_fill_triangle(ctx, p1, p2, p3)`: Enqueue a filled triangle.
* `render_copy(ctx, texture, src, dst)`: Copy a texture region (nearest-neighbor).
* `render_copy_blended(ctx, texture, src, dst)`: Copy a texture region with alpha blending.
* `render_copy_scaled(ctx, texture, src, dst)`: Copy a texture region scaled.
* `render_copy_bilinear(ctx, texture, src, dst)`: Copy a texture region with bilinear filtering.
* `render_field(ctx, rect, field)`: Enqueue a Signed Distance Field (SDF) shader.
* `render_present(ctx)`: Flush context, rasterize, and swap buffers on the OS window.

### 2. `PixelBuffer` (Surface-Based, Direct Direct Buffer Rasterization)
Used for direct off-screen drawing into memory. Driven by a copy-on-write `array.array[int]` backing store.
* `fill_rect(buf, rect, color)`: Draw a solid rectangle.
* `draw_rect(buf, rect, color)`: Draw a rectangle outline.
* `draw_line(buf, p1, p2, color)`: Draw a line.
* `draw_circle(buf, center, radius, color)`: Draw a circle outline.
* `fill_circle(buf, center, radius, color)`: Draw a filled circle.
* `fill_triangle(buf, p1, p2, p3, color)`: Draw a filled triangle.
* `blit(src, src_rect, dst, dst_rect)`: Direct pixel copy between buffers.
* `blit_blended(src, src_rect, dst, dst_rect)`: Blit with alpha blending.
* `blit_scaled(src, src_rect, dst, dst_rect)`: Nearest-neighbor scaled blit.
* `blit_bilinear(src, src_rect, dst, dst_rect)`: Bilinear filtered scaled blit.

---

## Core Guidelines & Development Rules

Effy is structured strictly to maximize safety, predictable execution, and PyPy JIT performance:

1. **No Eager Side Effects:** All FFI and OS interactions (ctypes) must live in `Effy/platform/`. All effectful functions in domain code must return `Effect[T]` thunks.
2. **Immutable Domain Types:** All types utilize `@dataclass(frozen=True, slots=True)` with sentinel-based `.evolve()` copy-on-write modifications.
3. **No Exceptions in Public API:** All fallible operations return `Result[T, SDLError]` (`Ok` or `Err`). Exceptions are used only for invalid type instantiation.
4. **Memory Pools:** Frame buffers use the JIT-friendly `PixelBufferPool` to recycle arrays, reducing garbage collection overhead.
5. **Linting and Typing:** Strictly typed (`mypy --strict` passes with 100% clean output) and styled (`ruff`).

> [!NOTE]
> **Documentation Update Note:** Former documents `AGENTS.md` and `SPECIFICATION.md` have been deprecated and retired. All relevant standards are maintained here in the main `README.md` to avoid fragmented or outdated rules.

## License

See the LICENSE file for details.
