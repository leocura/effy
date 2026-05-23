from __future__ import annotations
from typing import TYPE_CHECKING, Dict
from Effy.types import WindowID, TextureID

import threading

if TYPE_CHECKING:
    from Effy.platform import PlatformAdapter, PlatformWindowHandle

_active_adapter: PlatformAdapter | None = None
_window_registry: Dict[WindowID, PlatformWindowHandle] = {}
_active_timers: Dict[int, threading.Event] = {}
_timer_counter: int = 0
_window_counter: int = 0
_texture_counter: int = 0
_lock = threading.Lock()

def set_platform_adapter(adapter: PlatformAdapter | None) -> None:
    """Set the active platform adapter.

    Args:
        adapter: The active platform-specific adapter instance (e.g. X11 or Win32).
    """
    global _active_adapter
    with _lock:
        _active_adapter = adapter

def get_platform_adapter() -> PlatformAdapter | None:
    """Retrieve the active platform adapter.

    Returns:
        The active platform adapter instance, or None if not set.
    """
    with _lock:
        return _active_adapter

def next_window_id() -> WindowID:
    """Generate a unique, thread-safe monotonic WindowID."""
    global _window_counter
    with _lock:
        _window_counter += 1
        return WindowID(_window_counter)

def next_texture_id() -> TextureID:
    """Generate a unique, thread-safe monotonic TextureID."""
    global _texture_counter
    with _lock:
        _texture_counter += 1
        return TextureID(_texture_counter)

def register_window(window_id: WindowID, handle: PlatformWindowHandle) -> None:
    """Register a window handle associated with a window ID in a thread-safe manner.

    Args:
        window_id: The unique identifier of the window.
        handle: The platform-specific window handle.
    """
    with _lock:
        _window_registry[window_id] = handle

def unregister_window(window_id: WindowID) -> None:
    """Remove a window from the global registry.

    Args:
        window_id: The unique identifier of the window to unregister.
    """
    with _lock:
        if window_id in _window_registry:
            del _window_registry[window_id]

def get_window_handle(window_id: WindowID) -> PlatformWindowHandle | None:
    """Retrieve a platform-specific window handle by its window ID.

    Args:
        window_id: The unique identifier of the window.

    Returns:
        The window handle, or None if the window is not registered.
    """
    with _lock:
        return _window_registry.get(window_id)

def register_timer(cancel_event: threading.Event) -> int:
    """Register an active timer event and return a thread-safe incremented timer ID.

    Args:
        cancel_event: The threading.Event used to cancel the timer.

    Returns:
        A unique, newly generated integer timer ID.
    """
    global _timer_counter
    with _lock:
        _timer_counter += 1
        _active_timers[_timer_counter] = cancel_event
        return _timer_counter

def unregister_timer(timer_id: int) -> None:
    """Remove a timer from the active timers registry.

    Args:
        timer_id: The integer ID of the timer to unregister.
    """
    with _lock:
        if timer_id in _active_timers:
            del _active_timers[timer_id]

def get_timer_cancel_event(timer_id: int) -> threading.Event | None:
    """Retrieve the cancellation event for an active timer.

    Args:
        timer_id: The unique ID of the timer.

    Returns:
        The cancel Event, or None if not found.
    """
    with _lock:
        return _active_timers.get(timer_id)
