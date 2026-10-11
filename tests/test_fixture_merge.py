"""A fixture's same-material parts are one mesh, inside it and never across two (1.100.0).

Roadmap 233. A building's fixtures ship as one GLB of many placements -- a
layer, not a module -- and until 1.100.0 it was exported unmerged, so a
fixture whose parts share a material paid a submission a part. Built from
1.99.0's genomes at their default corner, a streetlight is a pole, a base and
a head in one metal (three meshes where one carries them), a pendant a cord
and a socket, a wall pack an arm and a body, a sign box its arms and its
cabinet (`docs/findings/fixture_merge/parts_probe.py` in the factory).
`merge.pack_by_material` takes each part's placement now and merges a
placement's parts by material inside it, so each fixture stays its own
culling unit and sheds the submissions its extra parts cost.

The pure half reads the wiring. The bpy half builds a layer both ways from one
manifest and reads the GLBs; it skips without Blender and was run inside
Blender 5.1.1 for this change, from the repo root:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_fixture_merge.py'])))"
"""

import ast
import json
import os
import struct

import pytest

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BUILD = os.path.join(_ZOO, "zoo_keeper", "bpylayer", "build.py")
_EXPORT = os.path.join(_ZOO, "zoo_keeper", "bpylayer", "export.py")


def _function(path, name):
    tree = ast.parse(open(path, encoding="utf-8").read())
    return next(n for n in tree.body
                if isinstance(n, ast.FunctionDef) and n.name == name)


def _calls(fn, attr):
    return [n for n in ast.walk(fn) if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute) and n.func.attr == attr]


def test_the_fixtures_layer_is_exported_merged_by_placement():
    calls = _calls(_function(_BUILD, "build_fixtures"), "export_glb")
    assert len(calls) == 1, len(calls)
    kw = {k.arg: ast.unparse(k.value) for k in calls[0].keywords}
    assert kw.get("units") == "units", kw
    assert kw.get("merge_parts") == "opts['merge_parts']", kw


def test_the_exporter_hands_the_units_to_the_merge():
    calls = _calls(_function(_EXPORT, "export_glb"), "pack_by_material")
    assert len(calls) == 1, len(calls)
    kw = {k.arg: ast.unparse(k.value) for k in calls[0].keywords}
    assert kw.get("units") == "units", kw


# --- bpy: what a layer ships --------------------------------------------------

def _anchor(aid, kind, pos, rot, count, spacing):
    return {"id": aid, "type": kind, "source": "derived", "pos": list(pos),
            "rot_y": rot, "row": {"count": count, "spacing": spacing},
            "reacts_to_alarm": False}


def _manifest():
    """Two pendants, two streetlights and a wall pack: five placements."""
    return {"light_manifest_version": "1.2.0", "building_id": "merge_bpy",
            "space": "Blender Z-up, meters", "anchors": [
                _anchor("counter", "pendant", (0.0, 0.0, 3.2), 0.0, 2, 2.0),
                _anchor("site/lane_lights", "streetlight", (10.0, 0.0, 6.0), 90.0, 2, 10.0),
                _anchor("rear_pack", "wall_pack", (-6.0, 4.0, 3.0), 180.0, 1, 0.0)]}


def _gltf(path):
    raw = open(path, "rb").read()
    assert raw[:4] == b"glTF"
    ln, kind = struct.unpack_from("<I4s", raw, 12)
    assert kind == b"JSON"
    return json.loads(raw[20:20 + ln])


def _build(tmp_path, merge):
    from zoo_keeper.bpylayer import build
    out = str(tmp_path / ("merged" if merge else "parts"))
    build.build_fixtures(_manifest(), out, theme="delco",
                         options={"save_blend": False, "merge_parts": merge})
    with open(os.path.join(out, "merge_bpy_fixtures.built.json"), encoding="utf-8") as fh:
        index = json.load(fh)
    return index, _gltf(os.path.join(out, index["files"]["glb"]))


def _drawn(j):
    """[(node name, material name, translation)] -- one per submission: a
    visual mesh node's every primitive. Colliders are not drawn."""
    mats = [m.get("name", "") for m in j.get("materials", [])]
    out = []
    for n in j["nodes"]:
        if "mesh" not in n or "colonly" in n["name"].lower():
            continue
        t = tuple(round(v, 4) for v in n.get("translation", (0.0, 0.0, 0.0)))
        for prim in j["meshes"][n["mesh"]]["primitives"]:
            out.append((n["name"], mats[prim["material"]] if "material" in prim else "", t))
    return out


def _by_family(drawn):
    """{(family, lens or not): submissions}: `M_Pendant_*` metal and
    `M_Pendant_Lens` apart, whatever the theme names the metal."""
    out = {}
    for _n, mat, _t in drawn:
        fam = mat[2:].split("_", 1)[0] if mat.startswith("M_") else mat
        key = (fam, mat.endswith("_Lens"))
        out[key] = out.get(key, 0) + 1
    return out


def test_bpy_a_fixtures_parts_merge_inside_it_and_never_across_two(tmp_path):
    pytest.importorskip("bpy")
    _ip, parts = _build(tmp_path, False)
    im, merged = _build(tmp_path, True)
    a, b = _by_family(_drawn(parts)), _by_family(_drawn(merged))
    # one placement, one mesh a material
    assert (a[("Pendant", False)], b[("Pendant", False)]) == (4, 2), (a, b)
    assert (a[("Streetlight", False)], b[("Streetlight", False)]) == (6, 2), (a, b)
    assert (a[("WallPack", False)], b[("WallPack", False)]) == (2, 1), (a, b)
    # a lens is the only part in its material: it ships as itself
    for fam in ("Pendant", "Streetlight", "WallPack"):
        assert a[(fam, True)] == b[(fam, True)], fam
    assert len(_drawn(parts)) - len(_drawn(merged)) == 2 + 4 + 1
    assert im["merge"]["merged"] == 5 and im["merge"]["units"] == 5, im["merge"]


def test_bpy_each_merged_mesh_stands_where_its_parts_stood(tmp_path):
    pytest.importorskip("bpy")
    _ip, parts = _build(tmp_path, False)
    _im, merged = _build(tmp_path, True)
    for fam in ("Pendant", "Streetlight", "WallPack"):
        def spots(j):
            return sorted({t for _n, mat, t in _drawn(j)
                           if mat.startswith("M_" + fam) and not mat.endswith("_Lens")})
        assert spots(parts) == spots(merged), fam


def test_bpy_every_marker_rides_out_beside_its_hardware(tmp_path):
    pytest.importorskip("bpy")
    ip, parts = _build(tmp_path, False)
    im, merged = _build(tmp_path, True)

    def marks(j):
        return sorted((n["name"], tuple(round(v, 4) for v in n.get("translation", (0, 0, 0))))
                      for n in j["nodes"] if n["name"].startswith("LuxEmit"))
    assert marks(parts) == marks(merged)
    assert len(marks(merged)) == im["emitter_markers"] == ip["emitter_markers"] == 5


def test_bpy_a_unit_whose_parts_disagree_on_their_frame_is_not_merged():
    pytest.importorskip("bpy")
    import bmesh
    import bpy
    from mathutils import Matrix
    from zoo_keeper.bpylayer import merge
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    coll = bpy.data.collections.new("units_bpy")
    bpy.context.scene.collection.children.link(coll)
    mat = bpy.data.materials.new("M_Test_metal")
    for k, x in enumerate((2.0, 2.0, 5.0)):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=0.2)
        me = bpy.data.meshes.new("Test_Part%d" % k)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        obj = bpy.data.objects.new("Test_Part%d" % k, me)
        coll.objects.link(obj)
        obj.matrix_world = Matrix.Translation((x, 0.0, 0.0))
    packed = merge.pack_by_material(
        coll, units={"Test_Part0": 0, "Test_Part1": 0, "Test_Part2": 0})
    try:
        assert packed.stats["refused"] == [("Test_Part2", "transform differs from its unit's")]
        assert packed.stats["merged"] == 1
        made = [o for o in packed.objects if o.name not in ("Test_Part0", "Test_Part1", "Test_Part2")]
        assert len(made) == 1
        assert tuple(round(v, 6) for v in made[0].matrix_world.translation) == (2.0, 0.0, 0.0)
    finally:
        packed.discard()
