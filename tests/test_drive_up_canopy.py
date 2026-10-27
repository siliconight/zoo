"""drive_up_canopy: minted 2026-10-27 by tools/new_species.py (roadmap 150), shaped for the walker's bank list, outside
("do the drive-up lane next"). The pure half plans it and holds its variant to the bank's; the bpy half builds it.
FAILS ON 1.137.0, which has no canopy. Run inside Blender for the shape:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_drive_up_canopy.py'])))"
"""
import pytest

from zoo_keeper.core import genome, intent, kit
from zoo_keeper.core import teller_line_forms as TF

SIZES = [(4.76, 4.25, 3.655), (5.6, 5.0, 4.3), (7.84, 7.0, 6.02)]


def test_drive_up_canopy_is_discovered_validates_and_is_asked_for_by_name():
    assert "drive_up_canopy" in genome.list_species()
    g = genome.load_species("drive_up_canopy")
    assert genome.validate_genome(g) == []
    assert intent.parse("drive up canopy").species == "drive_up_canopy"
    assert g["module_variants"] == TF.VARIANTS


def _plan(dims=(5.6, 5.0, 4.3), variant=0):
    slot = {"slot_id": "drive_up_canopy_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "drive_up_canopy", "fit": {"dims": list(dims), "pivot": "center"}}
    if variant:
        slot["variant"] = variant
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


def test_drive_up_canopy_plans_at_its_dims_in_every_banks_variant():
    for v in (0, 11, 15):
        plan = _plan(variant=v)
        assert plan["species_fallbacks"] == [] and plan["modules"][0]["species"] == "drive_up_canopy"
        assert int(plan["modules"][0].get("variant") or 0) == v
        assert not plan.get("dressing_fallbacks")


@pytest.mark.parametrize("dims", SIZES)
def test_bpy_a_canopy_is_its_slot_its_fascia_the_banks_colour_its_columns_on_the_island_line(tmp_path, dims):
    pytest.importorskip("bpy")
    import bpy
    from mathutils import Vector
    from zoo_keeper.bpylayer import build as B
    from zoo_keeper.recipes import drive_up_canopy as C
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    m = _plan(dims, variant=11)["modules"][0]
    report = B.build_module(m, str(tmp_path / m["stem"]), theme="delco", style=1, options={"save_blend": False})
    assert report["report"]["status"] == "pass", report["report"]
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = [min(p[a] for p in pts) for a in range(3)]
    for axis, size in enumerate(dims):
        assert max(p[axis] for p in pts) - lo[axis] == pytest.approx(size, abs=0.02), axis
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 1
    parts = {o.name.split(".")[0]: o for o in meshes}
    # the fascia is the variant's bank colour, in the vertex colour
    deck = parts["DriveUpCanopy_Deck"]
    want = C.fascia_rgb(11)
    attr = deck.data.color_attributes.get("Wear") or deck.data.color_attributes[0]
    got = tuple(attr.data[0].color[:3])
    # the tint carries the wear's darkening (measured 0.84-0.85 of the colour, every channel alike), so the colour is
    # its direction, and the darkening one factor in wear's range
    k = [g / w for g, w in zip(got, want)]
    assert max(k) - min(k) < 0.03 and 0.6 < sum(k) / 3.0 <= 1.05, (got, want)
    # the columns stand on the island line, the run's centre where the station's tube rises to
    col = parts["DriveUpCanopy_Column"]
    cols = [col.matrix_world @ v.co for v in col.data.vertices]
    cx = (min(p.x for p in cols) + max(p.x for p in cols)) / 2.0
    assert cx == pytest.approx(C.column_x(dims[0]), abs=1e-3)
    tube = [parts["DriveUpCanopy_Tube"].matrix_world @ v.co for v in parts["DriveUpCanopy_Tube"].data.vertices]
    assert (min(p.z for p in tube) + max(p.z for p in tube)) / 2.0 - lo[2] == pytest.approx(C.run_z(dims[2]), abs=1e-3)
    # the run reaches the wall at -X
    assert min(p.x for p in tube) == pytest.approx(lo[0], abs=1e-3)
