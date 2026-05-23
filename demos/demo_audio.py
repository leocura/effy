"""Audio demo: open the native audio device and play a 440 Hz sine wave for 2 seconds.

The script prints which audio backend was selected (PulseAudio, ALSA, or dummy).

Pass criteria: you hear a clean, undistorted A4 tone for approximately 2 seconds.
"""

import os
import sys

# Ensure parent directory is in sys.path to find Effy package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.implementation.name != "pypy":
    print(
        "ERROR: Effy requires PyPy. Run with:\n"
        "  pypy3 demos/test_audio.py",
        file=sys.stderr,
    )
    sys.exit(1)

import math

from Effy.init import init, quit, InitFlag
from Effy.audio.types import AudioSpec, AudioFormat, AudioBuffer
from Effy.audio.device import open_audio_device, queue_audio, close_audio_device
from Effy._internal.result import Ok, Err
from Effy._internal.registry import get_platform_adapter


def _build_sine_buffer(spec: AudioSpec, frequency: float, duration_s: float) -> AudioBuffer:
    """Build a pure sine wave AudioBuffer.

    Args:
        spec: The AudioSpec describing the format, sample rate, and channels.
        frequency: The sine frequency in Hz.
        duration_s: Duration of the tone in seconds.

    Returns:
        An AudioBuffer containing the sine wave samples.
    """
    total_frames = int(spec.freq * duration_s)
    chunk_spec = AudioSpec(
        freq=spec.freq,
        format=spec.format,
        channels=spec.channels,
        samples=total_frames,
    )
    buf = AudioBuffer.create(chunk_spec)

    for i in range(total_frames):
        sample = math.sin(2.0 * math.pi * frequency * i / spec.freq)
        for ch in range(spec.channels):
            buf = buf.write_sample(i, ch, sample)

    return buf


def _detect_audio_backend() -> str:
    """Inspect the live platform adapter to report the audio backend in use.

    Returns:
        A human-readable string identifying the backend (e.g. 'PulseAudio').
    """
    adapter = get_platform_adapter()
    if adapter is None:
        return "none"

    # The LinuxX11Adapter stores open devices in _audio_devices keyed by id(device)
    audio_devices = getattr(adapter, "_audio_devices", {})
    for device in audio_devices.values():
        backend = getattr(device, "backend_type", None)
        if backend == "pulseaudio":
            return "PulseAudio"
        if backend == "alsa":
            return "ALSA"
        if backend == "dummy":
            return "Dummy (no hardware audio found)"
    return "unknown"


def main() -> None:
    """Initialize audio, play a 440 Hz sine wave, then clean up."""
    init_result = init(InitFlag.AUDIO).run()
    if isinstance(init_result, Err):
        print(f"Init failed: {init_result.error}", file=sys.stderr)
        return
    init_ctx = init_result.value

    backend = _detect_audio_backend()
    print(f"Audio backend: {backend}")

    spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=1024)
    dev_result = open_audio_device(None, False, spec).run()
    if isinstance(dev_result, Err):
        print(f"Failed to open audio device: {dev_result.error}", file=sys.stderr)
        quit(init_ctx).run()
        return
    device = dev_result.value

    print("Playing 440 Hz sine wave for 2 seconds…")
    buf = _build_sine_buffer(spec, frequency=440.0, duration_s=2.0)

    # Queue in 1024-sample chunks matching the device buffer size
    chunk_frames = spec.samples
    total_frames = buf.spec.samples
    bytes_per_frame = (2 if spec.format == AudioFormat.S16 else 4) * spec.channels

    offset = 0
    while offset < total_frames:
        end = min(offset + chunk_frames, total_frames)
        chunk_spec = AudioSpec(
            freq=spec.freq,
            format=spec.format,
            channels=spec.channels,
            samples=end - offset,
        )
        # Slice the raw bytes for this chunk
        raw = bytes(buf._data)[offset * bytes_per_frame : end * bytes_per_frame]
        chunk_buf = AudioBuffer.from_bytes(chunk_spec, raw)
        queue_audio(device, chunk_buf).run()
        offset = end

    print("Done. Closing audio device.")
    close_audio_device(device).run()
    quit(init_ctx).run()


if __name__ == "__main__":
    main()
