import math
import sys
import time

from Effy.init import init
from Effy.init.flags import InitFlag
from Effy.video.window import create_window, destroy_window, WindowFlags
from Effy.render.renderer import (
    create_renderer,
    render_set_draw_color,
    render_clear,
    render_present,
    render_field,
)
from Effy.render.shader import (
    circle_field,
    rect_field,
    subtract_field,
    smooth_union_field,
)
from Effy.events import poll_event
from Effy.events.types import QuitEvent
from Effy.types import Color
from Effy._internal.result import Ok

def main() -> None:
    # Initialize video subsystem
    init_res = init(InitFlag.VIDEO).run()
    if not isinstance(init_res, Ok):
        print("Failed to initialize Effy:", init_res)
        return

    # Create window
    win_res = create_window(
        "Effy True SDF Rendering Demo", 100, 100, 640, 480, WindowFlags.SHOWN
    ).run()
    if not isinstance(win_res, Ok):
        print("Failed to create window:", win_res)
        return
    window = win_res.unwrap()

    # Create renderer
    ren_res = create_renderer(window).run()
    if not isinstance(ren_res, Ok):
        print("Failed to create renderer:", ren_res)
        return
    renderer = ren_res.unwrap()

    running = True
    start_time = time.time()

    while running:
        # Event pump
        event = poll_event().run()
        while event is not None:
            if isinstance(event, QuitEvent):
                running = False
            event = poll_event().run()

        # Calculate animation parameters
        t = time.time() - start_time
        
        # Center coordinates
        cx = 640 // 2
        cy = 480 // 2
        
        # Animated positions
        anim_x = int(math.sin(t * 2.0) * 100)
        anim_y = int(math.cos(t * 1.5) * 80)
        
        # 1. Base shape: A large rectangle with a circle subtracted from the middle
        base_rect = rect_field(cx - 150, cy - 100, 300, 200)
        hole = circle_field(cx, cy, 60)
        hollow_rect = subtract_field(base_rect, hole)
        
        # 2. Moving shape: An orbiting circle
        orbiter = circle_field(cx + anim_x, cy + anim_y, 40)
        
        # 3. Gooey Blend: Smooth union between the hollow rect and the orbiter
        # A smoothing factor of 30.0 gives a nice gooey/metaball effect
        final_sdf = smooth_union_field(hollow_rect, orbiter, 30.0)

        # Clear background
        renderer = render_set_draw_color(renderer, 30, 30, 40)
        renderer = render_clear(renderer)

        # Render the SDF field using the integrated deferred command
        # We use a nice electric blue color
        renderer = render_set_draw_color(renderer, 0, 200, 255, 255)
        renderer = render_field(renderer, None, final_sdf)

        # Present the frame
        renderer = render_present(renderer).run()

    destroy_window(window).run()

if __name__ == "__main__":
    main()
