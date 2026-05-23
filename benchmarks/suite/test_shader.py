import sys
import os
import math

def get_args():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "effy"

framework = get_args()

# Custom classes matching Effy's Field implementations to make Pygame branch fully functional and identical
class CircleField:
    __slots__ = ("cx", "cy", "r")
    def __init__(self, cx: int, cy: int, r: int):
        self.cx = cx
        self.cy = cy
        self.r = r
        
    def __call__(self, x: int, y: int) -> float:
        dx = x - self.cx
        dy = y - self.cy
        return math.sqrt(dx * dx + dy * dy) - self.r

class RectField:
    __slots__ = ("cx", "cy", "half_w", "half_h")
    def __init__(self, rx: int, ry: int, rw: int, rh: int):
        self.cx = rx + rw / 2.0
        self.cy = ry + rh / 2.0
        self.half_w = rw / 2.0
        self.half_h = rh / 2.0
        
    def __call__(self, x: int, y: int) -> float:
        dx = abs(x - self.cx) - self.half_w
        dy = abs(y - self.cy) - self.half_h
        
        dx_out = dx if dx > 0.0 else 0.0
        dy_out = dy if dy > 0.0 else 0.0
        dist_outside = math.sqrt(dx_out * dx_out + dy_out * dy_out)
        
        max_dxy = dx if dx > dy else dy
        dist_inside = max_dxy if max_dxy < 0.0 else 0.0
        
        return dist_outside + dist_inside

class UnionField:
    __slots__ = ("fields",)
    def __init__(self, f1, f2):
        self.fields = []
        try:
            is_f1_inf = (f1(0, 0) == float('inf'))
        except Exception:
            is_f1_inf = False
            
        try:
            is_f2_inf = (f2(0, 0) == float('inf'))
        except Exception:
            is_f2_inf = False
            
        if not is_f1_inf:
            if isinstance(f1, UnionField):
                self.fields.extend(f1.fields)
            else:
                self.fields.append(f1)
                
        if not is_f2_inf:
            if isinstance(f2, UnionField):
                self.fields.extend(f2.fields)
            else:
                self.fields.append(f2)
                
        if not self.fields:
            self.fields.append(f1)

    def __call__(self, x: int, y: int) -> float:
        m = self.fields[0](x, y)
        for f in self.fields[1:]:
            val = f(x, y)
            if val < m:
                m = val
        return m

if framework == "pygame":
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    import pygame
    pygame.init()
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from Effy.video.surface import PixelBuffer
    from Effy.types import Color
    from Effy.render.shader import circle_field, rect_field, union_field, render_field

from runner import BenchmarkRunner

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    width, height = 500, 500
    
    # Pre-generate the shared field tree
    composed_field = lambda x, y: float('inf')
    
    # 18 shapes total
    for i in range(50, 450, 50):
        c = CircleField(i, i, 30)
        composed_field = UnionField(composed_field, c)
        
    for i in range(10, 400, 40):
        r = RectField(i, i, 20, 20)
        composed_field = UnionField(composed_field, r)

    if framework == "pygame":
        # Procedural custom pixel shader loop in Pygame matching the exact mathematical rasterizer in Effy
        color_blue = (0, 0, 255)
        sr, sg, sb = color_blue
        sa = 255
        sa_norm = 1.0

        base_surface = pygame.Surface((width, height))

        def test_sdf_rendering():
            surface = base_surface
            surface.fill((0, 0, 0))
            
            # Lock the surface for direct pixel access
            px_arr = pygame.PixelArray(surface)
            
            for y in range(height):
                for x in range(width):
                    dist = composed_field(x, y)
                    val = 0.5 - dist
                    if val <= 0.0:
                        continue
                        
                    alpha = 1.0 if val >= 1.0 else val
                    sa_eff = sa_norm * alpha
                    
                    if sa_eff >= 0.996:
                        px_arr[x, y] = (sr, sg, sb)
                    else:
                        # Extract existing colors from Pygame 32-bit integer representation
                        pixel_val = px_arr[x, y]
                        dr = (pixel_val >> 16) & 255
                        dg = (pixel_val >> 8) & 255
                        db = pixel_val & 255
                        
                        isa = int(sa_eff * 256)
                        inv_isa = 256 - isa
                        
                        nr = (sr * isa + dr * inv_isa) >> 8
                        ng = (sg * isa + dg * inv_isa) >> 8
                        nb = (sb * isa + db * inv_isa) >> 8
                        
                        px_arr[x, y] = (nr, ng, nb)
                        
            px_arr.close()

    else:
        # Effy implementation using its built-in RenderFieldCmd and rasterizer
        color_blue = Color(0, 0, 255, 255)

        base_surface = PixelBuffer.create(width, height)

        def test_sdf_rendering():
            surface = base_surface
            surface = render_field(surface, None, composed_field, color_blue)
            _ = surface._data

    runner.register("SDF CSG Shader 500x500", test_sdf_rendering, iterations=5, warmup=1)
    runner.dump_json()

if __name__ == "__main__":
    main()
