"""A bevelled mesh leaves `bm_to_object` the same every build (1.109.0, factory roadmap 247).

`bm_to_object` sorts a finished mesh's faces by their corners before it writes them (1.103.0), and its
bevel runs first. `bmesh.ops.bevel` starts the faces it makes and remakes at corners of its own
choosing, which move with the bmesh's face order and with the process -- and `create_uvsphere` lays its
faces in an order that changes from process to process. So a bevelled sphere left with its faces
starting at other corners, which no sort by corners can undo: the satellite dish's bowl, built six times
in fresh processes from cold run 9298's roof-props command, left four ways (the factory's
docs/findings/roofprops_bytes/). The 1.103.0 tests built their shapes with `bevel=0.0`.

`bevel_edges` now remakes every face it leaves to start at its lowest vertex (`start_at_lowest`), which
since 1.109.0 carries a face's corner data round with its corners rather than refusing it: a turning
part reaches the bevel carrying its UVMap and Pivot layers (`prim_mesh`).

The pure half reads the source. The bpy half lays the bowl's faces in shuffled orders -- what a fresh
process does to them -- and bevels each; it skips without Blender and was run inside Blender 5.1.1 for
this change, from the repo root:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_bevelled_faces_in_order.py'])))"
"""

import ast
import os
import random

import pytest

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GEOMETRY = os.path.join(_ZOO, "zoo_keeper", "bpylayer", "geometry.py")

#: the dish's bowl as `recipes/satellite_dish` asks for it on a 0.6 m dish: 0.22 of its radius front
#: to back, flat enough that the bevel takes its rim -- 62 vertices unbevelled, 98 bevelled
RADII = (0.3, 0.066, 0.3)
BEVEL = 0.01


def _fn(path, name):
    tree = ast.parse(open(path, encoding="utf-8").read())
    return ast.unparse(next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name))


def test_the_bevel_restarts_every_face_it_leaves():
    body = _fn(_GEOMETRY, "bevel_edges")
    assert body.index("bmesh.ops.bevel(") < body.index("start_at_lowest(bm, list(bm.faces))")


def test_start_at_lowest_refuses_no_corner_data():
    assert "raise" not in _fn(_GEOMETRY, "start_at_lowest")


def _shuffled_bowl(seed):
    """The bowl's bmesh, its faces laid in a seeded shuffle of their order."""
    import bmesh
    from zoo_keeper.bpylayer import geometry
    bm = bmesh.new()
    geometry.add_ellipsoid(bm, (0.0, 0.0, 0.0), RADII, u_seg=12, v_seg=6)
    bm.faces.index_update()
    order = list(range(len(bm.faces)))
    random.Random(seed).shuffle(order)
    bm.faces.sort(key=lambda f: order[f.index])
    return bm


def test_bpy_blender_s_bevel_starts_the_bowl_s_faces_where_their_order_says():
    """The control: Blender's own bevel, handed the bowl in six orders, starts its faces more than one
    way -- else the restart below would be proving nothing."""
    pytest.importorskip("bpy")
    import bmesh
    made = set()
    for seed in range(6):
        bm = _shuffled_bowl(seed)
        try:
            edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > 0.6]
            assert edges, "nothing to bevel: this control could see nothing"
            bmesh.ops.bevel(bm, geom=edges, offset=BEVEL, segments=1, profile=0.7, affect="EDGES",
                            clamp_overlap=True)
            bm.verts.index_update()
            made.add(tuple(sorted(tuple(v.index for v in f.verts) for f in bm.faces)))
        finally:
            bm.free()
    assert len(made) > 1


def test_bpy_a_bevelled_bowl_is_one_mesh_however_its_faces_were_laid():
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import geometry
    made = set()
    for seed in range(6):
        col = bpy.data.collections.new("bevelled_bowl_%d" % seed)
        me = geometry.bm_to_object(_shuffled_bowl(seed), "Bowl_%d" % seed, col, bevel=BEVEL, texel=1.0).data
        assert len(me.vertices) == 98, len(me.vertices)          # the bevel ran
        made.add((tuple(tuple(round(c, 6) for c in v.co) for v in me.vertices),
                  tuple(tuple(p.vertices) for p in me.polygons)))
    assert len(made) == 1


def test_bpy_start_at_lowest_carries_each_corner_s_data_with_its_corner():
    pytest.importorskip("bpy")
    import bmesh
    from zoo_keeper.bpylayer import geometry
    bm = bmesh.new()
    try:
        vs = [bm.verts.new((x, y, 0.0)) for x, y in ((0, 0), (1, 0), (1, 1), (0, 1))]
        f = bm.faces.new([vs[2], vs[3], vs[0], vs[1]])
        f.material_index = 2
        uv = bm.loops.layers.uv.new("UVMap")
        pivot = bm.loops.layers.uv.new("Pivot")
        wear = bm.loops.layers.color.new("Wear")
        weight = bm.loops.layers.float.new("weight")
        bm.verts.index_update()
        for lp in f.loops:
            i = lp.vert.index
            lp[uv].uv = (0.1 * i, 0.2 * i)
            lp[uv].pin_uv = i == 2
            lp[pivot].uv = (i, -i)
            lp[wear] = (0.2 * i, 0.0, 1.0 - 0.2 * i, 1.0)
            lp[weight] = 1.5 * i

        def held(face):
            return {lp.vert.index: (tuple(lp[uv].uv), lp[uv].pin_uv, tuple(lp[pivot].uv), tuple(lp[wear]),
                                    lp[weight]) for lp in face.loops}
        before = held(f)
        out = geometry.start_at_lowest(bm, [f])
        bm.verts.index_update()
        assert [v.index for v in out[0].verts] == [0, 1, 2, 3]
        assert out[0].material_index == 2
        assert held(out[0]) == before
    finally:
        bm.free()
