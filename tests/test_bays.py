"""Bays: a run species fills a Deli Counter run in equal units (roadmap 44).

The 579 hinted placements that were longer than any single unit: an 8 m
teller counter, a 7 m shelf aisle, a 3 m locker bank, a 5 m desk row.
"""
from __future__ import annotations

import json
import os

from zoo_keeper.core import kit
from zoo_keeper.recipes._bays import bay_max_of, bays

_GENOMES = os.path.join(os.path.dirname(__file__), "..", "zoo_keeper", "genome", "species")


def _genome(sp):
    with open(os.path.join(_GENOMES, sp + ".json"), encoding="utf-8") as f:
        return json.load(f)


def test_equal_bays_never_a_sliver():
    assert bays(8.0, 4.0) == [(-2.0, 4.0), (2.0, 4.0)]
    # 5.0 at 2.2 -> three of 1.667, not two full and a 0.6 stub
    b = bays(5.0, 2.2)
    assert len(b) == 3 and all(abs(w - 5.0 / 3) < 1e-9 for _, w in b)
    assert abs(sum(w for _, w in b) - 5.0) < 1e-9
    assert b[0][0] < b[1][0] < b[2][0] and abs(b[1][0]) < 1e-9


def test_one_bay_is_the_unit_that_always_was():
    assert bays(2.0, 4.0) == [(0.0, 2.0)]
    assert bays(2.0, 0.0) == [(0.0, 2.0)]
    assert bays(2.0, None) == [(0.0, 2.0)]
    assert bay_max_of({"params": {}}) == 0.0
    assert bay_max_of({"params": {"bay_max": 2.4}}) == 2.4


def test_the_run_species_declare_bay_max_and_open_their_width():
    for sp, unit in (("counter", 4.0), ("shelving", 2.4),
                     ("filing_cabinet", 0.5), ("desk", 2.2)):
        g = _genome(sp)
        assert g["params"]["bay_max"] == unit, sp
        assert g["dimensions"]["width"]["max"] > unit, sp


def test_the_desk_declares_a_row_max_and_the_ranges_the_library_asks_for():
    """`bay_max` divides the width; `row_max` divides the DEPTH, and a
    cubicle block is the only shape that needs it today.

    Measured over the 328 named prop slots in the 130 built shells: 30 desk
    slots fell outside the old ranges -- 27 at 1.1 or 1.2 m tall and 10 at
    6.0 m deep -- which was 30 of the 43 misses in the whole library. After
    this the library's named prop slots go 285 fit / 43 miss to 314 / 14.
    """
    g = _genome("desk")
    assert g["params"]["row_max"] == 1.5
    assert g["dimensions"]["depth"]["max"] == 6.0
    assert g["dimensions"]["height"]["max"] == 1.3
    # a row is a unit, not a sliver: 6.0 m at 1.5 is four rows of 1.5
    from zoo_keeper.recipes._bays import bays
    rows = bays(6.0, 1.5)
    assert len(rows) == 4 and all(abs(r[1] - 1.5) < 1e-9 for r in rows)


def _prop(sid, dims, species):
    return {"slot_id": sid, "role": "prop", "size_mod": "full", "style": 1,
            "species": species, "fit": {"dims": list(dims), "pivot": "center"}}


def test_the_runs_the_library_authors_now_plan_as_their_species():
    """The shapes from the 2026-09-12 measurement, verbatim."""
    plan = kit.plan_kit({"building_id": "t", "slots": [
        _prop("teller_counter", (8.0, 0.8, 1.0), "counter"),
        _prop("nurse_station_0", (4.0, 1.4, 1.1), "counter"),
        _prop("aisle_shelf", (6.0, 1.0, 1.6), "shelving"),        # turned by DC
        _prop("rack_a", (9.0, 1.2, 3.0), "shelving"),
        _prop("ARMORY_LOCKER", (3.0, 0.8, 2.0), "filing_cabinet"),
        _prop("cabinet_manager_office", (0.9, 0.5, 1.4), "filing_cabinet"),
        _prop("cubicles_w", (4.4, 0.8, 0.75), "desk"),
        _prop("roof_unit", (3.0, 2.0, 1.2), "hvac_unit"),
        _prop("helipad_hvac", (4.0, 3.0, 1.4), "hvac_unit"),
        _prop("card_table_a", (1.4, 1.4, 0.8), "table"),
    ]}, theme="delco", style=1)
    got = {m["stem"].split("_delco")[0]: m["species"] for m in plan["modules"]}
    assert plan["species_fallbacks"] == [], plan["species_fallbacks"]
    assert set(got.values()) == {"counter", "shelving", "filing_cabinet",
                                 "desk", "hvac_unit", "table"}


def test_what_still_falls_back_says_why():
    """A 1.2 m tall bench is no chair (1.1 max).

    SUPERSEDED, kept above the result that replaced it. This used to assert
    that a 5 x 1.6 x 1.2 "boss desk" was a COUNTER by the alternate rule,
    because `desk` capped at 1.0 m tall and 1.2 m deep. Measured across the
    130 built shells, 27 of the library's desk volumes are 1.1 or 1.2 m tall
    and 15 are 1.3-1.6 m deep -- those are reception desks with a raised
    ledge and desks with a return, not service counters, and calling them
    counters was the range being too tight rather than the name being wrong.
    `desk` now runs to 1.3 m tall and 6.0 m deep and keeps its work surface
    at sitting height, so this builds as a desk and no alternate is needed.
    """
    plan = kit.plan_kit({"building_id": "t", "slots": [
        _prop("bench", (5.0, 1.4, 1.2), "chair"),
        _prop("boss_desk", (5.0, 1.6, 1.2), "desk"),
    ]}, theme="delco", style=1)
    reasons = {f["slot_id"]: f["reason"] for f in plan["species_fallbacks"]}
    assert list(reasons) == ["bench"] and "height 1.20 outside" in reasons["bench"]
    assert plan["species_alternates"] == [], plan["species_alternates"]
    # `desk` for the boss desk, `prop` for the bench that fell back
    assert {m["species"] for m in plan["modules"]} == {"desk", "prop"}


def test_tables_and_seating_run_in_bays_and_a_tall_desk_is_a_counter():
    """The 179 that still fell back on 2026-09-12, by the shapes measured."""
    plan = kit.plan_kit({"building_id": "t", "slots": [
        _prop("count_table", (4.0, 2.0, 0.9), "table"),
        _prop("kitchen_prep_table", (4.0, 1.2, 0.9), "table"),
        _prop("waiting_seats", (5.0, 2.0, 0.6), "chair"),
        _prop("bench_row", (2.8, 1.0, 0.9), "chair"),
        _prop("booth_seating_a", (2.0, 1.2, 1.1), "chair"),
        _prop("rack", (16.0, 1.4, 4.4), "shelving"),
        _prop("server_rack_cluster", (4.0, 1.4, 2.2), "shelving"),
        _prop("office_safe", (1.2, 1.0, 1.5), "drop_safe"),
        _prop("tank", (3.0, 3.0, 4.4), "water_tank"),
        _prop("exec_desk", (2.4, 1.1, 0.8), "desk"),
        _prop("coffee_island", (3.0, 2.0, 1.1), "counter"),
        _prop("front_desk", (6.0, 0.9, 1.1), "desk"),       # a counter by any name
        _prop("checkin_desk", (4.0, 1.4, 1.2), "desk"),
    ]}, theme="delco", style=1)
    assert plan["species_fallbacks"] == [], plan["species_fallbacks"]
    by = {m["stem"].split("_delco")[0]: m["species"] for m in plan["modules"]}
    assert by["prop_table_delco_01_w400_d200_h90".split("_delco")[0]] == "table"
    # SUPERSEDED: `front_desk` (6.0 x 0.9 x 1.1) and `checkin_desk`
    # (4.0 x 1.4 x 1.2) were built as counters while `desk` capped at 1.0 m.
    # They are reception desks -- a work surface at sitting height with a
    # ledge over its back edge -- and the species now says so, so they build
    # as what they are named and nothing falls to an alternate.
    assert {m["species"] for m in plan["modules"] if m["dims"][0] == 6.0} == {"desk"}
    assert plan["species_alternates"] == [], plan["species_alternates"]


def test_what_is_a_region_not_a_thing_still_falls_back():
    """A REGION is a species only when its unit tiles in two directions.

    `cubicles_w` used to be here as the example of a region: 8 x 6 m of
    floor called a desk. It has moved to the other side, because a cubicle
    block IS a grid of desks butted back to back and `row_max` divides the
    depth the way `bay_max` divides the width -- ten of the library's desk
    volumes are 6.0 m deep and every one of them is that. `gaming_tables`
    stays: a casino floor's tables stand apart with room to walk between
    them, so twelve metres of them is a region and no amount of tiling one
    table makes it right.
    """
    plan = kit.plan_kit({"building_id": "t", "slots": [
        _prop("cubicles_w", (8.0, 6.0, 1.2), "desk"),
        _prop("gaming_tables", (12.0, 6.0, 1.0), "table"),
    ]}, theme="delco", style=1)
    assert {f["slot_id"] for f in plan["species_fallbacks"]} == {"gaming_tables"}
    assert plan["species_alternates"] == []
    # the cubicle block builds; the casino floor is still a box
    assert {m["species"] for m in plan["modules"]} == {"desk", "prop"}
