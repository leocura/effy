from __future__ import annotations
from dataclasses import dataclass
from typing import cast
from Effy._internal.fp import _EVOLVE_SENTINEL

@dataclass(frozen=True, slots=True)
class Point:
    """An immutable 2D point representation with integer coordinates.

    Attributes:
        x: X-coordinate of the point.
        y: Y-coordinate of the point.
    """
    x: int
    y: int

    def evolve(self, x: int | object = _EVOLVE_SENTINEL, y: int | object = _EVOLVE_SENTINEL) -> Point:
        """Create a new Point instance with updated coordinates using a copy-on-write model.

        Args:
            x: New x-coordinate or sentinel to keep current value.
            y: New y-coordinate or sentinel to keep current value.

        Returns:
            A new Point instance.
        """
        return Point(
            self.x if x is _EVOLVE_SENTINEL else cast(int, x),
            self.y if y is _EVOLVE_SENTINEL else cast(int, y),
        )

@dataclass(frozen=True, slots=True)
class FPoint:
    """An immutable 2D point representation with floating-point coordinates.

    Attributes:
        x: X-coordinate of the point.
        y: Y-coordinate of the point.
    """
    x: float
    y: float

    def evolve(self, x: float | object = _EVOLVE_SENTINEL, y: float | object = _EVOLVE_SENTINEL) -> FPoint:
        """Create a new FPoint instance with updated coordinates using a copy-on-write model.

        Args:
            x: New x-coordinate or sentinel to keep current value.
            y: New y-coordinate or sentinel to keep current value.

        Returns:
            A new FPoint instance.
        """
        return FPoint(
            self.x if x is _EVOLVE_SENTINEL else cast(float, x),
            self.y if y is _EVOLVE_SENTINEL else cast(float, y),
        )

@dataclass(frozen=True, slots=True)
class Rect:
    """An immutable 2D rectangle representation with integer dimensions.

    Attributes:
        x: X-coordinate of the top-left corner.
        y: Y-coordinate of the top-left corner.
        w: Width of the rectangle.
        h: Height of the rectangle.
    """
    x: int
    y: int
    w: int
    h: int

    def evolve(self, x: int | object = _EVOLVE_SENTINEL, y: int | object = _EVOLVE_SENTINEL, w: int | object = _EVOLVE_SENTINEL, h: int | object = _EVOLVE_SENTINEL) -> Rect:
        """Create a new Rect instance with updated dimensions using a copy-on-write model.

        Args:
            x: New x-coordinate or sentinel to keep current value.
            y: New y-coordinate or sentinel to keep current value.
            w: New width or sentinel to keep current value.
            h: New height or sentinel to keep current value.

        Returns:
            A new Rect instance.
        """
        return Rect(
            self.x if x is _EVOLVE_SENTINEL else cast(int, x),
            self.y if y is _EVOLVE_SENTINEL else cast(int, y),
            self.w if w is _EVOLVE_SENTINEL else cast(int, w),
            self.h if h is _EVOLVE_SENTINEL else cast(int, h),
        )

@dataclass(frozen=True, slots=True)
class FRect:
    """An immutable 2D rectangle representation with floating-point dimensions.

    Attributes:
        x: X-coordinate of the top-left corner.
        y: Y-coordinate of the top-left corner.
        w: Width of the rectangle.
        h: Height of the rectangle.
    """
    x: float
    y: float
    w: float
    h: float

    def evolve(self, x: float | object = _EVOLVE_SENTINEL, y: float | object = _EVOLVE_SENTINEL, w: float | object = _EVOLVE_SENTINEL, h: float | object = _EVOLVE_SENTINEL) -> FRect:
        """Create a new FRect instance with updated dimensions using a copy-on-write model.

        Args:
            x: New x-coordinate or sentinel to keep current value.
            y: New y-coordinate or sentinel to keep current value.
            w: New width or sentinel to keep current value.
            h: New height or sentinel to keep current value.

        Returns:
            A new FRect instance.
        """
        return FRect(
            self.x if x is _EVOLVE_SENTINEL else cast(float, x),
            self.y if y is _EVOLVE_SENTINEL else cast(float, y),
            self.w if w is _EVOLVE_SENTINEL else cast(float, w),
            self.h if h is _EVOLVE_SENTINEL else cast(float, h),
        )


def intersect_rect(a: Rect, b: Rect) -> Rect | None:
    """Compute the intersection of two rectangles.

    Args:
        a: The first Rect.
        b: The second Rect.

    Returns:
        The intersecting Rect, or None if they do not overlap.
    """
    x1 = max(a.x, b.x)
    y1 = max(a.y, b.y)
    x2 = min(a.x + a.w, b.x + b.w)
    y2 = min(a.y + a.h, b.y + b.h)
    w = x2 - x1
    h = y2 - y1
    if w <= 0 or h <= 0:
        return None
    return Rect(x1, y1, w, h)


def union_rect(a: Rect, b: Rect) -> Rect:
    """Compute the smallest rectangle enclosing both input rectangles.

    Args:
        a: The first Rect.
        b: The second Rect.

    Returns:
        The enclosing Rect.
    """
    x1 = min(a.x, b.x)
    y1 = min(a.y, b.y)
    x2 = max(a.x + a.w, b.x + b.w)
    y2 = max(a.y + a.h, b.y + b.h)
    return Rect(x1, y1, x2 - x1, y2 - y1)


def point_in_rect(p: Point, r: Rect) -> bool:
    """Hit test to check if a point is inside a rectangle.

    Args:
        p: The Point to check.
        r: The Rect to check against.

    Returns:
        True if the point lies within the rectangle's bounds, False otherwise.
    """
    return r.x <= p.x < r.x + r.w and r.y <= p.y < r.y + r.h


def rect_empty(r: Rect) -> bool:
    """Check if a rectangle is empty (width or height is 0 or less).

    Args:
        r: The Rect to check.

    Returns:
        True if the rectangle has no area, False otherwise.
    """
    return r.w <= 0 or r.h <= 0


