from __future__ import annotations
from Effy.video.surface import PixelBuffer
from Effy.video.rect import Rect, Point
from Effy.types import Color
from Effy._internal.fp import pure
from Effy.render.renderer import (
    RenderContext, RendererFlags, create_renderer, render_clear, render_set_draw_color,
    render_fill_rect, render_draw_rect, render_present, render_copy,
    render_draw_line, render_draw_circle, render_fill_circle, render_fill_triangle,
    render_copy_blended, render_copy_scaled, render_copy_bilinear
)
from Effy.render.texture import Texture
from Effy.render.shader import render_field

@pure
def fill_rect(surface: PixelBuffer, rect: Rect | None, color: Color) -> PixelBuffer:
    """Fill a rectangular area with a solid color returning a new PixelBuffer.

    Args:
        surface: The target PixelBuffer.
        rect: The Rect to fill, or None to fill the entire surface.
        color: The Color to fill with.

    Returns:
        A brand-new PixelBuffer with the filled rectangle command enqueued.
    """
    from Effy.render.commands import FillRectCmd
    return surface._append_command(FillRectCmd(rect=rect, color=color))

@pure
def draw_rect(surface: PixelBuffer, rect: Rect, color: Color) -> PixelBuffer:
    """Draw the outline of a rectangle returning a new PixelBuffer.

    Args:
        surface: The input PixelBuffer.
        rect: The Rect outline to draw.
        color: The Color of the outline.

    Returns:
        A brand-new PixelBuffer with the outline command enqueued.
    """
    from Effy.render.commands import DrawRectCmd
    return surface._append_command(DrawRectCmd(rect=rect, color=color))

@pure
def draw_line(surface: PixelBuffer, p1: Point, p2: Point, color: Color) -> PixelBuffer:
    """Draw a line between two points using Bresenham's algorithm returning a new PixelBuffer.

    Args:
        surface: The input PixelBuffer.
        p1: Start point.
        p2: End point.
        color: Color of the line.

    Returns:
        A brand-new PixelBuffer with the drawn line command enqueued.
    """
    from Effy.render.commands import DrawLineCmd
    return surface._append_command(DrawLineCmd(p1=p1, p2=p2, color=color))

@pure
def draw_circle(surface: PixelBuffer, center: Point, radius: int, color: Color) -> PixelBuffer:
    """Draw a circle outline returning a new PixelBuffer.

    Args:
        surface: The input PixelBuffer.
        center: The Point representing the circle center.
        radius: The radius of the circle.
        color: The Color of the circle boundary.

    Returns:
        A brand-new PixelBuffer with the circle outline command enqueued.
    """
    from Effy.render.commands import DrawCircleCmd
    return surface._append_command(DrawCircleCmd(center=center, radius=radius, color=color))

@pure
def fill_circle(surface: PixelBuffer, center: Point, radius: int, color: Color) -> PixelBuffer:
    """Fill a circle returning a new PixelBuffer.

    Args:
        surface: The input PixelBuffer.
        center: The Point representing the circle center.
        radius: The radius of the circle.
        color: The Color to fill the circle with.

    Returns:
        A brand-new PixelBuffer with the filled circle command enqueued.
    """
    from Effy.render.commands import FillCircleCmd
    return surface._append_command(FillCircleCmd(center=center, radius=radius, color=color))

@pure
def fill_triangle(surface: PixelBuffer, p1: Point, p2: Point, p3: Point, color: Color) -> PixelBuffer:
    """Fill a triangle returning a new PixelBuffer.

    Args:
        surface: The input PixelBuffer.
        p1: First vertex.
        p2: Second vertex.
        p3: Third vertex.
        color: Fill Color.

    Returns:
        A brand-new PixelBuffer with the filled triangle command enqueued.
    """
    from Effy.render.commands import FillTriangleCmd
    return surface._append_command(FillTriangleCmd(p1=p1, p2=p2, p3=p3, color=color))

@pure
def blit(src: PixelBuffer, src_rect: Rect | None, dst: PixelBuffer, dst_rect: Rect | None) -> PixelBuffer:
    """Blit a source buffer region onto a destination buffer returning a new PixelBuffer.

    Args:
        src: Source PixelBuffer.
        src_rect: Bounding region of source to copy, or None for entire source.
        dst: Destination PixelBuffer.
        dst_rect: Target location on destination.

    Returns:
        A brand-new PixelBuffer containing the blitted result command enqueued.
    """
    from Effy.render.commands import BlitCmd
    return dst._append_command(BlitCmd(src_buffer=src, src_rect=src_rect, dst_rect=dst_rect))

@pure
def blit_blended(src: PixelBuffer, src_rect: Rect | None, dst: PixelBuffer, dst_rect: Rect | None) -> PixelBuffer:
    """Alpha-blend a source buffer region onto a destination buffer returning a new PixelBuffer.

    Args:
        src: Source PixelBuffer.
        src_rect: Bounding region of source to copy, or None for entire source.
        dst: Destination PixelBuffer.
        dst_rect: Target location on destination.

    Returns:
        A brand-new PixelBuffer containing the alpha-blended result command enqueued.
    """
    from Effy.render.commands import BlitBlendedCmd
    return dst._append_command(BlitBlendedCmd(src_buffer=src, src_rect=src_rect, dst_rect=dst_rect))

@pure
def blit_scaled(src: PixelBuffer, src_rect: Rect | None, dst: PixelBuffer, dst_rect: Rect | None) -> PixelBuffer:
    """Blit and scale a source buffer region onto a destination buffer returning a new PixelBuffer.

    Args:
        src: Source PixelBuffer.
        src_rect: Bounding region of source to copy.
        dst: Destination PixelBuffer.
        dst_rect: Target scale bounding region on destination.

    Returns:
        A brand-new PixelBuffer with the scaled blit command enqueued.
    """
    from Effy.render.commands import BlitScaledCmd
    return dst._append_command(BlitScaledCmd(src_buffer=src, src_rect=src_rect, dst_rect=dst_rect))

@pure
def blit_bilinear(src: PixelBuffer, src_rect: Rect | None, dst: PixelBuffer, dst_rect: Rect | None) -> PixelBuffer:
    """Blit and scale with bilinear filtering returning a new PixelBuffer.

    Args:
        src: Source PixelBuffer.
        src_rect: Bounding region of source to copy.
        dst: Destination PixelBuffer.
        dst_rect: Target scale bounding region on destination.

    Returns:
        A brand-new PixelBuffer with the scaled blit command enqueued.
    """
    from Effy.render.commands import BlitBilinearCmd
    return dst._append_command(BlitBilinearCmd(src_buffer=src, src_rect=src_rect, dst_rect=dst_rect))

__all__ = [
    "fill_rect", "draw_rect", "draw_line", "draw_circle", "fill_circle", "fill_triangle", "blit", "blit_blended", "blit_scaled", "blit_bilinear", "render_field",
    "RenderContext", "RendererFlags", "create_renderer", "render_clear", "render_set_draw_color", "render_fill_rect", "render_draw_rect", "render_present", "render_copy",
    "render_draw_line", "render_draw_circle", "render_fill_circle", "render_fill_triangle", "render_copy_blended", "render_copy_scaled", "render_copy_bilinear",
    "Texture"
]

