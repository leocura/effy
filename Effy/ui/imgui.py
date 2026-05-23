from __future__ import annotations
from dataclasses import dataclass
from typing import cast
from Effy.video.rect import Rect, Point, point_in_rect
from Effy.render.renderer import RenderContext, render_set_draw_color, render_fill_rect, render_text
from Effy.video.font import BitmapFont
from Effy._internal.fp import _EVOLVE_SENTINEL, pure


@dataclass(frozen=True, slots=True)
class UIState:
    """Immutable state container for an Immediate Mode GUI (IMGUI)."""
    mouse_pos: Point
    mouse_down: bool
    hot_item: str | None = None
    active_item: str | None = None

    def evolve(self, mouse_pos: Point | object = _EVOLVE_SENTINEL,
               mouse_down: bool | object = _EVOLVE_SENTINEL,
               hot_item: str | None | object = _EVOLVE_SENTINEL,
               active_item: str | None | object = _EVOLVE_SENTINEL) -> UIState:
        return UIState(
            self.mouse_pos if mouse_pos is _EVOLVE_SENTINEL else cast(Point, mouse_pos),
            self.mouse_down if mouse_down is _EVOLVE_SENTINEL else cast(bool, mouse_down),
            self.hot_item if hot_item is _EVOLVE_SENTINEL else cast(str | None, hot_item),
            self.active_item if active_item is _EVOLVE_SENTINEL else cast(str | None, active_item),
        )


@pure
def ui_begin(state: UIState) -> UIState:
    """Begin a new UI frame, clearing the hot item."""
    return state.evolve(hot_item=None)


@pure
def ui_end(state: UIState) -> UIState:
    """End a UI frame, resolving active state changes from mouse up."""
    if not state.mouse_down:
        return state.evolve(active_item=None)
    elif state.active_item is None:
        # Prevent clicking on empty space from grabbing focus later
        return state.evolve(active_item="")
    return state


@pure
def ui_button(state: UIState, renderer: RenderContext, font: BitmapFont, id_str: str, rect: Rect, text: str) -> tuple[UIState, RenderContext, bool]:
    """A functional push button widget.
    
    Returns:
        A tuple of (Evolved UIState, Evolved RenderContext, clicked boolean).
    """
    new_state = state
    clicked = False

    if point_in_rect(state.mouse_pos, rect):
        new_state = new_state.evolve(hot_item=id_str)
        if state.active_item is None and state.mouse_down:
            new_state = new_state.evolve(active_item=id_str)

    if not state.mouse_down and new_state.hot_item == id_str and new_state.active_item == id_str:
        clicked = True

    bg_color = (100, 100, 100)
    if new_state.hot_item == id_str:
        if new_state.active_item == id_str:
            bg_color = (60, 60, 60)
        else:
            bg_color = (140, 140, 140)

    renderer = render_set_draw_color(renderer, *bg_color)
    renderer = render_fill_rect(renderer, rect)
    
    text_width = len(text) * font.glyph_width
    text_x = rect.x + (rect.w - text_width) // 2
    text_y = rect.y + (rect.h - font.glyph_height) // 2
    
    renderer = render_set_draw_color(renderer, 255, 255, 255)
    renderer = render_text(renderer, font, text, text_x, text_y)
    
    return new_state, renderer, clicked


@pure
def ui_slider(state: UIState, renderer: RenderContext, font: BitmapFont, id_str: str, rect: Rect, value: float, min_val: float, max_val: float) -> tuple[UIState, RenderContext, float]:
    """A functional slider widget.
    
    Returns:
        A tuple of (Evolved UIState, Evolved RenderContext, new value float).
    """
    new_state = state
    
    if point_in_rect(state.mouse_pos, rect):
        new_state = new_state.evolve(hot_item=id_str)
        if state.active_item is None and state.mouse_down:
            new_state = new_state.evolve(active_item=id_str)
            
    new_val = value
    if new_state.active_item == id_str:
        ratio = (state.mouse_pos.x - rect.x) / float(rect.w)
        ratio = max(0.0, min(1.0, ratio))
        new_val = min_val + ratio * (max_val - min_val)

    bg_color = (80, 80, 80)
    renderer = render_set_draw_color(renderer, *bg_color)
    renderer = render_fill_rect(renderer, rect)
    
    fill_w = int(((new_val - min_val) / (max_val - min_val)) * rect.w) if max_val > min_val else 0
    fg_color = (120, 120, 180)
    if new_state.hot_item == id_str or new_state.active_item == id_str:
        fg_color = (140, 140, 200)
        
    renderer = render_set_draw_color(renderer, *fg_color)
    renderer = render_fill_rect(renderer, Rect(rect.x, rect.y, fill_w, rect.h))
    
    text = f"{new_val:.2f}"
    text_width = len(text) * font.glyph_width
    text_x = rect.x + (rect.w - text_width) // 2
    text_y = rect.y + (rect.h - font.glyph_height) // 2
    
    renderer = render_set_draw_color(renderer, 255, 255, 255)
    renderer = render_text(renderer, font, text, text_x, text_y)
    
    return new_state, renderer, new_val
