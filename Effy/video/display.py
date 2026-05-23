from __future__ import annotations
from Effy.types import Effect
from Effy.video.rect import Rect
from Effy._internal.registry import get_platform_adapter

def get_num_video_displays() -> Effect[int]:
    """Get the number of available video displays."""
    def _run() -> int:
        """Thunk implementing video display counting via the active platform adapter."""
        adapter = get_platform_adapter()
        if not adapter:
            return 1
        return adapter.get_num_video_displays()
    return Effect(_run)

def get_display_name(display_index: int) -> Effect[str]:
    """Get the name of a display."""
    def _run() -> str:
        """Thunk retrieving the display name from the active platform adapter."""
        adapter = get_platform_adapter()
        if not adapter:
            return "Default Display"
        return adapter.get_display_name(display_index)
    return Effect(_run)

def get_display_bounds(display_index: int) -> Effect[Rect]:
    """Get the bounds of a display as a Rect."""
    def _run() -> Rect:
        """Thunk retrieving display bounds Rect from the active platform adapter."""
        adapter = get_platform_adapter()
        if not adapter:
            return Rect(0, 0, 1920, 1080)
        return adapter.get_display_bounds(display_index)
    return Effect(_run)
