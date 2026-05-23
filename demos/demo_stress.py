"""Real-World Load Stress Demo for Effy.

Simulates and renders:
  1. 800 gravity-affected bouncing particles (filled circles)
  2. 20 rotating bouncy filled triangles
  3. 30 bouncing rainbow outline circles

Controls:
  - Space: Trigger an explosion from the center of the screen
  - Escape or close window: Quit

Pass criteria: Smooth rendering with real-time FPS and frame time profiling in the window title.
"""

import os
import sys
import random
import time
import math

# Ensure parent directory is in sys.path to find Effy package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.implementation.name != "pypy":
    print(
        "WARNING: Effy software rasterization is highly optimized for PyPy JIT.\n"
        "For maximum performance, run this demo using PyPy3:\n"
        "  pypy3 demos/demo_stress.py\n",
        file=sys.stderr,
    )

from Effy.init import init, quit, InitFlag
from Effy.video.window import create_window, destroy_window, WindowFlags
from Effy.render.renderer import (
    create_renderer,
    render_clear,
    render_set_draw_color,
    render_present,
    RendererFlags,
    RenderContext,
)
from Effy.render.commands import FillCircleCmd, DrawCircleCmd, FillTriangleCmd, FillRectCmd, DrawRectCmd
from Effy.render.renderer import _append_command
from Effy.video.rect import Rect, Point
from Effy.types import Color
from Effy.events import poll_event, QuitEvent, KeyDownEvent
from Effy._internal.registry import get_platform_adapter, get_window_handle

# X11 Escape keysym
_ESCAPE_KEYSYM = 0xFF1B
# X11 Space keysym
_SPACE_KEYSYM = 0x0020

W, H = 800, 600
GRAVITY = 0.2
ELASTICITY = -0.85

def draw_fill_circle(ctx: RenderContext, center: Point, radius: int, color: Color) -> RenderContext:
    return _append_command(ctx, FillCircleCmd(center=center, radius=radius, color=color))

def draw_outline_circle(ctx: RenderContext, center: Point, radius: int, color: Color) -> RenderContext:
    return _append_command(ctx, DrawCircleCmd(center=center, radius=radius, color=color))

def draw_fill_triangle(ctx: RenderContext, p1: Point, p2: Point, p3: Point, color: Color) -> RenderContext:
    return _append_command(ctx, FillTriangleCmd(p1=p1, p2=p2, p3=p3, color=color))

FONT_3x5 = {
    '0': (0x7, 0x5, 0x5, 0x5, 0x7),
    '1': (0x2, 0x2, 0x2, 0x2, 0x2),
    '2': (0x7, 0x1, 0x7, 0x4, 0x7),
    '3': (0x7, 0x1, 0x7, 0x1, 0x7),
    '4': (0x5, 0x5, 0x7, 0x1, 0x1),
    '5': (0x7, 0x4, 0x7, 0x1, 0x7),
    '6': (0x7, 0x4, 0x7, 0x5, 0x7),
    '7': (0x7, 0x1, 0x1, 0x1, 0x1),
    '8': (0x7, 0x5, 0x7, 0x5, 0x7),
    '9': (0x7, 0x5, 0x7, 0x1, 0x7),
    ':': (0x0, 0x2, 0x0, 0x2, 0x0),
    '.': (0x0, 0x0, 0x0, 0x0, 0x2),
    ' ': (0x0, 0x0, 0x0, 0x0, 0x0),
    'A': (0x7, 0x5, 0x7, 0x5, 0x5),
    'E': (0x7, 0x4, 0x6, 0x4, 0x7),
    'F': (0x7, 0x4, 0x6, 0x4, 0x4),
    'G': (0x7, 0x4, 0x5, 0x5, 0x7),
    'H': (0x5, 0x5, 0x7, 0x5, 0x5),
    'I': (0x7, 0x2, 0x2, 0x2, 0x7),
    'M': (0x5, 0x7, 0x5, 0x5, 0x5),
    'N': (0x5, 0x7, 0x5, 0x5, 0x5),
    'P': (0x7, 0x5, 0x7, 0x4, 0x4),
    'R': (0x6, 0x5, 0x6, 0x5, 0x5),
    'S': (0x7, 0x4, 0x7, 0x1, 0x7),
    'T': (0x7, 0x2, 0x2, 0x2, 0x2),
}

def draw_text(ctx: RenderContext, text: str, x: int, y: int, scale: int, color: Color) -> RenderContext:
    from Effy.render.commands import FillRectCmd
    current_x = x
    for char in text.upper():
        glyph = FONT_3x5.get(char)
        if glyph is not None:
            for row_idx, row_val in enumerate(glyph):
                for col_idx in range(3):
                    bit = (row_val >> (2 - col_idx)) & 1
                    if bit:
                        px = current_x + col_idx * scale
                        py = y + row_idx * scale
                        rect = Rect(px, py, scale, scale)
                        ctx = _append_command(ctx, FillRectCmd(rect=rect, color=color))
        current_x += 4 * scale
    return ctx

def init_particles(num):
    particles = []
    for _ in range(num):
        particles.append({
            "x": W / 2,
            "y": H / 2,
            "vx": random.uniform(-6, 6),
            "vy": random.uniform(-10, -2),
            "radius": random.randint(3, 7),
            "color": Color(random.randint(100, 255), random.randint(100, 255), random.randint(150, 255), 255)
        })
    return particles

def main() -> None:
    # Set high-resolution timer on Windows to avoid time.sleep frame drops
    if sys.platform == "win32":
        import ctypes
        try:
            ctypes.windll.winmm.timeBeginPeriod(1)
        except Exception:
            pass
    # Initialize Effy
    init_result = init(InitFlag.VIDEO).run()
    from Effy._internal.result import Err
    if isinstance(init_result, Err):
        print(f"Init failed: {init_result.error}", file=sys.stderr)
        return
    init_ctx = init_result.value

    # Create window
    win_result = create_window(
        "Effy — Stress Demo [Initializing...]",
        100, 100, W, H, WindowFlags.SHOWN
    ).run()
    if isinstance(win_result, Err):
        print(f"Window creation failed: {win_result.error}", file=sys.stderr)
        quit(init_ctx).run()
        return
    window = win_result.value

    # Create software renderer
    ctx_result = create_renderer(window, flags=RendererFlags.SOFTWARE).run()
    if isinstance(ctx_result, Err):
        print(f"Renderer creation failed: {ctx_result.error}", file=sys.stderr)
        destroy_window(window).run()
        quit(init_ctx).run()
        return
    ctx = ctx_result.value

    # Setup stress workloads
    random.seed(42)
    
    # 1. Particles (filled circles under gravity)
    particles = init_particles(800)

    # 2. Bouncy Rotating Triangles
    triangles = []
    for _ in range(20):
        triangles.append({
            "x": random.uniform(50, W - 50),
            "y": random.uniform(50, H - 50),
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-3, 3),
            "size": random.uniform(15, 25),
            "angle": random.uniform(0, 2 * math.pi),
            "v_angle": random.uniform(-0.05, 0.05),
            "color": Color(random.randint(180, 255), random.randint(80, 180), random.randint(180, 255), 255)
        })

    # 3. Rainbow Outline Circles
    outline_circles = []
    for i in range(30):
        outline_circles.append({
            "x": random.uniform(100, W - 100),
            "y": random.uniform(100, H - 100),
            "vx": random.uniform(-2, 2),
            "vy": random.uniform(-2, 2),
            "radius": random.randint(15, 30),
            "hue_shift": random.uniform(0, 2 * math.pi)
        })

    # FPS & Frame Profiling
    frame_count = 0
    total_frames = 0
    current_fps = 60.0
    fps_timer = time.perf_counter()
    frame_start = time.perf_counter()
    
    running = True
    while running:
        # Event Polling
        event = poll_event().run()
        while event is not None:
            if isinstance(event, QuitEvent):
                running = False
            elif isinstance(event, KeyDownEvent):
                if event.keycode == _ESCAPE_KEYSYM:
                    running = False
                elif event.keycode == _SPACE_KEYSYM:
                    # Explode particles from current cursor or center
                    particles = init_particles(800)
            event = poll_event().run()

        # Update Physics
        # Particles
        for p in particles:
            p["vy"] += GRAVITY
            p["x"] += p["vx"]
            p["y"] += p["vy"]

            # Edge Bounces with friction & boundaries
            if p["x"] < p["radius"]:
                p["x"] = p["radius"]
                p["vx"] *= ELASTICITY
            elif p["x"] > W - p["radius"]:
                p["x"] = W - p["radius"]
                p["vx"] *= ELASTICITY

            if p["y"] < p["radius"]:
                p["y"] = p["radius"]
                p["vy"] *= ELASTICITY
            elif p["y"] > H - p["radius"]:
                p["y"] = H - p["radius"]
                p["vy"] *= ELASTICITY
                # Sideways friction on floor
                p["vx"] *= 0.98

        # Triangles
        for t in triangles:
            t["x"] += t["vx"]
            t["y"] += t["vy"]
            t["angle"] += t["v_angle"]

            if t["x"] < t["size"] or t["x"] > W - t["size"]:
                t["vx"] *= -1
            if t["y"] < t["size"] or t["y"] > H - t["size"]:
                t["vy"] *= -1

        # Outline Circles
        for c in outline_circles:
            c["x"] += c["vx"]
            c["y"] += c["vy"]
            c["hue_shift"] += 0.02

            if c["x"] < c["radius"] or c["x"] > W - c["radius"]:
                c["vx"] *= -1
            if c["y"] < c["radius"] or c["y"] > H - c["radius"]:
                c["vy"] *= -1

        # Drawing - Queue All commands
        # Dark spatial space background
        ctx = render_set_draw_color(ctx, 15, 12, 28, 255)
        ctx = render_clear(ctx)

        # Draw Outline Circles with procedural colors
        for idx, c in enumerate(outline_circles):
            # Rainbow cycling colors using sine waves
            r = int(127 + 127 * math.sin(c["hue_shift"]))
            g = int(127 + 127 * math.sin(c["hue_shift"] + 2.0))
            b = int(127 + 127 * math.sin(c["hue_shift"] + 4.0))
            color = Color(r, g, b, 255)
            ctx = draw_outline_circle(ctx, Point(int(c["x"]), int(c["y"])), c["radius"], color)

        # Draw Rotating Filled Triangles
        for t in triangles:
            # Rotate vertices using sine/cosine
            cos_a = math.cos(t["angle"])
            sin_a = math.sin(t["angle"])
            s = t["size"]

            # Compute rotated vertex relative offsets
            p1_x = int(t["x"] + s * cos_a)
            p1_y = int(t["y"] + s * sin_a)
            
            p2_x = int(t["x"] + s * math.cos(t["angle"] + 2.094)) # 120 deg
            p2_y = int(t["y"] + s * math.sin(t["angle"] + 2.094))
            
            p3_x = int(t["x"] + s * math.cos(t["angle"] + 4.188)) # 240 deg
            p3_y = int(t["y"] + s * math.sin(t["angle"] + 4.188))

            ctx = draw_fill_triangle(
                ctx,
                Point(p1_x, p1_y),
                Point(p2_x, p2_y),
                Point(p3_x, p3_y),
                t["color"]
            )

        # Draw Bouncy Gravity Particles
        for p in particles:
            ctx = draw_fill_circle(ctx, Point(int(p["x"]), int(p["y"])), p["radius"], p["color"])

        # Draw HUD Panel
        # Inner fill background
        ctx = _append_command(ctx, FillRectCmd(rect=Rect(16, 16, 218, 108), color=Color(10, 8, 20, 220)))
        # Neon-cyan outline border
        ctx = _append_command(ctx, DrawRectCmd(rect=Rect(15, 15, 220, 110), color=Color(0, 255, 255, 255)))
        # Text rendering
        ctx = draw_text(ctx, f"FPS: {current_fps:.1f}", 25, 25, 3, Color(0, 255, 255, 255))
        ctx = draw_text(ctx, f"THINGS: {len(particles) + len(triangles) + len(outline_circles)}", 25, 55, 3, Color(255, 255, 255, 255))
        ctx = draw_text(ctx, f"FRAME: {total_frames}", 25, 85, 3, Color(255, 255, 0, 255))

        # Flush Queue & Present Surface
        ctx = render_present(ctx).run()

        # Framerate Calculation
        frame_count += 1
        total_frames += 1
        now = time.perf_counter()
        
        # Calculate Title Stats every 30 frames
        if frame_count >= 30:
            elapsed = now - fps_timer
            fps = frame_count / elapsed
            current_fps = fps
            ms_per_frame = (elapsed / frame_count) * 1000
            
            # Update Window Title with Stats
            title = (
                f"Effy Stress Demo | 800 Particles, 20 Triangles, 30 Circles | "
                f"FPS: {fps:.1f} ({ms_per_frame:.2f} ms/frame)"
            )
            # Use platform adapter or cffi directly to set title if supported,
            # but updating the title via create_window is done once,
            # so we can just update the window title using standard C/SDL adapter functions.
            adapter = get_platform_adapter()
            if adapter:
                # Set window title directly using low-level window handle
                handle = get_window_handle(window)
                if handle:
                    # Under X11/Windows, we can update window title
                    try:
                        adapter.lib.SDL_SetWindowTitle(handle, title.encode("utf-8"))
                    except Exception:
                        pass
                        
            frame_count = 0
            fps_timer = now

        # Limit to target 60 FPS under normal execution
        target_time = 1.0 / 60.0
        while True:
            frame_end = time.perf_counter()
            frame_time = frame_end - frame_start
            if frame_time >= target_time:
                break
            remaining = target_time - frame_time
            if remaining > 0.0015:
                time.sleep(remaining - 0.001)
        frame_start = time.perf_counter()

    # Clean Up
    if sys.platform == "win32":
        try:
            ctypes.windll.winmm.timeEndPeriod(1)
        except Exception:
            pass
            
    destroy_window(window).run()
    quit(init_ctx).run()

if __name__ == "__main__":
    main()
