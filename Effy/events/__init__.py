from __future__ import annotations
from Effy.types import Effect
from .types import (
    Event, QuitEvent, KeyDownEvent, KeyUpEvent, MouseMotionEvent,
    Scancode, Keycode, KeyMod, MouseButton, WindowEvent, WindowEventID, MouseWheelEvent,
    FingerDownEvent, FingerUpEvent, FingerMotionEvent,
    ControllerAxisEvent, ControllerButtonEvent, ControllerDeviceEvent,
    SensorUpdateEvent
)
from .queue import EventQueue
from Effy._internal.registry import get_platform_adapter

def poll_event() -> Effect[Event | None]:
    """Poll for currently pending events."""
    def _run() -> Event | None:
        """Thunk implementing platform event polling logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return None
        return adapter.poll_event()
    return Effect(_run)

def pump_events() -> Effect[None]:
    """Pumps the event loop, gathering events from the platform."""
    def _run() -> None:
        """Thunk implementing platform event loop pumping logic."""
        adapter = get_platform_adapter()
        if adapter:
            adapter.pump_events()
    return Effect(_run)

def wait_event(timeout_ms: int = 0) -> Effect[Event | None]:
    """Waits until the next event is available."""
    def _run() -> Event | None:
        """Thunk implementing platform event blocking wait logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return None
        return adapter.wait_event(timeout_ms)
    return Effect(_run)

__all__ = [
    "Event", "QuitEvent", "KeyDownEvent", "KeyUpEvent", "MouseMotionEvent",
    "Scancode", "Keycode", "KeyMod", "MouseButton",
    "WindowEvent", "WindowEventID", "MouseWheelEvent",
    "FingerDownEvent", "FingerUpEvent", "FingerMotionEvent",
    "ControllerAxisEvent", "ControllerButtonEvent", "ControllerDeviceEvent",
    "SensorUpdateEvent",
    "EventQueue",
    "poll_event", "pump_events", "wait_event"
]
