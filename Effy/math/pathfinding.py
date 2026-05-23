from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any, cast
import math
from Effy.video.rect import Point
from Effy._internal.fp import pure

# --- Purely Functional Priority Queue (Leftist Heap) ---

@dataclass(frozen=True, slots=True)
class PQueueNode:
    """An immutable node for a functional Leftist Heap priority queue."""
    priority: float
    item: Any
    left: PQueueNode | None = None
    right: PQueueNode | None = None
    rank: int = 0

def pq_merge(h1: PQueueNode | None, h2: PQueueNode | None) -> PQueueNode | None:
    """Merge two functional priority queues."""
    if h1 is None: return h2
    if h2 is None: return h1
    
    if h1.priority > h2.priority:
        h1, h2 = h2, h1
        
    right = pq_merge(h1.right, h2)
    left = h1.left
    
    left_rank = left.rank if left else 0
    right_rank = right.rank if right else 0
    
    if left_rank < right_rank:
        left, right = right, left
        
    new_rank = (right.rank + 1) if right else 1
    return PQueueNode(h1.priority, h1.item, left, right, new_rank)

def pq_push(pq: PQueueNode | None, priority: float, item: Any) -> PQueueNode:
    """Push an item onto the functional priority queue, returning a new queue."""
    return pq_merge(pq, PQueueNode(priority, item)) # type: ignore

def pq_pop(pq: PQueueNode | None) -> tuple[Any, PQueueNode | None]:
    """Pop the lowest priority item from the queue, returning the item and the new queue."""
    if pq is None:
        raise IndexError("pop from empty priority queue")
    return pq.item, pq_merge(pq.left, pq.right)


# --- Purely Functional Immutable Map (BST) ---

@dataclass(frozen=True, slots=True)
class MapNode:
    """An immutable node for a functional Binary Search Tree Map."""
    key: tuple[int, int]
    value: Any
    left: MapNode | None = None
    right: MapNode | None = None

def map_set(node: MapNode | None, key: tuple[int, int], value: Any) -> MapNode:
    """Set a key-value pair, returning a new immutable MapNode."""
    if node is None:
        return MapNode(key, value)
    if key == node.key:
        return MapNode(key, value, node.left, node.right)
    elif key < node.key:
        return MapNode(node.key, node.value, map_set(node.left, key, value), node.right)
    else:
        return MapNode(node.key, node.value, node.left, map_set(node.right, key, value))

def map_get(node: MapNode | None, key: tuple[int, int], default: Any = None) -> Any:
    """Retrieve a value by key from the immutable map."""
    if node is None:
        return default
    if key == node.key:
        return node.value
    elif key < node.key:
        return map_get(node.left, key, default)
    else:
        return map_get(node.right, key, default)


# --- Pathfinding Grid & Logic ---

@dataclass(frozen=True, slots=True)
class Grid:
    """A purely functional 2D grid for pathfinding."""
    width: int
    height: int
    obstacles: frozenset[Point] = frozenset()
    
    @pure
    def is_walkable(self, p: Point) -> bool:
        return 0 <= p.x < self.width and 0 <= p.y < self.height and p not in self.obstacles
        
    @pure
    def get_neighbors(self, p: Point, allow_diagonal: bool = False) -> tuple[Point, ...]:
        neighbors = [
            Point(p.x + 1, p.y),
            Point(p.x - 1, p.y),
            Point(p.x, p.y + 1),
            Point(p.x, p.y - 1)
        ]
        if allow_diagonal:
            neighbors.extend([
                Point(p.x + 1, p.y + 1),
                Point(p.x - 1, p.y - 1),
                Point(p.x + 1, p.y - 1),
                Point(p.x - 1, p.y + 1)
            ])
        return tuple(n for n in neighbors if self.is_walkable(n))

@pure
def manhattan_distance(a: Point, b: Point) -> float:
    return abs(a.x - b.x) + abs(a.y - b.y)

@pure
def euclidean_distance(a: Point, b: Point) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def _reconstruct_path(came_from: MapNode | None, current: Point) -> tuple[Point, ...]:
    path: list[Point] = [current]
    current_key = (current.x, current.y)
    nxt = map_get(came_from, current_key)
    while nxt is not None:
        path.append(nxt)
        current_key = (nxt.x, nxt.y)
        nxt = map_get(came_from, current_key)
    path.reverse()
    return tuple(path)

@pure
def find_path(
    grid: Grid,
    start: Point,
    end: Point,
    heuristic: Callable[[Point, Point], float] | None = None,
    allow_diagonal: bool = False
) -> tuple[Point, ...]:
    """Find a path from start to end using A* or Dijkstra's algorithm.
    
    If heuristic is None, this executes Dijkstra's algorithm.
    If heuristic is provided (e.g. manhattan_distance), this executes A*.
    Uses purely functional data structures to guarantee zero impurity.
    """
    if not grid.is_walkable(start) or not grid.is_walkable(end):
        return ()

    pq: PQueueNode | None = pq_push(None, 0.0, start)
    came_from: MapNode | None = None
    cost_so_far: MapNode | None = map_set(None, (start.x, start.y), 0.0)

    while pq is not None:
        current_any, pq = pq_pop(pq)
        current = cast(Point, current_any)
        
        if current == end:
            return _reconstruct_path(came_from, current)
            
        current_cost = cast(float, map_get(cost_so_far, (current.x, current.y), float('inf')))
        
        for nxt in grid.get_neighbors(current, allow_diagonal):
            new_cost = current_cost + 1.0 # uniform cost grid
            nxt_key = (nxt.x, nxt.y)
            prev_cost = cast(float, map_get(cost_so_far, nxt_key, float('inf')))
            
            if new_cost < prev_cost:
                cost_so_far = map_set(cost_so_far, nxt_key, new_cost)
                came_from = map_set(came_from, nxt_key, current)
                
                priority = new_cost
                if heuristic:
                    priority += heuristic(nxt, end)
                
                pq = pq_push(pq, priority, nxt)
                
    return ()
