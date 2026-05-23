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
    from Effy.video.rect import Rect
    from Effy.types import Color
    from Effy.render import blit, blit_scaled, blit_bilinear, fill_rect

from runner import BenchmarkRunner

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    width, height = 1920, 1080
    
    random.seed(42)
    
    # 1. Pre-generate Blit Small destinations
    raw_dests_small = [(random.randint(0, width - 50), random.randint(0, height - 50), 50, 50) for _ in range(1000)]
    
    # 2. Pre-generate Blit Scaled destinations
    raw_dests_scaled = [(random.randint(0, width - 200), random.randint(0, height - 200), 200, 200) for _ in range(100)]
    
    # 3. Pre-generate Blit Bilinear destinations
    raw_dests_bilinear = [(random.randint(0, width - 200), random.randint(0, height - 200), 200, 200) for _ in range(50)]

    if framework == "pygame":
        # Pygame Setup
        dests_small = raw_dests_small
        dests_scaled = raw_dests_scaled
        dests_bilinear = raw_dests_bilinear
        
        # Pre-allocate source surfaces and colors to avoid doing so inside timed functions
        color_red = (255, 0, 0)
        color_green = (0, 255, 0)
        color_blue = (0, 0, 255)
        
        src_surf_small = pygame.Surface((50, 50))
        src_surf_small.fill(color_red)
        
        src_surf_scaled = pygame.Surface((100, 100))
        src_surf_scaled.fill(color_green)
        
        src_surf_bilinear = pygame.Surface((100, 100))
        src_surf_bilinear.fill(color_blue)

        base_surface = pygame.Surface((width, height))

        def test_blit_small():
            surface = base_surface
            for dst_rect in dests_small:
                surface.blit(src_surf_small, dst_rect)
                
        def test_blit_scaled():
            surface = base_surface
            for dst_rect in dests_scaled:
                # To scale and blit, we perform transform.scale and then blit
                scaled = pygame.transform.scale(src_surf_scaled, (200, 200))
                surface.blit(scaled, dst_rect)
                
        def test_blit_bilinear():
            surface = base_surface
            for dst_rect in dests_bilinear:
                scaled = pygame.transform.smoothscale(src_surf_bilinear, (200, 200))
                surface.blit(scaled, dst_rect)

    else:
        # Effy Setup
        dests_small = [Rect(r[0], r[1], r[2], r[3]) for r in raw_dests_small]
        dests_scaled = [Rect(r[0], r[1], r[2], r[3]) for r in raw_dests_scaled]
        dests_bilinear = [Rect(r[0], r[1], r[2], r[3]) for r in raw_dests_bilinear]
        
        src_rect_small = Rect(0, 0, 50, 50)
        src_rect_scaled = Rect(0, 0, 100, 100)
        src_rect_bilinear = Rect(0, 0, 100, 100)
        
        src_surf_small = PixelBuffer.create(50, 50)
        src_surf_small = fill_rect(src_surf_small, None, Color(255, 0, 0, 255))
        
        src_surf_scaled = PixelBuffer.create(100, 100)
        src_surf_scaled = fill_rect(src_surf_scaled, None, Color(0, 255, 0, 255))
        
        src_surf_bilinear = PixelBuffer.create(100, 100)
        src_surf_bilinear = fill_rect(src_surf_bilinear, None, Color(0, 0, 255, 255))

        base_surface = PixelBuffer.create(width, height)

        def test_blit_small():
            surface = base_surface
            for dst_rect in dests_small:
                surface = blit(src_surf_small, src_rect_small, surface, dst_rect)
            _ = surface._data
                
        def test_blit_scaled():
            surface = base_surface
            for dst_rect in dests_scaled:
                surface = blit_scaled(src_surf_scaled, src_rect_scaled, surface, dst_rect)
            _ = surface._data
                
        def test_blit_bilinear():
            surface = base_surface
            for dst_rect in dests_bilinear:
                surface = blit_bilinear(src_surf_bilinear, src_rect_bilinear, surface, dst_rect)
            _ = surface._data

    runner.register("Blit Small", test_blit_small, iterations=50)
    runner.register("Blit Scaled", test_blit_scaled, iterations=20)
    runner.register("Blit Bilinear", test_blit_bilinear, iterations=20)
    
    runner.dump_json()

if __name__ == "__main__":
    main()
