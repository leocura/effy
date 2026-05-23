import time
from Effy.init import init, quit, InitFlag
from Effy.video.window import create_window, destroy_window, WindowFlags
from Effy.render.renderer import (
    create_renderer, render_clear, render_set_draw_color,
    render_present, RendererFlags, render_fill_polygon, render_draw_curve
)
from Effy.video.rect import Point
from Effy.events import poll_event, QuitEvent
from Effy._internal.result import Ok

def main() -> None:
    # 1. Initialize video system
    init_res = init(InitFlag.VIDEO).run()
    if not isinstance(init_res, Ok):
        print("Failed to initialize Effy")
        return
    init_ctx = init_res.value

    # 2. Open an OS window and spin up a software renderer
    win_res = create_window("Effy Polygon & Curve Demo", 100, 100, 800, 600, WindowFlags.SHOWN).run()
    if not isinstance(win_res, Ok):
        return
    window = win_res.value

    renderer_res = create_renderer(window, flags=RendererFlags.SOFTWARE).run()
    if not isinstance(renderer_res, Ok):
        return
    renderer = renderer_res.value

    running = True
    while running:
        # 3. Pull events
        event = poll_event().run()
        while event is not None:
            if isinstance(event, QuitEvent):
                running = False
            event = poll_event().run()

        # 4. Build render pass
        renderer = render_set_draw_color(renderer, 20, 20, 30)
        renderer = render_clear(renderer)
        
        # Self-intersecting pentagram polygon (tests non-zero winding fill)
        renderer = render_set_draw_color(renderer, 240, 200, 50)
        pentagram = (
            Point(200, 50), Point(300, 250), Point(50, 120), 
            Point(350, 120), Point(100, 250)
        )
        renderer = render_fill_polygon(renderer, pentagram)

        # Cubic Bezier curve
        renderer = render_set_draw_color(renderer, 50, 200, 240)
        curve = (Point(300, 100), Point(450, 20), Point(650, 300), Point(750, 100))
        renderer = render_draw_curve(renderer, curve)
        
        # Quadratic Bezier curve
        renderer = render_set_draw_color(renderer, 240, 50, 100)
        curve2 = (Point(300, 300), Point(500, 600), Point(750, 300))
        renderer = render_draw_curve(renderer, curve2)

        # 5. Rasterize and display
        renderer = render_present(renderer).run()
        time.sleep(1 / 60)

    # 6. Clean up
    destroy_window(window).run()
    quit(init_ctx).run()

if __name__ == "__main__":
    main()
