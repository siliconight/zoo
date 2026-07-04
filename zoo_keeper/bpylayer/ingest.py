"""Blender-side ingest: import an external asset, normalize it to Zoo's
standard (pivot bottom-center on Z=0, optional scale-to-height, applied
transforms, optional bbox collision), and export a Godot-ready GLB + meta.json
— the same output shape as a generated specimen, so the importer treats them
identically.

WRITE-BLIND: this runs only inside Blender; iterate on real tracebacks.
"""
from __future__ import annotations

import json
import os

import bpy
from mathutils import Vector

from . import collision as _collision
from . import export as _export
from ..core import ingest as _ingest


def _clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def import_asset(filepath: str) -> list:
    """Import a mesh file; return the imported mesh objects. Format by ext."""
    ext = os.path.splitext(filepath)[1].lower()
    before = set(bpy.data.objects)
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=filepath)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=filepath)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=filepath)
    elif ext == ".dae":
        bpy.ops.wm.collada_import(filepath=filepath)
    elif ext == ".stl":
        bpy.ops.wm.stl_import(filepath=filepath)
    elif ext == ".ply":
        bpy.ops.wm.ply_import(filepath=filepath)
    else:
        raise ValueError(f"unsupported ingest format: {ext}")
    new = [o for o in bpy.data.objects if o not in before]
    return [o for o in new if o.type == "MESH"]


def _combined_bounds(objs):
    lo = Vector((1e18, 1e18, 1e18))
    hi = Vector((-1e18, -1e18, -1e18))
    for o in objs:
        for corner in o.bound_box:
            wc = o.matrix_world @ Vector(corner)
            lo.x, lo.y, lo.z = min(lo.x, wc.x), min(lo.y, wc.y), min(lo.z, wc.z)
            hi.x, hi.y, hi.z = max(hi.x, wc.x), max(hi.y, wc.y), max(hi.z, wc.z)
    return lo, hi


def normalize(objs, target_height=None):
    """Move to pivot bottom-center on Z=0, optionally uniform-scale so the
    overall height == target_height, then apply transforms. Returns the
    measured (w, d, h) after normalization."""
    if not objs:
        raise ValueError("nothing imported to normalize")

    # scale so overall height matches the target (keeps proportions)
    lo, hi = _combined_bounds(objs)
    height = max(hi.z - lo.z, 1e-6)
    if target_height:
        s = float(target_height) / height
        for o in objs:
            o.scale = o.scale * s
        bpy.context.view_layer.update()
        lo, hi = _combined_bounds(objs)

    # recenter: bbox center to X/Y = 0, bottom to Z = 0
    cx = (lo.x + hi.x) * 0.5
    cy = (lo.y + hi.y) * 0.5
    shift = Vector((-cx, -cy, -lo.z))
    for o in objs:
        o.location = o.location + shift

    # apply transforms so the export is clean (glTF-friendly)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    lo, hi = _combined_bounds(objs)
    return {"width": round(hi.x - lo.x, 4), "depth": round(hi.y - lo.y, 4),
            "height": round(hi.z - lo.z, 4)}


def ingest(src_file, out_dir, name=None, target_height=None, species=None,
           collision=True, license_note=None, tool_version="0.0.0"):
    """Import -> normalize -> export GLB + meta.json into out_dir."""
    name = name or _ingest.safe_name(src_file)
    _clear_scene()
    objs = import_asset(src_file)
    if not objs:
        raise ValueError(f"no mesh found in {os.path.basename(src_file)}")

    # collect everything into one export collection
    coll = bpy.data.collections.new(f"{name}_ingest")
    bpy.context.scene.collection.children.link(coll)
    for i, o in enumerate(objs):
        o.name = name if len(objs) == 1 else f"{name}_{i + 1}"
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)

    dims = normalize(objs, target_height)

    if collision:
        lo = (-dims["width"] / 2, -dims["depth"] / 2, 0.0)
        hi = (dims["width"] / 2, dims["depth"] / 2, dims["height"])
        _collision.collision_from_boxes(name.title().replace("_", ""),
                                        [(lo, hi)], coll)

    os.makedirs(out_dir, exist_ok=True)
    glb_path = os.path.join(out_dir, f"{name}.glb")
    _export.export_glb(glb_path, coll)

    meta = _ingest.ingest_meta(name, src_file, tool_version, dimensions=dims,
                               species=species, license_note=license_note)
    meta_path = os.path.join(out_dir, f"{name}.meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    return {"name": name, "glb": glb_path, "meta": meta_path, "dimensions": dims}
