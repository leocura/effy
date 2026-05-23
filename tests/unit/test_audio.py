from Effy.audio import (
    AudioSpec, AudioBuffer, AudioFormat, AudioDevice,
    silence, mix_buffers, mix_streams, open_audio_device, queue_audio, close_audio_device, convert_audio
)
from Effy._internal.registry import set_platform_adapter
from Effy.platform.headless import HeadlessAdapter
from Effy.types import Effect, Ok
import pytest

def test_audio_buffer_create() -> None:
    spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=1024)
    buf = AudioBuffer.create(spec)
    assert buf.spec == spec
    assert len(buf._data) == 1024 * 2 * 2 # samples * channels * bytes_per_sample

def test_audio_buffer_write_get_s16() -> None:
    spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=1, samples=10)
    buf = AudioBuffer.create(spec)
    
    buf2 = buf.write_sample(0, 0, 0.5)
    assert buf2.get_sample(0, 0) == pytest.approx(0.5, abs=1e-4)
    
    # Test clipping
    buf3 = buf2.write_sample(1, 0, 1.5)
    assert buf3.get_sample(1, 0) == pytest.approx(1.0, abs=1e-4)
    
    buf4 = buf3.write_sample(2, 0, -1.5)
    assert buf4.get_sample(2, 0) == pytest.approx(-1.0, abs=1e-4)

def test_audio_buffer_write_get_f32() -> None:
    spec = AudioSpec(freq=44100, format=AudioFormat.F32, channels=1, samples=10)
    buf = AudioBuffer.create(spec)
    
    buf2 = buf.write_sample(0, 0, 0.5)
    assert buf2.get_sample(0, 0) == 0.5
    
    # Test values outside [-1, 1] for F32
    buf3 = buf2.write_sample(1, 0, 2.0)
    assert buf3.get_sample(1, 0) == 2.0

def test_audio_buffer_immutability() -> None:
    """Verify that writing to AudioBuffer returns a new buffer and does not mutate the original."""
    spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=1, samples=10)
    buf = AudioBuffer.create(spec)
    
    buf2 = buf.write_sample(0, 0, 0.5)
    assert buf2 is not buf
    assert buf2._data is not buf._data
    assert buf.get_sample(0, 0) == 0.0
    assert buf2.get_sample(0, 0) == pytest.approx(0.5, abs=1e-4)

def test_silence() -> None:
    spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=1024)
    buf = silence(spec)
    assert buf.spec == spec
    assert all(v == 0 for v in buf._data)

def test_mix_buffers() -> None:
    spec = AudioSpec(freq=44100, format=AudioFormat.F32, channels=1, samples=10)
    buf1 = AudioBuffer.create(spec).write_sample(0, 0, 0.5)
    buf2 = AudioBuffer.create(spec).write_sample(0, 0, 0.3)
    
    mixed = mix_buffers(buf1, buf2).unwrap()
    assert mixed.get_sample(0, 0) == pytest.approx(0.8)
    
    # Test with S16 to ensure clipping/scaling works in mix
    spec_s16 = AudioSpec(freq=44100, format=AudioFormat.S16, channels=1, samples=10)
    buf1_s16 = AudioBuffer.create(spec_s16).write_sample(0, 0, 0.5)
    buf2_s16 = AudioBuffer.create(spec_s16).write_sample(0, 0, 0.6) # Sum is 1.1, should clip to 1.0
    
    mixed_s16 = mix_buffers(buf1_s16, buf2_s16).unwrap()
    assert mixed_s16.get_sample(0, 0) == pytest.approx(1.0, abs=1e-4)

def test_mix_buffers_mismatch() -> None:
    spec1 = AudioSpec(freq=44100, format=AudioFormat.F32, channels=1, samples=10)
    spec2 = AudioSpec(freq=22050, format=AudioFormat.F32, channels=1, samples=10)
    buf1 = AudioBuffer.create(spec1)
    buf2 = AudioBuffer.create(spec2)
    
    res = mix_buffers(buf1, buf2)
    assert res.is_err()

class MockAudioStream:
    def __init__(self, buffer: AudioBuffer):
        self.buffer = buffer
    def pull(self, frames: int) -> AudioBuffer:
        return self.buffer

def test_mix_streams() -> None:
    spec = AudioSpec(freq=44100, format=AudioFormat.F32, channels=1, samples=10)
    buf1 = AudioBuffer.create(spec).write_sample(0, 0, 0.5)
    buf2 = AudioBuffer.create(spec).write_sample(0, 0, 0.3)
    
    stream1 = MockAudioStream(buf1)
    stream2 = MockAudioStream(buf2)
    
    mixed = mix_streams([stream1, stream2], frames=10, spec=spec).unwrap()
    assert mixed.get_sample(0, 0) == pytest.approx(0.8)

def test_convert_audio_format() -> None:
    spec_s16 = AudioSpec(freq=44100, format=AudioFormat.S16, channels=1, samples=10)
    spec_f32 = AudioSpec(freq=44100, format=AudioFormat.F32, channels=1, samples=10)
    
    buf_s16 = AudioBuffer.create(spec_s16).write_sample(0, 0, 0.5)
    buf_f32 = convert_audio(buf_s16, spec_f32)
    
    assert buf_f32.spec == spec_f32
    assert buf_f32.get_sample(0, 0) == pytest.approx(0.5, abs=1e-4)
    
    # Back to S16
    buf_s16_back = convert_audio(buf_f32, spec_s16)
    assert buf_s16_back.spec == spec_s16
    assert buf_s16_back.get_sample(0, 0) == pytest.approx(0.5, abs=1e-4)

def test_convert_audio_channels() -> None:
    spec_mono = AudioSpec(freq=44100, format=AudioFormat.F32, channels=1, samples=10)
    spec_stereo = AudioSpec(freq=44100, format=AudioFormat.F32, channels=2, samples=10)
    
    # Mono to Stereo
    buf_mono = AudioBuffer.create(spec_mono).write_sample(0, 0, 0.7)
    buf_stereo = convert_audio(buf_mono, spec_stereo)
    
    assert buf_stereo.spec == spec_stereo
    assert buf_stereo.get_sample(0, 0) == pytest.approx(0.7, abs=1e-6)
    assert buf_stereo.get_sample(0, 1) == pytest.approx(0.7, abs=1e-6)
    
    # Stereo to Mono
    buf_stereo = AudioBuffer.create(spec_stereo).write_sample(0, 0, 0.8).write_sample(0, 1, 0.2)
    buf_mono_back = convert_audio(buf_stereo, spec_mono)
    
    assert buf_mono_back.spec == spec_mono
    assert buf_mono_back.get_sample(0, 0) == pytest.approx(0.5)

def test_convert_audio_resampling() -> None:
    spec_44 = AudioSpec(freq=44100, format=AudioFormat.F32, channels=1, samples=10)
    spec_22 = AudioSpec(freq=22050, format=AudioFormat.F32, channels=1, samples=5)
    
    buf_44 = AudioBuffer.create(spec_44)
    for i in range(10):
        buf_44 = buf_44.write_sample(i, 0, float(i) / 10.0)
        
    buf_22 = convert_audio(buf_44, spec_22)
    assert buf_22.spec == spec_22
    # At index 2 of 22050, source index should be 2 / (22050/44100) = 4
    assert buf_22.get_sample(2, 0) == pytest.approx(0.4)

def test_audio_device_lifecycle() -> None:
    adapter = HeadlessAdapter()
    set_platform_adapter(adapter)
    
    try:
        spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=1024)
        
        # 1. Open Device
        open_eff = open_audio_device(None, False, spec)
        assert isinstance(open_eff, Effect)
        res = open_eff.run()
        assert isinstance(res, Ok)
        device = res.value
        assert isinstance(device, AudioDevice)
        assert device.spec == spec
        
        # 2. Queue Audio
        buf = silence(spec).write_sample(0, 0, 0.5)
        queue_eff = queue_audio(device, buf)
        assert isinstance(queue_eff, Effect)
        queue_res = queue_eff.run()
        assert isinstance(queue_res, Ok)
        
        # 3. Close Device
        close_eff = close_audio_device(device)
        assert isinstance(close_eff, Effect)
        close_eff.run()
        
    finally:
        set_platform_adapter(None)
