"""Blit and scaling demo: exercise all four software blitting modes.

This script opens a 640x480 window, creates a 64x64 colorful test pattern, and
blits it to the screen in four different quadrants using the four blit commands:
  - Top-Left: 1:1 Normal Blit (BlitCmd)
  - Top-Right: Nearest-Neighbor Scaled Blit (BlitScaledCmd)
  - Bottom-Left: Bilinear Filtered Scaled Blit (BlitBilinearCmd)
  - Bottom-Right: Alpha Blended Blit (BlitBlendedCmd) over a checkerboard pattern

Press Escape or close the window to quit.
"""

import os
import sys

# Ensure parent directory is in sys.path to find Effy package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.implementation.name != "pypy":
    print(
        "ERROR: Effy requires PyPy. Run with:\n"
        "  pypy3 demos/test_blit.py",
        file=sys.stderr,
    )
    sys.exit(1)

import time

from Effy.init import init, quit, InitFlag
from Effy.video.window import create_window, destroy_window, WindowFlags
from Effy.render.renderer import (
    create_renderer,
    render_clear,
    render_set_draw_color,
    render_present,
    render_fill_rect,
    render_draw_rect,
    RendererFlags,
    RenderContext,
)
from Effy.render import (
    fill_rect,
    draw_rect,
    draw_line,
    draw_circle,
    fill_circle,
)
from Effy.render.commands import (
    BlitCmd,
    BlitBlendedCmd,
    BlitScaledCmd,
    BlitBilinearCmd,
)
from Effy.video.rect import Rect, Point
from Effy.video.surface import PixelBuffer
from Effy.types import Color
from Effy.events import poll_event, QuitEvent, KeyDownEvent
from Effy._internal.result import Err

# Window Dimensions
_W = 640
_H = 480

# Keyboard keysyms
_ESCAPE_KEYSYM = 0xFF1B


def create_test_pattern() -> PixelBuffer:
    """Create a 64x64 PixelBuffer with a high-contrast, colorful test pattern.

    Returns:
        A PixelBuffer populated with shapes and alpha transparency.
    """
    buf = PixelBuffer.create(64, 64)

    # 1. Dark gray background
    buf = fill_rect(buf, None, Color(40, 40, 40, 255))

    # 2. Cyan border
    buf = draw_rect(buf, Rect(0, 0, 64, 64), Color(0, 255, 255, 255))

    # 3. Yellow circle in the center
    buf = fill_circle(buf, Point(32, 32), 20, Color(255, 255, 0, 255))

    # 4. Semi-transparent magenta square in the center
    buf = fill_rect(buf, Rect(22, 22, 20, 20), Color(255, 0, 255, 128))

    # 5. Red and blue diagonal cross lines
    buf = draw_line(buf, Point(0, 0), Point(64, 64), Color(255, 0, 0, 255))
    buf = draw_line(buf, Point(64, 0), Point(0, 64), Color(0, 0, 255, 255))

    return buf


def draw_scene(ctx: RenderContext, pattern: PixelBuffer) -> RenderContext:
    """Render all four blit modes in separate quadrants.

    Args:
        ctx: The current RenderContext.
        pattern: The 64x64 source test pattern.

    Returns:
        The updated RenderContext with enqueued draw and blit commands.
    """
    # 1. Clear with a very dark blue background
    ctx = render_set_draw_color(ctx, 15, 15, 25, 255)
    ctx = render_clear(ctx)

    # 2. Draw quadrant divider lines (gray)
    ctx = render_set_draw_color(ctx, 60, 60, 70, 255)
    ctx = render_fill_rect(ctx, Rect(318, 0, 4, _H))
    ctx = render_fill_rect(ctx, Rect(0, 238, _W, 4))

    # --- Quadrant 1: Top-Left (1:1 Normal Blit) ---
    q1_rect = Rect(128, 88, 64, 64)
    cmd1 = BlitCmd(src_buffer=pattern, src_rect=None, dst_rect=q1_rect)
    ctx = RenderContext(
        window_id=ctx.window_id,
        width=ctx.width,
        height=ctx.height,
        draw_color=ctx.draw_color,
        _commands=ctx._commands + (cmd1,),
    )

    # --- Quadrant 2: Top-Right (Nearest-Neighbor Scaled Blit) ---
    # Scale the 64x64 pattern to 192x192
    q2_rect = Rect(320 + 64, 24, 192, 192)
    cmd2 = BlitScaledCmd(src_buffer=pattern, src_rect=None, dst_rect=q2_rect)
    ctx = RenderContext(
        window_id=ctx.window_id,
        width=ctx.width,
        height=ctx.height,
        draw_color=ctx.draw_color,
        _commands=ctx._commands + (cmd2,),
    )

    # --- Quadrant 3: Bottom-Left (Bilinear Scaled Blit) ---
    # Scale the 64x64 pattern to 192x192 with bilinear filtering
    q3_rect = Rect(64, 240 + 24, 192, 192)
    cmd3 = BlitBilinearCmd(src_buffer=pattern, src_rect=None, dst_rect=q3_rect)
    ctx = RenderContext(
        window_id=ctx.window_id,
        width=ctx.width,
        height=ctx.height,
        draw_color=ctx.draw_color,
        _commands=ctx._commands + (cmd3,),
    )

    # --- Quadrant 4: Bottom-Right (Alpha Blended Blit) ---
    # Draw a checkerboard pattern background to showcase transparency blending
    bg_green = Color(0, 180, 80, 255)
    bg_orange = Color(240, 120, 20, 255)
    for y in range(240, 480, 48):
        for x in range(320, 640, 48):
            if ((x - 320) // 48 + (y - 240) // 48) % 2 == 0:
                ctx = render_set_draw_color(ctx, bg_green.r, bg_green.g, bg_green.b, bg_green.a)
            else:
                ctx = render_set_draw_color(ctx, bg_orange.r, bg_orange.g, bg_orange.b, bg_orange.a)
            ctx = render_fill_rect(ctx, Rect(x, y, 48, 48))

    # Center the 1:1 alpha-blended source in this quadrant over the checkerboard
    q4_rect = Rect(320 + 128, 240 + 88, 64, 64)
    cmd4 = BlitBlendedCmd(src_buffer=pattern, src_rect=None, dst_rect=q4_rect)
    ctx = RenderContext(
        window_id=ctx.window_id,
        width=ctx.width,
        height=ctx.height,
        draw_color=ctx.draw_color,
        _commands=ctx._commands + (cmd4,),
    )

    return ctx


def main() -> None:
    """Run the blitting and scaling demo event loop."""
    init_result = init(InitFlag.VIDEO).run()
    if isinstance(init_result, Err):
        print(f"Init failed: {init_result.error}", file=sys.stderr)
        return
    init_ctx = init_result.value

    win_result = create_window(
        "Effy — Blit & Scaling Test (Escape=quit)",
        100,
        100,
        _W,
        _H,
        WindowFlags.SHOWN,
    ).run()
    if isinstance(win_result, Err):
        print(f"Window creation failed: {win_result.error}", file=sys.stderr)
        quit(init_ctx).run()
        return
    window = win_result.value

    ctx_result = create_renderer(window, flags=RendererFlags.SOFTWARE).run()
    if isinstance(ctx_result, Err):
        print(f"Renderer creation failed: {ctx_result.error}", file=sys.stderr)
        destroy_window(window).run()
        quit(init_ctx).run()
        return
    ctx = ctx_result.value

    # Create the test pattern PixelBuffer once
    pattern = create_test_pattern()

    print("============================================================")
    print("              Effy Blit & Scaling Demo")
    print("============================================================")
    print("1. TOP-LEFT: 1:1 Normal Blit (BlitCmd)")
    print("2. TOP-RIGHT: Nearest-Neighbor Scaled Blit (BlitScaledCmd)")
    print("3. BOTTOM-LEFT: Bilinear Filtered Scaled Blit (BlitBilinearCmd)")
    print("4. BOTTOM-RIGHT: Alpha Blended Blit (BlitBlendedCmd) over checkerboard")
    print("Press Escape or close the window to quit.")
    print("============================================================")

    running = True
    while running:
        event = poll_event().run()
        while event is not None:
            if isinstance(event, QuitEvent):
                running = False
            elif isinstance(event, KeyDownEvent):
                if event.keycode == _ESCAPE_KEYSYM:
                    running = False
            event = poll_event().run()

        ctx = draw_scene(ctx, pattern)
        ctx = render_present(ctx).run()
        time.sleep(1 / 60)

    destroy_window(window).run()
    quit(init_ctx).run()


if __name__ == "__main__":
    main()
