"""Frozen command dataclasses for the deferred rendering pipeline.

Each dataclass encodes one drawing operation as a pure value object. Commands
are accumulated inside RenderContext._commands as an immutable tuple and are
rasterized in a single pass by _resolve_commands inside render_present.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Union, Callable
from Effy.video.rect import Rect, Point
from Effy.types import Color

Field = Callable[[int, int], float]


@dataclass(frozen=True, slots=True)
class FillRectCmd:
    """Command to fill a rectangular area with a solid color.

    Attributes:
        rect: The Rect to fill, or None to fill the entire surface.
        color: The fill Color.
    """
    rect: Rect | None
    color: Color


@dataclass(frozen=True, slots=True)
class DrawRectCmd:
    """Command to draw the outline of a rectangle.

    Attributes:
        rect: The Rect to stroke.
        color: The stroke Color.
    """
    rect: Rect
    color: Color


@dataclass(frozen=True, slots=True)
class DrawLineCmd:
    """Command to draw a line between two points.

    Attributes:
        p1: Start point.
        p2: End point.
        color: The line Color.
    """
    p1: Point
    p2: Point
    color: Color


@dataclass(frozen=True, slots=True)
class DrawCircleCmd:
    """Command to draw the outline of a circle.

    Attributes:
        center: Center point of the circle.
        radius: Radius of the circle.
        color: The stroke Color.
    """
    center: Point
    radius: int
    color: Color


@dataclass(frozen=True, slots=True)
class FillCircleCmd:
    """Command to fill a circle with a solid color.

    Attributes:
        center: Center point of the circle.
        radius: Radius of the circle.
        color: The fill Color.
    """
    center: Point
    radius: int
    color: Color


@dataclass(frozen=True, slots=True)
class FillTriangleCmd:
    """Command to fill a triangle with a solid color.

    Attributes:
        p1: First vertex.
        p2: Second vertex.
        p3: Third vertex.
        color: The fill Color.
    """
    p1: Point
    p2: Point
    p3: Point
    color: Color


@dataclass(frozen=True, slots=True)
class BlitCmd:
    """Command to copy a source buffer region onto the render target.

    Attributes:
        src_buffer: The source PixelBuffer to copy from.
        src_rect: The source region, or None for the full source.
        dst_rect: The destination region, or None for full fit.
    """
    src_buffer: Any  # PixelBuffer — Any to avoid circular imports
    src_rect: Rect | None
    dst_rect: Rect | None


@dataclass(frozen=True, slots=True)
class BlitBlendedCmd:
    """Command to alpha-blend a source buffer region onto the render target.

    Attributes:
        src_buffer: The source PixelBuffer to blend from.
        src_rect: The source region, or None for the full source.
        dst_rect: The destination region, or None for full fit.
    """
    src_buffer: Any  # PixelBuffer — Any to avoid circular imports
    src_rect: Rect | None
    dst_rect: Rect | None


@dataclass(frozen=True, slots=True)
class BlitScaledCmd:
    """Command to copy and scale a source buffer region onto the render target.

    Attributes:
        src_buffer: The source PixelBuffer to scale from.
        src_rect: The source region, or None for the full source.
        dst_rect: The destination region to scale into.
    """
    src_buffer: Any  # PixelBuffer — Any to avoid circular imports
    src_rect: Rect | None
    dst_rect: Rect | None


@dataclass(frozen=True, slots=True)
class BlitBilinearCmd:
    """Command to copy and scale with bilinear filtering onto the render target.

    Attributes:
        src_buffer: The source PixelBuffer to scale from.
        src_rect: The source region, or None for the full source.
        dst_rect: The destination region to scale into.
    """
    src_buffer: Any  # PixelBuffer — Any to avoid circular imports
    src_rect: Rect | None
    dst_rect: Rect | None


@dataclass(frozen=True, slots=True)
class FillPolygonCmd:
    """Command to fill an arbitrary polygon with a solid color.

    Attributes:
        points: A tuple of vertices defining the polygon.
        color: The fill Color.
    """
    points: tuple[Point, ...]
    color: Color


@dataclass(frozen=True, slots=True)
class DrawCurveCmd:
    """Command to draw a Bezier curve (quadratic or cubic).

    Attributes:
        points: A tuple of 3 (quadratic) or 4 (cubic) control Points.
        color: The stroke Color.
    """
    points: tuple[Point, ...]
    color: Color


@dataclass(frozen=True, slots=True)
class RenderFieldCmd:
    """Command to render a signed distance field.

    Attributes:
        rect: The bounding Rect to limit rendering, or None for the full surface.
        field: The SDF function to render.
        color: The fill Color.
    """
    rect: Rect | None
    field: Field
    color: Color


DrawCmd = Union[
    FillRectCmd,
    DrawRectCmd,
    DrawLineCmd,
    DrawCircleCmd,
    FillCircleCmd,
    FillTriangleCmd,
    FillPolygonCmd,
    DrawCurveCmd,
    BlitCmd,
    BlitBlendedCmd,
    BlitScaledCmd,
    BlitBilinearCmd,
    RenderFieldCmd,
]

__all__ = [
    "DrawCmd",
    "FillRectCmd",
    "DrawRectCmd",
    "DrawLineCmd",
    "DrawCircleCmd",
    "FillCircleCmd",
    "FillTriangleCmd",
    "FillPolygonCmd",
    "DrawCurveCmd",
    "BlitCmd",
    "BlitBlendedCmd",
    "BlitScaledCmd",
    "BlitBilinearCmd",
    "Field",
    "RenderFieldCmd",
]
