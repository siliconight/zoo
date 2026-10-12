"""A mesh leaves `bm_to_object` with its faces in one order, the same every build (1.103.0).

Blender's own BMesh operators lay faces in an order that changes from one process to the next: in
four fresh Blender 5.1 processes `create_uvsphere` kept its vertices' order and not its faces', and
`bisect_plane` neither; and an operator that makes a face from a list of edges starts it at a
corner that list's order picks -- the dome's cap, its rim given as the bmesh held it, started at
one of two corners in five processes, and at one when the rim was sorted (the factory's
docs/findings/grader_speed/uvsphere_order_probe.py). A GLB's triangles follow the faces and their
first corners, and Godot's lightmap unwrap follows the triangles, so two builds of the same kit made
two lightmaps: cold runs 9256 to 9259 packed the deli's three ways by one dome's chart. And
`add_hemisphere` handed its bisect a set of BMesh elements, which iterates in the order of their
addresses.

The pure half reads the source. The bpy half builds the shapes the domes, the bulbs and the bags
are made of and reads the meshes; it skips without Blender and was run inside Blender 5.1.1 for
this change, from the repo root:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_faces_in_order.py'])))"
"""

import ast
import os
import random

import pytest

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GEOMETRY = os.path.join(_ZOO, "zoo_keeper", "bpylayer", "geometry.py")
_DOME = os.path.join(_ZOO, "zoo_keeper", "recipes", "dome_fixture.py")


def _fn(path, name):
    tree = ast.parse(open(path, encoding="utf-8").read())
    return ast.unparse(next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name))


def test_the_faces_are_sorted_before_the_mesh_is_written():
    body = _fn(_GEOMETRY, "bm_to_object")
    assert body.index("in_one_order(bm, bm.faces)") < body.index("bm.faces.sort(") < body.index("bm.to_mesh(mesh)")


def test_the_hemisphere_hands_its_bisect_no_set():
    body = _fn(_GEOMETRY, "add_hemisphere")
    assert "set(geom)" not in body
    assert body.index("geom = in_one_order(") < body.index("bmesh.ops.bisect_plane(")


def test_the_hemisphere_starts_the_faces_its_bisect_split_at_their_lowest_vertex():
    body = _fn(_GEOMETRY, "add_hemisphere")
    assert body.index("bmesh.ops.transform(") < body.index("start_at_lowest(bm,") < body.index("return keep")


@pytest.mark.parametrize("segments", [14, 20])
def test_bpy_every_hemisphere_face_starts_at_its_lowest_vertex(segments):
    pytest.importorskip("bpy")
    import bmesh
    from zoo_keeper.bpylayer import geometry
    bm = bmesh.new()
    try:
        geometry.add_hemisphere(bm, (0.0, 0.0, 0.0), 0.2, 0.2, 0.1, segments=segments)
        bm.verts.index_update()
        late = [[v.index for v in f.verts] for f in bm.faces if f.verts[0].index != min(v.index for v in f.verts)]
        assert late == [], late[:3]
    finally:
        bm.free()


def test_the_fills_take_their_geometry_in_one_order_and_start_their_faces_at_the_lowest_vertex():
    dome = _fn(_DOME, "build")
    assert "rim = geometry.in_one_order(bm, [e for e in bm.edges if e.is_boundary])" in dome
    assert dome.index("bmesh.ops.holes_fill(") < dome.index("geometry.start_at_lowest(bm, cap['faces'])")
    src = open(_GEOMETRY, encoding="utf-8").read()
    assert src.count("bmesh.ops.contextual_create(") == 1
    assert "made = bmesh.ops.contextual_create(bm, geom=in_one_order(bm, cut))" in src
    assert 'start_at_lowest(bm, made.get("faces", []))' in src


def _faces(me):
    return [tuple(p.vertices) for p in me.polygons]


def _build(shape):
    import bmesh
    import bpy
    from zoo_keeper.bpylayer import geometry
    col = bpy.data.collections.new("faces_in_order_" + shape)
    bm = bmesh.new()
    if shape == "ellipsoid":
        geometry.add_ellipsoid(bm, (0.0, 0.0, 0.0), (0.05, 0.05, 0.06), u_seg=10, v_seg=6)
    else:
        geometry.add_hemisphere(bm, (0.0, 0.0, 0.0), 0.15, 0.15, 0.08, segments=20)
    bm.verts.index_update()
    # each face by its vertices, not its winding: the finish may turn a face to face out
    made = sorted(sorted(v.index for v in f.verts) for f in bm.faces)
    obj = geometry.bm_to_object(bm, "Faces_" + shape, col, bevel=0.0, texel=1.0)
    return obj.data, made


@pytest.mark.parametrize("shape", ["ellipsoid", "hemisphere"])
def test_bpy_the_faces_leave_sorted_by_their_vertices(shape):
    pytest.importorskip("bpy")
    me, _made = _build(shape)
    faces = _faces(me)
    assert faces == sorted(faces)


@pytest.mark.parametrize("shape", ["ellipsoid", "hemisphere"])
def test_bpy_the_faces_are_the_ones_the_shape_made(shape):
    pytest.importorskip("bpy")
    me, made = _build(shape)
    assert sorted(sorted(f) for f in _faces(me)) == made


def test_bpy_a_face_is_remade_to_start_at_its_lowest_vertex():
    pytest.importorskip("bpy")
    import bmesh
    from zoo_keeper.bpylayer import geometry
    bm = bmesh.new()
    try:
        vs = [bm.verts.new((x, y, 0.0)) for x, y in ((0, 0), (1, 0), (1, 1), (0, 1), (-0.5, 0.5))]
        f = bm.faces.new([vs[2], vs[3], vs[4], vs[0], vs[1]])
        f.material_index = 3
        f.smooth = True
        out = geometry.start_at_lowest(bm, [f])
        bm.verts.index_update()
        assert [v.index for v in out[0].verts] == [0, 1, 2, 3, 4]      # the same cycle, from 0
        assert out[0].material_index == 3 and out[0].smooth is True
        assert len(bm.faces) == 1
    finally:
        bm.free()


def test_bpy_it_refuses_a_face_that_carries_corner_data():
    pytest.importorskip("bpy")
    import bmesh
    from zoo_keeper.bpylayer import geometry
    bm = bmesh.new()
    try:
        vs = [bm.verts.new((x, y, 0.0)) for x, y in ((0, 0), (1, 0), (1, 1))]
        f = bm.faces.new([vs[1], vs[2], vs[0]])
        bm.loops.layers.uv.new("UVMap")
        with pytest.raises(ValueError):
            geometry.start_at_lowest(bm, [f])
    finally:
        bm.free()


def test_bpy_in_one_order_is_one_order_whatever_it_is_given():
    pytest.importorskip("bpy")
    import bmesh
    from zoo_keeper.bpylayer import geometry
    bm = bmesh.new()
    try:
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=4, radius=1.0)
        elems = list(bm.verts) + list(bm.edges) + list(bm.faces)
        runs = []
        for seed in (1, 2, 3):
            shuffled = list(elems)
            random.Random(seed).shuffle(shuffled)
            runs.append(geometry.in_one_order(bm, shuffled))
        assert runs[0] == runs[1] == runs[2]
        kinds = [0 if isinstance(e, bmesh.types.BMVert) else 1 if isinstance(e, bmesh.types.BMEdge) else 2
                 for e in runs[0]]
        assert kinds == sorted(kinds)
    finally:
        bm.free()
