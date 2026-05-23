from __future__ import annotations
from typing import Any, TYPE_CHECKING
from Effy._internal.result import Ok, Err, Result
from Effy.error import SDLError

if TYPE_CHECKING:
    from Effy.platform import PlatformHapticHandle, PlatformAudioHandle
    from Effy.audio.types import AudioSpec

from Effy.events.queue import EventQueue

class HeadlessAdapter:
    """An in-memory platform adapter used for testing and CI environments.

    Simulates display, audio, input, and clipboard without any OS interaction.
    Stores the last buffer presented via flip_buffer so tests can assert pixel
    correctness without a real display.
    """

    def __init__(self) -> None:
        """Initialize the headless adapter with empty state."""
        self._pending_events: EventQueue = EventQueue.empty()
        self._pressed_keys: set[Any] = set()
        self._mouse_x: int = 0
        self._mouse_y: int = 0
        self._mouse_buttons: Any = None
        self._touch_devices: dict[int, set[Any]] = {}
        self._gamepads: dict[int, Any] = {}
        self._sensors: dict[int, Any] = {}
        self._haptics_opened: set[int] = set()
        self._haptics_rumble_supported: set[int] = set()
        self._haptics_playing_rumble: dict[int, tuple[float, int]] = {}
        self._haptics_effects: dict[int, dict[int, Any]] = {}
        self._haptics_running_effects: dict[int, set[int]] = {}
        self._haptics_next_effect_id: int = 1
        self._clipboard_text: str = ""
        self._clipboard_data: dict[str, bytes] = {}
        self._last_presented_buffer: Any = None

    def init_video(self) -> Result[Any, Any]:
        """Initialize the headless video subsystem (no-op)."""
        return Ok("headless_video_handle")
        
    def quit_video(self, handle: Any) -> None:
        """Shut down the headless video subsystem (no-op)."""
        pass
        
    def create_window(self, params: Any) -> Result[Any, Any]:
        """Create a simulated window handle for headless testing."""
        return Ok("headless_window_handle")
        
    def destroy_window(self, handle: Any) -> None:
        """Destroy a simulated window handle (no-op)."""
        pass
        
    def set_window_title(self, handle: Any, title: str) -> None:
        """Set the window title (no-op in headless mode)."""
        pass
        
    def flip_buffer(self, handle: Any, buf: Any) -> None:
        """Capture the presented pixel buffer for test inspection.

        Args:
            handle: The platform window handle (ignored in headless mode).
            buf: The PixelBuffer to present.
        """
        from Effy.video.surface import PixelBuffer
        import array
        cloned_data = array.array(buf._data.typecode, buf._data)
        self._last_presented_buffer = PixelBuffer(
            width=buf.width,
            height=buf.height,
            pitch=buf.pitch,
            _data_cache=[cloned_data],
            _commands_list=list(buf._commands_list),
            _is_transient=False
        )
        
    def poll_event(self) -> Any | None:
        """Return the next event from the simulated event queue."""
        event, self._pending_events = self._pending_events.pop()
        return event

    def wait_event(self, timeout_ms: int) -> Any | None:
        """Wait for and return the next event from the simulated queue."""
        event, self._pending_events = self._pending_events.pop()
        return event

    def pump_events(self) -> None:
        """Pump the simulated event queue (no-op)."""
        pass
        
    def open_audio(self, spec: AudioSpec | None) -> Result[PlatformAudioHandle, SDLError]:
        """Open a simulated audio device for headless testing."""
        from Effy.platform import PlatformAudioHandle
        return Ok(PlatformAudioHandle(1))
        
    def write_audio(self, handle: PlatformAudioHandle, data: bytes) -> None:
        """Write audio data to the simulated device (no-op)."""
        pass
        
    def close_audio(self, handle: PlatformAudioHandle) -> None:
        """Close the simulated audio device (no-op)."""
        pass

    def get_keyboard_state(self) -> Any:
        """Return the simulated keyboard state snapshot."""
        from Effy.input.keyboard import KeyboardState
        return KeyboardState(pressed_keys=frozenset(self._pressed_keys))

    def get_mouse_state(self) -> Any:
        """Return the simulated mouse state snapshot."""
        from Effy.input.mouse import MouseState
        from Effy.events.types import MouseButton
        buttons = self._mouse_buttons if self._mouse_buttons is not None else MouseButton.NONE
        return MouseState(x=self._mouse_x, y=self._mouse_y, buttons=buttons)

    def get_touch_state(self) -> Any:
        """Return the simulated touch device state snapshot."""
        from Effy.input.touch import TouchState, TouchDeviceState
        devices = []
        for dev_id, fingers in self._touch_devices.items():
            devices.append(TouchDeviceState(device_id=dev_id, fingers=frozenset(fingers)))
        return TouchState(devices=frozenset(devices))

    def get_gamepad_state(self) -> Any:
        """Return the simulated gamepad state snapshot."""
        from Effy.input.gamepad import GamepadState
        return GamepadState(devices=frozenset(self._gamepads.values()))

    def get_sensor_state(self) -> Any:
        """Return the simulated sensor state snapshot."""
        from Effy.input.sensors import SensorState
        return SensorState(devices=frozenset(self._sensors.values()))

    def open_haptic(self, device_id: int) -> Result[PlatformHapticHandle, SDLError]:
        """Open a simulated haptic device."""
        self._haptics_opened.add(device_id)
        from Effy.platform import PlatformHapticHandle
        return Ok(PlatformHapticHandle(device_id))

    def close_haptic(self, device_id: int) -> None:
        """Close a simulated haptic device."""
        self._haptics_opened.discard(device_id)

    def is_rumble_supported(self, device_id: int) -> bool:
        """Check whether rumble is supported on the simulated device."""
        return device_id in self._haptics_rumble_supported

    def play_rumble(self, device_id: int, strength: float, duration_ms: int) -> Result[None, SDLError]:
        """Play a rumble effect on the simulated haptic device."""
        if device_id not in self._haptics_opened:
            return Err(SDLError(code=-1, message="Device not open"))
        self._haptics_playing_rumble[device_id] = (strength, duration_ms)
        return Ok(None)

    def stop_rumble(self, device_id: int) -> Result[None, SDLError]:
        """Stop the rumble effect on the simulated haptic device."""
        if device_id not in self._haptics_opened:
            return Err(SDLError(code=-1, message="Device not open"))
        self._haptics_playing_rumble.pop(device_id, None)
        return Ok(None)

    def upload_effect(self, device_id: int, effect: Any) -> Result[int, SDLError]:
        """Upload a haptic effect to the simulated device and return its ID."""
        if device_id not in self._haptics_opened:
            return Err(SDLError(code=-1, message="Device not open"))
        eff_id = self._haptics_next_effect_id
        self._haptics_next_effect_id += 1
        if device_id not in self._haptics_effects:
            self._haptics_effects[device_id] = {}
        self._haptics_effects[device_id][eff_id] = effect
        return Ok(eff_id)

    def run_effect(self, device_id: int, effect_id: int, iterations: int) -> Result[None, SDLError]:
        """Run a previously uploaded haptic effect on the simulated device."""
        if device_id not in self._haptics_opened:
            return Err(SDLError(code=-1, message="Device not open"))
        if device_id not in self._haptics_effects or effect_id not in self._haptics_effects[device_id]:
            return Err(SDLError(code=-1, message="Effect not found"))
        if device_id not in self._haptics_running_effects:
            self._haptics_running_effects[device_id] = set()
        self._haptics_running_effects[device_id].add(effect_id)
        return Ok(None)

    def stop_effect(self, device_id: int, effect_id: int) -> Result[None, SDLError]:
        """Stop a running haptic effect on the simulated device."""
        if device_id not in self._haptics_opened:
            return Err(SDLError(code=-1, message="Device not open"))
        if device_id in self._haptics_running_effects:
            self._haptics_running_effects[device_id].discard(effect_id)
        return Ok(None)

    def destroy_effect(self, device_id: int, effect_id: int) -> None:
        """Remove a haptic effect from the simulated device."""
        if device_id in self._haptics_effects:
            self._haptics_effects[device_id].pop(effect_id, None)
        if device_id in self._haptics_running_effects:
            self._haptics_running_effects[device_id].discard(effect_id)

    def get_num_video_displays(self) -> int:
        """Return the number of simulated video displays (always 1)."""
        return 1

    def get_display_name(self, index: int) -> str:
        """Return the name of the simulated display."""
        return "Headless Monitor"

    def get_display_bounds(self, index: int) -> Any:
        """Return the bounds of the simulated display (1920x1080)."""
        from Effy.video.rect import Rect
        return Rect(0, 0, 1920, 1080)

    def set_window_size(self, handle: Any, w: int, h: int) -> None:
        """Set the simulated window size (no-op)."""
        pass

    def set_window_position(self, handle: Any, x: int, y: int) -> None:
        """Set the simulated window position (no-op)."""
        pass

    def minimize_window(self, handle: Any) -> None:
        """Minimize the simulated window (no-op)."""
        pass

    def maximize_window(self, handle: Any) -> None:
        """Maximize the simulated window (no-op)."""
        pass

    def restore_window(self, handle: Any) -> None:
        """Restore the simulated window (no-op)."""
        pass

    def show_window(self, handle: Any) -> None:
        """Show the simulated window (no-op)."""
        pass

    def hide_window(self, handle: Any) -> None:
        """Hide the simulated window (no-op)."""
        pass

    def get_clipboard_text(self) -> str:
        """Get the mocked clipboard text."""
        return self._clipboard_text

    def set_clipboard_text(self, text: str) -> None:
        """Set the mocked clipboard text."""
        self._clipboard_text = text

    def get_clipboard_data(self, mime_type: str) -> Result[bytes, SDLError]:
        """Get the mocked clipboard data for a MIME type."""
        if mime_type in self._clipboard_data:
            return Ok(self._clipboard_data[mime_type])
        return Err(SDLError(code=-1, message=f"MIME type '{mime_type}' not found in clipboard"))

    def set_clipboard_data(self, mime_type: str, data: bytes) -> Result[None, SDLError]:
        """Set the mocked clipboard data for a MIME type."""
        self._clipboard_data[mime_type] = data
        return Ok(None)

    def present_accelerated(self, handle: Any, commands: list[Any], width: int, height: int) -> Result[None, SDLError]:
        """Hardware-accelerated rendering stub. Headless mode does not support accelerated presentation."""
        return Err(SDLError(code=-1, message="Hardware acceleration not supported on this platform"))
