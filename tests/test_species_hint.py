"""A volume's species hint is honoured when the species fits and reported
when it does not (roadmap 44). The box stays the fallback, never greybox.
"""
from __future__ import annotations

from zoo_keeper.core import kit


def _prop(slot_id, dims, species=None, style=1):
    s = {"slot_id": slot_id, "role": "prop", "size_mod": "full", "style": style,
         "fit": {"dims": list(dims), "pivot": "center"}}
    if species is not None:
        s["species"] = species
    return s


def _plan(*slots):
    return kit.plan_kit({"building_id": "t", "slots": list(slots)},
                        theme="delco", style=1)


def test_a_desk_that_fits_is_planned_as_a_desk_under_the_prop_stem():
    plan = _plan(_prop("desk_manager_office", (1.6, 0.8, 0.75), "desk"))
    (m,) = plan["modules"]
    assert m["type"] == "prop" and m["species"] == "desk"
    assert m["stem"] == "prop_desk_delco_01_w160_d80_h75"
    assert m["dims"] == [1.6, 0.8, 0.75] and m["fit"] == "exact"
    assert plan["species_fallbacks"] == []


def test_a_shape_no_species_can_be_is_built_as_the_box_and_said():
    """A 12 x 6 m block of gaming tables is a region, not a table (0.64.0
    opened widths to runs, so the old 8 m teller example is now a counter
    by the alternate rule -- see test_bays)."""
    plan = _plan(_prop("gaming_tables", (12.0, 6.0, 1.0), "table"))
    (m,) = plan["modules"]
    assert m["species"] == "prop"
    assert m["stem"] == "prop_delco_01_w1200_d600_h100"
    (fb,) = plan["species_fallbacks"]
    assert fb["slot_id"] == "gaming_tables" and fb["hint"] == "table"
    assert fb["built_as"] == "prop" and "width 12.00 outside 0.60..8.00" in fb["reason"]


def test_a_low_teller_line_is_a_counter_by_the_alternate_rule():
    plan = _plan(_prop("teller_counter", (8.0, 0.8, 1.0), "teller_line"))
    (m,) = plan["modules"]
    assert m["species"] == "counter" and m["stem"] == "prop_counter_delco_01_w800_d80_h100"
    (alt,) = plan["species_alternates"]
    assert alt["hint"] == "teller_line" and alt["built_as"] == "counter"
    assert plan["species_fallbacks"] == []


def test_a_species_that_would_fit_turned_says_so():
    plan = _plan(_prop("desk_side", (0.8, 1.6, 0.75), "desk"))
    (fb,) = plan["species_fallbacks"]
    assert "would fit turned 90 degrees" in fb["reason"]
    assert plan["modules"][0]["species"] == "prop"


def test_an_unknown_species_hint_is_the_box_with_the_reason():
    plan = _plan(_prop("thing", (1.0, 1.0, 1.0), "hoverboard"))
    assert plan["modules"][0]["species"] == "prop"
    (fb,) = plan["species_fallbacks"]
    assert fb["reason"].startswith("no genome for 'hoverboard'")


def test_a_desk_and_a_crate_of_one_size_are_two_modules_with_two_names():
    plan = _plan(_prop("desk_a", (1.6, 0.8, 0.75), "desk"),
                 _prop("crate_a", (1.6, 0.8, 0.75)))
    stems = sorted(m["stem"] for m in plan["modules"])
    assert stems == ["prop_delco_01_w160_d80_h75", "prop_desk_delco_01_w160_d80_h75"]


def test_an_unhinted_slot_is_exactly_what_it_always_was():
    plan = _plan(_prop("crate_stack", (1.1, 1.1, 0.95)))
    (m,) = plan["modules"]
    assert m["species"] == "prop" and m["stem"] == "prop_delco_01_w110_d110_h95"
    assert plan["species_fallbacks"] == []


def test_the_stem_mirror_carries_the_species():
    assert kit.module_stem("prop", "delco", 2, 160, None, 80, None, None, 75,
                           species="desk") == "prop_desk_delco_02_w160_d80_h75"
    assert kit.module_stem("prop", "delco", 2, 160, None, 80, None, None, 75,
                           species="prop") == "prop_delco_02_w160_d80_h75"
