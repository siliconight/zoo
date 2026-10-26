"""pew: minted 2026-10-25 by tools/new_species.py (roadmap 150), shaped for the factory's roadmap 308 (a chapel, a
viewing room, a courtroom's public benches and an assembly room furnished as a cafeteria, for want of a seat that faces
one front). The pure half plans it; the bpy half builds it. FAILS ON 1.129.0, which has no pew. Run inside Blender for
the shape:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_pew.py'])))"
"""
import pytest

from zoo_keeper.core import genome, kit


def test_pew_is_discovered_and_validates():
    assert "pew" in genome.list_species()
    assert genome.validate_genome(genome.load_species("pew")) == []


def _plan(dims=(3.6, 0.62, 0.95)):
    return kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "pew_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "pew",
        "fit": {"dims": list(dims), "pivot": "center"}}]},
        theme="delco", style=1)


def test_pew_plans_at_its_authored_dims():
    plan = _plan()
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "pew"


def test_a_pew_is_one_stained_wood():
    """One material, so a row of pews is one mesh to the merge: every style plans wood, in an oak's brown."""
    g = genome.load_species("pew")
    for name, s in g["styles"].items():
        r, gr, b = s["color"]
        assert s["material"] == "wood" and r > gr > b, name


def test_bpy_a_pew_is_its_slot_with_a_seat_a_back_and_a_rack(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from mathutils import Vector
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    w, d, h = 3.6, 0.62, 0.95
    m = _plan((w, d, h))["modules"][0]
    B.build_module(m, str(tmp_path / m["stem"]), theme="delco", style=1, options={"save_blend": False})
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")]
    names = sorted(o.name.split(".")[0] for o in meshes)
    assert names == sorted(["Pew_End_L", "Pew_End_R", "Pew_Seat", "Pew_Back", "Pew_TopRail", "Pew_Rack"]), names
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    for axis, size in ((0, w), (1, d), (2, h)):
        lo, hi = min(p[axis] for p in pts), max(p[axis] for p in pts)
        assert hi - lo == pytest.approx(size, abs=1e-3), (axis, lo, hi)
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 1

    def box(name):
        o = next(o for o in meshes if o.name.startswith(name))
        q = [o.matrix_world @ Vector(c) for c in o.bound_box]
        return [min(p[i] for p in q) for i in range(3)], [max(p[i] for p in q) for i in range(3)]
    (slo, shi), (blo, bhi), (rlo, rhi) = box("Pew_Seat"), box("Pew_Back"), box("Pew_Rack")
    assert shi[2] == pytest.approx(-h / 2.0 + 0.45, abs=0.01)          # a seat 0.45 m up
    assert slo[1] == pytest.approx(-d / 2.0, abs=0.01) and blo[1] < shi[1] <= bhi[1]   # sat on from the front, into the back
    assert bhi[2] > shi[2] + 0.35                                    # a back to lean on
    assert blo[1] <= rlo[1] < bhi[1] < rhi[1] <= d / 2.0                 # the rack behind, for the next row
    assert shi[1] - slo[1] < 0.5                                             # a seat a pew's depth


def test_bpy_a_deep_slot_keeps_the_seat_and_gains_a_kneeler(tmp_path):
    """The funeral home's authored `pew_row` boxes are 0.9 m deep: the seat stays a seat, the rest is a kneeler."""
    pytest.importorskip("bpy")
    import bpy
    from mathutils import Vector
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    w, d, h = 8.0, 0.9, 0.9
    m = _plan((w, d, h))["modules"][0]
    assert m["species"] == "pew"
    B.build_module(m, str(tmp_path / m["stem"]), theme="delco", style=1, options={"save_blend": False})
    meshes = {o.name.split(".")[0]: o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")}
    assert "Pew_Kneeler" in meshes, sorted(meshes)
    q = [meshes["Pew_Seat"].matrix_world @ Vector(c) for c in meshes["Pew_Seat"].bound_box]
    assert max(p[1] for p in q) - min(p[1] for p in q) < 0.5
    k = [meshes["Pew_Kneeler"].matrix_world @ Vector(c) for c in meshes["Pew_Kneeler"].bound_box]
    assert max(p[2] for p in k) < -h / 2.0 + 0.25 and max(p[1] for p in k) > d / 2.0 - 0.01
