from __future__ import annotations

from Effy.clipboard import (
    get_clipboard_text,
    set_clipboard_text,
    get_clipboard_history,
    clear_clipboard_history,
    get_clipboard_data,
    set_clipboard_data,
)
from Effy.compat import (
    SDL_GetClipboardText,
    SDL_SetClipboardText,
    SDL_GetClipboardData,
    SDL_SetClipboardData,
)
from Effy._internal.registry import set_platform_adapter
from Effy.platform.headless import HeadlessAdapter
from Effy.types import Effect, Ok, Err


def test_standard_clipboard_get_set() -> None:
    """Test setting and getting standard text data from the system clipboard."""
    adapter = HeadlessAdapter()
    set_platform_adapter(adapter)

    try:
        clear_clipboard_history().run()
        # Initially empty clipboard text
        text_eff = get_clipboard_text()
        assert isinstance(text_eff, Effect)
        assert text_eff.run() == ""

        # Set new clipboard text
        set_eff = set_clipboard_text("Hello, Effy!")
        assert isinstance(set_eff, Effect)
        set_eff.run()

        # Retrieve new text
        assert get_clipboard_text().run() == "Hello, Effy!"
    finally:
        set_platform_adapter(None)


def test_clipboard_history_ring() -> None:
    """Test thread-safe rolling clipboard history ring, including deduplication and boundaries."""
    adapter = HeadlessAdapter()
    set_platform_adapter(adapter)

    try:
        clear_clipboard_history().run()
        # Assert history is initially empty
        hist_eff = get_clipboard_history()
        assert isinstance(hist_eff, Effect)
        assert hist_eff.run() == []

        # Add unique copy entries
        set_clipboard_text("item1").run()
        set_clipboard_text("item2").run()
        set_clipboard_text("item3").run()

        # Check in-order history
        assert get_clipboard_history().run() == ["item1", "item2", "item3"]

        # Duplicate consecutive copies should be ignored to prevent pollution
        set_clipboard_text("item3").run()
        assert get_clipboard_history().run() == ["item1", "item2", "item3"]

        # Duplicate consecutive with different case/value should be stored
        set_clipboard_text("Item3").run()
        assert get_clipboard_history().run() == ["item1", "item2", "item3", "Item3"]

        # Clear history
        clear_eff = clear_clipboard_history()
        assert isinstance(clear_eff, Effect)
        clear_eff.run()
        assert get_clipboard_history().run() == []

        # Verify rolling limit of 10 items
        for i in range(15):
            set_clipboard_text(f"val_{i}").run()

        history = get_clipboard_history().run()
        assert len(history) == 10
        assert history == [f"val_{i}" for i in range(5, 15)]
    finally:
        set_platform_adapter(None)


def test_rich_mime_data_get_set() -> None:
    """Test copying and retrieving binary payloads associated with custom MIME formats."""
    adapter = HeadlessAdapter()
    set_platform_adapter(adapter)

    try:
        mime = "application/json"
        payload = b'{"hello": "world"}'

        # Retrieve a non-existent MIME format should return Err carrying EffyError
        get_fail_eff = get_clipboard_data(mime)
        assert isinstance(get_fail_eff, Effect)
        fail_res = get_fail_eff.run()
        assert isinstance(fail_res, Err)
        assert fail_res.is_err() is True

        # Copy data
        set_eff = set_clipboard_data(mime, payload)
        assert isinstance(set_eff, Effect)
        set_res = set_eff.run()
        assert isinstance(set_res, Ok)
        assert set_res.is_ok() is True

        # Retrieve successfully
        get_success_eff = get_clipboard_data(mime)
        success_res = get_success_eff.run()
        assert isinstance(success_res, Ok)
        assert success_res.is_ok() is True
        assert success_res.unwrap() == payload
    finally:
        set_platform_adapter(None)


def test_legacy_compat_clipboard_bindings() -> None:
    """Test that legacy compat layer bindings are correctly wired and work identically."""
    adapter = HeadlessAdapter()
    set_platform_adapter(adapter)

    try:
        clear_clipboard_history().run()
        # Standard legacy bindings
        SDL_SetClipboardText("Compat Text").run()
        assert SDL_GetClipboardText().run() == "Compat Text"

        # MIME legacy bindings
        set_res = SDL_SetClipboardData("text/plain", b"Compat Binary").run()
        assert isinstance(set_res, Ok)
        
        get_res = SDL_GetClipboardData("text/plain").run()
        assert isinstance(get_res, Ok)
        assert get_res.unwrap() == b"Compat Binary"
    finally:
        set_platform_adapter(None)
