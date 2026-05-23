import pytest
from Effy.ui.imgui import UIState, ui_begin, ui_end, ui_button, ui_slider
from Effy.video.rect import Point, Rect
from Effy.render.renderer import RenderContext
from Effy.video.font import BitmapFont

class MockFont:
    glyph_width = 8
    glyph_height = 8
    char_map = {}

def test_ui_button():
    ctx = UIState(Point(50, 50), False)
    renderer = RenderContext(0, 100, 100)
    font = MockFont() # type: ignore
    
    # Frame 1: hover
    ctx = ui_begin(ctx)
    ctx, renderer, clicked = ui_button(ctx, renderer, font, "btn1", Rect(0, 0, 100, 100), "Click")
    assert ctx.hot_item == "btn1"
    assert ctx.active_item is None
    assert clicked is False
    ctx = ui_end(ctx)
    
    # Frame 2: mousedown
    ctx = ctx.evolve(mouse_down=True)
    ctx = ui_begin(ctx)
    ctx, renderer, clicked = ui_button(ctx, renderer, font, "btn1", Rect(0, 0, 100, 100), "Click")
    assert ctx.hot_item == "btn1"
    assert ctx.active_item == "btn1"
    assert clicked is False
    ctx = ui_end(ctx)
    
    # Frame 3: mouseup
    ctx = ctx.evolve(mouse_down=False)
    ctx = ui_begin(ctx)
    ctx, renderer, clicked = ui_button(ctx, renderer, font, "btn1", Rect(0, 0, 100, 100), "Click")
    assert ctx.hot_item == "btn1"
    assert ctx.active_item == "btn1" # still active during the evaluation
    assert clicked is True
    ctx = ui_end(ctx)
    
    assert ctx.active_item is None # should be cleared after ui_end

def test_ui_slider():
    ctx = UIState(Point(50, 50), True, active_item="slider1") # active and dragging at 50%
    renderer = RenderContext(0, 100, 100)
    font = MockFont() # type: ignore
    
    ctx = ui_begin(ctx)
    ctx, renderer, new_val = ui_slider(ctx, renderer, font, "slider1", Rect(0, 0, 100, 20), 0.0, 0.0, 10.0)
    
    assert new_val == 5.0 # (50-0)/100 * 10
    ctx = ui_end(ctx)
    assert ctx.active_item == "slider1" # still dragging
