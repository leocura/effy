# Effy vs Pygame Performance Report

**Generated at:** 2026-05-24 00:06:52

## Environment

- **Effy Interpreter**: `/home/leocura/antigravity/effy/benchmarks/../.venv_pypy/bin/pypy3`
- **Pygame Interpreter**: `/home/leocura/antigravity/effy/benchmarks/../.venv_cpython/bin/python`

### Scenario: `scenario_game_loop.py`

- Effy: pypy 3.11.15
- Pygame: cpython 3.14.4

| Workload | Effy Avg FPS | Pygame Avg FPS | Speedup | Effy 1% Low | Pygame 1% Low | Effy 0.1% Low | Pygame 0.1% Low | Mem Peak (E/P) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Game Loop (1000 Sprites) | 57 | 325 | **0.18x** | 26.13ms | 3.35ms | 26.99ms | 3.60ms | 0.0MB / 0.0MB |

### Scenario: `scenario_particles.py`

- Effy: pypy 3.11.15
- Pygame: cpython 3.14.4

| Workload | Effy Avg FPS | Pygame Avg FPS | Speedup | Effy 1% Low | Pygame 1% Low | Effy 0.1% Low | Pygame 0.1% Low | Mem Peak (E/P) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Particle System (2000 Particles) | 69 | 98 | **0.70x** | 25.16ms | 12.71ms | 28.08ms | 13.02ms | 0.0MB / 0.0MB |

### Scenario: `scenario_pixel_buffer.py`

- Effy: pypy 3.11.15
- Pygame: cpython 3.14.4

| Workload | Effy Avg FPS | Pygame Avg FPS | Speedup | Effy 1% Low | Pygame 1% Low | Effy 0.1% Low | Pygame 0.1% Low | Mem Peak (E/P) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Pixel Buffer (1280x720) | 422 | 1 | **431.60x** | 3.68ms | 1060.16ms | 3.68ms | 1060.16ms | 0.0MB / 0.0MB |

### Scenario: `scenario_audio_mixer.py`

- Effy: pypy 3.11.15
- Pygame: cpython 3.14.4

| Workload | Effy Avg FPS | Pygame Avg FPS | Speedup | Effy 1% Low | Pygame 1% Low | Effy 0.1% Low | Pygame 0.1% Low | Mem Peak (E/P) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Audio Mix (4096 Samples) | 10256 | 462 | **22.18x** | 0.21ms | 3.10ms | 6.18ms | 3.19ms | 0.0MB / 0.0MB |

