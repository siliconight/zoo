"""GLB + .blend export and scene fact-gathering.

Export ops are the only bpy.ops used in Zoo; both are background-safe.
"""
from __future__ import annotations

import bpy

from . import geometry


def _select_only(objs):
    for obj in bpy.data.objects:
        obj.select_set(False)
    for obj in objs:
        obj.select_set(True)
    if objs:
        bpy.context.view_layer.objects.active = objs[0]


def export_glb(filepath, collection):
    objs = list(collection.objects)
    _select_only(objs)
    kwargs = dict(filepath=filepath, export_format="GLB",
                  use_selection=True, export_apply=True,
                  export_yup=True,
                  # Custom properties ride out as glTF extras; Godot imports
                  # them as node metadata. Carries the LuxEmit_* emitter
                  # marker payload (lux_type / lux_anchor_id / ...) (v0.30).
                  export_extras=True)
    try:
        bpy.ops.export_scene.gltf(**kwargs, export_vertex_color="ACTIVE")
    except TypeError:  # older/newer exporter without that kwarg
        bpy.ops.export_scene.gltf(**kwargs)


def save_blend(filepath):
    bpy.ops.wm.save_as_mainfile(filepath=filepath, compress=True)


# Godot collision name-suffix conventions (any -> static collision on import)
_COL_SUFFIXES = ("-colonly", "-convcolonly", "-col", "-convcol")


def gather_facts(collection, root_name):
    """Collect the facts core.validate judges."""
    meshes = [o for o in collection.objects if o.type == "MESH"
              and not o.name.endswith(_COL_SUFFIXES) and "_LOD" not in o.name]
    col = [o for o in collection.objects
           if o.name.endswith(_COL_SUFFIXES)]
    if meshes:
        lo, hi = geometry.bounds_of(meshes)
        dims = {"width": hi.x - lo.x, "depth": hi.y - lo.y,
                "height": hi.z - lo.z}
    else:
        dims = {}
    tris = 0
    has_uvs = bool(meshes)
    has_wear = bool(meshes)
    mats = set()
    bad_xf = []
    for obj in meshes:
        me = obj.data
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        if not me.uv_layers:
            has_uvs = False
        # Existence is not enough -- export_glb writes the ACTIVE colour
        # attribute, so a Wear layer that is not active is written into the
        # mesh and dropped on export. This reported True on a build whose
        # shipped COLOR_0 was uniformly 1.0.
        if geometry.WEAR_LAYER not in me.color_attributes:
            has_wear = False
        else:
            try:
                act = me.color_attributes.active_color
                if act is None or act.name != geometry.WEAR_LAYER:
                    has_wear = False
            except AttributeError:
                pass
        for m in me.materials:
            if m:
                mats.add(m.name)
        if (obj.location.length > 1e-6
                or any(abs(s - 1.0) > 1e-6 for s in obj.scale)):
            bad_xf.append(obj.name)
    return {
        "dimensions": {k: round(v, 4) for k, v in dims.items()},
        "tris": tris,
        "parts": [o.name for o in meshes],
        "has_uvs": has_uvs,
        "has_wear_colors": has_wear,
        "materials": sorted(mats),
        "has_collision": bool(col),
        "unapplied_transforms": bad_xf,
    }
