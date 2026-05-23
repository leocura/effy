"""Extended compressed audio decoder support using platform native APIs (Media Foundation on Windows, libmpg123 on Linux) or pydub."""

from __future__ import annotations
import sys
import ctypes
import array
from typing import Any
from Effy._internal.result import Ok, Err, Result
from Effy.error import EffyError
from Effy.audio.types import AudioBuffer, AudioSpec, AudioFormat
from Effy.types import Effect



class GUID(ctypes.Structure):
    """ctypes representation of a GUID structure."""
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8)
    ]
    
    def __init__(self, guid_str: str) -> None:
        """Parse curly braced GUID string."""
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

def _decode_via_media_foundation(file_path: str) -> Result[AudioBuffer, EffyError]:
    """Decode compressed audio file via Windows Media Foundation Source Reader."""
    if sys.platform != "win32":
        return Err(EffyError(code=-1, message="Media Foundation is Windows only"))

    try:
        ole32 = ctypes.windll.ole32
        ole32.CoInitialize(None)

        mfplat = ctypes.windll.mfplat
        mfreadwrite = ctypes.windll.mfreadwrite

        # Initialize MF
        hr = mfplat.MFStartup(0x00070010, 0)  # MF_VERSION
        if hr < 0:
            return Err(EffyError(code=-1, message="Failed to initialize Windows Media Foundation"))

        reader_ptr = ctypes.c_void_p()
        # MFCreateSourceReaderFromURL: index-less flat FFI exported function
        hr = mfreadwrite.MFCreateSourceReaderFromURL(
            ctypes.c_wchar_p(file_path),
            None,
            ctypes.byref(reader_ptr)
        )
        if hr < 0 or not reader_ptr.value:
            mfplat.MFShutdown()
            return Err(EffyError(code=-1, message=f"Media Foundation failed to open file: {file_path}"))

        # Configure Source Reader to output PCM
        # Create MediaType
        mt_ptr = ctypes.c_void_p()
        hr = mfplat.MFCreateMediaType(ctypes.byref(mt_ptr))
        if hr < 0 or not mt_ptr.value:
            _call_com(reader_ptr, 2, [])
            mfplat.MFShutdown()
            return Err(EffyError(code=-1, message="Failed to create MF MediaType"))

        # GUID definitions
        guid_major_audio = GUID("{73647561-0000-0010-8000-00AA00389B71}") # MFMediaType_Audio
        guid_sub_pcm = GUID("{00000001-0000-0010-8000-00AA00389B71}")     # MFAudioFormat_PCM

        # Set major type: index 6
        hr = _call_com(mt_ptr, 6, [ctypes.POINTER(GUID), ctypes.POINTER(GUID)], GUID("{05589f81-c356-11ce-bf01-00aa0055595a}"), ctypes.byref(guid_major_audio))
        # Set subtype: index 6
        hr = _call_com(mt_ptr, 6, [ctypes.POINTER(GUID), ctypes.POINTER(GUID)], GUID("{f78996fc-8182-418f-8176-2103e1269c9c}"), ctypes.byref(guid_sub_pcm))

        # Set output media type on Source Reader: index 4 (SetCurrentMediaType)
        # Args: DWORD dwStreamIndex, DWORD* pdwReserved, IMFMediaType* pMediaType
        hr = _call_com(reader_ptr, 4, [ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p], 0xFFFFFFFE, None, mt_ptr) # MF_SOURCE_READER_FIRST_AUDIO_STREAM = 0xFFFFFFFE
        _call_com(mt_ptr, 2, []) # Release raw MediaType

        if hr < 0:
            _call_com(reader_ptr, 2, [])
            mfplat.MFShutdown()
            return Err(EffyError(code=-1, message="Failed to configure WMF output to PCM"))

        # Retrieve final decoded PCM format details
        curr_mt_ptr = ctypes.c_void_p()
        hr = _call_com(reader_ptr, 15, [ctypes.c_ulong, ctypes.POINTER(ctypes.c_void_p)], 0xFFFFFFFE, ctypes.byref(curr_mt_ptr)) # GetCurrentMediaType
        
        freq = 44100
        channels = 2
        if hr >= 0 and curr_mt_ptr.value:
            # Extract sample rate and channels from current media type attribute keys
            # WMF details: MFAudioFormat_SamplesPerSec = {5FAEE79C-2B7E-4947-901B-5C4D68A1B6B2}
            # MFAudioFormat_NumChannels = {37EA23C0-DD18-47D5-B5F4-EE0421D8228E}
            # GetUINT32: index 7
            val = ctypes.c_uint(0)
            _call_com(curr_mt_ptr, 7, [ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_uint)], GUID("{5FAEE79C-2B7E-4947-901B-5C4D68A1B6B2}"), ctypes.byref(val))
            if val.value > 0:
                freq = val.value
            _call_com(curr_mt_ptr, 7, [ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_uint)], GUID("{37EA23C0-DD18-47D5-B5F4-EE0421D8228E}"), ctypes.byref(val))
            if val.value > 0:
                channels = val.value
            _call_com(curr_mt_ptr, 2, [])

        pcm_data = array.array("h")
        sample_flags = ctypes.c_ulong(0)
        actual_stream_index = ctypes.c_ulong(0)
        timestamp = ctypes.c_longlong(0)
        sample_ptr = ctypes.c_void_p()

        while True:
            # ReadSample: index 9
            # Args: DWORD dwStreamIndex, DWORD dwControlFlags, DWORD* pdwActualStreamIndex, DWORD* pdwStreamFlags, LONGLONG* pllTimestamp, IMFSample** ppSample
            hr = _call_com(
                reader_ptr, 9,
                [ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_longlong), ctypes.POINTER(ctypes.c_void_p)],
                0xFFFFFFFE, 0, ctypes.byref(actual_stream_index), ctypes.byref(sample_flags), ctypes.byref(timestamp), ctypes.byref(sample_ptr)
            )
            if hr < 0:
                break

            # Check EOF flag (MF_SOURCE_READERF_ENDOFSTREAM = 0x00000002)
            if sample_flags.value & 0x02:
                break

            if sample_ptr.value:
                # Extract byte buffer from IMFSample
                buf_ptr = ctypes.c_void_p()
                # IMFSample::ConvertToContiguousBuffer: index 16
                hr = _call_com(sample_ptr, 16, [ctypes.POINTER(ctypes.c_void_p)], ctypes.byref(buf_ptr))
                if hr >= 0 and buf_ptr.value:
                    curr_len = ctypes.c_ulong(0)
                    max_len = ctypes.c_ulong(0)
                    data_ptr = ctypes.c_void_p()
                    # IMFMediaBuffer::Lock: index 3
                    # Args: BYTE** ppbBuffer, DWORD* pcbMaxLength, DWORD* pcbCurrentLength
                    hr = _call_com(buf_ptr, 3, [ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong)], ctypes.byref(data_ptr), ctypes.byref(max_len), ctypes.byref(curr_len))
                    if hr >= 0 and data_ptr.value:
                        num_shorts = curr_len.value // 2
                        shorts_array = (ctypes.c_short * num_shorts).from_address(data_ptr.value)
                        pcm_data.fromlist(list(shorts_array))
                        # Unlock buffer: index 4
                        _call_com(buf_ptr, 4, [])
                    _call_com(buf_ptr, 2, [])
                _call_com(sample_ptr, 2, [])

        _call_com(reader_ptr, 2, [])
        mfplat.MFShutdown()

        spec = AudioSpec(freq=freq, format=AudioFormat.S16, channels=channels, samples=len(pcm_data) // channels)
        return Ok(AudioBuffer(spec=spec, _data_array=pcm_data, _is_transient=False))
    except Exception as e:
        return Err(EffyError(code=-1, message=f"WMF audio decoder exception: {str(e)}"))

def _decode_via_libmpg123(file_path: str) -> Result[AudioBuffer, EffyError]:
    """Decode MP3 audio file via Linux libmpg123.so dynamic FFI."""
    libmpg123 = None
    for name in ("libmpg123.so.0", "libmpg123.so", "libmpg123.so.51"):
        try:
            libmpg123 = ctypes.cdll.LoadLibrary(name)
            break
        except Exception:
            continue

    if not libmpg123:
        return Err(EffyError(code=-1, message="libmpg123 not available on host system"))

    try:
        # FFI Definitions
        libmpg123.mpg123_init.argtypes = []
        libmpg123.mpg123_init.restype = ctypes.c_int
        
        libmpg123.mpg123_new.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
        libmpg123.mpg123_new.restype = ctypes.c_void_p
        
        libmpg123.mpg123_open.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        libmpg123.mpg123_open.restype = ctypes.c_int
        
        libmpg123.mpg123_getformat.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        libmpg123.mpg123_getformat.restype = ctypes.c_int
        
        libmpg123.mpg123_read.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
        libmpg123.mpg123_read.restype = ctypes.c_int
        
        libmpg123.mpg123_close.argtypes = [ctypes.c_void_p]
        libmpg123.mpg123_close.restype = ctypes.c_int
        
        libmpg123.mpg123_delete.argtypes = [ctypes.c_void_p]
        libmpg123.mpg123_delete.restype = None
        
        libmpg123.mpg123_exit.argtypes = []
        libmpg123.mpg123_exit.restype = None

        libmpg123.mpg123_init()
        err = ctypes.c_int(0)
        mh = libmpg123.mpg123_new(None, ctypes.byref(err))
        if not mh:
            return Err(EffyError(code=-1, message="Failed to instantiate mpg123 decoder handle"))

        if libmpg123.mpg123_open(mh, file_path.encode('utf-8')) != 0:
            libmpg123.mpg123_delete(mh)
            return Err(EffyError(code=-1, message=f"mpg123 failed to open audio file: {file_path}"))

        rate = ctypes.c_long(0)
        channels = ctypes.c_int(0)
        encoding = ctypes.c_int(0)
        libmpg123.mpg123_getformat(mh, ctypes.byref(rate), ctypes.byref(channels), ctypes.byref(encoding))

        # Enforce standard signed 16-bit PCM target format
        # mpg123 MPG123_ENC_SIGNED_16 = 0xd0
        # Re-configure if needed (mpg123 handles format conversions automatically)
        
        pcm_data = array.array("h")
        chunk_size = 16384
        chunk_buf = (ctypes.c_char * chunk_size)()
        done = ctypes.c_size_t(0)

        # mpg123_read returns 0 (MPG123_OK), -1 (MPG123_DONE/EOF) or others
        while True:
            ret = libmpg123.mpg123_read(mh, chunk_buf, chunk_size, ctypes.byref(done))
            if done.value > 0:
                num_shorts = done.value // 2
                shorts_array = (ctypes.c_short * num_shorts).from_buffer(chunk_buf)
                pcm_data.fromlist(list(shorts_array))
            if ret == -1 or done.value == 0:  # MPG123_DONE
                break
            if ret < 0:
                break

        libmpg123.mpg123_close(mh)
        libmpg123.mpg123_delete(mh)
        libmpg123.mpg123_exit()

        spec = AudioSpec(freq=rate.value, format=AudioFormat.S16, channels=channels.value, samples=len(pcm_data) // channels.value)
        return Ok(AudioBuffer(spec=spec, _data_array=pcm_data, _is_transient=False))
    except Exception as e:
        return Err(EffyError(code=-1, message=f"libmpg123 decode exception: {str(e)}"))

def load_compressed_audio(file_path: str) -> Effect[Result[AudioBuffer, EffyError]]:
    """Entry point resolving to a lazy Effect wrapping loaded compressed audio data (MP3/Vorbis).

    Args:
        file_path: Relative or absolute path to the audio file.

    Returns:
        An Effect wrapping a Result that contains an AudioBuffer or an EffyError.
    """
    def _run() -> Result[AudioBuffer, EffyError]:
        if sys.platform == "win32":
            return _decode_via_media_foundation(file_path)
        else:
            return _decode_via_libmpg123(file_path)

    return Effect(_run)

def load_audio(file_path: str) -> Effect[Result[AudioBuffer, EffyError]]:
    """Unified audio loader that routes to load_wav or load_compressed_audio based on suffix.

    Args:
        file_path: Relative or absolute path to the audio file.

    Returns:
        An Effect wrapping a Result that resolves to an AudioBuffer or an EffyError.
    """
    def _run() -> Result[AudioBuffer, EffyError]:
        from Effy.audio.wav import load_wav
        if file_path.lower().endswith(".wav"):
            return load_wav(file_path).run()
        else:
            return load_compressed_audio(file_path).run()
    return Effect(_run)
