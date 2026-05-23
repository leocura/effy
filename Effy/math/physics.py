from __future__ import annotations
import math
from dataclasses import dataclass
from typing import cast
from Effy._internal.fp import _EVOLVE_SENTINEL, pure
from Effy.video.rect import FRect

@dataclass(frozen=True, slots=True)
class Vector2:
    """An immutable 2D vector representation."""
    x: float
    y: float

    def evolve(self, x: float | object = _EVOLVE_SENTINEL, y: float | object = _EVOLVE_SENTINEL) -> Vector2:
        return Vector2(
            self.x if x is _EVOLVE_SENTINEL else cast(float, x),
            self.y if y is _EVOLVE_SENTINEL else cast(float, y),
        )

    def add(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def sub(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def mul(self, scalar: float) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)

    def dot(self, other: Vector2) -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: Vector2) -> float:
        return self.x * other.y - self.y * other.x

    def magnitude_squared(self) -> float:
        return self.x * self.x + self.y * self.y

    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)

    def normalize(self) -> Vector2:
        mag = self.magnitude()
        if mag == 0.0:
            return self
        return Vector2(self.x / mag, self.y / mag)

    def normal(self) -> Vector2:
        return Vector2(-self.y, self.x).normalize()


@dataclass(frozen=True, slots=True)
class RigidBody:
    """An immutable rigid body containing basic physics state."""
    position: Vector2
    velocity: Vector2
    mass: float = 1.0
    restitution: float = 0.5
    is_static: bool = False

    def evolve(self, position: Vector2 | object = _EVOLVE_SENTINEL, 
               velocity: Vector2 | object = _EVOLVE_SENTINEL,
               mass: float | object = _EVOLVE_SENTINEL,
               restitution: float | object = _EVOLVE_SENTINEL,
               is_static: bool | object = _EVOLVE_SENTINEL) -> RigidBody:
        return RigidBody(
            self.position if position is _EVOLVE_SENTINEL else cast(Vector2, position),
            self.velocity if velocity is _EVOLVE_SENTINEL else cast(Vector2, velocity),
            self.mass if mass is _EVOLVE_SENTINEL else cast(float, mass),
            self.restitution if restitution is _EVOLVE_SENTINEL else cast(float, restitution),
            self.is_static if is_static is _EVOLVE_SENTINEL else cast(bool, is_static),
        )

    def integrate(self, dt: float, gravity: Vector2 = Vector2(0.0, 0.0)) -> RigidBody:
        if self.is_static:
            return self
        new_vel = self.velocity.add(gravity.mul(dt))
        new_pos = self.position.add(new_vel.mul(dt))
        return self.evolve(position=new_pos, velocity=new_vel)


@dataclass(frozen=True, slots=True)
class Polygon:
    """An immutable convex polygon defined by a tuple of counter-clockwise vertices."""
    vertices: tuple[Vector2, ...]
    
    def evolve(self, vertices: tuple[Vector2, ...] | object = _EVOLVE_SENTINEL) -> Polygon:
        return Polygon(self.vertices if vertices is _EVOLVE_SENTINEL else cast(tuple[Vector2, ...], vertices))


@pure
def sat_collision(poly_a: Polygon, poly_b: Polygon) -> tuple[bool, Vector2 | None]:
    """Check collision between two convex polygons using Separating Axis Theorem (SAT).
    
    Returns:
        A tuple (is_colliding, minimum_translation_vector).
        If not colliding, the second element is None.
        The MTV points from poly_a to poly_b.
    """
    polygons = (poly_a, poly_b)
    min_overlap = float('inf')
    smallest_axis: Vector2 | None = None
    
    for i in range(2):
        poly = polygons[i]
        for j in range(len(poly.vertices)):
            p1 = poly.vertices[j]
            p2 = poly.vertices[(j + 1) % len(poly.vertices)]
            
            edge = p2.sub(p1)
            axis = edge.normal()
            
            min_a, max_a = float('inf'), float('-inf')
            for v in poly_a.vertices:
                projection = v.dot(axis)
                if projection < min_a: min_a = projection
                if projection > max_a: max_a = projection
                
            min_b, max_b = float('inf'), float('-inf')
            for v in poly_b.vertices:
                projection = v.dot(axis)
                if projection < min_b: min_b = projection
                if projection > max_b: max_b = projection
                
            if max_a <= min_b or max_b <= min_a:
                return False, None
            
            overlap = min(max_a, max_b) - max(min_a, min_b)
            if overlap < min_overlap:
                min_overlap = overlap
                smallest_axis = axis

    if smallest_axis is not None:
        # Compute centers to ensure MTV direction
        sum_a = Vector2(0, 0)
        for v in poly_a.vertices: sum_a = sum_a.add(v)
        center_a = sum_a.mul(1.0 / len(poly_a.vertices))

        sum_b = Vector2(0, 0)
        for v in poly_b.vertices: sum_b = sum_b.add(v)
        center_b = sum_b.mul(1.0 / len(poly_b.vertices))

        dir_vec = center_b.sub(center_a)
        if dir_vec.dot(smallest_axis) < 0:
            smallest_axis = smallest_axis.mul(-1.0)
        mtv = smallest_axis.mul(min_overlap)
        return True, mtv
        
    return True, Vector2(0.0, 0.0)


@dataclass(frozen=True, slots=True)
class Circle:
    """An immutable circle."""
    center: Vector2
    radius: float


@pure
def circle_intersect(c1: Circle, c2: Circle) -> tuple[bool, Vector2 | None]:
    """Check collision between two circles.
    
    Returns:
        A tuple (is_colliding, minimum_translation_vector).
    """
    diff = c2.center.sub(c1.center)
    dist_sq = diff.magnitude_squared()
    r_sum = c1.radius + c2.radius
    if dist_sq >= r_sum * r_sum:
        return False, None
    dist = math.sqrt(dist_sq)
    if dist == 0.0:
        return True, Vector2(0, r_sum)
    overlap = r_sum - dist
    mtv = diff.mul(overlap / dist)
    return True, mtv


@pure
def aabb_intersect(r1: FRect, r2: FRect) -> bool:
    """Check static intersection between two AABB floating-point rectangles."""
    return not (r1.x + r1.w <= r2.x or r1.x >= r2.x + r2.w or r1.y + r1.h <= r2.y or r1.y >= r2.y + r2.h)


@pure
def aabb_sweep(r1: FRect, v1: Vector2, r2: FRect, v2: Vector2, dt: float) -> tuple[bool, float, Vector2]:
    """Perform a swept AABB intersection test.
    
    Returns:
        A tuple (is_colliding, time_of_impact, normal).
        If not colliding within dt, time_of_impact is 1.0 and normal is Vector2(0,0).
    """
    v = v1.sub(v2).mul(dt)
    
    if v.x == 0:
        if r1.x + r1.w <= r2.x or r1.x >= r2.x + r2.w:
            return False, 1.0, Vector2(0, 0)
        x_entry = float('-inf')
        x_exit = float('inf')
        x_inv_entry = 0.0
    else:
        if v.x > 0:
            x_inv_entry = r2.x - (r1.x + r1.w)
            x_inv_exit = (r2.x + r2.w) - r1.x
        else:
            x_inv_entry = (r2.x + r2.w) - r1.x
            x_inv_exit = r2.x - (r1.x + r1.w)
        x_entry = x_inv_entry / v.x
        x_exit = x_inv_exit / v.x

    if v.y == 0:
        if r1.y + r1.h <= r2.y or r1.y >= r2.y + r2.h:
            return False, 1.0, Vector2(0, 0)
        y_entry = float('-inf')
        y_exit = float('inf')
        y_inv_entry = 0.0
    else:
        if v.y > 0:
            y_inv_entry = r2.y - (r1.y + r1.h)
            y_inv_exit = (r2.y + r2.h) - r1.y
        else:
            y_inv_entry = (r2.y + r2.h) - r1.y
            y_inv_exit = r2.y - (r1.y + r1.h)
        y_entry = y_inv_entry / v.y
        y_exit = y_inv_exit / v.y

    entry_time = max(x_entry, y_entry)
    exit_time = min(x_exit, y_exit)
    
    if entry_time > exit_time or (x_entry < 0.0 and y_entry < 0.0) or x_entry > 1.0 or y_entry > 1.0:
        return False, 1.0, Vector2(0, 0)
        
    normal = Vector2(0, 0)
    if x_entry > y_entry:
        if x_inv_entry < 0:
            normal = Vector2(1, 0)
        else:
            normal = Vector2(-1, 0)
    else:
        if y_inv_entry < 0:
            normal = Vector2(0, 1)
        else:
            normal = Vector2(0, -1)

    return True, entry_time, normal
