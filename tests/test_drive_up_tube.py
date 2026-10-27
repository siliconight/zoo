"""drive_up_tube: minted 2026-10-27 by tools/new_species.py (roadmap 150), shaped for the walker's bank list, outside
(the factory's docs/reference/BANK_INTERIOR_COMPS.md: "a drive-up lane with a pneumatic tube"). The pure half plans it;
the bpy half builds it. FAILS ON 1.137.0, which has no drive-up station. Run inside Blender for the shape:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_drive_up_tube.py'])))"
"""
import pytest

from zoo_keeper.core import genome, intent, kit

SIZES = [(0.81, 0.72, 2.88), (0.9, 0.8, 3.2), (1.125, 1.0, 4.0)]


def test_drive_up_tube_is_discovered_validates_and_is_asked_for_by_name():
    assert "drive_up_tube" in genome.list_species()
    g = genome.load_species("drive_up_tube")
    assert genome.validate_genome(g) == []
    assert intent.parse("drive up tube").species == "drive_up_tube"
    assert intent.parse("pneumatic tube").species == "drive_up_tube"
    assert g["connectors"]["anchor"]["type"] == "floor" and g["collision"] is True


def _plan(dims=(0.9, 0.8, 3.2)):
    slot = {"slot_id": "drive_up_tube_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "drive_up_tube", "fit": {"dims": list(dims), "pivot": "center"}}
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


def test_drive_up_tube_plans_at_its_authored_dims():
    plan = _plan()
    assert plan["species_fallbacks"] == [] and plan["modules"][0]["species"] == "drive_up_tube"


@pytest.mark.parametrize("dims", SIZES)
def test_bpy_a_station_is_its_slot_on_one_material_its_receptacle_at_a_car_window(tmp_path, dims):
    pytest.importorskip("bpy")
    import bpy
    from mathutils import Vector
    from zoo_keeper.bpylayer import build as B
    from zoo_keeper.recipes import drive_up_tube as DU
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    m = _plan(dims)["modules"][0]
    report = B.build_module(m, str(tmp_path / m["stem"]), theme="delco", style=1, options={"save_blend": False})
    assert report["report"]["status"] == "pass", report["report"]
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = [min(p[a] for p in pts) for a in range(3)]
    for axis, size in enumerate(dims):
        hi = max(p[axis] for p in pts)
        assert hi - lo[axis] == pytest.approx(size, abs=0.02), (axis, lo[axis], hi)
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 1
    parts = {o.name.split(".")[0]: o for o in meshes}
    mouth = [parts["DriveUp_Mouth"].matrix_world @ v.co for v in parts["DriveUp_Mouth"].data.vertices]
    # the receptacle's sill a car window's height over the ground, and its face toward the lane (-Y) of the cabinet's
    assert min(p.z for p in mouth) - lo[2] == pytest.approx(DU.REC_SILL + 0.004, abs=1e-3)
    cab = [parts["DriveUp_Cabinet"].matrix_world @ v.co for v in parts["DriveUp_Cabinet"].data.vertices]
    assert min(p.y for p in mouth) < min(p.y for p in cab)
