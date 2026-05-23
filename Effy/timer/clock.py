from __future__ import annotations
from dataclasses import dataclass
from Effy._internal.fp import pure

@dataclass(frozen=True, slots=True)
class ClockState:
    """An immutable container representing the state of an frame rate clock.

    Attributes:
        last_ticks: The millisecond timestamp from the last recorded tick.
        delta_time: The time elapsed between the last two ticks in seconds.
    """
    last_ticks: int
    delta_time: float = 0.0

@pure
def tick(clock: ClockState, now: int) -> tuple[ClockState, float]:
    """Compute the time elapsed since the last tick and return the updated clock state.

    Args:
        clock: The current ClockState context.
        now: The current millisecond timestamp.

    Returns:
        A tuple of (new_clock_state, delta_time_in_seconds).
    """
    delta = (now - clock.last_ticks) / 1000.0
    return ClockState(last_ticks=now, delta_time=delta), delta
