"""Window management demo: exercises resize, move, minimize, maximize, and restore.

Press Space to advance through each operation in order.
Press Escape or close the window to quit.

Operation sequence:
  1. Resize   → 400 × 300
  2. Move     → position (300, 200)
  3. Minimize → iconify to taskbar
  4. Maximize → fill the screen
  5. Restore  → back to original size and position
"""

import os
import sys

# Ensure parent directory is in sys.path to find Effy package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.implementation.name != "pypy":
    print(
        "ERROR: Effy requires PyPy. Run with:\n"
        "  pypy3 demos/test_window.py",
        file=sys.stderr,
    )
    sys.exit(1)

import time

from Effy.init import init, quit, InitFlag
from Effy.video.window import (
    create_window,
    destroy_window,
    set_window_title,
    set_window_size,
    set_window_position,
    minimize_window,
    maximize_window,
    restore_window,
    WindowFlags,
)
from Effy.render.renderer import (
    create_renderer,
    render_clear,
    render_set_draw_color,
    render_present,
    RendererFlags,
)
from Effy.events import poll_event, QuitEvent, KeyDownEvent
from Effy._internal.result import Err

_ESCAPE_KEYSYM = 0xFF1B
_SPACE_KEYSYM  = 0x0020

# (label, background color) pairs for each step
_STEPS = [
    ("Step 1/5  Press Space → RESIZE to 400×300",    (60,  20,  80,  255)),
    ("Step 2/5  Press Space → MOVE to (300, 200)",   (20,  60,  80,  255)),
    ("Step 3/5  Press Space → MINIMIZE",              (80,  60,  20,  255)),
    ("Step 4/5  Press Space → MAXIMIZE",              (20,  80,  40,  255)),
    ("Step 5/5  Press Space → RESTORE",               (80,  30,  30,  255)),
    ("Done!     Press Escape to quit",                (30,  30,  30,  255)),
]


def main() -> None:
    """Run the window management demo event loop."""
    init_result = init(InitFlag.VIDEO).run()
    if isinstance(init_result, Err):
        print(f"Init failed: {init_result.error}", file=sys.stderr)
        return
    init_ctx = init_result.value

    win_result = create_window(
        _STEPS[0][0],
        100, 100, 640, 480,
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

    step = 0
    running = True

    print(_STEPS[step][0])
    print("Press Space to advance through window operations, Escape to quit.")

    while running:
        event = poll_event().run()
        while event is not None:
            if isinstance(event, QuitEvent):
                running = False

            elif isinstance(event, KeyDownEvent):
                if event.keycode == _ESCAPE_KEYSYM:
                    running = False

                elif event.keycode == _SPACE_KEYSYM and step < len(_STEPS) - 1:
                    step += 1
                    label = _STEPS[step][0]
                    print(label)
                    window = set_window_title(window, label).run()

                    if step == 1:
                        window = set_window_size(window, 400, 300).run()
                    elif step == 2:
                        window = set_window_position(window, 300, 200).run()
                    elif step == 3:
                        window = minimize_window(window).run()
                    elif step == 4:
                        window = maximize_window(window).run()
                    elif step == 5:
                        window = restore_window(window).run()

            event = poll_event().run()

        r, g, b, a = _STEPS[step][1]
        ctx = render_set_draw_color(ctx, r, g, b, a)
        ctx = render_clear(ctx)
        ctx = render_present(ctx).run()
        time.sleep(1 / 60)

    destroy_window(window).run()
    quit(init_ctx).run()


if __name__ == "__main__":
    main()
