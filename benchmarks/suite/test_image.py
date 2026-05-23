import sys
import os
import struct
import zlib

def get_args():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "effy"

framework = get_args()

if framework == "pygame":
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    import pygame
    pygame.init()
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from Effy.video.image import load_bmp, load_png

from runner import BenchmarkRunner

def generate_test_bmp(path, w, h):
    row_size = ((w * 24 + 31) // 32) * 4
    pixel_data = b'\x00' * (row_size * h)
    with open(path, "wb") as f:
        f.write(b"BM")
        f.write(struct.pack("<I", 54 + len(pixel_data)))
        f.write(b"\x00\x00\x00\x00")
        f.write(struct.pack("<I", 54))
        f.write(struct.pack("<I", 40))
        f.write(struct.pack("<i", w))
        f.write(struct.pack("<i", h))
        f.write(struct.pack("<H", 1))
        f.write(struct.pack("<H", 24))
        f.write(struct.pack("<I", 0))
        f.write(struct.pack("<I", len(pixel_data)))
        f.write(struct.pack("<i", 2835))
        f.write(struct.pack("<i", 2835))
        f.write(struct.pack("<I", 0))
        f.write(struct.pack("<I", 0))
        f.write(pixel_data)

def generate_test_png(path, w, h):
    scanline = b'\x00' + (b'\xff' * (w * 3))
    raw_data = scanline * h
    idat = zlib.compress(raw_data)

    def write_chunk(f, ctype, data):
        f.write(struct.pack(">I", len(data)))
        f.write(ctype)
        f.write(data)
        f.write(struct.pack(">I", zlib.crc32(ctype + data) & 0xffffffff))

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
        write_chunk(f, b"IHDR", ihdr)
        write_chunk(f, b"IDAT", idat)
        write_chunk(f, b"IEND", b"")

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    
    bmp_path = os.path.join(os.path.dirname(__file__), "test_bench_tmp.bmp")
    png_path = os.path.join(os.path.dirname(__file__), "test_bench_tmp.png")
    
    # We generate the files once per runner instance, before tests start
    generate_test_bmp(bmp_path, 64, 64)
    generate_test_png(png_path, 64, 64)
    
    if framework == "pygame":
        def test_load_bmp():
            pygame.image.load(bmp_path)
            
        def test_load_png():
            pygame.image.load(png_path)
    else:
        def test_load_bmp():
            res = load_bmp(bmp_path).run()
            # _cow() returns data which is accessed, but we just verify it's OK
            if not res.__class__.__name__ == "Ok":
                raise RuntimeError("Failed to load BMP")
                
        def test_load_png():
            res = load_png(png_path).run()
            if not res.__class__.__name__ == "Ok":
                raise RuntimeError("Failed to load PNG")

    runner.register("Load BMP (64x64)", test_load_bmp, iterations=50)
    runner.register("Load PNG (64x64)", test_load_png, iterations=50)

    try:
        runner.dump_json()
    finally:
        if os.path.exists(bmp_path):
            os.remove(bmp_path)
        if os.path.exists(png_path):
            os.remove(png_path)

if __name__ == "__main__":
    main()
