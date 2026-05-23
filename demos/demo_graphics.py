"""Graphics demo: visually exercise every software rasterizer primitive.

Press Space to cycle through scenes. Press Escape or close the window to quit.

Scenes (in order):
  1. Filled rectangle (red)
  2. Rectangle outline (cyan)
  3. Filled circle (green)
  4. Circle outline (yellow)
  5. Diagonal line (white)
  6. Filled triangle (magenta)
  7. Alpha-blended overlay (semi-transparent blue rect over scene 1)

Pass criteria: every primitive appears correctly shaped and colored.
"""

import os
import sys

# Ensure parent directory is in sys.path to find Effy package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.implementation.name != "pypy":
    print(
        "ERROR: Effy requires PyPy. Run with:\n"
        "  pypy3 demos/test_graphics.py",
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
    render_draw_line,
    render_draw_circle,
    render_fill_circle,
    render_fill_triangle,
    render_copy_blended,
    RendererFlags,
    RenderContext,
)
from Effy.render import fill_rect
from Effy.render.texture import Texture
from Effy.video.rect import Rect, Point
from Effy.video.surface import PixelBuffer
from Effy.types import Color, TextureID
from Effy.events import poll_event, QuitEvent, KeyDownEvent

# X11 Escape keysym
_ESCAPE_KEYSYM = 0xFF1B
# X11 Space keysym
_SPACE_KEYSYM = 0x0020

W, H = 640, 480
CENTER_X, CENTER_Y = W // 2, H // 2

SCENES = [
    "1/7  Filled rectangle (red)",
    "2/7  Rectangle outline (cyan)",
    "3/7  Filled circle (green)",
    "4/7  Circle outline (yellow)",
    "5/7  Diagonal line (white)",
    "6/7  Filled triangle (magenta)",
    "7/7  Alpha-blended overlay (blue, 50% opacity)",
]


def _draw_scene(ctx: RenderContext, scene_index: int) -> RenderContext:
    """Render the selected scene onto ctx and return the updated context.

    Args:
        ctx: The current RenderContext.
        scene_index: Index into SCENES selecting which primitive to draw.

    Returns:
        RenderContext with draw commands enqueued for the selected scene.
    """
    # Dark background
    ctx = render_set_draw_color(ctx, 20, 20, 30, 255)
    ctx = render_clear(ctx)

    if scene_index == 0:
        # Filled rectangle — red
        ctx = render_set_draw_color(ctx, 220, 50, 50, 255)
        ctx = render_fill_rect(ctx, Rect(160, 120, 320, 240))

    elif scene_index == 1:
        # Rectangle outline — cyan
        ctx = render_set_draw_color(ctx, 0, 220, 220, 255)
        ctx = render_draw_rect(ctx, Rect(160, 120, 320, 240))

    elif scene_index == 2:
        # Filled circle — green
        ctx = render_set_draw_color(ctx, 50, 200, 80, 255)
        ctx = render_fill_circle(ctx, Point(CENTER_X, CENTER_Y), 120)

    elif scene_index == 3:
        # Circle outline — yellow
        ctx = render_set_draw_color(ctx, 240, 220, 40, 255)
        ctx = render_draw_circle(ctx, Point(CENTER_X, CENTER_Y), 120)

    elif scene_index == 4:
        # Diagonal line — white
        ctx = render_set_draw_color(ctx, 255, 255, 255, 255)
        ctx = render_draw_line(ctx, Point(40, 40), Point(W - 40, H - 40))

    elif scene_index == 5:
        # Filled triangle — magenta
        ctx = render_set_draw_color(ctx, 220, 60, 220, 255)
        ctx = render_fill_triangle(ctx, Point(CENTER_X, 60), Point(80, H - 80), Point(W - 80, H - 80))

    elif scene_index == 6:
        # Base: filled red rect (scene 0)
        ctx = render_set_draw_color(ctx, 220, 50, 50, 255)
        ctx = render_fill_rect(ctx, Rect(160, 120, 320, 240))
        # Alpha overlay: semi-transparent blue
        overlay_buf = PixelBuffer.create(320, 240)
        overlay_buf = fill_rect(overlay_buf, None, Color(40, 80, 220, 128))
        tex = Texture(id=TextureID(1), width=320, height=240, buffer=overlay_buf)
        ctx = render_copy_blended(ctx, tex, None, Rect(160, 120, 320, 240))

    return ctx


def main() -> None:
    """Run the graphics demo event loop."""
    init_result = init(InitFlag.VIDEO).run()
    match init_result:
        case _ if hasattr(init_result, 'value') and hasattr(init_result, '__class__') and init_result.__class__.__name__ == 'Err':
            print(f"Init failed: {init_result.error}", file=sys.stderr)
            return
        case _:
            pass

    from Effy._internal.result import Ok, Err
    if isinstance(init_result, Err):
        print(f"Init failed: {init_result.error}", file=sys.stderr)
        return
    init_ctx = init_result.value

    win_result = create_window("Effy — Graphics Test (Space=next, Escape=quit)", 100, 100, W, H, WindowFlags.SHOWN).run()
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

    scene = 0
    print(f"Scene: {SCENES[scene]}")
    print("Press Space to advance, Escape to quit.")
    running = True

    while running:
        event = poll_event().run()
        while event is not None:
            if isinstance(event, QuitEvent):
                running = False
            elif isinstance(event, KeyDownEvent):
                if event.keycode == _ESCAPE_KEYSYM:
                    running = False
                elif event.keycode == _SPACE_KEYSYM:
                    scene = (scene + 1) % len(SCENES)
                    print(f"Scene: {SCENES[scene]}")
            event = poll_event().run()

        ctx = _draw_scene(ctx, scene)
        ctx = render_present(ctx).run()
        time.sleep(1 / 60)

    destroy_window(window).run()
    quit(init_ctx).run()


if __name__ == "__main__":
    main()
