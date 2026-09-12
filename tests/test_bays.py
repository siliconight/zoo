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
    plan = kit.plan_kit({"building_id": "t", "slots": [
        _prop("bench", (5.0, 1.4, 1.2), "chair"),
        _prop("boss_desk", (5.0, 1.6, 1.2), "desk"),
    ]}, theme="delco", style=1)
    reasons = {f["slot_id"]: f["reason"] for f in plan["species_fallbacks"]}
    assert "bench" in reasons and "boss_desk" in reasons
    assert "depth 1.60 outside" in reasons["boss_desk"]
