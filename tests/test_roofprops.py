"""Tests for the pure roof-prop scatter planner (v0.25)."""

import copy

from zoo_keeper.core import roofprops


def _manifest(w=20.0, d=12.0, h=0.3, z=4.05, roofs=1):
    slots = [{"slot_id": f"roof_{i}", "role": "roof",
              "transform": {"translation": [0.0, 0.0, z], "rot_y": 0},
              "fit": {"dims": [w, d, h], "pivot": "center"}}
             for i in range(roofs)]
    slots.append({"slot_id": "ext_0_N_seg0", "role": "wall",
                  "transform": {"translation": [0, 0, 2.1], "rot_y": 0},
                  "fit": {"dims": [2.0, 0.3, 4.2], "pivot": "center"}})
    return {"building_id": "t", "space": "spec/Blender Z-up raw coords",
            "slots": slots}


def test_scatter_populates_large_roof():
    plan = roofprops.scatter(_manifest(), 1999)
    assert plan["counts"]["hvac_unit"] >= 1
    assert plan["counts"]["vent_stack"] >= 2
    assert plan["counts"].get("water_tank", 0) == 1
    assert all(p["slot_id"].startswith("roof") for p in plan["placements"])


def test_props_sit_on_top_surface_within_margin():
    plan = roofprops.scatter(_manifest(w=20, d=12, h=0.3, z=4.05), 1999)
    for p in plan["placements"]:
        assert p["pos"][2] == 4.2  # 4.05 + 0.3/2
        fw, fd = p["footprint"]
        assert abs(p["pos"][0]) <= 10 - 0.6 - fw / 2 + 1e-6
        assert abs(p["pos"][1]) <= 6 - 0.6 - fd / 2 + 1e-6


def test_no_overlaps():
    plan = roofprops.scatter(_manifest(), 1999)
    boxes = []
    for p in plan["placements"]:
        fw, fd = p["footprint"]
        x, y = p["pos"][0], p["pos"][1]
        boxes.append((x - fw / 2, y - fd / 2, x + fw / 2, y + fd / 2))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            assert (a[2] <= b[0] or a[0] >= b[2]
                    or a[3] <= b[1] or a[1] >= b[3]), (a, b)


def test_small_roof_gets_no_tank_or_skylight():
    plan = roofprops.scatter(_manifest(w=5, d=4), 1999)
    assert plan["counts"].get("water_tank", 0) == 0
    assert plan["counts"].get("skylight", 0) == 0


def test_deterministic_and_seed_sensitive():
    m = _manifest()
    a = roofprops.scatter(m, 1999)
    b = roofprops.scatter(copy.deepcopy(m), 1999)
    c = roofprops.scatter(m, 7)
    assert a == b
    assert a["placements"] != c["placements"]


def test_no_roof_slots_yields_empty_plan():
    m = _manifest()
    m["slots"] = [s for s in m["slots"] if s["role"] != "roof"]
    plan = roofprops.scatter(m, 1999)
    assert plan["placements"] == [] and plan["counts"] == {}


def test_species_filter_and_density():
    plan = roofprops.scatter(_manifest(), 1999, species=("vent_stack",))
    assert set(plan["counts"]) == {"vent_stack"}
    sparse = roofprops.scatter(_manifest(), 1999, density=0.25)
    dense = roofprops.scatter(_manifest(), 1999, density=1.0)
    assert len(sparse["placements"]) <= len(dense["placements"])
