"""Pure functional pixel buffer implementation wrapping Python array.array."""

from __future__ import annotations
import array
from dataclasses import dataclass
from typing import Any
from Effy.types import Color
from Effy._internal.fp import pure


@dataclass(frozen=True, slots=True)
class PixelBuffer:
    """An immutable pixel buffer that uses deferred drawing commands.
    
    All drawing operations are accumulated as O(1) commands in _commands_list.
    Rasterization is deferred and performed in a single optimized pass on demand.
    """
    width: int
    height: int
    pitch: int
    _data_cache: list[array.array[int] | memoryview | None]
    _commands_list: list[Any]
    _is_transient: bool = False

    @staticmethod
    def create(width: int, height: int) -> PixelBuffer:
        """Create a new PixelBuffer initialized to transparent black.
        
        Args:
            width: Width of the buffer in pixels.
            height: Height of the buffer in pixels.
            
        Returns:
            A new PixelBuffer instance.
        """
        from Effy._internal.pool import pixel_buffer_pool
        data = pixel_buffer_pool.get(width, height, zero=True)
        return PixelBuffer(
            width=width,
            height=height,
            pitch=width,
            _data_cache=[data],
            _commands_list=[],
            _is_transient=False
        )

    @property
    def _data(self) -> array.array[int]:
        """Get the materialized array. Forces rasterization of queued commands."""
        val = self._data_cache[0]
        if val is None:
            from Effy._internal.pool import pixel_buffer_pool
            val = pixel_buffer_pool.get(self.width, self.height, zero=True)
            self._data_cache[0] = val

        if not isinstance(val, array.array):
            raise TypeError(f"Expected array in _data_cache[0], got {type(val)}")

        if self._commands_list:
            if self._is_transient:
                data = val
            else:
                data = array.array('I', val)

            # Resolve commands onto the data buffer then clear the queue
            from Effy.render.renderer import _resolve_commands
            _resolve_commands(self, data, self._commands_list)

            # Cache the materialized result and clear the commands
            self._data_cache[0] = data
            mv = memoryview(data)
            if len(self._data_cache) > 1:
                self._data_cache[1] = mv
            else:
                self._data_cache.append(mv)
            self._commands_list.clear()
            object.__setattr__(self, '_is_transient', False)
            return data

        if len(self._data_cache) > 1:
            if self._data_cache[1] is None:
                self._data_cache[1] = memoryview(val)
        else:
            self._data_cache.append(memoryview(val))

        return val

    @property
    def _mv(self) -> memoryview:
        """Get a cached memoryview of the materialized bytearray."""
        # Force materialization first
        _ = self._data
        mv = self._data_cache[1]
        if not isinstance(mv, memoryview):
            raise TypeError("Expected memoryview in _data_cache[1]")
        return mv

    def _cow(self) -> tuple[array.array[int], bool]:
        """Clone data only if not already transient to implement copy-on-write.

        Returns:
            A tuple containing the underlying pixel array and a boolean indicating
            whether it is a transient/mutated buffer.
        """
        if self._is_transient:
            return self._data, True
        return array.array('I', self._data), True

    def _append_command(self, cmd: Any) -> PixelBuffer:
        """Append a drawing command and return a new PixelBuffer.

        Args:
            cmd: The deferred drawing command to append.

        Returns:
            A new PixelBuffer containing the updated command queue.
        """
        if self._is_transient:
            self._commands_list.append(cmd)
            return self
        else:
            new_commands = list(self._commands_list)
            new_commands.append(cmd)
            return PixelBuffer(
                width=self.width,
                height=self.height,
                pitch=self.pitch,
                _data_cache=self._data_cache,
                _commands_list=new_commands,
                _is_transient=True
            )

    @pure
    def write_pixel(self, x: int, y: int, color: Color) -> PixelBuffer:
        """Draw a pixel at (x, y) and return a new PixelBuffer.
        
        Args:
            x: X-coordinate of the pixel.
            y: Y-coordinate of the pixel.
            color: Color to write.
            
        Returns:
            A brand-new PixelBuffer with the updated pixel.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return self

        data, transient = self._cow()
        offset = y * self.pitch + x
        data[offset] = color.r | (color.g << 8) | (color.b << 16) | (color.a << 24)

        return PixelBuffer(
            width=self.width,
            height=self.height,
            pitch=self.pitch,
            _data_cache=[data],
            _commands_list=[],
            _is_transient=transient
        )

    @pure
    def get_pixel(self, x: int, y: int) -> Color:
        """Read the Color at (x, y).
        
        Args:
            x: X-coordinate of the pixel.
            y: Y-coordinate of the pixel.
            
        Returns:
            The Color at the specified coordinates, or transparent black if out of bounds.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return Color(0, 0, 0, 0)

        data = self._data
        offset = y * self.pitch + x
        val = data[offset]
        return Color(
            r=val & 0xFF,
            g=(val >> 8) & 0xFF,
            b=(val >> 16) & 0xFF,
            a=(val >> 24) & 0xFF
        )

    def __eq__(self, other: object) -> bool:
        """Check equality with another PixelBuffer based on dimensions and data content.
        
        Args:
            other: The other object to compare with.
            
        Returns:
            True if equal, False otherwise.
        """
        if not isinstance(other, PixelBuffer):
            return NotImplemented
        if (self.width != other.width or 
            self.height != other.height or 
            self.pitch != other.pitch):
            return False
        
        return self._data == other._data


def _freeze_prevent_set(self: object, name: str, value: object) -> None:
    """Prevent assignment to any field, enforcing strict immutability.

    Args:
        name: Name of the attribute.
        value: Value to set.

    Raises:
        FrozenInstanceError: Always raised to prevent mutation.
    """
    from dataclasses import FrozenInstanceError
    raise FrozenInstanceError(f"cannot assign to field {name!r}")


def _freeze_prevent_del(self: object, name: str) -> None:
    """Prevent deletion of any field, enforcing strict immutability.

    Args:
        name: Name of the attribute.

    Raises:
        FrozenInstanceError: Always raised to prevent deletion.
    """
    from dataclasses import FrozenInstanceError
    raise FrozenInstanceError(f"cannot delete field {name!r}")


PixelBuffer.__setattr__ = _freeze_prevent_set  # type: ignore
PixelBuffer.__delattr__ = _freeze_prevent_del  # type: ignore


