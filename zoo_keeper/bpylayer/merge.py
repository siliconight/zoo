"""Pack a module's visual parts into one mesh per material, for export only.

WHY. Zoo emits every part of a prop as its own object, so a prop reaches
Godot as one MeshInstance3D per part and costs one draw call per part.
Measured on cold run 9062's card shop, read out of the shipped glTF JSON:
1,602 visual meshes across 90 module GLBs carrying 274 distinct materials
between them -- 5.8 parts per material, each its own submission. The pack
wall is the worst of them: 118 meshes, 4 materials, 1,592 triangles, i.e.
13.5 triangles per draw call.

Frame cost on that package tracked DRAW CALLS and not geometry: 1,730 calls
-> 9.49 ms mean, 6,376 -> 25.59 ms, while primitives stayed near 1.4M
throughout and render-CPU ran about twice GPU. A second lap over the same
ground was no faster, so it was not shader compilation either. The parts,
not the triangles, were the bill.

THE CHUNK IS THE MODULE, AND NO LARGER. Every part of one pack wall enters
and leaves view together, so merging inside a module costs no culling
granularity. Merging ACROSS modules would cost exactly that, and is
deliberately not done here.

WHAT IS NEVER MERGED, each because something downstream reads its name:
collision proxies (`core.partnames.COL_SUFFIXES` -- Godot's importer and six
re-implementations of it decide solidity from the suffix), and `_LOD`
alternates (a LOD stands in for a part rather than beside it; merged into the
base it would draw twice). Markers -- `LuxEmit_*`, read by
`lux_fixture_spawner.gd`, and `ATT_*` -- are EMPTIES and so are not in the
mesh pool at all, but they ride out in the export set untouched, and their
glTF `extras` payload with them.

A GROUP OF ONE IS NOT A MERGE. A part that is the only one carrying its
material is exported AS ITSELF, not copied into a new mesh: one surface in,
one surface out, no draw call removed, and the part keeps the name its
consumers read it by. This is also what keeps the merged names clear of the
part names -- `wall_pack` calls a part `WallPack_Lens` and paints it
`M_WallPack_Lens`, so a merged name built from family plus material slug is
the part's own name, and because this pass is non-destructive the part is
still there to collide with it.

WHAT IS PRESERVED. Materials, one per merged surface, so an emissive face
keeps its own emission instead of being averaged into a wall and
`zoo_worldskin.gd`'s material-name tests still find it. UVs, the active
`Wear` colour attribute, per-face smoothing, per-edge sharpness and seams --
and the triangle count, which is ASSERTED against the pre-merge total rather
than assumed.

VERTICES ARE NOT WELDED, and that is the whole of why the picture does not
move. `geometry.shade_by_angle` decides an edge's sharpness from the two
faces meeting at it WITHIN one part. Welding coincident vertices from two
parts would hand each the other's normal and re-shade both. Every source
contributes its own vertices, so each part's topology -- and therefore its
shading -- survives intact, and the merge is a pure re-packing of the same
triangles into fewer submissions.

NON-DESTRUCTIVE. Merged objects live in a throwaway collection torn down
when the export returns, so `export.gather_facts` still measures the parts a
recipe built (it runs first, and its `fit_names` / `dressing` filters match
literal part names), `save_blend` still writes them, and every recipe test
that asserts on object names still sees them.

WHAT THIS DOES NOT DO, said out loud because an instrument depends on it:
`tools/check_coplanar.py` finds z-fighting by looking for coplanar overlapping
faces drawn from DIFFERENT mesh nodes, and skips a plane group that comes
from one node. Parts merged into one mesh therefore stop being visible to it.
The geometry is unchanged -- nothing here creates or removes a coincident
pair -- but that gate goes quiet about intra-module pairs. Zoo's own
`tools/coplanar_probe.py` compares every triangle against every other
regardless of which object it came from, and runs on the Blender objects
before this, so the coverage still exists upstream.
"""
from __future__ import annotations

import bmesh
import bpy

from ..core import partnames
from . import geometry

#: Name of the throwaway collection the merged objects are built into.
_TEMP_COLLECTION = "ZooMergedExport"


def _layer_signature(me):
    """A hashable description of a mesh's UV and colour layers.

    Parts whose layers differ must not share a mesh: a part with no `Wear`
    colours merged into one that has them would be written with whatever the
    layer defaults to, which is black, not white. `geometry.bm_to_object`
    called with ``finish=False`` -- the CRT screen, the vending panel, the
    card atlas, the register -- produces exactly that kind of part, so this
    is a real case and not a defensive one.
    """
    uvs = tuple(sorted(layer.name for layer in me.uv_layers))
    cols = []
    for attr in getattr(me, "color_attributes", ()):
        cols.append((attr.name, attr.domain, attr.data_type))
    return (uvs, tuple(sorted(cols)))


def _unsupported(me):
    """Why this mesh cannot be merged, or None.

    An unrecognised layer shape REFUSES to merge rather than merging and
    dropping it. Corner-domain colour is what `geometry.wear_colors` writes
    and what this file knows how to copy; a point-domain attribute would be
    silently lost, so it disqualifies the part instead.
    """
    for attr in getattr(me, "color_attributes", ()):
        if attr.domain != "CORNER":
            return "colour attribute %r on domain %s" % (attr.name, attr.domain)
        if attr.data_type not in ("BYTE_COLOR", "FLOAT_COLOR"):
            return "colour attribute %r of type %s" % (attr.name, attr.data_type)
    return None


def _identity(obj):
    """Zoo builds everything at world scale in place (`geometry.bounds_of`),
    and `export.gather_facts` reports any object that is not as
    `unapplied_transforms`. Merging reads raw vertex coordinates, so an
    object carrying a transform is left unmerged rather than silently baked
    -- which would change where it stands."""
    m = obj.matrix_world
    for r in range(4):
        for c in range(4):
            if abs(m[r][c] - (1.0 if r == c else 0.0)) > 1e-6:
                return False
    return True


def _slots_used(me):
    """The material slot indices that actually carry faces, in order."""
    seen = []
    for poly in me.polygons:
        i = poly.material_index
        if i not in seen:
            seen.append(i)
    return sorted(seen)


def _slot_material(me, slot):
    if 0 <= slot < len(me.materials):
        return me.materials[slot]
    return None


def _copy_faces(dst, me, slot, dst_layers):
    """Append the faces of ``me`` with material_index ``slot`` into ``dst``.

    Vertices are created per source, never looked up in what is already
    there, so nothing welds across parts.
    """
    src = bmesh.new()
    src.from_mesh(me)
    src.verts.ensure_lookup_table()
    src_uv = {name: src.loops.layers.uv[name]
              for name in dst_layers["uv"] if name in src.loops.layers.uv}
    src_col = {name: src.loops.layers.color[name]
               for name in dst_layers["col"] if name in src.loops.layers.color}
    src_fcol = {name: src.loops.layers.float_color[name]
                for name in dst_layers["fcol"]
                if name in src.loops.layers.float_color}
    vmap = {}
    for face in src.faces:
        if face.material_index != slot:
            continue
        verts = []
        for v in face.verts:
            nv = vmap.get(v.index)
            if nv is None:
                nv = dst.verts.new(v.co)
                vmap[v.index] = nv
            verts.append(nv)
        try:
            nf = dst.faces.new(verts)
        except ValueError:
            # Two identical faces in one group: bmesh refuses the duplicate.
            # Dropping it would change the triangle count, which the caller
            # asserts, so say so rather than absorb it.
            src.free()
            raise ValueError(
                "merge: duplicate face copying %r slot %d" % (me.name, slot))
        nf.smooth = face.smooth
        nf.material_index = 0
        for sl, dl in zip(face.loops, nf.loops):
            for name, layer in src_uv.items():
                dl[dst_layers["uv"][name]].uv = sl[layer].uv
            for name, layer in src_col.items():
                dl[dst_layers["col"][name]] = sl[layer]
            for name, layer in src_fcol.items():
                dl[dst_layers["fcol"][name]] = sl[layer]
    # Edge sharpness AFTER the faces exist: `shade_by_angle` wrote the
    # shading into `e.smooth`, and an edge that came back smooth by default
    # would round a corner the recipe meant to keep hard.
    for e in src.edges:
        a = vmap.get(e.verts[0].index)
        b = vmap.get(e.verts[1].index)
        if a is None or b is None:
            continue
        de = dst.edges.get((a, b))
        if de is not None:
            de.smooth = e.smooth
            de.seam = e.seam
    src.free()


def _build_mesh(name, sources, dst_layers):
    """One merged mesh from ``sources`` = [(object, slot), ...] in order."""
    dst = bmesh.new()
    layers = {
        "uv": {n: dst.loops.layers.uv.new(n) for n in dst_layers["uv"]},
        "col": {n: dst.loops.layers.color.new(n) for n in dst_layers["col"]},
        "fcol": {n: dst.loops.layers.float_color.new(n)
                 for n in dst_layers["fcol"]},
    }
    for obj, slot in sources:
        _copy_faces(dst, obj.data, slot, layers)
    me = bpy.data.meshes.new(name)
    dst.to_mesh(me)
    dst.free()
    # Same reason `geometry.bm_to_object` does it: the exporter writes the
    # ACTIVE colour attribute, and a Wear layer that is not the active one is
    # in the mesh and not in the file.
    try:
        if geometry.WEAR_LAYER in me.color_attributes:
            me.color_attributes.active_color = me.color_attributes[
                geometry.WEAR_LAYER]
    except (AttributeError, KeyError, TypeError):
        pass
    return me


class Packed(object):
    """The export set, plus the teardown that puts the scene back.

    ``objects`` is what to export. ``stats`` is what happened, for a caller
    that wants to print it. ``discard()`` removes everything this made and is
    safe to call twice.
    """

    def __init__(self, objects, stats, temp_objects, temp_collection):
        self.objects = objects
        self.stats = stats
        self._objects = temp_objects
        self._collection = temp_collection

    def discard(self):
        for obj in self._objects:
            me = obj.data
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
            except (ReferenceError, RuntimeError):
                pass
            if me is not None and me.users == 0:
                try:
                    bpy.data.meshes.remove(me)
                except (ReferenceError, RuntimeError):
                    pass
        self._objects = []
        if self._collection is not None:
            scene = bpy.context.scene.collection
            if self._collection.name in scene.children:
                scene.children.unlink(self._collection)
            try:
                bpy.data.collections.remove(self._collection)
            except (ReferenceError, RuntimeError):
                pass
            self._collection = None


def _tri_count(me):
    me.calc_loop_triangles()
    return len(me.loop_triangles)


def pack_by_material(collection):
    """Build the merged export set for ``collection``. Never mutates it.

    Returns a `Packed`, or None when there is nothing worth merging (every
    group of size one would just rename parts for no gain).
    """
    keep = []      # exported as-is: colliders, LODs, empties, refusals
    pooled = []    # the objects whose faces are going into a merged mesh
    refused = []   # (name, why) -- reported, not swallowed
    #: (part name, material name or "", layer signature) -> [(object, slot)]
    by_desc = {}
    for obj in collection.objects:
        if obj.type != "MESH" or not partnames.is_mergeable(obj.name):
            keep.append(obj)
            continue
        why = _unsupported(obj.data)
        if why is None and not _identity(obj):
            why = "unapplied transform"
        slots = _slots_used(obj.data)
        if why is None and not slots:
            why = "no faces"
        if why is not None:
            refused.append((obj.name, why))
            keep.append(obj)
            continue
        pooled.append(obj)
        sig = _layer_signature(obj.data)
        for slot in slots:
            mat = _slot_material(obj.data, slot)
            by_desc.setdefault(
                (obj.name, mat.name if mat else "", sig), []).append((obj, slot))

    if not by_desc:
        return None

    # One descriptor per (part, material, layers). A multi-slot object -- the
    # cigarette machine paints its lit panel with a second material_index --
    # appears once per slot under the same name, so its slots land in
    # different material groups, which is the point.
    #
    # The module's own object names are spoken for. `wall_pack` names a part
    # `WallPack_Lens` and paints it `M_WallPack_Lens`, so the merged name
    # collides with the part it came from -- see `partnames.group_parts`.
    groups = partnames.group_parts(
        ((name, mat or None, sig) for (name, mat, sig) in by_desc),
        taken={o.name for o in collection.objects})
    if not any(len(srcs) > 1 for _n, _k, srcs in groups):
        return None       # every group is a single part; renaming buys nothing

    # THE BASELINE IS THE POOL, NOT THE COLLECTION. A part refused above is
    # still exported as itself, so counting its triangles here would make the
    # assertion below fail for a part that was never merged.
    before_tris = sum(_tri_count(o.data) for o in pooled)

    temp = bpy.data.collections.new(_TEMP_COLLECTION)
    bpy.context.scene.collection.children.link(temp)
    made = []
    passed = []
    renamed = []
    for name, key, source_names in groups:
        _fam, mat_name, sig = key
        sources = []
        for sname in source_names:
            sources.extend(by_desc[(sname, mat_name, sig)])
        # A GROUP OF ONE IS NOT A MERGE, so it keeps its own object and its
        # own name. Copying one part's faces into a new mesh removes no draw
        # call -- one surface goes in and one comes out -- and it costs the
        # part the name three consumers read it by
        # (`portable_building.STOCK_NODE_PREFIX`, patina's TRIM keywords,
        # `tools/glb_nodes.py`'s census). The object must use exactly one
        # slot to qualify: a part painted with two materials has to be split
        # into two meshes, which is the whole point, so it goes the long way.
        if len(sources) == 1 and len(_slots_used(sources[0][0].data)) == 1:
            passed.append(sources[0][0])
            continue
        dst_layers = {"uv": sorted(sig[0]),
                      "col": sorted(n for n, _d, t in sig[1]
                                    if t == "BYTE_COLOR"),
                      "fcol": sorted(n for n, _d, t in sig[1]
                                     if t == "FLOAT_COLOR")}
        me = _build_mesh(name, sources, dst_layers)
        if mat_name:
            src_obj, src_slot = sources[0]
            me.materials.append(src_obj.data.materials[src_slot])
        obj = bpy.data.objects.new(name, me)
        # Blender makes a name unique by appending `.001`, which would land
        # in the glTF node name and make the export non-reproducible. Catch
        # it here rather than discover it in a diff.
        if obj.name != name:
            renamed.append((name, obj.name))
        temp.objects.link(obj)
        made.append(obj)

    # The pass-throughs are the SAME objects, so their triangles are counted
    # on the same side of the check as they were on the other -- leaving them
    # out here would fail the assertion for parts nothing touched.
    after_tris = (sum(_tri_count(o.data) for o in made)
                  + sum(_tri_count(o.data) for o in passed))
    export_set = keep + passed + made
    # An object reaching the exporter twice would draw twice and be invisible
    # in every count here, because the triangle assertion below sums the two
    # sides separately. The three lists are built to be disjoint; this is the
    # cheap check that they are.
    if len({id(o) for o in export_set}) != len(export_set):
        Packed([], {}, made, temp).discard()
        raise AssertionError(
            "merge: an object reached the export set twice (%d objects, %d "
            "distinct)" % (len(export_set), len({id(o) for o in export_set})))
    packed = Packed(export_set, {}, made, temp)
    if renamed:
        packed.discard()
        raise AssertionError(
            "merge: Blender renamed %d merged part(s), e.g. %r -> %r"
            % (len(renamed), renamed[0][0], renamed[0][1]))
    if after_tris != before_tris:
        packed.discard()
        raise AssertionError(
            "merge changed the triangle count: %d in parts, %d in merged "
            "meshes" % (before_tris, after_tris))

    packed.stats = {
        "parts_in": len(pooled),
        "meshes_out": len(made) + len(passed),
        "merged": len(made),
        "passed_through": len(passed),
        "kept": len(keep),
        "refused": refused,
        "triangles": before_tris,
    }
    return packed
