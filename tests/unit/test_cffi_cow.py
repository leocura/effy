"""Unit tests specifically verifying the native-backed, Copy-on-Write (COW) behavior of buffers."""

import pytest
import array
from Effy.video.surface import PixelBuffer
from Effy.audio.types import AudioBuffer, AudioSpec, AudioFormat
from Effy.types import Color
from Effy.video.rect import Rect
from Effy.render import draw_rect, fill_rect
from Effy.audio.stream import mix_buffers



def test_pixel_buffer_backend() -> None:
    """Verify that PixelBuffer is backed by a bytearray."""
    buf = PixelBuffer.create(8, 8)
    
    # Check internal data type
    import array
    assert isinstance(buf._data, array.array)
    assert len(buf._data) == 8 * 8
    assert all(x == 0 for x in buf._data)


def test_pixel_buffer_cow_on_write() -> None:
    """Verify that write_pixel performs a true Copy-on-Write and returns a new buffer."""
    buf1 = PixelBuffer.create(4, 4)
    color = Color(255, 128, 64, 255)
    
    buf2 = buf1.write_pixel(1, 2, color)
    
    # Buffers must be physically distinct
    assert buf1._data is not buf2._data
    
    # Verify correctness of read values
    assert buf1.get_pixel(1, 2) == Color(0, 0, 0, 0)
    assert buf2.get_pixel(1, 2) == color
    
    # Verify that writing out of bounds returns the exact same instance
    buf3 = buf2.write_pixel(-1, -1, color)
    assert buf3 is buf2


def test_audio_buffer_backend() -> None:
    """Verify that AudioBuffer is backed by array.array."""
    spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=10)
    buf = AudioBuffer.create(spec)
    
    assert isinstance(buf._data_array, array.array)
    
    view = buf._data
    assert isinstance(view, memoryview)
    assert len(view) == 10 * 2 * 2  # 10 samples * 2 channels * 2 bytes/sample
    assert all(x == 0 for x in view)


def test_audio_buffer_cow_on_write() -> None:
    """Verify that write_sample performs a true Copy-on-Write and returns a new buffer."""
    spec = AudioSpec(freq=44100, format=AudioFormat.F32, channels=1, samples=10)
    buf1 = AudioBuffer.create(spec)
    
    buf2 = buf1.write_sample(5, 0, 0.75)
    
    assert buf1._data_array is not buf2._data_array
    assert buf1.get_sample(5, 0) == 0.0
    assert buf2.get_sample(5, 0) == pytest.approx(0.75, abs=1e-4)
    
    # Out of bounds write should return exact same instance
    buf3 = buf2.write_sample(10, 0, 0.5)
    assert buf3 is buf2


def test_audio_from_bytes() -> None:
    """Verify creating an AudioBuffer from raw bytes via from_bytes."""
    spec = AudioSpec(freq=22050, format=AudioFormat.S16, channels=1, samples=4)
    raw_data = b"\x01\x00\x02\x00\x03\x00\x04\x00"
    
    buf = AudioBuffer.from_bytes(spec, raw_data)
    assert buf.spec == spec
    assert bytes(buf._data) == raw_data
    
    # Check that the buffer is backed by a new array.array block
    assert isinstance(buf._data_array, array.array)


def test_drawing_cow_safety() -> None:
    """Verify that drawing primitives do not mutate the original PixelBuffer."""
    base = PixelBuffer.create(10, 10)
    color = Color(255, 255, 255, 255)
    
    # Fill a rectangle
    filled = fill_rect(base, Rect(2, 2, 5, 5), color)
    assert base.get_pixel(3, 3) == Color(0, 0, 0, 0)
    assert filled.get_pixel(3, 3) == color
    
    # Draw a rectangle
    drawn = draw_rect(filled, Rect(0, 0, 10, 10), Color(0, 255, 0, 255))
    assert filled.get_pixel(0, 0) == Color(0, 0, 0, 0)
    assert drawn.get_pixel(0, 0) == Color(0, 255, 0, 255)
    # The inner filled pixel remains white
    assert drawn.get_pixel(3, 3) == color


def test_audio_mixing_cow_safety() -> None:
    """Verify that audio mixing creates a completely new buffer and is pure."""
    spec = AudioSpec(freq=44100, format=AudioFormat.F32, channels=1, samples=5)
    a = AudioBuffer.create(spec).write_sample(2, 0, 0.3)
    b = AudioBuffer.create(spec).write_sample(2, 0, 0.4)
    
    mixed = mix_buffers(a, b).unwrap()
    
    assert mixed.get_sample(2, 0) == pytest.approx(0.7, abs=1e-4)
    # Originals are untouched
    assert a.get_sample(2, 0) == pytest.approx(0.3, abs=1e-4)
    assert b.get_sample(2, 0) == pytest.approx(0.4, abs=1e-4)
