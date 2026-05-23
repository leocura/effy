# Credits & Attributions

Effy is a pure-Python 2D graphics, audio, and windowing library inspired by and modeled after the API designs of **SDL2** and **Pygame**. 

Effy is a complete rewrite from scratch built on modern functional programming principles and tailored for the PyPy JIT compiler. To clarify its relationship with these libraries and honor their contributions:

## 1. Simple DirectMedia Layer (SDL2)

- **Inspiration:** Effy's window management, event systems, rendering context structure, filesystem abstractions, and high-resolution timer APIs are inspired by Simple DirectMedia Layer (SDL2).
- **Compatibility Interface:** The `Effy.compat` module exposes functional bindings (e.g., `SDL_Init`, `SDL_CreateWindow`, `SDL_Color`) mapped onto Effy's underlying system core to provide an easy transition for developers coming from SDL2.
- **License Notice:** SDL2 is Copyright (C) 1997-2026 Sam Lantinga and is licensed under the [zlib License](https://www.libsdl.org/license.php).
- **Distribution Notice:** Effy **does not bundle, package, or distribute** any SDL2 binary files (such as `.dll`, `.so`, or `.dylib` libraries) or original C source code. All platform integrations are implemented in pure Python using `ctypes` to invoke your native operating system's graphics/windowing layers directly (Win32, Quartz, X11).

---

## 2. Pygame

- **Inspiration:** Pygame inspired the development of a lightweight, accessible Python ecosystem for 2D software rendering, game development, and multimedia processing.
- **License Notice:** Pygame is licensed under the [GNU LGPL version 2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html).
- **No Distribution:** Pygame is **NOT distributed, bundled, or vendored** inside the `Effy` core library. It is completely absent from any runtime imports or source modules of Effy.
- **Benchmark Usage:** Pygame is only used conditionally in isolated benchmark suites (`benchmarks/`) to run performance comparisons between the compiled PyPy JIT and Pygame under CPython.
