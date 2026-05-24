import sys
import os
import array

def get_args():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "effy"

framework = get_args()

SAMPLES = 4096

if framework == "pygame":
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    import pygame
    pygame.init()
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from Effy.init import init, quit, InitFlag
    from Effy.audio.stream import mix_buffers
    from Effy.audio.types import AudioSpec, AudioFormat, AudioBuffer

from runner import BenchmarkRunner

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    
    if framework == "pygame":
        def setup():
            # Pygame doesn't expose a synchronous software mixer API like Effy.
            # We simulate the workload of mixing 2 stereo S16 buffers using a python array.
            buf_a = array.array('h', [1000] * (SAMPLES * 2))
            buf_b = array.array('h', [500] * (SAMPLES * 2))
            buf_out = array.array('h', [0] * (SAMPLES * 2))
            return {"a": buf_a, "b": buf_b, "out": buf_out}
            
        def run(context):
            # Pure python fallback simulating audio mixing
            a = context["a"]
            b = context["b"]
            out = context["out"]
            # To avoid clamp logic overhead in python, just add
            for i in range(len(a)):
                val = a[i] + b[i]
                if val > 32767: val = 32767
                elif val < -32768: val = -32768
                out[i] = val
                
        def teardown(context):
            pass
            
    else:
        def setup():
            init(InitFlag.AUDIO).run()
            spec = AudioSpec(freq=44100, format=AudioFormat.S16, channels=2, samples=SAMPLES)
            buf_a = AudioBuffer.create(spec)
            buf_b = AudioBuffer.create(spec)
            # Fill with dummy data
            for i in range(len(buf_a._data)):
                buf_a._data[i] = 100
                buf_b._data[i] = 50
            return {"a": buf_a, "b": buf_b}
            
        def run(context):
            a = context["a"]
            b = context["b"]
            # Effy's functional audio mixer
            mix_res = mix_buffers(a, b).run().value if hasattr(mix_buffers(a, b), 'run') else mix_buffers(a, b)
            
        def teardown(context):
            pass

    runner.register("Audio Mix (4096 Samples)", run, setup_func=setup, teardown_func=teardown, iterations=1000, warmup=100)
    runner.dump_json()

if __name__ == "__main__":
    main()
