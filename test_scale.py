import array
from Effy.video.rect import Rect, Point
from Effy.render.rasterizer import rasterize_blit_scaled, rasterize_blit_bilinear

# Create source buffer 2x2
src_data = array.array('I', [
    0xFF0000FF, 0xFF00FF00,
    0xFFFF0000, 0xFFFFFFFF
])
src_w, src_h = 2, 2
src_pitch = 2

# Create dst buffer 4x4
dst_data = array.array('I', [0] * 16)
dst_w, dst_h = 4, 4
dst_pitch = 4

print("Testing nearest neighbor scaling:")
rasterize_blit_scaled(src_data, src_w, src_h, src_pitch, None,
                      dst_data, dst_w, dst_h, dst_pitch, None)

for y in range(4):
    print([hex(dst_data[y*4 + x]) for x in range(4)])

# Create dst buffer 4x4
dst_data2 = array.array('I', [0] * 16)

print("\nTesting bilinear scaling:")
rasterize_blit_bilinear(src_data, src_w, src_h, src_pitch, None,
                        dst_data2, dst_w, dst_h, dst_pitch, None)

for y in range(4):
    print([hex(dst_data2[y*4 + x]) for x in range(4)])

print("Done!")
