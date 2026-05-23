# Effy Core Architecture

This directory contains the core implementation of Effy. Rather than wrapping SDL2 in standard mutable classes, we build our engine around a strict **Functional Core / Imperative Shell** pattern. This couples functional immutability with JIT-friendly memory recycling to achieve near-native execution speed without compiling a single line of C.

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

- **Functional Core (Pure):** We try to minimize mutations and side effects as much as possible. All transformations, math, and rasterizations operate as pure transformations over immutable domain models (`@dataclass(frozen=True, slots=True)`). This allows us to test drawing logic without mocks or state management.
- **Imperative Shell (Impure):** FFI, OS IO, and side-effects are completely isolated. All effectful operations are wrapped inside an `Effect[T]` wrapper, composed lazily and evaluated only at the final application boundary via `.run()`. We let the OS handle state; we just handle math.

### 2. Copy-on-Write & Memory Pools

Since purely functional rendering on large pixel matrices usually melts interpreters we attempt to bypass the heavy overhead by implementing the following:

- **Copy-on-Write (CoW):** High-performance operations on `PixelBuffer` and `AudioBuffer` return new wrappers or views only upon actual mutation.
- **Buffer Recycling:** Allocations are recycled via `PixelBufferPool`. By reusing pre-allocated system memory under the hood, we keep PyPy's JIT execution smooth, achieving zero-allocation draw passes that rival compiled C performance.

### 3. FFI Isolation

All standard library `ctypes` integrations and platform-specific adapters are isolated inside `Effy/platform/`. This establishes a clean boundary between low-level operating system calls and the rest of the library's domain code. The core codebase remains platform-agnostic and relies strictly on abstract system adapters.

### 4. Explicit Error Handling

To avoid implicit or unhandled control-flow jumps, Effy uses explicit `Result[T, EffyError]` types (`Ok` and `Err`) instead of standard Python runtime exceptions for expected failures. When an operation can fail, its type signature explicitly requires it, forcing developers to unpack the result and preventing silent errors. Standard Python exceptions are reserved strictly for developer assertions and type instantiation errors.

---

## Development & Formatting Rules

- All core structures utilize `@dataclass(frozen=True, slots=True)` to prevent arbitrary runtime mutations.
- Type annotations are required throughout. The codebase must pass strict static type-checking via `mypy --strict`.
- Styling and linting are maintained via `ruff`.
