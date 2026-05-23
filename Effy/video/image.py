"""Pure-Python zero-dependency image decoders for BMP and PNG formats."""

from __future__ import annotations
import struct
import zlib
from Effy.types import Effect, Result, Ok, Err
from Effy.video.surface import PixelBuffer
from Effy.error import EffyError


def load_bmp(file_path: str) -> Effect[Result[PixelBuffer, EffyError]]:
    """Load an uncompressed 24-bit or 32-bit BMP image from a file path.

    Args:
        file_path: Absolute or relative path to the BMP file.

    Returns:
        An Effect wrapping a Result that resolves to a PixelBuffer or an EffyError.
    """
    def _run() -> Result[PixelBuffer, EffyError]:
        """Load and parse the BMP file in a lazy thread-safe boundary context."""
        try:
            with open(file_path, "rb") as f:
                header = f.read(54)
                if len(header) < 54:
                    return Err(EffyError(code=-1, message="Invalid BMP: File too short"))

                if header[:2] != b"BM":
                    return Err(EffyError(code=-1, message="Invalid BMP: Missing BM signature"))

                bf_off_bits = struct.unpack_from("<I", header, 10)[0]
                bi_size = struct.unpack_from("<I", header, 14)[0]
                if bi_size < 40:
                    return Err(EffyError(code=-1, message="Invalid BMP: Unsupported DIB header size"))

                bi_width = struct.unpack_from("<i", header, 18)[0]
                bi_height = struct.unpack_from("<i", header, 22)[0]
                bi_planes = struct.unpack_from("<H", header, 26)[0]
                bi_bit_count = struct.unpack_from("<H", header, 28)[0]
                bi_compression = struct.unpack_from("<I", header, 30)[0]

                if bi_planes != 1:
                    return Err(EffyError(code=-1, message="Invalid BMP: Planes must be 1"))

                if bi_bit_count not in (24, 32):
                    return Err(EffyError(code=-1, message="Invalid BMP: Only 24-bit and 32-bit BMPs are supported"))

                if bi_compression != 0:
                    return Err(EffyError(code=-1, message="Invalid BMP: Only uncompressed BI_RGB is supported"))

                width = bi_width
                height = abs(bi_height)
                is_bottom_up = bi_height > 0

                f.seek(bf_off_bits)

                bytes_per_pixel = bi_bit_count // 8
                row_size = ((width * bi_bit_count + 31) // 32) * 4

                pixel_data = f.read(row_size * height)
                if len(pixel_data) < row_size * height:
                    return Err(EffyError(code=-1, message="Invalid BMP: Incomplete pixel data"))

                buf = PixelBuffer.create(width, height)
                data, transient = buf._cow()

                for y in range(height):
                    dest_y = (height - 1 - y) if is_bottom_up else y
                    row_offset = y * row_size
                    dest_row_offset = dest_y * width

                    if bytes_per_pixel == 3:
                        for x in range(width):
                            px_off = row_offset + x * 3
                            b = pixel_data[px_off]
                            g = pixel_data[px_off + 1]
                            r = pixel_data[px_off + 2]
                            a = 255
                            data[dest_row_offset + x] = r | (g << 8) | (b << 16) | (a << 24)
                    elif bytes_per_pixel == 4:
                        for x in range(width):
                            px_off = row_offset + x * 4
                            b = pixel_data[px_off]
                            g = pixel_data[px_off + 1]
                            r = pixel_data[px_off + 2]
                            a = pixel_data[px_off + 3]
                            data[dest_row_offset + x] = r | (g << 8) | (b << 16) | (a << 24)

                return Ok(PixelBuffer(
                    width=width,
                    height=height,
                    pitch=width,
                    _data_cache=[data],
                    _commands_list=[],
                    _is_transient=transient
                ))

        except FileNotFoundError:
            return Err(EffyError(code=2, message=f"BMP file not found: {file_path}"))
        except Exception as e:
            return Err(EffyError(code=-1, message=f"Failed to load BMP: {str(e)}"))

    return Effect(_run)


def load_png(file_path: str) -> Effect[Result[PixelBuffer, EffyError]]:
    """Load a non-interlaced 24-bit RGB or 32-bit RGBA PNG image from a file path.

    Args:
        file_path: Absolute or relative path to the PNG file.

    Returns:
        An Effect wrapping a Result that resolves to a PixelBuffer or an EffyError.
    """
    def _run() -> Result[PixelBuffer, EffyError]:
        """Decompress and parse PNG data blocks using standard library zlib."""
        try:
            with open(file_path, "rb") as f:
                sig = f.read(8)
                if sig != b"\x89PNG\r\n\x1a\n":
                    return Err(EffyError(code=-1, message="Invalid PNG: Missing PNG signature"))

                chunks = []
                while True:
                    length_bytes = f.read(4)
                    if len(length_bytes) < 4:
                        break
                    length = struct.unpack(">I", length_bytes)[0]
                    chunk_type = f.read(4)
                    chunk_data = f.read(length)
                    _ = f.read(4)  # Read CRC, ignore for performance

                    chunks.append((chunk_type, chunk_data))
                    if chunk_type == b"IEND":
                        break

                ihdr_data = None
                for c_type, c_data in chunks:
                    if c_type == b"IHDR":
                        ihdr_data = c_data
                        break

                if not ihdr_data:
                    return Err(EffyError(code=-1, message="Invalid PNG: Missing IHDR chunk"))

                width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                    ">IIBBBBB", ihdr_data
                )

                if compression != 0:
                    return Err(EffyError(code=-1, message="Unsupported PNG: Compression method must be 0"))
                if filter_method != 0:
                    return Err(EffyError(code=-1, message="Unsupported PNG: Filter method must be 0"))
                if interlace != 0:
                    return Err(EffyError(code=-1, message="Unsupported PNG: Interlaced PNGs are not supported"))

                if bit_depth != 8:
                    return Err(EffyError(code=-1, message=f"Unsupported PNG: Only 8-bit depth is supported, got {bit_depth}"))

                if color_type == 2:
                    bpp = 3
                elif color_type == 6:
                    bpp = 4
                else:
                    return Err(EffyError(code=-1, message=f"Unsupported PNG: Only RGB and RGBA color types are supported, got {color_type}"))

                idat_data = b"".join(c_data for c_type, c_data in chunks if c_type == b"IDAT")

                try:
                    decompressed = zlib.decompress(idat_data)
                except Exception as e:
                    return Err(EffyError(code=-1, message=f"PNG decompression failed: {str(e)}"))

                scanline_size = 1 + width * bpp
                expected_size = scanline_size * height

                if len(decompressed) < expected_size:
                    return Err(EffyError(code=-1, message="Invalid PNG: Incomplete decompressed data"))

                buf = PixelBuffer.create(width, height)
                data, transient = buf._cow()

                recon = bytearray(width * bpp)
                prev_recon = bytearray(width * bpp)

                def paeth_predictor(a: int, b: int, c: int) -> int:
                    """Compute Paeth's standard PNG predictor value."""
                    p = a + b - c
                    pa = abs(p - a)
                    pb = abs(p - b)
                    pc = abs(p - c)
                    if pa <= pb and pa <= pc:
                        return a
                    elif pb <= pc:
                        return b
                    else:
                        return c

                for y in range(height):
                    row_start = y * scanline_size
                    filter_type = decompressed[row_start]
                    scanline_data = decompressed[row_start + 1 : row_start + scanline_size]

                    if filter_type == 0:
                        for i in range(width * bpp):
                            recon[i] = scanline_data[i]
                    elif filter_type == 1:
                        for i in range(width * bpp):
                            val = scanline_data[i]
                            left = recon[i - bpp] if i >= bpp else 0
                            recon[i] = (val + left) & 0xFF
                    elif filter_type == 2:
                        for i in range(width * bpp):
                            val = scanline_data[i]
                            up = prev_recon[i]
                            recon[i] = (val + up) & 0xFF
                    elif filter_type == 3:
                        for i in range(width * bpp):
                            val = scanline_data[i]
                            left = recon[i - bpp] if i >= bpp else 0
                            up = prev_recon[i]
                            recon[i] = (val + (left + up) // 2) & 0xFF
                    elif filter_type == 4:
                        for i in range(width * bpp):
                            val = scanline_data[i]
                            left = recon[i - bpp] if i >= bpp else 0
                            up = prev_recon[i]
                            left_up = prev_recon[i - bpp] if i >= bpp else 0
                            recon[i] = (val + paeth_predictor(left, up, left_up)) & 0xFF
                    else:
                        return Err(EffyError(code=-1, message=f"Invalid PNG: Unknown filter type {filter_type}"))

                    prev_recon[:] = recon

                    dest_row_offset = y * width
                    if bpp == 3:
                        for x in range(width):
                            r = recon[x * 3]
                            g = recon[x * 3 + 1]
                            b = recon[x * 3 + 2]
                            a = 255
                            data[dest_row_offset + x] = r | (g << 8) | (b << 16) | (a << 24)
                    else:
                        for x in range(width):
                            r = recon[x * 4]
                            g = recon[x * 4 + 1]
                            b = recon[x * 4 + 2]
                            a = recon[x * 4 + 3]
                            data[dest_row_offset + x] = r | (g << 8) | (b << 16) | (a << 24)

                return Ok(PixelBuffer(
                    width=width,
                    height=height,
                    pitch=width,
                    _data_cache=[data],
                    _commands_list=[],
                    _is_transient=transient
                ))

        except FileNotFoundError:
            return Err(EffyError(code=2, message=f"PNG file not found: {file_path}"))
        except Exception as e:
            return Err(EffyError(code=-1, message=f"Failed to load PNG: {str(e)}"))

    return Effect(_run)


def load_image(file_path: str) -> Effect[Result[PixelBuffer, EffyError]]:
    """Unified image loader that auto-detects format via magic byte signatures.

    Supports uncompressed 24-bit/32-bit BMP files and non-interlaced 24-bit/32-bit PNG files.

    Args:
        file_path: Absolute or relative path to the image file.

    Returns:
        An Effect wrapping a Result that resolves to a PixelBuffer or an EffyError.
    """
    def _run() -> Result[PixelBuffer, EffyError]:
        """Read signature bytes and route request to load_bmp or load_png."""
        try:
            with open(file_path, "rb") as f:
                sig = f.read(8)
            
            if sig[:2] == b"BM":
                return load_bmp(file_path).run()
            elif sig == b"\x89PNG\r\n\x1a\n":
                return load_png(file_path).run()
            elif sig[:3] == b"\xFF\xD8\xFF" or sig[:4] == b"RIFF" or sig[:6] in (b"GIF87a", b"GIF89a"):
                from Effy.video.image_ext import load_extended_image
                return load_extended_image(file_path)
            else:
                return Err(EffyError(code=-1, message="Unsupported image format: Signature not recognized"))
        except FileNotFoundError:
            return Err(EffyError(code=2, message=f"Image file not found: {file_path}"))
        except Exception as e:
            return Err(EffyError(code=-1, message=f"Failed to load image: {str(e)}"))

    return Effect(_run)
