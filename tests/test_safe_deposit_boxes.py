"""safe_deposit_boxes module tests.

A vault-room wall of deposit boxes: a solid backing whose front is the doors, a capped bordered frame of dividers, and
(1.140.0, the walker's bank comp 12) a brass lock and a number plate on every door, larger boxes in the bottom rows,
and a few boxes drawn. Tests: the layout defines the exact (w, d, h) envelope and stays inside it; the grid is capped
so a big wall stays within its budget; every door has its hardware or is drawn; a slot's `drilled` state defers to
the intact base; and, built, the wall is one material with no two faces on one plane.

FAILS ON 1.139.0: `core.deposit_boxes` does not exist, the wall is `metal` (delco_1997's street rust), and its frame's
crossings are 884 coincident pairs.
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import deposit_boxes as db
from zoo_keeper.core import dna, genome, kit, validate


def _bbox(parts):
    lo, hi = [1e9] * 3, [-1e9] * 3
    for _name, boxes, _rgb in parts:
        for c, s in boxes:
            for i in range(3):
                lo[i] = min(lo[i], c[i] - s[i] / 2.0)
                hi[i] = max(hi[i], c[i] + s[i] / 2.0)
    return lo, hi


def _parts(parts):
    return {name: boxes for name, boxes, _rgb in parts}


@pytest.mark.parametrize("dims", [(2.0, 0.3, 2.4), (3.6, 0.4, 3.0), (0.8, 0.2, 1.2), (5.0, 0.6, 3.6),
                                  (0.6, 0.15, 0.8)])
def test_the_layout_is_exactly_the_slot(dims):
    w, d, h = dims
    lo, hi = _bbox(db.layout(w, d, h, {}, 7))
    for i, size in enumerate(dims):
        assert hi[i] - lo[i] == pytest.approx(size, abs=1e-9), (dims, i)
        assert (lo[i] + hi[i]) / 2.0 == pytest.approx(0.0, abs=1e-9), (dims, i)


def test_the_grid_is_capped_so_a_big_wall_stays_in_its_budget():
    budget = genome.load_species("safe_deposit_boxes")["budgets"]["tris_lod0"]
    parts = db.layout(5.0, 0.6, 3.6, {"cell": 0.1}, 7)
    n = sum(len(b) for _n, b, _c in parts)
    p = _parts(parts)
    # the frame is capped at 16 columns and 16 rows, as before
    assert len(p["SafeDepositBoxes_Divider"]) <= 17 + 17
    # twelve triangles a box, the backing's bevel at most another hundred
    assert n * 12 + 100 <= budget, (n, budget)


@pytest.mark.parametrize("dims", [(2.0, 0.3, 2.4), (0.8, 0.2, 1.2), (5.0, 0.6, 3.6)])
def test_every_door_has_a_lock_and_a_plate_or_is_drawn(dims):
    parts = _parts(db.layout(*dims, {}, 11))
    doors = db.cells(dims[0], dims[2], {})
    locks, plates = parts["SafeDepositBoxes_Lock"], parts["SafeDepositBoxes_Plate"]
    drawn = parts["SafeDepositBoxes_Drawn"]
    assert len(locks) == len(plates) == len(doors) - len(drawn)
    assert 1 <= len(drawn) <= db.DRAWN_MAX
    # the hardware stands proud of the doors and inside the frame's front
    front = dims[1] / 2.0
    for c, s in locks + plates + drawn:
        assert c[1] + s[1] / 2.0 < front - 0.005
    # a lock is on the door's right as its renter faces it (-x: the doors face +y), the plate on its upper left
    for (_i, _j, x0, z0, x1, z1), lock in zip([c for k, c in enumerate(doors)
                                              if k not in db.drawn(len(doors), 11)], locks):
        assert x0 <= lock[0][0] - lock[1][0] / 2.0 and lock[0][0] < (x0 + x1) / 2.0


def test_the_bottom_rows_are_the_large_boxes():
    uw, uh, cols, rows, _m, _b = db.grid(2.0, 2.4, {})
    zs = db.row_bounds(uh, rows)
    heights = [b - a for a, b in zip(zs, zs[1:])]
    assert heights[0] == pytest.approx(2.0 * heights[-1])
    assert heights[db.LARGE_ROWS] == pytest.approx(heights[-1])
    # a short wall keeps its rows
    _uw, uh2, _c, rows2, _m2, _b2 = db.grid(0.8, 0.6, {})
    assert len(db.row_bounds(uh2, rows2)) == rows2 + 1


def test_which_boxes_are_drawn_is_the_seeds():
    assert db.drawn(90, 3) == db.drawn(90, 3)
    assert db.drawn(90, 3) != db.drawn(90, 4)
    assert len(db.drawn(1, 0)) == 1


def test_the_wall_is_painted_steel():
    # bare until 1.142.0: lit by the bake, the wall read near black (the factory's docs/findings/bank_interior/,
    # frame 18), as the vault door did before it went painted (the factory's roadmap, item 46)
    g = genome.load_species("safe_deposit_boxes")
    assert g["materials"] == {"default": "metal_painted", "options": ["metal_painted", "laminate"]}
    assert {st["material"] for st in g["styles"].values()} <= {"metal_painted", "laminate"}
    for name, st in g["styles"].items():
        if st["material"] == "metal_painted":
            # the steel reads light: the brass locks and plates in the vertex are lighter still, the drawn cells dark
            assert sum(st["color"]) / 3.0 >= 0.53, (name, st["color"])


def test_plan_is_exact_fit_and_validates():
    g = genome.load_species("safe_deposit_boxes")
    m = {"type": "safe_deposit_boxes", "species": "safe_deposit_boxes",
         "state": None, "width_cm": 200, "fit": "exact",
         "dims": [2.0, 0.3, 2.4], "pivot": "center",
         "stem": "safe_deposit_boxes_delco_01_w200"}
    plan = dna.resolve_module_plan(m, g, "delco", 1, TOOL_VERSION)
    assert plan["pivot"] == "center" and plan["fit_exact"] is True
    assert plan["material"] == "metal_painted"
    parts = db.layout(2.0, 0.3, 2.4, plan["params"], 1)
    lo, hi = _bbox(parts)
    facts = {"dimensions": {"width": round(hi[0] - lo[0], 4),
                            "depth": round(hi[1] - lo[1], 4),
                            "height": round(hi[2] - lo[2], 4)},
             "tris": 12 * sum(len(b) for _n, b, _c in parts), "parts": [n for n, _b, _c in parts],
             "has_uvs": True, "has_wear_colors": True,
             "materials": ["M_SafeDepositBoxes_metal_painted"], "has_collision": True,
             "unapplied_transforms": []}
    report = validate.evaluate(facts, g, plan, {"collision": True})
    assert report["status"] == "pass", validate.summarize(report)


def test_drilled_state_defers_to_intact_base():
    slot = {"role": "safe_deposit_boxes", "size_mod": "full",
            "fit": {"dims": [2.0, 0.3, 2.4], "pivot": "center"},
            "interactive": {"id": "b:if:s1", "kind": "safe_deposit_boxes",
                            "states": ["intact", "drilled"],
                            "default": "intact"}}
    plan = kit.plan_kit({"building_id": "b", "slots": [slot]})
    stems = {m["stem"] for m in plan["modules"]}
    assert "safe_deposit_boxes_delco_01_w200" in stems
    assert "safe_deposit_boxes_delco_01_w200_drilled" not in stems
    deferred = {d["stem"] for d in plan["deferred_variants"]}
    assert "safe_deposit_boxes_delco_01_w200_drilled" in deferred


def test_bpy_the_wall_is_its_slot_in_one_material(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from mathutils import Vector
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    slot = {"slot_id": "sdb_0", "role": "safe_deposit_boxes", "size_mod": "full", "style": 1,
            "fit": {"dims": [2.0, 0.3, 2.4], "pivot": "center"}}
    m = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)["modules"][0]
    B.build_module(m, str(tmp_path / m["stem"]), theme="delco", style=1, options={"save_blend": False})
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    for axis, size in enumerate((2.0, 0.3, 2.4)):
        lo, hi = min(p[axis] for p in pts), max(p[axis] for p in pts)
        assert hi - lo == pytest.approx(size, abs=0.01), (axis, lo, hi)
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 1
