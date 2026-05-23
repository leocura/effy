from __future__ import annotations
from dataclasses import dataclass
from Effy.types import Effect, Result, Ok, Err
from Effy.error import EffyError

from Effy._internal.fp import pure

@dataclass(frozen=True, slots=True)
class RWops:
    """Immutable, position-tracked byte buffer for functional file I/O.

    Attributes:
        data: The raw bytes content of the buffer.
        position: The current read/write cursor offset within the data.
    """
    data: bytes
    position: int = 0

    @pure
    def read(self, size: int) -> tuple[RWops, bytes]:
        """Read up to size bytes from the current position.

        Args:
            size: Maximum number of bytes to read.

        Returns:
            A tuple of (new RWops with advanced position, bytes read).
        """
        end = min(self.position + size, len(self.data))
        read_data = self.data[self.position:end]
        return RWops(data=self.data, position=end), read_data

    @pure
    def write(self, data: bytes) -> RWops:
        """Write bytes at the current position, returning a new RWops.

        Args:
            data: The bytes to write into the buffer.

        Returns:
            A new RWops with the written data spliced in and an advanced position.
        """
        new_data = self.data[:self.position] + data + self.data[self.position + len(data):]
        return RWops(data=new_data, position=self.position + len(data))

    @pure
    def seek(self, offset: int, whence: int) -> RWops:
        """Reposition the cursor within the buffer.

        Args:
            offset: The byte offset relative to the whence anchor.
            whence: 0 for start, 1 for current position, 2 for end of data.

        Returns:
            A new RWops with the updated cursor position.
        """
        if whence == 0:
            pos = offset
        elif whence == 1:
            pos = self.position + offset
        elif whence == 2:
            pos = len(self.data) + offset
        else:
            pos = self.position
            
        pos = max(0, min(pos, len(self.data)))
        return RWops(data=self.data, position=pos)

def rw_from_file(path: str) -> Effect[Result[RWops, EffyError]]:
    """Read an entire file into an RWops buffer.

    Args:
        path: Filesystem path to read from.

    Returns:
        An Effect resolving to a Result containing the loaded RWops or an EffyError.
    """
    def _run() -> Result[RWops, EffyError]:
        """Thunk implementing file reading and loading logic."""
        try:
            with open(path, "rb") as f:
                data = f.read()
            return Ok(RWops(data=data))
        except Exception as e:
            return Err(EffyError(code=-1, message=str(e)))
    return Effect(_run)

def rw_to_file(rw: RWops, path: str) -> Effect[Result[None, EffyError]]:
    """Write the contents of an RWops buffer to a file.

    Args:
        rw: The RWops buffer to write.
        path: Filesystem path to write to.

    Returns:
        An Effect resolving to a Result indicating success or an EffyError.
    """
    def _run() -> Result[None, EffyError]:
        """Thunk implementing file writing and serialization logic."""
        try:
            with open(path, "wb") as f:
                f.write(rw.data)
            return Ok(None)
        except Exception as e:
            return Err(EffyError(code=-1, message=str(e)))
    return Effect(_run)

