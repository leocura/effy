"""Integration tests for touch gestures, coordinate systems, and platform transitions under the HeadlessAdapter."""

from __future__ import annotations
import math
from typing import Iterable
from hypothesis import given, strategies as st
import pytest

from Effy.init import init, quit
from Effy.init.flags import InitFlag
from Effy.video import create_window, destroy_window, WindowFlags
from Effy.events import poll_event
from Effy.events.types import (
    Event, WindowEvent, WindowEventID,
    FingerDownEvent, FingerUpEvent, FingerMotionEvent
)
from Effy._internal.registry import get_platform_adapter
from Effy.platform.headless import HeadlessAdapter
from Effy.input.touch import Finger
from Effy.input import get_touch_state


def generate_pinch_zoom_gesture(
    device_id: int,
    center_x: float,
    center_y: float,
    start_radius: float,
    end_radius: float,
    steps: int,
    start_timestamp: int = 1000,
    timestamp_step: int = 16
) -> tuple[Event, ...]:
    """Pure helper function to generate a pinch/zoom event sequence.

    Args:
        device_id: Unique identifier for the touch device.
        center_x: X-coordinate of the gesture center.
        center_y: Y-coordinate of the gesture center.
        start_radius: Initial distance from center for both fingers.
        end_radius: Final distance from center for both fingers.
        steps: Number of motion steps to generate.
        start_timestamp: Millisecond timestamp to start the sequence.
        timestamp_step: Milliseconds between consecutive motion steps.

    Returns:
        A tuple of simulated touch events (FingerDown, FingerMotion, FingerUp).
    """
    events: list[Event] = []

    # 1. FingerDown events for both fingers
    events.append(FingerDownEvent(
        timestamp=start_timestamp,
        touch_id=device_id,
        finger_id=0,
        x=center_x - start_radius,
        y=center_y,
        dx=0.0,
        dy=0.0,
        pressure=1.0
    ))
    events.append(FingerDownEvent(
        timestamp=start_timestamp,
        touch_id=device_id,
        finger_id=1,
        x=center_x + start_radius,
        y=center_y,
        dx=0.0,
        dy=0.0,
        pressure=1.0
    ))

    # 2. FingerMotion events tracking the zoom trajectory
    for i in range(1, steps + 1):
        t = i / steps
        current_radius = start_radius + t * (end_radius - start_radius)
        prev_radius = start_radius + ((i - 1) / steps) * (end_radius - start_radius)
        delta_r = current_radius - prev_radius

        events.append(FingerMotionEvent(
            timestamp=start_timestamp + i * timestamp_step,
            touch_id=device_id,
            finger_id=0,
            x=center_x - current_radius,
            y=center_y,
            dx=-delta_r,
            dy=0.0,
            pressure=1.0
        ))
        events.append(FingerMotionEvent(
            timestamp=start_timestamp + i * timestamp_step,
            touch_id=device_id,
            finger_id=1,
            x=center_x + current_radius,
            y=center_y,
            dx=delta_r,
            dy=0.0,
            pressure=1.0
        ))

    # 3. FingerUp events terminating the gesture
    final_timestamp = start_timestamp + (steps + 1) * timestamp_step
    events.append(FingerUpEvent(
        timestamp=final_timestamp,
        touch_id=device_id,
        finger_id=0,
        x=center_x - end_radius,
        y=center_y,
        dx=0.0,
        dy=0.0,
        pressure=0.0
    ))
    events.append(FingerUpEvent(
        timestamp=final_timestamp,
        touch_id=device_id,
        finger_id=1,
        x=center_x + end_radius,
        y=center_y,
        dx=0.0,
        dy=0.0,
        pressure=0.0
    ))

    return tuple(events)


def analyze_pinch_zoom_ratio(events: Iterable[Event], device_id: int) -> float:
    """Pure analysis function to compute the total zoom scaling factor from a gesture.

    Args:
        events: Sequence of events to inspect.
        device_id: Unique identifier for the target touch device.

    Returns:
        The ratio of the final gesture finger distance to the initial distance.
    """
    initial_positions: dict[int, tuple[float, float]] = {}
    final_positions: dict[int, tuple[float, float]] = {}

    for event in events:
        if isinstance(event, FingerDownEvent) and event.touch_id == device_id:
            initial_positions[event.finger_id] = (event.x, event.y)
            final_positions[event.finger_id] = (event.x, event.y)
        elif isinstance(event, FingerMotionEvent) and event.touch_id == device_id:
            final_positions[event.finger_id] = (event.x, event.y)
        elif isinstance(event, FingerUpEvent) and event.touch_id == device_id:
            final_positions[event.finger_id] = (event.x, event.y)

    if 0 not in initial_positions or 1 not in initial_positions:
        return 1.0
    if 0 not in final_positions or 1 not in final_positions:
        return 1.0

    dx_init = initial_positions[0][0] - initial_positions[1][0]
    dy_init = initial_positions[0][1] - initial_positions[1][1]
    init_dist = math.sqrt(dx_init * dx_init + dy_init * dy_init)

    dx_final = final_positions[0][0] - final_positions[1][0]
    dy_final = final_positions[0][1] - final_positions[1][1]
    final_dist = math.sqrt(dx_final * dx_final + dy_final * dy_final)

    if init_dist == 0.0:
        return 1.0
    return final_dist / init_dist


def test_pinch_zoom_happy_path() -> None:
    """Test standard pinch-zoom gesture event generation and analysis happy path."""
    device_id = 7
    start_r = 0.1
    end_r = 0.3
    steps = 5

    events = generate_pinch_zoom_gesture(
        device_id=device_id,
        center_x=0.5,
        center_y=0.5,
        start_radius=start_r,
        end_radius=end_r,
        steps=steps
    )

    # 1. Total events = 2 (Down) + 2 * 5 (Motion) + 2 (Up) = 14
    assert len(events) == 14

    # 2. Analyze the zoom ratio
    zoom_ratio = analyze_pinch_zoom_ratio(events, device_id)
    # Expected ratio = end_r / start_r = 0.3 / 0.1 = 3.0
    assert pytest.approx(zoom_ratio) == 3.0


def test_pinch_zoom_edge_cases() -> None:
    """Test pinch-zoom analysis edge cases (empty inputs, missing fingers, division by zero)."""
    device_id = 9

    # Edge Case 1: Empty input
    assert analyze_pinch_zoom_ratio((), device_id) == 1.0

    # Edge Case 2: Only one finger down
    single_finger = (
        FingerDownEvent(
            timestamp=100, touch_id=device_id, finger_id=0,
            x=0.5, y=0.5, dx=0.0, dy=0.0, pressure=1.0
        ),
    )
    assert analyze_pinch_zoom_ratio(single_finger, device_id) == 1.0

    # Edge Case 3: Initial distance is zero (both fingers at the exact same point)
    zero_dist_events = (
        FingerDownEvent(
            timestamp=100, touch_id=device_id, finger_id=0,
            x=0.5, y=0.5, dx=0.0, dy=0.0, pressure=1.0
        ),
        FingerDownEvent(
            timestamp=100, touch_id=device_id, finger_id=1,
            x=0.5, y=0.5, dx=0.0, dy=0.0, pressure=1.0
        ),
        FingerUpEvent(
            timestamp=200, touch_id=device_id, finger_id=0,
            x=0.4, y=0.5, dx=0.0, dy=0.0, pressure=0.0
        ),
        FingerUpEvent(
            timestamp=200, touch_id=device_id, finger_id=1,
            x=0.6, y=0.5, dx=0.0, dy=0.0, pressure=0.0
        ),
    )
    assert analyze_pinch_zoom_ratio(zero_dist_events, device_id) == 1.0


@given(
    center_x=st.floats(min_value=0.4, max_value=0.6),
    center_y=st.floats(min_value=0.4, max_value=0.6),
    start_radius=st.floats(min_value=0.01, max_value=0.1),
    end_radius=st.floats(min_value=0.11, max_value=0.39),
    steps=st.integers(min_value=1, max_value=20)
)
def test_pinch_zoom_hypothesis_property(
    center_x: float,
    center_y: float,
    start_radius: float,
    end_radius: float,
    steps: int
) -> None:
    """Hypothesis test to prove zoom ratio calculation correctness across dynamic boundaries."""
    device_id = 42
    events = generate_pinch_zoom_gesture(
        device_id=device_id,
        center_x=center_x,
        center_y=center_y,
        start_radius=start_radius,
        end_radius=end_radius,
        steps=steps
    )

    zoom_ratio = analyze_pinch_zoom_ratio(events, device_id)
    expected_ratio = end_radius / start_radius
    assert pytest.approx(zoom_ratio) == expected_ratio


def test_touch_state_query_and_updates() -> None:
    """Integration test simulating multi-touch coordinates on HeadlessAdapter."""
    res = init(InitFlag.VIDEO).run()
    assert res.is_ok()
    ctx = res.unwrap()

    adapter = get_platform_adapter()
    assert isinstance(adapter, HeadlessAdapter)

    try:
        device_id = 3
        # Initially empty touch state
        touch_state = get_touch_state().run()
        assert len(touch_state.devices) == 0

        # Simulate 2 active fingers touching the screen
        finger1 = Finger(id=0, x=0.25, y=0.5, pressure=1.0)
        finger2 = Finger(id=1, x=0.75, y=0.5, pressure=0.8)

        adapter._touch_devices[device_id] = {finger1, finger2}

        # Query touch state and verify properties
        updated_state = get_touch_state().run()
        assert len(updated_state.devices) == 1

        f1_query = updated_state.get_finger(device_id, 0)
        assert f1_query is not None
        assert f1_query.x == 0.25
        assert f1_query.y == 0.5
        assert f1_query.pressure == 1.0

        f2_query = updated_state.get_finger(device_id, 1)
        assert f2_query is not None
        assert f2_query.x == 0.75
        assert f2_query.y == 0.5
        assert f2_query.pressure == 0.8

        # Out-of-bounds or non-existent checks
        assert updated_state.get_finger(device_id, 99) is None
        assert updated_state.get_finger(99, 0) is None

    finally:
        quit(ctx).run()


def test_platform_window_state_transitions() -> None:
    """Integration test verifying platform WindowEvent processing via mock transitions."""
    res = init(InitFlag.VIDEO).run()
    assert res.is_ok()
    ctx = res.unwrap()

    adapter = get_platform_adapter()
    assert isinstance(adapter, HeadlessAdapter)

    try:
        win_res = create_window("Transition Test", 0, 0, 800, 600, WindowFlags.SHOWN).run()
        assert win_res.is_ok()
        win = win_res.unwrap()

        # 1. Simulate RESIZED transition from platform
        adapter._pending_events = adapter._pending_events + (
            WindowEvent(
                timestamp=1000,
                window_id=win.id,
                event_id=WindowEventID.RESIZED,
                data1=1024,
                data2=768
            ),
        )

        ev = poll_event().run()
        assert isinstance(ev, WindowEvent)
        assert ev.event_id == WindowEventID.RESIZED
        assert ev.data1 == 1024
        assert ev.data2 == 768

        # 2. Simulate FOCUS_LOST transition from platform
        adapter._pending_events = adapter._pending_events + (
            WindowEvent(
                timestamp=1010,
                window_id=win.id,
                event_id=WindowEventID.FOCUS_LOST,
                data1=0,
                data2=0
            ),
        )
        ev2 = poll_event().run()
        assert isinstance(ev2, WindowEvent)
        assert ev2.event_id == WindowEventID.FOCUS_LOST

        # 3. Simulate FOCUS_GAINED transition from platform
        adapter._pending_events = adapter._pending_events + (
            WindowEvent(
                timestamp=1020,
                window_id=win.id,
                event_id=WindowEventID.FOCUS_GAINED,
                data1=0,
                data2=0
            ),
        )
        ev3 = poll_event().run()
        assert isinstance(ev3, WindowEvent)
        assert ev3.event_id == WindowEventID.FOCUS_GAINED

        # 4. Simulate MINIMIZED transition from platform
        adapter._pending_events = adapter._pending_events + (
            WindowEvent(
                timestamp=1030,
                window_id=win.id,
                event_id=WindowEventID.MINIMIZED,
                data1=0,
                data2=0
            ),
        )
        ev4 = poll_event().run()
        assert isinstance(ev4, WindowEvent)
        assert ev4.event_id == WindowEventID.MINIMIZED

        destroy_window(win).run()

    finally:
        quit(ctx).run()
