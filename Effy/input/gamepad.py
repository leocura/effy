"""Gamepad and Game Controller snapshot state representation and mapping logic."""
from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from Effy._internal.fp import pure


class GamepadButton(IntEnum):
    """Buttons on a standard gamepad/controller."""

    INVALID = -1
    A = 0
    B = 1
    X = 2
    Y = 3
    BACK = 4
    GUIDE = 5
    START = 6
    LEFT_STICK = 7
    RIGHT_STICK = 8
    LEFT_SHOULDER = 9
    RIGHT_SHOULDER = 10
    DPAD_UP = 11
    DPAD_DOWN = 12
    DPAD_LEFT = 13
    DPAD_RIGHT = 14
    MISC1 = 15
    PADDLE1 = 16
    PADDLE2 = 17
    PADDLE3 = 18
    PADDLE4 = 19
    TOUCHPAD = 20


class GamepadAxis(IntEnum):
    """Axes on a standard gamepad/controller."""

    INVALID = -1
    LEFTX = 0
    LEFTY = 1
    RIGHTX = 2
    RIGHTY = 3
    TRIGGERLEFT = 4
    TRIGGERRIGHT = 5


@dataclass(frozen=True, slots=True)
class GamepadDeviceState:
    """Represents a frozen snapshot of a single gamepad's state."""

    device_id: int
    name: str
    pressed_buttons: frozenset[GamepadButton]
    axes: frozenset[tuple[GamepadAxis, float]]

    @pure
    def is_pressed(self, button: GamepadButton) -> bool:
        """Check if a specific button is currently pressed.

        Args:
            button: The GamepadButton enum to check.

        Returns:
            True if pressed, False otherwise.
        """
        return button in self.pressed_buttons

    @pure
    def get_axis(self, axis: GamepadAxis) -> float:
        """Get the value of a specific axis.

        Args:
            axis: The GamepadAxis enum to retrieve.

        Returns:
            The normalized value between -1.0 and 1.0 (or 0.0 and 1.0 for triggers).
        """
        for a, val in self.axes:
            if a == axis:
                return val
        return 0.0


@dataclass(frozen=True, slots=True)
class GamepadState:
    """Represents a snapshot of all active gamepad states."""

    devices: frozenset[GamepadDeviceState]

    @pure
    def get_device(self, device_id: int) -> GamepadDeviceState | None:
        """Retrieve the state of a specific gamepad by its device ID.

        Args:
            device_id: The ID of the gamepad device.

        Returns:
            The GamepadDeviceState instance if found, or None.
        """
        for dev in self.devices:
            if dev.device_id == device_id:
                return dev
        return None


def parse_gamecontrollerdb(content: str) -> dict[str, tuple[str, str, dict[str, str]]]:
    """Parse a gamecontrollerdb format string into a dictionary of mappings.

    Args:
        content: The text content of the database.

    Returns:
        A dictionary mapping GUID strings to tuples of (name, platform, mappings).
    """
    mappings: dict[str, tuple[str, str, dict[str, str]]] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(",")
        if len(parts) < 3:
            continue
        guid = parts[0].strip()
        name = parts[1].strip()
        platform = "unknown"
        mapping_dict: dict[str, str] = {}
        for part in parts[2:]:
            part = part.strip()
            if not part:
                continue
            if ":" not in part:
                continue
            k, v = part.split(":", 1)
            k = k.strip()
            v = v.strip()
            if k == "platform":
                platform = v
            else:
                mapping_dict[k] = v
        mappings[guid] = (name, platform, mapping_dict)
    return mappings


def map_hardware_to_gamepad(
    mapping: dict[str, str],
    raw_buttons: frozenset[int],
    raw_axes: dict[int, float],
    raw_hats: dict[int, int]
) -> tuple[frozenset[GamepadButton], frozenset[tuple[GamepadAxis, float]]]:
    """Translate raw controller inputs into standardized Gamepad buttons and axes.

    Args:
        mapping: The parsed mapping dictionary for this gamepad.
        raw_buttons: A set of pressed hardware button indices.
        raw_axes: A dictionary of current raw hardware axis index -> float values.
        raw_hats: A dictionary of current raw hardware hat index -> int values.

    Returns:
        A tuple of (frozenset of pressed GamepadButtons, frozenset of GamepadAxis tuples).
    """
    pressed: set[GamepadButton] = set()
    axes_vals: dict[GamepadAxis, float] = {}

    button_str_map = {
        "a": GamepadButton.A,
        "b": GamepadButton.B,
        "x": GamepadButton.X,
        "y": GamepadButton.Y,
        "back": GamepadButton.BACK,
        "guide": GamepadButton.GUIDE,
        "start": GamepadButton.START,
        "leftstick": GamepadButton.LEFT_STICK,
        "rightstick": GamepadButton.RIGHT_STICK,
        "leftshoulder": GamepadButton.LEFT_SHOULDER,
        "rightshoulder": GamepadButton.RIGHT_SHOULDER,
        "dpup": GamepadButton.DPAD_UP,
        "dpdown": GamepadButton.DPAD_DOWN,
        "dpleft": GamepadButton.DPAD_LEFT,
        "dpright": GamepadButton.DPAD_RIGHT,
        "misc1": GamepadButton.MISC1,
        "paddle1": GamepadButton.PADDLE1,
        "paddle2": GamepadButton.PADDLE2,
        "paddle3": GamepadButton.PADDLE3,
        "paddle4": GamepadButton.PADDLE4,
        "touchpad": GamepadButton.TOUCHPAD,
    }

    axis_str_map = {
        "leftx": GamepadAxis.LEFTX,
        "lefty": GamepadAxis.LEFTY,
        "rightx": GamepadAxis.RIGHTX,
        "righty": GamepadAxis.RIGHTY,
        "lefttrigger": GamepadAxis.TRIGGERLEFT,
        "righttrigger": GamepadAxis.TRIGGERRIGHT,
    }

    for std_key, hw_val in mapping.items():
        # Handle buttons
        if std_key in button_str_map:
            btn = button_str_map[std_key]
            if hw_val.startswith("b"):
                try:
                    b_idx = int(hw_val[1:])
                    if b_idx in raw_buttons:
                        pressed.add(btn)
                except ValueError:
                    pass
            elif hw_val.startswith("h"):
                try:
                    hat_parts = hw_val[1:].split(".")
                    h_idx = int(hat_parts[0])
                    h_val = int(hat_parts[1])
                    if raw_hats.get(h_idx, 0) & h_val:
                        pressed.add(btn)
                except (ValueError, IndexError):
                    pass
            elif hw_val.startswith("a") or hw_val.startswith("+a") or hw_val.startswith("-a"):
                try:
                    a_sign = 1
                    a_str = hw_val
                    if hw_val.startswith("+"):
                        a_str = hw_val[1:]
                    elif hw_val.startswith("-"):
                        a_sign = -1
                        a_str = hw_val[1:]
                    a_idx = int(a_str[1:])
                    val = raw_axes.get(a_idx, 0.0) * a_sign
                    if val > 0.5:
                        pressed.add(btn)
                except ValueError:
                    pass

        # Handle axes
        elif std_key in axis_str_map:
            ax = axis_str_map[std_key]
            if hw_val.startswith("a") or hw_val.startswith("+a") or hw_val.startswith("-a"):
                try:
                    a_sign = 1
                    a_str = hw_val
                    if hw_val.startswith("+"):
                        a_str = hw_val[1:]
                    elif hw_val.startswith("-"):
                        a_sign = -1
                        a_str = hw_val[1:]
                    a_idx = int(a_str[1:])
                    axes_vals[ax] = raw_axes.get(a_idx, 0.0) * a_sign
                except ValueError:
                    pass
            elif hw_val.startswith("b"):
                try:
                    b_idx = int(hw_val[1:])
                    axes_vals[ax] = 1.0 if b_idx in raw_buttons else 0.0
                except ValueError:
                    pass

    return frozenset(pressed), frozenset(axes_vals.items())
