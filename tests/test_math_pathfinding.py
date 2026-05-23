import pytest
from Effy.video.rect import Point
from Effy.math.pathfinding import Grid, find_path, manhattan_distance

def test_pathfinding_dijkstra():
    grid = Grid(10, 10, frozenset([Point(1, 0), Point(1, 1), Point(1, 2)]))
    path = find_path(grid, Point(0, 0), Point(2, 0))
    assert path is not None
    assert len(path) > 0
    assert path[0] == Point(0, 0)
    assert path[-1] == Point(2, 0)
    # The shortest path should go around the obstacle at x=1
    # (0,0) -> (0,1) -> (0,2) -> (0,3) -> (1,3) -> (2,3) -> (2,2) -> (2,1) -> (2,0)
    # This is 8 steps, plus start, so len should be 9
    assert len(path) == 9

def test_pathfinding_astar():
    grid = Grid(10, 10, frozenset([Point(1, 0), Point(1, 1), Point(1, 2)]))
    path = find_path(grid, Point(0, 0), Point(2, 0), heuristic=manhattan_distance)
    assert path is not None
    assert len(path) > 0
    assert path[0] == Point(0, 0)
    assert path[-1] == Point(2, 0)
    assert len(path) == 9

def test_no_path():
    grid = Grid(3, 3, frozenset([Point(1, 0), Point(1, 1), Point(1, 2)]))
    path = find_path(grid, Point(0, 0), Point(2, 0))
    assert len(path) == 0
