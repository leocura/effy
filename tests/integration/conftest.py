import pytest
from Effy._internal.registry import set_platform_adapter
from Effy.platform.headless import HeadlessAdapter

@pytest.fixture(autouse=True)
def headless():
    set_platform_adapter(HeadlessAdapter())
    yield
    set_platform_adapter(None)
