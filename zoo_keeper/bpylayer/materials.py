"""Export-safe flat Principled materials with vertex-color wear.

Kept glTF-exporter friendly: Principled BSDF, constant base color, and a
best-effort Color Attribute multiply for in-Blender preview (wrapped in
try/except so node API churn can never break a build). Godot reads the
COLOR_0 attribute directly via 'Vertex Color -> Use as Albedo'.
"""
from __future__ import annotations

import bpy

from .geometry import WEAR_LAYER

ROUGHNESS = {"laminate": 0.55, "wood": 0.65, "metal": 0.35, "plastic": 0.45,
             "leather": 0.70, "rubber": 0.85, "canvas": 0.90, "carbon": 0.30,
             "glass": 0.05, "paper": 0.80}
METALLIC = {"metal": 0.85, "carbon": 0.30}


def make_material(name, base_color, material_kind):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    rgba = (*base_color, 1.0)
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = ROUGHNESS.get(material_kind, 0.6)
    bsdf.inputs["Metallic"].default_value = METALLIC.get(material_kind, 0.0)
    try:  # preview-only wear multiply; harmless if node API differs
        attr = tree.nodes.new("ShaderNodeVertexColor")
        attr.layer_name = WEAR_LAYER
        mix = tree.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        mix.inputs[6].default_value = rgba          # A
        tree.links.new(attr.outputs["Color"], mix.inputs[7])   # B
        tree.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    except Exception:
        pass
    return mat


def assign(objs, mat):
    for obj in objs:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
