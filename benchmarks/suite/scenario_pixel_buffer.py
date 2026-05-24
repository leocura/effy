import sys
import os
import array
import ctypes
import os
import array

def get_args():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "effy"

framework = get_args()

WIDTH, HEIGHT = 1280, 720

if framework == "pygame":
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    import pygame
    pygame.init()
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from Effy.init import init, quit, InitFlag
    from Effy.video.window import create_window, destroy_window, WindowFlags
    from Effy.render.renderer import create_renderer, render_clear, render_present, RendererFlags, render_copy_scaled
    from Effy.video.surface import PixelBuffer
    from Effy.render.texture import create_texture_from_surface
    from Effy.video.rect import Rect
    from Effy.types import Color

from runner import BenchmarkRunner

class AnimState:
    def __init__(self):
        self.frame = 0

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    
    if framework == "pygame":
        def setup():
            surface = pygame.Surface((WIDTH, HEIGHT))
            state = AnimState()
            return {"surface": surface, "state": state}
            
        def run(context):
            surface = context["surface"]
            state = context["state"]
            frame = state.frame
            
            # Use PixelArray for software pixel manipulation
            pxarray = pygame.PixelArray(surface)
            for y in range(HEIGHT):
                row_offset = (y + frame) & 255
                for x in range(WIDTH):
                    col_offset = (x + frame) & 255
                    pxarray[x, y] = (row_offset, col_offset, 128)
            pxarray.close()
            
            state.frame += 1
            
        def teardown(context):
            pass
            
    else:
        def setup():
            init(InitFlag.VIDEO).run()
            win = create_window("Bench", 0, 0, WIDTH, HEIGHT, WindowFlags.HIDDEN).run().value
            rend = create_renderer(win, -1, RendererFlags.SOFTWARE).run().value
            pb = PixelBuffer.create(WIDTH, HEIGHT)
            state = AnimState()
            return {"rend": rend, "win": win, "pb": pb, "state": state}
            
        def run(context):
            pb = context["pb"]
            state = context["state"]
            frame = state.frame
            
            # Pure software pixel math iteration
            data = pb._data_cache[0]
            w = WIDTH
            h = HEIGHT
            
            row_lut = [(y + frame) & 255 for y in range(h)]
            col_lut = [((x + frame) & 255) << 8 for x in range(w)]
            base_color = 0xFF000000 | (128 << 16)
            
            idx = 0
            for y in range(h):
                r_color = base_color | row_lut[y]
                for x in range(w):
                    data[idx] = r_color | col_lut[x]
                    idx += 1
            
            # Notice: We intentionally do NOT create_texture_from_surface or present
            # here, because we are strictly benchmarking CPU pixel iteration throughput!
            
            state.frame += 1
            
        def teardown(context):
            destroy_window(context["win"]).run()

    runner.register("Pixel Buffer (1280x720)", run, setup_func=setup, teardown_func=teardown, iterations=10, warmup=2)
    runner.dump_json()

if __name__ == "__main__":
    main()
