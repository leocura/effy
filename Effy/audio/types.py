"""Pure functional audio buffer types wrapping native array.array."""

from __future__ import annotations
import array
from dataclasses import dataclass
from enum import IntEnum
from typing import cast, Any
from Effy._internal.fp import _EVOLVE_SENTINEL, pure


class AudioFormat(IntEnum):
    """Supported audio formats (signed 16-bit or 32-bit float)."""
    S16 = 1
    F32 = 2


@dataclass(frozen=True, slots=True)
class AudioSpec:
    """An immutable specification for audio formatting.

    Attributes:
        freq: DSP frequency in samples per second (e.g. 44100).
        format: Supported audio format (e.g. AudioFormat.S16 or AudioFormat.F32).
        channels: Number of output audio channels (e.g. 1 for mono, 2 for stereo).
        samples: Audio buffer size in sample frames.
    """
    freq: int
    format: AudioFormat
    channels: int
    samples: int


@dataclass(frozen=True, slots=True)
class AudioBuffer:
    """An immutable audio buffer wrapping standard array.array.
    
    All modifications return a new AudioBuffer constructed via CoW copy.
    """
    spec: AudioSpec
    _data_array: array.array[Any]
    _is_transient: bool = False

    @staticmethod
    def create(spec: AudioSpec) -> AudioBuffer:
        """Create a new AudioBuffer initialized to silence.
        
        Args:
            spec: The AudioSpec specifying format, channels, and sample count.
            
        Returns:
            A new AudioBuffer instance.
        """
        typecode = 'h' if spec.format == AudioFormat.S16 else 'f'
        arr = array.array(typecode, [0 if typecode == 'h' else 0.0] * (spec.samples * spec.channels))
        return AudioBuffer(spec=spec, _data_array=arr, _is_transient=False)

    @property
    def _data(self) -> memoryview:
        """Expose a compatible byte-oriented memoryview of the underlying memory.
        
        Returns:
            A memoryview wrapping the raw memory buffer.
        """
        return memoryview(self._data_array).cast('B')

    def _cow(self) -> tuple[array.array[Any], bool]:
        """Return (data_array, is_transient). Copies only if not already transient."""
        if self._is_transient:
            return self._data_array, True
        new_array = array.array(self._data_array.typecode, self._data_array)
        return new_array, True

    def evolve(self, spec: AudioSpec | object = _EVOLVE_SENTINEL) -> AudioBuffer:
        """Evolve the AudioBuffer with a new specification.
        
        Args:
            spec: The new specification or sentinel to keep the existing one.
            
        Returns:
            A new AudioBuffer with the updated spec.
        """
        return AudioBuffer(
            spec=self.spec if spec is _EVOLVE_SENTINEL else cast(AudioSpec, spec),
            _data_array=self._data_array,
            _is_transient=self._is_transient
        )

    @pure
    def write_sample(self, frame_index: int, channel: int, value: float) -> AudioBuffer:
        """Write a single audio sample and return a new AudioBuffer.
        
        Args:
            frame_index: The index of the frame.
            channel: The channel index.
            value: The float sample value to write (-1.0 to 1.0).
            
        Returns:
            A brand-new AudioBuffer.
        """
        if frame_index < 0 or frame_index >= self.spec.samples or channel < 0 or channel >= self.spec.channels:
            return self

        data_array, transient = self._cow()
        idx = frame_index * self.spec.channels + channel

        if self.spec.format == AudioFormat.S16:
            v = int(max(-1.0, min(1.0, value)) * 32767)
            data_array[idx] = v
        else:
            data_array[idx] = value

        return AudioBuffer(
            spec=self.spec,
            _data_array=data_array,
            _is_transient=transient
        )

    @pure
    def get_sample(self, frame_index: int, channel: int) -> float:
        """Read a single audio sample from the buffer.
        
        Args:
            frame_index: The index of the frame.
            channel: The channel index.
            
        Returns:
            The sample value as a float, or 0.0 if out of bounds.
        """
        if frame_index < 0 or frame_index >= self.spec.samples or channel < 0 or channel >= self.spec.channels:
            return 0.0

        idx = frame_index * self.spec.channels + channel

        if self.spec.format == AudioFormat.S16:
            val = self._data_array[idx]
            return float(val) / 32767.0
        else:
            return float(self._data_array[idx])

    @staticmethod
    def from_bytes(spec: AudioSpec, data: bytes) -> AudioBuffer:
        """Create a new AudioBuffer from a bytes object.
        
        Args:
            spec: The AudioSpec specifying format, channels, and sample count.
            data: The bytes containing the audio data.
            
        Returns:
            A new AudioBuffer instance.
        """
        typecode = 'h' if spec.format == AudioFormat.S16 else 'f'
        bytes_per_sample = 2 if spec.format == AudioFormat.S16 else 4
        expected_size_bytes = spec.samples * spec.channels * bytes_per_sample
        
        raw_bytes = data[:expected_size_bytes]
        if len(raw_bytes) < expected_size_bytes:
            raw_bytes += b'\x00' * (expected_size_bytes - len(raw_bytes))
            
        arr = array.array(typecode)
        arr.frombytes(raw_bytes)
        return AudioBuffer(spec=spec, _data_array=arr, _is_transient=False)

    def __eq__(self, other: object) -> bool:
        """Check equality with another AudioBuffer.
        
        Args:
            other: The other object to compare with.
            
        Returns:
            True if equal, False otherwise.
        """
        if not isinstance(other, AudioBuffer):
            return NotImplemented
        if self.spec != other.spec:
            return False
        return self._data_array == other._data_array


def _freeze_prevent_set(self: object, name: str, value: object) -> None:
    """Prevent assignment to any field, enforcing strict immutability."""
    from dataclasses import FrozenInstanceError
    raise FrozenInstanceError(f"cannot assign to field {name!r}")


def _freeze_prevent_del(self: object, name: str) -> None:
    """Prevent deletion of any field, enforcing strict immutability."""
    from dataclasses import FrozenInstanceError
    raise FrozenInstanceError(f"cannot delete field {name!r}")


AudioBuffer.__setattr__ = _freeze_prevent_set  # type: ignore
AudioBuffer.__delattr__ = _freeze_prevent_del  # type: ignore


@dataclass(frozen=True, slots=True)
class AudioDevice:
    """An immutable audio device representation.

    Attributes:
        id: Unique integer identifier of the audio playback/recording device.
        spec: The AudioSpec formatting specification configured for the device.
    """
    id: int
    spec: AudioSpec

