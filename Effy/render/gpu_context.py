"""Immutable 2D Render Graphs for the Functionally Pure GPU Pipeline.

This module defines the purely functional, immutable structure of a 2D scene
destined for hardware acceleration via the GPU. It is designed as a parallel
path to the software `RenderContext`.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from Effy.types import WindowID
from Effy.video.rect import Rect


class RenderNode:
    """Base class for all immutable nodes in the 2D Render Graph."""
    pass


@dataclass(frozen=True, slots=True)
class GroupNode(RenderNode):
    """A node that groups multiple child nodes together."""
    children: tuple[RenderNode, ...] = ()


@dataclass(frozen=True, slots=True)
class Transform2DNode(RenderNode):
    """A node that applies a 2D affine transformation to its child.
    
    Attributes:
        matrix: A 3x3 transformation matrix represented as a tuple of 9 floats.
        child: The RenderNode to transform.
    """
    matrix: tuple[float, float, float, float, float, float, float, float, float]
    child: RenderNode


@dataclass(frozen=True, slots=True)
class ShaderNode(RenderNode):
    """A node that executes a compiled GPU shader program over a bounded region.
    
    Attributes:
        shader: A reference to the compiled GPUProgram.
        uniforms: A dictionary of uniform bindings passed to the shader.
        bounds: The Rect defining the screen-space bounding box for this shader.
    """
    shader: Any  # GPUProgram reference
    uniforms: dict[str, Any]
    bounds: Rect


@dataclass(frozen=True, slots=True)
class TextureNode(RenderNode):
    """A node that draws a 2D texture (e.g. from an emulator pixel buffer).
    
    Attributes:
        texture_view: The wgpu.GPUTextureView object or internal texture ID to draw.
        bounds: The Rect defining the screen-space bounds to draw the texture.
    """
    texture_view: Any
    bounds: Rect


@dataclass(frozen=True, slots=True)
class GPUContext:
    """An immutable rendering context that accumulates a 2D Render Graph.
    
    Unlike `RenderContext` which appends to a flat command list, `GPUContext`
    holds the root node of an immutable tree.
    
    Attributes:
        window_id: The ID of the window associated with this context.
        width: Width of the render target.
        height: Height of the render target.
        root_node: The current root RenderNode.
    """
    window_id: WindowID
    width: int
    height: int
    root_node: RenderNode = field(default_factory=GroupNode)

    def with_root(self, new_root: RenderNode) -> GPUContext:
        """Returns a new GPUContext with the specified root node."""
        return GPUContext(
            window_id=self.window_id,
            width=self.width,
            height=self.height,
            root_node=new_root
        )
