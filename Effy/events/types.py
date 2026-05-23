from __future__ import annotations
from dataclasses import dataclass
from typing import NewType, TYPE_CHECKING
from enum import IntFlag, IntEnum
from Effy.types import WindowID

if TYPE_CHECKING:
    from Effy.input.gamepad import GamepadAxis, GamepadButton
    from Effy.input.sensors import SensorType


Scancode = NewType("Scancode", int)
Keycode = NewType("Keycode", int)

class KeyMod(IntFlag):
    """Flags specifying active keyboard modifier states (e.g. Ctrl, Shift, Alt)."""
    NONE = 0x0000
    LSHIFT = 0x0001
    RSHIFT = 0x0002
    LCTRL = 0x0040
    RCTRL = 0x0080
    LALT = 0x0100
    RALT = 0x0200
    LGUI = 0x0400
    RGUI = 0x0800
    NUM = 0x1000
    CAPS = 0x2000
    MODE = 0x4000
    SCROLL = 0x8000

    CTRL = LCTRL | RCTRL
    SHIFT = LSHIFT | RSHIFT
    ALT = LALT | RALT
    GUI = LGUI | RGUI


class MouseButton(IntFlag):
    """Flags specifying active mouse button states."""
    NONE = 0
    LEFT = 1 << 0
    MIDDLE = 1 << 1
    RIGHT = 1 << 2
    X1 = 1 << 3
    X2 = 1 << 4


@dataclass(frozen=True, slots=True)
class QuitEvent:
    """An event indicating that the user requested to quit the application.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
    """
    timestamp: int


@dataclass(frozen=True, slots=True)
class KeyDownEvent:
    """An event indicating a key was pressed down.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        window_id: The ID of the window with keyboard focus.
        scancode: The hardware scancode of the pressed key.
        keycode: The virtual keycode representation of the pressed key.
        mod: Active modifier keys (e.g. Ctrl, Alt).
        repeat: True if this is a key repeat event, False otherwise.
    """
    timestamp: int
    window_id: WindowID
    scancode: Scancode
    keycode: Keycode
    mod: KeyMod
    repeat: bool


@dataclass(frozen=True, slots=True)
class KeyUpEvent:
    """An event indicating a key was released.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        window_id: The ID of the window with keyboard focus.
        scancode: The hardware scancode of the released key.
        keycode: The virtual keycode representation of the released key.
        mod: Active modifier keys (e.g. Ctrl, Alt).
    """
    timestamp: int
    window_id: WindowID
    scancode: Scancode
    keycode: Keycode
    mod: KeyMod


@dataclass(frozen=True, slots=True)
class MouseMotionEvent:
    """An event indicating the mouse cursor was moved.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        window_id: The ID of the window with mouse focus.
        x: The absolute x-coordinate relative to the window.
        y: The absolute y-coordinate relative to the window.
        xrel: Relative x-axis motion since the last event.
        yrel: Relative y-axis motion since the last event.
        buttons: MouseButton flags representing currently held buttons.
    """
    timestamp: int
    window_id: WindowID
    x: int
    y: int
    xrel: int
    yrel: int
    buttons: MouseButton


class WindowEventID(IntEnum):
    """Identifications for specific types of window events."""
    NONE = 0
    SHOWN = 1
    HIDDEN = 2
    EXPOSED = 3
    MOVED = 4
    RESIZED = 5
    SIZE_CHANGED = 6
    MINIMIZED = 7
    MAXIMIZED = 8
    RESTORED = 9
    ENTER = 10
    LEAVE = 11
    FOCUS_GAINED = 12
    FOCUS_LOST = 13
    CLOSE = 14
    TAKE_FOCUS = 15
    HIT_TEST = 16


@dataclass(frozen=True, slots=True)
class WindowEvent:
    """An event reporting window state changes.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        window_id: The ID of the affected window.
        event_id: The WindowEventID detailing the specific window state change.
        data1: Event-specific metadata (e.g. new width on resize).
        data2: Event-specific metadata (e.g. new height on resize).
    """
    timestamp: int
    window_id: WindowID
    event_id: WindowEventID
    data1: int
    data2: int


@dataclass(frozen=True, slots=True)
class MouseWheelEvent:
    """An event indicating the mouse wheel was scrolled.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        window_id: The ID of the window with mouse focus.
        which: The mouse device index.
        x: Horizontal scroll amount (positive to the right).
        y: Vertical scroll amount (positive away from user).
        direction: Direction of scroll (0 for normal, 1 for flipped).
        precise_x: High-precision horizontal scroll float.
        precise_y: High-precision vertical scroll float.
    """
    timestamp: int
    window_id: WindowID
    which: int
    x: int
    y: int
    direction: int
    precise_x: float
    precise_y: float


@dataclass(frozen=True, slots=True)
class FingerDownEvent:
    """Event triggered when a finger touches a touch-sensitive device.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        touch_id: The unique ID of the touch device.
        finger_id: The unique ID of the finger within the touch session.
        x: Normalized horizontal coordinate from 0.0 to 1.0.
        y: Normalized vertical coordinate from 0.0 to 1.0.
        dx: Normalized relative horizontal displacement.
        dy: Normalized relative vertical displacement.
        pressure: Normalized pressure value from 0.0 to 1.0.
    """

    timestamp: int
    touch_id: int
    finger_id: int
    x: float
    y: float
    dx: float
    dy: float
    pressure: float


@dataclass(frozen=True, slots=True)
class FingerUpEvent:
    """Event triggered when a finger is lifted from a touch-sensitive device.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        touch_id: The unique ID of the touch device.
        finger_id: The unique ID of the finger within the touch session.
        x: Normalized horizontal coordinate from 0.0 to 1.0.
        y: Normalized vertical coordinate from 0.0 to 1.0.
        dx: Normalized relative horizontal displacement.
        dy: Normalized relative vertical displacement.
        pressure: Normalized pressure value from 0.0 to 1.0.
    """

    timestamp: int
    touch_id: int
    finger_id: int
    x: float
    y: float
    dx: float
    dy: float
    pressure: float


@dataclass(frozen=True, slots=True)
class FingerMotionEvent:
    """Event triggered when a finger moves on a touch-sensitive device.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        touch_id: The unique ID of the touch device.
        finger_id: The unique ID of the finger within the touch session.
        x: Normalized horizontal coordinate from 0.0 to 1.0.
        y: Normalized vertical coordinate from 0.0 to 1.0.
        dx: Normalized relative horizontal displacement.
        dy: Normalized relative vertical displacement.
        pressure: Normalized pressure value from 0.0 to 1.0.
    """

    timestamp: int
    touch_id: int
    finger_id: int
    x: float
    y: float
    dx: float
    dy: float
    pressure: float


@dataclass(frozen=True, slots=True)
class ControllerAxisEvent:
    """Event triggered when a game controller axis moves.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        which: The joystick device index.
        axis: The GamepadAxis enum detailing the affected axis.
        value: Normalized float value of the axis.
    """

    timestamp: int
    which: int
    axis: GamepadAxis
    value: float


@dataclass(frozen=True, slots=True)
class ControllerButtonEvent:
    """Event triggered when a game controller button is pressed or released.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        which: The joystick device index.
        button: The GamepadButton enum detailing the button.
        state: True if pressed, False if released.
    """

    timestamp: int
    which: int
    button: GamepadButton
    state: bool


@dataclass(frozen=True, slots=True)
class ControllerDeviceEvent:
    """Event triggered when a game controller device is added or removed.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        which: The joystick device index.
        is_added: True if the device was added, False if removed.
    """

    timestamp: int
    which: int
    is_added: bool


@dataclass(frozen=True, slots=True)
class SensorUpdateEvent:
    """Event triggered when a sensor updates its reading.

    Attributes:
        timestamp: Millisecond timestamp of when the event occurred.
        which: The ID of the sensor device.
        type: The type of the sensor.
        data: The 3-axis sensor data reading.
    """

    timestamp: int
    which: int
    type: SensorType
    data: tuple[float, float, float]


Event = (
    QuitEvent
    | KeyDownEvent
    | KeyUpEvent
    | MouseMotionEvent
    | WindowEvent
    | MouseWheelEvent
    | FingerDownEvent
    | FingerUpEvent
    | FingerMotionEvent
    | ControllerAxisEvent
    | ControllerButtonEvent
    | ControllerDeviceEvent
    | SensorUpdateEvent
)
