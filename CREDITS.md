# Credits & Attributions

Effy is a pure-Python 2D graphics, audio, and windowing library inspired by and modeled after the API designs of **SDL2** and **Pygame**. 

Effy is a complete rewrite from scratch built on modern functional programming principles and tailored for the PyPy JIT compiler. To clarify its relationship with these libraries and honor their contributions:

---

## 1. Simple DirectMedia Layer (SDL2)

- **Inspiration:** Effy's window management, event systems, rendering context structure, filesystem abstractions, and high-resolution timer APIs are inspired by Simple DirectMedia Layer (SDL2).
- **Compatibility Interface:** The `Effy.compat` module exposes functional bindings (e.g., `SDL_Init`, `SDL_CreateWindow`, `SDL_Color`) mapped onto Effy's underlying system core to provide an easy transition for developers coming from SDL2.
- **License Notice:** SDL2 is Copyright (C) 1997-2026 Sam Lantinga and other contributors, and is licensed under the [zlib License](https://www.libsdl.org/license.php).
- **Distribution Notice:** Effy **does not bundle, package, or distribute** any SDL2 binary files (such as `.dll`, `.so`, or `.dylib` libraries) or original C source code. All platform integrations are implemented in pure Python using `ctypes` to invoke your native operating system's graphics/windowing layers directly (Win32, Quartz, X11).

---

## 2. Pygame

- **Inspiration:** Pygame inspired the development of a lightweight, accessible Python ecosystem for 2D software rendering, game development, and multimedia processing.
- **License Notice:** Pygame is licensed under the [GNU LGPL version 2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html).
- **No Distribution:** Pygame is **NOT distributed, bundled, or vendored** inside the `Effy` core library. It is completely absent from any runtime imports or source modules of Effy.
- **Benchmark Usage:** Pygame is only used conditionally in isolated benchmark suites (`benchmarks/`) to run performance comparisons between the compiled PyPy JIT and Pygame under CPython.

---

## 3. Low-Level Operating System APIs

Effy's platform subsystem dynamically interacts directly with the hosting native operating system's APIs via standard library `ctypes` to achieve lightweight, dependency-free graphics and audio loops. We credit and attribute the following native software interfaces:

- **Linux (X11 & Audio Stack):**
  - **Xlib & Xrandr (`libX11.so`, `libGL.so.1`):** Used to interface directly with the X Window System to manage hardware displays, create windows, handle system inputs (keyboard, mouse), and manage OpenGL-accelerated context stubs.
  - **PulseAudio & ALSA (`libpulse-simple.so.0`, `libasound.so.2`):** Used to feed raw sound buffers directly into native sound systems (PulseAudio simple interface and Advanced Linux Sound Architecture client library).
- **Windows (Win32/GDI & Audio Stack):**
  - **User32 / GDI32 / Kernel32:** Used for Win32 window creation, display monitoring bounds, and drawing/flipping `PixelBuffer` buffers using Windows Graphics Device Interface (GDI) context handles.
  - **WASAPI (`ole32.dll` / COM):** Used to establish an audio stream through the Windows Audio Session API (WASAPI) via COM interface dispatching.
  - **XInput (`xinput1_4.dll` / `xinput1_3.dll`):** Used to query standard Xbox controller device state, axis configurations, and trigger haptic rumble effects.

---

## 4. Signed Distance Field & CSG Mathematics

Effy's custom shader pipeline subsystem ([shader.py](file:///home/leocura/antigravity/effy/Effy/render/shader.py)) implements functional rendering primitives:
- **Inspiration:** Signed Distance Field (SDF) mathematics, Constructive Solid Geometry (CSG) logical operations (union, intersection, subtraction), and gooey polynomial smooth unions are inspired by computer graphics formulations popularized in the graphics field by developers like **Inigo Quilez**.

---

## 5. Core Development Tooling

We attribute the active open-source ecosystems that maintain the linting, type-checking, and property-based testing quality metrics of Effy:
- **Hypothesis:** Property-based testing framework (licensed under the [Mozilla Public License 2.0](https://github.com/HypothesisWorks/hypothesis/blob/master/hypothesis-python/LICENSE.txt)). Used for proving the structural boundaries of touch gestures and results.
- **pytest:** Unit testing framework (licensed under the [MIT License](https://github.com/pytest-dev/pytest/blob/main/LICENSE)).
- **mypy:** Strict type-checking utility (licensed under the [MIT License](https://github.com/python/mypy/blob/master/LICENSE)).
- **ruff:** High-performance Python linter and formatter (licensed under the [MIT License](https://github.com/astral-sh/ruff/blob/main/LICENSE)).
