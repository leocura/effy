from Effy.compat import (
    SDL_Init, SDL_Quit, SDL_CreateWindow, SDL_DestroyWindow, SDL_PollEvent, SDL_Rect, SDL_Point, SDL_Color, SDL_INIT_VIDEO, SDL_WINDOW_SHOWN,
    SDL_FingerDownEvent, SDL_GetTouchState, SDL_GetGamepadState, SDL_GetSensorState,
    SDL_GamepadButton, SDL_GameControllerButton, SDL_HapticOpen, SDL_HapticRumblePlay
)

def test_compat_imports():
    assert SDL_Init is not None
    assert SDL_Quit is not None
    assert SDL_CreateWindow is not None
    assert SDL_DestroyWindow is not None
    assert SDL_PollEvent is not None
    assert SDL_Rect is not None
    assert SDL_Point is not None
    assert SDL_Color is not None
    assert SDL_INIT_VIDEO is not None
    assert SDL_WINDOW_SHOWN is not None
    assert SDL_FingerDownEvent is not None
    assert SDL_GetTouchState is not None
    assert SDL_GetGamepadState is not None
    assert SDL_GetSensorState is not None
    assert SDL_GamepadButton is not None
    assert SDL_GameControllerButton is not None
    assert SDL_HapticOpen is not None
    assert SDL_HapticRumblePlay is not None
