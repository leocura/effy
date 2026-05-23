"""Pure-functional Bitmap Font system using hardware-accelerated BlitCmd pipeline."""

from __future__ import annotations
from dataclasses import dataclass
from Effy.types import Effect, Result, Ok, Err
from Effy.video.surface import PixelBuffer
from Effy.video.image import load_image
from Effy.video.rect import Rect
from Effy.error import EffyError


@dataclass(frozen=True, slots=True)
class BitmapFont:
    """An immutable Bitmap Font mapped to a single PixelBuffer texture atlas.
    
    Attributes:
        buffer: The PixelBuffer containing the font spritesheet.
        glyph_width: The fixed width of each glyph.
        glyph_height: The fixed height of each glyph.
        char_map: Dictionary mapping characters to their source Rect in the buffer.
    """
    buffer: PixelBuffer
    glyph_width: int
    glyph_height: int
    char_map: dict[str, Rect]


def load_grid_font(
    file_path: str,
    glyph_width: int,
    glyph_height: int,
    char_map_str: str
) -> Effect[Result[BitmapFont, EffyError]]:
    """Load a fixed-grid spritesheet font from an image file.

    The char_map_str string maps linearly (left-to-right, top-to-bottom) across
    the spritesheet.

    Args:
        file_path: Path to the image file containing the font atlas.
        glyph_width: Width of a single character in pixels.
        glyph_height: Height of a single character in pixels.
        char_map_str: A string of characters matching the grid cells.

    Returns:
        An Effect wrapping a Result that resolves to a BitmapFont or an EffyError.
    """
    def _run() -> Result[BitmapFont, EffyError]:
        load_res = load_image(file_path).run()
        if not isinstance(load_res, Ok):
            return load_res
            
        buffer = load_res.value
        cols = buffer.width // glyph_width
        rows = buffer.height // glyph_height
        
        mapping = {}
        for i, char in enumerate(char_map_str):
            if char == '\n':
                continue
            
            c = i % cols
            r = i // cols
            
            if r >= rows:
                break
                
            mapping[char] = Rect(
                x=c * glyph_width,
                y=r * glyph_height,
                w=glyph_width,
                h=glyph_height
            )
            
        return Ok(BitmapFont(
            buffer=buffer,
            glyph_width=glyph_width,
            glyph_height=glyph_height,
            char_map=mapping
        ))

    return Effect(_run)
