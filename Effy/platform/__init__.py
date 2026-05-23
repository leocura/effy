from __future__ import annotations
from typing import Protocol, NewType, TYPE_CHECKING
from Effy._internal.result import Result
from Effy.error import EffyError

# Opaque handles — typed NewTypes instead of Any
PlatformWindowHandle = NewType("PlatformWindowHandle", int)
PlatformAudioHandle = NewType("PlatformAudioHandle", int)
PlatformVideoHandle = NewType("PlatformVideoHandle", int)
PlatformHapticHandle = NewType("PlatformHapticHandle", int)

if TYPE_CHECKING:
    from Effy.types import WindowParams
    from Effy.video.rect import Rect
    from Effy.video.surface import PixelBuffer
    from Effy.audio.types import AudioSpec
    from Effy.events.types import Event
    from Effy.input.keyboard import KeyboardState
    from Effy.input.mouse import MouseState
    from Effy.input.touch import TouchState
    from Effy.input.gamepad import GamepadState
    from Effy.input.sensors import SensorState
    from Effy.input.haptics import HapticEffect
    from Effy.render.commands import DrawCmd



class PlatformAdapter(Protocol):
    """Protocol defining the interface that all platform-specific adapters must satisfy.

    Each method corresponds to a native OS operation (window management, event
    polling, audio I/O, input queries, haptics) that the imperative shell delegates to.
    """

    def init_video(self) -> Result[PlatformVideoHandle, EffyError]:
        """Initialize the platform video subsystem."""
        ...

    def quit_video(self, handle: PlatformVideoHandle) -> None:
        """Shut down the platform video subsystem."""
        ...

    def create_window(self, params: WindowParams) -> Result[PlatformWindowHandle, EffyError]:
        """Create a native platform window."""
        ...

    def destroy_window(self, handle: PlatformWindowHandle) -> None:
        """Destroy a native platform window."""
        ...

    def set_window_title(self, handle: PlatformWindowHandle, title: str) -> None:
        """Set the title of a native window."""
        ...

    def flip_buffer(self, handle: PlatformWindowHandle, buf: PixelBuffer) -> None:
        """Present a PixelBuffer to the native window surface."""
        ...

    def poll_event(self) -> Event | None:
        """Return the next pending event or None if the queue is empty."""
        ...

    def wait_event(self, timeout_ms: int) -> Event | None:
        """Block until an event is available or the timeout elapses."""
        ...

    def pump_events(self) -> None:
        """Process native OS messages and populate the internal event queue."""
        ...

    def open_audio(self, spec: AudioSpec | None) -> Result[PlatformAudioHandle, EffyError]:
        """Open a native audio output device."""
        ...

    def write_audio(self, handle: PlatformAudioHandle, data: bytes) -> None:
        """Write raw audio sample data to the opened device."""
        ...

    def close_audio(self, handle: PlatformAudioHandle) -> None:
        """Close a previously opened audio device."""
        ...

    def get_num_video_displays(self) -> int:
        """Return the number of connected video displays."""
        ...

    def get_display_name(self, index: int) -> str:
        """Return the human-readable name of a display."""
        ...

    def get_display_bounds(self, index: int) -> Rect:
        """Return the bounding rectangle of a display."""
        ...

    def set_window_size(self, handle: PlatformWindowHandle, w: int, h: int) -> None:
        """Resize a native window."""
        ...

    def set_window_position(self, handle: PlatformWindowHandle, x: int, y: int) -> None:
        """Move a native window to the specified position."""
        ...

    def minimize_window(self, handle: PlatformWindowHandle) -> None:
        """Minimize a native window."""
        ...

    def maximize_window(self, handle: PlatformWindowHandle) -> None:
        """Maximize a native window."""
        ...

    def restore_window(self, handle: PlatformWindowHandle) -> None:
        """Restore a minimized or maximized window to its normal size."""
        ...

    def show_window(self, handle: PlatformWindowHandle) -> None:
        """Make a hidden native window visible."""
        ...

    def hide_window(self, handle: PlatformWindowHandle) -> None:
        """Hide a visible native window."""
        ...

    def get_keyboard_state(self) -> KeyboardState:
        """Return a snapshot of the current keyboard state."""
        ...

    def get_mouse_state(self) -> MouseState:
        """Return a snapshot of the current mouse state."""
        ...

    def get_touch_state(self) -> TouchState:
        """Return a snapshot of the current touch input state."""
        ...

    def get_gamepad_state(self) -> GamepadState:
        """Return a snapshot of the current gamepad state."""
        ...

    def get_sensor_state(self) -> SensorState:
        """Return a snapshot of the current sensor readings."""
        ...

    def open_haptic(self, device_id: int) -> Result[PlatformHapticHandle, EffyError]:
        """Open a haptic device for force feedback."""
        ...

    def close_haptic(self, handle: PlatformHapticHandle) -> None:
        """Close a haptic device."""
        ...

    def is_rumble_supported(self, handle: PlatformHapticHandle) -> bool:
        """Check whether the haptic device supports simple rumble."""
        ...

    def play_rumble(
        self, handle: PlatformHapticHandle, strength: float, duration_ms: int
    ) -> Result[None, EffyError]:
        """Play a simple rumble effect."""
        ...

    def stop_rumble(self, handle: PlatformHapticHandle) -> Result[None, EffyError]:
        """Stop an active rumble effect."""
        ...

    def upload_effect(
        self, handle: PlatformHapticHandle, effect: HapticEffect
    ) -> Result[int, EffyError]:
        """Upload a custom haptic effect to the device."""
        ...

    def run_effect(
        self, handle: PlatformHapticHandle, effect_id: int, iterations: int
    ) -> Result[None, EffyError]:
        """Run a previously uploaded haptic effect."""
        ...

    def stop_effect(
        self, handle: PlatformHapticHandle, effect_id: int
    ) -> Result[None, EffyError]:
        """Stop a running haptic effect."""
        ...

    def destroy_effect(self, handle: PlatformHapticHandle, effect_id: int) -> None:
        """Destroy an uploaded haptic effect and free its resources."""
        ...

    def get_clipboard_text(self) -> str:
        """Get text from the system clipboard."""
        ...

    def set_clipboard_text(self, text: str) -> None:
        """Set text in the system clipboard."""
        ...

    def get_clipboard_data(self, mime_type: str) -> Result[bytes, EffyError]:
        """Get binary data for a specific MIME type from the clipboard."""
        ...

    def set_clipboard_data(self, mime_type: str, data: bytes) -> Result[None, EffyError]:
        """Set binary data for a specific MIME type in the clipboard."""
        ...

    def present_accelerated(
        self, handle: PlatformWindowHandle, commands: list[DrawCmd], width: int, height: int
    ) -> Result[None, EffyError]:
        """Present the deferred commands using hardware acceleration.

        Args:
            handle: Native window handle.
            commands: List of DrawCmd to render.
            width: Width of the render target.
            height: Height of the render target.

        Returns:
            A Result wrapper representing success or failure.
        """
        ...



def get_best_adapter() -> PlatformAdapter:
    """Detect the current platform and return the most appropriate adapter.

    Selection priority: Windows GDI > Linux X11 > macOS Quartz > Headless.

    Returns:
        An instance of the best available PlatformAdapter.
    """
    from Effy.platform.windows_gdi import WindowsGDIAdapter
    from Effy.platform.linux_x11 import LinuxX11Adapter
    from Effy.platform.macos_quartz import MacOSQuartzAdapter
    from Effy.platform.headless import HeadlessAdapter

    if WindowsGDIAdapter.detect():
        return WindowsGDIAdapter()
    if LinuxX11Adapter.detect():
        return LinuxX11Adapter()
    if MacOSQuartzAdapter.detect():
        return MacOSQuartzAdapter()
    return HeadlessAdapter()
