"""Input demo: live keyboard and mouse tracking in a real window.

- Window title updates with the last key pressed (as a raw keysym hex value).
- A colored dot tracks the mouse cursor position.
- Dot color changes on left (red), middle (green), and right (blue) click.

Press Escape or close the window to quit.
"""

import os
import sys

# Ensure parent directory is in sys.path to find Effy package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.implementation.name != "pypy":
    print(
        "ERROR: Effy requires PyPy. Run with:\n"
        "  pypy3 demos/test_input.py",
        file=sys.stderr,
    )
    sys.exit(1)

import time

from Effy.init import init, quit, InitFlag
from Effy.video.window import create_window, destroy_window, set_window_title, WindowFlags
from Effy.render.renderer import (
    create_renderer,
    render_clear,
    render_set_draw_color,
    render_fill_rect,
    render_present,
    RenderContext,
    RendererFlags,
)
from Effy.render.commands import FillCircleCmd
from Effy.video.rect import Rect, Point
from Effy.types import Color
from Effy.events import poll_event, QuitEvent, KeyDownEvent, MouseMotionEvent
from Effy.events.types import MouseButton
from Effy._internal.result import Err

_ESCAPE_KEYSYM = 0xFF1B

# Dot colors per button held
_COLOR_DEFAULT = Color(255, 255, 255, 255)   # white — no button
_COLOR_LEFT    = Color(220, 60,  60,  255)   # red
_COLOR_MIDDLE  = Color(60,  200, 80,  255)   # green
_COLOR_RIGHT   = Color(60,  100, 220, 255)   # blue

DOT_RADIUS = 10
W, H = 640, 480


def _dot_color(buttons: MouseButton) -> Color:
    """Return the dot color based on which mouse button is held.

    Args:
        buttons: The currently held MouseButton flags.

    Returns:
        A Color for the cursor dot.
    """
    if buttons & MouseButton.LEFT:
        return _COLOR_LEFT
    if buttons & MouseButton.MIDDLE:
        return _COLOR_MIDDLE
    if buttons & MouseButton.RIGHT:
        return _COLOR_RIGHT
    return _COLOR_DEFAULT


def _render_frame(ctx: RenderContext, mx: int, my: int, dot_col: Color) -> RenderContext:
    """Draw the background and the cursor dot.

    Args:
        ctx: The active RenderContext.
        mx: Current mouse x position.
        my: Current mouse y position.
        dot_col: Color to use for the cursor dot.

    Returns:
        Updated RenderContext with commands enqueued.
    """
    ctx = render_set_draw_color(ctx, 15, 15, 25, 255)
    ctx = render_clear(ctx)

    # Crosshair guide lines
    ctx = render_set_draw_color(ctx, 40, 40, 55, 255)
    ctx = render_fill_rect(ctx, Rect(0, my - 1, W, 2))
    ctx = render_fill_rect(ctx, Rect(mx - 1, 0, 2, H))

    # Cursor dot
    cmd = FillCircleCmd(center=Point(mx, my), radius=DOT_RADIUS, color=dot_col)
    ctx = RenderContext(
        window_id=ctx.window_id,
        width=ctx.width,
        height=ctx.height,
        draw_color=ctx.draw_color,
        _commands=ctx._commands + (cmd,),
    )
    return ctx


def main() -> None:
    """Run the input-tracking demo event loop."""
    init_result = init(InitFlag.VIDEO).run()
    if isinstance(init_result, Err):
        print(f"Init failed: {init_result.error}", file=sys.stderr)
        return
    init_ctx = init_result.value

    win_result = create_window(
        "Effy — Input Test (move mouse, click, type keys | Escape=quit)",
        100, 100, W, H, WindowFlags.SHOWN,
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

    mx, my = W // 2, H // 2
    dot_col = _COLOR_DEFAULT
    running = True

    print("Move the mouse and press keys. Watch the window title and the dot.")

    while running:
        event = poll_event().run()
        while event is not None:
            if isinstance(event, QuitEvent):
                running = False

            elif isinstance(event, KeyDownEvent):
                if event.keycode == _ESCAPE_KEYSYM:
                    running = False
                else:
                    label = f"Effy — Last key: keysym=0x{event.keycode:04X}  scancode={event.scancode}"
                    window = set_window_title(window, label).run()
                    print(label)

            elif isinstance(event, MouseMotionEvent):
                mx = event.x
                my = event.y
                dot_col = _dot_color(event.buttons)

            event = poll_event().run()

        ctx = _render_frame(ctx, mx, my, dot_col)
        ctx = render_present(ctx).run()
        time.sleep(1 / 60)

    destroy_window(window).run()
    quit(init_ctx).run()


if __name__ == "__main__":
    main()
