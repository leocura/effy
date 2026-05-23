import sys
import os
import math
import array

def get_args():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "effy"

framework = get_args()

# Match the exact spec definitions
class AudioSpecCopy:
    def __init__(self, freq: int, format_str: str, channels: int, samples: int):
        self.freq = freq
        self.format = format_str
        self.channels = channels
        self.samples = samples

# Implement exact matching audio spec conversion and mixing functions in pure Python/array for CPython/Pygame branch
def pure_python_convert_audio(src_arr: array.array, src_spec: AudioSpecCopy, target_spec: AudioSpecCopy) -> array.array:
    num_samples = src_spec.samples
    src_channels = src_spec.channels
    
    samples_flat = []
    if src_spec.format == "S16":
        for c in range(src_channels):
            channel_samples = [float(src_arr[f * src_channels + c]) / 32767.0 for f in range(num_samples)]
            samples_flat.append(channel_samples)
    else:
        for c in range(src_channels):
            channel_samples = [float(src_arr[f * src_channels + c]) for f in range(num_samples)]
            samples_flat.append(channel_samples)

    dst_channels = target_spec.channels
    converted_channels = []
    
    if src_channels == dst_channels:
        converted_channels = samples_flat
    elif src_channels == 1 and dst_channels == 2:
        converted_channels = [samples_flat[0], list(samples_flat[0])]
    elif src_channels == 2 and dst_channels == 1:
        mono_samples = []
        l_chan = samples_flat[0]
        r_chan = samples_flat[1]
        for l_val, r_val in zip(l_chan, r_chan):
            mono_samples.append((l_val + r_val) / 2.0)
        converted_channels = [mono_samples]
    else:
        first_channel = samples_flat[0]
        converted_channels = [list(first_channel) for _ in range(dst_channels)]

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
                if ceil_idx >= len_c: ceil_idx = len_c - 1
                weight = src_idx - floor_idx
                if floor_idx >= len_c:
                    resampled.append(0.0)
                else:
                    val_floor = c_samples[floor_idx]
                    val_ceil = c_samples[ceil_idx]
                    val = (1.0 - weight) * val_floor + weight * val_ceil
                    resampled.append(val)
            resampled_channels.append(resampled)

    typecode = 'h' if target_spec.format == "S16" else 'f'
    total_samples = target_spec.samples * target_spec.channels
    
    if target_spec.format == "S16":
        flat_list = [0] * total_samples
        for c in range(target_spec.channels):
            c_samples = resampled_channels[c]
            for f in range(target_spec.samples):
                val = c_samples[f]
                if val < -1.0: val = -1.0
                elif val > 1.0: val = 1.0
                flat_list[f * target_spec.channels + c] = int(val * 32767)
        arr = array.array('h', flat_list)
    else:
        flat_list = [0.0] * total_samples
        for c in range(target_spec.channels):
            c_samples = resampled_channels[c]
            for f in range(target_spec.samples):
                flat_list[f * target_spec.channels + c] = c_samples[f]
        arr = array.array('f', flat_list)
        
    return arr

def pure_python_mix_buffers(a_arr: array.array, b_arr: array.array, spec: AudioSpecCopy) -> array.array:
    num_elements = spec.samples * spec.channels
    typecode = 'h' if spec.format == "S16" else 'f'
    arr = array.array(typecode, [0 if typecode == 'h' else 0.0] * num_elements)
    
    if spec.format == "S16":
        for i in range(num_elements):
            arr[i] = max(-32767, min(32767, a_arr[i] + b_arr[i]))
    else:
        for i in range(num_elements):
            arr[i] = a_arr[i] + b_arr[i]
            
    return arr

if framework == "pygame":
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    import pygame
    pygame.init()
    
    spec_44_mono_s16 = AudioSpecCopy(freq=44100, format_str="S16", channels=1, samples=4096)
    spec_48_stereo_f32 = AudioSpecCopy(freq=48000, format_str="F32", channels=2, samples=4456)
    
    # Pre-generate waves to isolate timed converting / mixing functions
    sine_arr = array.array('h', [int(math.sin(2 * math.pi * 440 * f / 44100) * 32767) for f in range(4096)])
    
    mix_source_buffers = []
    for i in range(10):
        arr = array.array('f', [math.sin(2 * math.pi * (200 + i * 50) * f / 48000) * 0.1 for f in range(4456 * 2)])
        mix_source_buffers.append(arr)

    def test_audio_conversion():
        _ = pure_python_convert_audio(sine_arr, spec_44_mono_s16, spec_48_stereo_f32)

    def test_audio_mixing():
        mixed = mix_source_buffers[0]
        for b in mix_source_buffers[1:]:
            mixed = pure_python_mix_buffers(mixed, b, spec_48_stereo_f32)
        _ = mixed

else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from Effy.audio import AudioSpec, AudioBuffer, AudioFormat, mix_buffers, convert_audio
    
    spec_44_mono_s16 = AudioSpec(freq=44100, format=AudioFormat.S16, channels=1, samples=4096)
    spec_48_stereo_f32 = AudioSpec(freq=48000, format=AudioFormat.F32, channels=2, samples=4456)
    
    # Pre-generate waves
    sine_buffer = AudioBuffer.create(spec_44_mono_s16)
    for f in range(spec_44_mono_s16.samples):
        val = math.sin(2 * math.pi * 440 * f / spec_44_mono_s16.freq)
        sine_buffer = sine_buffer.write_sample(f, 0, val)

    mix_source_buffers = []
    for i in range(10):
        buf = AudioBuffer.create(spec_48_stereo_f32)
        for f in range(spec_48_stereo_f32.samples):
            val = math.sin(2 * math.pi * (200 + i * 50) * f / spec_48_stereo_f32.freq) * 0.1
            buf = buf.write_sample(f, 0, val)
            buf = buf.write_sample(f, 1, val)
        mix_source_buffers.append(buf)

    def test_audio_conversion():
        _ = convert_audio(sine_buffer, spec_48_stereo_f32)

    def test_audio_mixing():
        mixed = mix_source_buffers[0]
        for b in mix_source_buffers[1:]:
            mixed = mix_buffers(mixed, b).unwrap()
        _ = mixed._data_array

from runner import BenchmarkRunner

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    runner.register("Audio Spec Conversion", test_audio_conversion, iterations=30)
    runner.register("Audio Multi-Stream Mix", test_audio_mixing, iterations=20)
    runner.dump_json()

if __name__ == "__main__":
    main()
