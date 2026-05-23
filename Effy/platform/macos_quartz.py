from __future__ import annotations
import sys
from Effy._internal.result import Ok, Err, Result
from Effy.error import EffyError

from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from Effy.platform import PlatformHapticHandle

class MacOSQuartzAdapter:
    """macOS Quartz Platform Adapter.
    
    TODO: Implement direct interaction with Objective-C runtime via ctypes.
    """
    
    def __init__(self) -> None:
        """Initialize the macOS Quartz adapter."""
        self._clipboard_text: str = ""
        self._clipboard_data: dict[str, bytes] = {}

    @classmethod
    def detect(cls) -> bool:
        """Detect whether the current platform is macOS."""
        return sys.platform == "darwin"

    def init_video(self) -> Result[Any, EffyError]:
        """Initialize macOS Quartz video subsystem (stub)."""
        # TODO: Equivalent to SDL_Init(SDL_INIT_VIDEO)
        return Err(EffyError(code=-1, message="macOS Quartz adapter not implemented"))

    def quit_video(self, handle: Any) -> None:
        """Shut down the macOS Quartz video subsystem (stub)."""
        # TODO: Equivalent to SDL_QuitSubSystem(SDL_INIT_VIDEO)
        pass

    def create_window(self, params: Any) -> Result[Any, EffyError]:
        """Create a native macOS window (stub)."""
        # TODO: Equivalent to SDL_CreateWindow
        return Err(EffyError(code=-1, message="macOS Quartz adapter not implemented"))

    def destroy_window(self, handle: Any) -> None:
        """Destroy a native macOS window (stub)."""
        # TODO: Equivalent to SDL_DestroyWindow
        pass

    def set_window_title(self, handle: Any, title: str) -> None:
        """Set the title of a macOS window (stub)."""
        # TODO: Equivalent to SDL_SetWindowTitle
        raise NotImplementedError("macOS Quartz adapter not implemented")

    def flip_buffer(self, handle: Any, buf: Any) -> None:
        """Flip the window surface buffer to the screen (stub)."""
        # TODO: Equivalent to SDL_UpdateWindowSurface
        pass

    def poll_event(self) -> Any | None:
        """Poll for a pending macOS event without blocking (stub)."""
        # TODO: Equivalent to SDL_PollEvent
        return None

    def wait_event(self, timeout_ms: int) -> Any | None:
        """Wait for a macOS event with a timeout in milliseconds (stub)."""
        # TODO: Equivalent to SDL_WaitEvent
        return None

    def pump_events(self) -> None:
        """Pump the macOS event loop to gather pending events (stub)."""
        # TODO: Equivalent to SDL_PumpEvents
        pass

    def open_audio(self, spec: Any) -> Result[Any, EffyError]:
        """Open a macOS CoreAudio device (stub)."""
        # TODO: Implement pure Python audio via CoreAudio
        return Err(EffyError(code=-1, message="macOS Quartz adapter not implemented"))

    def write_audio(self, handle: Any, data: bytes) -> None:
        """Write audio data to an open CoreAudio device (stub)."""
        pass

    def close_audio(self, handle: Any) -> None:
        """Close an open CoreAudio device (stub)."""
        pass

    def get_num_video_displays(self) -> int:
        """Return the number of connected video displays (stub, always 1)."""
        return 1

    def get_display_name(self, index: int) -> str:
        """Return the name of the display at the given index (stub)."""
        return "macOS Monitor"

    def get_display_bounds(self, index: int) -> Any:
        """Return the bounding rectangle of the display at the given index (stub)."""
        from Effy.video.rect import Rect
        return Rect(0, 0, 1920, 1080)

    def set_window_size(self, handle: Any, w: int, h: int) -> None:
        """Set the size of a macOS window (stub)."""
        pass

    def set_window_position(self, handle: Any, x: int, y: int) -> None:
        """Set the position of a macOS window (stub)."""
        pass

    def minimize_window(self, handle: Any) -> None:
        """Minimize a macOS window (stub)."""
        pass

    def maximize_window(self, handle: Any) -> None:
        """Maximize a macOS window (stub)."""
        pass

    def restore_window(self, handle: Any) -> None:
        """Restore a macOS window from minimized or maximized state (stub)."""
        pass

    def show_window(self, handle: Any) -> None:
        """Show a hidden macOS window (stub)."""
        pass

    def hide_window(self, handle: Any) -> None:
        """Hide the window."""
        pass

    def get_keyboard_state(self) -> Any:
        """Retrieve current keyboard snapshot."""
        from Effy.input.keyboard import KeyboardState
        return KeyboardState(pressed_keys=frozenset())

    def get_mouse_state(self) -> Any:
        """Retrieve current mouse snapshot."""
        from Effy.input.mouse import MouseState
        from Effy.events.types import MouseButton
        return MouseState(x=0, y=0, buttons=MouseButton.NONE)

    def get_touch_state(self) -> Any:
        """Retrieve current touch snapshot."""
        from Effy.input.touch import TouchState
        return TouchState(devices=frozenset())

    def get_gamepad_state(self) -> Any:
        """Retrieve current gamepad snapshot state."""
        from Effy.input.gamepad import GamepadState
        return GamepadState(devices=frozenset())

    def get_sensor_state(self) -> Any:
        """Retrieve current sensor snapshot state."""
        from Effy.input.sensors import SensorState
        return SensorState(devices=frozenset())

    def open_haptic(self, device_id: int) -> Result[PlatformHapticHandle, EffyError]:
        """Open a haptic device for play back."""
        from Effy.platform import PlatformHapticHandle
        return Ok(PlatformHapticHandle(device_id))

    def close_haptic(self, device_id: int) -> None:
        """Close an opened haptic device."""
        pass

    def is_rumble_supported(self, device_id: int) -> bool:
        """Determine whether rumble is supported on this haptic device."""
        return False

    def play_rumble(self, device_id: int, strength: float, duration_ms: int) -> Result[None, EffyError]:
        """Play a simple rumble effect on the haptic device."""
        return Err(EffyError(code=-1, message="Rumble not implemented on macOS Quartz stub"))

    def stop_rumble(self, device_id: int) -> Result[None, EffyError]:
        """Stop rumble playback on the haptic device."""
        return Err(EffyError(code=-1, message="Rumble not implemented on macOS Quartz stub"))

    def upload_effect(self, device_id: int, effect: Any) -> Result[int, EffyError]:
        """Upload a custom haptic effect to the haptic device."""
        return Err(EffyError(code=-1, message="Haptic custom effects not implemented on macOS Quartz stub"))

    def run_effect(self, device_id: int, effect_id: int, iterations: int) -> Result[None, EffyError]:
        """Run a previously uploaded custom haptic effect."""
        return Err(EffyError(code=-1, message="Haptic custom effects not implemented on macOS Quartz stub"))

    def stop_effect(self, device_id: int, effect_id: int) -> Result[None, EffyError]:
        """Stop playback of a custom haptic effect."""
        return Err(EffyError(code=-1, message="Haptic custom effects not implemented on macOS Quartz stub"))

    def destroy_effect(self, device_id: int, effect_id: int) -> None:
        """Destroy an uploaded haptic effect to release memory."""
        pass

    def get_clipboard_text(self) -> str:
        """Get the text from the macOS system clipboard using pbpaste or in-memory fallback."""
        import subprocess
        try:
            res = subprocess.run(
                ["pbpaste"],
                capture_output=True,
                text=True,
                timeout=1.0
            )
            if res.returncode == 0:
                return res.stdout
        except Exception:
            pass
        return self._clipboard_text

    def set_clipboard_text(self, text: str) -> None:
        """Set the text in the macOS system clipboard using pbcopy or in-memory fallback."""
        import subprocess
        self._clipboard_text = text
        try:
            subprocess.run(
                ["pbcopy"],
                input=text,
                text=True,
                capture_output=True,
                timeout=1.0
            )
        except Exception:
            pass

    def get_clipboard_data(self, mime_type: str) -> Result[bytes, EffyError]:
        """Get binary data for a specific MIME type from the macOS clipboard using in-memory fallback."""
        if mime_type in self._clipboard_data:
            return Ok(self._clipboard_data[mime_type])
        return Err(EffyError(code=-1, message=f"MIME type '{mime_type}' not found in clipboard"))

    def set_clipboard_data(self, mime_type: str, data: bytes) -> Result[None, EffyError]:
        """Set binary data for a specific MIME type in the macOS clipboard using in-memory fallback."""
        self._clipboard_data[mime_type] = data
        return Ok(None)

    def present_accelerated(self, handle: Any, commands: list[Any], width: int, height: int) -> Result[None, EffyError]:
        """Hardware-accelerated rendering stub. macOS Quartz stub does not support accelerated presentation."""
        return Err(EffyError(code=-1, message="Hardware acceleration not supported on this platform"))
