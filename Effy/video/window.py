from __future__ import annotations
from enum import IntFlag
from dataclasses import dataclass
from Effy.types import WindowID, Effect, Result, Ok, Err, WindowParams
from Effy.error import EffyError
from Effy._internal.registry import get_platform_adapter, register_window, unregister_window, get_window_handle, next_window_id

class WindowFlags(IntFlag):
    """Flags specifying window traits and states."""
    NONE = 0
    FULLSCREEN = 0x00000001
    OPENGL = 0x00000002
    SHOWN = 0x00000004
    HIDDEN = 0x00000008
    BORDERLESS = 0x00000010
    RESIZABLE = 0x00000020
    MINIMIZED = 0x00000040
    MAXIMIZED = 0x00000080
    MOUSE_GRABBED = 0x00000100
    INPUT_FOCUS = 0x00000200
    MOUSE_FOCUS = 0x00000400
    FOREIGN = 0x00000800
    ALLOW_HIGHDPI = 0x00002000
    MOUSE_CAPTURE = 0x00004000
    ALWAYS_ON_TOP = 0x00008000
    SKIP_TASKBAR = 0x00010000
    UTILITY = 0x00020000
    TOOLTIP = 0x00040000
    POPUP_MENU = 0x00080000
    KEYBOARD_GRABBED = 0x00100000
    VULKAN = 0x10000000
    METAL = 0x20000000

@dataclass(frozen=True, slots=True)
class Window:
    """An immutable representation of an SDL window.

    Attributes:
        id: Unique identifier for the window.
        title: The title text of the window.
        x: X-coordinate of the window position.
        y: Y-coordinate of the window position.
        w: Width of the window in pixels.
        h: Height of the window in pixels.
        flags: WindowFlags specifying active state configurations.
    """
    id: WindowID
    title: str
    x: int
    y: int
    w: int
    h: int
    flags: WindowFlags

def create_window(
    title: str,
    x: int, y: int,
    w: int, h: int,
    flags: WindowFlags,
) -> Effect[Result[Window, EffyError]]:
    """Create a new window and return an Effect that produces the Window or EffyError.

    Args:
        title: The title text for the window.
        x: The initial x position of the window.
        y: The initial y position of the window.
        w: The initial width of the window in pixels.
        h: The initial height of the window in pixels.
        flags: A combination of WindowFlags specifying attributes.

    Returns:
        An Effect wrapping a Result containing the created Window or an EffyError.
    """
    def _run() -> Result[Window, EffyError]:
        """Thunk that creates the window via the platform adapter."""
        adapter = get_platform_adapter()
        if not adapter:
            return Err(EffyError(code=-1, message="SDL not initialized"))

        params = WindowParams(title=title, x=x, y=y, w=w, h=h, flags=flags)
        res = adapter.create_window(params)
        if isinstance(res, Err):
            return res

        handle = res.value
        window_id = next_window_id()
        register_window(window_id, handle)

        return Ok(Window(id=window_id, title=title, x=x, y=y, w=w, h=h, flags=flags))

    return Effect(_run)

def destroy_window(window: Window) -> Effect[None]:
    """Destroy an existing window and release its platform-specific resources.

    Args:
        window: The Window object to destroy.

    Returns:
        An Effect that destroys the window when run.
    """
    def _run() -> None:
        """Thunk that destroys the window via the platform adapter."""
        adapter = get_platform_adapter()
        handle = get_window_handle(window.id)
        if adapter and handle:
            adapter.destroy_window(handle)
            unregister_window(window.id)
    return Effect(_run)

def set_window_title(window: Window, title: str) -> Effect[Window]:
    """Set the title text of the window.

    Args:
        window: The Window context object to update.
        title: The new title string.

    Returns:
        An Effect that yields the updated Window instance when run.
    """
    def _run() -> Window:
        """Thunk that updates the window's title via the platform adapter."""
        adapter = get_platform_adapter()
        handle = get_window_handle(window.id)
        if adapter and handle:
            adapter.set_window_title(handle, title)
        return Window(id=window.id, title=title, x=window.x, y=window.y, w=window.w, h=window.h, flags=window.flags)
    return Effect(_run)

def set_window_size(window: Window, w: int, h: int) -> Effect[Window]:
    """Set the size of a window programmatically.

    Args:
        window: The Window context object to update.
        w: The new width in pixels.
        h: The new height in pixels.

    Returns:
        An Effect that yields the updated Window instance when run.
    """
    def _run() -> Window:
        """Thunk that updates the window's size via the platform adapter."""
        adapter = get_platform_adapter()
        handle = get_window_handle(window.id)
        if adapter and handle:
            adapter.set_window_size(handle, w, h)
        return Window(
            id=window.id,
            title=window.title,
            x=window.x,
            y=window.y,
            w=w,
            h=h,
            flags=window.flags
        )
    return Effect(_run)

def set_window_position(window: Window, x: int, y: int) -> Effect[Window]:
    """Set the position of a window programmatically.

    Args:
        window: The Window context object to update.
        x: The new x-coordinate.
        y: The new y-coordinate.

    Returns:
        An Effect that yields the updated Window instance when run.
    """
    def _run() -> Window:
        """Thunk that updates the window's position via the platform adapter."""
        adapter = get_platform_adapter()
        handle = get_window_handle(window.id)
        if adapter and handle:
            adapter.set_window_position(handle, x, y)
        return Window(
            id=window.id,
            title=window.title,
            x=x,
            y=y,
            w=window.w,
            h=window.h,
            flags=window.flags
        )
    return Effect(_run)

def minimize_window(window: Window) -> Effect[Window]:
    """Minimize a window to an iconified state.

    Args:
        window: The Window context object to update.

    Returns:
        An Effect that yields the minimized Window instance when run.
    """
    def _run() -> Window:
        """Thunk that minimizes the window via the platform adapter."""
        adapter = get_platform_adapter()
        handle = get_window_handle(window.id)
        if adapter and handle:
            adapter.minimize_window(handle)
        new_flags = (window.flags | WindowFlags.MINIMIZED) & ~WindowFlags.MAXIMIZED
        return Window(
            id=window.id,
            title=window.title,
            x=window.x,
            y=window.y,
            w=window.w,
            h=window.h,
            flags=new_flags
        )
    return Effect(_run)

def maximize_window(window: Window) -> Effect[Window]:
    """Maximize a window to fill the screen.

    Args:
        window: The Window context object to update.

    Returns:
        An Effect that yields the maximized Window instance when run.
    """
    def _run() -> Window:
        """Thunk that maximizes the window via the platform adapter."""
        adapter = get_platform_adapter()
        handle = get_window_handle(window.id)
        if adapter and handle:
            adapter.maximize_window(handle)
        new_flags = (window.flags | WindowFlags.MAXIMIZED) & ~WindowFlags.MINIMIZED
        return Window(
            id=window.id,
            title=window.title,
            x=window.x,
            y=window.y,
            w=window.w,
            h=window.h,
            flags=new_flags
        )
    return Effect(_run)

def restore_window(window: Window) -> Effect[Window]:
    """Restore a minimized or maximized window to its original size and position.

    Args:
        window: The Window context object to update.

    Returns:
        An Effect that yields the restored Window instance when run.
    """
    def _run() -> Window:
        """Thunk that restores the window size and position via the platform adapter."""
        adapter = get_platform_adapter()
        handle = get_window_handle(window.id)
        if adapter and handle:
            adapter.restore_window(handle)
        new_flags = window.flags & ~(WindowFlags.MINIMIZED | WindowFlags.MAXIMIZED)
        return Window(
            id=window.id,
            title=window.title,
            x=window.x,
            y=window.y,
            w=window.w,
            h=window.h,
            flags=new_flags
        )
    return Effect(_run)

def show_window(window: Window) -> Effect[Window]:
    """Show a window that was previously hidden.

    Args:
        window: The Window context object to update.

    Returns:
        An Effect that yields the visible Window instance when run.
    """
    def _run() -> Window:
        """Thunk that shows the window via the platform adapter."""
        adapter = get_platform_adapter()
        handle = get_window_handle(window.id)
        if adapter and handle:
            adapter.show_window(handle)
        new_flags = (window.flags | WindowFlags.SHOWN) & ~WindowFlags.HIDDEN
        return Window(
            id=window.id,
            title=window.title,
            x=window.x,
            y=window.y,
            w=window.w,
            h=window.h,
            flags=new_flags
        )
    return Effect(_run)

def hide_window(window: Window) -> Effect[Window]:
    """Hide a window from view.

    Args:
        window: The Window context object to update.

    Returns:
        An Effect that yields the hidden Window instance when run.
    """
    def _run() -> Window:
        """Thunk that hides the window via the platform adapter."""
        adapter = get_platform_adapter()
        handle = get_window_handle(window.id)
        if adapter and handle:
            adapter.hide_window(handle)
        new_flags = (window.flags | WindowFlags.HIDDEN) & ~WindowFlags.SHOWN
        return Window(
            id=window.id,
            title=window.title,
            x=window.x,
            y=window.y,
            w=window.w,
            h=window.h,
            flags=new_flags
        )
    return Effect(_run)
