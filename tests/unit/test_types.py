from Effy.types import Color

def test_color_evolve() -> None:
    c = Color(1, 2, 3, 4)
    c2 = c.evolve(r=10)
    assert c2 == Color(10, 2, 3, 4)
    assert c == Color(1, 2, 3, 4) # immutability

def test_color_default_alpha() -> None:
    c = Color(1, 2, 3)
    assert c.a == 255

def test_color_validation() -> None:
    import pytest
    with pytest.raises(ValueError):
        Color(256, 0, 0)
    with pytest.raises(ValueError):
        Color(-1, 0, 0)
    with pytest.raises(ValueError):
        Color(0, 0, 0, 999)

