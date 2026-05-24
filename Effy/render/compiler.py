"""Python-to-Shader Compilation (AST to GPU) for Effy.

This module provides the `@gpu_shader` decorator and the underlying AST
transpiler that converts pure Python math/SDF functions into GPU bytecode
(like WGSL or SPIR-V).
"""

from __future__ import annotations
import ast
import inspect
from typing import Callable, Any


class GPUProgram:
    """A compiled GPU shader program.
    
    Attributes:
        source_code: The transpiled shader source code (e.g., WGSL).
        original_func: The original Python function that was compiled.
    """
    def __init__(self, source_code: str, original_func: Callable):
        self.source_code = source_code
        self.original_func = original_func


class ShaderCompilerVisitor(ast.NodeVisitor):
    """An AST NodeVisitor that transpiles Python AST into WGSL."""
    
    def __init__(self):
        self.wgsl_code: list[str] = []
        self._indent_level = 0
        
    def _emit(self, text: str):
        self.wgsl_code.append(text)
        
    def _indent(self):
        self._emit("    " * self._indent_level)

    def _get_wgsl_type(self, py_type: str) -> str:
        mapping = {
            "float": "f32",
            "int": "i32",
            "Color": "vec4<f32>"
        }
        return mapping.get(py_type, "f32")

    def visit_FunctionDef(self, node: ast.FunctionDef):
        args = []
        for arg in node.args.args:
            arg_type = "f32"
            if arg.annotation and isinstance(arg.annotation, ast.Name):
                arg_type = self._get_wgsl_type(arg.annotation.id)
            args.append(f"{arg.arg}: {arg_type}")
            
        ret_type = "f32"
        if node.returns and isinstance(node.returns, ast.Name):
            ret_type = self._get_wgsl_type(node.returns.id)
            
        self._emit(f"fn {node.name}({', '.join(args)}) -> {ret_type} {{\n")
        self._indent_level += 1
        for stmt in node.body:
            self._indent()
            self.visit(stmt)
            self._emit(";\n")
        self._indent_level -= 1
        self._emit("}\n")
        
    def visit_Return(self, node: ast.Return):
        self._emit("return ")
        if node.value:
            self.visit(node.value)
            
    def visit_BinOp(self, node: ast.BinOp):
        self._emit("(")
        self.visit(node.left)
        
        op = node.op
        if isinstance(op, ast.Add):
            self._emit(" + ")
        elif isinstance(op, ast.Sub):
            self._emit(" - ")
        elif isinstance(op, ast.Mult):
            self._emit(" * ")
        elif isinstance(op, ast.Div):
            self._emit(" / ")
        else:
            self._emit(" /* unsupported op */ ")
            
        self.visit(node.right)
        self._emit(")")
        
    def visit_Name(self, node: ast.Name):
        self._emit(node.id)
        
    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, float):
            val = str(node.value)
            if "." not in val:
                val += ".0"
            self._emit(val)
        elif isinstance(node.value, int):
            self._emit(str(node.value))
        else:
            self._emit(str(node.value))
            
    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "math":
                func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            
        if func_name == "sample_texture":
            self._emit("textureSample(tex, samp, vec2<f32>(")
            self.visit(node.args[0])
            self._emit(", ")
            self.visit(node.args[1])
            self._emit("))")
            return
            
        mapping = {
            "sqrt": "sqrt",
            "abs": "abs",
            "sin": "sin",
            "cos": "cos",
            "min": "min",
            "max": "max"
        }
        wgsl_func = mapping.get(func_name, func_name)
        
        self._emit(f"{wgsl_func}(")
        for i, arg in enumerate(node.args):
            if i > 0:
                self._emit(", ")
            self.visit(arg)
        self._emit(")")

    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            self._emit(f"let {node.targets[0].id} = ")
            self.visit(node.value)


def gpu_shader(func: Callable) -> GPUProgram:
    """Decorator to JIT compile a pure Python function into a GPU shader.
    
    This function retrieves the source code of the decorated function, parses it
    into an AST, and transpiles it to WGSL using the ShaderCompilerVisitor.
    
    Args:
        func: The pure Python function to compile.
        
    Returns:
        A GPUProgram instance containing the compiled shader.
    """
    try:
        source = inspect.getsource(func)
    except OSError:
        # Fallback if source is not available (e.g., in REPL)
        return GPUProgram("// Source not available", func)
        
    tree = ast.parse(source)
    visitor = ShaderCompilerVisitor()
    visitor.visit(tree)
    
    wgsl_source = "".join(visitor.wgsl_code)
    return GPUProgram(wgsl_source, func)

def compile_pipeline(device: Any, shader: GPUProgram) -> tuple[Any, Any]:
    """Compile a GPUProgram into a WebGPU render pipeline.

    Args:
        device: The wgpu.GPUDevice to compile against.
        shader: The GPUProgram containing the WGSL source.

    Returns:
        A tuple of (GPURenderPipeline, GPUBindGroupLayout).
    """
    import wgpu
    wgsl_source = f"""
    struct RectUniforms {{
        dst_x: f32,
        dst_y: f32,
        dst_w: f32,
        dst_h: f32,
        src_x: f32,
        src_y: f32,
        src_w: f32,
        src_h: f32,
        screen_w: f32,
        screen_h: f32,
        pad1: f32,
        pad2: f32,
    }};

    struct VertexInput {{
        @builtin(vertex_index) vertex_index : u32,
    }};
    struct VertexOutput {{
        @builtin(position) position : vec4<f32>,
        @location(0) uv : vec2<f32>,
    }};

    @group(0) @binding(2) var<uniform> rect_data: RectUniforms;

    @vertex
    fn vs_main(in: VertexInput) -> VertexOutput {{
        var out: VertexOutput;
        var quad_pos = array<vec2<f32>, 6>(
            vec2<f32>(0.0, 0.0),
            vec2<f32>(1.0, 0.0),
            vec2<f32>(0.0, 1.0),
            vec2<f32>(0.0, 1.0),
            vec2<f32>(1.0, 0.0),
            vec2<f32>(1.0, 1.0)
        );
        let uv = quad_pos[in.vertex_index];
        
        // Map to dst_rect
        let screen_x = rect_data.dst_x + uv.x * rect_data.dst_w;
        let screen_y = rect_data.dst_y + uv.y * rect_data.dst_h;
        
        // Map to NDC [-1, 1]
        let ndc_x = (screen_x / max(1.0, rect_data.screen_w)) * 2.0 - 1.0;
        let ndc_y = 1.0 - (screen_y / max(1.0, rect_data.screen_h)) * 2.0;
        
        out.position = vec4<f32>(ndc_x, ndc_y, 0.0, 1.0);
        
        // Map UVs to src_rect
        out.uv = vec2<f32>(
            rect_data.src_x + uv.x * rect_data.src_w,
            rect_data.src_y + uv.y * rect_data.src_h
        );
        return out;
    }}

    @group(0) @binding(0) var tex: texture_2d<f32>;
    @group(0) @binding(1) var samp: sampler;

    {shader.source_code}

    @fragment
    fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {{
        return {shader.original_func.__name__}(in.uv.x, in.uv.y);
    }}
    """
    
    shader_module = device.create_shader_module(code=wgsl_source)
    
    bind_group_layout = device.create_bind_group_layout(
        entries=[
            {
                "binding": 0,
                "visibility": wgpu.ShaderStage.FRAGMENT,
                "texture": {"sample_type": wgpu.TextureSampleType.float},
            },
            {
                "binding": 1,
                "visibility": wgpu.ShaderStage.FRAGMENT,
                "sampler": {"type": wgpu.SamplerBindingType.filtering},
            },
            {
                "binding": 2,
                "visibility": wgpu.ShaderStage.VERTEX,
                "buffer": {
                    "type": wgpu.BufferBindingType.uniform,
                    "min_binding_size": 48,
                },
            },
        ]
    )
    
    pipeline_layout = device.create_pipeline_layout(bind_group_layouts=[bind_group_layout])
    
    render_pipeline = device.create_render_pipeline(
        layout=pipeline_layout,
        vertex={
            "module": shader_module,
            "entry_point": "vs_main",
            "buffers": [],
        },
        primitive={
            "topology": wgpu.PrimitiveTopology.triangle_list,
            "front_face": wgpu.FrontFace.ccw,
            "cull_mode": wgpu.CullMode.none,
        },
        depth_stencil=None,
        multisample=None,
        fragment={
            "module": shader_module,
            "entry_point": "fs_main",
            "targets": [
                {
                    "format": wgpu.TextureFormat.rgba8unorm,
                    "blend": None,
                },
            ],
        },
    )
    return render_pipeline, bind_group_layout

