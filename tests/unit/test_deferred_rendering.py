"""Tests specifically targeting the deferred rendering optimization.

These tests verify the core promise of the optimization: drawing calls are
pure O(1) command enqueues, no pixel buffer is allocated before render_present,
and the single rasterization pass produces correct pixel output.
"""

import pytest
from Effy._internal.registry import set_platform_adapter, register_window
from Effy.platform.headless import HeadlessAdapter
from Effy.render.renderer import (
    RenderContext, render_clear, render_set_draw_color, render_fill_rect,
    render_draw_rect, render_present,
)
from Effy.video import Rect
from Effy.types import WindowID, Color


WINDOW_ID = WindowID(42)
WIDTH, HEIGHT = 64, 64


@pytest.fixture(autouse=True)
def headless():
    """Register a headless adapter and a dummy window handle for all tests."""
    adapter = HeadlessAdapter()
    set_platform_adapter(adapter)
    register_window(WINDOW_ID, "headless_window_handle")
    yield adapter
    set_platform_adapter(None)


def _ctx(draw_color: Color = Color(0, 0, 0, 255)) -> RenderContext:
    """Build a blank RenderContext for tests."""
    return RenderContext(
        window_id=WINDOW_ID,
        width=WIDTH,
        height=HEIGHT,
        draw_color=draw_color,
    )


class TestZeroAllocationBeforePresent:
    """Verify that no pixel data is materialized before render_present is called."""

    def test_render_context_has_no_buffer_field(self):
        """RenderContext must not expose a 'buffer' field."""
        ctx = _ctx()
        assert not hasattr(ctx, "buffer")

    def test_draw_calls_do_not_produce_pixel_buffers(self):
        """Issuing draw calls should only grow _commands, not allocate buffers."""
        ctx = _ctx(Color(255, 0, 0))
        ctx = render_clear(ctx)
        ctx = render_fill_rect(ctx, Rect(0, 0, 10, 10))
        ctx = render_draw_rect(ctx, Rect(5, 5, 20, 20))
        # Only commands — no pixel data anywhere in the context
        assert not hasattr(ctx, "buffer")
        assert len(ctx._commands) == 3

    def test_hundred_draw_calls_produce_hundred_commands(self):
        """Each draw call must be exactly O(1) — one command appended."""
        ctx = _ctx(Color(0, 0, 255))
        for i in range(100):
            ctx = render_fill_rect(ctx, Rect(i % WIDTH, i % HEIGHT, 1, 1))
        assert len(ctx._commands) == 100


class TestCommandOrdering:
    """Verify that commands are rasterized in the correct order."""

    def test_later_commands_overwrite_earlier_ones(self, headless):
        """A red fill followed by a green fill at the same region should end green."""
        ctx = render_clear(_ctx(Color(0, 0, 0)))
        ctx = render_set_draw_color(ctx, 255, 0, 0)
        ctx = render_fill_rect(ctx, Rect(0, 0, WIDTH, HEIGHT))
        ctx = render_set_draw_color(ctx, 0, 255, 0)
        ctx = render_fill_rect(ctx, Rect(0, 0, WIDTH, HEIGHT))
        render_present(ctx).run()
        buf = headless._last_presented_buffer
        assert buf.get_pixel(0, 0) == Color(0, 255, 0)

    def test_clear_sets_background_color(self, headless):
        """render_clear should set the entire surface to the draw color."""
        ctx = render_set_draw_color(_ctx(), 100, 150, 200)
        ctx = render_clear(ctx)
        render_present(ctx).run()
        buf = headless._last_presented_buffer
        assert buf.get_pixel(0, 0) == Color(100, 150, 200)
        assert buf.get_pixel(WIDTH - 1, HEIGHT - 1) == Color(100, 150, 200)


class TestPresent:
    """Verify render_present flush semantics."""

    def test_present_returns_empty_command_queue(self, headless):
        """The returned context after present must have an empty command queue."""
        ctx = render_clear(_ctx())
        ctx = render_fill_rect(ctx, Rect(0, 0, 10, 10))
        assert len(ctx._commands) == 2
        next_ctx = render_present(ctx).run()
        assert len(next_ctx._commands) == 0

    def test_present_preserves_draw_color(self, headless):
        """The draw color must be preserved across present calls."""
        ctx = render_set_draw_color(_ctx(), 77, 88, 99)
        next_ctx = render_present(ctx).run()
        assert next_ctx.draw_color == Color(77, 88, 99)

    def test_present_stores_buffer_in_headless_adapter(self, headless):
        """render_present must invoke flip_buffer, populating the adapter's buffer."""
        ctx = render_clear(_ctx(Color(33, 44, 55)))
        assert headless._last_presented_buffer is None
        render_present(ctx).run()
        assert headless._last_presented_buffer is not None

    def test_sequential_frames_do_not_carry_over_commands(self, headless):
        """Each new frame starts with a clean command queue after present."""
        ctx = render_clear(_ctx(Color(255, 0, 0)))
        ctx = render_fill_rect(ctx, Rect(0, 0, 10, 10))
        ctx = render_present(ctx).run()
        # Second frame: only clear — no leftover fill from first frame
        ctx = render_set_draw_color(ctx, 0, 0, 255)
        ctx = render_clear(ctx)
        render_present(ctx).run()
        buf = headless._last_presented_buffer
        # Entire surface should be blue; no red rect should remain
        assert buf.get_pixel(5, 5) == Color(0, 0, 255)


class TestRenderContextImmutability:
    """Verify that RenderContext instances are properly immutable."""

    def test_render_context_is_frozen(self):
        """Assigning to a RenderContext field must raise FrozenInstanceError."""
        from dataclasses import FrozenInstanceError
        ctx = _ctx()
        with pytest.raises(FrozenInstanceError):
            ctx.draw_color = Color(1, 2, 3)  # type: ignore[misc]

    def test_draw_calls_return_new_instances(self):
        """Each draw call must return a new RenderContext, not mutate the original."""
        ctx = _ctx(Color(255, 0, 0))
        ctx2 = render_fill_rect(ctx, Rect(0, 0, 10, 10))
        assert ctx is not ctx2
        assert len(ctx._commands) == 0
        assert len(ctx2._commands) == 1
