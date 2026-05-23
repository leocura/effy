from __future__ import annotations
import sys
import ctypes
from ctypes import wintypes
from typing import Any, cast, TYPE_CHECKING
from Effy._internal.result import Ok, Err, Result
from Effy.error import SDLError
from Effy.platform import PlatformAudioHandle

if TYPE_CHECKING:
    from Effy.video.rect import Rect
    from Effy.input.sensors import SensorState
    from Effy.input.haptics import HapticEffect
    from Effy.platform import PlatformHapticHandle
    from Effy.audio.types import AudioSpec

WINFUNCTYPE: Any = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)
windll: Any = getattr(ctypes, "windll", None)

# Win32 Constants
WM_DESTROY = 0x0002
WM_CLOSE = 0x0010
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
WM_MOUSEMOVE = 0x0200
WM_SIZE = 0x0005
WM_MOUSEWHEEL = 0x020A
PM_REMOVE = 0x0001
WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_VISIBLE = 0x10000000
IDC_ARROW = 32512
BI_BITFIELDS = 3
DIB_RGB_COLORS = 0

# Virtual Key Codes
VK_LSHIFT = 0xA0
VK_RSHIFT = 0xA1
VK_LCONTROL = 0xA2
VK_RCONTROL = 0xA3
VK_LMENU = 0xA4
VK_RMENU = 0xA5
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_CAPITAL = 0x14
VK_NUMLOCK = 0x90
VK_SCROLL = 0x91

if sys.platform == "win32" or TYPE_CHECKING:
    WNDPROC_TYPE = WINFUNCTYPE(ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

    class WNDCLASSEXW(ctypes.Structure):
        """Win32 WNDCLASSEXW structure for window class registration."""
        _fields_ = [
            ('cbSize', wintypes.UINT),
            ('style', wintypes.UINT),
            ('lpfnWndProc', WNDPROC_TYPE),
            ('cbClsExtra', ctypes.c_int),
            ('cbWndExtra', ctypes.c_int),
            ('hInstance', wintypes.HINSTANCE),
            ('hIcon', wintypes.HICON),
            ('hCursor', wintypes.HANDLE),
            ('hbrBackground', wintypes.HBRUSH),
            ('lpszMenuName', wintypes.LPCWSTR),
            ('lpszClassName', wintypes.LPCWSTR),
            ('hIconSm', wintypes.HICON),
        ]

    class MSG(ctypes.Structure):
        """Win32 MSG structure for window message dispatch."""
        _fields_ = [
            ('hwnd', wintypes.HWND),
            ('message', wintypes.UINT),
            ('wParam', wintypes.WPARAM),
            ('lParam', wintypes.LPARAM),
            ('time', wintypes.DWORD),
            ('pt', wintypes.POINT),
        ]

    class BITMAPINFOHEADER(ctypes.Structure):
        """Win32 BITMAPINFOHEADER structure describing bitmap dimensions and format."""
        _fields_ = [
            ('biSize', wintypes.DWORD),
            ('biWidth', wintypes.LONG),
            ('biHeight', wintypes.LONG),
            ('biPlanes', wintypes.WORD),
            ('biBitCount', wintypes.WORD),
            ('biCompression', wintypes.DWORD),
            ('biSizeImage', wintypes.DWORD),
            ('biXPelsPerMeter', wintypes.LONG),
            ('biYPelsPerMeter', wintypes.LONG),
            ('biClrUsed', wintypes.DWORD),
            ('biClrImportant', wintypes.DWORD),
        ]

    class BITMAPINFO(ctypes.Structure):
        """Win32 BITMAPINFO structure combining header and color masks."""
        _fields_ = [
            ('bmiHeader', BITMAPINFOHEADER),
            ('bmiColors', wintypes.DWORD * 3),
        ]

    windll.user32.DefWindowProcW.restype = ctypes.c_ssize_t
    windll.user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]

    windll.user32.GetKeyState.restype = wintypes.SHORT
    windll.user32.GetKeyState.argtypes = [ctypes.c_int]

# Module level callback
def _wnd_proc(hwnd: int, msg: int, wparam: int, lparam: int) -> int:
    """Win32 window procedure callback for message dispatch."""
    from Effy._internal.registry import get_platform_adapter
    adapter = get_platform_adapter()
    if adapter and hasattr(adapter, "_handle_message"):
        return cast(int, adapter._handle_message(hwnd, msg, wparam, lparam))
    if sys.platform == "win32":
        return cast(int, windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam))
    return 0

if sys.platform == "win32" or TYPE_CHECKING:
    _c_wnd_proc = WNDPROC_TYPE(_wnd_proc)

if sys.platform == "win32" or TYPE_CHECKING:
    class GUID(ctypes.Structure):
        """ctypes representation of a GUID structure."""
        _fields_ = [
            ("Data1", ctypes.c_ulong),
            ("Data2", ctypes.c_ushort),
            ("Data3", ctypes.c_ushort),
            ("Data4", ctypes.c_ubyte * 8)
        ]
        
        def __init__(self, guid_str: str) -> None:
            """Parse a GUID string into a GUID structure.
            
            Args:
                guid_str: The curly-braced string representation of a GUID.
            """
            import re
            parts = re.findall(r'[0-9a-fA-F]+', guid_str)
            self.Data1 = int(parts[0], 16)
            self.Data2 = int(parts[1], 16)
            self.Data3 = int(parts[2], 16)
            d4 = parts[3] + parts[4]
            for i in range(8):
                self.Data4[i] = int(d4[i*2 : i*2+2], 16)

    class WAVEFORMATEX(ctypes.Structure):
        """WAVEFORMATEX structure defining standard waveform audio format details."""
        _fields_ = [
            ("wFormatTag", ctypes.c_ushort),
            ("nChannels", ctypes.c_ushort),
            ("nSamplesPerSec", ctypes.c_ulong),
            ("nAvgBytesPerSec", ctypes.c_ulong),
            ("nBlockAlign", ctypes.c_ushort),
            ("wBitsPerSample", ctypes.c_ushort),
            ("cbSize", ctypes.c_ushort),
        ]

    class WAVEFORMATEXTENSIBLE(ctypes.Structure):
        """WAVEFORMATEXTENSIBLE structure for extended multi-channel and float formats."""
        _fields_ = [
            ("Format", WAVEFORMATEX),
            ("Samples", ctypes.c_ushort),
            ("dwChannelMask", ctypes.c_ulong),
            ("SubFormat", GUID)
        ]

    def call_com_method(interface_ptr: Any, index: int, argtypes: list[Any], *args: Any) -> int:
        """Call a method on a COM interface pointer using virtual table lookup.
        
        Args:
            interface_ptr: The COM object interface pointer.
            index: The zero-based method index in the interface vtbl.
            argtypes: The list of ctypes types for the method arguments.
            *args: The argument values to pass.
            
        Returns:
            The HRESULT return code from the COM method call.
        """
        vtbl = ctypes.cast(interface_ptr, ctypes.POINTER(ctypes.c_void_p))[0]
        func_ptr = ctypes.cast(vtbl, ctypes.POINTER(ctypes.c_void_p))[index]
        proto = WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, *argtypes)
        func = proto(func_ptr)
        return int(func(interface_ptr, *args))


class WindowsAudioDevice:
    """Native audio hardware output device representation for Windows systems (WASAPI)."""
    
    def __init__(
        self,
        backend_type: str,
        audio_client: Any,
        render_client: Any,
        spec: Any,
        hardware_spec: Any,
        buffer_size: int
    ) -> None:
        """Initialize the Windows native audio playback device wrapper.
        
        Args:
            backend_type: The string identifier of the backend (e.g. 'wasapi', 'dummy').
            audio_client: The native IAudioClient COM pointer or None.
            render_client: The native IAudioRenderClient COM pointer or None.
            spec: The user requested AudioSpec.
            hardware_spec: The actual hardware AudioSpec format.
            buffer_size: The capacity of the WASAPI endpoint buffer in frames.
        """
        self.backend_type: str = backend_type
        self.audio_client: Any = audio_client
        self.render_client: Any = render_client
        self.spec: Any = spec
        self.hardware_spec: Any = hardware_spec
        self.buffer_size: int = buffer_size



# XInput structs and Touch constants injected
WM_TOUCH = 0x0240
TWF_WANTPALM = 0x00000002

class TOUCHINPUT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long),
        ("hSource", ctypes.c_void_p),
        ("dwID", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("dwMask", ctypes.c_ulong),
        ("dwTime", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ("cxContact", ctypes.c_ulong),
        ("cyContact", ctypes.c_ulong),
    ]

class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ("wButtons", ctypes.c_ushort),
        ("bLeftTrigger", ctypes.c_ubyte),
        ("bRightTrigger", ctypes.c_ubyte),
        ("sThumbLX", ctypes.c_short),
        ("sThumbLY", ctypes.c_short),
        ("sThumbRX", ctypes.c_short),
        ("sThumbRY", ctypes.c_short),
    ]

class XINPUT_STATE(ctypes.Structure):
    _fields_ = [
        ("dwPacketNumber", ctypes.c_ulong),
        ("Gamepad", XINPUT_GAMEPAD),
    ]

class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [
        ("wLeftMotorSpeed", ctypes.c_ushort),
        ("wRightMotorSpeed", ctypes.c_ushort),
    ]

_xinput_dll = None
if sys.platform == "win32":
    try:
        _xinput_dll = ctypes.WinDLL("xinput1_4.dll")
    except Exception:
        try:
            _xinput_dll = ctypes.WinDLL("xinput9_1_0.dll")
        except Exception:
            try:
                _xinput_dll = ctypes.WinDLL("xinput1_3.dll")
            except Exception:
                pass

if _xinput_dll:
    _XInputGetState = getattr(_xinput_dll, "XInputGetState", None)
    if _XInputGetState:
        _XInputGetState.argtypes = [ctypes.c_ulong, ctypes.POINTER(XINPUT_STATE)]
        _XInputGetState.restype = ctypes.c_ulong
    _XInputSetState = getattr(_xinput_dll, "XInputSetState", None)
    if _XInputSetState:
        _XInputSetState.argtypes = [ctypes.c_ulong, ctypes.POINTER(XINPUT_VIBRATION)]
        _XInputSetState.restype = ctypes.c_ulong

if sys.platform == "win32":
    try:
        windll.user32.RegisterTouchWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        windll.user32.GetTouchInputInfo.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.POINTER(TOUCHINPUT), ctypes.c_int]
        windll.user32.CloseTouchInputHandle.argtypes = [ctypes.c_void_p]
        
        windll.user32.RegisterClipboardFormatW.argtypes = [ctypes.c_wchar_p]
        windll.user32.RegisterClipboardFormatW.restype = ctypes.c_uint
        
        windll.user32.GetClipboardData.argtypes = [ctypes.c_uint]
        windll.user32.GetClipboardData.restype = ctypes.c_void_p
        
        windll.user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        windll.user32.SetClipboardData.restype = ctypes.c_void_p
    except Exception:
        pass

class WindowsGDIAdapter:
    """Platform adapter implementing the Effy platform interface using Win32 GDI and WASAPI."""

    def __init__(self) -> None:
        from Effy.events.queue import EventQueue
        self._pending_events: EventQueue = EventQueue.empty()
        self._h_instance: Any = None
        self._class_name: str = "Effy_WindowClass"
        self._class_atom: Any = None
        self._last_mouse_x: int | None = None
        self._last_mouse_y: int | None = None
        self._pressed_keys: set[Any] = set()
        self._mouse_x: int = 0
        self._mouse_y: int = 0
        self._mouse_buttons: Any = None
        self._touch_devices: dict[int, set[Any]] = {}
        self._clipboard_text: str = ""
        self._clipboard_data: dict[str, bytes] = {}
        self._last_gamepad_state: Any = None
        self._bgra_buffer: bytearray = bytearray()
        self._audio_devices: dict[PlatformAudioHandle, Any] = {}
        self._next_audio_id: int = 1

    @classmethod
    def detect(cls) -> bool:
        """Return True if running on Windows."""
        return sys.platform == "win32"

    def init_video(self) -> Result[Any, SDLError]:
        """Initialize the Windows GDI video subsystem and register the window class."""
        if sys.platform != "win32":
             return Err(SDLError(code=-1, message="Not on Windows"))

        self._h_instance = windll.kernel32.GetModuleHandleW(None)
        
        wndclass = WNDCLASSEXW()
        wndclass.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wndclass.style = 0
        wndclass.lpfnWndProc = _c_wnd_proc
        wndclass.cbClsExtra = 0
        wndclass.cbWndExtra = 0
        wndclass.hInstance = self._h_instance
        wndclass.hIcon = 0
        wndclass.hCursor = windll.user32.LoadCursorW(None, IDC_ARROW)
        wndclass.hbrBackground = 0
        wndclass.lpszMenuName = None
        wndclass.lpszClassName = self._class_name
        wndclass.hIconSm = 0
        
        atom = windll.user32.RegisterClassExW(ctypes.byref(wndclass))
        if not atom:
            return Err(SDLError(code=-1, message="Failed to register window class"))
            
        self._class_atom = atom
        return Ok("windows_video_handle")
        
    def quit_video(self, handle: Any) -> None:
        """Unregister the Win32 window class and tear down the video subsystem."""
        if sys.platform == "win32":
            if self._class_atom:
                windll.user32.UnregisterClassW(self._class_name, self._h_instance)
        
    def create_window(self, params: Any) -> Result[Any, SDLError]:
        """Create a native Win32 window using CreateWindowExW."""
        if sys.platform != "win32":
             return Err(SDLError(code=-1, message="Not on Windows"))

        title = getattr(params, "title", "Effy Window")
        w = getattr(params, "w", 640)
        h = getattr(params, "h", 480)
        
        # Equivalent to SDL_CreateWindow
        hwnd = windll.user32.CreateWindowExW(
            0, # dwExStyle
            self._class_name, # lpClassName
            title, # lpWindowName
            WS_OVERLAPPEDWINDOW | WS_VISIBLE, # dwStyle
            0, 0, w, h, # x, y, nWidth, nHeight
            None, # hWndParent
            None, # hMenu
            self._h_instance, # hInstance
            None # lpParam
        )
        
        if not hwnd:
            return Err(SDLError(code=-1, message="Failed to create window"))
            
        if hasattr(windll.user32, "RegisterTouchWindow"):
            windll.user32.RegisterTouchWindow(hwnd, TWF_WANTPALM)
            
        return Ok(hwnd)

    def destroy_window(self, handle: Any) -> None:
        """Destroy the native Win32 window."""
        if sys.platform == "win32":
            windll.user32.DestroyWindow(handle)

    def set_window_title(self, handle: Any, title: str) -> None:
        """Set the title of the native window."""
        if sys.platform == "win32":
            windll.user32.SetWindowTextW(handle, title)

    def flip_buffer(self, handle: Any, buffer: Any) -> None:
        """Present a PixelBuffer to the given window handle using GDI."""
        if sys.platform != "win32":
            return
            
        hwnd = handle
        user32 = windll.user32
        gdi32 = windll.gdi32
        
        hdc = user32.GetDC(hwnd)
        if not hdc:
            return
            
        try:
            w, h = buffer.width, buffer.height
            expected_len = w * h * 4
            if len(buffer._data) < expected_len:
                return

            bmi = BITMAPINFO()
            bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            bmi.bmiHeader.biWidth = w
            bmi.bmiHeader.biHeight = -h  # top-down DIB
            bmi.bmiHeader.biPlanes = 1
            bmi.bmiHeader.biBitCount = 32
            bmi.bmiHeader.biCompression = 0  # BI_RGB

            # We reuse the persistent BGRA bytearray to match Windows GDI format
            # since PixelBuffer stores RGBA, minimizing allocations and GC pressure.
            if len(self._bgra_buffer) != expected_len:
                self._bgra_buffer = bytearray(expected_len)
            self._bgra_buffer[:] = buffer._data
            self._bgra_buffer[0::4], self._bgra_buffer[2::4] = self._bgra_buffer[2::4], self._bgra_buffer[0::4]

            data_ptr = (ctypes.c_char * expected_len).from_buffer(self._bgra_buffer)
            
            gdi32.SetDIBitsToDevice(
                hdc,
                0, 0, w, h,
                0, 0, 0, h,
                ctypes.byref(data_ptr),
                ctypes.byref(bmi),
                0  # DIB_RGB_COLORS
            )
        finally:
            user32.ReleaseDC(hwnd, hdc)

    def pump_events(self) -> None:
        """Pump the Windows message loop to process pending events."""
        if sys.platform != "win32":
            return
            
        msg = MSG()
        # PM_REMOVE is 0x0001
        while windll.user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):
            windll.user32.TranslateMessage(ctypes.byref(msg))
            windll.user32.DispatchMessageW(ctypes.byref(msg))

    def poll_event(self) -> Any | None:
        """Return the next pending Effy event, or None if the queue is empty."""
        if not self._pending_events:
            self.pump_events()
            
        event, self._pending_events = self._pending_events.pop()
        return event

    def wait_event(self, timeout_ms: int) -> Any | None:
        """Block until an event is available or timeout_ms elapses, then return it."""
        if not self._pending_events:
            self.pump_events()
            
        if self._pending_events:
            event, self._pending_events = self._pending_events.pop()
            return event
            
        if sys.platform == "win32":
            import time
            start = time.monotonic_ns() // 1_000_000
            while True:
                self.pump_events()
                if self._pending_events:
                    event, self._pending_events = self._pending_events.pop()
                    return event
                
                now = time.monotonic_ns() // 1_000_000
                if timeout_ms > 0 and (now - start) >= timeout_ms:
                    return None
                time.sleep(0.001)
        return None

    def _get_key_mod(self) -> Any:
        """Convert current Win32 key states into KeyMod flags."""
        from Effy.events.types import KeyMod
        mod = KeyMod.NONE
        
        # GetKeyState returns a short. High-order bit is 1 if key is down.
        # Low-order bit is 1 if key is toggled (caps lock, num lock).
        if windll.user32.GetKeyState(0x10) & 0x8000:
            mod |= KeyMod.SHIFT
        if windll.user32.GetKeyState(0x11) & 0x8000:
            mod |= KeyMod.LCTRL
        if windll.user32.GetKeyState(0x12) & 0x8000:
            mod |= KeyMod.LALT
        if (windll.user32.GetKeyState(0x5B) & 0x8000) or (windll.user32.GetKeyState(0x5C) & 0x8000):
            mod |= KeyMod.LGUI
        if windll.user32.GetKeyState(0x14) & 0x0001:
            mod |= KeyMod.CAPS
        if windll.user32.GetKeyState(0x90) & 0x0001:
            mod |= KeyMod.NUM
            
        return mod
        
    def _handle_message(self, hwnd: int, msg: int, wparam: int, lparam: int) -> int:
        """Translate a Win32 MSG into a Effy event and enqueue it."""
        if msg == WM_DESTROY:
            from Effy.events.types import QuitEvent
            self._pending_events = self._pending_events.push(QuitEvent(timestamp=0))
            return 0
        elif msg == WM_CLOSE:
            if sys.platform == "win32":
                windll.user32.DestroyWindow(hwnd)
            return 0
        elif msg in (WM_KEYDOWN, WM_KEYUP, WM_SYSKEYDOWN, WM_SYSKEYUP):
            from Effy.events.types import KeyDownEvent, KeyUpEvent, Scancode, Keycode
            from Effy.types import WindowID
            
            scancode = Scancode((lparam >> 16) & 0xFF)
            keycode = Keycode(wparam)
            mod = self._get_key_mod()
            
            if msg in (WM_KEYDOWN, WM_SYSKEYDOWN):
                repeat = bool((lparam >> 30) & 1)
                self._pressed_keys.add(scancode)
                self._pending_events = self._pending_events.push(KeyDownEvent(
                    timestamp=0,
                    window_id=WindowID(hwnd),
                    scancode=scancode,
                    keycode=keycode,
                    mod=mod,
                    repeat=repeat
                ))
            else:
                self._pressed_keys.discard(scancode)
                self._pending_events = self._pending_events.push(KeyUpEvent(
                    timestamp=0,
                    window_id=WindowID(hwnd),
                    scancode=scancode,
                    keycode=keycode,
                    mod=mod
                ))
            return 0
        elif msg == WM_MOUSEMOVE:
            from Effy.events.types import MouseMotionEvent, MouseButton
            from Effy.types import WindowID
            
            x = lparam & 0xFFFF
            if x >= 0x8000:
                x -= 0x10000
            y = (lparam >> 16) & 0xFFFF
            if y >= 0x8000:
                y -= 0x10000
            
            buttons = MouseButton.NONE
            if wparam & 0x0001: # MK_LBUTTON
                buttons |= MouseButton.LEFT
            if wparam & 0x0002: # MK_RBUTTON
                buttons |= MouseButton.RIGHT
            if wparam & 0x0010: # MK_MBUTTON
                buttons |= MouseButton.MIDDLE
                
            xrel = 0
            yrel = 0
            if self._last_mouse_x is not None:
                xrel = x - self._last_mouse_x
            if self._last_mouse_y is not None:
                yrel = y - self._last_mouse_y
                
            self._last_mouse_x = x
            self._last_mouse_y = y
            self._mouse_x = x
            self._mouse_y = y
            self._mouse_buttons = buttons
                
            self._pending_events = self._pending_events.push(MouseMotionEvent(
                timestamp=0,
                window_id=WindowID(hwnd),
                x=x,
                y=y,
                xrel=xrel,
                yrel=yrel,
                buttons=buttons
            ))
            return 0
        elif msg == WM_SIZE:
            from Effy.events.types import WindowEvent, WindowEventID
            from Effy.types import WindowID
            
            w = lparam & 0xFFFF
            h = (lparam >> 16) & 0xFFFF
            
            event_id = WindowEventID.RESIZED
            if wparam == 1: # SIZE_MINIMIZED
                event_id = WindowEventID.MINIMIZED
            elif wparam == 2: # SIZE_MAXIMIZED
                event_id = WindowEventID.MAXIMIZED
            elif wparam == 0: # SIZE_RESTORED
                event_id = WindowEventID.RESTORED
                
            self._pending_events = self._pending_events.push(WindowEvent(
                timestamp=0,
                window_id=WindowID(hwnd),
                event_id=event_id,
                data1=w,
                data2=h
            ))
            return 0
        elif msg == WM_MOUSEWHEEL:
            from Effy.events.types import MouseWheelEvent
            from Effy.types import WindowID
            
            delta = ctypes.c_short(wparam >> 16).value
            scroll_y = delta // 120
            
            self._pending_events = self._pending_events.push(MouseWheelEvent(
                timestamp=0,
                window_id=WindowID(hwnd),
                which=0,
                x=0,
                y=scroll_y,
                direction=0,
                precise_x=0.0,
                precise_y=float(scroll_y)
            ))
            return 0

        elif msg == WM_TOUCH:
            from Effy.events.types import FingerDownEvent, FingerUpEvent, FingerMotionEvent
            
            num_inputs = wparam & 0xFFFF
            inputs = (TOUCHINPUT * num_inputs)()
            if windll.user32.GetTouchInputInfo(ctypes.c_void_p(lparam), num_inputs, inputs, ctypes.sizeof(TOUCHINPUT)):
                for i in range(num_inputs):
                    ti = inputs[i]
                    x = ti.x / 100.0
                    y = ti.y / 100.0
                    # TOUCHEVENTF_DOWN = 0x0002, TOUCHEVENTF_UP = 0x0004, TOUCHEVENTF_MOVE = 0x0001
                    if ti.dwFlags & 0x0002: # DOWN
                        if 0 not in self._touch_devices:
                            self._touch_devices[0] = set()
                        self._touch_devices[0].add(ti.dwID)
                        self._pending_events = self._pending_events.push(FingerDownEvent(
                            timestamp=0, touch_id=0, finger_id=ti.dwID,
                            x=x, y=y, dx=0.0, dy=0.0, pressure=1.0
                        ))
                    elif ti.dwFlags & 0x0004: # UP
                        if 0 in self._touch_devices:
                            self._touch_devices[0].discard(ti.dwID)
                        self._pending_events = self._pending_events.push(FingerUpEvent(
                            timestamp=0, touch_id=0, finger_id=ti.dwID,
                            x=x, y=y, dx=0.0, dy=0.0, pressure=1.0
                        ))
                    elif ti.dwFlags & 0x0001: # MOVE
                        self._pending_events = self._pending_events.push(FingerMotionEvent(
                            timestamp=0, touch_id=0, finger_id=ti.dwID,
                            x=x, y=y, dx=0.0, dy=0.0, pressure=1.0
                        ))
                windll.user32.CloseTouchInputHandle(ctypes.c_void_p(lparam))
            return 0

        if sys.platform == "win32":
            return cast(int, windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam))
        return 0
        
    def open_audio(self, spec: AudioSpec | None) -> Result[PlatformAudioHandle, SDLError]:
        """Open a native Windows audio hardware playback output (WASAPI) or fall back to dummy."""
        from Effy.audio.types import AudioSpec, AudioFormat
        
        if spec is None:
            spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=1024)

        if sys.platform != "win32":
            sys.stderr.write("Warning: Failed to initialize native audio hardware (WASAPI). Falling back to dummy device.\n")
            device = WindowsAudioDevice(
                backend_type="dummy",
                audio_client=None,
                render_client=None,
                spec=spec,
                hardware_spec=spec,
                buffer_size=0
            )
            handle_id = PlatformAudioHandle(self._next_audio_id)
            self._next_audio_id += 1
            self._audio_devices[handle_id] = device
            return Ok(handle_id)

        enumerator_ptr = ctypes.c_void_p()
        device_ptr = ctypes.c_void_p()
        audio_client_ptr = ctypes.c_void_p()
        render_client_ptr = ctypes.c_void_p()

        try:
            windll.ole32.CoInitialize(None)

            clsid_enumerator = GUID("{BCDE0359-4F65-4CF6-87B7-8539B5586A93}")
            iid_enumerator = GUID("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
            
            hr = windll.ole32.CoCreateInstance(
                ctypes.byref(clsid_enumerator),
                None,
                23,  # CLSCTX_ALL
                ctypes.byref(iid_enumerator),
                ctypes.byref(enumerator_ptr)
            )
            if hr < 0 or not enumerator_ptr.value:
                raise RuntimeError("Failed to create MMDeviceEnumerator")

            hr = call_com_method(
                enumerator_ptr,
                4,  # GetDefaultAudioEndpoint
                [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)],
                0,  # eRender
                0,  # eConsole
                ctypes.byref(device_ptr)
            )
            if hr < 0 or not device_ptr.value:
                raise RuntimeError("Failed to get default audio endpoint")

            iid_audio_client = GUID("{1CB9AD4C-DBFA-4c53-B178-C2F54517A11C}")
            hr = call_com_method(
                device_ptr,
                3,  # Activate
                [ctypes.POINTER(GUID), ctypes.c_ulong, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)],
                ctypes.byref(iid_audio_client),
                23,  # CLSCTX_ALL
                None,
                ctypes.byref(audio_client_ptr)
            )
            if hr < 0 or not audio_client_ptr.value:
                raise RuntimeError("Failed to activate IAudioClient")

            wave_format_ptr = ctypes.POINTER(WAVEFORMATEX)()
            hr = call_com_method(
                audio_client_ptr,
                8,  # GetMixFormat
                [ctypes.POINTER(ctypes.POINTER(WAVEFORMATEX))],
                ctypes.byref(wave_format_ptr)
            )
            if hr < 0 or not wave_format_ptr:
                raise RuntimeError("Failed to get mix format")

            wfx = wave_format_ptr.contents
            hw_freq = wfx.nSamplesPerSec
            hw_channels = wfx.nChannels
            if wfx.wFormatTag == 3:
                hw_format = AudioFormat.F32
            elif wfx.wFormatTag == 1:
                hw_format = AudioFormat.S16 if wfx.wBitsPerSample == 16 else AudioFormat.F32
            elif wfx.wFormatTag == 0xFFFE:
                wfe = ctypes.cast(wave_format_ptr, ctypes.POINTER(WAVEFORMATEXTENSIBLE)).contents
                if wfe.SubFormat.Data1 == 3:
                    hw_format = AudioFormat.F32
                else:
                    hw_format = AudioFormat.S16 if wfx.wBitsPerSample == 16 else AudioFormat.F32
            else:
                hw_format = AudioFormat.F32

            hw_spec = AudioSpec(freq=hw_freq, format=hw_format, channels=hw_channels, samples=spec.samples)

            hr = call_com_method(
                audio_client_ptr,
                3,  # Initialize
                [ctypes.c_int, ctypes.c_ulong, ctypes.c_longlong, ctypes.c_longlong, ctypes.POINTER(WAVEFORMATEX), ctypes.c_void_p],
                0,  # AUDCLNT_SHAREMODE_SHARED
                0,
                1000000,  # hBufferDuration (100ms)
                0,
                wave_format_ptr,
                None
            )
            windll.ole32.CoTaskMemFree(wave_format_ptr)
            if hr < 0:
                raise RuntimeError("Failed to initialize IAudioClient")

            buffer_size = ctypes.c_uint32(0)
            hr = call_com_method(
                audio_client_ptr,
                4,  # GetBufferSize
                [ctypes.POINTER(ctypes.c_uint32)],
                ctypes.byref(buffer_size)
            )
            if hr < 0:
                raise RuntimeError("Failed to get IAudioClient buffer size")

            iid_audio_render_client = GUID("{F294ACFC-3146-4483-A7BF-ADDCA7C260E2}")
            hr = call_com_method(
                audio_client_ptr,
                14,  # GetService
                [ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)],
                ctypes.byref(iid_audio_render_client),
                ctypes.byref(render_client_ptr)
            )
            if hr < 0 or not render_client_ptr.value:
                raise RuntimeError("Failed to get IAudioRenderClient service")

            # Pre-fill buffer with silence
            p_data = ctypes.c_void_p()
            hr = call_com_method(
                render_client_ptr,
                3,  # GetBuffer
                [ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p)],
                buffer_size.value,
                ctypes.byref(p_data)
            )
            if hr >= 0 and p_data.value:
                bytes_per_sample = 2 if hw_spec.format == AudioFormat.S16 else 4
                silence_bytes = b"\x00" * (buffer_size.value * hw_spec.channels * bytes_per_sample)
                ctypes.memmove(p_data, silence_bytes, len(silence_bytes))
                call_com_method(
                    render_client_ptr,
                    4,  # ReleaseBuffer
                    [ctypes.c_uint32, ctypes.c_ulong],
                    buffer_size.value,
                    0
                )

            hr = call_com_method(audio_client_ptr, 10, [])  # Start
            if hr < 0:
                raise RuntimeError("Failed to start IAudioClient")

            # Clean up intermediate enumerator & device pointers
            call_com_method(device_ptr, 2, [])
            call_com_method(enumerator_ptr, 2, [])

            device = WindowsAudioDevice(
                backend_type="wasapi",
                audio_client=audio_client_ptr,
                render_client=render_client_ptr,
                spec=spec,
                hardware_spec=hw_spec,
                buffer_size=buffer_size.value
            )
            handle_id = PlatformAudioHandle(self._next_audio_id)
            self._next_audio_id += 1
            self._audio_devices[handle_id] = device
            return Ok(handle_id)

        except Exception:
            sys.stderr.write("Warning: Failed to initialize native audio hardware (WASAPI). Falling back to dummy device.\n")

            if render_client_ptr.value:
                call_com_method(render_client_ptr, 2, [])
            if audio_client_ptr.value:
                call_com_method(audio_client_ptr, 2, [])
            if device_ptr.value:
                call_com_method(device_ptr, 2, [])
            if enumerator_ptr.value:
                call_com_method(enumerator_ptr, 2, [])

            device = WindowsAudioDevice(
                backend_type="dummy",
                audio_client=None,
                render_client=None,
                spec=spec,
                hardware_spec=spec,
                buffer_size=0
            )
            handle_id = PlatformAudioHandle(self._next_audio_id)
            self._next_audio_id += 1
            self._audio_devices[handle_id] = device
            return Ok(handle_id)

    def write_audio(self, handle: PlatformAudioHandle, data: bytes) -> None:
        """Write raw mixed audio frames to the physical output hardware."""
        if not hasattr(self, "_audio_devices"):
            return
        device = self._audio_devices.get(handle)
        if not device or device.backend_type != "wasapi":
            return

        from Effy.audio.types import AudioFormat, AudioBuffer, AudioSpec
        from Effy.audio.convert import convert_audio

        buf = AudioBuffer.from_bytes(device.spec, data)
        if device.spec != device.hardware_spec:
            target_samples = int(device.spec.samples * (device.hardware_spec.freq / device.spec.freq))
            target_spec = AudioSpec(
                freq=device.hardware_spec.freq,
                format=device.hardware_spec.format,
                channels=device.hardware_spec.channels,
                samples=target_samples
            )
            buf = convert_audio(buf, target_spec)
            converted_data = bytes(buf._data)
        else:
            converted_data = data

        bytes_per_sample = 2 if device.hardware_spec.format == AudioFormat.S16 else 4
        bytes_per_frame = device.hardware_spec.channels * bytes_per_sample
        frames_to_write = len(converted_data) // bytes_per_frame

        padding = ctypes.c_uint32(0)
        hr = call_com_method(
            device.audio_client,
            6,  # GetCurrentPadding
            [ctypes.POINTER(ctypes.c_uint32)],
            ctypes.byref(padding)
        )
        if hr < 0:
            return

        available_frames = device.buffer_size - padding.value
        write_len = min(frames_to_write, available_frames)

        if write_len > 0:
            p_data = ctypes.c_void_p()
            hr = call_com_method(
                device.render_client,
                3,  # GetBuffer
                [ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p)],
                write_len,
                ctypes.byref(p_data)
            )
            if hr >= 0 and p_data.value:
                write_bytes_count = write_len * bytes_per_frame
                ctypes.memmove(p_data, converted_data[:write_bytes_count], write_bytes_count)
                call_com_method(
                    device.render_client,
                    4,  # ReleaseBuffer
                    [ctypes.c_uint32, ctypes.c_ulong],
                    write_len,
                    0
                )

    def close_audio(self, handle: PlatformAudioHandle) -> None:
        """Close the native Windows audio hardware playback output."""
        if not hasattr(self, "_audio_devices"):
            return
        device = self._audio_devices.pop(handle, None)
        if not device or device.backend_type != "wasapi":
            return

        call_com_method(device.audio_client, 11, [])  # Stop
        call_com_method(device.render_client, 2, [])  # Release
        call_com_method(device.audio_client, 2, [])  # Release

    def get_keyboard_state(self) -> Any:
        """Return the current keyboard state as a frozen set of pressed scancodes."""
        from Effy.input.keyboard import KeyboardState
        return KeyboardState(pressed_keys=frozenset(self._pressed_keys))

    def get_mouse_state(self) -> Any:
        """Return the current mouse position and button state."""
        from Effy.input.mouse import MouseState
        from Effy.events.types import MouseButton
        buttons = self._mouse_buttons if self._mouse_buttons is not None else MouseButton.NONE
        return MouseState(x=self._mouse_x, y=self._mouse_y, buttons=buttons)

    def get_touch_state(self) -> Any:
        """Return the current state of all registered touch devices."""
        from Effy.input.touch import TouchState, TouchDeviceState
        devices = []
        for dev_id, fingers in self._touch_devices.items():
            devices.append(TouchDeviceState(device_id=dev_id, fingers=frozenset(fingers)))
        return TouchState(devices=frozenset(devices))

    def get_gamepad_state(self) -> Any:
        """Return the current gamepad snapshot state via XInput."""
        from Effy.input.gamepad import GamepadState, GamepadDeviceState, GamepadButton, GamepadAxis
        devices: list[GamepadDeviceState] = []
        if sys.platform == "win32" and _xinput_dll and _XInputGetState:
            for i in range(4):
                state = XINPUT_STATE()
                if _XInputGetState(i, ctypes.byref(state)) == 0:
                    gp = state.Gamepad
                    buttons = set()
                    if gp.wButtons & 0x1000:
                        buttons.add(GamepadButton.A)
                    if gp.wButtons & 0x2000:
                        buttons.add(GamepadButton.B)
                    if gp.wButtons & 0x4000:
                        buttons.add(GamepadButton.X)
                    if gp.wButtons & 0x8000:
                        buttons.add(GamepadButton.Y)
                    if gp.wButtons & 0x0010:
                        buttons.add(GamepadButton.START)
                    if gp.wButtons & 0x0020:
                        buttons.add(GamepadButton.BACK)
                    if gp.wButtons & 0x0040:
                        buttons.add(GamepadButton.LEFT_STICK)
                    if gp.wButtons & 0x0080:
                        buttons.add(GamepadButton.RIGHT_STICK)
                    if gp.wButtons & 0x0100:
                        buttons.add(GamepadButton.LEFT_SHOULDER)
                    if gp.wButtons & 0x0200:
                        buttons.add(GamepadButton.RIGHT_SHOULDER)
                    if gp.wButtons & 0x0001:
                        buttons.add(GamepadButton.DPAD_UP)
                    if gp.wButtons & 0x0002:
                        buttons.add(GamepadButton.DPAD_DOWN)
                    if gp.wButtons & 0x0004:
                        buttons.add(GamepadButton.DPAD_LEFT)
                    if gp.wButtons & 0x0008:
                        buttons.add(GamepadButton.DPAD_RIGHT)
                    
                    axes = {}
                    axes[GamepadAxis.LEFTX] = max(-1.0, gp.sThumbLX / 32767.0)
                    axes[GamepadAxis.LEFTY] = max(-1.0, gp.sThumbLY / 32767.0)
                    axes[GamepadAxis.RIGHTX] = max(-1.0, gp.sThumbRX / 32767.0)
                    axes[GamepadAxis.RIGHTY] = max(-1.0, gp.sThumbRY / 32767.0)
                    axes[GamepadAxis.TRIGGERLEFT] = gp.bLeftTrigger / 255.0
                    axes[GamepadAxis.TRIGGERRIGHT] = gp.bRightTrigger / 255.0
                    
                    devices.append(GamepadDeviceState(
                        device_id=i,
                        name=f"XInput Controller {i}",
                        pressed_buttons=frozenset(buttons),
                        axes=frozenset(axes.items())
                    ))
        return GamepadState(devices=frozenset(devices))

    def set_clipboard_text(self, text: str) -> None:
        """Set text in the Windows system clipboard using ctypes or in-memory fallback."""
        self._clipboard_text = text
        if sys.platform != "win32":
            return
        try:
            import ctypes
            user32 = windll.user32
            kernel32 = windll.kernel32
            if user32.OpenClipboard(0):
                try:
                    user32.EmptyClipboard()
                    CF_UNICODETEXT = 13
                    GMEM_MOVEABLE = 0x0002
                    size = (len(text) + 1) * 2
                    h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
                    if h_mem:
                        p_mem = kernel32.GlobalLock(h_mem)
                        if p_mem:
                            ctypes.memmove(p_mem, ctypes.c_wchar_p(text), size)
                            kernel32.GlobalUnlock(h_mem)
                            user32.SetClipboardData(CF_UNICODETEXT, h_mem)
                finally:
                    user32.CloseClipboard()
        except Exception:
            pass

    def get_clipboard_data(self, mime_type: str) -> Result[bytes, SDLError]:
        """Get binary data for a specific MIME type from the Windows clipboard using in-memory fallback."""
        if mime_type in self._clipboard_data:
            return Ok(self._clipboard_data[mime_type])
        return Err(SDLError(code=-1, message=f"MIME type '{mime_type}' not found in clipboard"))

    def set_clipboard_data(self, mime_type: str, data: bytes) -> Result[None, SDLError]:
        """Set binary data for a specific MIME type in the Windows clipboard using in-memory fallback."""
        self._clipboard_data[mime_type] = data
        return Ok(None)

    def get_num_video_displays(self) -> int:
        """Return the number of connected video displays."""
        if sys.platform == "win32":
            try:
                num = windll.user32.GetSystemMetrics(80)  # SM_CMONITORS
                return int(max(1, num))
            except Exception:
                pass
        return 1

    def get_display_name(self, index: int) -> str:
        """Return the name of the specified display."""
        return f"Windows Display {index}"

    def get_display_bounds(self, index: int) -> Rect:
        """Return the bounding rectangle of the display."""
        from Effy.video.rect import Rect
        w, h = 1920, 1080
        if sys.platform == "win32":
            try:
                w = windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
                h = windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
            except Exception:
                pass
        return Rect(0, 0, w, h)

    def set_window_size(self, handle: Any, w: int, h: int) -> None:
        """Resize the native window programmatically."""
        if sys.platform == "win32":
            SWP_NOMOVE = 0x0002
            SWP_NOZORDER = 0x0004
            SWP_NOACTIVATE = 0x0010
            windll.user32.SetWindowPos(handle, None, 0, 0, w, h, SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE)

    def set_window_position(self, handle: Any, x: int, y: int) -> None:
        """Set window coordinates programmatically."""
        if sys.platform == "win32":
            SWP_NOSIZE = 0x0001
            SWP_NOZORDER = 0x0004
            SWP_NOACTIVATE = 0x0010
            windll.user32.SetWindowPos(handle, None, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)

    def minimize_window(self, handle: Any) -> None:
        """Minimize the native window."""
        if sys.platform == "win32":
            windll.user32.ShowWindow(handle, 6)  # SW_MINIMIZE

    def maximize_window(self, handle: Any) -> None:
        """Maximize the native window."""
        if sys.platform == "win32":
            windll.user32.ShowWindow(handle, 3)  # SW_SHOWMAXIMIZED

    def restore_window(self, handle: Any) -> None:
        """Restore the minimized or maximized window."""
        if sys.platform == "win32":
            windll.user32.ShowWindow(handle, 9)  # SW_RESTORE

    def show_window(self, handle: Any) -> None:
        """Make the native window visible."""
        if sys.platform == "win32":
            windll.user32.ShowWindow(handle, 5)  # SW_SHOW

    def hide_window(self, handle: Any) -> None:
        """Hide the native window."""
        if sys.platform == "win32":
            windll.user32.ShowWindow(handle, 0)  # SW_HIDE

    def get_clipboard_text(self) -> str:
        """Get text from the Windows system clipboard using ctypes or in-memory fallback."""
        if sys.platform != "win32":
            return self._clipboard_text
        try:
            user32 = windll.user32
            kernel32 = windll.kernel32
            if user32.OpenClipboard(0):
                try:
                    CF_UNICODETEXT = 13
                    h_mem = user32.GetClipboardData(CF_UNICODETEXT)
                    if h_mem:
                        p_mem = kernel32.GlobalLock(h_mem)
                        if p_mem:
                            text = ctypes.c_wchar_p(p_mem).value or ""
                            kernel32.GlobalUnlock(h_mem)
                            self._clipboard_text = text
                            return text
                finally:
                    user32.CloseClipboard()
        except Exception:
            pass
        return self._clipboard_text

    def get_sensor_state(self) -> SensorState:
        """Return a snapshot of the current sensor readings (fallback)."""
        from Effy.input.sensors import SensorState
        return SensorState(devices=frozenset())

    def open_haptic(self, device_id: int) -> Result[PlatformHapticHandle, SDLError]:
        """Open a haptic device."""
        from Effy.platform import PlatformHapticHandle
        if not hasattr(self, "_haptics_opened"):
            self._haptics_opened = set()
        self._haptics_opened.add(device_id)
        return Ok(PlatformHapticHandle(device_id))

    def close_haptic(self, handle: PlatformHapticHandle) -> None:
        """Close an opened haptic device."""
        if hasattr(self, "_haptics_opened"):
            self._haptics_opened.discard(int(handle))

    def is_rumble_supported(self, handle: PlatformHapticHandle) -> bool:
        """Check if simple rumble is supported."""
        return False

    def play_rumble(
        self, handle: PlatformHapticHandle, strength: float, duration_ms: int
    ) -> Result[None, SDLError]:
        """Play a simple rumble effect."""
        return Err(SDLError(code=-1, message="Rumble not supported on Windows GDI stub"))

    def stop_rumble(self, handle: PlatformHapticHandle) -> Result[None, SDLError]:
        """Stop rumble playback."""
        return Err(SDLError(code=-1, message="Rumble not supported on Windows GDI stub"))

    def upload_effect(
        self, handle: PlatformHapticHandle, effect: HapticEffect
    ) -> Result[int, SDLError]:
        """Upload a custom haptic effect."""
        return Err(SDLError(code=-1, message="Haptic custom effects not supported on Windows GDI stub"))

    def run_effect(
        self, handle: PlatformHapticHandle, effect_id: int, iterations: int
    ) -> Result[None, SDLError]:
        """Run an uploaded custom haptic effect."""
        return Err(SDLError(code=-1, message="Haptic custom effects not supported on Windows GDI stub"))

    def stop_effect(
        self, handle: PlatformHapticHandle, effect_id: int
    ) -> Result[None, SDLError]:
        """Stop playback of a custom haptic effect."""
        return Err(SDLError(code=-1, message="Haptic custom effects not supported on Windows GDI stub"))

    def destroy_effect(self, handle: PlatformHapticHandle, effect_id: int) -> None:
        """Destroy an uploaded haptic effect."""
        pass

    def present_accelerated(self, handle: Any, commands: list[Any], width: int, height: int) -> Result[None, SDLError]:
        """Hardware-accelerated rendering stub. Windows GDI does not support accelerated presentation."""
        return Err(SDLError(code=-1, message="Hardware acceleration not supported on this platform"))
