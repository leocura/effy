import sys
import os
import time
import array

sys.path.insert(0, '/home/leocura/antigravity/effy')

from Effy.init import init
from Effy.init.flags import InitFlag
from Effy.types import Color
from Effy.video.window import create_window, WindowFlags, destroy_window
from Effy.render.renderer import create_renderer, RendererFlags, RenderContext, render_shader, render_copy_scaled, render_clear, render_present
from Effy.video.surface import PixelBuffer
from Effy.render.texture import create_texture_from_surface
from Effy.video.rect import Rect
from Effy.render.compiler import gpu_shader

@gpu_shader
def draw_screen(u: float, v: float) -> Color:
    return sample_texture(u, v)

def run_benchmark(use_gpu: bool, num_frames: int = 600):
    res = init(InitFlag.VIDEO).run()
    if res.is_err():
        print("Failed to init Effy:", res.value)
        return

    win_res = create_window("Benchmark", 100, 100, 160*3, 144*3, WindowFlags.HIDDEN).run()
    if win_res.is_err():
        print("Failed to create window")
        return
    window = win_res.value
    
    flags = RendererFlags.SOFTWARE
    rend_res = create_renderer(window, -1, flags).run()
    if rend_res.is_err():
        print("Failed to create renderer")
        return
    
    # Create dummy frame 160x144
    data_arr = array.array('I', [0xFFFFFFFF] * (160 * 144))
    
    # Pre-create texture
    pb = PixelBuffer(width=160, height=144, pitch=160, _data_cache=[data_arr], _commands_list=[], _is_transient=False)
    display_tex = create_texture_from_surface(pb).run().value

    start_time = time.perf_counter()

    for _ in range(num_frames):
        ctx = RenderContext(window_id=window.id, width=window.w, height=window.h, draw_color=Color(0,0,0,255), _commands=[], flags=flags)
        ctx = render_clear(ctx)
        
        if use_gpu:
            ctx = render_shader(ctx, display_tex, None, Rect(0, 0, window.w, window.h), shader=draw_screen, gpu=use_gpu)
        else:
            ctx = render_copy_scaled(ctx, display_tex, None, Rect(0, 0, window.w, window.h))
            
        ctx = render_present(ctx).run()

    end_time = time.perf_counter()
    total_time = end_time - start_time
    fps = num_frames / total_time
    
    print(f"{'GPU' if use_gpu else 'Software Fixed-Point'} Scaling:")
    print(f"Total time for {num_frames} frames: {total_time:.4f}s")
    print(f"Average FPS: {fps:.2f}\n")
    
    destroy_window(window).run()

if __name__ == "__main__":
    print("Starting Benchmark...\n")
    run_benchmark(use_gpu=True)
    run_benchmark(use_gpu=False)
