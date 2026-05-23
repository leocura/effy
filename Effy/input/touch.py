"""Touch and multi-touch input device snapshot representations."""
from __future__ import annotations
from dataclasses import dataclass
from Effy._internal.fp import pure


@dataclass(frozen=True, slots=True)
class Finger:
    """Represents a frozen snapshot of a single finger's state on a touch device.

    Attributes:
        id: Unique identifier for the finger.
        x: Normalized horizontal coordinate from 0.0 to 1.0.
        y: Normalized vertical coordinate from 0.0 to 1.0.
        pressure: Pressure value from 0.0 to 1.0.
    """

    id: int
    x: float
    y: float
    pressure: float


@dataclass(frozen=True, slots=True)
class TouchDeviceState:
    """Represents a frozen snapshot of a single touch device and its active fingers.

    Attributes:
        device_id: Unique identifier of the touch device.
        fingers: Set of active fingers currently touching the device.
    """

    device_id: int
    fingers: frozenset[Finger]


@dataclass(frozen=True, slots=True)
class TouchState:
    """Represents a frozen snapshot of all active touch devices.

    Attributes:
        devices: Set of active TouchDeviceStates.
    """

    devices: frozenset[TouchDeviceState]

    @pure
    def get_finger(self, device_id: int, finger_id: int) -> Finger | None:
        """Retrieve the state of a specific finger on a specific touch device.

        Args:
            device_id: Unique identifier of the target touch device.
            finger_id: Unique identifier of the target finger.

        Returns:
            The Finger snapshot if found, or None.
        """
        for dev in self.devices:
            if dev.device_id == device_id:
                for finger in dev.fingers:
                    if finger.id == finger_id:
                        return finger
        return None
