from __future__ import annotations
from dataclasses import dataclass
from Effy.types import TextureID, Effect, Result, Ok
from Effy.video.surface import PixelBuffer
from Effy.error import EffyError
from Effy._internal.registry import next_texture_id

@dataclass(frozen=True, slots=True)
class Texture:
    """Immutable handle wrapping a PixelBuffer as a named texture resource.

    Attributes:
        id: A unique TextureID identifying this texture.
        buffer: The underlying PixelBuffer containing the texture pixel data.
    """
    id: TextureID
    buffer: PixelBuffer

def create_texture_from_surface(buffer: PixelBuffer) -> Effect[Result[Texture, EffyError]]:
    """Create a Texture from an existing PixelBuffer.

    Args:
        buffer: The source PixelBuffer to wrap as a texture.

    Returns:
        An Effect resolving to a Result containing the new Texture or an EffyError.
    """
    def _run() -> Result[Texture, EffyError]:
        """Thunk that creates the texture with a unique ID."""
        tex_id = next_texture_id()
        return Ok(Texture(id=tex_id, buffer=buffer))
    return Effect(_run)

