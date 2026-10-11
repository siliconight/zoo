"""`geometry.add_hemisphere` keeps the upper half it names, every vertex scaled (1.99.1).

Until 1.99.1 the helper's bisect pointed its plane normal down, and
`clear_inner` clears the side behind the normal, so it kept the LOWER half:
measured in Blender 5.1.1 at radii (0.5, 0.5, 0.3), z -0.3 .. 0 at every ring
count, the mean face normal z -0.74. Each caller lays it as a cap on top, so
each cap hung inside its own body -- the bollard flat-topped, the exhaust
fan's hood a bowl around its drum (the fan 0.385 m tall in a 0.55 m slot),
the soda cup's lid dome under its lid, the helmet's shell below its rim. And
at an odd ring count (`segments` 14 asks for 7 rings) no ring lies on the
cut, the bisect makes the rim's vertices new, and they were left out of the
transform: 14 vertices at radius 0.975 on a hemisphere asked for at 0.5. The
probes are `docs/findings/hemisphere_half/` in the factory.

The pure half reads the helper. The bpy half builds hemispheres, and the four
capped species the way a kit build does, and reads the meshes; it skips
without Blender and was run inside Blender 5.1.1 for this change, from the
repo root:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_hemisphere.py'])))"
"""

import ast
import json
import math
import os

import pytest

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GEOMETRY = os.path.join(_ZOO, "zoo_keeper", "bpylayer", "geometry.py")
_SPECIES = os.path.join(_ZOO, "zoo_keeper", "genome", "species")

#: Each caller's cap, by the object it lands in.
_CAPS = {"bollard": "Bollard_Pipe", "exhaust_fan": "ExhaustFan_Dome",
         "soda_cup": "Cup_LidDome", "helmet": "Helmet_Shell"}


def _helper():
    tree = ast.parse(open(_GEOMETRY, encoding="utf-8").read())
    return next(n for n in tree.body
                if isinstance(n, ast.FunctionDef) and n.name == "add_hemisphere")


def test_the_bisect_clears_the_lower_side_and_scales_its_cut():
    fn = _helper()
    calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == "bisect_plane"]
    assert len(calls) == 1, len(calls)
    kw = {k.arg: k.value for k in calls[0].keywords}
    # clear_inner clears the side BEHIND the normal: an upward normal keeps the top
    assert ast.literal_eval(kw["plane_no"]) == (0, 0, 1)
    assert ast.literal_eval(kw["clear_inner"]) is True
    assert "clear_outer" not in kw
    body = ast.unparse(fn)
    assert "geom_cut" in body            # the rim the bisect makes is scaled too
    assert " or [" not in body           # and nothing falls back to every vertex in the bmesh


@pytest.mark.parametrize("segments", [10, 12, 14, 20])
def test_bpy_the_hemisphere_is_the_upper_half_with_every_vertex_scaled(segments):
    pytest.importorskip("bpy")
    import bmesh
    from zoo_keeper.bpylayer import geometry
    rx, rz = 0.5, 0.3
    bm = bmesh.new()
    try:
        ret = geometry.add_hemisphere(bm, (0.0, 0.0, 0.0), rx, rx, rz, segments=segments)
        assert len(ret) == len(bm.verts), (len(ret), len(bm.verts))
        zs = [v.co.z for v in bm.verts]
        assert min(zs) == pytest.approx(0.0, abs=1e-6), min(zs)
        assert max(zs) == pytest.approx(rz, abs=1e-6), max(zs)
        far = max(math.hypot(v.co.x, v.co.y) for v in bm.verts)
        assert far <= rx + 1e-6, far
        bm.normal_update()
        assert sum(f.normal.z for f in bm.faces) / len(bm.faces) > 0.5
    finally:
        bm.free()


def _build(tmp_path, species):
    """One `prop` slot at the genome's default corner, planned and built the
    way a `zoo_kit_build` job builds it (the coplanar census's path)."""
    import bpy
    from zoo_keeper.bpylayer import build, materials
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    materials.set_skin_library(None)
    with open(os.path.join(_SPECIES, species + ".json"), encoding="utf-8") as f:
        g = json.load(f)
    dims = [float(g["dimensions"][k]["default"]) for k in ("width", "depth", "height")]
    slot = {"slot_id": species + "_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": species, "fit": {"dims": dims, "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "hemisphere_test", "slots": [slot]},
                        theme="delco_1997", style=1)
    mod = plan["modules"][0]
    assert mod.get("species") == species, mod.get("species")
    build.build_module(mod, str(tmp_path / "out"), theme="delco_1997", style=1,
                       options={"save_blend": False})
    return dims, [o for o in bpy.data.objects if o.type == "MESH"
                  and not o.name.endswith(_COL_SUFFIXES) and "_LOD" not in o.name]


def _points(objs):
    return [o.matrix_world @ v.co for o in objs for v in o.data.vertices]


@pytest.mark.parametrize("species", sorted(_CAPS))
def test_bpy_each_cap_crowns_its_body(tmp_path, species):
    """A dome's top is its pole; a flat top or a bowl's rim reaches the full
    radius. Read about the cap's own vertical axis, within 1 mm of its top."""
    pytest.importorskip("bpy")
    _dims, objs = _build(tmp_path, species)
    cap = [o for o in objs if _CAPS[species] in o.name]
    assert len(cap) == 1, sorted(o.name for o in objs)
    pts = _points(cap)
    xs, ys = [p.x for p in pts], [p.y for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    half = max(max(xs) - cx, max(ys) - cy)
    top = max(p.z for p in pts)
    reach = max(math.hypot(p.x - cx, p.y - cy) for p in pts if p.z > top - 1e-3)
    assert reach < 0.5 * half, (species, round(reach, 4), round(half, 4))


@pytest.mark.parametrize("species", ["bollard", "exhaust_fan"])
def test_bpy_a_capped_body_stands_its_slots_full_height(tmp_path, species):
    """The exhaust fan stood 0.385 m in a 0.55 m slot while its hood hung
    around its drum; the bollard keeps its height with the cap inside it."""
    pytest.importorskip("bpy")
    (_w, _d, h), objs = _build(tmp_path, species)
    zs = [p.z for p in _points(objs)]
    assert max(zs) - min(zs) == pytest.approx(h, abs=1e-4), (species, max(zs) - min(zs), h)
