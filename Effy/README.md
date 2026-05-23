# Effy Core Architecture

This directory contains the core implementation of Effy. The codebase follows a strict **Functional Core / Imperative Shell** architecture designed to combine the mathematical safety of functional programming with the speed requirements of PyPy's JIT compiler.

```
Effy/
├── _internal/       Effect[T] runtime wrapper, Result[T,E] types, FP utilities, array pools
├── types.py         Core shared primitives (Color, WindowID, TextureID, Ticks, TimerID)
├── error.py         System SDLError representations
├── init/            Initialization and boundary shutdown handlers
├── video/           Immutable Rects/Points, copy-on-write PixelBuffer structures
├── render/          Deferred rasterizer pipeline (Bresenham lines, midpoint circles, etc.)
├── audio/           Copy-on-write AudioBuffer mixing, resampling, and device audio loops
├── events/          Immutable queue, event filter/map/fold
├── input/           Keyboard, mouse, touch, gamepad, sensors, haptics adapters
├── clipboard/       Operating system clipboard interaction
├── timer/           High-resolution clock timers
├── filesystem/      RWops byte buffers and IO helpers
├── platform/        Direct ctypes OS wrappers (X11, Win32, Quartz, Headless)
└── compat/          Optional SDL2-style compatible functional names
```

## Architectural Pillars

### 1. Functional Core / Imperative Shell

To eliminate unpredictable side effects, the logic in Effy is split:
- **Functional Core (Pure):** All transformations, rasterizations, math, and buffer operations are pure functions that operate on immutable data structures (frozen dataclasses with slots). They take an input state and return a new, updated state. No global state is altered.
- **Imperative Shell (Impure):** All operations interacting with the OS, FFI, memory boundaries, or files are wrapped in `Effect[T]` objects. These effects are lazy computations. They do nothing when created; they are only evaluated when explicitly called with `.run()` at the final application boundary.

### 2. Copy-on-Write and Array Recycling

Modifying large pixel matrices (`PixelBuffer`) or audio streams (`AudioBuffer`) under functional immutable rules can cause extreme garbage collection overhead due to constant array allocation. 

Effy solves this with two patterns:
- **Copy-on-Write (CoW):** High-performance operations return fresh wrapper instances pointing to new, modified array backings only when actual modifications happen.
- **JIT-Friendly Memory Pools:** Under the hood, arrays are checked out and recycled via the `PixelBufferPool`. This allows PyPy's JIT to reuse large chunks of pre-allocated system memory instead of triggering heavy garbage collection sweeps.

### 3. FFI Isolation

No ctypes or platform-specific imports are allowed in core domain files. All direct OS calls are completely isolated inside `Effy/platform/` modules (e.g., Linux X11 socket read/writes, Windows GDI handles). Domain modules only interact with these platform adapters via abstract platform protocols.

### 4. Direct Error Monads

Effy avoids raising standard Python runtime exceptions for normal runtime failures (such as a failure to create an audio device or window). Fallible operations return a `Result[T, SDLError]` type:
- `Ok(value)` indicates a successful computation.
- `Err(error)` contains the detailed failure context.

Exceptions are strictly reserved for developer errors, such as invalid type instantiations or assertion failures.

---

## Development & Formatting Rules

- All core structures utilize `@dataclass(frozen=True, slots=True)` to prevent arbitrary runtime mutations.
- Type annotations are required throughout. The codebase must pass strict static type-checking via `mypy --strict`.
- Styling and linting are maintained via `ruff`.
