from __future__ import annotations
import math
from typing import Callable, TYPE_CHECKING
from Effy._internal.fp import pure

if TYPE_CHECKING:
    from Effy.video.surface import PixelBuffer
    from Effy.video.rect import Rect
    from Effy.types import Color

Field = Callable[[int, int], float]


@pure
class CircleField:
    """A signed distance field representing a circle centered at (cx, cy)."""

    __slots__ = ("cx", "cy", "r")

    def __init__(self, cx: int, cy: int, r: int):
        """Initialize the circle field with center and radius.

        Args:
            cx: The x-coordinate of the circle's center.
            cy: The y-coordinate of the circle's center.
            r: The radius of the circle.
        """
        self.cx = cx
        self.cy = cy
        self.r = r
        
    def __call__(self, x: int, y: int) -> float:
        """Evaluate the signed distance at coordinates (x, y).

        Args:
            x: The x-coordinate to evaluate.
            y: The y-coordinate to evaluate.

        Returns:
            The signed distance to the circle's boundary.
        """
        dx = x - self.cx
        dy = y - self.cy
        return math.sqrt(dx * dx + dy * dy) - self.r


@pure
def circle_field(cx: int, cy: int, r: int) -> Field:
    """Create a circular signed distance field centered at (cx, cy) with radius r.
    
    Returns:
        A Field function returning exact signed distance (negative inside, positive outside).
    """
    return CircleField(cx, cy, r)


class RectField:
    """A signed distance field representing an axis-aligned rectangle."""

    __slots__ = ("cx", "cy", "half_w", "half_h")

    def __init__(self, rx: int, ry: int, rw: int, rh: int):
        """Initialize the rectangle field with position and dimensions.

        Args:
            rx: The x-coordinate of the rectangle's top-left corner.
            ry: The y-coordinate of the rectangle's top-left corner.
            rw: The width of the rectangle.
            rh: The height of the rectangle.
        """
        self.cx = rx + rw / 2.0
        self.cy = ry + rh / 2.0
        self.half_w = rw / 2.0
        self.half_h = rh / 2.0
        
    def __call__(self, x: int, y: int) -> float:
        """Evaluate the signed distance at coordinates (x, y).

        Args:
            x: The x-coordinate to evaluate.
            y: The y-coordinate to evaluate.

        Returns:
            The signed distance to the rectangle's boundary.
        """
        dx = abs(x - self.cx) - self.half_w
        dy = abs(y - self.cy) - self.half_h
        
        # Inline max/min checks to avoid function call overhead
        dx_out = dx if dx > 0.0 else 0.0
        dy_out = dy if dy > 0.0 else 0.0
        dist_outside = math.sqrt(dx_out * dx_out + dy_out * dy_out)
        
        max_dxy = dx if dx > dy else dy
        dist_inside = max_dxy if max_dxy < 0.0 else 0.0
        
        return dist_outside + dist_inside


@pure
def rect_field(rx: int, ry: int, rw: int, rh: int) -> Field:
    """Create a rectangular signed distance field.
    
    Returns:
        A Field function returning exact signed distance to the rectangle.
    """
    return RectField(rx, ry, rw, rh)


class LineField:
    """A signed distance field representing a rounded line segment."""

    __slots__ = ("x1", "y1", "dx", "dy", "l2", "half_thick")

    def __init__(self, x1: int, y1: int, x2: int, y2: int, thickness: float):
        """Initialize the line field with start/end points and thickness.

        Args:
            x1: The x-coordinate of the start point.
            y1: The y-coordinate of the start point.
            x2: The x-coordinate of the end point.
            y2: The y-coordinate of the end point.
            thickness: The thickness of the line segment.
        """
        self.x1 = x1
        self.y1 = y1
        self.dx = x2 - x1
        self.dy = y2 - y1
        self.l2 = self.dx * self.dx + self.dy * self.dy
        self.half_thick = thickness / 2.0
        
    def __call__(self, x: int, y: int) -> float:
        """Evaluate the signed distance at coordinates (x, y).

        Args:
            x: The x-coordinate to evaluate.
            y: The y-coordinate to evaluate.

        Returns:
            The signed distance to the line segment.
        """
        px = x - self.x1
        py = y - self.y1
        
        if self.l2 == 0.0:
            return math.sqrt(px * px + py * py) - self.half_thick
            
        t = (px * self.dx + py * self.dy) / self.l2
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
            
        proj_x = self.x1 + t * self.dx
        proj_y = self.y1 + t * self.dy
        
        dx = x - proj_x
        dy = y - proj_y
        return math.sqrt(dx * dx + dy * dy) - self.half_thick


@pure
def line_field(x1: int, y1: int, x2: int, y2: int, thickness: float) -> Field:
    """Create a line segment signed distance field.
    
    Returns:
        A Field function returning exact signed distance to a rounded line segment.
    """
    return LineField(x1, y1, x2, y2, thickness)


class UnionField:
    """A signed distance field representing the CSG union of two fields."""

    __slots__ = ("fields",)

    def __init__(self, f1: Field, f2: Field):
        """Initialize the union of two fields.

        Args:
            f1: The first Field.
            f2: The second Field.
        """
        self.fields: list[Field] = []
        
        # Test f1 and f2 to see if they are the dummy infinity seed field
        try:
            is_f1_inf = (f1(0, 0) == float('inf'))
        except Exception:
            is_f1_inf = False
            
        try:
            is_f2_inf = (f2(0, 0) == float('inf'))
        except Exception:
            is_f2_inf = False
            
        if not is_f1_inf:
            if isinstance(f1, UnionField):
                self.fields.extend(f1.fields)
            else:
                self.fields.append(f1)
                
        if not is_f2_inf:
            if isinstance(f2, UnionField):
                self.fields.extend(f2.fields)
            else:
                self.fields.append(f2)
                
        if not self.fields:
            self.fields.append(f1)

    def __call__(self, x: int, y: int) -> float:
        """Evaluate the minimum signed distance at coordinates (x, y) across all fields.

        Args:
            x: The x-coordinate to evaluate.
            y: The y-coordinate to evaluate.

        Returns:
            The minimum signed distance to the combined boundary.
        """
        m = self.fields[0](x, y)
        for f in self.fields[1:]:
            val = f(x, y)
            if val < m:
                m = val
        return m


class IntersectField:
    """A signed distance field representing the CSG intersection of two fields."""

    __slots__ = ("fields",)

    def __init__(self, f1: Field, f2: Field):
        """Initialize the intersection of two fields.

        Args:
            f1: The first Field.
            f2: The second Field.
        """
        self.fields: list[Field] = []
        if isinstance(f1, IntersectField):
            self.fields.extend(f1.fields)
        else:
            self.fields.append(f1)
        if isinstance(f2, IntersectField):
            self.fields.extend(f2.fields)
        else:
            self.fields.append(f2)

    def __call__(self, x: int, y: int) -> float:
        """Evaluate the maximum signed distance at coordinates (x, y) across all fields.

        Args:
            x: The x-coordinate to evaluate.
            y: The y-coordinate to evaluate.

        Returns:
            The maximum signed distance to the intersection boundary.
        """
        m = self.fields[0](x, y)
        for f in self.fields[1:]:
            val = f(x, y)
            if val > m:
                m = val
        return m


class SubtractField:
    """A signed distance field representing the CSG subtraction of a field from another."""

    __slots__ = ("f1", "f2")

    def __init__(self, f1: Field, f2: Field):
        """Initialize the subtraction of f2 from f1.

        Args:
            f1: The base Field to subtract from.
            f2: The Field to be subtracted.
        """
        self.f1 = f1
        self.f2 = f2

    def __call__(self, x: int, y: int) -> float:
        """Evaluate the signed distance at coordinates (x, y) after subtraction.

        Args:
            x: The x-coordinate to evaluate.
            y: The y-coordinate to evaluate.

        Returns:
            The signed distance to the subtracted boundary.
        """
        d1 = self.f1(x, y)
        d2 = self.f2(x, y)
        return d1 if d1 > -d2 else -d2


@pure
def union_field(f1: Field, f2: Field) -> Field:
    """Create a field representing the true CSG union of two fields."""
    return UnionField(f1, f2)


@pure
def intersect_field(f1: Field, f2: Field) -> Field:
    """Create a field representing the true CSG intersection of two fields."""
    return IntersectField(f1, f2)


@pure
def subtract_field(f1: Field, f2: Field) -> Field:
    """Create a field representing the true CSG subtraction of the second field from the first."""
    return SubtractField(f1, f2)


class SmoothUnionField:
    """A signed distance field representing gooey blending of two fields."""

    __slots__ = ("f1", "f2", "k")

    def __init__(self, f1: Field, f2: Field, k: float):
        """Initialize the smooth union with two fields and a smoothing factor.

        Args:
            f1: The first Field.
            f2: The second Field.
            k: The smoothing factor.
        """
        self.f1 = f1
        self.f2 = f2
        self.k = k
        
    def __call__(self, x: int, y: int) -> float:
        """Evaluate the smoothly blended signed distance at coordinates (x, y).

        Args:
            x: The x-coordinate to evaluate.
            y: The y-coordinate to evaluate.

        Returns:
            The smoothly blended signed distance value.
        """
        d1 = self.f1(x, y)
        d2 = self.f2(x, y)
        k = self.k
        h = k - abs(d1 - d2)
        h = h / k if h > 0.0 else 0.0
        min_d = d1 if d1 < d2 else d2
        return min_d - h * h * k * 0.25


@pure
def smooth_union_field(f1: Field, f2: Field, k: float) -> Field:
    """Create a field representing a smooth polynomial union of two fields (gooey blending).
    
    Args:
        k: The smoothing factor. Larger is more gooey.
    """
    return SmoothUnionField(f1, f2, k)


@pure
def render_field(surface: PixelBuffer, rect: Rect | None, field: Field, color: Color) -> PixelBuffer:
    """Render a signed distance field returning a new PixelBuffer.

    Args:
        surface: The input PixelBuffer.
        rect: Bounding region to limit rendering, or None for the full surface.
        field: The Field function to render.
        color: The Color of the field.

    Returns:
        A brand-new PixelBuffer with the field rendering command enqueued.
    """
    from Effy.render.commands import RenderFieldCmd
    return surface._append_command(RenderFieldCmd(rect=rect, field=field, color=color))
