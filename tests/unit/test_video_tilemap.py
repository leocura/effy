import pytest
import tempfile
import json
import os
from Effy.video.tilemap import parse_tiled_json, render_tilemap
from Effy.video.camera import Camera
from Effy.render.renderer import RenderContext
from Effy.render.commands import BlitBlendedCmd
from Effy._internal.result import Ok

class MockBuffer:
    width = 256
    height = 256

class MockTexture:
    buffer = MockBuffer()

def test_parse_tiled_json():
    # Create a dummy json map
    data = {
        "width": 10,
        "height": 10,
        "tilewidth": 32,
        "tileheight": 32,
        "layers": [
            {
                "type": "tilelayer",
                "data": [1, 2, 0, 1] + [0] * 96,
                "width": 10,
                "height": 10,
                "visible": True
            }
        ],
        "tilesets": [
            {
                "firstgid": 1,
                "columns": 8,
                "tilewidth": 32,
                "tileheight": 32
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
        json.dump(data, f)
        temp_path = f.name
        
    try:
        res = parse_tiled_json(temp_path).run()
        assert isinstance(res, Ok)
        tilemap = res.value
        
        assert tilemap.width == 10
        assert tilemap.tilewidth == 32
        assert len(tilemap.layers) == 1
        assert tilemap.layers[0].data[0] == 1
        assert tilemap.layers[0].data[1] == 2
        assert tilemap.layers[0].data[2] == 0
    finally:
        os.unlink(temp_path)

def test_render_tilemap():
    res = parse_tiled_json("nonexistent.json").run()
    # It should fail nicely
    assert not isinstance(res, Ok)
    
    # Let's mock a tilemap
    from Effy.video.tilemap import Tilemap, TileLayer, Tileset
    
    tm = Tilemap(
        width=10, height=10, tilewidth=32, tileheight=32,
        layers=(
            TileLayer(data=tuple([1, 0, 2] + [0]*97), width=10, height=10, visible=True),
        ),
        tilesets=(
            Tileset(firstgid=1, columns=8, tilewidth=32, tileheight=32),
        )
    )
    
    renderer = RenderContext(0, 100, 100)
    camera = Camera(x=0.0, y=0.0) # screen center is 50,50. world 0,0 is at 50,50
    tex = MockTexture() # type: ignore
    
    renderer = render_tilemap(renderer, tm, camera, tex)
    # The first tile is at 0,0, world coordinates
    # The second tile is at 2*32=64, 0
    cmds = renderer._commands
    assert len(cmds) == 2
    assert isinstance(cmds[0], BlitBlendedCmd)
    
    # Check screen projection for the first tile
    # Camera at 0,0 -> translation is 50, 50.
    # Tile 0 is at (0, 0)
    # Screen rect: (50, 50, 32, 32)
    assert cmds[0].dst_rect.x == 50
    assert cmds[0].dst_rect.y == 50
    assert cmds[0].dst_rect.w == 32
    assert cmds[0].dst_rect.h == 32

    # Second tile is index 2, world x = 64
    assert cmds[1].dst_rect.x == 50 + 64
