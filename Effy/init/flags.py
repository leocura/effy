from enum import IntFlag

class InitFlag(IntFlag):
    """Bitmask flags for selecting which Effy subsystems to initialize."""

    TIMER    = 0x00000001
    AUDIO    = 0x00000010
    VIDEO    = 0x00000020
    JOYSTICK = 0x00000200
    HAPTIC   = 0x00001000
    GAMEPAD  = 0x00002000
    EVENTS   = 0x00004000
    SENSOR   = 0x00008000
    EVERYTHING = TIMER | AUDIO | VIDEO | JOYSTICK | HAPTIC | GAMEPAD | EVENTS | SENSOR
