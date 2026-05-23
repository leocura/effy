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
    from Effy.video.rect import Point
    from Effy.types import Color
    from Effy.render import fill_triangle

from runner import BenchmarkRunner

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    width, height = 1920, 1080
    
    random.seed(42)
    
    # Pre-generate triangle parameters to avoid overhead in timed loop
    raw_triangles = []
    for _ in range(500):
        p1 = (random.randint(0, width), random.randint(0, height))
        p2 = (random.randint(0, width), random.randint(0, height))
        p3 = (random.randint(0, width), random.randint(0, height))
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        raw_triangles.append((p1, p2, p3, color))

    if framework == "pygame":
        triangles = raw_triangles

        base_surface = pygame.Surface((width, height))

        def test_fill_triangles():
            surface = base_surface
            for p1, p2, p3, color in triangles:
                pygame.draw.polygon(surface, color, [p1, p2, p3])
    else:
        # Effy setup
        triangles = []
        for p1, p2, p3, color in raw_triangles:
            pt1 = Point(p1[0], p1[1])
            pt2 = Point(p2[0], p2[1])
            pt3 = Point(p3[0], p3[1])
            col = Color(color[0], color[1], color[2], 255)
            triangles.append((pt1, pt2, pt3, col))

        base_surface = PixelBuffer.create(width, height)

        def test_fill_triangles():
            surface = base_surface
            for p1, p2, p3, color in triangles:
                surface = fill_triangle(surface, p1, p2, p3, color)
            _ = surface._data

    runner.register("Fill Triangles", test_fill_triangles, iterations=50)
    runner.dump_json()

if __name__ == "__main__":
    main()
