# Effy vs Pygame Comprehensive Benchmark Report

Generated at: 2026-05-22 20:59:57

## Environment
## Suite: `test_primitives.py`

- Effy version string: pypy 3.11.13
- Pygame version string: cpython 3.13.5

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Fill Rect Small | 2.7305 | 9.5058 | 3.48x | 7.1128 | 22.6908 | 0.00 | 0.00 |
| Fill Rect Large | 2.8360 | 2.0833 | 0.73x | 6.5938 | 4.5787 | 0.00 | 0.00 |
| Draw Line | 13.5230 | 16.1075 | 1.19x | 27.6243 | 31.7333 | 0.00 | 0.00 |
| Fill Circle | 3.4379 | 2.7966 | 0.81x | 19.9177 | 5.5943 | 0.00 | 0.00 |
| Draw Rect | 29.6512 | 7.5196 | 0.25x | 41.5545 | 17.2426 | 0.00 | 0.00 |

## Suite: `test_surfaces.py`

- Effy version string: pypy 3.11.13
- Pygame version string: cpython 3.13.5

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Blit Small | 41.2399 | 2.7915 | 0.07x | 87.7006 | 5.0280 | 0.00 | 0.00 |
| Blit Scaled | 23.1707 | 4.7273 | 0.20x | 42.8495 | 6.8837 | 0.00 | 0.00 |
| Blit Bilinear | 75.1694 | 9.0632 | 0.12x | 111.0837 | 10.7300 | 0.00 | 0.00 |

## Suite: `test_particles.py`

- Effy version string: pypy 3.11.13
- Pygame version string: cpython 3.13.5

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Particles Sim (2000) | 5.2157 | 14.0916 | 2.70x | 16.6485 | 24.9644 | 0.00 | 0.01 |

## Suite: `test_triangles.py`

- Effy version string: pypy 3.11.13
- Pygame version string: cpython 3.13.5

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Fill Triangles | 249.8263 | 61.0629 | 0.24x | 377.5589 | 98.4954 | 0.00 | 0.00 |

## Suite: `test_shader.py`

- Effy version string: pypy 3.11.13
- Pygame version string: cpython 3.13.5

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| SDF CSG Shader 500x500 | 73.2411 | 13455.1364 | 183.71x | 81.1613 | 14652.6764 | 0.00 | 0.00 |

## Suite: `test_audio.py`

- Effy version string: pypy 3.11.13
- Pygame version string: cpython 3.13.5

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Audio Spec Conversion | 0.2717 | 212.6911 | 782.95x | 0.8364 | 257.7766 | 0.00 | 0.54 |
| Audio Multi-Stream Mix | 1.1005 | 98.5380 | 89.54x | 2.0949 | 125.7485 | 0.00 | 0.14 |

## Suite: `test_geometry.py`

- Effy version string: pypy 3.11.13
- Pygame version string: cpython 3.13.5

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Geometry Operations | 2.2212 | 12.9532 | 5.83x | 17.4576 | 20.6741 | 0.00 | 0.03 |

