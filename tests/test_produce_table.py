"""produce_table: minted 2026-10-26 by tools/new_species.py (roadmap 150), shaped for the walker's grocery comps (the
factory's docs/reference/GROCERY_STORE_COMPS.md: a produce section of tables of fruit and vegetables). The pure half
plans it; the bpy half builds it. FAILS ON 1.131.0, which has no produce table. Run inside Blender for the shape:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_produce_table.py'])))"
"""
import pytest

from zoo_keeper.core import genome, kit


def test_produce_table_is_discovered_and_validates():
    assert "produce_table" in genome.list_species()
    assert genome.validate_genome(genome.load_species("produce_table")) == []


def _plan(dims=(2.4, 1.2, 0.95), variant=0):
    slot = {"slot_id": "produce_table_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "produce_table", "fit": {"dims": list(dims), "pivot": "center"}}
    if variant:
        slot["variant"] = variant
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


def test_produce_table_plans_at_its_authored_dims_and_takes_a_variant():
    plan = _plan()
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "produce_table"
    g = genome.load_species("produce_table")
    assert g["module_variants"] == 8                        # `recipes/produce_table.PRODUCE`, eight kinds
    assert _plan(variant=3)["modules"][0]["stem"] != plan["modules"][0]["stem"]


def test_its_wood_is_wood():
    for name, s in genome.load_species("produce_table")["styles"].items():
        r, gr, b = s["color"]
        assert s["material"] == "wood" and r > gr > b, name


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


def test_bpy_a_table_is_its_slot_on_two_materials(tmp_path):
    pytest.importorskip("bpy")
    w, d, h = 2.4, 1.2, 0.95
    meshes, pts = _build(tmp_path, (w, d, h))
    for axis, size in ((0, w), (1, d), (2, h)):
        lo, hi = min(p[axis] for p in pts), max(p[axis] for p in pts)
        assert hi - lo == pytest.approx(size, abs=0.02), (axis, lo, hi)
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 2
    heaps = [o for o in meshes if o.name.startswith("ProduceTable_Heap")]
    assert len(heaps) == 4                                  # 2.4 m at a 0.6 m bay


def test_bpy_a_long_table_takes_more_bays(tmp_path):
    pytest.importorskip("bpy")
    meshes, _pts = _build(tmp_path, (4.2, 1.2, 0.95), variant=2)
    assert len([o for o in meshes if o.name.startswith("ProduceTable_Heap")]) == 7
