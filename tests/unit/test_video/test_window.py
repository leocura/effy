import pytest
from typing import Any
from Effy._internal.registry import set_platform_adapter
from Effy.platform.headless import HeadlessAdapter
from Effy.video import (
    WindowFlags, create_window, destroy_window, set_window_title,
    set_window_size, set_window_position, minimize_window, maximize_window,
    restore_window, show_window, hide_window,
    get_num_video_displays, get_display_name, get_display_bounds, Rect
)
from Effy._internal.result import Ok

@pytest.fixture(autouse=True)
def setup_headless() -> Any:
    set_platform_adapter(HeadlessAdapter())
    yield
    set_platform_adapter(None)

def test_display_queries() -> None:
    # 1. Number of displays
    num_displays_effect = get_num_video_displays()
    num_displays = num_displays_effect.run()
    assert num_displays == 1

    # 2. Display Name
    name_effect = get_display_name(0)
    name = name_effect.run()
    assert name == "Headless Monitor"

    # 3. Display Bounds
    bounds_effect = get_display_bounds(0)
    bounds = bounds_effect.run()
    assert bounds == Rect(0, 0, 1920, 1080)

def test_window_lifecycle_and_actions() -> None:
    # 1. Create Window
    create_effect = create_window(
        title="Test Window",
        x=100, y=200,
        w=640, h=480,
        flags=WindowFlags.SHOWN
    )
    res = create_effect.run()
    assert isinstance(res, Ok)
    window = res.value
    assert window.title == "Test Window"
    assert window.x == 100
    assert window.y == 200
    assert window.w == 640
    assert window.h == 480
    assert window.flags == WindowFlags.SHOWN

    # 2. Set title
    title_effect = set_window_title(window, "New Title")
    window = title_effect.run()
    assert window.title == "New Title"

    # 3. Set size
    size_effect = set_window_size(window, 800, 600)
    window = size_effect.run()
    assert window.w == 800
    assert window.h == 600

    # 4. Set position
    pos_effect = set_window_position(window, 300, 400)
    window = pos_effect.run()
    assert window.x == 300
    assert window.y == 400

    # 5. Minimize
    min_effect = minimize_window(window)
    window = min_effect.run()
    assert WindowFlags.MINIMIZED in window.flags
    assert WindowFlags.MAXIMIZED not in window.flags

    # 6. Maximize
    max_effect = maximize_window(window)
    window = max_effect.run()
    assert WindowFlags.MAXIMIZED in window.flags
    assert WindowFlags.MINIMIZED not in window.flags

    # 7. Restore
    restore_effect = restore_window(window)
    window = restore_effect.run()
    assert WindowFlags.MINIMIZED not in window.flags
    assert WindowFlags.MAXIMIZED not in window.flags

    # 8. Hide
    hide_effect = hide_window(window)
    window = hide_effect.run()
    assert WindowFlags.HIDDEN in window.flags
    assert WindowFlags.SHOWN not in window.flags

    # 9. Show
    show_effect = show_window(window)
    window = show_effect.run()
    assert WindowFlags.SHOWN in window.flags
    assert WindowFlags.HIDDEN not in window.flags

    # 10. Destroy
    destroy_effect = destroy_window(window)
    destroy_effect.run()
