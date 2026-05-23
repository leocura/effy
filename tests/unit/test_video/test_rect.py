from Effy.video.rect import Rect, Point, FRect, FPoint

def test_rect_evolve() -> None:
    r = Rect(1, 2, 3, 4)
    r2 = r.evolve(x=10)
    assert r2 == Rect(10, 2, 3, 4)
    assert r == Rect(1, 2, 3, 4) # immutability

def test_point_evolve() -> None:
    p = Point(1, 2)
    p2 = p.evolve(y=10)
    assert p2 == Point(1, 10)
    assert p == Point(1, 2)

def test_frect_evolve() -> None:
    r = FRect(1.0, 2.0, 3.0, 4.0)
    r2 = r.evolve(w=10.0)
    assert r2 == FRect(1.0, 2.0, 10.0, 4.0)
    assert r == FRect(1.0, 2.0, 3.0, 4.0)

def test_fpoint_evolve() -> None:
    p = FPoint(1.0, 2.0)
    p2 = p.evolve(x=10.0)
    assert p2 == FPoint(10.0, 2.0)
    assert p == FPoint(1.0, 2.0)
