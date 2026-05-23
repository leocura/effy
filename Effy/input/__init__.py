from __future__ import annotations
from Effy.types import Effect
from Effy._internal.registry import get_platform_adapter
from .keyboard import KeyboardState
from .mouse import MouseState
from .touch import Finger, TouchDeviceState, TouchState
from .gamepad import (
    GamepadButton, GamepadAxis, GamepadDeviceState, GamepadState,
    parse_gamecontrollerdb, map_hardware_to_gamepad
)
from .sensors import SensorType, SensorDeviceState, SensorState
from .haptics import (
    HapticEffect, HapticDevice, open_haptic_device, close_haptic_device,
    is_haptic_rumble_supported, play_haptic_rumble, stop_haptic_rumble,
    upload_haptic_effect, run_haptic_effect, stop_haptic_effect, destroy_haptic_effect
)


def get_keyboard_state() -> Effect[KeyboardState]:
    """Get a snapshot of the current keyboard state."""
    def _run() -> KeyboardState:
        """Thunk implementing platform keyboard state snapshot logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return KeyboardState(pressed_keys=frozenset())
        return adapter.get_keyboard_state()
    return Effect(_run)

def get_mouse_state() -> Effect[MouseState]:
    """Get a snapshot of the current mouse state."""
    def _run() -> MouseState:
        """Thunk implementing platform mouse state snapshot logic."""
        adapter = get_platform_adapter()
        if not adapter:
            from Effy.events.types import MouseButton
            return MouseState(x=0, y=0, buttons=MouseButton.NONE)
        return adapter.get_mouse_state()
    return Effect(_run)

def get_touch_state() -> Effect[TouchState]:
    """Get a snapshot of the current touch state."""
    def _run() -> TouchState:
        """Thunk implementing platform touch input snapshot logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return TouchState(devices=frozenset())
        return adapter.get_touch_state()
    return Effect(_run)

def get_gamepad_state() -> Effect[GamepadState]:
    """Get a snapshot of the current gamepad state."""
    def _run() -> GamepadState:
        """Thunk implementing platform gamepad device snapshot logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return GamepadState(devices=frozenset())
        return adapter.get_gamepad_state()
    return Effect(_run)

def get_sensor_state() -> Effect[SensorState]:
    """Get a snapshot of the current sensor state."""
    def _run() -> SensorState:
        """Thunk implementing platform sensor snapshot logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return SensorState(devices=frozenset())
        return adapter.get_sensor_state()
    return Effect(_run)

__all__ = [
    "KeyboardState", "MouseState",
    "Finger", "TouchDeviceState", "TouchState",
    "GamepadButton", "GamepadAxis", "GamepadDeviceState", "GamepadState",
    "parse_gamecontrollerdb", "map_hardware_to_gamepad",
    "SensorType", "SensorDeviceState", "SensorState",
    "HapticEffect", "HapticDevice",
    "get_keyboard_state", "get_mouse_state", "get_touch_state",
    "get_gamepad_state", "get_sensor_state",
    "open_haptic_device", "close_haptic_device",
    "is_haptic_rumble_supported", "play_haptic_rumble", "stop_haptic_rumble",
    "upload_haptic_effect", "run_haptic_effect", "stop_haptic_effect", "destroy_haptic_effect"
]
