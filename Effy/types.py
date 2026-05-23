from __future__ import annotations
from dataclasses import dataclass
from typing import NewType, cast
from Effy._internal.result import Result, Ok, Err
from Effy._internal.effect import Effect
from Effy._internal.fp import _EVOLVE_SENTINEL

WindowID = NewType("WindowID", int)
TextureID = NewType("TextureID", int)
Ticks = NewType("Ticks", int)  # milliseconds
TimerID = NewType("TimerID", int)


@dataclass(frozen=True, slots=True)
class Color:
    """An immutable representation of an RGBA color.

    Attributes:
        r: Red component (0-255).
        g: Green component (0-255).
        b: Blue component (0-255).
        a: Alpha transparency component (0-255). Defaults to 255 (fully opaque).
    """

    r: int
    g: int
    b: int
    a: int = 255

    def __post_init__(self) -> None:
        """Validate that all color components are within the [0, 255] range."""
        if not (
            0 <= self.r <= 255
            and 0 <= self.g <= 255
            and 0 <= self.b <= 255
            and 0 <= self.a <= 255
        ):
            raise ValueError(
                f"Color components must be 0-255, got ({self.r}, {self.g}, {self.b}, {self.a})"
            )

    def evolve(
        self,
        r: int | object = _EVOLVE_SENTINEL,
        g: int | object = _EVOLVE_SENTINEL,
        b: int | object = _EVOLVE_SENTINEL,
        a: int | object = _EVOLVE_SENTINEL,
    ) -> Color:
        """Create a new Color instance with updated components using a copy-on-write model.

        Args:
            r: New red component value or sentinel to retain current value.
            g: New green component value or sentinel to retain current value.
            b: New blue component value or sentinel to retain current value.
            a: New alpha component value or sentinel to retain current value.

        Returns:
            A new Color instance.
        """
        return Color(
            self.r if r is _EVOLVE_SENTINEL else cast(int, r),
            self.g if g is _EVOLVE_SENTINEL else cast(int, g),
            self.b if b is _EVOLVE_SENTINEL else cast(int, b),
            self.a if a is _EVOLVE_SENTINEL else cast(int, a),
        )


@dataclass(frozen=True, slots=True)
class WindowParams:
    """Frozen dataclass representing the creation parameters of a window."""

    title: str
    x: int
    y: int
    w: int
    h: int
    flags: int


__all__ = [
    "WindowID",
    "TextureID",
    "Ticks",
    "TimerID",
    "Color",
    "WindowParams",
    "Result",
    "Ok",
    "Err",
    "Effect",
]
