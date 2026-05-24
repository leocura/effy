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
    from Effy.init import init, quit, InitFlag
    from Effy.video.window import create_window, destroy_window, WindowFlags
    from Effy.render.renderer import create_renderer, render_clear, render_fill_rect, render_set_draw_color, render_present, RendererFlags
    from Effy.video.rect import Rect
    from Effy.types import Color

from runner import BenchmarkRunner

NUM_SPRITES = 1000
WIDTH, HEIGHT = 1280, 720

class GameState:
    def __init__(self):
        random.seed(42)
        self.sprites = []
        for _ in range(NUM_SPRITES):
            x = random.randint(0, WIDTH - 10)
            y = random.randint(0, HEIGHT - 10)
            vx = random.choice([-2, -1, 1, 2])
            vy = random.choice([-2, -1, 1, 2])
            self.sprites.append([x, y, vx, vy])

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    
    if framework == "pygame":
        def setup_game_loop():
            surface = pygame.Surface((WIDTH, HEIGHT))
            state = GameState()
            return {"surface": surface, "state": state}
            
        def run_game_loop(context):
            surface = context["surface"]
            state = context["state"]
            
            # Clear screen
            surface.fill((0, 0, 0))
            
            # Update and draw
            color = (0, 255, 0)
            for s in state.sprites:
                s[0] += s[2]
                s[1] += s[3]
                if s[0] <= 0 or s[0] >= WIDTH - 10: s[2] *= -1
                if s[1] <= 0 or s[1] >= HEIGHT - 10: s[3] *= -1
                
                pygame.draw.rect(surface, color, (s[0], s[1], 10, 10))
                
        def teardown_game_loop(context):
            pass
            
    else:
        def setup_game_loop():
            init(InitFlag.VIDEO).run()
            win = create_window("Bench", 0, 0, WIDTH, HEIGHT, WindowFlags.HIDDEN).run().value
            rend = create_renderer(win, -1, RendererFlags.SOFTWARE).run().value
            state = GameState()
            return {"rend": rend, "win": win, "state": state}
            
        def run_game_loop(context):
            rend = context["rend"]
            state = context["state"]
            
            # Clear screen
            rend = render_set_draw_color(rend, 0, 0, 0, 255)
            rend = render_clear(rend)
            
            # Update and draw
            rend = render_set_draw_color(rend, 0, 255, 0, 255)
            for s in state.sprites:
                s[0] += s[2]
                s[1] += s[3]
                if s[0] <= 0 or s[0] >= WIDTH - 10: s[2] *= -1
                if s[1] <= 0 or s[1] >= HEIGHT - 10: s[3] *= -1
                
                rect = Rect(s[0], s[1], 10, 10)
                rend = render_fill_rect(rend, rect)
                
            render_present(rend).run()
            context["rend"] = rend # Update rend context since it's immutable
            
        def teardown_game_loop(context):
            destroy_window(context["win"]).run()

    runner.register("Game Loop (1000 Sprites)", run_game_loop, setup_func=setup_game_loop, teardown_func=teardown_game_loop, iterations=600, warmup=100)
    runner.dump_json()

if __name__ == "__main__":
    main()
