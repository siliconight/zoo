"""planter: minted 2026-10-27 by tools/new_species.py (roadmap 150), shaped for the walker's bank comps (the factory's
docs/reference/BANK_INTERIOR_COMPS.md: plants in planters by the windows and counters in comps 1, 4, 5 and 6). The
pure half plans it; the bpy half builds it. FAILS ON 1.135.0, which has no planter. Run inside Blender for the shape:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_planter.py'])))"
"""
import pytest

from zoo_keeper.core import genome, intent, kit


def test_planter_is_discovered_validates_and_is_asked_for_by_name():
    assert "planter" in genome.list_species()
    assert genome.validate_genome(genome.load_species("planter")) == []
    assert intent.parse("potted plant").species == "planter"


def _plan(dims=(0.6, 0.6, 1.5), variant=0):
    slot = {"slot_id": "planter_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "planter", "fit": {"dims": list(dims), "pivot": "center"}}
    if variant:
        slot["variant"] = variant
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


def test_planter_plans_and_its_variant_is_the_plant():
    plan = _plan()
    assert plan["species_fallbacks"] == [] and plan["modules"][0]["species"] == "planter"
    assert genome.load_species("planter")["module_variants"] == 4
    assert _plan(variant=2)["modules"][0]["stem"] != plan["modules"][0]["stem"]


def _build(tmp_path, dims, variant=0):
    import bpy
    from mathutils import Vector
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    m = _plan(dims, variant)["modules"][0]
    B.build_module(m, str(tmp_path / m["stem"]), theme="delco", style=1, options={"save_blend": False})
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    return meshes, pts


@pytest.mark.parametrize("dims,variant", [((0.4, 0.4, 0.8), 0), ((0.6, 0.6, 1.5), 2), ((0.9, 0.9, 2.0), 3)])
def test_bpy_a_planter_is_its_slot_on_two_materials_with_soil_showing(tmp_path, dims, variant):
    pytest.importorskip("bpy")
    meshes, pts = _build(tmp_path, dims, variant)
    for axis, size in enumerate(dims):
        lo, hi = min(p[axis] for p in pts), max(p[axis] for p in pts)
        assert hi - lo == pytest.approx(size, abs=0.02), (axis, lo, hi)
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 2
    names = {o.name.split(".")[0] for o in meshes}
    assert {"Planter_Pot", "Planter_Lip", "Planter_Soil", "Planter_Stems", "Planter_Leaves"} <= names, names
    # the soil stands above the pot's solid: the first cut capped the pot and buried it
    top = {o.name.split(".")[0]: max((o.matrix_world @ v.co).z for v in o.data.vertices) for o in meshes}
    assert top["Planter_Soil"] > top["Planter_Pot"]
