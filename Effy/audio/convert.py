"""Pure functional audio conversion routines optimized via native arrays."""

from __future__ import annotations
import array
from Effy.audio.types import AudioBuffer, AudioSpec, AudioFormat
from Effy._internal.fp import pure


@pure
def convert_audio(buf: AudioBuffer, target_spec: AudioSpec) -> AudioBuffer:
    """Convert an AudioBuffer to a target AudioSpec (resampling, format, and channel conversion).

    This is a pure functional resampler and format/channel converter.

    Args:
        buf: The source AudioBuffer.
        target_spec: The target AudioSpec specification.

    Returns:
        A brand-new AudioBuffer in the target specification.
    """
    if buf.spec == target_spec:
        return buf

    # 1. Format and Channel Conversion at source rate
    # Extract raw data flat arrays to avoid per-element get_sample function overhead in pure Python
    src_spec = buf.spec
    src_channels = src_spec.channels
    data_arr = buf._data_array
    
    samples_flat: list[list[float]] = [] # list of channels, each is a list of floats
    if src_spec.format == AudioFormat.S16:
        for c in range(src_channels):
            sliced = data_arr[c::src_channels]
            channel_samples = [float(x) / 32767.0 for x in sliced]
            samples_flat.append(channel_samples)
    else:
        for c in range(src_channels):
            sliced = data_arr[c::src_channels]
            channel_samples = [float(x) for x in sliced]
            samples_flat.append(channel_samples)

    # 2. Channel Conversion
    dst_channels = target_spec.channels
    converted_channels: list[list[float]] = []
    
    if src_channels == dst_channels:
        converted_channels = samples_flat
    elif src_channels == 1 and dst_channels == 2:
        # Mono -> Stereo: Duplicate
        converted_channels = [samples_flat[0], list(samples_flat[0])]
    elif src_channels == 2 and dst_channels == 1:
        # Stereo -> Mono: Average
        mono_samples = []
        l_chan = samples_flat[0]
        r_chan = samples_flat[1]
        for l_val, r_val in zip(l_chan, r_chan):
            mono_samples.append((l_val + r_val) / 2.0)
        converted_channels = [mono_samples]
    else:
        # Generic fallback: duplicate first channel or pad with silence
        first_channel = samples_flat[0]
        converted_channels = [list(first_channel) for _ in range(dst_channels)]

    # 3. Resampling (Linear Interpolation)
    src_freq = src_spec.freq
    dst_freq = target_spec.freq
    dst_samples_count = target_spec.samples
    
    if src_freq == dst_freq:
        resampled_channels = converted_channels
    else:
        resampled_channels = []
        ratio = dst_freq / src_freq
        for c_samples in converted_channels:
            resampled = []
            len_c = len(c_samples)
            for i in range(dst_samples_count):
                src_idx = i / ratio
                floor_idx = int(src_idx)
                ceil_idx = floor_idx + 1
                if ceil_idx >= len_c:
                    ceil_idx = len_c - 1
                weight = src_idx - floor_idx
                if floor_idx >= len_c:
                    resampled.append(0.0)
                else:
                    val_floor = c_samples[floor_idx]
                    val_ceil = c_samples[ceil_idx]
                    val = (1.0 - weight) * val_floor + weight * val_ceil
                    resampled.append(val)
            resampled_channels.append(resampled)

    # 4. Pack into target buffer using native array.array bulk constructor
    total_samples = target_spec.samples * target_spec.channels
    
    if target_spec.format == AudioFormat.S16:
        arr_s16 = array.array('h', [0] * total_samples)
        for c in range(target_spec.channels):
            c_samples = resampled_channels[c]
            chan_arr_h = array.array('h', (int(max(-1.0, min(1.0, val)) * 32767) for val in c_samples))
            arr_s16[c::target_spec.channels] = chan_arr_h
        return AudioBuffer(spec=target_spec, _data_array=arr_s16, _is_transient=False)
    else:
        arr_f32 = array.array('f', [0.0] * total_samples)
        for c in range(target_spec.channels):
            c_samples = resampled_channels[c]
            chan_arr_f = array.array('f', c_samples)
            arr_f32[c::target_spec.channels] = chan_arr_f
        return AudioBuffer(spec=target_spec, _data_array=arr_f32, _is_transient=False)

