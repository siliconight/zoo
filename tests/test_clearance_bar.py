"""clearance_bar: minted 2026-10-27 by tools/new_species.py (roadmap 150), shaped for the drive-up's research (a bank
drive-up plan's 'CLEARANCE "HEADACHE BAR"'). The pure half plans it and sets its plate; the bpy half builds it. FAILS ON
1.138.0, which has no clearance bar. Run inside Blender for the shape:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_clearance_bar.py'])))"
"""
import pytest

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import genome, intent, kit

SIZES = [(3.91, 0.212, 3.06), (4.6, 0.25, 3.6), (5.98, 0.325, 4.68)]


def test_clearance_bar_is_discovered_validates_and_is_asked_for_by_name():
    assert "clearance_bar" in genome.list_species()
    g = genome.load_species("clearance_bar")
    assert genome.validate_genome(g) == []
    assert intent.parse("clearance bar").species == "clearance_bar"
    assert intent.parse("headache bar").species == "clearance_bar"
    assert g["materials"]["default"] == "metal_painted"


def test_its_plate_sets():
    # the recipe's own figures, read from source: the recipe imports Blender
    import ast
    import os
    src = open(os.path.join(os.path.dirname(genome.__file__), "..", "recipes", "clearance_bar.py"), encoding="utf-8").read()
    c = {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse(src).body
         if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
         and n.targets[0].id in ("PLATE", "PLATE_TEXT", "PLATE_COLOURS", "CLEAR")}
    p = CA.paint({"kind": "teller_board", "w_m": c["PLATE"][0], "h_m": c["PLATE"][1], "text": c["PLATE_TEXT"],
                  "colours": c["PLATE_COLOURS"], "voice": "shop", "numbers": []})
    assert not p.unset
    assert c["CLEAR"] == pytest.approx(9 * 0.3048, abs=0.01)


def _plan(dims=(4.6, 0.25, 3.6)):
    slot = {"slot_id": "clearance_bar_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "clearance_bar", "fit": {"dims": list(dims), "pivot": "center"}}
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


def test_clearance_bar_plans_at_its_authored_dims():
    plan = _plan()
    assert plan["species_fallbacks"] == [] and plan["modules"][0]["species"] == "clearance_bar"


@pytest.mark.parametrize("dims", SIZES)
def test_bpy_a_bar_is_its_slot_its_bar_at_nine_feet(tmp_path, dims):
    pytest.importorskip("bpy")
    import bpy
    from mathutils import Vector
    from zoo_keeper.bpylayer import build as B
    from zoo_keeper.recipes import clearance_bar as CB
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    m = _plan(dims)["modules"][0]
    report = B.build_module(m, str(tmp_path / m["stem"]), theme="delco", style=1, options={"save_blend": False})
    assert report["report"]["status"] == "pass", report["report"]
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = [min(p[a] for p in pts) for a in range(3)]
    for axis, size in enumerate(dims):
        assert max(p[axis] for p in pts) - lo[axis] == pytest.approx(size, abs=0.02), axis
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 2
    # the plate faces the lane's entry (-Y) at the bar's height
    plate = [o for o in meshes if o.name.startswith("ClearanceBar_Plate")]
    assert plate
    zs = [(o.matrix_world @ v.co).z - lo[2] for o in plate for v in o.data.vertices]
    assert min(zs) < CB.CLEAR + CB.BAR / 2.0 < max(zs)
