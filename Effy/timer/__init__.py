from __future__ import annotations
import time
import threading
from typing import Callable, Any, cast
from Effy.types import Effect, TimerID
from Effy._internal.registry import register_timer, unregister_timer, get_timer_cancel_event

def get_ticks() -> Effect[int]:
    """Return an Effect that produces the number of milliseconds since some arbitrary point."""
    def _run() -> int:
        """Thunk returning current time since arbitrary point in milliseconds."""
        return time.monotonic_ns() // 1_000_000
    return Effect(_run)

def delay(ms: int) -> Effect[None]:
    """Return an Effect that sleeps for the specified number of milliseconds."""
    def _run() -> None:
        """Thunk sleeping for the specified milliseconds."""
        time.sleep(ms / 1000.0)
    return Effect(_run)

def _load_native_timer() -> tuple[Callable[[], int], Callable[[], int]]:
    """Determine the host platform and load the appropriate native high-resolution timer.

    Returns:
        A tuple of (counter_fn, frequency_fn) callable objects.
    """
    import sys
    import ctypes

    # 1. Windows Implementation using QueryPerformanceCounter/QueryPerformanceFrequency
    if sys.platform == "win32":
        try:
            kernel32 = ctypes.windll.kernel32
            
            kernel32.QueryPerformanceCounter.argtypes = [ctypes.POINTER(ctypes.c_int64)]
            kernel32.QueryPerformanceCounter.restype = ctypes.c_int

            kernel32.QueryPerformanceFrequency.argtypes = [ctypes.POINTER(ctypes.c_int64)]
            kernel32.QueryPerformanceFrequency.restype = ctypes.c_int

            def win_counter() -> int:
                """Query native high-resolution performance counter on Windows."""
                count = ctypes.c_int64(0)
                if kernel32.QueryPerformanceCounter(ctypes.byref(count)):
                    return count.value
                return 0

            def win_frequency() -> int:
                """Query native high-resolution performance frequency on Windows."""
                freq = ctypes.c_int64(0)
                if kernel32.QueryPerformanceFrequency(ctypes.byref(freq)):
                    return freq.value
                return 1_000_000_000

            # Verify the timer call works on the platform
            if win_counter() > 0:
                return win_counter, win_frequency
        except Exception:
            pass

    # 2. Linux / macOS / Unix Implementation using clock_gettime
    elif sys.platform.startswith("linux") or sys.platform == "darwin" or sys.platform.startswith("freebsd"):
        try:
            libc = ctypes.CDLL(None)
            if hasattr(libc, "clock_gettime"):
                class timespec(ctypes.Structure):
                    """ctypes representation of C timespec struct."""
                    _fields_ = [
                        ("tv_sec", ctypes.c_long),
                        ("tv_nsec", ctypes.c_long),
                    ]

                libc.clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]
                libc.clock_gettime.restype = ctypes.c_int

                # Determine the appropriate CLOCK_MONOTONIC constant
                if sys.platform == "darwin":
                    clock_id = 6
                elif sys.platform.startswith("freebsd"):
                    clock_id = 4
                else:
                    clock_id = 1  # CLOCK_MONOTONIC on Linux

                def unix_counter() -> int:
                    """Query native clock_gettime(CLOCK_MONOTONIC) on Unix-like systems."""
                    ts = timespec()
                    if libc.clock_gettime(clock_id, ctypes.byref(ts)) == 0:
                        return cast(int, ts.tv_sec * 1_000_000_000 + ts.tv_nsec)
                    return 0

                def unix_frequency() -> int:
                    """Get the frequency of the Unix native timer (nanoseconds)."""
                    return 1_000_000_000

                # Verify the timer call works on the platform
                if unix_counter() > 0:
                    return unix_counter, unix_frequency
        except Exception:
            pass

    # 3. Standard CPython / PyPy Fallback
    def fallback_counter() -> int:
        """Fallback high-resolution timer using Python's perf_counter_ns."""
        return time.perf_counter_ns()

    def fallback_frequency() -> int:
        """Fallback frequency (ticks per second)."""
        return 1_000_000_000

    return fallback_counter, fallback_frequency

_counter_fn, _frequency_fn = _load_native_timer()

def get_performance_counter() -> Effect[int]:
    """Return an Effect that produces the high-resolution performance counter."""
    return Effect(_counter_fn)

def get_performance_frequency() -> Effect[int]:
    """Return an Effect that produces the high-resolution performance counter frequency (ticks per second)."""
    return Effect(_frequency_fn)

def add_timer(interval: int, callback: Callable[[int, Any], int], param: Any) -> Effect[TimerID]:
    """Add a callback timer that runs on a separate thread at the specified interval.
    
    The callback signature should be callback(interval: int, param: Any) -> int.
    If it returns 0, the timer will be cancelled. If it returns a non-zero value,
    the timer will reschedule itself with the returned interval.
    """
    def _run() -> TimerID:
        """Thunk spawning a background thread to manage and schedule the timer callback."""
        cancel_event = threading.Event()
        timer_id = register_timer(cancel_event)

        def _timer_loop() -> None:
            """Internal thread loop performing the periodic timer sleeping and callbacks."""
            current_interval = interval
            while not cancel_event.is_set():
                sleep_left = current_interval / 1000.0
                while sleep_left > 0:
                    if cancel_event.is_set():
                        return
                    chunk = min(sleep_left, 0.01)
                    time.sleep(chunk)
                    sleep_left -= chunk
                
                if cancel_event.is_set():
                    return
                
                try:
                    new_interval = callback(current_interval, param)
                except Exception:
                    unregister_timer(timer_id)
                    return
                
                if new_interval == 0:
                    unregister_timer(timer_id)
                    return
                current_interval = new_interval

        t = threading.Thread(target=_timer_loop, daemon=True)
        t.start()
        return TimerID(timer_id)
    return Effect(_run)

def remove_timer(timer_id: TimerID) -> Effect[bool]:
    """Remove a previously added timer by its TimerID. Returns True if successfully removed."""
    def _run() -> bool:
        """Thunk cancelling and unregistering the timer by its ID."""
        cancel_event = get_timer_cancel_event(int(timer_id))
        if cancel_event is not None:
            cancel_event.set()
            unregister_timer(int(timer_id))
            return True
        return False
    return Effect(_run)

__all__ = [
    "get_ticks", "delay", "get_performance_counter",
    "get_performance_frequency", "add_timer", "remove_timer"
]
