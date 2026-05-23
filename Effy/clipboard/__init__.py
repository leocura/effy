from __future__ import annotations
import threading
from Effy.types import Effect, Result, Err
from Effy.error import SDLError
from Effy._internal.registry import get_platform_adapter

# Thread-safe in-memory history storage
_history_lock = threading.Lock()
_clipboard_history: list[str] = []
MAX_HISTORY_SIZE = 10

def get_clipboard_text() -> Effect[str]:
    """Get the text from the system clipboard.

    Returns:
        An Effect wrapping the retrieval of the clipboard text.
    """
    def _run() -> str:
        """Thunk implementing native platform clipboard text retrieval logic."""
        adapter = get_platform_adapter()
        if adapter:
            return adapter.get_clipboard_text()
        return ""
    return Effect(_run)

def set_clipboard_text(text: str) -> Effect[None]:
    """Set the text in the system clipboard and append it to the history.

    Args:
        text: The text to set in the clipboard.

    Returns:
        An Effect that sets the clipboard text and updates the history log.
    """
    def _run() -> None:
        """Thunk implementing native platform clipboard text update and local history logic."""
        adapter = get_platform_adapter()
        if adapter:
            adapter.set_clipboard_text(text)
        
        # Append to history ring
        with _history_lock:
            # Avoid duplicate consecutive copies in the history
            if not _clipboard_history or _clipboard_history[-1] != text:
                _clipboard_history.append(text)
                if len(_clipboard_history) > MAX_HISTORY_SIZE:
                    _clipboard_history.pop(0)
    return Effect(_run)

def get_clipboard_history() -> Effect[list[str]]:
    """Get a copy of the immutable clipboard history.

    Returns:
        An Effect wrapping the list of historical clipboard text items.
    """
    def _run() -> list[str]:
        """Thunk implementing thread-safe retrieval of clipboard history."""
        with _history_lock:
            return list(_clipboard_history)
    return Effect(_run)

def clear_clipboard_history() -> Effect[None]:
    """Clear all items in the clipboard history.

    Returns:
        An Effect that clears the history.
    """
    def _run() -> None:
        """Thunk implementing thread-safe clearing of clipboard history."""
        with _history_lock:
            _clipboard_history.clear()
    return Effect(_run)

def get_clipboard_data(mime_type: str) -> Effect[Result[bytes, SDLError]]:
    """Get binary data for a specific MIME type from the system clipboard.

    Args:
        mime_type: The MIME format string (e.g. 'application/json').

    Returns:
        An Effect wrapping the Result containing either the data bytes or an SDLError.
    """
    def _run() -> Result[bytes, SDLError]:
        """Thunk implementing native platform clipboard custom MIME data retrieval logic."""
        adapter = get_platform_adapter()
        if adapter:
            return adapter.get_clipboard_data(mime_type)
        return Err(SDLError(code=-1, message="Active platform adapter does not support custom clipboard data"))
    return Effect(_run)

def set_clipboard_data(mime_type: str, data: bytes) -> Effect[Result[None, SDLError]]:
    """Set binary data for a specific MIME type in the system clipboard.

    Args:
        mime_type: The MIME format string (e.g. 'application/json').
        data: The binary data to copy.

    Returns:
        An Effect wrapping the Result indicating success or carrying an SDLError.
    """
    def _run() -> Result[None, SDLError]:
        """Thunk implementing native platform clipboard custom MIME data update logic."""
        adapter = get_platform_adapter()
        if adapter:
            return adapter.set_clipboard_data(mime_type, data)
        return Err(SDLError(code=-1, message="Active platform adapter does not support custom clipboard data"))
    return Effect(_run)

__all__ = [
    "get_clipboard_text",
    "set_clipboard_text",
    "get_clipboard_history",
    "clear_clipboard_history",
    "get_clipboard_data",
    "set_clipboard_data",
]
