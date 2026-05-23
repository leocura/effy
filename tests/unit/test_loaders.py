"""Unit tests verifying correct behavior, filtering, conversions, and error handling of asset loaders."""

from __future__ import annotations
import struct
import zlib
import tempfile
import os
import wave
import pytest
from Effy.types import Color
from Effy.video.image import load_bmp, load_png, load_image
from Effy.audio.wav import load_wav
from Effy.audio.types import AudioFormat


def make_bmp(
    width: int,
    height: int,
    bit_count: int,
    pixels: list[tuple[int, int, int]] | list[tuple[int, int, int, int]],
) -> bytes:
    """Synthesize a valid uncompressed BMP byte stream in memory.

    Args:
        width: Image width.
        height: Image height. Can be negative for top-down layout.
        bit_count: Bits per pixel (24 or 32).
        pixels: List of color tuples (R, G, B) or (R, G, B, A).

    Returns:
        The complete BMP file bytes.
    """
    bytes_per_pixel = bit_count // 8
    abs_h = abs(height)
    row_size = ((width * bit_count + 31) // 32) * 4
    pixel_data_size = row_size * abs_h
    bf_off_bits = 54
    bf_size = bf_off_bits + pixel_data_size

    file_header = struct.pack("<2sIHHI", b"BM", bf_size, 0, 0, bf_off_bits)
    dib_header = struct.pack(
        "<IiiHHIIiiII",
        40,
        width,
        height,
        1,
        bit_count,
        0,
        pixel_data_size,
        2835,
        2835,
        0,
        0,
    )

    body = bytearray()
    for y in range(abs_h):
        row = bytearray()
        for x in range(width):
            idx = y * width + x
            px = pixels[idx]
            if bit_count == 24:
                row.extend(struct.pack("BBB", px[2], px[1], px[0]))
            else:
                row.extend(struct.pack("BBBB", px[2], px[1], px[0], px[3]))
        row.extend(b"\x00" * (row_size - len(row)))
        body.extend(row)

    return file_header + dib_header + bytes(body)


def make_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    """Helper to synthesize a standard PNG chunk with CRC suffix.

    Args:
        chunk_type: 4-byte chunk signature (e.g. b"IHDR").
        payload: Chunk data.

    Returns:
        The chunk bytes.
    """
    length = len(payload)
    length_bytes = struct.pack(">I", length)
    crc = zlib.crc32(chunk_type + payload) & 0xFFFFFFFF
    crc_bytes = struct.pack(">I", crc)
    return length_bytes + chunk_type + payload + crc_bytes


def make_png(
    width: int,
    height: int,
    color_type: int,
    pixels: list[tuple[int, int, int]] | list[tuple[int, int, int, int]],
    filter_type: int = 0,
) -> bytes:
    """Synthesize a valid non-interlaced PNG byte stream in memory.

    Args:
        width: Image width.
        height: Image height.
        color_type: PNG color type (2 for RGB, 6 for RGBA).
        pixels: List of color tuples (R, G, B) or (R, G, B, A).
        filter_type: PNG scanline reconstruction filter type (0-4).

    Returns:
        The complete PNG file bytes.
    """
    bit_depth = 8
    bpp = 3 if color_type == 2 else 4

    ihdr_payload = struct.pack(
        ">IIBBBBB", width, height, bit_depth, color_type, 0, 0, 0
    )
    ihdr_chunk = make_chunk(b"IHDR", ihdr_payload)

    raw_idat = bytearray()
    for y in range(height):
        raw_idat.append(filter_type)
        row_bytes = bytearray()
        for x in range(width):
            idx = y * width + x
            px = pixels[idx]
            if color_type == 2:
                row_bytes.extend(struct.pack("BBB", px[0], px[1], px[2]))
            else:
                row_bytes.extend(struct.pack("BBBB", px[0], px[1], px[2], px[3]))

        # Apply inverse-filters for test synthesis
        filtered_row = bytearray(width * bpp)
        if filter_type == 0:
            filtered_row[:] = row_bytes
        elif filter_type == 1:
            for i in range(width * bpp):
                val = row_bytes[i]
                left = row_bytes[i - bpp] if i >= bpp else 0
                filtered_row[i] = (val - left) & 0xFF
        elif filter_type == 2:
            filtered_row[:] = row_bytes
        else:
            filtered_row[:] = row_bytes

        raw_idat.extend(filtered_row)

    compressed_idat = zlib.compress(bytes(raw_idat))
    idat_chunk = make_chunk(b"IDAT", compressed_idat)
    iend_chunk = make_chunk(b"IEND", b"")

    return b"\x89PNG\r\n\x1a\n" + ihdr_chunk + idat_chunk + iend_chunk


def write_temp_file(data: bytes, suffix: str) -> str:
    """Helper to write data to a temporary file and return its path.

    Args:
        data: Raw bytes to write.
        suffix: File extension/suffix.

    Returns:
        The absolute path to the temp file.
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    return path


def test_load_bmp_24bit() -> None:
    """Verify loading of a standard 24-bit uncompressed BMP image."""
    pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
    bmp_bytes = make_bmp(2, 2, 24, pixels)
    path = write_temp_file(bmp_bytes, ".bmp")
    try:
        res = load_bmp(path).run()
        assert res.is_ok() is True
        buf = res.unwrap()
        assert buf.width == 2
        assert buf.height == 2
        # Bottom-up mapping: row 0 in file is row 1 in PixelBuffer
        # row 0 in file is [(255, 0, 0), (0, 255, 0)] -> maps to y=1
        # row 1 in file is [(0, 0, 255), (255, 255, 255)] -> maps to y=0
        assert buf.get_pixel(0, 1) == Color(255, 0, 0, 255)
        assert buf.get_pixel(1, 1) == Color(0, 255, 0, 255)
        assert buf.get_pixel(0, 0) == Color(0, 0, 255, 255)
        assert buf.get_pixel(1, 0) == Color(255, 255, 255, 255)
    finally:
        os.remove(path)


def test_load_bmp_32bit() -> None:
    """Verify loading of a 32-bit uncompressed BMP image with alpha transparency."""
    pixels = [
        (255, 0, 0, 128),
        (0, 255, 0, 64),
        (0, 0, 255, 255),
        (255, 255, 255, 0),
    ]
    bmp_bytes = make_bmp(2, 2, 32, pixels)
    path = write_temp_file(bmp_bytes, ".bmp")
    try:
        res = load_bmp(path).run()
        assert res.is_ok() is True
        buf = res.unwrap()
        assert buf.width == 2
        assert buf.height == 2
        # Bottom-up mapping: row 0 in file is row 1 in PixelBuffer
        assert buf.get_pixel(0, 1) == Color(255, 0, 0, 128)
        assert buf.get_pixel(1, 1) == Color(0, 255, 0, 64)
        assert buf.get_pixel(0, 0) == Color(0, 0, 255, 255)
        assert buf.get_pixel(1, 0) == Color(255, 255, 255, 0)
    finally:
        os.remove(path)


def test_load_bmp_top_down() -> None:
    """Verify loading of a top-down BMP image (negative height DIB parameter)."""
    pixels = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)]
    bmp_bytes = make_bmp(2, -2, 24, pixels)
    path = write_temp_file(bmp_bytes, ".bmp")
    try:
        res = load_bmp(path).run()
        assert res.is_ok() is True
        buf = res.unwrap()
        assert buf.get_pixel(0, 0) == Color(1, 2, 3, 255)
        assert buf.get_pixel(1, 0) == Color(4, 5, 6, 255)
    finally:
        os.remove(path)


def test_load_png_24bit() -> None:
    """Verify loading of a standard 24-bit RGB PNG file."""
    pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (10, 20, 30)]
    png_bytes = make_png(2, 2, 2, pixels)
    path = write_temp_file(png_bytes, ".png")
    try:
        res = load_png(path).run()
        assert res.is_ok() is True
        buf = res.unwrap()
        assert buf.width == 2
        assert buf.height == 2
        assert buf.get_pixel(0, 0) == Color(255, 0, 0, 255)
        assert buf.get_pixel(1, 1) == Color(10, 20, 30, 255)
    finally:
        os.remove(path)


def test_load_png_32bit() -> None:
    """Verify loading of a 32-bit RGBA PNG file with custom alpha transparency."""
    pixels = [
        (255, 0, 0, 100),
        (0, 255, 0, 200),
        (0, 0, 255, 50),
        (10, 20, 30, 0),
    ]
    png_bytes = make_png(2, 2, 6, pixels)
    path = write_temp_file(png_bytes, ".png")
    try:
        res = load_png(path).run()
        assert res.is_ok() is True
        buf = res.unwrap()
        assert buf.get_pixel(0, 0) == Color(255, 0, 0, 100)
        assert buf.get_pixel(1, 1) == Color(10, 20, 30, 0)
    finally:
        os.remove(path)


def test_load_png_filter_sub() -> None:
    """Verify standard PNG Sub filter reconstruction correctness."""
    pixels = [(10, 20, 30), (40, 50, 60), (70, 80, 90), (100, 110, 120)]
    png_bytes = make_png(2, 2, 2, pixels, filter_type=1)
    path = write_temp_file(png_bytes, ".png")
    try:
        res = load_png(path).run()
        assert res.is_ok() is True
        buf = res.unwrap()
        assert buf.get_pixel(0, 0) == Color(10, 20, 30, 255)
        assert buf.get_pixel(1, 0) == Color(40, 50, 60, 255)
    finally:
        os.remove(path)


def test_load_image_auto_detect() -> None:
    """Verify unified load_image routes to correct loaders via signatures."""
    bmp_pixels = [(255, 0, 0), (0, 255, 0)]
    png_pixels = [(0, 0, 255), (255, 255, 255)]

    bmp_bytes = make_bmp(2, 1, 24, bmp_pixels)
    png_bytes = make_png(2, 1, 2, png_pixels)

    bmp_path = write_temp_file(bmp_bytes, ".bmp")
    png_path = write_temp_file(png_bytes, ".png")

    try:
        # Load BMP via unified loader
        res1 = load_image(bmp_path).run()
        assert res1.is_ok() is True
        # Bottom-up: y=0 maps to the single row (since height=1)
        assert res1.unwrap().get_pixel(0, 0) == Color(255, 0, 0, 255)

        # Load PNG via unified loader
        res2 = load_image(png_path).run()
        assert res2.is_ok() is True
        assert res2.unwrap().get_pixel(0, 0) == Color(0, 0, 255, 255)
    finally:
        os.remove(bmp_path)
        os.remove(png_path)


def test_load_wav_formats() -> None:
    """Verify loading and adaptation of WAV audio PCM files across channels and sample widths."""
    # Test 16-bit stereo PCM
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(44100)
            # 10 sample frames * 2 channels = 20 samples
            samples = [i * 1000 for i in range(20)]
            w.writeframes(struct.pack("<20h", *samples))

        res = load_wav(path).run()
        assert res.is_ok() is True
        buf = res.unwrap()
        assert buf.spec.freq == 44100
        assert buf.spec.channels == 2
        assert buf.spec.format == AudioFormat.S16
        assert buf.spec.samples == 10
        assert buf.get_sample(0, 0) == pytest.approx(0.0)
        assert buf.get_sample(0, 1) == pytest.approx(1000.0 / 32767.0, abs=1e-4)
    finally:
        os.remove(path)

    # Test 8-bit mono PCM (unsigned 0-255)
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(1)
            w.setframerate(22050)
            # Unsigned samples (128 is silence/0.0, 0 is negative max, 255 is positive max)
            samples_8 = [128, 0, 255, 64]
            w.writeframes(bytes(samples_8))

        res = load_wav(path).run()
        assert res.is_ok() is True
        buf = res.unwrap()
        assert buf.spec.freq == 22050
        assert buf.spec.channels == 1
        assert buf.spec.format == AudioFormat.S16
        assert buf.spec.samples == 4
        # 128 maps to 0.0
        assert buf.get_sample(0, 0) == pytest.approx(0.0, abs=1e-2)
        # 0 maps to -128 * 256 = -32768, which is -1.0 in S16 format
        assert buf.get_sample(1, 0) == pytest.approx(-1.0, abs=1e-2)
    finally:
        os.remove(path)


def test_loader_errors() -> None:
    """Verify correct error propagation and code containment for missing or corrupt files."""
    # Non-existent files
    res = load_image("nonexistent_file.png").run()
    assert res.is_err() is True
    assert res.error.code == 2

    res_wav = load_wav("nonexistent_file.wav").run()
    assert res_wav.is_err() is True
    assert res_wav.error.code == 2

    # Corrupt data signatures
    fd, path = tempfile.mkstemp(suffix=".png")
    with os.fdopen(fd, "wb") as f:
        f.write(b"not a png signature")
    try:
        res = load_image(path).run()
        assert res.is_err() is True
    finally:
        os.remove(path)
