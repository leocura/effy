"""Keyboard input state snapshot representation."""
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from Effy._internal.fp import pure

if TYPE_CHECKING:
    from Effy.events.types import Scancode


@dataclass(frozen=True, slots=True)
class KeyboardState:
    """Represents a frozen snapshot of the keyboard state.

    Attributes:
        pressed_keys: A frozen set of currently pressed keyboard scancodes.
    """

    pressed_keys: frozenset[Scancode]

    @pure
    def is_pressed(self, scancode: Scancode) -> bool:
        """Check if a specific scancode is currently pressed.

        Args:
            scancode: The scancode to check.

        Returns:
            True if the key is pressed, False otherwise.
        """
        return scancode in self.pressed_keys
