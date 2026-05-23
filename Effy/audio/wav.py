"""Pure-Python zero-dependency WAV audio decoder using the standard library wave module."""

from __future__ import annotations
import wave
import array
from Effy.types import Effect, Result, Ok, Err
from Effy.audio.types import AudioBuffer, AudioSpec, AudioFormat
from Effy.error import EffyError


def load_wav(file_path: str) -> Effect[Result[AudioBuffer, EffyError]]:
    """Load a PCM WAVE file (.wav) from a file path.

    Supports mono and stereo files in standard signed 16-bit PCM format,
    as well as 8-bit PCM (unsigned), 24-bit PCM (signed), or 32-bit float formats,
    which are automatically converted/adapted to the core AudioBuffer format.

    Args:
        file_path: Absolute or relative path to the WAV file.

    Returns:
        An Effect wrapping a Result that resolves to an AudioBuffer or an EffyError.
    """
    def _run() -> Result[AudioBuffer, EffyError]:
        """Load and parse the WAV file in a lazy thread-safe boundary context."""
        try:
            with wave.open(file_path, "rb") as w:
                nchannels = w.getnchannels()
                sampwidth = w.getsampwidth()
                framerate = w.getframerate()
                nframes = w.getnframes()

                if nchannels not in (1, 2):
                    return Err(
                        EffyError(
                            code=-1,
                            message=f"Unsupported WAV: Only mono (1) and stereo (2) channels are supported, got {nchannels}",
                        )
                    )

                raw_data = w.readframes(nframes)

                if sampwidth == 2:
                    # Native 16-bit signed PCM
                    spec = AudioSpec(
                        freq=framerate,
                        format=AudioFormat.S16,
                        channels=nchannels,
                        samples=nframes,
                    )
                    return Ok(AudioBuffer.from_bytes(spec, raw_data))

                elif sampwidth == 4:
                    # Native 32-bit float PCM
                    spec = AudioSpec(
                        freq=framerate,
                        format=AudioFormat.F32,
                        channels=nchannels,
                        samples=nframes,
                    )
                    return Ok(AudioBuffer.from_bytes(spec, raw_data))

                elif sampwidth == 1:
                    # 8-bit unsigned PCM (0 to 255) -> convert to S16
                    s16_data = array.array("h")
                    for val in raw_data:
                        # Map unsigned [0, 255] (centered at 128) to signed S16
                        s16_data.append((val - 128) * 256)
                    spec = AudioSpec(
                        freq=framerate,
                        format=AudioFormat.S16,
                        channels=nchannels,
                        samples=nframes,
                    )
                    return Ok(
                        AudioBuffer(
                            spec=spec, _data_array=s16_data, _is_transient=False
                        )
                    )

                elif sampwidth == 3:
                    # 24-bit signed PCM -> convert to S16 by decoding 3-byte groups
                    s16_data = array.array("h")
                    num_samples = len(raw_data) // 3
                    for i in range(num_samples):
                        offset = i * 3
                        b0 = raw_data[offset]
                        b1 = raw_data[offset + 1]
                        b2 = raw_data[offset + 2]

                        # Reconstruct signed 24-bit value
                        val = b0 | (b1 << 8) | (b2 << 16)
                        if val & 0x800000:
                            val -= 0x1000000

                        s16_data.append(val >> 8)

                    spec = AudioSpec(
                        freq=framerate,
                        format=AudioFormat.S16,
                        channels=nchannels,
                        samples=nframes,
                    )
                    return Ok(
                        AudioBuffer(
                            spec=spec, _data_array=s16_data, _is_transient=False
                        )
                    )

                else:
                    return Err(
                        EffyError(
                            code=-1,
                            message=f"Unsupported WAV sample width: {sampwidth} bytes",
                        )
                    )

        except wave.Error as e:
            return Err(
                EffyError(
                    code=-1, message=f"Invalid WAV file format: {str(e)}"
                )
            )
        except FileNotFoundError:
            return Err(
                EffyError(code=2, message=f"WAV file not found: {file_path}")
            )
        except Exception as e:
            return Err(
                EffyError(code=-1, message=f"Failed to load WAV: {str(e)}")
            )

    return Effect(_run)
