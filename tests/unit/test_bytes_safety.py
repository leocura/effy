"""Unit tests for verifying absolute immutability and branching safety of buffers."""

import pytest
from dataclasses import FrozenInstanceError
from Effy.video.surface import PixelBuffer
from Effy.audio.types import AudioBuffer, AudioSpec, AudioFormat
from Effy.types import Color


def test_pixel_buffer_strict_immutability() -> None:
    """Verify that PixelBuffer is frozen and its attributes cannot be mutated."""
    buf = PixelBuffer.create(10, 10)
    with pytest.raises(FrozenInstanceError):
        buf.width = 20  # type: ignore

    with pytest.raises(FrozenInstanceError):
        buf._data = b""  # type: ignore


def test_pixel_buffer_branching_safety() -> None:
    """Verify that writing pixels creates new instances and does not leak between branches."""
    base = PixelBuffer.create(10, 10)
    
    # Branch A
    branch_a = base.write_pixel(1, 1, Color(255, 0, 0, 255))
    
    # Branch B
    branch_b = base.write_pixel(1, 1, Color(0, 255, 0, 255))
    
    # Base remains transparent black
    assert base.get_pixel(1, 1) == Color(0, 0, 0, 0)
    
    # Branch A and B are independent
    assert branch_a.get_pixel(1, 1) == Color(255, 0, 0, 255)
    assert branch_b.get_pixel(1, 1) == Color(0, 255, 0, 255)
    
    # Assert physical separation of data sequences
    assert branch_a._data is not base._data
    assert branch_b._data is not base._data
    assert branch_a._data is not branch_b._data


def test_audio_buffer_strict_immutability() -> None:
    """Verify that AudioBuffer is frozen and its attributes cannot be mutated."""
    spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=100)
    buf = AudioBuffer.create(spec)
    
    with pytest.raises(FrozenInstanceError):
        buf.spec = spec  # type: ignore

    with pytest.raises(FrozenInstanceError):
        buf._data = b""  # type: ignore


def test_audio_buffer_branching_safety() -> None:
    """Verify that writing audio samples creates new instances and does not leak between branches."""
    spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=100)
    base = AudioBuffer.create(spec)
    
    # Branch A
    branch_a = base.write_sample(0, 0, 0.5)
    
    # Branch B
    branch_b = base.write_sample(0, 0, -0.5)
    
    # Base remains silent
    assert base.get_sample(0, 0) == 0.0
    
    # Branch A and B are independent
    assert branch_a.get_sample(0, 0) == pytest.approx(0.5, abs=1e-4)
    assert branch_b.get_sample(0, 0) == pytest.approx(-0.5, abs=1e-4)
    
    # Assert physical separation of data sequences
    assert branch_a._data is not base._data
    assert branch_b._data is not base._data
    assert branch_a._data is not branch_b._data
