from __future__ import annotations
from typing import cast
from Effy.types import Effect
from Effy._internal.result import Ok, Err, Result
from Effy.error import SDLError
from Effy._internal.registry import get_platform_adapter
from Effy.audio.types import AudioSpec, AudioBuffer, AudioDevice
from Effy.platform import PlatformAudioHandle

def open_audio_device(
    device: str | None,
    is_capture: bool,
    desired: AudioSpec,
) -> Effect[Result[AudioDevice, SDLError]]:
    """Open an audio device for playback or capture."""
    def _run() -> Result[AudioDevice, SDLError]:
        """Thunk implementing native platform audio opening logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return Err(SDLError(code=-1, message="No platform adapter initialized"))
        
        res = adapter.open_audio(desired)
        if isinstance(res, Err):
            return cast(Result[AudioDevice, SDLError], res)
        
        handle = res.value
        return Ok(AudioDevice(id=handle, spec=desired))
    return Effect(_run)

def queue_audio(device: AudioDevice, buf: AudioBuffer) -> Effect[Result[None, SDLError]]:
    """Queue audio data to the given audio device."""
    def _run() -> Result[None, SDLError]:
        """Thunk implementing native platform audio queueing/writing logic."""
        adapter = get_platform_adapter()
        if not adapter:
            return Err(SDLError(code=-1, message="No platform adapter initialized"))
        
        adapter.write_audio(cast(PlatformAudioHandle, device.id), bytes(buf._data))
        return Ok(None)
    return Effect(_run)

def close_audio_device(device: AudioDevice) -> Effect[None]:
    """Close the given audio device."""
    def _run() -> None:
        """Thunk implementing native platform audio closing/release logic."""
        adapter = get_platform_adapter()
        if adapter:
            adapter.close_audio(cast(PlatformAudioHandle, device.id))
    return Effect(_run)
