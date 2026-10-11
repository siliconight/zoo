"""Tests for the pure roof-prop scatter planner (v0.25; 1.101.0 keeps a prop off the
roof's holes and landings, tests it as the box it occupies, and gives a tank a height;
1.102.0 lets what the building is decide what its roof carries, and fewer)."""

import copy
import math

from zoo_keeper.core import roofprops


def _manifest(w=20.0, d=12.0, h=0.3, z=4.05, roofs=1, voids=None, keep_out=None,
              building="t"):
    slots = [{"slot_id": f"roof_{i}", "role": "roof",
              "transform": {"translation": [0.0, 0.0, z], "rot_y": 0},
              "fit": {"dims": [w, d, h], "pivot": "center",
                      "voids": list(voids or ()), "keep_out": list(keep_out or ())}}
             for i in range(roofs)]
    slots.append({"slot_id": "ext_0_N_seg0", "role": "wall",
                  "transform": {"translation": [0, 0, 2.1], "rot_y": 0},
                  "fit": {"dims": [2.0, 0.3, 4.2], "pivot": "center"}})
    return {"building_id": building, "space": "spec/Blender Z-up raw coords",
            "slots": slots}


def _yawed_box(p):
    """The box a placement OCCUPIES at its yaw, from its footprint and rot_z --
    not from any key the planner writes, so 1.100.0's placements are judged by
    the same rule."""
    fw, fd = p["footprint"]
    c = abs(math.cos(math.radians(p["rot_z"])))
    s = abs(math.sin(math.radians(p["rot_z"])))
    ex, ey = fw / 2 * c + fd / 2 * s, fw / 2 * s + fd / 2 * c
    return (p["pos"][0] - ex, p["pos"][1] - ey, p["pos"][0] + ex, p["pos"][1] + ey)


def _hits(box, rect):
    return not (box[2] <= rect[0] or box[0] >= rect[2]
                or box[3] <= rect[1] or box[1] >= rect[3])


# --- 1.102.0: the building decides --------------------------------------------------------

def test_the_profile_follows_the_building_s_words():
    """FAILS ON 1.101.0: there is no `profile_of`. Tokens, not substrings:
    a barber is a shop and not a bar."""
    p = roofprops.profile_of
    assert p("deli_a01") == "kitchen" and p("primos_pizza") == "kitchen"
    assert p("strip_club_a02") == "kitchen"
    assert p("barber_shop") == "shop" and p("pharmacy_a01") == "shop"
    assert p("large_warehouse_a01") == "big_box" and p("market_hall_a03") == "big_box"
    assert p("funeral_home_a01") == "office" and p("bank_tower_a02") == "office"
    assert p("apartment_walkup_a02") == "home" and p("twin_a01") == "home"
    assert p("parking_garage_a01") == "none" and p("construction_site_a02") == "none"
    assert p("something_unnamed") == "shop" and p(None) == "shop"


def test_a_shop_roof_carries_a_unit_or_two_and_a_vent():
    """FAILS ON 1.101.0: a 20 x 12 roof carried 16 props whatever the building."""
    plan = roofprops.scatter(_manifest(), 1999)          # building "t": a shop
    c = plan["counts"]
    assert plan["profile"] == "shop"
    assert 1 <= c.get("hvac_unit", 0) <= 2 and c.get("vent_stack", 0) == 1
    assert c.get("skylight", 0) == 0 and c.get("water_tank", 0) == 0
    assert len(plan["placements"]) <= 5


def test_a_deli_roof_is_a_unit_or_two_a_vent_and_its_hood_fan():
    totals = []
    for seed in range(30):
        c = roofprops.scatter(_manifest(building="deli_a01"), seed)["counts"]
        assert 1 <= c.get("hvac_unit", 0) <= 2, (seed, c)
        assert c.get("vent_stack", 0) == 1 and 1 <= c.get("exhaust_fan", 0) <= 2, (seed, c)
        assert c.get("skylight", 0) == 0 and c.get("satellite_dish", 0) <= 1, (seed, c)
        totals.append(sum(c.values()))
    # about a third of 1.101.0's 17, and not one number for every roof
    assert 3 <= sum(totals) / len(totals) <= 6 and len(set(totals)) > 1


def test_a_warehouse_roof_gets_more_and_the_skylights():
    c = roofprops.scatter(_manifest(building="large_warehouse_a01"), 1999)["counts"]
    assert c.get("skylight", 0) >= 2 and c.get("hvac_unit", 0) >= 2
    assert sum(c.values()) >= 7


def test_no_two_roofs_match():
    a = roofprops.scatter(_manifest(building="deli_a01"), 1999)
    b = roofprops.scatter(_manifest(building="deli_a02"), 1999)
    assert a["placements"] != b["placements"]


def test_a_parking_deck_carries_nothing():
    plan = roofprops.scatter(_manifest(building="parking_garage_a01", z=11.85), 1999)
    assert plan["profile"] == "none" and plan["placements"] == [] and plan["counts"] == {}


# --- kept from 0.25 and 1.101.0 -----------------------------------------------------------

def test_props_sit_on_top_surface_within_margin():
    plan = roofprops.scatter(_manifest(w=20, d=12, h=0.3, z=4.05, building="warehouse_a01"), 1999)
    for p in plan["placements"]:
        assert p["pos"][2] == 4.2  # 4.05 + 0.3/2
        # the box it OCCUPIES at its yaw, not the unrotated footprint (1.101.0)
        x0, y0, x1, y1 = _yawed_box(p)
        assert max(abs(x0), abs(x1)) <= 10 - 0.6 + 2e-3, p
        assert max(abs(y0), abs(y1)) <= 6 - 0.6 + 2e-3, p


def test_no_overlaps():
    plan = roofprops.scatter(_manifest(building="warehouse_a01"), 1999)
    boxes = [_yawed_box(p) for p in plan["placements"]]   # the yawed boxes
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            assert (a[2] <= b[0] or a[0] >= b[2]
                    or a[3] <= b[1] or a[1] >= b[3]), (a, b)


def test_small_roof_gets_no_tank_or_skylight():
    plan = roofprops.scatter(_manifest(w=5, d=4, building="warehouse_a01"), 1999)
    assert plan["counts"].get("water_tank", 0) == 0
    assert plan["counts"].get("skylight", 0) == 0


def test_deterministic_and_seed_sensitive():
    m = _manifest(building="warehouse_a01")
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
    plan = roofprops.scatter(_manifest(building="warehouse_a01"), 1999, species=("vent_stack",))
    assert set(plan["counts"]) == {"vent_stack"}
    sparse = roofprops.scatter(_manifest(building="warehouse_a01"), 1999, density=0.25)
    dense = roofprops.scatter(_manifest(building="warehouse_a01"), 1999, density=1.0)
    assert len(sparse["placements"]) <= len(dense["placements"])


def test_a_yawed_hvac_at_the_long_edge_stays_inside_the_margin():
    """FAILS ON 1.100.0: the clamp read the unrotated 1.8 x 1.1 box, so a
    90-degree unit on a 4 m deep roof reached 0.25 m from the footprint's edge
    (the margin is 0.6; a parapet is 0.35 thick)."""
    worst = 0.0
    for seed in range(40):
        plan = roofprops.scatter(_manifest(w=20, d=4.0, building="warehouse_a01"), seed,
                                 species=("hvac_unit",))
        for p in plan["placements"]:
            x0, y0, x1, y1 = _yawed_box(p)
            worst = max(worst, abs(y0), abs(y1))
            assert max(abs(y0), abs(y1)) <= 2.0 - 0.6 + 2e-3, (seed, p)
            assert max(abs(x0), abs(x1)) <= 10.0 - 0.6 + 2e-3, (seed, p)
    assert worst > 0.0   # the roof was dressed at all


def test_no_prop_stands_on_a_hole_or_a_landing():
    """FAILS ON 1.100.0, which read neither `voids` nor `keep_out`."""
    hatch = {"x0": -0.65, "y0": -0.65, "x1": 0.65, "y1": 0.65}
    landing = {"x0": 6.0, "y0": -5.0, "x1": 9.0, "y1": -2.0}
    ring = (hatch["x0"] - 1.0, hatch["y0"] - 1.0, hatch["x1"] + 1.0, hatch["y1"] + 1.0)
    land = (landing["x0"], landing["y0"], landing["x1"], landing["y1"])
    hit = 0
    for seed in range(20):
        plan = roofprops.scatter(_manifest(voids=[hatch], keep_out=[landing],
                                           building="warehouse_a01"), seed)
        assert plan.get("forbidden") == {"roof_0": 2}, plan.get("forbidden")
        for p in plan["placements"]:
            box = _yawed_box(p)
            hit += _hits(box, ring) + _hits(box, land)
        assert len(plan["placements"]) >= 7, seed   # the roof is still dressed
    assert hit == 0, hit


def test_a_tank_needs_a_tall_roof():
    """FAILS ON 1.100.0: every roof of 50 m2 got one. A gravity tank serves
    floors below it; Delco's shells stand 3.2 to 13 m, and two of 133 reach 12.
    Kept by the walker on 2026-10-11, whatever the building."""
    low = roofprops.scatter(_manifest(z=4.05, building="office"), 1999)
    tall = roofprops.scatter(_manifest(z=11.85, building="office"), 1999)       # top at 12.0
    assert low["counts"].get("water_tank", 0) == 0
    assert tall["counts"].get("water_tank", 0) == 1


def test_a_placement_records_the_box_it_occupies():
    """`rot_z` ships rounded to a tenth of a degree, so the box recomputed
    from it may differ from the planner's by a millimetre."""
    plan = roofprops.scatter(_manifest(building="warehouse_a01"), 1999)
    for p in plan["placements"]:
        x0, y0, x1, y1 = _yawed_box(p)
        assert abs(p["extents"][0] - (x1 - x0) / 2) <= 2e-3, p
        assert abs(p["extents"][1] - (y1 - y0) / 2) <= 2e-3, p
        # the test roof sits at the origin unrotated: local is spec
        assert p["local"] == [round(p["pos"][0], 3), round(p["pos"][1], 3)], p


def test_extents_are_the_yawed_box():
    assert roofprops._extents(1.8, 1.1, 0.0) == (0.9, 0.55)
    ex, ey = roofprops._extents(1.8, 1.1, 90.0)
    assert abs(ex - 0.55) < 1e-9 and abs(ey - 0.9) < 1e-9
    ex, ey = roofprops._extents(2.0, 2.0, 45.0)
    assert abs(ex - math.sqrt(2)) < 1e-9 and abs(ey - math.sqrt(2)) < 1e-9


def test_forbidden_rects_grow_voids_and_keep_landings_as_given():
    slot = {"voids": [{"x0": 0, "y0": 0, "x1": 1, "y1": 2}],
            "keep_out": [{"x0": 3, "y0": 3, "x1": 4, "y1": 5}]}
    assert roofprops.forbidden_rects(slot) == [(-1.0, -1.0, 2.0, 3.0),
                                               (3.0, 3.0, 4.0, 5.0)]
