from Effy._internal.registry import get_platform_adapter
from Effy.platform.headless import HeadlessAdapter

def test_headless_adapter_active() -> None:
    adapter = get_platform_adapter()
    assert isinstance(adapter, HeadlessAdapter)
