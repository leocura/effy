from __future__ import annotations
from hypothesis import given, strategies as st
from Effy.events.types import QuitEvent, Event, WindowEvent, WindowEventID, MouseWheelEvent
from Effy.events.filter import filter_events, map_events, fold_events
from Effy.events.queue import EventQueue
from Effy.types import WindowID

def test_filter_events_happy_path() -> None:
    ev1 = QuitEvent(timestamp=1)
    ev2 = QuitEvent(timestamp=2)
    events: tuple[Event, ...] = (ev1, ev2)
    result = filter_events(lambda e: e.timestamp > 1, events)
    assert result == (ev2,)

def test_filter_events_empty() -> None:
    result = filter_events(lambda e: True, ())
    assert result == ()

def test_map_events_happy_path() -> None:
    ev1 = QuitEvent(timestamp=1)
    ev2 = QuitEvent(timestamp=2)
    events: tuple[Event, ...] = (ev1, ev2)
    result = map_events(lambda e: e.timestamp, events)
    assert result == (1, 2)

def test_map_events_empty() -> None:
    result = map_events(lambda e: e.timestamp, ())
    assert result == ()

def test_fold_events_happy_path() -> None:
    ev1 = QuitEvent(timestamp=1)
    ev2 = QuitEvent(timestamp=2)
    events: tuple[Event, ...] = (ev1, ev2)
    result = fold_events(lambda acc, e: acc + e.timestamp, 0, events)
    assert result == 3

def test_fold_events_empty() -> None:
    result = fold_events(lambda acc, e: acc + 1, 0, ())
    assert result == 0

@given(st.lists(st.builds(QuitEvent, st.integers())).map(tuple))
def test_fold_events_property(events: tuple[QuitEvent, ...]) -> None:
    expected = sum(e.timestamp for e in events)
    result = fold_events(lambda acc, e: acc + e.timestamp, 0, events)
    assert result == expected

def test_event_queue_operations() -> None:
    q = EventQueue.empty()
    assert q.is_empty() is True
    assert len(q) == 0
    
    q2 = q.push(QuitEvent(timestamp=1))
    assert q.is_empty() is True  # Persistent check
    assert q2.is_empty() is False
    assert len(q2) == 1
    assert q2.peek() == QuitEvent(timestamp=1)
    
    q3 = q2.push_many((QuitEvent(timestamp=2), QuitEvent(timestamp=3)))
    assert len(q3) == 3
    
    ev, q4 = q3.pop()
    assert ev == QuitEvent(timestamp=1)
    assert len(q4) == 2
    
    ev2, q5 = q4.pop()
    assert ev2 == QuitEvent(timestamp=2)
    
    ev3, q6 = q5.pop()
    assert ev3 == QuitEvent(timestamp=3)
    assert q6.is_empty() is True

def test_event_queue_tuple_compatibility() -> None:
    q = EventQueue.empty()
    q2 = q + (QuitEvent(timestamp=100),)
    assert len(q2) == 1
    assert q2[0] == QuitEvent(timestamp=100)
    
    q3 = q2 + QuitEvent(timestamp=200)
    assert len(q3) == 2
    assert q3[1] == QuitEvent(timestamp=200)
    
    slice_q = q3[1:]
    assert isinstance(slice_q, EventQueue)
    assert len(slice_q) == 1
    assert slice_q[0] == QuitEvent(timestamp=200)

def test_window_and_mouse_wheel_events() -> None:
    win_ev = WindowEvent(timestamp=10, window_id=WindowID(1), event_id=WindowEventID.RESIZED, data1=100, data2=200)
    wheel_ev = MouseWheelEvent(timestamp=20, window_id=WindowID(1), which=0, x=1, y=2, direction=0, precise_x=1.0, precise_y=2.0)
    
    # Assert fields
    assert win_ev.event_id == WindowEventID.RESIZED
    assert wheel_ev.y == 2
    
    # Test functional processing
    evs: tuple[Event, ...] = (win_ev, wheel_ev)
    filtered = filter_events(lambda e: isinstance(e, WindowEvent), evs)
    assert len(filtered) == 1
    assert filtered[0] == win_ev

def test_new_events() -> None:
    from Effy.events.types import (
        FingerDownEvent, FingerUpEvent, FingerMotionEvent,
        ControllerAxisEvent, ControllerButtonEvent, ControllerDeviceEvent,
        SensorUpdateEvent
    )
    from Effy.input.gamepad import GamepadButton, GamepadAxis
    from Effy.input.sensors import SensorType
    
    # Touch events
    fd = FingerDownEvent(timestamp=100, touch_id=1, finger_id=2, x=0.5, y=0.5, dx=0.0, dy=0.0, pressure=1.0)
    fu = FingerUpEvent(timestamp=101, touch_id=1, finger_id=2, x=0.5, y=0.5, dx=0.0, dy=0.0, pressure=0.0)
    fm = FingerMotionEvent(timestamp=102, touch_id=1, finger_id=2, x=0.6, y=0.6, dx=0.1, dy=0.1, pressure=1.0)
    
    # Gamepad events
    caxis = ControllerAxisEvent(timestamp=103, which=0, axis=GamepadAxis.LEFTX, value=0.5)
    cbtn = ControllerButtonEvent(timestamp=104, which=0, button=GamepadButton.A, state=1)
    cdev = ControllerDeviceEvent(timestamp=105, which=0, is_added=True)
    
    # Sensor events
    sens = SensorUpdateEvent(timestamp=106, which=0, type=SensorType.ACCEL, data=(1.0, 2.0, 3.0))
    
    assert fd.finger_id == 2
    assert fu.touch_id == 1
    assert fm.dx == 0.1
    assert caxis.axis == GamepadAxis.LEFTX
    assert cbtn.button == GamepadButton.A
    assert cdev.is_added is True
    assert sens.type == SensorType.ACCEL
    assert sens.data == (1.0, 2.0, 3.0)
