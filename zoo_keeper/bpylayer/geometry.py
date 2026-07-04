"""bmesh geometry helpers for Zoo recipes.

Design rules:
- bmesh + data API only; no context-dependent bpy.ops for geometry.
- UVs via deterministic cube projection (no smart_project / edit mode).
- Wear via a 'Wear' corner color attribute: concavity darkening + seeded
  noise scaled by the plan's wear value. Godot multiplies it into albedo
  when 'Use as Albedo' is enabled on the material.
"""
from __future__ import annotations

import bmesh
import bpy
from mathutils import Matrix, Vector

WEAR_LAYER = "Wear"


# --- primitives (operate on a shared bmesh) --------------------------------

def new_bm() -> bmesh.types.BMesh:
    return bmesh.new()


def add_box(bm, center, size):
    """Axis-aligned box. center/size are (x, y, z) in meters."""
    ret = bmesh.ops.create_cube(bm, size=1.0)
    verts = ret["verts"]
    mat = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector(size).to_4d())
    bmesh.ops.transform(bm, matrix=mat, verts=verts)
    return verts


def add_cylinder(bm, center, radius, depth, segments=14, axis="Z",
                 cap=True):
    """Cylinder along +axis through center."""
    ret = bmesh.ops.create_cone(
        bm, cap_ends=cap, cap_tris=True, segments=segments,
        radius1=radius, radius2=radius, depth=depth)
    verts = ret["verts"]
    rot = Matrix.Identity(4)
    if axis == "X":
        rot = Matrix.Rotation(1.5707963, 4, "Y")
    elif axis == "Y":
        rot = Matrix.Rotation(1.5707963, 4, "X")
    mat = Matrix.Translation(Vector(center)) @ rot
    bmesh.ops.transform(bm, matrix=mat, verts=verts)
    return verts


def add_hemisphere(bm, center, radius_x, radius_y, radius_z, segments=20):
    """Upper hemisphere shell (open bottom), squashed to per-axis radii."""
    ret = bmesh.ops.create_uvsphere(
        bm, u_segments=segments, v_segments=max(6, segments // 2),
        radius=1.0)
    verts = ret["verts"]
    geom = verts + [e for v in verts for e in v.link_edges] + \
        [f for v in verts for f in v.link_faces]
    cut = bmesh.ops.bisect_plane(
        bm, geom=list(set(geom)), dist=1e-5,
        plane_co=(0, 0, 0), plane_no=(0, 0, -1), clear_inner=True)
    keep = [v for v in bm.verts if v.is_valid and v in set(verts)] or \
        [v for v in bm.verts if v.is_valid]
    mat = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector((radius_x, radius_y, radius_z)).to_4d())
    bmesh.ops.transform(bm, matrix=mat, verts=keep)
    return keep


def solidify(bm, thickness):
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=thickness)


def bevel_edges(bm, offset, segments=1, angle_min=0.6):
    """Bevel sharp edges (dihedral angle above angle_min radians)."""
    if offset <= 0:
        return
    edges = [e for e in bm.edges
             if len(e.link_faces) == 2
             and e.calc_face_angle(0.0) > angle_min]
    if edges:
        bmesh.ops.bevel(bm, geom=edges, offset=offset, segments=segments,
                        profile=0.7, affect="EDGES", clamp_overlap=True)


# --- UVs + wear -------------------------------------------------------------

def cube_project_uv(bm, texel=1.0):
    """Deterministic box projection: each face mapped by dominant normal
    axis; UVs in world meters * texel so texture density is uniform."""
    uv = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        n = f.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for loop in f.loops:
            co = loop.vert.co
            if az >= ax and az >= ay:
                u, v = co.x, co.y
            elif ax >= ay:
                u, v = co.y, co.z
            else:
                u, v = co.x, co.z
            loop[uv].uv = (u * texel, v * texel)


def wear_colors(bm, rng, wear):
    """Write grayscale wear into a corner color layer.

    Concave verts (avg edge angle) darken; seeded noise adds grime.
    wear=0 -> white; wear=1 -> heavy darkening."""
    layer = (bm.loops.layers.color.get(WEAR_LAYER)
             or bm.loops.layers.color.new(WEAR_LAYER))
    vert_dark = {}
    for v in bm.verts:
        angles = [e.calc_face_angle_signed(0.0) for e in v.link_edges
                  if len(e.link_faces) == 2]
        concave = sum(-a for a in angles if a < 0) / max(1, len(angles))
        noise = rng.random()
        dark = min(1.0, concave * 1.5 + noise * 0.5) * wear
        vert_dark[v.index] = 1.0 - min(0.85, dark)
    bm.verts.index_update()
    for f in bm.faces:
        for loop in f.loops:
            g = vert_dark.get(loop.vert.index, 1.0)
            loop[layer][:] = (g, g, g, 1.0)


# --- object plumbing ---------------------------------------------------------

def bm_to_object(bm, name, collection, finish=True, bevel=0.0,
                 texel=1.0, rng=None, wear=0.0):
    """Finish a bmesh (bevel -> normals -> UVs -> wear) and link an object."""
    if finish:
        bevel_edges(bm, bevel)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        cube_project_uv(bm, texel)
        if rng is not None:
            wear_colors(bm, rng, wear)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def bounds_of(objs):
    """(min, max) world-space AABB across objects (transforms assumed
    identity — Zoo builds everything at world scale in-place)."""
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for obj in objs:
        for v in obj.data.vertices:
            co = v.co
            lo.x, lo.y, lo.z = min(lo.x, co.x), min(lo.y, co.y), min(lo.z, co.z)
            hi.x, hi.y, hi.z = max(hi.x, co.x), max(hi.y, co.y), max(hi.z, co.z)
    return lo, hi
