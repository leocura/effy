from __future__ import annotations
import sys
import ctypes
from typing import Any, TYPE_CHECKING
from Effy._internal.result import Ok, Err, Result
from Effy.error import SDLError
from Effy.platform import PlatformAudioHandle

if TYPE_CHECKING:
    from Effy.platform import PlatformHapticHandle
    from Effy.audio.types import AudioSpec

# X11 Constants
ZPixmap = 2

class XAnyEvent(ctypes.Structure):
    """X11 basic event structure."""
    _fields_ = [
        ("type", ctypes.c_int),
        ("serial", ctypes.c_ulong),
        ("send_event", ctypes.c_bool),
        ("display", ctypes.c_void_p),
        ("window", ctypes.c_ulong),
    ]

class XKeyEvent(ctypes.Structure):
    """X11 key event structure."""
    _fields_ = [
        ("type", ctypes.c_int),
        ("serial", ctypes.c_ulong),
        ("send_event", ctypes.c_bool),
        ("display", ctypes.c_void_p),
        ("window", ctypes.c_ulong),
        ("root", ctypes.c_ulong),
        ("subwindow", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("x_root", ctypes.c_int),
        ("y_root", ctypes.c_int),
        ("state", ctypes.c_uint),
        ("keycode", ctypes.c_uint),
        ("same_screen", ctypes.c_bool),
    ]

class XButtonEvent(ctypes.Structure):
    """X11 button event structure."""
    _fields_ = [
        ("type", ctypes.c_int),
        ("serial", ctypes.c_ulong),
        ("send_event", ctypes.c_bool),
        ("display", ctypes.c_void_p),
        ("window", ctypes.c_ulong),
        ("root", ctypes.c_ulong),
        ("subwindow", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("x_root", ctypes.c_int),
        ("y_root", ctypes.c_int),
        ("state", ctypes.c_uint),
        ("button", ctypes.c_uint),
        ("same_screen", ctypes.c_bool),
    ]

class XMotionEvent(ctypes.Structure):
    """X11 mouse motion event structure."""
    _fields_ = [
        ("type", ctypes.c_int),
        ("serial", ctypes.c_ulong),
        ("send_event", ctypes.c_bool),
        ("display", ctypes.c_void_p),
        ("window", ctypes.c_ulong),
        ("root", ctypes.c_ulong),
        ("subwindow", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("x_root", ctypes.c_int),
        ("y_root", ctypes.c_int),
        ("state", ctypes.c_uint),
        ("is_hint", ctypes.c_char),
        ("same_screen", ctypes.c_bool),
    ]

class XConfigureEvent(ctypes.Structure):
    """X11 configuration/resize event structure."""
    _fields_ = [
        ("type", ctypes.c_int),
        ("serial", ctypes.c_ulong),
        ("send_event", ctypes.c_bool),
        ("display", ctypes.c_void_p),
        ("event", ctypes.c_ulong),
        ("window", ctypes.c_ulong),
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("width", ctypes.c_int),
        ("height", ctypes.c_int),
        ("border_width", ctypes.c_int),
        ("above", ctypes.c_ulong),
        ("override_redirect", ctypes.c_bool),
    ]

class XClientMessageData(ctypes.Union):
    """X11 client message union representation."""
    _fields_ = [
        ("b", ctypes.c_char * 20),
        ("s", ctypes.c_short * 10),
        ("l", ctypes.c_long * 5),
    ]

class XClientMessageEvent(ctypes.Structure):
    """X11 client message event structure."""
    _fields_ = [
        ("type", ctypes.c_int),
        ("serial", ctypes.c_ulong),
        ("send_event", ctypes.c_bool),
        ("display", ctypes.c_void_p),
        ("window", ctypes.c_ulong),
        ("message_type", ctypes.c_ulong),
        ("format", ctypes.c_int),
        ("data", XClientMessageData),
    ]

class XEvent(ctypes.Union):
    """Union type representing all possible X11 events."""
    _fields_ = [
        ("type", ctypes.c_int),
        ("xany", XAnyEvent),
        ("xkey", XKeyEvent),
        ("xbutton", XButtonEvent),
        ("xmotion", XMotionEvent),
        ("xconfigure", XConfigureEvent),
        ("xclient", XClientMessageEvent),
        ("pad", ctypes.c_byte * 192),
    ]

class XImageFuncs(ctypes.Structure):
    """X11 XImage function pointer routines."""
    _fields_ = [
        ("create_image", ctypes.c_void_p),
        ("destroy_image", ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)),
        ("get_pixel", ctypes.c_void_p),
        ("put_pixel", ctypes.c_void_p),
        ("sub_image", ctypes.c_void_p),
        ("add_pixel", ctypes.c_void_p),
    ]

class XImage(ctypes.Structure):
    """X11 image structure for software buffering."""
    _fields_ = [
        ("width", ctypes.c_int),
        ("height", ctypes.c_int),
        ("xoffset", ctypes.c_int),
        ("format", ctypes.c_int),
        ("data", ctypes.c_void_p),
        ("byte_order", ctypes.c_int),
        ("bitmap_unit", ctypes.c_int),
        ("bitmap_bit_order", ctypes.c_int),
        ("bitmap_pad", ctypes.c_int),
        ("depth", ctypes.c_int),
        ("bytes_per_line", ctypes.c_int),
        ("bits_per_pixel", ctypes.c_int),
        ("red_mask", ctypes.c_ulong),
        ("green_mask", ctypes.c_ulong),
        ("blue_mask", ctypes.c_ulong),
        ("obdata", ctypes.c_void_p),
        ("f", XImageFuncs),
    ]

class XVisualInfo(ctypes.Structure):
    """X11 Visual Info structure."""
    _fields_ = [
        ("visual", ctypes.c_void_p),
        ("visualid", ctypes.c_ulong),
        ("screen", ctypes.c_int),
        ("depth", ctypes.c_int),
        ("class_val", ctypes.c_int),
        ("red_mask", ctypes.c_ulong),
        ("green_mask", ctypes.c_ulong),
        ("blue_mask", ctypes.c_ulong),
        ("colormap_size", ctypes.c_int),
        ("bits_per_rgb", ctypes.c_int),
    ]

class XSetWindowAttributes(ctypes.Structure):
    """XSetWindowAttributes structure."""
    _fields_ = [
        ("background_pixmap", ctypes.c_ulong),
        ("background_pixel", ctypes.c_ulong),
        ("border_pixmap", ctypes.c_ulong),
        ("border_pixel", ctypes.c_ulong),
        ("bit_gravity", ctypes.c_int),
        ("win_gravity", ctypes.c_int),
        ("backing_store", ctypes.c_int),
        ("backing_planes", ctypes.c_ulong),
        ("backing_pixel", ctypes.c_ulong),
        ("save_under", ctypes.c_bool),
        ("event_mask", ctypes.c_long),
        ("do_not_propagate_mask", ctypes.c_long),
        ("override_redirect", ctypes.c_bool),
        ("colormap", ctypes.c_ulong),
        ("cursor", ctypes.c_ulong),
    ]

# Linux Audio Output Integration - PulseAudio & ALSA ctypes definitions
_pulse: ctypes.CDLL | None

try:
    _pulse = ctypes.CDLL("libpulse-simple.so.0")
except OSError:
    _pulse = None

if _pulse:
    class pa_sample_spec(ctypes.Structure):
        """PulseAudio sample specification structure."""
        _fields_ = [
            ("format", ctypes.c_int),
            ("rate", ctypes.c_uint32),
            ("channels", ctypes.c_uint8),
        ]
    
    _pulse.pa_simple_new.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(pa_sample_spec),
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_int)
    ]
    _pulse.pa_simple_new.restype = ctypes.c_void_p
    
    _pulse.pa_simple_write.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int)
    ]
    _pulse.pa_simple_write.restype = ctypes.c_int
    
    _pulse.pa_simple_free.argtypes = [
        ctypes.c_void_p
    ]
    _pulse.pa_simple_free.restype = None

_asound: ctypes.CDLL | None
try:
    _asound = ctypes.CDLL("libasound.so.2")
except OSError:
    _asound = None

if _asound:
    _asound.snd_pcm_open.argtypes = [
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_int
    ]
    _asound.snd_pcm_open.restype = ctypes.c_int
    
    _asound.snd_pcm_hw_params_malloc.argtypes = [
        ctypes.POINTER(ctypes.c_void_p)
    ]
    _asound.snd_pcm_hw_params_malloc.restype = ctypes.c_int
    
    _asound.snd_pcm_hw_params_any.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p
    ]
    _asound.snd_pcm_hw_params_any.restype = ctypes.c_int
    
    _asound.snd_pcm_hw_params_set_access.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_int
    ]
    _asound.snd_pcm_hw_params_set_access.restype = ctypes.c_int
    
    _asound.snd_pcm_hw_params_set_format.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_int
    ]
    _asound.snd_pcm_hw_params_set_format.restype = ctypes.c_int
    
    _asound.snd_pcm_hw_params_set_channels.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint
    ]
    _asound.snd_pcm_hw_params_set_channels.restype = ctypes.c_int
    
    _asound.snd_pcm_hw_params_set_rate_near.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint),
        ctypes.POINTER(ctypes.c_int)
    ]
    _asound.snd_pcm_hw_params_set_rate_near.restype = ctypes.c_int
    
    _asound.snd_pcm_hw_params.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p
    ]
    _asound.snd_pcm_hw_params.restype = ctypes.c_int
    
    _asound.snd_pcm_hw_params_free.argtypes = [
        ctypes.c_void_p
    ]
    _asound.snd_pcm_hw_params_free.restype = None
    
    _asound.snd_pcm_writei.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_ulong
    ]
    _asound.snd_pcm_writei.restype = ctypes.c_long
    
    _asound.snd_pcm_recover.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_int
    ]
    _asound.snd_pcm_recover.restype = ctypes.c_int
    
    _asound.snd_pcm_close.argtypes = [
        ctypes.c_void_p
    ]
    _asound.snd_pcm_close.restype = ctypes.c_int


class LinuxAudioDevice:
    """Native audio hardware output device representation for Linux systems."""
    
    def __init__(self, backend_type: str, handle: Any, spec: Any) -> None:
        """Initialize the Linux native audio playback device wrapper.
        
        Args:
            backend_type: The string identifier of the backend (e.g. 'pulseaudio', 'alsa', 'dummy').
            handle: The native device handle object or None for dummy backend.
            spec: The AudioSpec specification used to open the device.
        """
        self.backend_type: str = backend_type
        self.handle: Any = handle
        self.spec: Any = spec


class LinuxX11Adapter:
    """Linux X11 Platform Adapter interacting directly with libX11.so."""
    
    def __init__(self) -> None:
        """Initialize the X11 platform adapter instance."""
        from Effy.events.queue import EventQueue
        self._pending_events: EventQueue = EventQueue.empty()
        self._pressed_keys: set[Any] = set()
        self._mouse_x: int = 0
        self._mouse_y: int = 0
        self._mouse_buttons: Any = None
        self._touch_devices: dict[int, set[Any]] = {}
        self._display: Any = None
        self._screen: int = 0
        self._root: int = 0
        self._x11: Any = None
        self._wm_protocols: int = 0
        self._wm_delete_window: int = 0
        self._windows: dict[int, dict[str, Any]] = {}
        self._clipboard_text: str = ""
        self._clipboard_data: dict[str, bytes] = {}
        self._audio_devices: dict[PlatformAudioHandle, Any] = {}
        self._next_audio_id: int = 1
        self._x11_gl: Any = None
        self._gl_contexts: dict[int, Any] = {}
        self._gl_texture_cache: dict[int, tuple[int, int, int]] = {}



    @classmethod
    def detect(cls) -> bool:
        """Detect if running under Linux platform."""
        return sys.platform == "linux"

    def _init_gl_functions(self) -> None:
        """Bind argtypes and restypes for all required OpenGL and GLX functions."""
        if not self._x11_gl:
            return
            
        gl = self._x11_gl
        
        # GLX bindings
        gl.glXChooseVisual.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        gl.glXChooseVisual.restype = ctypes.c_void_p
        
        gl.glXCreateContext.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
        gl.glXCreateContext.restype = ctypes.c_void_p
        
        gl.glXMakeCurrent.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p]
        gl.glXMakeCurrent.restype = ctypes.c_int
        
        gl.glXSwapBuffers.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        gl.glXSwapBuffers.restype = None
        
        gl.glXDestroyContext.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        gl.glXDestroyContext.restype = None
        
        # OpenGL Primitives bindings
        gl.glViewport.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        gl.glViewport.restype = None
        
        gl.glClearColor.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float]
        gl.glClearColor.restype = None
        
        gl.glClear.argtypes = [ctypes.c_uint]
        gl.glClear.restype = None
        
        gl.glMatrixMode.argtypes = [ctypes.c_uint]
        gl.glMatrixMode.restype = None
        
        gl.glLoadIdentity.argtypes = []
        gl.glLoadIdentity.restype = None
        
        gl.glOrtho.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
        gl.glOrtho.restype = None
        
        gl.glColor4ub.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte]
        gl.glColor4ub.restype = None
        
        gl.glBegin.argtypes = [ctypes.c_uint]
        gl.glBegin.restype = None
        
        gl.glEnd.argtypes = []
        gl.glEnd.restype = None
        
        gl.glVertex2f.argtypes = [ctypes.c_float, ctypes.c_float]
        gl.glVertex2f.restype = None
        
        gl.glEnable.argtypes = [ctypes.c_uint]
        gl.glEnable.restype = None
        
        gl.glDisable.argtypes = [ctypes.c_uint]
        gl.glDisable.restype = None
        
        gl.glBlendFunc.argtypes = [ctypes.c_uint, ctypes.c_uint]
        gl.glBlendFunc.restype = None
        
        gl.glGenTextures.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
        gl.glGenTextures.restype = None
        
        gl.glDeleteTextures.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
        gl.glDeleteTextures.restype = None
        
        gl.glBindTexture.argtypes = [ctypes.c_uint, ctypes.c_uint]
        gl.glBindTexture.restype = None
        
        gl.glTexImage2D.argtypes = [
            ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p
        ]
        gl.glTexImage2D.restype = None
        
        gl.glTexParameteri.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_int]
        gl.glTexParameteri.restype = None
        
        gl.glTexCoord2f.argtypes = [ctypes.c_float, ctypes.c_float]
        gl.glTexCoord2f.restype = None


    def init_video(self) -> Result[Any, SDLError]:
        """Connect to the X display and prepare the video system."""
        try:
            self._x11 = ctypes.cdll.LoadLibrary("libX11.so")
        except Exception as e:
            return Err(SDLError(code=-1, message=f"Failed to load libX11.so: {e}"))

        self._x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        self._x11.XOpenDisplay.restype = ctypes.c_void_p
        self._x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
        self._x11.XCloseDisplay.restype = ctypes.c_int
        self._x11.XDefaultScreen.argtypes = [ctypes.c_void_p]
        self._x11.XDefaultScreen.restype = ctypes.c_int
        self._x11.XRootWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._x11.XRootWindow.restype = ctypes.c_ulong
        self._x11.XBlackPixel.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._x11.XBlackPixel.restype = ctypes.c_ulong
        self._x11.XWhitePixel.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._x11.XWhitePixel.restype = ctypes.c_ulong
        
        self._x11.XCreateSimpleWindow.argtypes = [
            ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int,
            ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_ulong, ctypes.c_ulong
        ]
        self._x11.XCreateSimpleWindow.restype = ctypes.c_ulong
        
        self._x11.XSelectInput.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_long]
        self._x11.XSelectInput.restype = ctypes.c_int
        self._x11.XMapWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        self._x11.XMapWindow.restype = ctypes.c_int
        self._x11.XUnmapWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        self._x11.XUnmapWindow.restype = ctypes.c_int
        self._x11.XDestroyWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        self._x11.XDestroyWindow.restype = ctypes.c_int
        self._x11.XStoreName.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_char_p]
        self._x11.XStoreName.restype = ctypes.c_int
        
        self._x11.XCreateGC.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p]
        self._x11.XCreateGC.restype = ctypes.c_void_p
        self._x11.XFreeGC.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self._x11.XFreeGC.restype = ctypes.c_int

        self._x11.XCreateImage.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_int,
            ctypes.c_int, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint,
            ctypes.c_int, ctypes.c_int
        ]
        self._x11.XCreateImage.restype = ctypes.c_void_p

        self._x11.XPutImage.argtypes = [
            ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_uint, ctypes.c_uint
        ]
        self._x11.XPutImage.restype = ctypes.c_int

        self._x11.XPending.argtypes = [ctypes.c_void_p]
        self._x11.XPending.restype = ctypes.c_int
        self._x11.XNextEvent.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self._x11.XNextEvent.restype = ctypes.c_int
        self._x11.XDefaultVisual.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._x11.XDefaultVisual.restype = ctypes.c_void_p
        self._x11.XDefaultDepth.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._x11.XDefaultDepth.restype = ctypes.c_int
        self._x11.XFlush.argtypes = [ctypes.c_void_p]
        self._x11.XFlush.restype = ctypes.c_int

        self._x11.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_bool]
        self._x11.XInternAtom.restype = ctypes.c_ulong
        self._x11.XSetWMProtocols.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong), ctypes.c_int]
        self._x11.XSetWMProtocols.restype = ctypes.c_int
        
        self._x11.XKeycodeToKeysym.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int]
        self._x11.XKeycodeToKeysym.restype = ctypes.c_ulong

        self._x11.XMoveWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int]
        self._x11.XMoveWindow.restype = ctypes.c_int
        self._x11.XResizeWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_uint, ctypes.c_uint]
        self._x11.XResizeWindow.restype = ctypes.c_int
        self._x11.XIconifyWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int]
        self._x11.XIconifyWindow.restype = ctypes.c_int
        self._x11.XMapRaised.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        self._x11.XMapRaised.restype = ctypes.c_int

        self._x11.XCreateColormap.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_int]
        self._x11.XCreateColormap.restype = ctypes.c_ulong

        self._x11.XCreateWindow.argtypes = [
            ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int,
            ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_int,
            ctypes.c_uint, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p
        ]
        self._x11.XCreateWindow.restype = ctypes.c_ulong

        # Try to load libGL.so.1 for hardware acceleration
        try:
            self._x11_gl = ctypes.cdll.LoadLibrary("libGL.so.1")
            self._init_gl_functions()
        except Exception:
            self._x11_gl = None

        display = self._x11.XOpenDisplay(None)

        if not display:
            return Err(SDLError(code=-1, message="Failed to open X display (is DISPLAY env var set?)"))

        self._display = display
        self._screen = self._x11.XDefaultScreen(display)
        self._root = self._x11.XRootWindow(display, self._screen)
        
        # Atoms for WM protocols
        self._wm_protocols = self._x11.XInternAtom(display, b"WM_PROTOCOLS", False)
        self._wm_delete_window = self._x11.XInternAtom(display, b"WM_DELETE_WINDOW", False)

        return Ok(display)

    def quit_video(self, handle: Any) -> None:
        """Close connection to X server and cleanup."""
        if self._x11 and self._display:
            self._x11.XCloseDisplay(self._display)
            self._display = None

    def _choose_gl_visual(self) -> Any:
        """Choose an OpenGL compatible visual from GLX.

        Returns:
            An XVisualInfo object or None.
        """
        if not self._x11_gl:
            return None
        GLX_RGBA = 4
        GLX_DOUBLEBUFFER = 5
        GLX_RED_SIZE = 8
        GLX_GREEN_SIZE = 9
        GLX_BLUE_SIZE = 10
        GLX_ALPHA_SIZE = 11
        GLX_DEPTH_SIZE = 12
        attrs = (ctypes.c_int * 15)(
            GLX_RGBA,
            GLX_DOUBLEBUFFER,
            GLX_RED_SIZE, 8,
            GLX_GREEN_SIZE, 8,
            GLX_BLUE_SIZE, 8,
            GLX_ALPHA_SIZE, 8,
            GLX_DEPTH_SIZE, 24,
            0
        )
        vi_ptr = self._x11_gl.glXChooseVisual(self._display, self._screen, attrs)
        if vi_ptr:
            return ctypes.cast(vi_ptr, ctypes.POINTER(XVisualInfo)).contents
        return None

    def create_window(self, params: Any) -> Result[Any, SDLError]:
        """Create a native X11 window."""
        if not self._display:
            return Err(SDLError(code=-1, message="Video system not initialized"))

        title = getattr(params, "title", "Effy Window")
        x = getattr(params, "x", 0)
        y = getattr(params, "y", 0)
        w = getattr(params, "w", 640)
        h = getattr(params, "h", 480)

        # Check if OpenGL visual can be used
        vi = self._choose_gl_visual()
        
        if vi:
            colormap = self._x11.XCreateColormap(self._display, self._root, vi.visual, 0)
            swa = XSetWindowAttributes()
            swa.colormap = colormap
            swa.event_mask = 1 | 2 | 4 | 8 | 64 | 32768 | 131072
            
            value_mask = (1 << 13) | (1 << 11)
            
            window = self._x11.XCreateWindow(
                self._display, self._root, x, y, w, h, 0,
                vi.depth, 1, # InputOutput
                vi.visual,
                value_mask,
                ctypes.byref(swa)
            )
        else:
            black = self._x11.XBlackPixel(self._display, self._screen)
            white = self._x11.XWhitePixel(self._display, self._screen)
            window = self._x11.XCreateSimpleWindow(
                self._display, self._root, x, y, w, h, 1, black, white
            )

        if not window:
            return Err(SDLError(code=-1, message="Failed to create X11 window"))

        # Set title
        self._x11.XStoreName(self._display, window, title.encode('utf-8'))

        # Set up delete protocol
        protocols_arr = (ctypes.c_ulong * 1)(self._wm_delete_window)
        self._x11.XSetWMProtocols(self._display, window, protocols_arr, 1)

        # Select Event Mask:
        # KeyPress(1) | KeyRelease(2) | ButtonPress(4) | ButtonRelease(8) |
        # PointerMotion(64) | Exposure(32768) | StructureNotify(131072)
        event_mask = 1 | 2 | 4 | 8 | 64 | 32768 | 131072
        self._x11.XSelectInput(self._display, window, event_mask)

        # Show window
        self._x11.XMapWindow(self._display, window)
        self._x11.XFlush(self._display)

        gc = self._x11.XCreateGC(self._display, window, 0, None)
        self._windows[window] = {"gc": gc, "w": w, "h": h, "title": title}

        return Ok(window)


    def destroy_window(self, handle: Any) -> None:
        """Destroy native window and its GC."""
        if self._x11 and self._display:
            if handle in self._windows:
                gc = self._windows[handle]["gc"]
                self._x11.XFreeGC(self._display, gc)
                del self._windows[handle]
            self._x11.XDestroyWindow(self._display, handle)
            self._x11.XFlush(self._display)

    def set_window_title(self, handle: Any, title: str) -> None:
        """Update native window title."""
        if self._x11 and self._display:
            self._x11.XStoreName(self._display, handle, title.encode('utf-8'))
            if handle in self._windows:
                self._windows[handle]["title"] = title
            self._x11.XFlush(self._display)

    def flip_buffer(self, handle: Any, buf: Any) -> None:
        """Perform fast software buffer flipping (RGBA to BGRA) and blit to window.
        
        This implementation uses a stateless, loop-free slice swizzle
        and direct ctypes mapping to achieve optimal rendering performance.
        """
        if not self._x11 or not self._display or handle not in self._windows:
            return

        width = buf.width
        height = buf.height
        gc = self._windows[handle]["gc"]

        visual = self._x11.XDefaultVisual(self._display, self._screen)
        depth = self._x11.XDefaultDepth(self._display, self._screen)

        # Declarative slice swap (RGBA to BGRA)
        swap_buf = bytearray(buf._data)
        swap_buf[0::4], swap_buf[2::4] = swap_buf[2::4], swap_buf[0::4]

        # Zero-copy mapping to ctypes array pointer
        c_array = (ctypes.c_char * len(swap_buf)).from_buffer(swap_buf)

        ximage_ptr = self._x11.XCreateImage(
            self._display, visual, depth, ZPixmap, 0, c_array, width, height, 32, 0
        )
        if not ximage_ptr:
            return

        self._x11.XPutImage(
            self._display, handle, gc, ximage_ptr, 0, 0, 0, 0, width, height
        )
        self._x11.XFlush(self._display)

        ximage = ctypes.cast(ximage_ptr, ctypes.POINTER(XImage)).contents
        ximage.data = None  # Prevent Xlib from freeing the Python-managed swap_buf array
        ximage.f.destroy_image(ximage_ptr)

    def _get_gl_texture(self, src_buffer: Any) -> int:
        """Get or create a cached OpenGL texture ID for the given PixelBuffer.

        Args:
            src_buffer: The source PixelBuffer.

        Returns:
            The OpenGL texture ID.
        """
        buf_id = id(src_buffer)
        if buf_id in self._gl_texture_cache:
            tex_id, w, h = self._gl_texture_cache[buf_id]
            if w == src_buffer.width and h == src_buffer.height:
                return tex_id

        tex_id_var = ctypes.c_uint(0)
        self._x11_gl.glGenTextures(1, ctypes.byref(tex_id_var))
        tex_id = tex_id_var.value

        self._x11_gl.glBindTexture(0x0DE1, tex_id)

        data_mv = src_buffer._mv
        data_bytes = data_mv.tobytes()

        self._x11_gl.glTexImage2D(
            0x0DE1, 0, 0x1908, src_buffer.width, src_buffer.height, 0,
            0x1908, 0x1401, data_bytes
        )

        self._x11_gl.glTexParameteri(0x0DE1, 0x2801, 0x2600)
        self._x11_gl.glTexParameteri(0x0DE1, 0x2800, 0x2600)

        if len(self._gl_texture_cache) >= 1000:
            for key in list(self._gl_texture_cache.keys())[:100]:
                old_tex_id, _, _ = self._gl_texture_cache.pop(key)
                old_tex_id_var = ctypes.c_uint(old_tex_id)
                self._x11_gl.glDeleteTextures(1, ctypes.byref(old_tex_id_var))

        self._gl_texture_cache[buf_id] = (tex_id, src_buffer.width, src_buffer.height)
        return tex_id

    def present_accelerated(self, handle: Any, commands: list[Any], width: int, height: int) -> Result[None, SDLError]:
        """Present the deferred commands using hardware-accelerated OpenGL/GLX.

        Args:
            handle: Native window handle.
            commands: List of DrawCmd to render.
            width: Width of the render target.
            height: Height of the render target.

        Returns:
            A Result wrapper representing success or failure.
        """
        if not self._x11_gl:
            return Err(SDLError(code=-1, message="OpenGL/GLX not initialized"))

        if handle not in self._gl_contexts:
            vi = self._choose_gl_visual()
            if not vi:
                return Err(SDLError(code=-1, message="Failed to choose GLX visual"))
            gl_context = self._x11_gl.glXCreateContext(self._display, ctypes.byref(vi), None, True)
            if not gl_context:
                return Err(SDLError(code=-1, message="Failed to create GLX context"))
            self._gl_contexts[handle] = gl_context

        gl_context = self._gl_contexts[handle]

        self._x11_gl.glXMakeCurrent(self._display, handle, gl_context)

        self._x11_gl.glViewport(0, 0, width, height)
        self._x11_gl.glMatrixMode(0x1701)
        self._x11_gl.glLoadIdentity()
        self._x11_gl.glOrtho(0.0, float(width), float(height), 0.0, -1.0, 1.0)
        self._x11_gl.glMatrixMode(0x1700)
        self._x11_gl.glLoadIdentity()

        self._x11_gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        self._x11_gl.glClear(0x00004000)

        self._x11_gl.glEnable(0x0BE2)
        self._x11_gl.glBlendFunc(0x0302, 0x0303)

        from Effy.render.commands import (
            FillRectCmd, DrawRectCmd, DrawLineCmd,
            DrawCircleCmd, FillCircleCmd, FillTriangleCmd,
            BlitCmd, BlitBlendedCmd, BlitScaledCmd, BlitBilinearCmd,
            RenderFieldCmd
        )
        import math

        for cmd in commands:
            if isinstance(cmd, FillRectCmd):
                if cmd.rect is None:
                    x1, y1, x2, y2 = 0.0, 0.0, float(width), float(height)
                else:
                    x1 = float(cmd.rect.x)
                    y1 = float(cmd.rect.y)
                    x2 = float(cmd.rect.x + cmd.rect.w)
                    y2 = float(cmd.rect.y + cmd.rect.h)
                self._x11_gl.glColor4ub(cmd.color.r, cmd.color.g, cmd.color.b, cmd.color.a)
                self._x11_gl.glBegin(0x0007)
                self._x11_gl.glVertex2f(x1, y1)
                self._x11_gl.glVertex2f(x2, y1)
                self._x11_gl.glVertex2f(x2, y2)
                self._x11_gl.glVertex2f(x1, y2)
                self._x11_gl.glEnd()

            elif isinstance(cmd, DrawRectCmd):
                x1 = float(cmd.rect.x)
                y1 = float(cmd.rect.y)
                x2 = float(cmd.rect.x + cmd.rect.w)
                y2 = float(cmd.rect.y + cmd.rect.h)
                self._x11_gl.glColor4ub(cmd.color.r, cmd.color.g, cmd.color.b, cmd.color.a)
                self._x11_gl.glBegin(0x0002)
                self._x11_gl.glVertex2f(x1, y1)
                self._x11_gl.glVertex2f(x2, y1)
                self._x11_gl.glVertex2f(x2, y2)
                self._x11_gl.glVertex2f(x1, y2)
                self._x11_gl.glEnd()

            elif isinstance(cmd, DrawLineCmd):
                self._x11_gl.glColor4ub(cmd.color.r, cmd.color.g, cmd.color.b, cmd.color.a)
                self._x11_gl.glBegin(0x0001)
                self._x11_gl.glVertex2f(float(cmd.p1.x), float(cmd.p1.y))
                self._x11_gl.glVertex2f(float(cmd.p2.x), float(cmd.p2.y))
                self._x11_gl.glEnd()

            elif isinstance(cmd, FillTriangleCmd):
                self._x11_gl.glColor4ub(cmd.color.r, cmd.color.g, cmd.color.b, cmd.color.a)
                self._x11_gl.glBegin(0x0004)
                self._x11_gl.glVertex2f(float(cmd.p1.x), float(cmd.p1.y))
                self._x11_gl.glVertex2f(float(cmd.p2.x), float(cmd.p2.y))
                self._x11_gl.glVertex2f(float(cmd.p3.x), float(cmd.p3.y))
                self._x11_gl.glEnd()

            elif isinstance(cmd, (FillCircleCmd, DrawCircleCmd)):
                cx = float(cmd.center.x)
                cy = float(cmd.center.y)
                r = float(cmd.radius)
                self._x11_gl.glColor4ub(cmd.color.r, cmd.color.g, cmd.color.b, cmd.color.a)
                
                num_segments = max(16, int(2.0 * math.pi * r / 2.0))
                if num_segments > 100:
                    num_segments = 100

                if isinstance(cmd, FillCircleCmd):
                    self._x11_gl.glBegin(0x0006)
                    self._x11_gl.glVertex2f(cx, cy)
                    for i in range(num_segments + 1):
                        theta = 2.0 * math.pi * float(i) / float(num_segments)
                        self._x11_gl.glVertex2f(cx + r * math.cos(theta), cy + r * math.sin(theta))
                    self._x11_gl.glEnd()
                else:
                    self._x11_gl.glBegin(0x0002)
                    for i in range(num_segments):
                        theta = 2.0 * math.pi * float(i) / float(num_segments)
                        self._x11_gl.glVertex2f(cx + r * math.cos(theta), cy + r * math.sin(theta))
                    self._x11_gl.glEnd()

            elif isinstance(cmd, (BlitCmd, BlitBlendedCmd, BlitScaledCmd, BlitBilinearCmd)):
                src_buffer = cmd.src_buffer
                
                if cmd.src_rect is None:
                    sx1, sy1, sx2, sy2 = 0.0, 0.0, float(src_buffer.width), float(src_buffer.height)
                else:
                    sx1 = float(cmd.src_rect.x)
                    sy1 = float(cmd.src_rect.y)
                    sx2 = float(cmd.src_rect.x + cmd.src_rect.w)
                    sy2 = float(cmd.src_rect.y + cmd.src_rect.h)
                
                if cmd.dst_rect is None:
                    dx1, dy1 = 0.0, 0.0
                    dx2, dy2 = float(width), float(height)
                else:
                    dx1 = float(cmd.dst_rect.x)
                    dy1 = float(cmd.dst_rect.y)
                    if isinstance(cmd, (BlitScaledCmd, BlitBilinearCmd)):
                        dx2 = dx1 + float(cmd.dst_rect.w)
                        dy2 = dy1 + float(cmd.dst_rect.h)
                    else:
                        dx2 = dx1 + (sx2 - sx1)
                        dy2 = dy1 + (sy2 - sy1)

                tex_id = self._get_gl_texture(src_buffer)
                self._x11_gl.glEnable(0x0DE1)
                self._x11_gl.glBindTexture(0x0DE1, tex_id)

                if isinstance(cmd, BlitBilinearCmd):
                    self._x11_gl.glTexParameteri(0x0DE1, 0x2801, 0x2601)
                    self._x11_gl.glTexParameteri(0x0DE1, 0x2800, 0x2601)
                else:
                    self._x11_gl.glTexParameteri(0x0DE1, 0x2801, 0x2600)
                    self._x11_gl.glTexParameteri(0x0DE1, 0x2800, 0x2600)

                tex_w = float(src_buffer.width)
                tex_h = float(src_buffer.height)
                s1 = sx1 / tex_w
                t1 = sy1 / tex_h
                s2 = sx2 / tex_w
                t2 = sy2 / tex_h

                self._x11_gl.glColor4ub(255, 255, 255, 255)
                self._x11_gl.glBegin(0x0007)
                self._x11_gl.glTexCoord2f(s1, t1)
                self._x11_gl.glVertex2f(dx1, dy1)
                self._x11_gl.glTexCoord2f(s2, t1)
                self._x11_gl.glVertex2f(dx2, dy1)
                self._x11_gl.glTexCoord2f(s2, t2)
                self._x11_gl.glVertex2f(dx2, dy2)
                self._x11_gl.glTexCoord2f(s1, t2)
                self._x11_gl.glVertex2f(dx1, dy2)
                self._x11_gl.glEnd()
                
                self._x11_gl.glDisable(0x0DE1)

            elif isinstance(cmd, RenderFieldCmd):
                from Effy.video.surface import PixelBuffer
                from Effy._internal.pool import pixel_buffer_pool
                from Effy.render.renderer import _dispatch_render_field

                temp_data = pixel_buffer_pool.get(width, height, zero=True)
                _dispatch_render_field(cmd, temp_data, width, height, width)

                temp_buf = PixelBuffer(
                    width=width,
                    height=height,
                    pitch=width,
                    _data_cache=[temp_data],
                    _commands_list=[],
                    _is_transient=True
                )

                tex_id = self._get_gl_texture(temp_buf)
                self._x11_gl.glEnable(0x0DE1)
                self._x11_gl.glBindTexture(0x0DE1, tex_id)

                self._x11_gl.glTexParameteri(0x0DE1, 0x2801, 0x2600)
                self._x11_gl.glTexParameteri(0x0DE1, 0x2800, 0x2600)

                self._x11_gl.glColor4ub(255, 255, 255, 255)
                self._x11_gl.glBegin(0x0007)
                self._x11_gl.glTexCoord2f(0.0, 0.0)
                self._x11_gl.glVertex2f(0.0, 0.0)
                self._x11_gl.glTexCoord2f(1.0, 0.0)
                self._x11_gl.glVertex2f(float(width), 0.0)
                self._x11_gl.glTexCoord2f(1.0, 1.0)
                self._x11_gl.glVertex2f(float(width), float(height))
                self._x11_gl.glTexCoord2f(0.0, 1.0)
                self._x11_gl.glVertex2f(0.0, float(height))
                self._x11_gl.glEnd()

                self._x11_gl.glDisable(0x0DE1)

                tex_id_var = ctypes.c_uint(tex_id)
                self._x11_gl.glDeleteTextures(1, ctypes.byref(tex_id_var))
                self._gl_texture_cache.pop(id(temp_buf), None)
                pixel_buffer_pool.put(width, height, temp_data)

        self._x11_gl.glXSwapBuffers(self._display, handle)
        return Ok(None)


    def _get_key_mod(self, state: int) -> Any:
        """Convert X11 event state modifier mask to KeyMod flags."""
        from Effy.events.types import KeyMod
        mod = KeyMod.NONE
        if state & (1 << 0): # ShiftMask
            mod |= KeyMod.SHIFT
        if state & (1 << 1): # LockMask (Caps Lock)
            mod |= KeyMod.CAPS
        if state & (1 << 2): # ControlMask
            mod |= KeyMod.LCTRL
        if state & (1 << 3): # Mod1Mask (usually Alt)
            mod |= KeyMod.LALT
        if state & (1 << 4): # Mod2Mask (usually Num Lock)
            mod |= KeyMod.NUM
        if state & (1 << 6): # Mod4Mask (usually Super/Win)
            mod |= KeyMod.LGUI
        return mod

    def pump_events(self) -> None:
        """Process all pending X11 events and push them to the queue."""
        if not self._x11 or not self._display:
            return

        from Effy.events.types import QuitEvent, KeyDownEvent, KeyUpEvent, MouseMotionEvent, MouseButton, WindowEvent, WindowEventID, Scancode, Keycode
        from Effy.types import WindowID

        event = XEvent()
        while self._x11.XPending(self._display) > 0:
            self._x11.XNextEvent(self._display, ctypes.byref(event))

            # 33 = ClientMessage
            if event.type == 33:
                client_ev = ctypes.cast(ctypes.byref(event), ctypes.POINTER(XClientMessageEvent)).contents
                if client_ev.message_type == self._wm_protocols and client_ev.data.l[0] == self._wm_delete_window:
                    self._pending_events = self._pending_events.push(QuitEvent(timestamp=0))

            # 2 = KeyPress, 3 = KeyRelease
            elif event.type in (2, 3):
                key_ev = event.xkey
                scancode = Scancode(key_ev.keycode)
                keysym = self._x11.XKeycodeToKeysym(self._display, key_ev.keycode, 0)
                keycode = Keycode(keysym)
                mod = self._get_key_mod(key_ev.state)

                if event.type == 2:
                    self._pressed_keys.add(scancode)
                    self._pending_events = self._pending_events.push(KeyDownEvent(
                        timestamp=0,
                        window_id=WindowID(key_ev.window),
                        scancode=scancode,
                        keycode=keycode,
                        mod=mod,
                        repeat=False
                    ))
                else:
                    self._pressed_keys.discard(scancode)
                    self._pending_events = self._pending_events.push(KeyUpEvent(
                        timestamp=0,
                        window_id=WindowID(key_ev.window),
                        scancode=scancode,
                        keycode=keycode,
                        mod=mod
                    ))

            # 6 = MotionNotify
            elif event.type == 6:
                motion_ev = event.xmotion
                x = motion_ev.x
                y = motion_ev.y

                xrel = x - self._mouse_x
                yrel = y - self._mouse_y
                self._mouse_x = x
                self._mouse_y = y

                buttons = MouseButton.NONE
                if motion_ev.state & (1 << 8): # Button1
                    buttons |= MouseButton.LEFT
                if motion_ev.state & (1 << 9): # Button2
                    buttons |= MouseButton.MIDDLE
                if motion_ev.state & (1 << 10): # Button3
                    buttons |= MouseButton.RIGHT
                self._mouse_buttons = buttons

                self._pending_events = self._pending_events.push(MouseMotionEvent(
                    timestamp=0,
                    window_id=WindowID(motion_ev.window),
                    x=x,
                    y=y,
                    xrel=xrel,
                    yrel=yrel,
                    buttons=buttons
                ))

            # 22 = ConfigureNotify (resized/moved)
            elif event.type == 22:
                conf_ev = event.xconfigure
                hwnd = conf_ev.window
                if hwnd in self._windows:
                    old_w = self._windows[hwnd]["w"]
                    old_h = self._windows[hwnd]["h"]
                    new_w = conf_ev.width
                    new_h = conf_ev.height

                    if old_w != new_w or old_h != new_h:
                        self._windows[hwnd]["w"] = new_w
                        self._windows[hwnd]["h"] = new_h
                        self._pending_events = self._pending_events.push(WindowEvent(
                            timestamp=0,
                            window_id=WindowID(hwnd),
                            event_id=WindowEventID.RESIZED,
                            data1=new_w,
                            data2=new_h
                        ))

    def poll_event(self) -> Any | None:
        """Poll the next event from queue or pump from X11."""
        if not self._pending_events:
            self.pump_events()
        event, self._pending_events = self._pending_events.pop()
        return event

    def wait_event(self, timeout_ms: int) -> Any | None:
        """Wait for an event or timeout."""
        if not self._pending_events:
            self.pump_events()

        if self._pending_events:
            event, self._pending_events = self._pending_events.pop()
            return event

        if self._x11 and self._display:
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

    def open_audio(self, spec: AudioSpec | None) -> Result[PlatformAudioHandle, SDLError]:
        """Open a native Linux audio hardware playback output (PulseAudio/ALSA) or fall back to dummy."""
        from Effy.audio.types import AudioSpec, AudioFormat
        if spec is None:
            spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=1024)

        # 1. Try PulseAudio Simple API first
        if _pulse:
            ss = pa_sample_spec()
            ss.format = 3 if spec.format == AudioFormat.S16 else 5
            ss.rate = spec.freq
            ss.channels = spec.channels
            
            error = ctypes.c_int(0)
            pa_handle = _pulse.pa_simple_new(
                None,            # default server
                b"Effy",       # app name
                1,               # PA_STREAM_PLAYBACK
                None,            # default device
                b"Playback",     # stream name
                ctypes.byref(ss),
                None,            # default map
                None,            # default attr
                ctypes.byref(error)
            )
            if pa_handle:
                device = LinuxAudioDevice(backend_type="pulseaudio", handle=pa_handle, spec=spec)
                handle_id = PlatformAudioHandle(self._next_audio_id)
                self._next_audio_id += 1
                self._audio_devices[handle_id] = device
                return Ok(handle_id)

        # 2. Try ALSA as fallback
        if _asound:
            pcm_ptr = ctypes.c_void_p()
            err = _asound.snd_pcm_open(ctypes.byref(pcm_ptr), b"default", 0, 0)
            if err >= 0:
                params = ctypes.c_void_p()
                err = _asound.snd_pcm_hw_params_malloc(ctypes.byref(params))
                if err >= 0:
                    err = _asound.snd_pcm_hw_params_any(pcm_ptr, params)
                if err >= 0:
                    err = _asound.snd_pcm_hw_params_set_access(pcm_ptr, params, 3) # RW_INTERLEAVED
                if err >= 0:
                    fmt_val = 2 if spec.format == AudioFormat.S16 else 14
                    err = _asound.snd_pcm_hw_params_set_format(pcm_ptr, params, fmt_val)
                if err >= 0:
                    err = _asound.snd_pcm_hw_params_set_channels(pcm_ptr, params, spec.channels)
                if err >= 0:
                    rate = ctypes.c_uint(spec.freq)
                    dir_val = ctypes.c_int(0)
                    err = _asound.snd_pcm_hw_params_set_rate_near(pcm_ptr, params, ctypes.byref(rate), ctypes.byref(dir_val))
                if err >= 0:
                    err = _asound.snd_pcm_hw_params(pcm_ptr, params)
                if params:
                    _asound.snd_pcm_hw_params_free(params)
                
                if err >= 0:
                    device = LinuxAudioDevice(backend_type="alsa", handle=pcm_ptr, spec=spec)
                    handle_id = PlatformAudioHandle(self._next_audio_id)
                    self._next_audio_id += 1
                    self._audio_devices[handle_id] = device
                    return Ok(handle_id)
                else:
                    _asound.snd_pcm_close(pcm_ptr)

        # 3. Fallback dummy device (with warning to stderr)
        import sys
        sys.stderr.write("Warning: Failed to initialize native audio hardware (PulseAudio/ALSA). Falling back to dummy device.\n")
        
        device = LinuxAudioDevice(backend_type="dummy", handle=None, spec=spec)
        handle_id = PlatformAudioHandle(self._next_audio_id)
        self._next_audio_id += 1
        self._audio_devices[handle_id] = device
        return Ok(handle_id)

    def write_audio(self, handle: PlatformAudioHandle, data: bytes) -> None:
        """Write raw mixed audio frames to the physical output hardware."""
        device = self._audio_devices.get(handle)
        if not device:
            return

        if device.backend_type == "pulseaudio" and _pulse:
            error = ctypes.c_int(0)
            _pulse.pa_simple_write(device.handle, data, len(data), ctypes.byref(error))
        elif device.backend_type == "alsa" and _asound:
            from Effy.audio.types import AudioFormat
            bytes_per_sample = 2 if device.spec.format == AudioFormat.S16 else 4
            frames = len(data) // (device.spec.channels * bytes_per_sample)
            written = _asound.snd_pcm_writei(device.handle, data, frames)
            if written < 0:
                _asound.snd_pcm_recover(device.handle, int(written), 0)

    def close_audio(self, handle: PlatformAudioHandle) -> None:
        """Close the native Linux audio hardware playback output."""
        device = self._audio_devices.pop(handle, None)
        if not device:
            return

        if device.backend_type == "pulseaudio" and _pulse:
            _pulse.pa_simple_free(device.handle)
        elif device.backend_type == "alsa" and _asound:
            _asound.snd_pcm_close(device.handle)

    def get_keyboard_state(self) -> Any:
        """Retrieve current keyboard snapshot."""
        from Effy.input.keyboard import KeyboardState
        return KeyboardState(pressed_keys=frozenset(self._pressed_keys))

    def get_mouse_state(self) -> Any:
        """Retrieve current mouse snapshot."""
        from Effy.input.mouse import MouseState
        from Effy.events.types import MouseButton
        buttons = self._mouse_buttons if self._mouse_buttons is not None else MouseButton.NONE
        return MouseState(x=self._mouse_x, y=self._mouse_y, buttons=buttons)

    def get_touch_state(self) -> Any:
        """Retrieve current touch snapshot."""
        from Effy.input.touch import TouchState, TouchDeviceState
        devices = []
        for dev_id, fingers in self._touch_devices.items():
            devices.append(TouchDeviceState(device_id=dev_id, fingers=frozenset(fingers)))
        return TouchState(devices=frozenset(devices))

    def get_gamepad_state(self) -> Any:
        """Retrieve current gamepad snapshot state."""
        from Effy.input.gamepad import GamepadState
        return GamepadState(devices=frozenset())

    def get_sensor_state(self) -> Any:
        """Retrieve current sensor snapshot state."""
        from Effy.input.sensors import SensorState
        return SensorState(devices=frozenset())

    def open_haptic(self, device_id: int) -> Result[PlatformHapticHandle, SDLError]:
        """Open a haptic device for play back."""
        from Effy.platform import PlatformHapticHandle
        return Ok(PlatformHapticHandle(device_id))

    def close_haptic(self, device_id: int) -> None:
        """Close an opened haptic device."""
        pass

    def is_rumble_supported(self, device_id: int) -> bool:
        """Determine whether rumble is supported on this haptic device."""
        return False

    def play_rumble(self, device_id: int, strength: float, duration_ms: int) -> Result[None, SDLError]:
        """Play a simple rumble effect on the haptic device."""
        return Err(SDLError(code=-1, message="Rumble not implemented on Linux X11 stub"))

    def stop_rumble(self, device_id: int) -> Result[None, SDLError]:
        """Stop rumble playback on the haptic device."""
        return Err(SDLError(code=-1, message="Rumble not implemented on Linux X11 stub"))

    def upload_effect(self, device_id: int, effect: Any) -> Result[int, SDLError]:
        """Upload a custom haptic effect to the haptic device."""
        return Err(SDLError(code=-1, message="Haptic custom effects not implemented on Linux X11 stub"))

    def run_effect(self, device_id: int, effect_id: int, iterations: int) -> Result[None, SDLError]:
        """Run a previously uploaded custom haptic effect."""
        return Err(SDLError(code=-1, message="Haptic custom effects not implemented on Linux X11 stub"))

    def stop_effect(self, device_id: int, effect_id: int) -> Result[None, SDLError]:
        """Stop playback of a custom haptic effect."""
        return Err(SDLError(code=-1, message="Haptic custom effects not implemented on Linux X11 stub"))

    def destroy_effect(self, device_id: int, effect_id: int) -> None:
        """Destroy an uploaded haptic effect to release memory."""
        pass

    def get_num_video_displays(self) -> int:
        """Get the number of video displays."""
        return 1

    def get_display_name(self, index: int) -> str:
        """Get description of video display."""
        return "Linux Monitor"

    def get_display_bounds(self, index: int) -> Any:
        """Get spatial boundaries of video display."""
        from Effy.video.rect import Rect
        return Rect(0, 0, 1920, 1080)

    def set_window_size(self, handle: Any, w: int, h: int) -> None:
        """Set window dimensions programmatically."""
        if self._x11 and self._display:
            self._x11.XResizeWindow(self._display, handle, w, h)
            if handle in self._windows:
                self._windows[handle]["w"] = w
                self._windows[handle]["h"] = h
            self._x11.XFlush(self._display)

    def set_window_position(self, handle: Any, x: int, y: int) -> None:
        """Set window coordinates programmatically."""
        if self._x11 and self._display:
            self._x11.XMoveWindow(self._display, handle, x, y)
            self._x11.XFlush(self._display)

    def minimize_window(self, handle: Any) -> None:
        """Request window iconification."""
        if self._x11 and self._display:
            self._x11.XIconifyWindow(self._display, handle, self._screen)
            self._x11.XFlush(self._display)

    def maximize_window(self, handle: Any) -> None:
        """Request window maximization (map raised)."""
        if self._x11 and self._display:
            self._x11.XMapRaised(self._display, handle)
            self._x11.XFlush(self._display)

    def restore_window(self, handle: Any) -> None:
        """Request window restoration (map window)."""
        if self._x11 and self._display:
            self._x11.XMapWindow(self._display, handle)
            self._x11.XFlush(self._display)

    def show_window(self, handle: Any) -> None:
        """Request window mapping."""
        if self._x11 and self._display:
            self._x11.XMapWindow(self._display, handle)
            self._x11.XFlush(self._display)

    def hide_window(self, handle: Any) -> None:
        """Request window unmapping."""
        if self._x11 and self._display:
            self._x11.XUnmapWindow(self._display, handle)
            self._x11.XFlush(self._display)

    def get_clipboard_text(self) -> str:
        """Get the text from the X11 system clipboard using xclip/xsel or in-memory fallback."""
        import subprocess
        # Try xclip first
        try:
            res = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True,
                text=True,
                timeout=1.0
            )
            if res.returncode == 0:
                return res.stdout
        except Exception:
            pass

        # Try xsel as fallback
        try:
            res = subprocess.run(
                ["xsel", "--clipboard", "--output"],
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
        """Set the text in the X11 system clipboard using xclip/xsel or in-memory fallback."""
        import subprocess
        self._clipboard_text = text

        # Try xclip
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text,
                text=True,
                capture_output=True,
                timeout=1.0
            )
            return
        except Exception:
            pass

        # Try xsel
        try:
            subprocess.run(
                ["xsel", "--clipboard", "--input"],
                input=text,
                text=True,
                capture_output=True,
                timeout=1.0
            )
            return
        except Exception:
            pass

    def get_clipboard_data(self, mime_type: str) -> Result[bytes, SDLError]:
        """Get binary data for a specific MIME type from the X11 clipboard using xclip or in-memory fallback."""
        import subprocess
        try:
            res = subprocess.run(
                ["xclip", "-selection", "clipboard", "-t", mime_type, "-o"],
                capture_output=True,
                timeout=1.0
            )
            if res.returncode == 0:
                return Ok(res.stdout)
        except Exception:
            pass

        if mime_type in self._clipboard_data:
            return Ok(self._clipboard_data[mime_type])
        return Err(SDLError(code=-1, message=f"MIME type '{mime_type}' not found in clipboard"))

    def set_clipboard_data(self, mime_type: str, data: bytes) -> Result[None, SDLError]:
        """Set binary data for a specific MIME type in the X11 clipboard using xclip or in-memory fallback."""
        import subprocess
        self._clipboard_data[mime_type] = data

        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard", "-t", mime_type],
                input=data,
                capture_output=True,
                timeout=1.0
            )
        except Exception:
            pass

        return Ok(None)
