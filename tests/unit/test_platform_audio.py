"""Unit tests for the platform-specific audio driver integrations (Linux and Windows)."""

from Effy._internal.result import Ok
from Effy.audio.types import AudioSpec, AudioFormat
from Effy.platform.linux_x11 import LinuxX11Adapter
from Effy.platform.windows_gdi import WindowsGDIAdapter

def test_linux_audio_fallback(capsys) -> None:
    """Verify that the Linux audio driver gracefully falls back to dummy with a stderr warning if hardware is unavailable."""
    adapter = LinuxX11Adapter()
    spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=1024)
    
    res = adapter.open_audio(spec)
    assert isinstance(res, Ok)
    handle = res.value
    
    # It must be created and tracked
    assert handle is not None
    assert handle in adapter._audio_devices
    device = adapter._audio_devices[handle]
    
    # If it fell back to dummy, it must have printed a warning to stderr
    if device.backend_type == "dummy":
        captured = capsys.readouterr()
        assert "Warning: Failed to initialize native audio hardware" in captured.err
        assert device.handle is None
    
    # Test writing to the device does not crash
    adapter.write_audio(handle, b"\x00" * 4096)
    
    # Test closing the device
    adapter.close_audio(handle)
    assert handle not in adapter._audio_devices


def test_windows_audio_fallback(capsys) -> None:
    """Verify that the Windows audio driver gracefully falls back to dummy with a stderr warning if hardware is unavailable or not on Windows."""
    adapter = WindowsGDIAdapter()
    spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=1024)
    
    res = adapter.open_audio(spec)
    assert isinstance(res, Ok)
    handle = res.value
    
    # It must be created and tracked
    assert handle is not None
    assert handle in adapter._audio_devices
    device = adapter._audio_devices[handle]
    
    # Since we are running on Linux (or a system where WASAPI fails/is absent), it must fall back to dummy
    assert device.backend_type == "dummy"
    captured = capsys.readouterr()
    assert "Warning: Failed to initialize native audio hardware (WASAPI)" in captured.err
    assert device.audio_client is None
    assert device.render_client is None
    
    # Test writing to the dummy device does not crash
    adapter.write_audio(handle, b"\x00" * 4096)
    
    # Test closing the device
    adapter.close_audio(handle)
    assert handle not in adapter._audio_devices


def test_audio_open_default_spec() -> None:
    """Verify that passing None as the AudioSpec constructs a default spec in both adapters."""
    # Test Linux
    linux_adapter = LinuxX11Adapter()
    res_linux = linux_adapter.open_audio(None)
    assert isinstance(res_linux, Ok)
    linux_handle = res_linux.value
    linux_device = linux_adapter._audio_devices[linux_handle]
    assert linux_device.spec.freq == 44100
    assert linux_device.spec.format == AudioFormat.S16
    assert linux_device.spec.channels == 2
    assert linux_device.spec.samples == 1024
    linux_adapter.close_audio(linux_handle)

    # Test Windows
    windows_adapter = WindowsGDIAdapter()
    res_windows = windows_adapter.open_audio(None)
    assert isinstance(res_windows, Ok)
    windows_handle = res_windows.value
    windows_device = windows_adapter._audio_devices[windows_handle]
    assert windows_device.spec.freq == 44100
    assert windows_device.spec.format == AudioFormat.S16
    assert windows_device.spec.channels == 2
    assert windows_device.spec.samples == 1024
    windows_adapter.close_audio(windows_handle)
