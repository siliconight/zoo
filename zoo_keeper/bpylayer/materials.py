"""Export-safe Principled materials: flat vertex-color wear by default,
Pixelcoat texture packs when a skin library is set.

Flat path (unchanged since forever): constant base color + best-effort
Color Attribute multiply for in-Blender preview. Godot reads COLOR_0 via
'Vertex Color -> Use as Albedo'.

Skin path (v0.27): ``set_skin_library(dir, theme)`` points the factory at
a folder of Pixelcoat packs (see ``core.skins`` for layout + resolution
order). When ``make_material`` finds a pack for a material kind it builds
an image-textured material instead — albedo (Closest interpolation, the
pixel-art look), normal (OpenGL Y+, Non-Color), stepped roughness
(Non-Color), optional emissive — shared per (kind, theme) across every
species. No pack -> flat, exactly as before: the art pass stays
progressive, matching DC's greybox fallback.

Density: mesh UVs are world meters * texel (geometry.cube_project_uv). A
Mapping node scales UVs by 1/meters_per_tile from the pack manifest, so a
pack authored as "one tile = 2 m" repeats every 2 m at texel 1.0 (the
glTF exporter emits this as KHR_texture_transform, which Godot 4 reads).
Wear still exports as COLOR_0 and multiplies the albedo texture at
runtime per the glTF spec; the in-Blender wear-preview mix is skipped on
textured materials to keep the exporter's texture detection unambiguous.
"""
from __future__ import annotations

import bpy

from .geometry import WEAR_LAYER

ROUGHNESS = {"laminate": 0.55, "wood": 0.65, "metal": 0.35, "plastic": 0.45,
             "leather": 0.70, "rubber": 0.85, "canvas": 0.90, "carbon": 0.30,
             "glass": 0.05, "glass_facade": 0.08, "paper": 0.80,
             "concrete": 0.92, "plaster": 0.88,
             "brick": 0.90, "tile": 0.35, "drywall": 0.90, "ceiling_tile": 0.92,
             "carpet": 0.98, "dirt": 0.97}
METALLIC = {"metal": 0.85, "carbon": 0.30}

_SKINS = {"dir": None, "theme": "delco"}


def set_skin_library(skins_dir, theme="delco"):
    """Point the material factory at a folder of Pixelcoat packs. Call
    once per session (the CLI does it when --skins is given); pass None
    to go back to flat materials."""
    _SKINS["dir"] = skins_dir
    _SKINS["theme"] = theme


def get_skin_library():
    """(dir, theme) the factory was pointed at — recipes with non-kind
    resolution needs (sign faces) read the library through this."""
    return _SKINS["dir"], _SKINS["theme"]


def _find_pack(material_kind):
    if not _SKINS["dir"]:
        return None
    from ..core import skins  # pure; imported lazily to keep flat path lean
    return skins.find_pack(_SKINS["dir"], material_kind, _SKINS["theme"])


def make_material(name, base_color, material_kind):
    """Same signature as always — recipes never know whether they got a
    flat or a textured material. With a skin library set, all parts of a
    kind share one textured material named for the pack (the genome's
    per-specimen color rides only the flat path; textured paint jobs are
    the pack's job)."""
    pack = _find_pack(material_kind)
    if pack:
        skin_name = f"M_Skin_{material_kind}_{_SKINS['theme']}"
        mat = bpy.data.materials.get(skin_name)
        if mat:
            return mat
        print(f"[zoo] skin: {material_kind} <- {pack['id']} ({pack['dir']})")
        return _textured(skin_name, pack, material_kind)

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


def make_emissive_material(name, color, strength=2.0):
    """Self-lit surface (fixture diffusers, streetlight lenses, sign faces).

    Plain Principled with Emission Color/Strength — exports as glTF emissive
    (+ KHR_materials_emissive_strength), which Godot 4 imports as
    StandardMaterial3D emission. Lux's LEVEL role keeps imported standard
    materials, so the face stays lit under any preset and contributes to a
    LightmapGI bake on the pc2000 path. No wear-preview mix and callers
    should paint the mesh with wear=0: a lit lens doesn't grime, and a
    white COLOR_0 keeps the albedo multiply neutral in Godot."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    rgba = (*color, 1.0)
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = 0.35
    try:  # Blender 4.x socket names; older builds fall back below
        bsdf.inputs["Emission Color"].default_value = rgba
        bsdf.inputs["Emission Strength"].default_value = float(strength)
    except KeyError:
        try:
            bsdf.inputs["Emission"].default_value = rgba
        except KeyError:
            pass
    return mat


def make_emissive_textured_material(name, pack, strength=2.2):
    """Sign face from a Pixelcoat sign pack: the albedo drives Base Color
    AND Emission Color (glTF emissive texture), so the artwork is what
    glows. Name must keep the ``_Face`` suffix — Lux's emissive binder
    matches by suffix, and the power cut has to kill branded signs exactly
    like flat ones. Roughness map linked when the pack ships one. Cached by
    name; callers make the name unique per pack."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = 0.35
    maps = pack["maps"]

    def tex_node(path, non_color=False):
        node = tree.nodes.new("ShaderNodeTexImage")
        node.image = _load_image(path, non_color)
        node.interpolation = "Closest"
        node.extension = "EXTEND"          # a sign face never tiles
        return node

    albedo = tex_node(maps["albedo"])
    tree.links.new(albedo.outputs["Color"], bsdf.inputs["Base Color"])
    try:  # Blender 4.x sockets; the flat fallback path mirrors this
        tree.links.new(albedo.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = float(strength)
    except KeyError:
        try:
            tree.links.new(albedo.outputs["Color"], bsdf.inputs["Emission"])
        except KeyError:
            pass
    if "roughness" in maps:
        rough = tex_node(maps["roughness"], non_color=True)
        tree.links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
    return mat


def _load_image(path, non_color=False):
    img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        try:  # colorspace name varies across OCIO configs
            img.colorspace_settings.name = "Non-Color"
        except Exception:
            pass
    return img


def _textured(name, pack, material_kind):
    """Image-textured Principled from a Pixelcoat pack. Exporter-friendly
    by construction: plain Image Texture -> socket links the glTF exporter
    recognizes, nothing clever between texture and Base Color."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    # Kind-level defaults still set: they are the fallback response for
    # any socket a pack doesn't texture.
    bsdf.inputs["Roughness"].default_value = ROUGHNESS.get(material_kind, 0.6)
    bsdf.inputs["Metallic"].default_value = METALLIC.get(material_kind, 0.0)
    maps = pack["maps"]

    def tex_node(path, non_color=False):
        node = tree.nodes.new("ShaderNodeTexImage")
        node.image = _load_image(path, non_color)
        node.interpolation = "Closest"       # pixel art stays pixel art
        node.extension = "REPEAT"
        return node

    vector_out = None
    mpt = pack.get("meters_per_tile") or 1.0
    if abs(mpt - 1.0) > 1e-9:
        try:  # UV scale -> KHR_texture_transform on export
            uv = tree.nodes.new("ShaderNodeUVMap")
            uv.uv_map = "UVMap"
            mapping = tree.nodes.new("ShaderNodeMapping")
            s = 1.0 / mpt
            mapping.inputs["Scale"].default_value = (s, s, s)
            tree.links.new(uv.outputs["UV"], mapping.inputs["Vector"])
            vector_out = mapping.outputs["Vector"]
        except Exception:
            vector_out = None

    def link_vector(node):
        if vector_out is not None:
            tree.links.new(vector_out, node.inputs["Vector"])

    albedo = tex_node(maps["albedo"])
    link_vector(albedo)
    tree.links.new(albedo.outputs["Color"], bsdf.inputs["Base Color"])

    if "roughness" in maps:
        rough = tex_node(maps["roughness"], non_color=True)
        link_vector(rough)
        tree.links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])

    if "normal" in maps:
        try:
            nrm = tex_node(maps["normal"], non_color=True)
            link_vector(nrm)
            nmap = tree.nodes.new("ShaderNodeNormalMap")
            nmap.inputs["Strength"].default_value = 1.0
            tree.links.new(nrm.outputs["Color"], nmap.inputs["Color"])
            tree.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
        except Exception:
            pass

    if "emissive" in maps:
        try:
            emi = tex_node(maps["emissive"])
            link_vector(emi)
            sock = ("Emission Color" if "Emission Color" in bsdf.inputs
                    else "Emission")                 # Blender 4.x vs older
            tree.links.new(emi.outputs["Color"], bsdf.inputs[sock])
            bsdf.inputs["Emission Strength"].default_value = 1.0
        except Exception:
            pass

    # See-through glass: honor a Pixelcoat pack's transparency hint
    # (import_hints.transparency = {opacity, ior}). opacity < 1 sets the
    # Principled Alpha + a blended surface so the glTF exporter writes
    # alphaMode=BLEND and Godot imports a transparent material. Facade glass
    # ships no hint (opaque). The blend-method attribute name varies across
    # Blender versions, so set both known spellings best-effort.
    trans = pack.get("transparency")
    if trans and float(trans.get("opacity", 1.0)) < 1.0:
        try:
            bsdf.inputs["Alpha"].default_value = float(trans["opacity"])
        except Exception:
            pass
        try:
            if "IOR" in bsdf.inputs:
                bsdf.inputs["IOR"].default_value = float(trans.get("ior", 1.45))
        except Exception:
            pass
        for _attr, _val in (("blend_method", "BLEND"),
                            ("surface_render_method", "BLENDED")):
            try:
                setattr(mat, _attr, _val)
            except Exception:
                pass

    return mat


def assign(objs, mat):
    for obj in objs:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
