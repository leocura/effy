"""State-Passing Abstraction for the Functionally Pure GPU Pipeline.

This module defines a linear state-passing layer to wrap inherently stateful
GPU driver interactions (like ctypes calls to WebGPU, Vulkan, or Metal).
By treating the GPU driver state as a token (`GPUState`) passed into and
returned by every function, the Python-facing API remains functionally pure.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from Effy.video.rect import Rect
import struct

import wgpu

class GPUState:
    """A linear state token representing the state of the GPU driver.
    
    This token is passed into and returned from every stateful GPU operation,
    ensuring a strict ordering and functional purity. It should never be reused.
    """
    __slots__ = ("device", "encoder", "render_pass")
    
    def __init__(self, device: wgpu.GPUDevice, encoder: wgpu.GPUCommandEncoder | None = None, render_pass: wgpu.GPURenderPassEncoder | None = None):
        self.device = device
        self.encoder = encoder
        self.render_pass = render_pass


_PIPELINE_CACHE = {}
_TEXTURE_CACHE = {}
_OUT_TEXTURE_CACHE = {}
_UNIFORM_CACHE = {}

def _get_or_compile_pipeline(device, shader):
    key = shader.source_code
    if key not in _PIPELINE_CACHE:
        from Effy.render.compiler import compile_pipeline
        _PIPELINE_CACHE[key] = compile_pipeline(device, shader)
    return _PIPELINE_CACHE[key]


_DEVICE = None

def init_gpu_driver() -> tuple[GPUState | None, bool]:
    """Initialize the underlying GPU driver using wgpu.
    
    Returns:
        A tuple of the new GPUState and a boolean indicating success.
    """
    global _DEVICE
    try:
        if _DEVICE is None:
            adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
            _DEVICE = adapter.request_device_sync()
        return GPUState(device=_DEVICE), True
    except Exception:
        return None, False


def begin_render_pass(state: GPUState, texture_view: wgpu.GPUTextureView, clear_color: tuple[float, float, float, float] = (0, 0, 0, 1)) -> GPUState:
    """Begin a render pass targeting the given texture view.
    
    Args:
        state: The linear GPUState token.
        texture_view: The texture view to render into.
        clear_color: The background clear color.
        
    Returns:
        The evolved GPUState token.
    """
    encoder = state.device.create_command_encoder()
    render_pass = encoder.begin_render_pass(
        color_attachments=[
            {
                "view": texture_view,
                "resolve_target": None,
                "clear_value": clear_color,
                "load_op": wgpu.LoadOp.clear,
                "store_op": wgpu.StoreOp.store,
            }
        ],
    )
    return GPUState(device=state.device, encoder=encoder, render_pass=render_pass)


def bind_shader(state: GPUState, render_pipeline: wgpu.GPURenderPipeline) -> GPUState:
    """Bind a compiled shader program to the GPU pipeline.
    
    Args:
        state: The linear GPUState token.
        render_pipeline: The compiled WGPU pipeline to bind.
        
    Returns:
        The evolved GPUState token.
    """
    state.render_pass.set_pipeline(render_pipeline)
    return GPUState(device=state.device, encoder=state.encoder, render_pass=state.render_pass)


def draw_quad(state: GPUState, rect: Rect) -> GPUState:
    """Draw a screen-space quad using the currently bound pipeline.
    
    Args:
        state: The linear GPUState token.
        rect: The screen-space bounds to draw the quad into.
        
    Returns:
        The evolved GPUState token.
    """
    # For a full screen quad mapping via uniform offsets, draw 6 vertices
    state.render_pass.draw(6, 1, 0, 0)
    return GPUState(device=state.device, encoder=state.encoder, render_pass=state.render_pass)


def end_render_pass(state: GPUState) -> GPUState:
    """End the current render pass.
    
    Args:
        state: The linear GPUState token.
        
    Returns:
        The evolved GPUState token.
    """
    state.render_pass.end()
    return GPUState(device=state.device, encoder=state.encoder, render_pass=None)


def submit_commands(state: GPUState) -> GPUState:
    """Submit the command encoder to the device queue.
    
    Args:
        state: The linear GPUState token.
        
    Returns:
        The evolved GPUState token.
    """
    state.device.queue.submit([state.encoder.finish()])
    return GPUState(device=state.device, encoder=None, render_pass=None)


def upload_texture(state: GPUState, width: int, height: int, data: bytes) -> tuple[GPUState, wgpu.GPUTexture]:
    """Create a GPUTexture and upload RGBA pixel data to it.
    
    Args:
        state: The linear GPUState token.
        width: Texture width.
        height: Texture height.
        data: Raw RGBA bytes.
        
    Returns:
        A tuple of the evolved GPUState and the created GPUTexture.
    """
    key = (width, height)
    if key not in _TEXTURE_CACHE:
        _TEXTURE_CACHE[key] = state.device.create_texture(
            size=(width, height, 1),
            usage=wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.COPY_DST,
            dimension=wgpu.TextureDimension.d2,
            format=wgpu.TextureFormat.rgba8unorm,
            mip_level_count=1,
            sample_count=1,
        )
    texture = _TEXTURE_CACHE[key]
    
    state.device.queue.write_texture(
        {"texture": texture, "origin": (0, 0, 0), "mip_level": 0},
        data,
        {"bytes_per_row": width * 4, "rows_per_image": height},
        (width, height, 1)
    )
    
    return state, texture


def read_texture_to_buffer(state: GPUState, texture: wgpu.GPUTexture, width: int, height: int) -> tuple[GPUState, bytes]:
    """Read a GPUTexture back to CPU memory.
    
    Args:
        state: The linear GPUState token.
        texture: The GPUTexture to read.
        width: Texture width.
        height: Texture height.
        
    Returns:
        A tuple of the evolved GPUState and the raw RGBA bytes.
    """
    memory_view = state.device.queue.read_texture(
        {"texture": texture, "origin": (0, 0, 0), "mip_level": 0},
        {"bytes_per_row": width * 4, "rows_per_image": height},
        (width, height, 1)
    )
    return state, memory_view.tobytes()

def resolve_gpu_shader(cmd: RenderShaderCmd, screen_w: int, screen_h: int) -> Result[Any, EffyError]:
    """Execute a single shader command natively on the WGPU backend.

    Args:
        cmd: The RenderShaderCmd to execute.
        screen_w: Full screen width fallback.
        screen_h: Full screen height fallback.

    Returns:
        A Result containing the output pixel array.array[int] representing the target region.
    """
    from Effy.types import Ok, Err
    import array
    import wgpu
    
    state, success = init_gpu_driver()
    if not success:
        return Err(EffyError(code=-1, message="Failed to initialize WGPU Driver"))

    target_w = cmd.dst_rect.w if cmd.dst_rect else screen_w
    target_h = cmd.dst_rect.h if cmd.dst_rect else screen_h

    key_out = (target_w, target_h)
    if key_out not in _OUT_TEXTURE_CACHE:
        _OUT_TEXTURE_CACHE[key_out] = state.device.create_texture(
            size=(target_w, target_h, 1),
            usage=wgpu.TextureUsage.RENDER_ATTACHMENT | wgpu.TextureUsage.COPY_SRC,
            dimension=wgpu.TextureDimension.d2,
            format=wgpu.TextureFormat.rgba8unorm,
            mip_level_count=1,
            sample_count=1,
        )
    out_texture = _OUT_TEXTURE_CACHE[key_out]

    if "sampler" not in _UNIFORM_CACHE:
        _UNIFORM_CACHE["sampler"] = state.device.create_sampler(
            mag_filter=wgpu.FilterMode.nearest,
            min_filter=wgpu.FilterMode.nearest,
        )
    sampler = _UNIFORM_CACHE["sampler"]

    if "uniform_buffer" not in _UNIFORM_CACHE:
        _UNIFORM_CACHE["uniform_buffer"] = state.device.create_buffer(
            size=48,
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
        )
    uniform_buffer = _UNIFORM_CACHE["uniform_buffer"]

    render_pipeline, bind_group_layout = _get_or_compile_pipeline(state.device, cmd.shader)

    # Upload texture if present
    if cmd.src_buffer:
        src_bytes = cmd.src_buffer._data.tobytes()
        state, input_tex = upload_texture(state, cmd.src_buffer.width, cmd.src_buffer.height, src_bytes)
    else:
        # Fallback texture
        state, input_tex = upload_texture(state, 1, 1, b'\x00\x00\x00\x00')

    # Draw region starts at 0,0 locally in the out_texture
    dx, dy, dw, dh = 0.0, 0.0, float(target_w), float(target_h)
    sx, sy, sw, sh = 0.0, 0.0, 1.0, 1.0

    uniform_data = struct.pack('12f', dx, dy, dw, dh, sx, sy, sw, sh, float(target_w), float(target_h), 0.0, 0.0)
    state.device.queue.write_buffer(uniform_buffer, 0, uniform_data)

    bind_group = state.device.create_bind_group(
        layout=bind_group_layout,
        entries=[
            {"binding": 0, "resource": input_tex.create_view()},
            {"binding": 1, "resource": sampler},
            {"binding": 2, "resource": {"buffer": uniform_buffer, "offset": 0, "size": 48}},
        ]
    )

    # Render Pass - clear with transparent black to preserve software composite
    state = begin_render_pass(state, out_texture.create_view(), clear_color=(0, 0, 0, 0))
    state = bind_shader(state, render_pipeline)
    state.render_pass.set_bind_group(0, bind_group, [], 0, 99)
    state = draw_quad(state, None)
    state = end_render_pass(state)
    state = submit_commands(state)

    # Readback
    state, final_rgba = read_texture_to_buffer(state, out_texture, target_w, target_h)

    data_arr = array.array('I')
    data_arr.frombytes(final_rgba)
    return Ok(data_arr)
