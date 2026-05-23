from __future__ import annotations
import json
from dataclasses import dataclass
from Effy.types import Result, Ok, Err, Effect
from Effy.error import EffyError
from Effy.video.rect import Rect, FPoint
from Effy.render.renderer import RenderContext
from Effy.video.camera import Camera, world_to_screen, screen_to_world
from Effy.render.texture import Texture
from Effy.render.commands import BlitBlendedCmd
from Effy._internal.fp import pure

@dataclass(frozen=True, slots=True)
class Tileset:
    """Immutable representation of a tileset in a Tiled JSON map."""
    firstgid: int
    columns: int
    tilewidth: int
    tileheight: int


@dataclass(frozen=True, slots=True)
class TileLayer:
    """Immutable representation of a tile layer."""
    data: tuple[int, ...]
    width: int
    height: int
    visible: bool


@dataclass(frozen=True, slots=True)
class Tilemap:
    """Immutable representation of a complete tilemap."""
    width: int
    height: int
    tilewidth: int
    tileheight: int
    layers: tuple[TileLayer, ...]
    tilesets: tuple[Tileset, ...]


def parse_tiled_json(filepath: str) -> Effect[Result[Tilemap, EffyError]]:
    """Parse a Tiled JSON map file.
    
    Args:
        filepath: Path to the JSON map.
        
    Returns:
        An Effect wrapping a Result that resolves to a Tilemap or an EffyError.
    """
    def _run() -> Result[Tilemap, EffyError]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tilesets = []
            for ts in data.get('tilesets', []):
                tilesets.append(Tileset(
                    firstgid=ts['firstgid'],
                    columns=ts['columns'],
                    tilewidth=ts['tilewidth'],
                    tileheight=ts['tileheight']
                ))
                
            layers = []
            for layer in data.get('layers', []):
                if layer.get('type') == 'tilelayer':
                    layers.append(TileLayer(
                        data=tuple(layer.get('data', [])),
                        width=layer.get('width', 0),
                        height=layer.get('height', 0),
                        visible=layer.get('visible', True)
                    ))
                    
            return Ok(Tilemap(
                width=data.get('width', 0),
                height=data.get('height', 0),
                tilewidth=data.get('tilewidth', 0),
                tileheight=data.get('tileheight', 0),
                layers=tuple(layers),
                tilesets=tuple(tilesets)
            ))
        except FileNotFoundError:
            return Err(EffyError(code=2, message=f"Tilemap file not found: {filepath}"))
        except Exception as e:
            return Err(EffyError(code=-1, message=f"Failed to parse tilemap: {str(e)}"))
            
    return Effect(_run)


@pure
def render_tilemap(renderer: RenderContext, tilemap: Tilemap, camera: Camera, texture: Texture) -> RenderContext:
    """Render visible tiles using simple camera frustum culling.
    
    This acts as an optimized sprite batcher by evaluating bounds once 
    and directly pushing BlitBlendedCmds into the command queue, skipping 
    redundant function call overhead.
    
    Args:
        renderer: The active RenderContext.
        tilemap: The parsed Tilemap.
        camera: The active Camera for transformations.
        texture: The loaded Texture containing the tileset atlas.
        
    Returns:
        A new RenderContext containing the batched draw commands.
    """
    if not tilemap.tilesets:
        return renderer
        
    ts = tilemap.tilesets[0]
    
    # Unproject the screen corners to world space to calculate the visible grid bounds
    top_left = screen_to_world(camera, renderer.width, renderer.height, FPoint(0.0, 0.0))
    bottom_right = screen_to_world(camera, renderer.width, renderer.height, FPoint(float(renderer.width), float(renderer.height)))
    
    # Determine tile indices covering the screen
    start_col = max(0, int(top_left.x // tilemap.tilewidth))
    start_row = max(0, int(top_left.y // tilemap.tileheight))
    end_col = min(tilemap.width - 1, int(bottom_right.x // tilemap.tilewidth) + 1)
    end_row = min(tilemap.height - 1, int(bottom_right.y // tilemap.tileheight) + 1)

    commands = list(renderer._commands)
    
    for layer in tilemap.layers:
        if not layer.visible:
            continue
            
        for r in range(start_row, end_row + 1):
            for c in range(start_col, end_col + 1):
                idx = r * layer.width + c
                if idx < 0 or idx >= len(layer.data):
                    continue
                
                gid = layer.data[idx]
                if gid == 0:
                    continue
                
                tid = gid - ts.firstgid
                if tid < 0:
                    continue
                
                src_x = (tid % ts.columns) * ts.tilewidth
                src_y = (tid // ts.columns) * ts.tileheight
                src_rect = Rect(src_x, src_y, ts.tilewidth, ts.tileheight)
                
                world_x = c * tilemap.tilewidth
                world_y = r * tilemap.tileheight
                
                # Project back to screen
                screen_rect = world_to_screen(camera, renderer.width, renderer.height, Rect(world_x, world_y, tilemap.tilewidth, tilemap.tileheight))
                
                commands.append(BlitBlendedCmd(src_buffer=texture.buffer, src_rect=src_rect, dst_rect=screen_rect))
                
    # Return evolved context
    return RenderContext(
        window_id=renderer.window_id,
        width=renderer.width,
        height=renderer.height,
        draw_color=renderer.draw_color,
        _commands=commands,
        _is_transient=True,
        flags=renderer.flags
    )
