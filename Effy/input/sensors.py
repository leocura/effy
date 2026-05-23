"""Sensors snapshot state representation."""
from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from Effy._internal.fp import pure


class SensorType(IntEnum):
    """Types of supported sensors."""

    UNKNOWN = 0
    ACCEL = 1
    GYRO = 2


@dataclass(frozen=True, slots=True)
class SensorDeviceState:
    """Represents a frozen snapshot of a single sensor's state."""

    device_id: int
    name: str
    type: SensorType
    data: tuple[float, float, float]


@dataclass(frozen=True, slots=True)
class SensorState:
    """Represents a snapshot of all active sensor states."""

    devices: frozenset[SensorDeviceState]

    @pure
    def get_sensor(self, device_id: int) -> SensorDeviceState | None:
        """Retrieve the state of a specific sensor by its device ID.

        Args:
            device_id: The ID of the sensor device.

        Returns:
            The SensorDeviceState instance if found, or None.
        """
        for dev in self.devices:
            if dev.device_id == device_id:
                return dev
        return None
