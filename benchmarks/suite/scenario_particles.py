import sys
import os
import random
import math

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
    from Effy.init import init, quit, InitFlag
    from Effy.video.window import create_window, destroy_window, WindowFlags
    from Effy.render.renderer import create_renderer, render_clear, render_fill_rect, render_set_draw_color, render_present, RendererFlags
    from Effy.video.rect import Rect

from runner import BenchmarkRunner

NUM_PARTICLES = 2000
WIDTH, HEIGHT = 1280, 720
GRAVITY = 0.1

class ParticleSystem:
    def __init__(self):
        random.seed(42)
        # x, y, vx, vy, life, max_life
        self.particles = []
        for _ in range(NUM_PARTICLES):
            self.emit()

    def emit(self):
        x = WIDTH / 2
        y = HEIGHT / 2
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.0, 5.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        life = random.uniform(50, 200)
        self.particles.append([x, y, vx, vy, life, life])

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    
    if framework == "pygame":
        def setup():
            surface = pygame.Surface((WIDTH, HEIGHT))
            ps = ParticleSystem()
            return {"surface": surface, "ps": ps}
            
        def run(context):
            surface = context["surface"]
            ps = context["ps"]
            
            surface.fill((0, 0, 0))
            
            # Physics & Rendering
            i = 0
            while i < len(ps.particles):
                p = ps.particles[i]
                p[2] += 0 # wind?
                p[3] += GRAVITY
                p[0] += p[2]
                p[1] += p[3]
                p[4] -= 1
                
                if p[4] <= 0:
                    # Reset particle
                    p[0] = WIDTH / 2
                    p[1] = HEIGHT / 2
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(1.0, 5.0)
                    p[2] = math.cos(angle) * speed
                    p[3] = math.sin(angle) * speed
                    p[4] = random.uniform(50, 200)
                else:
                    # Draw
                    color_val = max(0, min(255, int((p[4] / p[5]) * 255)))
                    pygame.draw.rect(surface, (color_val, color_val, 255), (int(p[0]), int(p[1]), 2, 2))
                i += 1
                
        def teardown(context):
            pass
            
    else:
        def setup():
            init(InitFlag.VIDEO).run()
            win = create_window("Bench", 0, 0, WIDTH, HEIGHT, WindowFlags.HIDDEN).run().value
            rend = create_renderer(win, -1, RendererFlags.SOFTWARE).run().value
            ps = ParticleSystem()
            return {"rend": rend, "win": win, "ps": ps}
            
        def run(context):
            rend = context["rend"]
            ps = context["ps"]
            
            rend = render_set_draw_color(rend, 0, 0, 0, 255)
            rend = render_clear(rend)
            
            i = 0
            while i < len(ps.particles):
                p = ps.particles[i]
                p[3] += GRAVITY
                p[0] += p[2]
                p[1] += p[3]
                p[4] -= 1
                
                if p[4] <= 0:
                    p[0] = WIDTH / 2
                    p[1] = HEIGHT / 2
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(1.0, 5.0)
                    p[2] = math.cos(angle) * speed
                    p[3] = math.sin(angle) * speed
                    p[4] = random.uniform(50, 200)
                else:
                    color_val = max(0, min(255, int((p[4] / p[5]) * 255)))
                    rend = render_set_draw_color(rend, color_val, color_val, 255, 255)
                    rect = Rect(int(p[0]), int(p[1]), 2, 2)
                    rend = render_fill_rect(rend, rect)
                i += 1
                
            render_present(rend).run()
            context["rend"] = rend
            
        def teardown(context):
            destroy_window(context["win"]).run()

    runner.register("Particle System (2000 Particles)", run, setup_func=setup, teardown_func=teardown, iterations=600, warmup=100)
    runner.dump_json()

if __name__ == "__main__":
    main()
