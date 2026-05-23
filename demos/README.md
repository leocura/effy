# Effy Visual Human Testing Suite

Interactive demo programs for manually testing Effy's real platform adapter —
graphics, audio, input, window management, and blitting — with actual windows on screen.

> **These scripts must be run with PyPy.** Effy blocks CPython at import time.

---

## Prerequisites

- PyPy 3.9+ installed and on PATH as `pypy3`
- A running X session (`$DISPLAY` is set)
- For audio: PulseAudio or ALSA available (the adapter tries PulseAudio first,
  then ALSA, then falls back to a dummy device and prints a warning)
- Run all commands from the `effy/` directory

---

## Running the demos

```bash
cd effy/

.venv_pypy/bin/pypy3 demos/test_graphics.py   # Software rasterizer primitives
.venv_pypy/bin/pypy3 demos/test_audio.py      # 440 Hz sine tone
.venv_pypy/bin/pypy3 demos/test_input.py      # Keyboard and mouse live tracking
.venv_pypy/bin/pypy3 demos/test_window.py     # Resize / move / minimize / maximize
.venv_pypy/bin/pypy3 demos/test_blit.py       # All four blit modes side by side
```

---

## What to verify (pass criteria)

| Demo | Pass when… |
|---|---|
| `test_graphics.py` | Each primitive (rect, circle, line, triangle, alpha overlay) appears correctly shaped and colored. Press **Space** to cycle, **Escape** to quit. |
| `test_audio.py` | You hear a clean, undistorted A4 (440 Hz) tone for ~2 seconds. The terminal prints which audio backend was selected. |
| `test_input.py` | Window title updates on every keypress. A colored dot follows the mouse cursor. Dot color changes on left / middle / right click. Press **Escape** to quit. |
| `test_window.py` | Each Space press triggers a visible operation: resize → move → minimize → maximize → restore. The terminal prints each step. Press **Escape** to quit. |
| `test_blit.py` | Four quadrants each show the same source pattern rendered with a different blit mode (1:1, scaled nearest, scaled bilinear, alpha-blended). Press **Escape** to quit. |
