from __future__ import annotations
from Effy.input.keyboard import KeyboardState
from Effy.input.mouse import MouseState
from Effy.input.touch import TouchState, TouchDeviceState, Finger
from Effy.input import (
    get_keyboard_state, get_mouse_state, get_touch_state,
    get_gamepad_state, get_sensor_state
)
from Effy.events.types import Scancode, MouseButton
from Effy._internal.registry import set_platform_adapter
from Effy.platform.headless import HeadlessAdapter
from Effy.types import Effect

def test_keyboard_state() -> None:
    """Test KeyboardState construction and pressed key queries."""
    state = KeyboardState(pressed_keys=frozenset([Scancode(1), Scancode(2)]))
    assert state.is_pressed(Scancode(1)) is True
    assert state.is_pressed(Scancode(3)) is False

def test_mouse_state() -> None:
    """Test MouseState construction and pressed mouse button queries."""
    state = MouseState(x=10, y=20, buttons=MouseButton.LEFT | MouseButton.RIGHT)
    assert state.is_button_pressed(MouseButton.LEFT) is True
    assert state.is_button_pressed(MouseButton.MIDDLE) is False
    assert state.is_button_pressed(MouseButton.RIGHT) is True

def test_touch_state_functional() -> None:
    """Test TouchState construction and query by finger ID."""
    finger1 = Finger(id=0, x=0.5, y=0.5, pressure=1.0)
    finger2 = Finger(id=1, x=0.2, y=0.8, pressure=0.5)
    dev = TouchDeviceState(device_id=42, fingers=frozenset([finger1, finger2]))
    state = TouchState(devices=frozenset([dev]))
    
    assert state.get_finger(42, 0) == finger1
    assert state.get_finger(42, 1) == finger2
    assert state.get_finger(42, 3) is None
    assert state.get_finger(100, 0) is None

def test_input_state_effects_with_adapter() -> None:
    """Test input state snapshot Effect queries utilizing mock data in the HeadlessAdapter."""
    # Set up adapter
    adapter = HeadlessAdapter()
    set_platform_adapter(adapter)
    
    try:
        # Initial empty states
        kbd_eff = get_keyboard_state()
        mouse_eff = get_mouse_state()
        touch_eff = get_touch_state()
        gamepad_eff = get_gamepad_state()
        sensor_eff = get_sensor_state()
        
        assert isinstance(kbd_eff, Effect)
        assert isinstance(mouse_eff, Effect)
        assert isinstance(touch_eff, Effect)
        assert isinstance(gamepad_eff, Effect)
        assert isinstance(sensor_eff, Effect)
        
        kbd = kbd_eff.run()
        mouse = mouse_eff.run()
        touch = touch_eff.run()
        gamepad = gamepad_eff.run()
        sensor = sensor_eff.run()
        
        assert len(kbd.pressed_keys) == 0
        assert mouse.x == 0
        assert len(touch.devices) == 0
        assert len(gamepad.devices) == 0
        assert len(sensor.devices) == 0
        
        # Simulate active state changes
        adapter._pressed_keys.add(Scancode(5))
        adapter._mouse_x = 100
        adapter._mouse_y = 200
        adapter._mouse_buttons = MouseButton.LEFT | MouseButton.MIDDLE
        
        finger = Finger(id=9, x=0.1, y=0.2, pressure=0.8)
        adapter._touch_devices[99] = {finger}
        
        from Effy.input.gamepad import GamepadDeviceState, GamepadButton, GamepadAxis
        from Effy.input.sensors import SensorDeviceState, SensorType
        
        gamepad_dev = GamepadDeviceState(
            device_id=3,
            name="Mock Controller",
            pressed_buttons=frozenset([GamepadButton.A]),
            axes=frozenset([(GamepadAxis.LEFTX, 0.75)])
        )
        adapter._gamepads[3] = gamepad_dev
        
        sensor_dev = SensorDeviceState(
            device_id=4,
            name="Mock Accelerometer",
            type=SensorType.ACCEL,
            data=(1.0, 2.0, 3.0)
        )
        adapter._sensors[4] = sensor_dev
        
        # Query again
        kbd = get_keyboard_state().run()
        mouse = get_mouse_state().run()
        touch = get_touch_state().run()
        gamepad = get_gamepad_state().run()
        sensor = get_sensor_state().run()
        
        assert kbd.is_pressed(Scancode(5)) is True
        assert mouse.x == 100
        assert mouse.y == 200
        assert mouse.is_button_pressed(MouseButton.LEFT) is True
        assert mouse.is_button_pressed(MouseButton.MIDDLE) is True
        assert mouse.is_button_pressed(MouseButton.RIGHT) is False
        
        f = touch.get_finger(99, 9)
        assert f is not None
        assert f.pressure == 0.8
        
        gp_dev = gamepad.get_device(3)
        assert gp_dev is not None
        assert gp_dev.is_pressed(GamepadButton.A) is True
        assert gp_dev.is_pressed(GamepadButton.B) is False
        assert gp_dev.get_axis(GamepadAxis.LEFTX) == 0.75
        assert gp_dev.get_axis(GamepadAxis.LEFTY) == 0.0
        
        sn_dev = sensor.get_sensor(4)
        assert sn_dev is not None
        assert sn_dev.type == SensorType.ACCEL
        assert sn_dev.data == (1.0, 2.0, 3.0)
        assert sensor.get_sensor(99) is None
        
    finally:
        set_platform_adapter(None)

def test_gamecontrollerdb_parsing_and_mapping() -> None:
    """Test standard gamecontrollerdb parser and hardware translating mappings."""
    from Effy.input.gamepad import parse_gamecontrollerdb, map_hardware_to_gamepad, GamepadButton, GamepadAxis
    
    db_content = (
        "030000005e0400008e02000010010000,X360 Controller,"
        "platform:Linux,a:b0,b:b1,x:b2,y:b3,lefttrigger:a2,righttrigger:a5,"
        "leftx:a0,lefty:a1,dpup:h0.1,dpdown:h0.4\n"
    )
    parsed = parse_gamecontrollerdb(db_content)
    assert "030000005e0400008e02000010010000" in parsed
    name, platform, mapping = parsed["030000005e0400008e02000010010000"]
    assert name == "X360 Controller"
    assert platform == "Linux"
    assert mapping["a"] == "b0"
    
    raw_buttons = frozenset([0, 2])
    raw_axes = {0: 0.5, 1: -0.25, 2: 0.8}
    raw_hats = {0: 1}
    
    btn_pressed, axis_vals = map_hardware_to_gamepad(mapping, raw_buttons, raw_axes, raw_hats)
    
    assert GamepadButton.A in btn_pressed
    assert GamepadButton.B not in btn_pressed
    assert GamepadButton.X in btn_pressed
    assert GamepadButton.DPAD_UP in btn_pressed
    
    axis_dict = dict(axis_vals)
    assert axis_dict[GamepadAxis.LEFTX] == 0.5
    assert axis_dict[GamepadAxis.LEFTY] == -0.25
    assert axis_dict[GamepadAxis.TRIGGERLEFT] == 0.8

def test_haptics_functional_with_adapter() -> None:
    """Test haptic effects composition, playback triggers and mock state via HeadlessAdapter."""
    from Effy.input.haptics import (
        HapticEffect, open_haptic_device, close_haptic_device,
        is_haptic_rumble_supported, play_haptic_rumble, stop_haptic_rumble,
        upload_haptic_effect, run_haptic_effect, stop_haptic_effect, destroy_haptic_effect
    )
    
    adapter = HeadlessAdapter()
    set_platform_adapter(adapter)
    
    try:
        device_id = 42
        
        # Open device
        res = open_haptic_device(device_id).run()
        assert res.is_ok() is True
        dev = res.unwrap()
        assert dev.device_id == device_id
        assert device_id in adapter._haptics_opened
        
        # Test rumble support query
        assert is_haptic_rumble_supported(dev).run() is False
        adapter._haptics_rumble_supported.add(device_id)
        assert is_haptic_rumble_supported(dev).run() is True
        
        # Test play rumble
        play_res = play_haptic_rumble(dev, 0.75, 500).run()
        assert play_res.is_ok() is True
        assert adapter._haptics_playing_rumble[device_id] == (0.75, 500)
        
        # Test stop rumble
        stop_res = stop_haptic_rumble(dev).run()
        assert stop_res.is_ok() is True
        assert device_id not in adapter._haptics_playing_rumble
        
        # Test custom haptic effects upload
        effect = HapticEffect(type="rumble", duration_ms=1000, strength=0.9, large_rumble=0.5)
        upload_res = upload_haptic_effect(dev, effect).run()
        assert upload_res.is_ok() is True
        eff_id = upload_res.unwrap()
        assert eff_id == 1
        assert adapter._haptics_effects[device_id][eff_id] == effect
        
        # Run custom effect
        run_res = run_haptic_effect(dev, eff_id, 3).run()
        assert run_res.is_ok() is True
        assert eff_id in adapter._haptics_running_effects[device_id]
        
        # Stop custom effect
        stop_eff_res = stop_haptic_effect(dev, eff_id).run()
        assert stop_eff_res.is_ok() is True
        assert eff_id not in adapter._haptics_running_effects[device_id]
        
        # Destroy effect
        destroy_haptic_effect(dev, eff_id).run()
        assert eff_id not in adapter._haptics_effects[device_id]
        
        # Close device
        close_haptic_device(dev).run()
        assert device_id not in adapter._haptics_opened
        
    finally:
        set_platform_adapter(None)
