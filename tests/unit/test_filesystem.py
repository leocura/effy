from Effy.filesystem import get_base_path, get_pref_path
from Effy.types import Effect

def test_get_base_path_returns_effect():
    effect = get_base_path()
    assert isinstance(effect, Effect)

def test_get_pref_path_returns_effect():
    effect = get_pref_path("org", "app")
    assert isinstance(effect, Effect)
