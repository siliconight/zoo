"""wall_clock: minted 2026-10-27 by tools/new_species.py (roadmap 150), shaped for the walker's bank comps (the
factory's docs/reference/BANK_INTERIOR_COMPS.md: "a date clock over the line (2, 4), a wall clock"). The pure half plans
it; the bpy half builds it. FAILS ON 1.135.0, which has no wall clock. Run inside Blender for the shape:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_wall_clock.py'])))"
"""
import pytest

from zoo_keeper.core import genome, intent, kit


def test_wall_clock_is_discovered_validates_and_is_asked_for_by_name():
    assert "wall_clock" in genome.list_species()
    g = genome.load_species("wall_clock")
    assert genome.validate_genome(g) == []
    assert intent.parse("wall clock").species == "wall_clock"
    # hung on a wall, out of reach: no collision
    assert g["collision"] is False and g["connectors"]["anchor"]["type"] == "wall"


def _plan(dims=(0.36, 0.06, 0.36)):
    slot = {"slot_id": "wall_clock_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "wall_clock", "fit": {"dims": list(dims), "pivot": "center"}}
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


def test_wall_clock_plans_at_its_authored_dims():
    plan = _plan()
    assert plan["species_fallbacks"] == [] and plan["modules"][0]["species"] == "wall_clock"


@pytest.mark.parametrize("dims", [(0.25, 0.04, 0.25), (0.36, 0.06, 0.36), (0.5, 0.1, 0.5)])
def test_bpy_a_clock_is_its_slot_on_one_material_its_face_toward_the_room(tmp_path, dims):
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
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 1
    # the hands and marks stand in front of the face, toward -Y, the room
    front = {o.name.split(".")[0]: min((o.matrix_world @ v.co).y for v in o.data.vertices) for o in meshes}
    assert front["WallClock_Ink"] < front["WallClock_Face"]
