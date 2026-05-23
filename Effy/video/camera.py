from __future__ import annotations
import math
from dataclasses import dataclass
from typing import cast, overload
from Effy.video.rect import Point, FPoint, Rect, FRect
from Effy._internal.fp import _EVOLVE_SENTINEL

@dataclass(frozen=True, slots=True)
class TransformMatrix:
    """A fully immutable 2D affine transformation matrix for composable rendering pipelines."""
    m00: float = 1.0
    m01: float = 0.0
    m02: float = 0.0
    m10: float = 0.0
    m11: float = 1.0
    m12: float = 0.0

    def multiply(self, other: TransformMatrix) -> TransformMatrix:
        """Compose this matrix with another matrix."""
        return TransformMatrix(
            self.m00 * other.m00 + self.m01 * other.m10,
            self.m00 * other.m01 + self.m01 * other.m11,
            self.m00 * other.m02 + self.m01 * other.m12 + self.m02,
            self.m10 * other.m00 + self.m11 * other.m10,
            self.m10 * other.m01 + self.m11 * other.m11,
            self.m10 * other.m02 + self.m11 * other.m12 + self.m12,
        )
        
    def inverse(self) -> TransformMatrix:
        """Calculate the inverse of this matrix."""
        det = self.m00 * self.m11 - self.m01 * self.m10
        if det == 0:
            return TransformMatrix() # Fallback to identity for singular matrices
        inv_det = 1.0 / det
        return TransformMatrix(
            self.m11 * inv_det,
            -self.m01 * inv_det,
            (self.m01 * self.m12 - self.m02 * self.m11) * inv_det,
            -self.m10 * inv_det,
            self.m00 * inv_det,
            (self.m02 * self.m10 - self.m00 * self.m12) * inv_det,
        )

    def transform_point(self, p: Point) -> Point:
        x = p.x * self.m00 + p.y * self.m01 + self.m02
        y = p.x * self.m10 + p.y * self.m11 + self.m12
        return Point(int(x), int(y))
        
    def transform_fpoint(self, p: FPoint) -> FPoint:
        x = p.x * self.m00 + p.y * self.m01 + self.m02
        y = p.x * self.m10 + p.y * self.m11 + self.m12
        return FPoint(x, y)
        
    def transform_rect(self, r: Rect) -> Rect:
        """Transforms a rectangle, returning its axis-aligned bounding box."""
        p1 = self.transform_point(Point(r.x, r.y))
        p2 = self.transform_point(Point(r.x + r.w, r.y))
        p3 = self.transform_point(Point(r.x, r.y + r.h))
        p4 = self.transform_point(Point(r.x + r.w, r.y + r.h))
        min_x = min(p1.x, p2.x, p3.x, p4.x)
        max_x = max(p1.x, p2.x, p3.x, p4.x)
        min_y = min(p1.y, p2.y, p3.y, p4.y)
        max_y = max(p1.y, p2.y, p3.y, p4.y)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def transform_frect(self, r: FRect) -> FRect:
        """Transforms a floating point rectangle, returning its axis-aligned bounding box."""
        p1 = self.transform_fpoint(FPoint(r.x, r.y))
        p2 = self.transform_fpoint(FPoint(r.x + r.w, r.y))
        p3 = self.transform_fpoint(FPoint(r.x, r.y + r.h))
        p4 = self.transform_fpoint(FPoint(r.x + r.w, r.y + r.h))
        min_x = min(p1.x, p2.x, p3.x, p4.x)
        max_x = max(p1.x, p2.x, p3.x, p4.x)
        min_y = min(p1.y, p2.y, p3.y, p4.y)
        max_y = max(p1.y, p2.y, p3.y, p4.y)
        return FRect(min_x, min_y, max_x - min_x, max_y - min_y)


def translate(x: float, y: float) -> TransformMatrix:
    """Create a translation matrix."""
    return TransformMatrix(m02=x, m12=y)

def scale(sx: float, sy: float) -> TransformMatrix:
    """Create a scaling matrix."""
    return TransformMatrix(m00=sx, m11=sy)

def rotate(angle_rad: float) -> TransformMatrix:
    """Create a rotation matrix."""
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return TransformMatrix(m00=c, m01=-s, m10=s, m11=c)

@dataclass(frozen=True, slots=True)
class Camera:
    """A purely functional 2D Camera abstraction."""
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0
    rotation: float = 0.0
    
    def evolve(self, x: float | object = _EVOLVE_SENTINEL, y: float | object = _EVOLVE_SENTINEL, zoom: float | object = _EVOLVE_SENTINEL, rotation: float | object = _EVOLVE_SENTINEL) -> Camera:
        return Camera(
            self.x if x is _EVOLVE_SENTINEL else cast(float, x),
            self.y if y is _EVOLVE_SENTINEL else cast(float, y),
            self.zoom if zoom is _EVOLVE_SENTINEL else cast(float, zoom),
            self.rotation if rotation is _EVOLVE_SENTINEL else cast(float, rotation),
        )

def get_camera_matrix(camera: Camera, viewport_width: int, viewport_height: int) -> TransformMatrix:
    """Generate the composed TransformMatrix for the camera given a viewport size.
    
    By default, the camera coordinates represent the center of the screen.
    """
    cx = viewport_width / 2.0
    cy = viewport_height / 2.0
    
    m = translate(cx, cy)
    if camera.zoom != 1.0:
        m = m.multiply(scale(camera.zoom, camera.zoom))
    if camera.rotation != 0.0:
        m = m.multiply(rotate(camera.rotation))
    m = m.multiply(translate(-camera.x, -camera.y))
    return m

@overload
def world_to_screen(camera: Camera, viewport_width: int, viewport_height: int, target: Point) -> Point: ...
@overload
def world_to_screen(camera: Camera, viewport_width: int, viewport_height: int, target: Rect) -> Rect: ...
@overload
def world_to_screen(camera: Camera, viewport_width: int, viewport_height: int, target: FPoint) -> FPoint: ...
@overload
def world_to_screen(camera: Camera, viewport_width: int, viewport_height: int, target: FRect) -> FRect: ...

def world_to_screen(camera: Camera, viewport_width: int, viewport_height: int, target: Point | Rect | FPoint | FRect) -> Point | Rect | FPoint | FRect:
    """Project world coordinates into screen coordinates based on camera state."""
    mat = get_camera_matrix(camera, viewport_width, viewport_height)
    if isinstance(target, Point):
        return mat.transform_point(target)
    elif isinstance(target, Rect):
        return mat.transform_rect(target)
    elif isinstance(target, FPoint):
        return mat.transform_fpoint(target)
    elif isinstance(target, FRect):
        return mat.transform_frect(target)
    raise TypeError(f"Unsupported type for world_to_screen: {type(target)}")

@overload
def screen_to_world(camera: Camera, viewport_width: int, viewport_height: int, target: Point) -> Point: ...
@overload
def screen_to_world(camera: Camera, viewport_width: int, viewport_height: int, target: Rect) -> Rect: ...
@overload
def screen_to_world(camera: Camera, viewport_width: int, viewport_height: int, target: FPoint) -> FPoint: ...
@overload
def screen_to_world(camera: Camera, viewport_width: int, viewport_height: int, target: FRect) -> FRect: ...

def screen_to_world(camera: Camera, viewport_width: int, viewport_height: int, target: Point | Rect | FPoint | FRect) -> Point | Rect | FPoint | FRect:
    """Un-project screen coordinates back into absolute world coordinates."""
    mat = get_camera_matrix(camera, viewport_width, viewport_height).inverse()
    if isinstance(target, Point):
        return mat.transform_point(target)
    elif isinstance(target, Rect):
        return mat.transform_rect(target)
    elif isinstance(target, FPoint):
        return mat.transform_fpoint(target)
    elif isinstance(target, FRect):
        return mat.transform_frect(target)
    raise TypeError(f"Unsupported type for screen_to_world: {type(target)}")


def camera_lerp(camera: Camera, target_x: float, target_y: float, factor: float) -> Camera:
    """Smoothly interpolate camera towards a target coordinate."""
    factor = max(0.0, min(1.0, factor))
    new_x = camera.x + (target_x - camera.x) * factor
    new_y = camera.y + (target_y - camera.y) * factor
    return camera.evolve(x=new_x, y=new_y)

def apply_shake(camera: Camera, intensity: float, seed: int) -> Camera:
    """Apply deterministic screen shake noise based on a seed (e.g. frame ticks)."""
    nx = math.sin(seed * 12.9898) * 43758.5453
    ny = math.sin(seed * 78.233) * 43758.5453
    
    shake_x = (nx - math.floor(nx)) * 2.0 - 1.0
    shake_y = (ny - math.floor(ny)) * 2.0 - 1.0
    
    return camera.evolve(x=camera.x + shake_x * intensity, y=camera.y + shake_y * intensity)
