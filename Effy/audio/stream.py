"""Pure functional audio stream mixing routines using immutable bytes."""

from __future__ import annotations
from Effy.audio.types import AudioBuffer, AudioSpec
from Effy._internal.fp import pure
from Effy._internal.result import Ok, Err, Result
from Effy.error import EffyError
from typing import Protocol, Sequence


class AudioStream(Protocol):
    """Protocol for an effectful or pure audio stream that can pull audio buffers."""
    def pull(self, frames: int) -> AudioBuffer:
        """Pull the next buffer from the stream.
        
        Args:
            frames: Number of sample frames to pull.
            
        Returns:
            An AudioBuffer containing the audio data.
        """
        ...


@pure
def silence(spec: AudioSpec) -> AudioBuffer:
    """Return a zeroed, silent audio buffer of the given spec.
    
    Args:
        spec: The AudioSpec of the buffer.
        
    Returns:
        An AudioBuffer initialized to silence.
    """
    return AudioBuffer.create(spec)


@pure
def mix_buffers(a: AudioBuffer, b: AudioBuffer) -> Result[AudioBuffer, EffyError]:
    """Mix two audio buffers. Assumes they have the same specification.
    
    Args:
        a: First AudioBuffer.
        b: Second AudioBuffer.
        
    Returns:
        A Result wrapping a brand-new AudioBuffer containing the mixed signal, or an EffyError.
    """
    if a.spec != b.spec:
        return Err(EffyError(code=-1, message="Audio specifications must match"))
    
    spec = a.spec
    num_elements = spec.samples * spec.channels
    if num_elements == 0:
        return Ok(AudioBuffer.create(spec))
        
    from Effy.audio.types import AudioFormat
    import array
    
    typecode = 'h' if spec.format == AudioFormat.S16 else 'f'
    arr = array.array(typecode, [0 if typecode == 'h' else 0.0] * num_elements)
    
    a_arr = a._data_array
    b_arr = b._data_array
    
    if spec.format == AudioFormat.S16:
        # Mix and clamp to signed 16-bit range [-32767, 32767]
        for i in range(num_elements):
            arr[i] = max(-32767, min(32767, a_arr[i] + b_arr[i]))
    else:
        for i in range(num_elements):
            arr[i] = a_arr[i] + b_arr[i]
        
    return Ok(AudioBuffer(
        spec=spec,
        _data_array=arr,
        _is_transient=False
    ))


@pure
def mix_streams(streams: Sequence[AudioStream], frames: int, spec: AudioSpec) -> Result[AudioBuffer, EffyError]:
    """Mix multiple audio streams into a single buffer.
    
    Args:
        streams: A sequence of AudioStream instances to mix.
        frames: The number of frames to pull from each.
        spec: The AudioSpec for mixing.
        
    Returns:
        A Result wrapping a brand-new AudioBuffer containing the combined mixed streams, or an EffyError.
    """
    res: Result[AudioBuffer, EffyError] = Ok(silence(spec))
    for s in streams:
        buf = s.pull(frames)
        def mix_step(current: AudioBuffer) -> Result[AudioBuffer, EffyError]:
            """Inner helper function to mix the current accumulated buffer with the stream's buffer."""
            return mix_buffers(current, buf)
        res = res.and_then(mix_step)
    return res
