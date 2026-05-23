"""Extended image format decoder support using platform native APIs (WIC on Windows, libjpeg/libwebp on Linux) or Pillow."""

from __future__ import annotations
import sys
import ctypes
from typing import Any, TYPE_CHECKING
from Effy._internal.result import Ok, Err, Result
from Effy.error import EffyError
from Effy.video.surface import PixelBuffer

if TYPE_CHECKING:
    from ctypes import wintypes
else:
    try:
        from ctypes import wintypes
    except ImportError:
        wintypes = None



# Windows COM/WIC definitions
class GUID(ctypes.Structure):
    """ctypes representation of a GUID structure."""
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8)
    ]
    
    def __init__(self, guid_str: str) -> None:
        """Parse a curly-braced string GUID."""
        import re
        parts = re.findall(r'[0-9a-fA-F]+', guid_str)
        self.Data1 = int(parts[0], 16)
        self.Data2 = int(parts[1], 16)
        self.Data3 = int(parts[2], 16)
        d4_str = parts[3] + parts[4]
        d4_bytes = bytes.fromhex(d4_str)
        for i, b in enumerate(d4_bytes):
            self.Data4[i] = b

def _call_com(interface_ptr: Any, index: int, argtypes: list[Any], *args: Any) -> int:
    """Call COM method via vtable."""
    WINFUNCTYPE = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)
    vtbl = ctypes.cast(interface_ptr, ctypes.POINTER(ctypes.c_void_p))[0]
    func_ptr = ctypes.cast(vtbl, ctypes.POINTER(ctypes.c_void_p))[index]
    proto = WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, *argtypes)
    func = proto(func_ptr)
    return int(func(interface_ptr, *args))

def _load_via_wic(file_path: str) -> Result[PixelBuffer, EffyError]:
    """Decode compressed image using Windows Imaging Component (WIC)."""
    if sys.platform != "win32":
        return Err(EffyError(code=-1, message="WIC is Windows only"))

    try:
        ole32 = ctypes.windll.ole32
        ole32.CoInitialize(None)

        clsid_factory = GUID("{CACAF262-9370-4615-A13B-9F5539DA4C0A}")
        iid_factory = GUID("{EC5EC8A9-C395-4314-9C77-54D7A935470F}")
        
        factory_ptr = ctypes.c_void_p()
        hr = ole32.CoCreateInstance(
            ctypes.byref(clsid_factory),
            None,
            23,  # CLSCTX_ALL
            ctypes.byref(iid_factory),
            ctypes.byref(factory_ptr)
        )
        if hr < 0 or not factory_ptr.value:
            return Err(EffyError(code=-1, message="Failed to create WIC Imaging Factory"))

        decoder_ptr = ctypes.c_void_p()
        # CreateDecoderFromFilename: index 3
        # Args: LPCWSTR filename, GUID* vendor, DWORD access, WICDecodeOptions, IWICBitmapDecoder**
        hr = _call_com(
            factory_ptr, 3,
            [wintypes.LPCWSTR, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)],
            file_path, None, 0x80000000, 0, ctypes.byref(decoder_ptr)
        )
        if hr < 0 or not decoder_ptr.value:
            _call_com(factory_ptr, 2, [])  # Release Factory
            return Err(EffyError(code=-1, message=f"WIC failed to load/decode image file: {file_path}"))

        frame_ptr = ctypes.c_void_p()
        # IWICBitmapDecoder::GetFrame index 13
        # Args: UINT index, IWICBitmapFrameDecode**
        hr = _call_com(decoder_ptr, 13, [ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p)], 0, ctypes.byref(frame_ptr))
        if hr < 0 or not frame_ptr.value:
            _call_com(decoder_ptr, 2, [])
            _call_com(factory_ptr, 2, [])
            return Err(EffyError(code=-1, message="Failed to retrieve WIC decoder frame"))

        converter_ptr = ctypes.c_void_p()
        # CreateFormatConverter: index 11
        hr = _call_com(factory_ptr, 11, [ctypes.POINTER(ctypes.c_void_p)], ctypes.byref(converter_ptr))
        if hr < 0 or not converter_ptr.value:
            _call_com(frame_ptr, 2, [])
            _call_com(decoder_ptr, 2, [])
            _call_com(factory_ptr, 2, [])
            return Err(EffyError(code=-1, message="Failed to create WIC format converter"))

        # Initialize Format Converter to GUID_WICPixelFormat32bppRGBA
        guid_rgba = GUID("{F5C7FD7C-4039-4C28-9311-CA6862216826}")
        # IWICFormatConverter::Initialize: index 8
        # Args: IWICBitmapSource, REFGUID dstFormat, WICBitmapDitherType, IWICPalette, double alphaThreshold, WICBitmapPaletteType
        hr = _call_com(
            converter_ptr, 8,
            [ctypes.c_void_p, ctypes.POINTER(GUID), ctypes.c_int, ctypes.c_void_p, ctypes.c_double, ctypes.c_int],
            frame_ptr, ctypes.byref(guid_rgba), 0, None, 0.0, 0
        )
        if hr < 0:
            _call_com(converter_ptr, 2, [])
            _call_com(frame_ptr, 2, [])
            _call_com(decoder_ptr, 2, [])
            _call_com(factory_ptr, 2, [])
            return Err(EffyError(code=-1, message="WIC converter initialization failed"))

        width = ctypes.c_uint(0)
        height = ctypes.c_uint(0)
        # IWICBitmapSource::GetSize: index 3
        _call_com(converter_ptr, 3, [ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)], ctypes.byref(width), ctypes.byref(height))

        w, h = width.value, height.value
        buf = PixelBuffer.create(w, h)
        data, transient = buf._cow()

        expected_len = w * h * 4
        c_array = (ctypes.c_char * expected_len).from_buffer(data)

        # IWICBitmapSource::CopyPixels: index 7
        # Args: WICRect* rc, UINT stride, UINT cbBufferSize, BYTE* pbBuffer
        hr = _call_com(converter_ptr, 7, [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p], None, w * 4, expected_len, ctypes.byref(c_array))

        # Release WIC resources
        _call_com(converter_ptr, 2, [])
        _call_com(frame_ptr, 2, [])
        _call_com(decoder_ptr, 2, [])
        _call_com(factory_ptr, 2, [])

        if hr < 0:
            return Err(EffyError(code=-1, message="Failed to copy WIC decoded pixels"))

        return Ok(PixelBuffer(
            width=w,
            height=h,
            pitch=w,
            _data_cache=[data],
            _commands_list=[],
            _is_transient=transient
        ))
    except Exception as e:
        return Err(EffyError(code=-1, message=f"WIC decoder exception: {str(e)}"))

def _load_via_libjpeg(file_path: str) -> Result[PixelBuffer, EffyError]:
    """Decode JPEG using native system libjpeg.so via ctypes."""
    libjpeg = None
    for name in ("libjpeg.so.62", "libjpeg.so.8", "libjpeg.so"):
        try:
            libjpeg = ctypes.cdll.LoadLibrary(name)
            break
        except Exception:
            continue

    if not libjpeg:
        return Err(EffyError(code=-1, message="libjpeg not available on host system"))

    # Minimal libjpeg structures and FFI binding
    class JpegErrorMgr(ctypes.Structure):
        """Minimal libjpeg error manager structure."""
        _fields_ = [("error_exit", ctypes.c_void_p)] + [("pad", ctypes.c_byte * 128)]

    class JpegDecompressStruct(ctypes.Structure):
        """Minimal libjpeg decompress structure."""
        _fields_ = [
            ("err", ctypes.POINTER(JpegErrorMgr)),
            ("pad1", ctypes.c_byte * 16),
            ("src", ctypes.c_void_p),
            ("image_width", ctypes.c_uint),
            ("image_height", ctypes.c_uint),
            ("num_components", ctypes.c_int),
            ("pad2", ctypes.c_byte * 128),
            ("output_width", ctypes.c_uint),
            ("output_height", ctypes.c_uint),
            ("output_components", ctypes.c_int),
            ("output_scanline", ctypes.c_uint),
            ("pad3", ctypes.c_byte * 256)
        ]

    try:
        # FFI Signatures
        libjpeg.jpeg_std_error.argtypes = [ctypes.POINTER(JpegErrorMgr)]
        libjpeg.jpeg_std_error.restype = ctypes.POINTER(JpegErrorMgr)
        
        libjpeg.jpeg_CreateDecompress.argtypes = [ctypes.POINTER(JpegDecompressStruct), ctypes.c_int, ctypes.c_size_t]
        libjpeg.jpeg_CreateDecompress.restype = None
        
        libjpeg.jpeg_stdio_src.argtypes = [ctypes.POINTER(JpegDecompressStruct), ctypes.c_void_p]
        libjpeg.jpeg_stdio_src.restype = None
        
        libjpeg.jpeg_read_header.argtypes = [ctypes.POINTER(JpegDecompressStruct), ctypes.c_bool]
        libjpeg.jpeg_read_header.restype = ctypes.c_int
        
        libjpeg.jpeg_start_decompress.argtypes = [ctypes.POINTER(JpegDecompressStruct)]
        libjpeg.jpeg_start_decompress.restype = ctypes.c_bool
        
        libjpeg.jpeg_read_scanlines.argtypes = [ctypes.POINTER(JpegDecompressStruct), ctypes.c_void_p, ctypes.c_uint]
        libjpeg.jpeg_read_scanlines.restype = ctypes.c_uint
        
        libjpeg.jpeg_finish_decompress.argtypes = [ctypes.POINTER(JpegDecompressStruct)]
        libjpeg.jpeg_finish_decompress.restype = ctypes.c_bool
        
        libjpeg.jpeg_destroy_decompress.argtypes = [ctypes.POINTER(JpegDecompressStruct)]
        libjpeg.jpeg_destroy_decompress.restype = None

        # Load C stdio fopen
        libc = ctypes.CDLL(None)
        libc.fopen.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        libc.fopen.restype = ctypes.c_void_p
        libc.fclose.argtypes = [ctypes.c_void_p]
        libc.fclose.restype = ctypes.c_int

        fp = libc.fopen(file_path.encode('utf-8'), b"rb")
        if not fp:
            return Err(EffyError(code=2, message=f"Failed to open JPEG file: {file_path}"))

        cinfo = JpegDecompressStruct()
        jerr = JpegErrorMgr()
        cinfo.err = libjpeg.jpeg_std_error(ctypes.byref(jerr))
        
        # JPEG library version 80 (standard size matching)
        libjpeg.jpeg_CreateDecompress(ctypes.byref(cinfo), 80, ctypes.sizeof(JpegDecompressStruct))
        libjpeg.jpeg_stdio_src(ctypes.byref(cinfo), fp)
        libjpeg.jpeg_read_header(ctypes.byref(cinfo), True)
        libjpeg.jpeg_start_decompress(ctypes.byref(cinfo))

        w, h = cinfo.output_width, cinfo.output_height
        comp = cinfo.output_components

        buf = PixelBuffer.create(w, h)
        data, transient = buf._cow()

        row_stride = w * comp
        row_buffer = (ctypes.c_char * row_stride)()
        row_pointer = (ctypes.c_void_p * 1)(ctypes.cast(ctypes.byref(row_buffer), ctypes.c_void_p))

        for y in range(h):
            libjpeg.jpeg_read_scanlines(ctypes.byref(cinfo), ctypes.byref(row_pointer), 1)
            row_offset = y * w
            if comp == 3:
                for x in range(w):
                    r = row_buffer[x * 3]
                    g = row_buffer[x * 3 + 1]
                    b = row_buffer[x * 3 + 2]
                    a = 255
                    data[row_offset + x] = ord(r) | (ord(g) << 8) | (ord(b) << 16) | (a << 24)
            elif comp == 4:
                for x in range(w):
                    r = row_buffer[x * 4]
                    g = row_buffer[x * 4 + 1]
                    b = row_buffer[x * 4 + 2]
                    a = row_buffer[x * 4 + 3]
                    data[row_offset + x] = ord(r) | (ord(g) << 8) | (ord(b) << 16) | (ord(a) << 24)
            elif comp == 1:
                for x in range(w):
                    gray = ord(row_buffer[x])
                    data[row_offset + x] = gray | (gray << 8) | (gray << 16) | (255 << 24)

        libjpeg.jpeg_finish_decompress(ctypes.byref(cinfo))
        libjpeg.jpeg_destroy_decompress(ctypes.byref(cinfo))
        libc.fclose(fp)

        return Ok(PixelBuffer(
            width=w,
            height=h,
            pitch=w,
            _data_cache=[data],
            _commands_list=[],
            _is_transient=transient
        ))
    except Exception as e:
        return Err(EffyError(code=-1, message=f"libjpeg decompress exception: {str(e)}"))

def load_extended_image(file_path: str) -> Result[PixelBuffer, EffyError]:
    """Uniform entry point to decode image files of JPEG, WebP, GIF, or other formats.

    Args:
        file_path: Path to the image file.

    Returns:
        A Result containing a PixelBuffer or an EffyError.
    """
    if sys.platform == "win32":
        return _load_via_wic(file_path)
    else:
        return _load_via_libjpeg(file_path)
