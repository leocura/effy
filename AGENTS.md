# AGENTS.md — Effy

> [!NOTE]  
> This file has been revived to provide critical instructions for AI agents working on the Effy codebase. Always prioritize these guidelines when generating code or troubleshooting.

## 1. Functional Programming First (FP-First)
- **Immutability:** Effy adheres strictly to an FP-first paradigm. Prefer pure functions, immutable data structures, and copy-on-write semantics (e.g., `PixelBuffer`, `AudioBuffer`).
- **No Hidden State:** Avoid mutable object-oriented state, class-level side effects, and imperative stateful mutations. Use deferred execution and clean monad-like structures (like `RenderContext` and `Result` types such as `Ok`/`Err`).
- **PyPy JIT Optimization:** Realize that Effy heavily relies on PyPy's JIT compiler. Make sure mathematical pipelines, SDF shaders, and rendering logic are written clearly as pure functional transformations to hit fast-paths. Use `@pure` decorators where relevant.

## 2. Expressive Logging and Error Handling
- **High-Fidelity Context:** Logs and errors must be highly expressive to facilitate debugging and optimization. Never throw generic or empty exceptions.
- **Traceability:** When returning `Err` or logging a warning, always include the necessary state context, parameter values, and clear guidance on why a failure occurred. 
- **Optimization Hints:** When dealing with software rasterization or audio mixing bottlenecks, emit logs that can actively help developers (and agents) identify performance regressions.

## 3. General Rules
- Ensure code readability and maintainability. Do not over-comment inline code; instead, let the functional structure speak for itself.
- All classes and functions **must** have descriptive docstrings.
- Stick to the Minimal External Dependencies rule. Rely entirely on standard libraries (`ctypes`, `array`, `struct`, etc.) and `wgpu`.
