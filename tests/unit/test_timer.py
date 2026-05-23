from __future__ import annotations
import time
from typing import Any
from Effy.timer.clock import ClockState, tick
from Effy.timer import (
    get_ticks, delay, get_performance_counter, get_performance_frequency,
    add_timer, remove_timer
)
from Effy.types import Effect

def test_clock_state_tick() -> None:
    clock = ClockState(last_ticks=1000)
    new_clock, delta = tick(clock, now=2000)
    assert new_clock.last_ticks == 2000
    assert new_clock.delta_time == 1.0
    assert delta == 1.0

def test_get_ticks_returns_effect() -> None:
    eff = get_ticks()
    assert isinstance(eff, Effect)

def test_delay_returns_effect() -> None:
    eff = delay(100)
    assert isinstance(eff, Effect)

def test_performance_counters() -> None:
    # 1. Frequency
    freq_effect = get_performance_frequency()
    assert isinstance(freq_effect, Effect)
    freq = freq_effect.run()
    assert freq > 0

    # 2. Counter
    counter_effect = get_performance_counter()
    assert isinstance(counter_effect, Effect)
    c1 = counter_effect.run()
    time.sleep(0.001)
    c2 = counter_effect.run()
    assert c2 > c1

def test_native_timer_loading() -> None:
    import sys
    from Effy.timer import _load_native_timer
    counter_fn, freq_fn = _load_native_timer()
    assert callable(counter_fn)
    assert callable(freq_fn)

    # Verify that the correct native counter function was loaded on Linux/Windows/macOS
    if sys.platform.startswith("linux"):
        assert counter_fn.__name__ == "unix_counter"
        assert freq_fn.__name__ == "unix_frequency"
    elif sys.platform == "win32":
        assert counter_fn.__name__ == "win_counter"
        assert freq_fn.__name__ == "win_frequency"
    elif sys.platform == "darwin":
        assert counter_fn.__name__ == "unix_counter"
        assert freq_fn.__name__ == "unix_frequency"

def test_asynchronous_timers() -> None:
    calls: list[tuple[int, Any]] = []

    def cb(interval: int, param: Any) -> int:
        calls.append((interval, param))
        if len(calls) >= 3:
            return 0  # Stop the timer
        return interval

    # 1. Add Timer
    timer_effect = add_timer(10, cb, "test_param")
    assert isinstance(timer_effect, Effect)
    timer_id = timer_effect.run()
    assert timer_id is not None
    
    # Wait for the timer to run at least a few times
    time.sleep(0.06)
    assert len(calls) > 0
    assert calls[0][1] == "test_param"

    # 2. Remove Timer
    calls_rem: list[int] = []

    def cb_rem(interval: int, param: Any) -> int:
        calls_rem.append(interval)
        return interval

    timer_id_2 = add_timer(10, cb_rem, None).run()
    time.sleep(0.015)
    
    remove_effect = remove_timer(timer_id_2)
    assert isinstance(remove_effect, Effect)
    removed = remove_effect.run()
    assert removed is True

    count_after_remove = len(calls_rem)
    time.sleep(0.04)
    # No further calls should have been made
    assert len(calls_rem) == count_after_remove
