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
    from Effy.video.rect import Rect, Point, intersect_rect, union_rect, point_in_rect, rect_empty

from runner import BenchmarkRunner

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    
    # 1. Pre-generate all random input coordinates and sizes outside the timed function loop
    random.seed(42)
    raw_rects = []
    for _ in range(1000):
        raw_rects.append((random.randint(0, 1000), random.randint(0, 1000), random.randint(1, 100), random.randint(1, 100)))
        
    raw_points = []
    for _ in range(1000):
        raw_points.append((random.randint(0, 1100), random.randint(0, 1100)))

    if framework == "pygame":
        # Pygame pre-allocated structures
        rects = [pygame.Rect(r[0], r[1], r[2], r[3]) for r in raw_rects]
        points = raw_points
        points_subset = points[:50] # 50 points per rect comparison

        def test_geometry_operations():
            # Perform operations
            # Intersection checks
            colliding = 0
            for i in range(len(rects) - 1):
                if rects[i].colliderect(rects[i+1]):
                    colliding += 1
                    
            # Unions
            unions = []
            for i in range(0, len(rects) - 1, 2):
                unions.append(rects[i].union(rects[i+1]))
                
            # Point in rect checks
            point_hits = 0
            for r in rects:
                for p in points_subset:
                    if r.collidepoint(p):
                        point_hits += 1
                        
            # Empty checks
            empty_count = 0
            for r in rects:
                if r.width <= 0 or r.height <= 0:
                    empty_count += 1
    else:
        # Effy pre-allocated structures
        rects = [Rect(r[0], r[1], r[2], r[3]) for r in raw_rects]
        points = [Point(p[0], p[1]) for p in raw_points]
        points_subset = points[:50] # 50 points per rect comparison

        def test_geometry_operations():
            # Perform operations
            # Intersection checks
            colliding = 0
            for i in range(len(rects) - 1):
                if intersect_rect(rects[i], rects[i+1]) is not None:
                    colliding += 1
                    
            # Unions
            unions = []
            for i in range(0, len(rects) - 1, 2):
                unions.append(union_rect(rects[i], rects[i+1]))
                
            # Point in rect checks
            point_hits = 0
            for r in rects:
                for p in points_subset:
                    if point_in_rect(p, r):
                        point_hits += 1
                        
            # Empty checks
            empty_count = 0
            for r in rects:
                if rect_empty(r):
                    empty_count += 1

    runner.register("Geometry Operations", test_geometry_operations, iterations=100)
    runner.dump_json()

if __name__ == "__main__":
    main()
