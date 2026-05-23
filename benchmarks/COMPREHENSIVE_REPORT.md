# Effy vs Pygame Comprehensive Benchmark Report

Generated at: 2026-05-23 18:24:27

## Environment
## Suite: `test_primitives.py`

- Effy version string: pypy 3.11.15
- Pygame version string: cpython 3.14.4

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Fill Rect Small | 1.0269 | 1.7417 | 1.70x | 2.2742 | 1.8129 | 0.00 | 0.00 |
| Fill Rect Large | 0.6196 | 1.4501 | 2.34x | 0.6410 | 1.5225 | 0.00 | 0.00 |
| Draw Line | 4.6739 | 3.9369 | 0.84x | 9.9511 | 4.0983 | 0.00 | 0.00 |
| Fill Circle | 1.7223 | 0.9802 | 0.57x | 3.6187 | 1.0152 | 0.00 | 0.00 |
| Draw Rect | 15.6582 | 1.9373 | 0.12x | 23.3611 | 2.0927 | 0.00 | 0.00 |

## Suite: `test_surfaces.py`

- Effy version string: pypy 3.11.15
- Pygame version string: cpython 3.14.4

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Blit Small | 6.3815 | 1.2562 | 0.20x | 7.5707 | 1.7288 | 0.00 | 0.00 |
| Blit Scaled | 9.9854 | 3.1178 | 0.31x | 13.0823 | 3.6691 | 0.00 | 0.00 |
| Blit Bilinear | 44.2211 | 4.7144 | 0.11x | 48.2515 | 5.0723 | 0.00 | 0.00 |

## Suite: `test_particles.py`

- Effy version string: pypy 3.11.15
- Pygame version string: cpython 3.14.4

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Particles Sim (2000) | 2.1202 | 6.6660 | 3.14x | 4.8630 | 7.6780 | 0.00 | 0.01 |

## Suite: `test_triangles.py`

- Effy version string: pypy 3.11.15
- Pygame version string: cpython 3.14.4

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Fill Triangles | 175.3431 | 18.6703 | 0.11x | 197.9334 | 21.9739 | 0.00 | 0.00 |

## Suite: `test_shader.py`

- Effy version string: pypy 3.11.15
- Pygame version string: cpython 3.14.4

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| SDF CSG Shader 500x500 | 55.7965 | 4243.6404 | 76.06x | 57.6459 | 4823.5555 | 0.00 | 0.00 |

## Suite: `test_audio.py`

- Effy version string: pypy 3.11.15
- Pygame version string: cpython 3.14.4

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Audio Spec Conversion | 0.1047 | 51.1133 | 488.02x | 0.1886 | 59.7475 | 0.00 | 0.54 |
| Audio Multi-Stream Mix | 0.6056 | 18.0746 | 29.84x | 5.8247 | 18.4655 | 0.00 | 0.14 |

## Suite: `test_geometry.py`

- Effy version string: pypy 3.11.15
- Pygame version string: cpython 3.14.4

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Geometry Operations | 0.9833 | 5.8994 | 6.00x | 8.6503 | 6.2413 | 0.00 | 0.03 |

## Suite: `test_events.py`

- Effy version string: pypy 3.11.15
- Pygame version string: cpython 3.14.4

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Push Events Seq | 3.3493 | 1.0339 | 0.31x | 10.5724 | 1.1976 | 0.00 | 0.00 |
| Push Many | 0.0048 | 0.7974 | 166.59x | 0.0721 | 0.9771 | 0.00 | 0.00 |
| Full Cycle | 3.0565 | 3.3936 | 1.11x | 3.0720 | 3.7422 | 0.00 | 0.19 |

## Suite: `test_image.py`

- Effy version string: pypy 3.11.15
- Pygame version string: cpython 3.14.4

| Test | Effy Avg (ms) | Pygame Avg (ms) | Speedup (Pygame/Effy) | Effy 1% Low (ms) | Pygame 1% Low (ms) | Effy Mem Peak (MB) | Pygame Mem Peak (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Load BMP (64x64) | 0.0939 | 0.0181 | 0.19x | 0.7190 | 0.0461 | 0.00 | 0.00 |
| Load PNG (64x64) | 0.1504 | 0.0222 | 0.15x | 1.3701 | 0.0282 | 0.00 | 0.00 |

