"""GLB + .blend export and scene fact-gathering.

Export ops are the only bpy.ops used in Zoo; both are background-safe.
"""
from __future__ import annotations

import bpy

from ..core import gltf_textures, partnames
from . import geometry, merge


def _select_only(objs):
    for obj in bpy.data.objects:
        obj.select_set(False)
    for obj in objs:
        obj.select_set(True)
    if objs:
        bpy.context.view_layer.objects.active = objs[0]


def export_glb(filepath, collection, merge_parts=True, share_textures=True):
    """Write ``collection`` to a GLB.

    ``merge_parts`` packs the module's visual parts into one mesh per
    material first (`merge.pack_by_material`), which is what the file costs
    in draw calls rather than what it contains. It is a keyword rather than
    a constant so the two can be measured against each other from ONE build
    -- an A/B whose only difference is this flag, with the same seed, the
    same skins and the same commit. `tools/zoo_cli.py --no-merge-parts` is
    that control.

    ``share_textures`` moves the embedded images out to `_tex/` beside the
    GLB, named by a hash of their pixels, so modules that use one pack
    texture name one file (`core.gltf_textures` carries the measurement and
    the reason). Blender's GLB writer embeds unconditionally and has no
    setting for this, so it is a pass over the file it just wrote rather than
    an export option. A keyword for the same reason as `merge_parts`: the two
    states have to be measurable against each other from one build.

    The merged objects are torn down before this returns, so the scene
    `save_blend` writes is the one the recipe built either way.
    """
    packed = merge.pack_by_material(collection) if merge_parts else None
    objs = packed.objects if packed is not None else list(collection.objects)
    try:
        _select_only(objs)
        _export_selection(filepath)
        if share_textures:
            _share_textures(filepath)
    finally:
        if packed is not None:
            packed.discard()
    return packed.stats if packed is not None else None


def _share_textures(filepath):
    """Externalise the GLB's images, and say so on stdout.

    NEVER FATAL. A module that exported is a module that exists, and the
    embedded form it already has is the form every Zoo build before this one
    shipped -- so a file this pass cannot rewrite is left exactly as Blender
    wrote it and the reason is printed. Refusing the export instead would
    turn a size optimisation into a build failure.
    """
    try:
        st = gltf_textures.externalise_file(filepath)
    except (gltf_textures.GlbFormatError, OSError, ValueError) as exc:
        print(f"[zoo] textures stay embedded in {filepath}: {exc}")
        return None
    if st["images"]:
        print(f"[zoo] textures: {st['images']} images -> {st['written']} new "
              f"+ {st['shared']} already beside the GLB; "
              f"{st['bytes_before']} -> {st['bytes_after']} bytes")
    return st


def _export_selection(filepath):
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


# Godot collision name-suffix conventions (any -> static collision on import).
# Defined once in `core.partnames`, because `bpylayer.merge` asks the same
# question and two spellings of one contract drift.
_COL_SUFFIXES = partnames.COL_SUFFIXES


def gather_facts(collection, root_name, fit_names=None, dressing=()):
    """Collect the facts core.validate judges.

    ``fit_names``: when a recipe declares which of its objects define the
    slot envelope (a door leaf swung out of its frame does not), the
    dimensions and centre are measured on those, and the full visual bounds
    are reported beside them as ``overhang`` rather than silently replacing
    them. Without it every visual mesh is measured, exactly as before.

    ``dressing`` names objects set ON the module -- a desk's surface stock --
    that count toward its triangles and parts but not toward its measured
    size and centre: the slot is the desk's, and a monitor standing above
    the desk's top is not the desk being 37 cm too tall. Empty, which every
    caller before 0.84.0 passes, measures every mesh as it always did.

    Given both, dressing is set aside first and the envelope is the named fit
    objects among what remains; ``overhang`` stays the bounds of every visual
    mesh, dressing included, because it answers what stands in the room.
    """
    meshes = [o for o in collection.objects if o.type == "MESH"
              and not o.name.endswith(_COL_SUFFIXES) and "_LOD" not in o.name]
    col = [o for o in collection.objects
           if o.name.endswith(_COL_SUFFIXES)]
    skip = {getattr(o, "name", o) for o in dressing}
    body = [o for o in meshes if o.name not in skip] or meshes
    fit = ([o for o in body if o.name in set(fit_names)]
           if fit_names else body)
    overhang = None
    if fit_names and meshes:
        alo, ahi = geometry.bounds_of(meshes)
        overhang = {"min": [round(alo.x, 4), round(alo.y, 4), round(alo.z, 4)],
                    "max": [round(ahi.x, 4), round(ahi.y, 4), round(ahi.z, 4)]}
    if fit:
        lo, hi = geometry.bounds_of(fit)
        dims = {"width": hi.x - lo.x, "depth": hi.y - lo.y,
                "height": hi.z - lo.z}
        # Where the module's box actually sits. The kit index has always
        # REPEATED the plan's "pivot": "center"; this is the measurement the
        # claim is checked against (`fit_pivot`). Measured 2026-09-12 on
        # cold run 9019's site kit: the minted placeholders and the car were
        # built base-up (z 0 .. h) under a "center" claim, and a consumer
        # placing them by that claim stood them h/2 in the air.
        center = [round((lo.x + hi.x) / 2, 4), round((lo.y + hi.y) / 2, 4),
                  round((lo.z + hi.z) / 2, 4)]
    else:
        dims = {}
        center = None
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
    out = {
        "dimensions": {k: round(v, 4) for k, v in dims.items()},
        "center": center,
        "tris": tris,
        "parts": [o.name for o in meshes],
        "has_uvs": has_uvs,
        "has_wear_colors": has_wear,
        "materials": sorted(mats),
        "has_collision": bool(col),
        "unapplied_transforms": bad_xf,
    }
    if overhang is not None:
        out["overhang"] = overhang
    return out
