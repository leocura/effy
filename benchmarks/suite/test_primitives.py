import sys
import os
import random

def get_args():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "effy"

framework = get_args()

if framework == "pygame":
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    import pygame
    pygame.init()
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from Effy.video.surface import PixelBuffer
    from Effy.video.rect import Rect, Point
    from Effy.types import Color
    from Effy.render import fill_rect, draw_line, fill_circle, draw_rect

from runner import BenchmarkRunner

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    width, height = 1920, 1080
    
    # Pre-generate all random input data to eliminate random generation overhead during timing
    random.seed(42)
    
    # 1. Fill Rect Small inputs
    raw_rects_small = [(random.randint(0, width - 10), random.randint(0, height - 10), 10, 10) for _ in range(1000)]
    
    # 2. Fill Rect Large inputs
    raw_rects_large = [(random.randint(0, width - 500), random.randint(0, height - 500), 500, 500) for _ in range(10)]
    
    # 3. Draw Line inputs
    raw_lines = [((random.randint(0, width), random.randint(0, height)), 
                  (random.randint(0, width), random.randint(0, height))) for _ in range(1000)]
                  
    # 4. Fill Circle inputs
    raw_circles = [((random.randint(50, width - 50), random.randint(50, height - 50)), 20) for _ in range(500)]
    
    # 5. Draw Rect inputs
    raw_rects_draw = [(random.randint(0, width - 100), random.randint(0, height - 100), 100, 100) for _ in range(1000)]

    if framework == "pygame":
        # Convert pre-generated data into Pygame-specific objects/tuples
        rects_small = raw_rects_small
        rects_large = raw_rects_large
        lines = raw_lines
        circles = raw_circles
        rects_draw = raw_rects_draw
        color_red = (255, 0, 0)
        color_green = (0, 255, 0)
        color_blue = (0, 0, 255)
        color_yellow = (255, 255, 0)
        color_magenta = (255, 0, 255)

        base_surface = pygame.Surface((width, height))

        def test_fill_rect_small():
            surface = base_surface
            for rect in rects_small:
                surface.fill(color_red, rect=rect)
                
        def test_fill_rect_large():
            surface = base_surface
            for rect in rects_large:
                surface.fill(color_green, rect=rect)
                
        def test_draw_line():
            surface = base_surface
            for p1, p2 in lines:
                pygame.draw.line(surface, color_blue, p1, p2)
                
        def test_fill_circle():
            surface = base_surface
            for center, radius in circles:
                pygame.draw.circle(surface, color_yellow, center, radius)
                
        def test_draw_rect():
            surface = base_surface
            for rect in rects_draw:
                pygame.draw.rect(surface, color_magenta, rect, 1)

    else:
        # Convert pre-generated data into Effy objects
        rects_small = [Rect(r[0], r[1], r[2], r[3]) for r in raw_rects_small]
        rects_large = [Rect(r[0], r[1], r[2], r[3]) for r in raw_rects_large]
        lines = [(Point(l[0][0], l[0][1]), Point(l[1][0], l[1][1])) for l in raw_lines]
        circles = [(Point(c[0][0], c[0][1]), c[1]) for c in raw_circles]
        rects_draw = [Rect(r[0], r[1], r[2], r[3]) for r in raw_rects_draw]
        color_red = Color(255, 0, 0, 255)
        color_green = Color(0, 255, 0, 255)
        color_blue = Color(0, 0, 255, 255)
        color_yellow = Color(255, 255, 0, 255)
        color_magenta = Color(255, 0, 255, 255)

        base_surface = PixelBuffer.create(width, height)

        def test_fill_rect_small():
            surface = base_surface
            for rect in rects_small:
                surface = fill_rect(surface, rect, color_red)
            _ = surface._data
                
        def test_fill_rect_large():
            surface = base_surface
            for rect in rects_large:
                surface = fill_rect(surface, rect, color_green)
            _ = surface._data
                
        def test_draw_line():
            surface = base_surface
            for p1, p2 in lines:
                surface = draw_line(surface, p1, p2, color_blue)
            _ = surface._data
                
        def test_fill_circle():
            surface = base_surface
            for center, radius in circles:
                surface = fill_circle(surface, center, radius, color_yellow)
            _ = surface._data
                
        def test_draw_rect():
            surface = base_surface
            for rect in rects_draw:
                surface = draw_rect(surface, rect, color_magenta)
            _ = surface._data

    runner.register("Fill Rect Small", test_fill_rect_small, iterations=50)
    runner.register("Fill Rect Large", test_fill_rect_large, iterations=50)
    runner.register("Draw Line", test_draw_line, iterations=50)
    runner.register("Fill Circle", test_fill_circle, iterations=50)
    runner.register("Draw Rect", test_draw_rect, iterations=50)
    
    runner.dump_json()

if __name__ == "__main__":
    main()
