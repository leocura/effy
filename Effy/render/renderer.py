"""Deferred rendering pipeline for Effy.

RenderContext accumulates drawing commands as an immutable tuple of frozen
DrawCmd objects. No pixel data is allocated or copied during draw calls. The
entire queue is rasterized in a single pass inside render_present, yielding
one CFFI allocation per frame regardless of how many drawing primitives were
issued.
"""

from __future__ import annotations
import array
from dataclasses import dataclass, field
from enum import IntFlag
from typing import Any, Callable
from Effy.types import WindowID, Effect, Result, Ok, Err, Color
from Effy.video.surface import PixelBuffer
from Effy.video.window import Window
from Effy.video.rect import Rect, Point
from Effy.error import EffyError
from Effy._internal.registry import get_platform_adapter, get_window_handle
from Effy._internal.fp import pure
from Effy.render.commands import (
    DrawCmd,
    FillRectCmd, DrawRectCmd, DrawLineCmd,
    DrawCircleCmd, FillCircleCmd, FillTriangleCmd,
    BlitCmd, BlitBlendedCmd, BlitScaledCmd, BlitBilinearCmd,
    RenderFieldCmd, Field,
)
from Effy.render import rasterizer
from Effy.render.texture import Texture


class RendererFlags(IntFlag):
    """Flags specifying hardware or software renderer features."""
    SOFTWARE = 0x00000001
    ACCELERATED = 0x00000002
    PRESENTVSYNC = 0x00000004
    TARGETTEXTURE = 0x00000008


@dataclass(frozen=True, slots=True)
class RenderContext:
    """An immutable rendering context that accumulates drawing commands.

    Drawing calls append O(1) frozen command objects to _commands. No pixel
    buffer is allocated until render_present flushes the queue.

    Attributes:
        window_id: The ID of the window associated with this renderer.
        width: Width of the render target in pixels.
        height: Height of the render target in pixels.
        draw_color: The current active draw Color for shape fills and strokes.
        _commands: List of deferred DrawCmd objects.
    """
    window_id: WindowID
    width: int
    height: int
    draw_color: Color = Color(0, 0, 0, 255)
    _commands: list[DrawCmd] = field(default_factory=list)
    _is_transient: bool = False
    flags: RendererFlags = RendererFlags.SOFTWARE



def _dispatch_blit(cmd: BlitCmd, data: array.array[int], w: int, h: int, pitch: int) -> None:
    """Dispatch blit draw command to the software rasterizer."""
    src = cmd.src_buffer
    rasterizer.rasterize_blit(src._data, src.width, src.height, src.pitch, cmd.src_rect, data, w, h, pitch, cmd.dst_rect)

def _dispatch_blit_blended(cmd: BlitBlendedCmd, data: array.array[int], w: int, h: int, pitch: int) -> None:
    """Dispatch alpha-blended blit draw command to the software rasterizer."""
    src = cmd.src_buffer
    rasterizer.rasterize_blit_blended(src._data, src.width, src.height, src.pitch, cmd.src_rect, data, w, h, pitch, cmd.dst_rect)

def _dispatch_blit_scaled(cmd: BlitScaledCmd, data: array.array[int], w: int, h: int, pitch: int) -> None:
    """Dispatch nearest-neighbor scaled blit draw command to the software rasterizer."""
    src = cmd.src_buffer
    rasterizer.rasterize_blit_scaled(src._data, src.width, src.height, src.pitch, cmd.src_rect, data, w, h, pitch, cmd.dst_rect)

def _dispatch_blit_bilinear(cmd: BlitBilinearCmd, data: array.array[int], w: int, h: int, pitch: int) -> None:
    """Dispatch bilinear-filtered scaled blit draw command to the software rasterizer."""
    src = cmd.src_buffer
    rasterizer.rasterize_blit_bilinear(src._data, src.width, src.height, src.pitch, cmd.src_rect, data, w, h, pitch, cmd.dst_rect)

def _dispatch_fill_rect(cmd: FillRectCmd, data: array.array[int], w: int, h: int, pitch: int) -> None:
    """Dispatch fill rectangle draw command to the software rasterizer."""
    rasterizer.rasterize_fill_rect(data, w, h, pitch, cmd.rect, cmd.color)

def _dispatch_draw_line(cmd: DrawLineCmd, data: array.array[int], w: int, h: int, pitch: int) -> None:
    """Dispatch draw line draw command to the software rasterizer."""
    rasterizer.rasterize_draw_line(data, w, h, pitch, cmd.p1, cmd.p2, cmd.color)

def _dispatch_draw_rect(cmd: DrawRectCmd, data: array.array[int], w: int, h: int, pitch: int) -> None:
    """Dispatch stroke rectangle outline draw command to the software rasterizer."""
    rasterizer.rasterize_draw_rect(data, w, h, pitch, cmd.rect, cmd.color)

def _dispatch_draw_circle(cmd: DrawCircleCmd, data: array.array[int], w: int, h: int, pitch: int) -> None:
    """Dispatch stroke circle outline draw command to the software rasterizer."""
    rasterizer.rasterize_draw_circle(data, w, h, pitch, cmd.center, cmd.radius, cmd.color)

def _dispatch_fill_circle(cmd: FillCircleCmd, data: array.array[int], w: int, h: int, pitch: int) -> None:
    """Dispatch fill circle draw command to the software rasterizer."""
    rasterizer.rasterize_fill_circle(data, w, h, pitch, cmd.center, cmd.radius, cmd.color)

def _dispatch_fill_triangle(cmd: FillTriangleCmd, data: array.array[int], w: int, h: int, pitch: int) -> None:
    """Dispatch fill triangle draw command to the software rasterizer."""
    rasterizer.rasterize_fill_triangle(data, w, h, pitch, cmd.p1, cmd.p2, cmd.p3, cmd.color)

def _dispatch_render_field(cmd: RenderFieldCmd, data: array.array[int], w: int, h: int, pitch: int) -> None:
    """Dispatch signed distance field rendering draw command to the software rasterizer."""
    rasterizer.rasterize_field(data, w, h, pitch, cmd.rect, cmd.field, cmd.color)


_DISPATCH_TABLE: dict[type[DrawCmd], Callable[[Any, array.array[int], int, int, int], None]] = {
    BlitCmd: _dispatch_blit,
    BlitBlendedCmd: _dispatch_blit_blended,
    BlitScaledCmd: _dispatch_blit_scaled,
    BlitBilinearCmd: _dispatch_blit_bilinear,
    FillRectCmd: _dispatch_fill_rect,
    DrawLineCmd: _dispatch_draw_line,
    DrawRectCmd: _dispatch_draw_rect,
    DrawCircleCmd: _dispatch_draw_circle,
    FillCircleCmd: _dispatch_fill_circle,
    FillTriangleCmd: _dispatch_fill_triangle,
    RenderFieldCmd: _dispatch_render_field,
}


def _resolve_commands(buffer: PixelBuffer, data: array.array[int], commands: list[DrawCmd]) -> None:
    """Rasterize all queued DrawCmd objects into an array.array[int] in a single pass.

    Args:
        buffer: A PixelBuffer to provide dimensions.
        data: The destination array.array[int] to render into.
        commands: The list of DrawCmd objects to execute in order.
    """
    w, h, pitch = buffer.width, buffer.height, buffer.pitch
    dispatch = _DISPATCH_TABLE

    for cmd in commands:
        handler = dispatch.get(type(cmd))
        if handler:
            handler(cmd, data, w, h, pitch)


def _append_command(ctx: RenderContext, cmd: DrawCmd) -> RenderContext:
    """Helper to append a command, optimizing for transience."""
    if ctx._is_transient:
        ctx._commands.append(cmd)
        return ctx
    else:
        new_commands = list(ctx._commands)
        new_commands.append(cmd)
        return RenderContext(
            window_id=ctx.window_id,
            width=ctx.width,
            height=ctx.height,
            draw_color=ctx.draw_color,
            _commands=new_commands,
            _is_transient=True,
            flags=ctx.flags
        )


def create_renderer(
    window: Window,
    index: int = -1,
    flags: RendererFlags = RendererFlags.SOFTWARE,
) -> Effect[Result[RenderContext, EffyError]]:
    """Create a new rendering context for a given window.

    Args:
        window: The target Window context to render into.
        index: The index of the rendering driver to initialize, or -1.
        flags: The configuration flags for the renderer.

    Returns:
        An Effect wrapping a Result that contains either the RenderContext or an EffyError.
    """
    def _run() -> Result[RenderContext, EffyError]:
        """Thunk implementing platform rendering context creation logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return Err(EffyError(code=-1, message="SDL not initialized"))
        return Ok(RenderContext(
            window_id=window.id,
            width=window.w,
            height=window.h,
            draw_color=Color(0, 0, 0, 255),
            _commands=[],
            flags=flags
        ))

    return Effect(_run)


@pure
def render_clear(ctx: RenderContext) -> RenderContext:
    """Reset the command queue and enqueue a full-surface clear with the draw color.

    Args:
        ctx: The active RenderContext.

    Returns:
        A new RenderContext with a fresh command queue containing only the clear command.
    """
    return RenderContext(
        window_id=ctx.window_id,
        width=ctx.width,
        height=ctx.height,
        draw_color=ctx.draw_color,
        _commands=[FillRectCmd(rect=None, color=ctx.draw_color)],
        _is_transient=False,
        flags=ctx.flags
    )


@pure
def render_set_draw_color(ctx: RenderContext, r: int, g: int, b: int, a: int = 255) -> RenderContext:
    """Set the active drawing color for subsequent draw commands.

    Args:
        ctx: The active RenderContext to evolve.
        r: Red component (0-255).
        g: Green component (0-255).
        b: Blue component (0-255).
        a: Alpha transparency component (0-255). Defaults to 255.

    Returns:
        A new RenderContext containing the updated draw color.
    """
    return RenderContext(
        window_id=ctx.window_id,
        width=ctx.width,
        height=ctx.height,
        draw_color=Color(r, g, b, a),
        _commands=ctx._commands,
        _is_transient=ctx._is_transient,
        flags=ctx.flags
    )



@pure
def render_fill_rect(ctx: RenderContext, rect: Rect) -> RenderContext:
    """Enqueue a filled rectangle draw command.

    Args:
        ctx: The active RenderContext.
        rect: The Rect bounding the region to fill.

    Returns:
        A new RenderContext with FillRectCmd appended to the queue.
    """
    cmd = FillRectCmd(rect=rect, color=ctx.draw_color)
    return _append_command(ctx, cmd)


@pure
def render_draw_rect(ctx: RenderContext, rect: Rect) -> RenderContext:
    """Enqueue a rectangle outline draw command.

    Args:
        ctx: The active RenderContext.
        rect: The Rect bounding the region to stroke.

    Returns:
        A new RenderContext with DrawRectCmd appended to the queue.
    """
    cmd = DrawRectCmd(rect=rect, color=ctx.draw_color)
    return _append_command(ctx, cmd)


@pure
def render_copy(ctx: RenderContext, tex: Texture, src: Rect | None, dst: Rect | None) -> RenderContext:
    """Enqueue a blit command to copy a texture region onto the render target.

    Args:
        ctx: The active RenderContext.
        tex: The Texture to copy from.
        src: The rectangular source region of the texture, or None for the full texture.
        dst: The target rectangular destination within the buffer, or None for full fit.

    Returns:
        A new RenderContext with BlitCmd appended to the queue.
    """
    cmd = BlitCmd(src_buffer=tex.buffer, src_rect=src, dst_rect=dst)
    return _append_command(ctx, cmd)


@pure
def render_field(ctx: RenderContext, rect: Rect | None, field: Field) -> RenderContext:
    """Enqueue a signed distance field draw command.

    Args:
        ctx: The active RenderContext.
        rect: The Rect bounding the region to render, or None for the full surface.
        field: The Field function returning exact signed distance.

    Returns:
        A new RenderContext with RenderFieldCmd appended to the queue.
    """
    cmd = RenderFieldCmd(rect=rect, field=field, color=ctx.draw_color)
    return _append_command(ctx, cmd)


def render_present(ctx: RenderContext) -> Effect[RenderContext]:
    """Flush the command queue, rasterize all commands, and present to the window.

    This is the sole point of pixel buffer allocation per frame. All deferred
    draw commands are executed in a single rasterization pass here.

    Args:
        ctx: The active RenderContext containing the accumulated command queue.

    Returns:
        An Effect yielding a new RenderContext with an empty command queue,
        ready for the next frame.
    """
    def _run() -> RenderContext:
        """Thunk implementing platform rendering pipeline resolution and presentation logic."""
        adapter = get_platform_adapter()
        handle = get_window_handle(ctx.window_id)

        success = False
        if adapter and handle and (ctx.flags & RendererFlags.ACCELERATED):
            if hasattr(adapter, "present_accelerated"):
                res = adapter.present_accelerated(handle, ctx._commands, ctx.width, ctx.height)
                if isinstance(res, Ok):
                    success = True

        if not success:
            from Effy._internal.pool import pixel_buffer_pool
            data = pixel_buffer_pool.get(ctx.width, ctx.height, zero=False)
            
            buffer = PixelBuffer(
                width=ctx.width,
                height=ctx.height,
                pitch=ctx.width,
                _data_cache=[data],
                _commands_list=[],
                _is_transient=True
            )
            
            _resolve_commands(buffer, data, ctx._commands)

            if adapter and handle:
                adapter.flip_buffer(handle, buffer)

            pixel_buffer_pool.put(ctx.width, ctx.height, data)

        return RenderContext(
            window_id=ctx.window_id,
            width=ctx.width,
            height=ctx.height,
            draw_color=ctx.draw_color,
            _commands=[],
            _is_transient=False,
            flags=ctx.flags
        )

    return Effect(_run)



@pure
def render_draw_line(ctx: RenderContext, p1: Point, p2: Point) -> RenderContext:
    """Enqueue a line drawing command from p1 to p2.

    Args:
        ctx: The active RenderContext.
        p1: The start Point of the line.
        p2: The end Point of the line.

    Returns:
        A new RenderContext with DrawLineCmd appended to the queue.
    """
    cmd = DrawLineCmd(p1=p1, p2=p2, color=ctx.draw_color)
    return _append_command(ctx, cmd)


@pure
def render_draw_circle(ctx: RenderContext, center: Point, radius: int) -> RenderContext:
    """Enqueue a circle outline drawing command.

    Args:
        ctx: The active RenderContext.
        center: The Point representing the circle center.
        radius: The radius of the circle.

    Returns:
        A new RenderContext with DrawCircleCmd appended to the queue.
    """
    cmd = DrawCircleCmd(center=center, radius=radius, color=ctx.draw_color)
    return _append_command(ctx, cmd)


@pure
def render_fill_circle(ctx: RenderContext, center: Point, radius: int) -> RenderContext:
    """Enqueue a filled circle drawing command.

    Args:
        ctx: The active RenderContext.
        center: The Point representing the circle center.
        radius: The radius of the circle.

    Returns:
        A new RenderContext with FillCircleCmd appended to the queue.
    """
    cmd = FillCircleCmd(center=center, radius=radius, color=ctx.draw_color)
    return _append_command(ctx, cmd)


@pure
def render_fill_triangle(ctx: RenderContext, p1: Point, p2: Point, p3: Point) -> RenderContext:
    """Enqueue a filled triangle drawing command.

    Args:
        ctx: The active RenderContext.
        p1: The first vertex Point.
        p2: The second vertex Point.
        p3: The third vertex Point.

    Returns:
        A new RenderContext with FillTriangleCmd appended to the queue.
    """
    cmd = FillTriangleCmd(p1=p1, p2=p2, p3=p3, color=ctx.draw_color)
    return _append_command(ctx, cmd)


@pure
def render_copy_blended(ctx: RenderContext, tex: Texture, src: Rect | None, dst: Rect | None) -> RenderContext:
    """Enqueue a blended blit command to copy a texture region onto the render target with alpha blending.

    Args:
        ctx: The active RenderContext.
        tex: The Texture to copy from.
        src: The rectangular source region of the texture, or None for the full texture.
        dst: The target rectangular destination within the buffer, or None for full fit.

    Returns:
        A new RenderContext with BlitBlendedCmd appended to the queue.
    """
    cmd = BlitBlendedCmd(src_buffer=tex.buffer, src_rect=src, dst_rect=dst)
    return _append_command(ctx, cmd)


@pure
def render_copy_scaled(ctx: RenderContext, tex: Texture, src: Rect | None, dst: Rect | None) -> RenderContext:
    """Enqueue a scaled blit command to copy a texture region onto the render target with nearest-neighbor scaling.

    Args:
        ctx: The active RenderContext.
        tex: The Texture to copy from.
        src: The rectangular source region of the texture, or None for the full texture.
        dst: The target rectangular destination within the buffer, or None for full fit.

    Returns:
        A new RenderContext with BlitScaledCmd appended to the queue.
    """
    cmd = BlitScaledCmd(src_buffer=tex.buffer, src_rect=src, dst_rect=dst)
    return _append_command(ctx, cmd)


@pure
def render_copy_bilinear(ctx: RenderContext, tex: Texture, src: Rect | None, dst: Rect | None) -> RenderContext:
    """Enqueue a bilinear-filtered scaled blit command to copy a texture region onto the render target.

    Args:
        ctx: The active RenderContext.
        tex: The Texture to copy from.
        src: The rectangular source region of the texture, or None for the full texture.
        dst: The target rectangular destination within the buffer, or None for full fit.

    Returns:
        A new RenderContext with BlitBilinearCmd appended to the queue.
    """
    cmd = BlitBilinearCmd(src_buffer=tex.buffer, src_rect=src, dst_rect=dst)
    return _append_command(ctx, cmd)

