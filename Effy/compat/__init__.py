"""Optional SDL2-style compatible functional names.

This module provides compatibility mappings and names aligned with the Simple DirectMedia Layer (SDL2) API.
SDL2 is copyright (C) 1997-2026 Sam Lantinga and other contributors, and is distributed under the zlib License.
"""
from __future__ import annotations

# Flags and Enums
from Effy.init.flags import InitFlag
from Effy.video import WindowFlags
from Effy.render import RendererFlags

# Core types
from Effy.types import Color as SDL_Color
from Effy.video import Rect as SDL_Rect, Point as SDL_Point
from Effy.error import SDLError, EffyError as SDL_Error
from Effy.events import (
    Event as SDL_Event,
    FingerDownEvent as SDL_FingerDownEvent,
    FingerUpEvent as SDL_FingerUpEvent,
    FingerMotionEvent as SDL_FingerMotionEvent,
    ControllerAxisEvent as SDL_ControllerAxisEvent,
    ControllerButtonEvent as SDL_ControllerButtonEvent,
    ControllerDeviceEvent as SDL_ControllerDeviceEvent,
    SensorUpdateEvent as SDL_SensorUpdateEvent
)

# Functions
from Effy.init import init as SDL_Init, quit as SDL_Quit
from Effy.video import (
    create_window as SDL_CreateWindow, destroy_window as SDL_DestroyWindow,
    set_window_title as SDL_SetWindowTitle, set_window_size as SDL_SetWindowSize,
    set_window_position as SDL_SetWindowPosition, minimize_window as SDL_MinimizeWindow,
    maximize_window as SDL_MaximizeWindow, restore_window as SDL_RestoreWindow,
    show_window as SDL_ShowWindow, hide_window as SDL_HideWindow,
    get_num_video_displays as SDL_GetNumVideoDisplays, get_display_name as SDL_GetDisplayName,
    get_display_bounds as SDL_GetDisplayBounds
)
from Effy.events import poll_event as SDL_PollEvent, wait_event as SDL_WaitEvent, pump_events as SDL_PumpEvents
from Effy.render import (
    create_renderer as SDL_CreateRenderer, render_clear as SDL_RenderClear,
    render_present as SDL_RenderPresent, render_set_draw_color as SDL_SetRenderDrawColor,
    render_fill_rect as SDL_RenderFillRect, render_draw_rect as SDL_RenderDrawRect,
    render_copy as SDL_RenderCopy, render_draw_line as SDL_RenderDrawLine,
    render_draw_circle as SDL_RenderDrawCircle, render_fill_circle as SDL_RenderFillCircle,
    render_fill_triangle as SDL_RenderFillTriangle, render_copy_blended as SDL_RenderCopyBlended,
    render_copy_scaled as SDL_RenderCopyScaled, render_copy_bilinear as SDL_RenderCopyBilinear
)
from Effy.render.texture import create_texture_from_surface as SDL_CreateTextureFromSurface
from Effy.filesystem import get_base_path as SDL_GetBasePath, get_pref_path as SDL_GetPrefPath, RWops as SDL_RWops, rw_from_file as SDL_RWFromFile, rw_to_file as SDL_RWToFile
from Effy.clipboard import (
    get_clipboard_text as SDL_GetClipboardText,
    set_clipboard_text as SDL_SetClipboardText,
    get_clipboard_data as SDL_GetClipboardData,
    set_clipboard_data as SDL_SetClipboardData,
)
from Effy.timer import (
    get_ticks as SDL_GetTicks, delay as SDL_Delay,
    get_performance_counter as SDL_GetPerformanceCounter,
    get_performance_frequency as SDL_GetPerformanceFrequency,
    add_timer as SDL_AddTimer, remove_timer as SDL_RemoveTimer
)
from Effy.input import (
    get_touch_state as SDL_GetTouchState,
    get_gamepad_state as SDL_GetGamepadState,
    get_sensor_state as SDL_GetSensorState,
    GamepadButton as SDL_GamepadButton,
    GamepadAxis as SDL_GamepadAxis,
    GamepadDeviceState as SDL_GamepadDeviceState,
    GamepadState as SDL_GamepadState,
    SensorType as SDL_SensorType,
    SensorDeviceState as SDL_SensorDeviceState,
    SensorState as SDL_SensorState,
    HapticEffect as SDL_HapticEffect,
    HapticDevice as SDL_HapticDevice,
    open_haptic_device as SDL_HapticOpen,
    close_haptic_device as SDL_HapticClose,
    is_haptic_rumble_supported as SDL_HapticRumbleSupported,
    play_haptic_rumble as SDL_HapticRumblePlay,
    stop_haptic_rumble as SDL_HapticRumbleStop,
    upload_haptic_effect as SDL_HapticNewEffect,
    run_haptic_effect as SDL_HapticRunEffect,
    stop_haptic_effect as SDL_HapticStopEffect,
    destroy_haptic_effect as SDL_HapticDestroyEffect
)

SDL_GameControllerButton = SDL_GamepadButton
SDL_GameControllerAxis = SDL_GamepadAxis
SDL_GameControllerDeviceState = SDL_GamepadDeviceState
SDL_GameControllerState = SDL_GamepadState
SDL_GameControllerGetState = SDL_GetGamepadState


SDL_INIT_TIMER = InitFlag.TIMER
SDL_INIT_AUDIO = InitFlag.AUDIO
SDL_INIT_VIDEO = InitFlag.VIDEO
SDL_INIT_JOYSTICK = InitFlag.JOYSTICK
SDL_INIT_HAPTIC = InitFlag.HAPTIC
SDL_INIT_GAMEPAD = InitFlag.GAMEPAD
SDL_INIT_EVENTS = InitFlag.EVENTS
SDL_INIT_SENSOR = InitFlag.SENSOR
SDL_INIT_EVERYTHING = InitFlag.EVERYTHING

SDL_WINDOW_FULLSCREEN = WindowFlags.FULLSCREEN
SDL_WINDOW_OPENGL = WindowFlags.OPENGL
SDL_WINDOW_SHOWN = WindowFlags.SHOWN
SDL_WINDOW_HIDDEN = WindowFlags.HIDDEN
SDL_WINDOW_BORDERLESS = WindowFlags.BORDERLESS
SDL_WINDOW_RESIZABLE = WindowFlags.RESIZABLE
SDL_WINDOW_MINIMIZED = WindowFlags.MINIMIZED
SDL_WINDOW_MAXIMIZED = WindowFlags.MAXIMIZED
SDL_WINDOW_MOUSE_GRABBED = WindowFlags.MOUSE_GRABBED
SDL_WINDOW_INPUT_FOCUS = WindowFlags.INPUT_FOCUS
SDL_WINDOW_MOUSE_FOCUS = WindowFlags.MOUSE_FOCUS
SDL_WINDOW_FOREIGN = WindowFlags.FOREIGN
SDL_WINDOW_ALLOW_HIGHDPI = WindowFlags.ALLOW_HIGHDPI
SDL_WINDOW_MOUSE_CAPTURE = WindowFlags.MOUSE_CAPTURE
SDL_WINDOW_ALWAYS_ON_TOP = WindowFlags.ALWAYS_ON_TOP
SDL_WINDOW_SKIP_TASKBAR = WindowFlags.SKIP_TASKBAR
SDL_WINDOW_UTILITY = WindowFlags.UTILITY
SDL_WINDOW_TOOLTIP = WindowFlags.TOOLTIP
SDL_WINDOW_POPUP_MENU = WindowFlags.POPUP_MENU
SDL_WINDOW_KEYBOARD_GRABBED = WindowFlags.KEYBOARD_GRABBED
SDL_WINDOW_VULKAN = WindowFlags.VULKAN
SDL_WINDOW_METAL = WindowFlags.METAL

SDL_RENDERER_SOFTWARE = RendererFlags.SOFTWARE
SDL_RENDERER_ACCELERATED = RendererFlags.ACCELERATED
SDL_RENDERER_PRESENTVSYNC = RendererFlags.PRESENTVSYNC
SDL_RENDERER_TARGETTEXTURE = RendererFlags.TARGETTEXTURE

__all__ = [
    "SDL_Color", "SDL_Rect", "SDL_Point", "SDL_Event", "SDLError", "SDL_Error",
    "SDL_Init", "SDL_Quit", "SDL_CreateWindow", "SDL_DestroyWindow",
    "SDL_SetWindowTitle", "SDL_SetWindowSize", "SDL_SetWindowPosition",
    "SDL_MinimizeWindow", "SDL_MaximizeWindow", "SDL_RestoreWindow",
    "SDL_ShowWindow", "SDL_HideWindow", "SDL_GetNumVideoDisplays",
    "SDL_GetDisplayName", "SDL_GetDisplayBounds",
    "SDL_PollEvent", "SDL_WaitEvent", "SDL_PumpEvents",
    "SDL_CreateRenderer", "SDL_RenderClear", "SDL_RenderPresent", "SDL_SetRenderDrawColor", "SDL_RenderFillRect", "SDL_RenderDrawRect", "SDL_RenderCopy",
    "SDL_RenderDrawLine", "SDL_RenderDrawCircle", "SDL_RenderFillCircle", "SDL_RenderFillTriangle", "SDL_RenderCopyBlended", "SDL_RenderCopyScaled", "SDL_RenderCopyBilinear",
    "SDL_CreateTextureFromSurface",
    "SDL_GetBasePath", "SDL_GetPrefPath", "SDL_RWops", "SDL_RWFromFile", "SDL_RWToFile", "SDL_GetClipboardText", "SDL_SetClipboardText", "SDL_GetClipboardData", "SDL_SetClipboardData",
    "SDL_GetTicks", "SDL_Delay", "SDL_GetPerformanceCounter", "SDL_GetPerformanceFrequency", "SDL_AddTimer", "SDL_RemoveTimer",
    "SDL_INIT_TIMER", "SDL_INIT_AUDIO", "SDL_INIT_VIDEO", "SDL_INIT_JOYSTICK",
    "SDL_INIT_HAPTIC", "SDL_INIT_GAMEPAD", "SDL_INIT_EVENTS", "SDL_INIT_SENSOR",
    "SDL_INIT_EVERYTHING",
    "SDL_WINDOW_FULLSCREEN", "SDL_WINDOW_OPENGL", "SDL_WINDOW_SHOWN",
    "SDL_WINDOW_HIDDEN", "SDL_WINDOW_BORDERLESS", "SDL_WINDOW_RESIZABLE",
    "SDL_WINDOW_MINIMIZED", "SDL_WINDOW_MAXIMIZED", "SDL_WINDOW_MOUSE_GRABBED",
    "SDL_WINDOW_INPUT_FOCUS", "SDL_WINDOW_MOUSE_FOCUS", "SDL_WINDOW_FOREIGN",
    "SDL_WINDOW_ALLOW_HIGHDPI", "SDL_WINDOW_MOUSE_CAPTURE", "SDL_WINDOW_ALWAYS_ON_TOP",
    "SDL_WINDOW_SKIP_TASKBAR", "SDL_WINDOW_UTILITY", "SDL_WINDOW_TOOLTIP",
    "SDL_WINDOW_POPUP_MENU", "SDL_WINDOW_KEYBOARD_GRABBED", "SDL_WINDOW_VULKAN",
    "SDL_WINDOW_METAL",
    "SDL_RENDERER_SOFTWARE", "SDL_RENDERER_ACCELERATED", "SDL_RENDERER_PRESENTVSYNC", "SDL_RENDERER_TARGETTEXTURE",
    # Gamepad, Touch, Sensors, Haptics Events
    "SDL_FingerDownEvent", "SDL_FingerUpEvent", "SDL_FingerMotionEvent",
    "SDL_ControllerAxisEvent", "SDL_ControllerButtonEvent", "SDL_ControllerDeviceEvent",
    "SDL_SensorUpdateEvent",
    # Gamepad, Touch, Sensors, Haptics Types and Functions
    "SDL_GetTouchState", "SDL_GetGamepadState", "SDL_GetSensorState",
    "SDL_GamepadButton", "SDL_GamepadAxis", "SDL_GamepadDeviceState", "SDL_GamepadState",
    "SDL_SensorType", "SDL_SensorDeviceState", "SDL_SensorState",
    "SDL_HapticEffect", "SDL_HapticDevice",
    "SDL_HapticOpen", "SDL_HapticClose", "SDL_HapticRumbleSupported",
    "SDL_HapticRumblePlay", "SDL_HapticRumbleStop",
    "SDL_HapticNewEffect", "SDL_HapticRunEffect", "SDL_HapticStopEffect", "SDL_HapticDestroyEffect",
    "SDL_GameControllerButton", "SDL_GameControllerAxis", "SDL_GameControllerDeviceState",
    "SDL_GameControllerState", "SDL_GameControllerGetState"
]
