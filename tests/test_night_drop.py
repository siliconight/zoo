"""night_drop: minted 2026-10-27 by tools/new_species.py (roadmap 150), shaped for the walker's bank list, outside (the
factory's docs/reference/BANK_INTERIOR_COMPS.md: "a night depository is a slot in the wall for after-hours deposits").
The pure half plans it and sets its lettering; the bpy half builds it. FAILS ON 1.137.0, which has no night drop. Run
inside Blender for the shape:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_night_drop.py'])))"
"""
import pytest

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import genome, intent, kit
from zoo_keeper.core import night_drop_forms as ND

SIZES = [(0.582, 0.145, 0.873), (0.6, 0.15, 0.9), (0.78, 0.195, 1.17)]


def test_night_drop_is_discovered_validates_and_is_asked_for_by_name():
    assert "night_drop" in genome.list_species()
    g = genome.load_species("night_drop")
    assert genome.validate_genome(g) == []
    assert intent.parse("night drop").species == "night_drop"
    assert intent.parse("night depository").species == "night_drop"
    assert g["connectors"]["anchor"]["type"] == "wall"


def _plan(dims=(0.6, 0.15, 0.9)):
    slot = {"slot_id": "night_drop_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "night_drop", "fit": {"dims": list(dims), "pivot": "center"}}
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


def test_night_drop_plans_at_its_authored_dims():
    plan = _plan()
    assert plan["species_fallbacks"] == [] and plan["modules"][0]["species"] == "night_drop"


@pytest.mark.parametrize("dims", SIZES)
def test_the_lettering_sets_at_every_size_and_stays_on_the_plate(dims):
    """NIGHT DEPOSITORY sets at 0.52 x 0.18 m in the shop voice and not at
    0.16: the genome's narrowest plate leaves the label 0.522 m."""
    w, d, h = dims
    x0, x1, z0, z1, y = ND.label_box(w, d, h)
    c = CA.paint({"kind": "teller_board", "w_m": x1 - x0, "h_m": z1 - z0, "text": ND.LABEL_TEXT,
                  "colours": ND.LABEL_COLOURS, "voice": "shop", "numbers": []})
    assert not c.unset, (dims, c.unset)
    assert -w / 2 < x0 < x1 < w / 2 and -h / 2 < z0 < z1 < h / 2 and -d / 2 < y < d / 2


def test_the_genomes_narrowest_plate_still_sets_its_lettering():
    g = genome.load_species("night_drop")
    x0, x1, _z0, _z1, _y = ND.label_box(g["dimensions"]["width"]["min"], 0.15, 0.9)
    assert x1 - x0 >= 0.52


@pytest.mark.parametrize("dims", SIZES)
def test_bpy_a_night_drop_is_its_slot_its_door_and_pull_toward_the_street(tmp_path, dims):
    pytest.importorskip("bpy")
    import bpy
    from mathutils import Vector
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    m = _plan(dims)["modules"][0]
    B.build_module(m, str(tmp_path / m["stem"]), theme="delco", style=1, options={"save_blend": False})
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    for axis, size in enumerate(dims):
        lo, hi = min(p[axis] for p in pts), max(p[axis] for p in pts)
        assert hi - lo == pytest.approx(size, abs=0.02), (axis, lo, hi)
    # the steel on one material and the lettering on its own: two submissions
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 2
    front = {o.name.split(".")[0]: min((o.matrix_world @ v.co).y for v in o.data.vertices) for o in meshes}
    names = set(front)
    for part in ("NightDrop_Plate", "NightDrop_Hood", "NightDrop_Door", "NightDrop_Handle", "NightDrop_Lock"):
        assert part in names, (part, sorted(names))
    # the pull is the front, then the door, the hood, the plate
    assert front["NightDrop_Handle"] < front["NightDrop_Door"] < front["NightDrop_Hood"] < front["NightDrop_Plate"]
