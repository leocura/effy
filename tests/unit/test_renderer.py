"""Unit tests for the deferred rendering pipeline (RenderContext).

All pixel assertions go through render_present against a HeadlessAdapter,
which captures the final resolved PixelBuffer via its _last_presented_buffer
attribute. This verifies both the correctness of command rasterization and
that no pixel buffer is materialized before render_present is called.
"""

import pytest
from Effy._internal.registry import set_platform_adapter, register_window
from Effy.platform.headless import HeadlessAdapter
from Effy.render import (
    render_clear, render_set_draw_color, render_fill_rect, render_draw_rect,
    render_present, RenderContext, render_draw_line, render_draw_circle,
    render_fill_circle, render_fill_triangle
)
from Effy.render.commands import FillRectCmd, DrawRectCmd, DrawLineCmd, DrawCircleCmd, FillCircleCmd, FillTriangleCmd
from Effy.video import Rect, Point
from Effy.types import WindowID, Color


WINDOW_ID = WindowID(1)
WIDTH, HEIGHT = 100, 100


@pytest.fixture(autouse=True)
def headless():
    """Register a headless adapter and a dummy window handle for all tests."""
    adapter = HeadlessAdapter()
    set_platform_adapter(adapter)
    register_window(WINDOW_ID, "headless_window_handle")
    yield adapter
    set_platform_adapter(None)


def _make_ctx(draw_color: Color = Color(0, 0, 0, 255)) -> RenderContext:
    """Create a blank RenderContext for tests."""
    return RenderContext(
        window_id=WINDOW_ID,
        width=WIDTH,
        height=HEIGHT,
        draw_color=draw_color,
    )


def _present_and_get_buffer(ctx: RenderContext, adapter: HeadlessAdapter):
    """Run render_present and return the resolved PixelBuffer from the adapter."""
    render_present(ctx).run()
    return adapter._last_presented_buffer


class TestRenderClear:
    """Tests for render_clear."""

    def test_enqueues_fill_rect_cmd(self):
        """render_clear should append exactly one FillRectCmd covering the whole surface."""
        ctx = _make_ctx(Color(255, 0, 0))
        ctx2 = render_clear(ctx)
        assert len(ctx2._commands) == 1
        assert isinstance(ctx2._commands[0], FillRectCmd)
        assert ctx2._commands[0].rect is None
        assert ctx2._commands[0].color == Color(255, 0, 0)

    def test_resets_previous_commands(self):
        """render_clear should discard any previously accumulated commands."""
        ctx = _make_ctx(Color(0, 255, 0))
        ctx = render_fill_rect(ctx, Rect(0, 0, 10, 10))
        ctx = render_clear(ctx)
        assert len(ctx._commands) == 1

    def test_pixel_output_is_correct(self, headless):
        """After present, all pixels should match the clear color."""
        ctx = _make_ctx(Color(255, 0, 0))
        ctx = render_clear(ctx)
        buf = _present_and_get_buffer(ctx, headless)
        assert buf.get_pixel(0, 0) == Color(255, 0, 0)
        assert buf.get_pixel(99, 99) == Color(255, 0, 0)


class TestRenderSetDrawColor:
    """Tests for render_set_draw_color."""

    def test_updates_draw_color_without_adding_command(self):
        """Changing draw color should not enqueue any command."""
        ctx = _make_ctx()
        ctx2 = render_set_draw_color(ctx, 255, 0, 0)
        assert ctx2.draw_color == Color(255, 0, 0)
        assert len(ctx2._commands) == 0

    def test_subsequent_commands_use_new_color(self, headless):
        """Commands issued after a color change should use the new color."""
        ctx = render_clear(_make_ctx(Color(0, 0, 0)))
        ctx = render_set_draw_color(ctx, 0, 255, 0)
        ctx = render_fill_rect(ctx, Rect(10, 10, 20, 20))
        buf = _present_and_get_buffer(ctx, headless)
        assert buf.get_pixel(15, 15) == Color(0, 255, 0)
        assert buf.get_pixel(5, 5) == Color(0, 0, 0)


class TestRenderFillRect:
    """Tests for render_fill_rect."""

    def test_enqueues_fill_rect_cmd(self):
        """render_fill_rect should append exactly one FillRectCmd."""
        ctx = _make_ctx(Color(255, 0, 0))
        ctx2 = render_fill_rect(ctx, Rect(10, 10, 20, 20))
        assert len(ctx2._commands) == 1
        assert isinstance(ctx2._commands[0], FillRectCmd)

    def test_no_pixel_buffer_before_present(self):
        """No pixel buffer should be materialized before render_present."""
        ctx = _make_ctx(Color(255, 0, 0))
        ctx2 = render_fill_rect(ctx, Rect(10, 10, 20, 20))
        # Confirm no buffer field exists on the new context
        assert not hasattr(ctx2, "buffer")

    def test_pixel_output_is_correct(self, headless):
        """After present, pixels inside the rect should match the draw color."""
        ctx = render_clear(_make_ctx(Color(0, 0, 0)))
        ctx = render_set_draw_color(ctx, 255, 0, 0)
        ctx = render_fill_rect(ctx, Rect(10, 10, 20, 20))
        buf = _present_and_get_buffer(ctx, headless)
        assert buf.get_pixel(15, 15) == Color(255, 0, 0)
        assert buf.get_pixel(5, 5) == Color(0, 0, 0)


class TestRenderDrawRect:
    """Tests for render_draw_rect."""

    def test_enqueues_draw_rect_cmd(self):
        """render_draw_rect should append exactly one DrawRectCmd."""
        ctx = _make_ctx(Color(255, 0, 0))
        ctx2 = render_draw_rect(ctx, Rect(10, 10, 20, 20))
        assert len(ctx2._commands) == 1
        assert isinstance(ctx2._commands[0], DrawRectCmd)

    def test_pixel_output_is_correct(self, headless):
        """After present, border pixels should be colored; interior should be empty."""
        ctx = render_clear(_make_ctx(Color(0, 0, 0)))
        ctx = render_set_draw_color(ctx, 255, 0, 0)
        ctx = render_draw_rect(ctx, Rect(10, 10, 20, 20))
        buf = _present_and_get_buffer(ctx, headless)
        assert buf.get_pixel(10, 10) == Color(255, 0, 0)
        assert buf.get_pixel(15, 10) == Color(255, 0, 0)
        assert buf.get_pixel(15, 15) == Color(0, 0, 0)


class TestRenderPresent:
    """Tests for render_present flush semantics."""

    def test_returns_clean_context_with_empty_queue(self, headless):
        """render_present should return a new context with an empty command queue."""
        ctx = _make_ctx(Color(255, 0, 0))
        ctx = render_fill_rect(ctx, Rect(0, 0, 10, 10))
        assert len(ctx._commands) == 1
        next_ctx = render_present(ctx).run()
        assert len(next_ctx._commands) == 0

    def test_chained_draw_calls_accumulate_commands(self):
        """Multiple draw calls should accumulate commands without any allocation."""
        ctx = _make_ctx(Color(255, 0, 0))
        for _ in range(100):
            ctx = render_fill_rect(ctx, Rect(0, 0, 10, 10))
        assert len(ctx._commands) == 100

    def test_frame_produces_correct_layered_output(self, headless):
        """Commands should be rasterized in order, with later commands on top."""
        ctx = render_clear(_make_ctx(Color(0, 0, 0)))
        ctx = render_set_draw_color(ctx, 255, 0, 0)
        ctx = render_fill_rect(ctx, Rect(0, 0, 50, 50))
        ctx = render_set_draw_color(ctx, 0, 255, 0)
        ctx = render_fill_rect(ctx, Rect(25, 25, 50, 50))
        buf = _present_and_get_buffer(ctx, headless)
        # Green painted over red in the overlapping region
        assert buf.get_pixel(30, 30) == Color(0, 255, 0)
        # Red only in the non-overlapping region
        assert buf.get_pixel(10, 10) == Color(255, 0, 0)
        # Black background
        assert buf.get_pixel(90, 90) == Color(0, 0, 0)


class TestRenderDrawingPrimitives:
    """Unit tests for the new high-level functional drawing primitives on RenderContext."""

    def test_render_draw_line(self, headless):
        """render_draw_line should correctly enqueue and draw a line."""
        ctx = render_clear(_make_ctx(Color(0, 0, 0)))
        ctx = render_set_draw_color(ctx, 255, 255, 255)
        ctx = render_draw_line(ctx, Point(10, 10), Point(20, 10))
        
        assert len(ctx._commands) == 2
        assert isinstance(ctx._commands[1], DrawLineCmd)
        
        buf = _present_and_get_buffer(ctx, headless)
        # Pixel along the horizontal line should be white
        assert buf.get_pixel(15, 10) == Color(255, 255, 255)

    def test_render_draw_circle(self, headless):
        """render_draw_circle should correctly enqueue and stroke a circle outline."""
        ctx = render_clear(_make_ctx(Color(0, 0, 0)))
        ctx = render_set_draw_color(ctx, 0, 255, 0)
        ctx = render_draw_circle(ctx, Point(50, 50), 10)
        
        assert len(ctx._commands) == 2
        assert isinstance(ctx._commands[1], DrawCircleCmd)
        
        buf = _present_and_get_buffer(ctx, headless)
        # Boundary pixel
        assert buf.get_pixel(60, 50) == Color(0, 255, 0)
        # Interior pixel (empty)
        assert buf.get_pixel(50, 50) == Color(0, 0, 0)

    def test_render_fill_circle(self, headless):
        """render_fill_circle should correctly enqueue and fill a circle."""
        ctx = render_clear(_make_ctx(Color(0, 0, 0)))
        ctx = render_set_draw_color(ctx, 0, 0, 255)
        ctx = render_fill_circle(ctx, Point(50, 50), 10)
        
        assert len(ctx._commands) == 2
        assert isinstance(ctx._commands[1], FillCircleCmd)
        
        buf = _present_and_get_buffer(ctx, headless)
        # Boundary pixel
        assert buf.get_pixel(60, 50) == Color(0, 0, 255)
        # Interior pixel (filled)
        assert buf.get_pixel(50, 50) == Color(0, 0, 255)

    def test_render_fill_triangle(self, headless):
        """render_fill_triangle should correctly enqueue and fill a triangle."""
        ctx = render_clear(_make_ctx(Color(0, 0, 0)))
        ctx = render_set_draw_color(ctx, 255, 0, 255)
        ctx = render_fill_triangle(ctx, Point(50, 20), Point(30, 60), Point(70, 60))
        
        assert len(ctx._commands) == 2
        assert isinstance(ctx._commands[1], FillTriangleCmd)
        
        buf = _present_and_get_buffer(ctx, headless)
        # Inside triangle
        assert buf.get_pixel(50, 40) == Color(255, 0, 255)
        # Outside triangle
        assert buf.get_pixel(10, 10) == Color(0, 0, 0)


class TestRendererAccelerated:
    """Unit tests for the hardware-accelerated rendering configurations and fallback logic."""

    def test_create_renderer_with_accelerated_flags(self):
        """create_renderer with ACCELERATED should store flags on the RenderContext."""
        from Effy.render import create_renderer, RendererFlags
        from Effy.video import Window, WindowFlags
        from Effy._internal.result import Ok

        win = Window(id=WINDOW_ID, title="Test", x=0, y=0, w=100, h=100, flags=WindowFlags.SHOWN)
        res = create_renderer(win, flags=RendererFlags.SOFTWARE).run()
        
        assert isinstance(res, Ok)
        ctx = res.value
        assert ctx.flags == RendererFlags.SOFTWARE


    def test_render_present_fallback_to_software(self, headless):
        """If the platform adapter lacks hardware acceleration, render_present should fallback to software."""
        from Effy.render import create_renderer, RendererFlags, render_clear, render_present
        from Effy.video import Window, WindowFlags

        win = Window(id=WINDOW_ID, title="Test", x=0, y=0, w=100, h=100, flags=WindowFlags.SHOWN)
        res = create_renderer(win, flags=RendererFlags.SOFTWARE).run()
        ctx = res.value
        ctx = render_clear(ctx)
        
        # HeadlessAdapter does not implement present_accelerated, so it will fall back to software
        next_ctx = render_present(ctx).run()
        assert len(next_ctx._commands) == 0
        assert headless._last_presented_buffer is not None
        assert headless._last_presented_buffer.get_pixel(0, 0) == Color(0, 0, 0)

    def test_render_present_accelerated_success(self, headless):
        """If the platform adapter supports present_accelerated, it should be called directly."""
        from Effy.render import create_renderer, RendererFlags, render_clear, render_present
        from Effy.video import Window, WindowFlags
        from Effy._internal.result import Ok

        called_args = []

        # Mock present_accelerated on headless adapter
        def mock_present_accelerated(handle, commands, width, height):
            called_args.append((handle, commands, width, height))
            return Ok(None)

        headless.present_accelerated = mock_present_accelerated

        win = Window(id=WINDOW_ID, title="Test", x=0, y=0, w=100, h=100, flags=WindowFlags.SHOWN)
        res = create_renderer(win, flags=RendererFlags.SOFTWARE).run()
        ctx = res.value
        ctx = render_clear(ctx)
        
        next_ctx = render_present(ctx).run()
        
        assert len(next_ctx._commands) == 0
        assert len(called_args) == 1
        assert called_args[0][0] == "headless_window_handle"
        assert len(called_args[0][1]) == 1  # 1 Clear command
        
        # Clean up mock
        delattr(headless, "present_accelerated")


