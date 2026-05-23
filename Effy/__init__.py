"""Effy: Pure Python SDL Reimplementation."""
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


