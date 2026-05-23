"""Haptics and Force Feedback API."""
from __future__ import annotations
from dataclasses import dataclass
from Effy.types import Effect
from Effy._internal.result import Result, Err
from Effy.error import EffyError
from Effy._internal.registry import get_platform_adapter
from Effy.platform import PlatformHapticHandle


@dataclass(frozen=True, slots=True)
class HapticEffect:
    """Represents a force feedback effect configuration."""

    type: str  # e.g., "rumble", "constant", "periodic", "ramp"
    duration_ms: int
    strength: float  # 0.0 to 1.0
    attack_ms: int = 0
    fade_ms: int = 0
    large_rumble: float = 0.0
    small_rumble: float = 0.0


@dataclass(frozen=True, slots=True)
class HapticDevice:
    """Opaque representation of a haptic device."""

    device_id: PlatformHapticHandle
    name: str


def open_haptic_device(device_id: int) -> Effect[Result[HapticDevice, EffyError]]:
    """Open a haptic device for force feedback.

    Args:
        device_id: The index/ID of the device to open.

    Returns:
        An Effect resolving to a Result containing the HapticDevice or an EffyError.
    """
    def _run() -> Result[HapticDevice, EffyError]:
        """Thunk implementing platform haptic device opening logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return Err(EffyError(code=-1, message="Haptic subsystem not available"))
        res = adapter.open_haptic(device_id)
        return res.map(lambda h: HapticDevice(device_id=h, name=f"Haptic Device {device_id}"))
    return Effect(_run)


def close_haptic_device(device: HapticDevice) -> Effect[None]:
    """Close an active haptic device.

    Args:
        device: The HapticDevice instance to close.

    Returns:
        An Effect that closes the device.
    """
    def _run() -> None:
        """Thunk implementing platform haptic device closing logic."""
        adapter = get_platform_adapter()
        if adapter:
            adapter.close_haptic(device.device_id)
    return Effect(_run)


def is_haptic_rumble_supported(device: HapticDevice) -> Effect[bool]:
    """Check if the haptic device supports simple rumble.

    Args:
        device: The HapticDevice to query.

    Returns:
        An Effect resolving to True if supported, False otherwise.
    """
    def _run() -> bool:
        """Thunk implementing platform haptic rumble capability query logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return False
        return bool(adapter.is_rumble_supported(device.device_id))
    return Effect(_run)


def play_haptic_rumble(
    device: HapticDevice, strength: float, duration_ms: int
) -> Effect[Result[None, EffyError]]:
    """Play a simple rumble effect on the device.

    Args:
        device: The HapticDevice to run the rumble on.
        strength: The rumble intensity from 0.0 to 1.0.
        duration_ms: How long the rumble should play in milliseconds.

    Returns:
        An Effect resolving to a Result indicating success or failure.
    """
    def _run() -> Result[None, EffyError]:
        """Thunk implementing platform haptic rumble playback logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return Err(EffyError(code=-1, message="Haptic rumble not supported"))
        return adapter.play_rumble(device.device_id, strength, duration_ms)
    return Effect(_run)


def stop_haptic_rumble(device: HapticDevice) -> Effect[Result[None, EffyError]]:
    """Stop any active rumble effect on the device.

    Args:
        device: The HapticDevice to stop.

    Returns:
        An Effect resolving to a Result indicating success or failure.
    """
    def _run() -> Result[None, EffyError]:
        """Thunk implementing platform haptic rumble stop logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return Err(EffyError(code=-1, message="Haptic rumble not supported"))
        return adapter.stop_rumble(device.device_id)
    return Effect(_run)


def upload_haptic_effect(
    device: HapticDevice, effect: HapticEffect
) -> Effect[Result[int, EffyError]]:
    """Upload a custom haptic effect to the device.

    Args:
        device: The HapticDevice to upload to.
        effect: The HapticEffect description to upload.

    Returns:
        An Effect resolving to a Result containing the assigned effect ID or an EffyError.
    """
    def _run() -> Result[int, EffyError]:
        """Thunk implementing platform custom haptic effect upload logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return Err(EffyError(code=-1, message="Haptic custom effects not supported"))
        return adapter.upload_effect(device.device_id, effect)
    return Effect(_run)


def run_haptic_effect(
    device: HapticDevice,
    effect_id: int,
    iterations: int = 1,
) -> Effect[Result[None, EffyError]]:
    """Run an uploaded haptic effect.

    Args:
        device: The HapticDevice instance.
        effect_id: The ID of the uploaded effect.
        iterations: The number of times to run the effect (default 1).

    Returns:
        An Effect resolving to a Result indicating success or failure.
    """
    def _run() -> Result[None, EffyError]:
        """Thunk implementing platform custom haptic effect execution logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return Err(EffyError(code=-1, message="Haptic custom effects not supported"))
        return adapter.run_effect(device.device_id, effect_id, iterations)
    return Effect(_run)


def stop_haptic_effect(device: HapticDevice, effect_id: int) -> Effect[Result[None, EffyError]]:
    """Stop a running haptic effect.

    Args:
        device: The HapticDevice instance.
        effect_id: The ID of the effect to stop.

    Returns:
        An Effect resolving to a Result indicating success or failure.
    """
    def _run() -> Result[None, EffyError]:
        """Thunk implementing platform custom haptic effect stop logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return Err(EffyError(code=-1, message="Haptic custom effects not supported"))
        return adapter.stop_effect(device.device_id, effect_id)
    return Effect(_run)


def destroy_haptic_effect(device: HapticDevice, effect_id: int) -> Effect[None]:
    """Destroy an uploaded haptic effect to free resources.

    Args:
        device: The HapticDevice instance.
        effect_id: The ID of the effect to destroy.

    Returns:
        An Effect that destroys the effect.
    """
    def _run() -> None:
        """Thunk implementing platform custom haptic effect destruction/release logic."""
        adapter = get_platform_adapter()
        if adapter:
            adapter.destroy_effect(device.device_id, effect_id)
    return Effect(_run)

