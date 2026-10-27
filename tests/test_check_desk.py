"""check_desk: minted 2026-10-27 by tools/new_species.py (roadmap 150), shaped for the walker's bank comps (the
factory's docs/reference/BANK_INTERIOR_COMPS.md: "a check desk island stands mid-floor ... a standing-height table with
slots for slips", comp 1's with a date block on its middle). The pure half plans it; the bpy half builds it. FAILS ON
1.134.0, which has no check desk. Run inside Blender for the shape:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_check_desk.py'])))"
"""
import pytest

from zoo_keeper.core import genome, kit


def test_check_desk_is_discovered_and_validates():
    assert "check_desk" in genome.list_species()
    assert genome.validate_genome(genome.load_species("check_desk")) == []


def _plan(dims=(1.6, 0.9, 1.1)):
    slot = {"slot_id": "check_desk_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "check_desk", "fit": {"dims": list(dims), "pivot": "center"}}
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


def test_check_desk_plans_at_its_authored_dims():
    plan = _plan()
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "check_desk"


def test_it_is_a_standing_height_desk():
    r = genome.load_species("check_desk")["dimensions"]
    assert 1.0 <= r["height"]["min"] and r["height"]["max"] <= 1.2       # a customer writes standing
    assert r["width"]["min"] >= 1.0


def _build(tmp_path, dims):
    import bpy
    from mathutils import Vector
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    m = _plan(dims)["modules"][0]
    B.build_module(m, str(tmp_path / m["stem"]), theme="delco", style=1, options={"save_blend": False})
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    return meshes, pts


@pytest.mark.parametrize("dims", [(1.0, 0.6, 1.0), (1.6, 0.9, 1.1), (3.2, 1.2, 1.2)])
def test_bpy_a_desk_is_its_slot_on_two_materials(tmp_path, dims):
    pytest.importorskip("bpy")
    meshes, pts = _build(tmp_path, dims)
    for axis, size in enumerate(dims):
        lo, hi = min(p[axis] for p in pts), max(p[axis] for p in pts)
        assert hi - lo == pytest.approx(size, abs=0.02), (axis, lo, hi)
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 2
    names = {o.name.split(".")[0] for o in meshes}
    assert {"CheckDesk_Top", "CheckDesk_Pedestal", "CheckDesk_Pockets", "CheckDesk_DateBlock",
            "CheckDesk_Paper"} <= names, names


def test_bpy_the_pedestals_keep_apart_on_a_short_desk(tmp_path):
    """At 0.8 m the fixed pedestals met in the middle (the census's first reading): they scale below 1.6 m."""
    pytest.importorskip("bpy")
    from zoo_keeper.recipes import check_desk as K
    for w in (1.0, 1.6, 3.2):
        peds = [b for name, _k, boxes, _c in K.layout(w, 0.9, 1.1) if name == "CheckDesk_Pedestal" for b in boxes]
        (a, sa), (b, sb) = peds
        assert (b[0] - sb[0] / 2.0) - (a[0] + sa[0] / 2.0) > 0.3, w
