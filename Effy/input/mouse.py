"""Mouse input state snapshot representation."""
from __future__ import annotations
from dataclasses import dataclass
from Effy.events.types import MouseButton
from Effy._internal.fp import pure


@dataclass(frozen=True, slots=True)
class MouseState:
    """Represents a frozen snapshot of the mouse state.

    Attributes:
        x: Absolute horizontal coordinate relative to the active window.
        y: Absolute vertical coordinate relative to the active window.
        buttons: Combined flag representing all currently pressed mouse buttons.
    """

    x: int
    y: int
    buttons: MouseButton

    @pure
    def is_button_pressed(self, button: MouseButton) -> bool:
        """Check if a specific mouse button is currently pressed.

        Args:
            button: The MouseButton flags to query.

        Returns:
            True if the button is pressed, False otherwise.
        """
        return bool(self.buttons & button)
