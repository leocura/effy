# Effy Developer User Guide

Welcome to **Effy**! This guide is a thorough developer manual designed to help you construct applications, simulations, game engines, and hardware emulators using Effy.

Effy is a pure-Python, zero-dependency reimplementation of SDL2 built entirely on functional programming principles. It is heavily optimized for **PyPy**'s JIT compiler.

---

## 1. Architectural Foundations

Most traditional multimedia libraries (like Pygame or standard SDL2 wrappers) rely heavily on mutable global state, eager side-effects, and object-oriented mutation. Effy rejects this in favor of a **Functional Core / Imperative Shell** architecture.

```
┌──────────────────────────────────────────────────────────┐
│                     IMPERATIVE SHELL                     │
│  - OS Windowing     - Physical Audio     - Event Polling │
│  - Effect execution (.run())                             │
└────────────────────────────┬─────────────────────────────┘
                             │ (monadic composition)
┌────────────────────────────▼─────────────────────────────┐
│                      FUNCTIONAL CORE                     │
│  - Pure draw commands     - Copy-on-Write buffers        │
│  - Immutable state        - Deterministic math           │
└──────────────────────────────────────────────────────────┘
```

### The Three Golden Rules of Effy Developer:
1. **Zero Eager Side-Effects:** No function in the core may trigger I/O, sleep, access hardware, or mutate a global variable. All side-effects are wrapped inside `Effect` thunks and composed lazily.
2. **Immutable Domain Types:** All types (such as `Color`, `Rect`, `Point`, `KeyboardState`) use `@dataclass(frozen=True, slots=True)`. Mutations are performed using sentinel-based copy-on-write evolutions.
3. **No Exceptions in Public APIs:** All operations that can fail due to external conditions (like OS errors or missing audio hardware) return a monadic `Result` type (`Ok` or `Err`). Exceptions are reserved strictly for internal programming bugs.

---

## 2. The Monadic Toolset: `Effect` and `Result`

Effy models all fallible operations with `Result` and all side-effects with `Effect`.

### 2.1 The `Result[T, E]` Type

A `Result` represents either a success (`Ok[T]`) or a failure (`Err[E]`). It is modeled as a discriminated union:

```python
from Effy._internal.result import Ok, Err, Result
from Effy.error import EffyError

def find_element(items: list[str], target: str) -> Result[int, EffyError]:
    try:
        idx = items.index(target)
        return Ok(idx)
    except ValueError:
        return Err(EffyError(code=404, message=f"'{target}' not found"))
```

#### Chaining and Monadic Composition
You can map or chain results using standard monadic methods:
* `.map(fn)`: Evolve the success value if `Ok`, otherwise return `Err` unchanged.
* `.map_err(fn)`: Evolve the error if `Err`, otherwise return `Ok` unchanged.
* `.and_then(fn)`: FlatMap — chain another fallible function returning a `Result`.

```python
result = (
    find_element(["apple", "banana", "cherry"], "banana")
    .map(lambda idx: idx * 10)
    .and_then(lambda val: Ok(f"Value: {val}") if val > 5 else Err(EffyError(-1, "Too small")))
)

match result:
    case Ok(msg):
        print(f"Success: {msg}")
    case Err(err):
        print(f"Failed ({err.code}): {err.message}")
```

### 2.2 The `Effect[T]` Monad

An `Effect` wraps a side-effectful thunk without executing it. It represents an IO action as a pure, lazy value.

```python
from Effy.types import Effect

def print_hello() -> Effect[None]:
    return Effect(lambda: print("Hello World"))

# No printing has occurred yet!
action = print_hello()

# The side-effect is explicitly triggered here:
action.run()
```

#### Monadic Composition of Effects
You chain multiple lazy operations using `.and_then(fn)`. This compiles an execution plan that executes sequentially exactly once when `.run()` is called:

```python
from Effy.init import init
from Effy.init.flags import InitFlag
from Effy.video.window import create_window, WindowFlags

# Build the initialization pipeline
setup_pipeline = (
    init(InitFlag.VIDEO)
    .and_then(lambda ctx_res: (
        create_window("Effy App", 100, 100, 640, 480, WindowFlags.SHOWN)
        if ctx_res.is_ok()
        else Effect.pure(ctx_res)  # Lift error forward
    ))
)

# Execute the entire OS sequence at the boundary:
window_result = setup_pipeline.run()
```

---

## 3. 2D Software Render Pipeline

Effy features two rendering paths. 

### 3.1 Deferred `RenderContext` Pipeline (Window rendering)
Use `RenderContext` when presenting graphics directly to an OS window. To avoid garbage collection (GC) churn and memory allocations, Effy uses **deferred command accumulation**:
- Every draw function (`render_fill_rect`, `render_draw_line`, etc.) is pure and O(1). It simply appends a frozen `DrawCmd` object to the renderer's command queue.
- `render_present(ctx)` flushes and rasterizes the entire queue in a single optimized pass, utilizing the `PixelBufferPool` to recycle memory and performing exactly **one** allocation per frame.

```python
from Effy.video.rect import Rect, Point
from Effy.render.renderer import (
    render_clear, render_set_draw_color, render_fill_rect,
    render_draw_line, render_fill_circle, render_present
)

def draw_frame(renderer):
    # Enqueue clear background (dark slate)
    renderer = render_set_draw_color(renderer, 30, 30, 40)
    renderer = render_clear(renderer)

    # Enqueue a bright red rectangle
    renderer = render_set_draw_color(renderer, 230, 70, 70)
    renderer = render_fill_rect(renderer, Rect(50, 50, 100, 100))

    # Enqueue a white diagonal line
    renderer = render_set_draw_color(renderer, 255, 255, 255)
    renderer = render_draw_line(renderer, Point(50, 50), Point(150, 150))

    # Enqueue a blue filled circle
    renderer = render_set_draw_color(renderer, 70, 70, 230)
    renderer = render_fill_circle(renderer, Point(300, 200), 40)

    # Flush all commands to the screen in a single pass:
    return render_present(renderer)
```

### 3.2 Offscreen `PixelBuffer` Pipeline (Direct drawing)
Use `PixelBuffer` for direct offscreen drawing or texture synthesis. It wraps an `array.array[int]` representing RGBA pixels.
Backing stores utilize a **Copy-on-Write (CoW)** model using a `_is_transient` flag. A sequence of updates will only copy the backing array once on the first write, reusing the buffer for subsequent writes in the same pipeline chain.

```python
from Effy.video.surface import PixelBuffer
from Effy.render import fill_circle, draw_line
from Effy.types import Color

# Create a 256x256 blank surface
surface = PixelBuffer.create(256, 256)

# Chain mutations safely.Backing store clones once, then mutates in-place!
surface = fill_circle(surface, Point(128, 128), 50, Color(0, 255, 0))
surface = draw_line(surface, Point(0, 0), Point(255, 255), Color(255, 255, 255))
```

---

## 4. Functional Events and Input

Rather than mutating a global input state, inputs and window events are fetched as immutable snapshots.

### 4.1 Event Loop and Processing

Use `poll_event` to query the platform event queue. It returns `Effect[Event | None]`.

```python
from Effy.events import poll_event
from Effy.events.types import QuitEvent, KeyDownEvent

def handle_events() -> Effect[bool]:
    """Poll and process all queued events. Returns whether to keep running."""
    def _run() -> bool:
        running = True
        event = poll_event().run()
        while event is not None:
            if isinstance(event, QuitEvent):
                running = False
            elif isinstance(event, KeyDownEvent):
                print(f"Key pressed! Keycode: {event.keycode}")
            event = poll_event().run()
        return running
    return Effect(_run)
```

### 4.2 Querying Input State

You can fetch snapshots of the keyboard and mouse states at any point in your loop:

```python
from Effy.input import get_keyboard_state, get_mouse_state

def process_movement(speed: float) -> Effect[Point]:
    def _run() -> Point:
        # Get immutable snapshots
        kbd = get_keyboard_state().run()
        mouse = get_mouse_state().run()
        
        # Scancode values are ints (compat constants or scan definitions)
        dx, dy = 0, 0
        if 80 in kbd.pressed_keys:  # 'Left' scancode
            dx = -1
        if 79 in kbd.pressed_keys:  # 'Right' scancode
            dx = 1
            
        return Point(dx, dy)
    return Effect(_run)
```

---

## 5. Audio Synthesis and Mixing

Effy features sample-level audio synthesis and hardware playback streams.

### 5.1 The `AudioBuffer` and AudioSpec

`AudioBuffer` wraps a high-speed `array.array` using:
- Typecode `'h'` (signed 16-bit) for `AudioFormat.S16`.
- Typecode `'f'` (32-bit float) for `AudioFormat.F32`.

```python
import math
from Effy.audio import AudioSpec, AudioFormat, AudioBuffer

# 44100Hz, Stereo, 16-bit, 1024 sample frame buffer
spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=1024)

def generate_sine_wave(freq_hz: float, spec: AudioSpec) -> AudioBuffer:
    """Generate a pure sine wave buffer (silence)."""
    buf = AudioBuffer.create(spec)
    for frame in range(spec.samples):
        # Calculate sample phase
        t = frame / spec.freq
        sample_val = math.sin(2.0 * math.pi * freq_hz * t)
        
        # Write to Left and Right channels (values clamped between -1.0 and 1.0)
        buf = buf.write_sample(frame, 0, sample_val)  # Left
        buf = buf.write_sample(frame, 1, sample_val)  # Right
    return buf
```

### 5.2 Opening the Audio Device and Playing Audio

```python
from Effy.audio import open_audio_device, queue_audio, close_audio_device

def play_sound() -> Effect[None]:
    def _run() -> None:
        # Open default device
        dev_res = open_audio_device(spec).run()
        if dev_res.is_ok():
            device = dev_res.unwrap()
            
            # Synthesize wave and convert to raw audio bytes
            buf = generate_sine_wave(440.0, device.spec)
            
            # Queue sample bytes for native hardware playback
            queue_audio(device, buf.to_bytes()).run()
            
            # Close when finished
            close_audio_device(device).run()
    return Effect(_run)
```

---

## 6. Deterministic Loops and Timing

For physics simulations or high-frequency game logic, a deterministic game loop with accurate delta timing is vital.

```python
import time
from Effy.timer import get_performance_counter, get_performance_frequency

def run_loop() -> Effect[None]:
    def _run() -> None:
        freq = get_performance_frequency().run()
        last_time = get_performance_counter().run()
        
        # 60 FPS Target
        target_dt = 1.0 / 60.0
        
        running = True
        while running:
            now = get_performance_counter().run()
            dt = (now - last_time) / freq
            last_time = now
            
            # Perform simulation updates with dynamic dt
            # update_physics(dt)
            
            # Frame limiting sleep
            elapsed = (get_performance_counter().run() - now) / freq
            sleep_time = target_dt - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
    return Effect(_run)
```

---

## 7. Practical Case Study: Hooking an Emulator or Physics Engine

Here is a complete, production-grade template demonstrating how to properly wire an external emulator, hardware simulation, or physics engine into a Effy event, rendering, and timing loop.

This example hooks up a simulated processor/state machine (emulating a screen buffer and audio synth) and presents it cleanly at a solid, frame-limited 60Hz.

```python
from __future__ import annotations
import sys
import time
from typing import List

# Core Effy imports
from Effy.init import init, quit, InitFlag
from Effy.video.window import create_window, destroy_window, WindowFlags
from Effy.video.rect import Rect, Point
from Effy.video.surface import PixelBuffer
from Effy.types import Color, TextureID
from Effy.render.renderer import (
    create_renderer, render_clear, render_set_draw_color,
    render_copy, render_present, RenderContext, RendererFlags
)
from Effy.render.texture import Texture
from Effy.render import fill_rect
from Effy.events import poll_event
from Effy.events.types import QuitEvent, KeyDownEvent, KeyUpEvent
from Effy.input import get_keyboard_state
from Effy.audio import (
    AudioSpec, AudioFormat, AudioBuffer,
    open_audio_device, queue_audio, close_audio_device, AudioDevice
)
from Effy.timer import get_performance_counter, get_performance_frequency
from Effy._internal.result import Ok, Err

# -------------------------------------------------------------
# Simulated Emulator Core / Physics State
# -------------------------------------------------------------

class VirtualSystem:
    """Mock emulator or physics system generating video frame buffers and audio."""
    
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.frame_count = 0
        self.audio_phase = 0.0

    def step(self, dt: float) -> None:
        """Step the simulation or CPU state forward."""
        self.frame_count += 1

    def render_screen(self, buffer: PixelBuffer) -> PixelBuffer:
        """Directly synthesize a moving horizontal bar on the PixelBuffer."""
        # Simple color clear
        buffer = fill_rect(buffer, None, Color(10, 10, 20))
        
        # Draw moving horizontal bar based on frame count
        bar_y = (self.frame_count * 2) % self.height
        buffer = fill_rect(buffer, Rect(0, bar_y, self.width, 16), Color(0, 220, 220))
        return buffer

    def synthesize_audio(self, spec: AudioSpec) -> AudioBuffer:
        """Synthesize a dynamic 220Hz triangle beep for emulator output."""
        buf = AudioBuffer.create(spec)
        import math
        for i in range(spec.samples):
            # Dynamic frequency modulation
            freq = 220.0 + (math.sin(self.frame_count * 0.05) * 50.0)
            self.audio_phase += (2.0 * math.pi * freq) / spec.freq
            val = math.sin(self.audio_phase)
            buf = buf.write_sample(i, 0, val * 0.3)  # Left
            buf = buf.write_sample(i, 1, val * 0.3)  # Right
        return buf

# -------------------------------------------------------------
# Core Effy Presentation Loop
# -------------------------------------------------------------

def run_emulator(width: int, height: int) -> None:
    # 1. Initialize all subsystems (Video + Audio)
    init_res = init(InitFlag.VIDEO | InitFlag.AUDIO).run()
    if isinstance(init_res, Err):
        print(f"Failed to initialize systems: {init_res.error.message}", file=sys.stderr)
        return
    init_ctx = init_res.unwrap()

    # 2. Open an audio output playback device
    audio_spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=1024)
    audio_res = open_audio_device(audio_spec).run()
    audio_device = audio_res.unwrap() if isinstance(audio_res, Ok) else None
    if audio_device is None:
        print("Warning: Failed to initialize audio output. Running headless audio.", file=sys.stderr)

    # 3. Create OS Window & Renderer
    win_res = create_window("Effy Simulator Case Study", 100, 100, width * 2, height * 2, WindowFlags.SHOWN).run()
    if isinstance(win_res, Err):
        print(f"Failed to create window: {win_res.error.message}", file=sys.stderr)
        return
    window = win_res.unwrap()

    renderer_res = create_renderer(window, flags=RendererFlags.SOFTWARE).run()
    if isinstance(renderer_res, Err):
        print(f"Failed to create renderer: {renderer_res.error.message}", file=sys.stderr)
        destroy_window(window).run()
        return
    renderer = renderer_res.unwrap()

    # 4. Allocate persistent pixel buffer and wrap in Texture for presentation scaling
    screen_buffer = PixelBuffer.create(width, height)
    texture = Texture(id=TextureID(1), width=width, height=height, buffer=screen_buffer)

    # 5. Initialize Virtual Simulation
    emulator = VirtualSystem(width, height)

    # Timing variables
    freq = get_performance_frequency().run()
    last_time = get_performance_counter().run()
    target_dt = 1.0 / 60.0  # target 60FPS

    running = True
    try:
        while running:
            loop_start = get_performance_counter().run()
            dt = (loop_start - last_time) / freq
            last_time = loop_start

            # ---------------------------------------------------------
            # A. Process Events
            # ---------------------------------------------------------
            event = poll_event().run()
            while event is not None:
                if isinstance(event, QuitEvent):
                    running = False
                event = poll_event().run()

            # Process keyboard shortcuts (e.g. Escape to quit)
            kbd = get_keyboard_state().run()
            if 41 in kbd.pressed_keys:  # Scancode 41 (Escape key)
                running = False

            # ---------------------------------------------------------
            # B. Step Emulator CPU & Synthesize Audio
            # ---------------------------------------------------------
            emulator.step(dt)

            if audio_device is not None:
                audio_buf = emulator.synthesize_audio(audio_device.spec)
                queue_audio(audio_device, audio_buf.to_bytes()).run()

            # ---------------------------------------------------------
            # C. Render Emulator Screen to Back-buffer & Scaling Texture
            # ---------------------------------------------------------
            # Direct pixel writing via pure functional transformations
            screen_buffer = emulator.render_screen(screen_buffer)
            texture = Texture(id=texture.id, width=width, height=height, buffer=screen_buffer)

            # Build deferred display rendering pipeline
            renderer = render_set_draw_color(renderer, 0, 0, 0, 255)
            renderer = render_clear(renderer)
            # Scaled copy from backbuffer onto full window viewport (zero-copy presentation)
            renderer = render_copy(renderer, texture, None, Rect(0, 0, width * 2, height * 2))
            
            # Swaps back-buffer on the physical OS Window
            renderer = render_present(renderer).run()

            # ---------------------------------------------------------
            # D. Deterministic 60Hz Frame Rate Limiter
            # ---------------------------------------------------------
            loop_end = get_performance_counter().run()
            elapsed = (loop_end - loop_start) / freq
            sleep_needed = target_dt - elapsed
            if sleep_needed > 0:
                time.sleep(sleep_needed)

    finally:
        # 6. Shut down and cleanly release resources
        if audio_device is not None:
            close_audio_device(audio_device).run()
        destroy_window(window).run()
        quit(init_ctx).run()
        print("Simulator execution stopped cleanly.")

if __name__ == "__main__":
    # Run at 256x224 (Classic retro gaming viewport) scaled up 2x
    run_emulator(256, 224)
```

---

## 8. Summary of Best Practices for Production

1. **Avoid `.run()` in loop logic:** When constructing draw command lists, chain them completely first and call `render_present(ctx).run()` precisely **once** per frame to trigger graphics.
2. **PyPy Optimization:** Always run code via `pypy3`. PyPy's JIT compiles software rasterizer loops to optimized machine code, giving up to **30x speed improvement** over standard CPython.
3. **Use Memory Pools:** Always let `PixelBuffer.create` recycle arrays. Avoid manually allocating large bytearrays inside game loops, as doing so puts severe pressure on the Garbage Collector.
