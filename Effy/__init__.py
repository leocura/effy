"""Effy: A pure-Python 2D graphics, audio, and windowing library inspired by SDL2 and Pygame.

This library is designed from scratch with a functional core and minimal external dependencies.
"""
from __future__ import annotations
import sys
import warnings

if sys.implementation.name != "pypy":
    warnings.warn(
        "Effy is optimized for PyPy. Performance on CPython will be significantly worse "
        "for software rasterization and audio mixing. Consider running under PyPy for "
        "production use.",
        RuntimeWarning,
        stacklevel=2,
    )


