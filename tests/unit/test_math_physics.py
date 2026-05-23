import pytest
from Effy.math.physics import Vector2, RigidBody, Polygon, Circle, sat_collision, circle_intersect, aabb_intersect, aabb_sweep
from Effy.video.rect import FRect

def test_vector2_math():
    v1 = Vector2(3.0, 4.0)
    v2 = Vector2(1.0, 2.0)
    assert v1.add(v2) == Vector2(4.0, 6.0)
    assert v1.sub(v2) == Vector2(2.0, 2.0)
    assert v1.dot(v2) == 11.0
    assert v1.cross(v2) == 2.0
    assert v1.magnitude() == 5.0
    assert v1.normalize() == Vector2(0.6, 0.8)

def test_rigidbody_integration():
    rb = RigidBody(Vector2(0, 0), Vector2(10, 0))
    rb2 = rb.integrate(1.0, gravity=Vector2(0, 9.8))
    assert rb2.velocity == Vector2(10, 9.8)
    assert rb2.position == Vector2(10, 9.8)

def test_sat_collision():
    # Two overlapping squares
    poly1 = Polygon((Vector2(0, 0), Vector2(10, 0), Vector2(10, 10), Vector2(0, 10)))
    poly2 = Polygon((Vector2(5, 5), Vector2(15, 5), Vector2(15, 15), Vector2(5, 15)))
    colliding, mtv = sat_collision(poly1, poly2)
    assert colliding is True
    assert mtv is not None
    assert mtv.magnitude() > 0

    # Two non-overlapping squares
    poly3 = Polygon((Vector2(20, 20), Vector2(30, 20), Vector2(30, 30), Vector2(20, 30)))
    colliding, mtv = sat_collision(poly1, poly3)
    assert colliding is False
    assert mtv is None

def test_circle_intersect():
    c1 = Circle(Vector2(0, 0), 5.0)
    c2 = Circle(Vector2(8, 0), 5.0) # distance is 8, r_sum is 10, overlap is 2
    colliding, mtv = circle_intersect(c1, c2)
    assert colliding is True
    assert mtv is not None
    assert mtv.x == -2.0 or mtv.x == 2.0

    c3 = Circle(Vector2(20, 0), 5.0)
    colliding, mtv = circle_intersect(c1, c3)
    assert colliding is False
    assert mtv is None

def test_aabb_sweep():
    r1 = FRect(0, 0, 10, 10)
    v1 = Vector2(10, 0)
    r2 = FRect(15, 0, 10, 10)
    v2 = Vector2(0, 0)
    
    # After dt=1.0, r1 moves 10 units right, x becomes 10, overlaps with r2 (x=15)
    # distance is 15 - 10 = 5. Speed is 10. Time of impact = 5/10 = 0.5
    colliding, toi, normal = aabb_sweep(r1, v1, r2, v2, 1.0)
    assert colliding is True
    assert toi == 0.5
    assert normal == Vector2(-1, 0)
