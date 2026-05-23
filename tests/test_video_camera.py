import pytest
import math
from Effy.video.camera import Camera, get_camera_matrix, TransformMatrix, translate
from Effy.video.rect import Point, Rect

def test_camera_translation():
    camera = Camera(x=10.0, y=20.0)
    mat = get_camera_matrix(camera, 100, 100)
    # camera at 10,20. screen center 50,50.
    # world point (10, 20) should map to screen (50, 50)
    p = mat.transform_point(Point(10, 20))
    assert p == Point(50, 50)

def test_camera_zoom():
    camera = Camera(x=0.0, y=0.0, zoom=2.0)
    mat = get_camera_matrix(camera, 100, 100)
    # distance from 0,0 is doubled
    p = mat.transform_point(Point(10, 10))
    assert p == Point(70, 70) # center is 50,50 + 10*2 = 70

def test_matrix_inverse():
    mat1 = translate(10.0, 20.0)
    mat_inv = mat1.inverse()
    p = mat_inv.transform_point(Point(10, 20))
    assert p == Point(0, 0)
