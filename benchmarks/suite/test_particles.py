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
    from Effy.render import fill_circle, fill_rect

from runner import BenchmarkRunner

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    width, height = 1920, 1080
    num_particles = 2000
    
    # 1. Pre-generate all particle setup data outside the timed loop to isolate simulation/rendering overhead
    random.seed(42)
    raw_particles = []
    for _ in range(num_particles):
        raw_particles.append({
            "x": random.uniform(0, width),
            "y": random.uniform(0, height),
            "vx": random.uniform(-5, 5),
            "vy": random.uniform(-5, 5),
            "color_rgb": (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        })

    if framework == "pygame":
        # Pre-initialize Pygame particle states
        particles = []
        for p in raw_particles:
            particles.append({
                "x": p["x"],
                "y": p["y"],
                "vx": p["vx"],
                "vy": p["vy"],
                "color": p["color_rgb"]
            })
            
        color_black = (0, 0, 0)

        base_surface = pygame.Surface((width, height))

        def test_particles_simulation():
            surface = base_surface
            surface.fill(color_black)
            
            for p in particles:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                
                # Bounce
                if p["x"] < 0 or p["x"] > width: p["vx"] *= -1
                if p["y"] < 0 or p["y"] > height: p["vy"] *= -1
                
                pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 3)

    else:
        # Pre-initialize Effy particle states
        particles = []
        for p in raw_particles:
            particles.append({
                "x": p["x"],
                "y": p["y"],
                "vx": p["vx"],
                "vy": p["vy"],
                "color": Color(p["color_rgb"][0], p["color_rgb"][1], p["color_rgb"][2], 255)
            })
            
        color_black = Color(0, 0, 0, 255)

        base_surface = PixelBuffer.create(width, height)

        def test_particles_simulation():
            surface = base_surface
            surface = fill_rect(surface, None, color_black)
            
            for p in particles:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                
                # Bounce
                if p["x"] < 0 or p["x"] > width: p["vx"] *= -1
                if p["y"] < 0 or p["y"] > height: p["vy"] *= -1
                
                surface = fill_circle(surface, Point(int(p["x"]), int(p["y"])), 3, p["color"])
            _ = surface._data

    runner.register("Particles Sim (2000)", test_particles_simulation, iterations=50)
    runner.dump_json()

if __name__ == "__main__":
    main()
