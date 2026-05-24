from hypothesis import given, strategies as st
from Effy.video.surface import PixelBuffer
from Effy.video.rect import Rect, Point
from Effy.types import Color
from Effy.render import fill_rect, draw_rect, draw_line, draw_circle, fill_circle, fill_triangle, blit, blit_blended, blit_scaled, blit_bilinear
from Effy.render.rasterizer import _sort_triangle_vertices

def test_fill_rect_happy_path():
    surface = PixelBuffer.create(10, 10)
    color = Color(255, 0, 0, 255)
    rect = Rect(2, 2, 5, 5)
    
    result = fill_rect(surface, rect, color)
    
    # Check a pixel inside the rect
    assert result.get_pixel(2, 2) == color
    assert result.get_pixel(6, 6) == color
    
    # Check a pixel outside the rect
    assert result.get_pixel(1, 1) == Color(0, 0, 0, 0)
    assert result.get_pixel(7, 7) == Color(0, 0, 0, 0)

def test_fill_rect_none_fills_all():
    surface = PixelBuffer.create(10, 10)
    color = Color(0, 255, 0, 255)
    
    result = fill_rect(surface, None, color)
    
    for y in range(10):
        for x in range(10):
            assert result.get_pixel(x, y) == color

def test_fill_rect_clipping():
    surface = PixelBuffer.create(10, 10)
    color = Color(0, 0, 255, 255)
    rect = Rect(5, 5, 10, 10) # Overflows
    
    result = fill_rect(surface, rect, color)
    
    assert result.get_pixel(9, 9) == color
    # Outside bounds should return transparent black by default in get_pixel
    assert result.get_pixel(10, 10) == Color(0, 0, 0, 0)

def test_draw_rect_happy_path():
    surface = PixelBuffer.create(10, 10)
    color = Color(255, 255, 0, 255)
    rect = Rect(2, 2, 5, 5)
    
    result = draw_rect(surface, rect, color)
    
    # Check borders
    assert result.get_pixel(2, 2) == color # Top-left
    assert result.get_pixel(6, 2) == color # Top-right
    assert result.get_pixel(2, 6) == color # Bottom-left
    assert result.get_pixel(6, 6) == color # Bottom-right
    
    # Check inside (should be empty)
    assert result.get_pixel(3, 3) == Color(0, 0, 0, 0)
    assert result.get_pixel(5, 5) == Color(0, 0, 0, 0)

def test_draw_line_horizontal():
    surface = PixelBuffer.create(10, 10)
    color = Color(0, 255, 255, 255)
    p1 = Point(2, 2)
    p2 = Point(7, 2)
    
    result = draw_line(surface, p1, p2, color)
    
    for x in range(2, 8):
        assert result.get_pixel(x, 2) == color

def test_draw_line_vertical():
    surface = PixelBuffer.create(10, 10)
    color = Color(255, 0, 255, 255)
    p1 = Point(2, 2)
    p2 = Point(2, 7)
    
    result = draw_line(surface, p1, p2, color)
    
    for y in range(2, 8):
        assert result.get_pixel(2, y) == color

def test_draw_line_diagonal():
    surface = PixelBuffer.create(10, 10)
    color = Color(255, 255, 255, 255)
    p1 = Point(2, 2)
    p2 = Point(7, 7)
    
    result = draw_line(surface, p1, p2, color)
    
    for i in range(2, 8):
        assert result.get_pixel(i, i) == color

def test_draw_circle_happy_path():
    surface = PixelBuffer.create(20, 20)
    color = Color(255, 0, 0, 255)
    center = Point(10, 10)
    radius = 5
    
    result = draw_circle(surface, center, radius, color)
    
    # Check points on the circle
    assert result.get_pixel(15, 10) == color # Right
    assert result.get_pixel(5, 10) == color # Left
    assert result.get_pixel(10, 15) == color # Bottom
    assert result.get_pixel(10, 5) == color # Top
    
    # Check center (should be empty)
    assert result.get_pixel(10, 10) == Color(0, 0, 0, 0)

def test_fill_circle_happy_path():
    surface = PixelBuffer.create(20, 20)
    color = Color(0, 255, 0, 255)
    center = Point(10, 10)
    radius = 5
    
    result = fill_circle(surface, center, radius, color)
    
    # Check points inside the circle
    assert result.get_pixel(10, 10) == color
    assert result.get_pixel(12, 12) == color
    
    # Check points outside
    assert result.get_pixel(16, 16) == Color(0, 0, 0, 0)

def test_fill_triangle_happy_path():
    surface = PixelBuffer.create(10, 10)
    color = Color(255, 0, 255, 255)
    p1 = Point(1, 1)
    p2 = Point(5, 1)
    p3 = Point(1, 5)
    
    result = fill_triangle(surface, p1, p2, p3, color)
    
    # Check points inside
    assert result.get_pixel(2, 2) == color
    assert result.get_pixel(1, 1) == color
    
    # Check points outside
    assert result.get_pixel(5, 5) == Color(0, 0, 0, 0)

def test_sort_triangle_vertices_orders_by_y_then_x():
    ordered = _sort_triangle_vertices(Point(5, 4), Point(3, 1), Point(1, 1))

    assert ordered == (Point(1, 1), Point(3, 1), Point(5, 4))

def test_fill_triangle_handles_flat_edges():
    surface = PixelBuffer.create(10, 10)
    color = Color(255, 0, 255, 255)

    flat_top = fill_triangle(surface, Point(1, 1), Point(5, 1), Point(3, 5), color)
    flat_bottom = fill_triangle(surface, Point(3, 1), Point(1, 5), Point(5, 5), color)

    assert flat_top.get_pixel(3, 2) == color
    assert flat_top.get_pixel(3, 4) == color
    assert flat_top.get_pixel(0, 0) == Color(0, 0, 0, 0)

    assert flat_bottom.get_pixel(3, 2) == color
    assert flat_bottom.get_pixel(3, 4) == color
    assert flat_bottom.get_pixel(0, 0) == Color(0, 0, 0, 0)

def test_blit_happy_path():
    src = PixelBuffer.create(5, 5)
    color = Color(255, 255, 255, 255)
    src = fill_rect(src, None, color) # Fill src with white
    
    dst = PixelBuffer.create(10, 10)
    # Blit whole src to dst at (2, 2)
    result = blit(src, None, dst, Rect(2, 2, 5, 5))
    
    # Check that (2, 2) to (6, 6) in dst is white
    for y in range(2, 7):
        for x in range(2, 7):
            assert result.get_pixel(x, y) == color
            
    # Check outside
    assert result.get_pixel(1, 1) == Color(0, 0, 0, 0)

def test_blit_blended_happy_path():
    src = PixelBuffer.create(5, 5)
    color = Color(255, 0, 0, 128) # Semi-transparent red
    src = fill_rect(src, None, color)
    
    dst = PixelBuffer.create(5, 5)
    dst = fill_rect(dst, None, Color(0, 255, 0, 255)) # Solid green
    
    result = blit_blended(src, None, dst, None)
    
    # Result should be a mix of red and green
    # 255 * 0.5 + 0 * 0.5 = 127
    # 0 * 0.5 + 255 * 0.5 = 127
    pixel = result.get_pixel(2, 2)
    assert 120 <= pixel.r <= 135
    assert 120 <= pixel.g <= 135
    assert pixel.b == 0
    assert 254 <= pixel.a <= 255

def test_blit_scaled_happy_path():
    src = PixelBuffer.create(2, 2)
    color = Color(255, 255, 255, 255)
    src = fill_rect(src, None, color) # Fill src with white
    
    dst = PixelBuffer.create(4, 4)
    # Blit 2x2 src to 4x4 dst (scale up)
    result = blit_scaled(src, None, dst, Rect(0, 0, 4, 4))
    
    # Check that all pixels in dst are white
    for y in range(4):
        for x in range(4):
            assert result.get_pixel(x, y) == color

def test_blit_bilinear_happy_path():
    src = PixelBuffer.create(2, 2)
    color = Color(255, 255, 255, 255)
    src = fill_rect(src, None, color)
    
    dst = PixelBuffer.create(4, 4)
    result = blit_bilinear(src, None, dst, Rect(0, 0, 4, 4))
    
    for y in range(4):
        for x in range(4):
            assert result.get_pixel(x, y) == color

@given(
    st.integers(min_value=0, max_value=10),
    st.integers(min_value=0, max_value=10),
    st.integers(min_value=1, max_value=10),
    st.integers(min_value=1, max_value=10)
)
def test_fill_rect_property(x, y, w, h):
    surface = PixelBuffer.create(20, 20)
    color = Color(255, 255, 255, 255)
    rect = Rect(x, y, w, h)
    
    result = fill_rect(surface, rect, color)
    
    # Verify that pixels inside the rect are colored
    for py in range(y, min(20, y + h)):
        for px in range(x, min(20, x + w)):
            assert result.get_pixel(px, py) == color


def test_blit_blended_clipping_and_edge_cases():
    src = PixelBuffer.create(5, 5)
    color = Color(255, 0, 0, 128)
    src = fill_rect(src, None, color)
    
    dst = PixelBuffer.create(5, 5)
    dst = fill_rect(dst, None, Color(0, 255, 0, 255))
    
    # Blit with offset clipping out of bounds
    result = blit_blended(src, Rect(-2, -2, 10, 10), dst, Rect(3, 3, 5, 5))
    # It shouldn't crash, and outside should remain untouched
    assert result.get_pixel(0, 0) == Color(0, 255, 0, 255)


def test_blit_scaled_parity_1to1():
    """Verify that a 1:1 scaling blit matches a standard 1:1 blit perfectly."""
    src = PixelBuffer.create(2, 2)
    src = src.write_pixel(0, 0, Color(255, 0, 0, 255))
    src = src.write_pixel(1, 0, Color(0, 255, 0, 255))
    src = src.write_pixel(0, 1, Color(0, 0, 255, 255))
    src = src.write_pixel(1, 1, Color(255, 255, 255, 255))

    dst1 = PixelBuffer.create(2, 2)
    dst2 = PixelBuffer.create(2, 2)

    res_blit = blit(src, None, dst1, None)
    res_scaled = blit_scaled(src, None, dst2, Rect(0, 0, 2, 2))

    for y in range(2):
        for x in range(2):
            assert res_blit.get_pixel(x, y) == res_scaled.get_pixel(x, y)


def test_blit_scaled_parity_integer_3x():
    """Verify that the fast path 3x integer scaling produces correct pixel replication."""
    src = PixelBuffer.create(2, 2)
    c00 = Color(255, 0, 0, 255)
    c10 = Color(0, 255, 0, 255)
    c01 = Color(0, 0, 255, 255)
    c11 = Color(255, 255, 255, 255)

    src = src.write_pixel(0, 0, c00)
    src = src.write_pixel(1, 0, c10)
    src = src.write_pixel(0, 1, c01)
    src = src.write_pixel(1, 1, c11)

    dst = PixelBuffer.create(6, 6)
    result = blit_scaled(src, None, dst, Rect(0, 0, 6, 6))

    for y in range(6):
        for x in range(6):
            expected_color = (
                c00 if (x < 3 and y < 3) else
                c10 if (x >= 3 and y < 3) else
                c01 if (x < 3 and y >= 3) else
                c11
            )
            assert result.get_pixel(x, y) == expected_color


def test_blit_scaled_parity_fractional_2_5x():
    """Verify that a 2.5x fractional scale falls back correctly and maintains correctness."""
    src = PixelBuffer.create(2, 2)
    c00 = Color(255, 0, 0, 255)
    c10 = Color(0, 255, 0, 255)
    c01 = Color(0, 0, 255, 255)
    c11 = Color(255, 255, 255, 255)

    src = src.write_pixel(0, 0, c00)
    src = src.write_pixel(1, 0, c10)
    src = src.write_pixel(0, 1, c01)
    src = src.write_pixel(1, 1, c11)

    dst = PixelBuffer.create(5, 5)
    result = blit_scaled(src, None, dst, Rect(0, 0, 5, 5))

    for y in range(5):
        for x in range(5):
            src_x = (x * 2) // 5
            src_y = (y * 2) // 5
            expected_color = (
                c00 if (src_x == 0 and src_y == 0) else
                c10 if (src_x == 1 and src_y == 0) else
                c01 if (src_x == 0 and src_y == 1) else
                c11
            )
            assert result.get_pixel(x, y) == expected_color


def test_blit_scaled_out_of_bounds_clipping():
    """Verify that integer scaled blitting handles out-of-bounds clipping properly without crashing."""
    src = PixelBuffer.create(2, 2)
    c00 = Color(255, 0, 0, 255)
    c10 = Color(0, 255, 0, 255)
    c01 = Color(0, 0, 255, 255)
    c11 = Color(255, 255, 255, 255)

    src = src.write_pixel(0, 0, c00)
    src = src.write_pixel(1, 0, c10)
    src = src.write_pixel(0, 1, c01)
    src = src.write_pixel(1, 1, c11)

    dst = PixelBuffer.create(4, 4)
    result = blit_scaled(src, None, dst, Rect(-2, -2, 4, 4))

    for y in range(2):
        for x in range(2):
            assert result.get_pixel(x, y) == c11

    assert result.get_pixel(2, 2) == Color(0, 0, 0, 0)

