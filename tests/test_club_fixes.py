"""The five club defects 0.88.0 found and did not fix (0.89.0).

Each was seen in a frame or a build log of the scratch club walk, not
guessed, and each clause here failed against 0.88.0 before its fix:

1. A slot may ask for Pixelcoat 0.42.0's club kinds (`carpet_club`,
   `wallpaper_club`, `wood_stained`, `paint_block`) and 0.43.0's `cloth`:
   `dna.resolve_module_plan` keeps a slot's material only when it is in
   `skins.KNOWN_KINDS`, so a club floor asking for `carpet_club` built in
   concrete with no error.
2. The neon sign's tubes stood 60-70 mm off the backer (the tubes at the
   slot's front, the backer 25 mm thick at its back) and the room light
   threw a second, dark copy of every word onto the backer, offset by that
   gap -- double vision in `tables.png`. A real sign's tubes sit a finger
   off the can on their standoffs; the backer is the can.
3. Two slots differing only in `material` planned one stem, so one
   overwrote the other on disk (`STEM COLLISION` on the sofa with and
   without DC's `wood`). The material is in the stem when it is not the
   species' own for the theme -- `_m<kind>` -- and the kit index says so.
4. A slot's material overrode booth_seat's upholstery: DC's `wood` on a
   sofa built a wood sofa. Upholstered species keep their upholstery and
   take the slot material on the frame; which species those are is one
   table, `dna.UPHOLSTERED`.
5. A bar stool's seat and a cocktail table's cloth are chosen by the
   VARIANT, not drawn from the stream, on kinds that now tint (`plastic`,
   `velvet`, `cloth`), so a `_n2` stool is the same stool in every kit.
"""
from __future__ import annotations

import ast
import os
import random

import pytest

from zoo_keeper.core import club_forms as CF
from zoo_keeper.core import dna, genome, kit, neon_forms, skins

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_MATERIALS = os.path.join(_ROOT, "zoo_keeper", "bpylayer", "materials.py")

CLUB_KINDS = ("carpet_club", "wallpaper_club", "wood_stained", "paint_block",
              "velvet", "cloth")


def _roughness_keys():
    tree = ast.parse(open(_MATERIALS, encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "ROUGHNESS" for t in node.targets):
            return {ast.literal_eval(k) for k in node.value.keys}
    raise AssertionError("ROUGHNESS literal not found")


# --- 1. the club kinds --------------------------------------------------------

@pytest.mark.parametrize("kind", CLUB_KINDS)
def test_a_slot_may_ask_for_a_club_kind(kind):
    assert kind in skins.KNOWN_KINDS
    assert kind in _roughness_keys()


def test_a_floor_slot_asking_for_the_club_carpet_gets_it():
    g = genome.load_species("floor")
    module = {"type": "floor", "species": "floor", "state": None, "width_cm": 400,
              "depth_cm": 300, "material": "carpet_club", "fit": "exact",
              "dims": [4.0, 3.0, 0.1], "pivot": "center"}
    plan = dna.resolve_module_plan(module, g, "delco_1997", 1, "test")
    assert plan["material"] == "carpet_club"


# --- 2. the neon sign ---------------------------------------------------------

@pytest.mark.parametrize("dims", [(1.4, 0.1, 0.6), (1.6, 0.1, 0.7), (2.4, 0.06, 0.9),
                                  (0.8, 0.16, 0.4)])
def test_the_tubes_sit_a_finger_off_the_can(dims):
    """The gap between a tube's back and the backer's face is the standoff
    and nothing else; the backer takes the rest of the depth. The dark
    copy a light throws is offset by this gap, so it is bounded here."""
    w, d, h = dims
    got = neon_forms.plan_sign(w, d, h, 3)
    backer = [p for p in got["prims"] if p["part"] == "NeonSign_Backer"]
    assert len(backer) == 1
    back_face = min(v[1] for v in backer[0]["verts"])
    tubes = [p for p in got["prims"] if p["part"] == "NeonSign_Tubes"]
    tube_back = max(max(v[1] for v in p["verts"]) for p in tubes)
    gap = back_face - tube_back
    assert 0.0 < gap <= neon_forms.TUBE_STANDOFF + 1e-6, (dims, gap)
    # the tubes' fronts are still the slot's front, the backer's back its wall
    assert abs(min(min(v[1] for v in p["verts"]) for p in tubes) - (-d / 2)) < 1e-6
    assert abs(max(v[1] for v in backer[0]["verts"]) - d / 2) < 1e-6


def test_the_standoff_is_a_real_neon_standoff():
    assert 0.01 <= neon_forms.TUBE_STANDOFF <= 0.03


# --- 3. the material in the stem ----------------------------------------------

def _prop(slot_id, species, dims, material=None, **dress):
    s = {"slot_id": slot_id, "role": "prop", "size_mod": "full", "species": species,
         "fit": {"dims": list(dims), "pivot": "center"}, "style": 1}
    if material:
        s["material"] = material
    s.update(dress)
    return s


def test_module_stem_carries_the_material_after_the_dressing():
    assert kit.module_stem("prop", "delco_1997", 1, 200, None, 90, None, None, 85,
                           species="booth_seat", form="sofa", variant=1,
                           material="wood") == \
        "prop_booth_seat_delco_1997_01_w200_d90_h85_fsofa_n1_mwood"
    # before the void/opening hashes and the state, like the dressing
    assert kit.module_stem("floor", "delco", 1, 400, "night", 300, "abc123",
                           material="carpet_club") == \
        "floor_delco_01_w400_d300_mcarpet_club_vabc123_night"
    assert kit.module_stem("wall", "delco", 1, 200) == "wall_delco_01_w200"


def test_two_sofa_slots_differing_only_in_material_are_two_files():
    plan = kit.plan_kit({"building_id": "b", "slots": [
        _prop("a", "booth_seat", (2.0, 0.9, 0.85), form="sofa", variant=1),
        _prop("b", "booth_seat", (2.0, 0.9, 0.85), material="wood", form="sofa",
              variant=1),
    ]}, theme="delco_1997", style=1)
    stems = sorted(m["stem"] for m in plan["modules"])
    assert stems == ["prop_booth_seat_delco_1997_01_w200_d90_h85_fsofa_n1",
                     "prop_booth_seat_delco_1997_01_w200_d90_h85_fsofa_n1_mwood"]
    assert plan["stem_collisions"] == []
    by = {m["stem"]: m for m in plan["modules"]}
    assert by[stems[1]]["material_tag"] == "wood"
    assert by[stems[0]]["material_tag"] is None


def test_the_species_own_material_adds_nothing_to_the_stem():
    """A bar stool IS metal_bare; a slot saying so names the same file."""
    plan = kit.plan_kit({"building_id": "b", "slots": [
        _prop("a", "bar_stool", (0.42, 0.42, 0.76)),
        _prop("b", "bar_stool", (0.42, 0.42, 0.76), material="metal_bare"),
    ]}, theme="delco_1997", style=1)
    assert [m["stem"] for m in plan["modules"]] == ["prop_bar_stool_delco_1997_01_w42_d42_h76"]
    assert plan["modules"][0]["count"] == 2


def test_an_unknown_material_adds_nothing_to_the_stem():
    plan = kit.plan_kit({"building_id": "b", "slots": [
        _prop("a", "bar_stool", (0.42, 0.42, 0.76), material="unobtainium")]},
        theme="delco_1997", style=1)
    assert plan["modules"][0]["stem"] == "prop_bar_stool_delco_1997_01_w42_d42_h76"


def test_a_wall_in_the_theme_default_material_keeps_its_filename():
    plan = kit.plan_kit({"building_id": "b", "slots": [
        {"slot_id": "w", "role": "wall", "size_mod": "full", "style": 1,
         "material": "concrete", "fit": {"dims": [2.0, 0.35, 4.0], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["modules"][0]["stem"] == "wall_delco_01_w200"


def test_dna_constructs_the_same_stem_the_kit_planned():
    g = genome.load_species("booth_seat")
    module = {"type": "prop", "species": "booth_seat", "state": None, "width_cm": 200,
              "depth_cm": 90, "height_cm": 85, "material": "wood", "fit": "exact",
              "dims": [2.0, 0.9, 0.85], "pivot": "center", "form": "sofa", "variant": 1,
              "style": 1}
    plan = dna.resolve_module_plan(module, g, "delco_1997", 1, "test")
    assert plan["module"]["stem"] == "prop_booth_seat_delco_1997_01_w200_d90_h85_fsofa_n1_mwood"
    assert plan["module"]["material_tag"] == "wood"


def test_species_default_material_is_what_the_plan_would_pick_unasked():
    assert kit.species_default_material("booth_seat", "delco_1997") == "leather"
    assert kit.species_default_material("booth_seat", "1990s") == "canvas"
    assert kit.species_default_material("bar_stool", "delco_1997") == "metal_bare"
    assert kit.species_default_material("no_such_species", "delco") is None


# --- 4. upholstery -----------------------------------------------------------

def test_the_upholstered_species_are_one_table():
    assert set(dna.UPHOLSTERED) >= {"booth_seat", "club_chair", "bar_stool"}
    for sp in dna.UPHOLSTERED:
        genome.load_species(sp)          # every entry is a species that exists


def test_a_wood_slot_builds_a_leather_sofa_on_wood_legs():
    g = genome.load_species("booth_seat")
    module = {"type": "prop", "species": "booth_seat", "state": None, "width_cm": 200,
              "depth_cm": 90, "height_cm": 85, "material": "wood", "fit": "exact",
              "dims": [2.0, 0.9, 0.85], "pivot": "center", "form": "sofa", "style": 1}
    plan = dna.resolve_module_plan(module, g, "delco_1997", 1, "test")
    assert plan["upholstery"]["material"] == "leather"
    assert plan["upholstery"]["color"] == plan["color"]
    assert plan["material"] == "wood"
    assert plan["upholstery"]["frame"] == "wood"


def test_an_upholstery_kind_on_the_slot_is_the_upholstery():
    g = genome.load_species("booth_seat")
    module = {"type": "prop", "species": "booth_seat", "state": None, "width_cm": 200,
              "depth_cm": 90, "height_cm": 85, "material": "canvas", "fit": "exact",
              "dims": [2.0, 0.9, 0.85], "pivot": "center", "style": 1}
    plan = dna.resolve_module_plan(module, g, "delco_1997", 1, "test")
    assert plan["upholstery"]["material"] == "canvas"
    assert plan["upholstery"]["frame"] is None


def test_an_unupholstered_species_carries_no_upholstery():
    g = genome.load_species("cocktail_table")
    module = {"type": "prop", "species": "cocktail_table", "state": None, "width_cm": 75,
              "depth_cm": 75, "height_cm": 74, "material": "wood", "fit": "exact",
              "dims": [0.75, 0.75, 0.74], "pivot": "center", "style": 1}
    plan = dna.resolve_module_plan(module, g, "delco_1997", 1, "test")
    assert "upholstery" not in plan


# --- 5. seats and cloths by variant ------------------------------------------

def test_a_stool_seat_is_its_variant():
    n = len(CF.SEATS)
    for v in range(2 * n):
        got = CF.plan_stool(0.42, 0.42, 0.76, random.Random(v * 7 + 1), variant=v)
        rgb, kind = CF.SEATS[v % n]
        assert got["seat_rgb"] == rgb and got["seat_kind"] == kind
    assert {k for _c, k in CF.SEATS} <= {"plastic", "velvet"}
    assert len(CF.SEATS) >= 3


def test_a_cloth_is_dark_red_or_white_by_variant():
    reds = whites = 0
    for v in range(4):
        got = CF.plan_table(0.75, 0.75, 0.74, random.Random(v), "cloth", variant=v)
        r, g, b = got["cloth_rgb"]
        assert got["cloth_kind"] == "cloth"
        if r > 0.15 and g < 0.08 and b < 0.1:
            reds += 1
        elif min(r, g, b) > 0.75:
            whites += 1
    assert reds >= 1 and whites >= 1 and reds + whites == 4


def test_the_seed_no_longer_decides_a_seat_or_a_cloth():
    seats = {tuple(CF.plan_stool(0.42, 0.42, 0.76, random.Random(s), variant=2)["seat_rgb"])
             for s in range(12)}
    cloths = {tuple(CF.plan_table(0.75, 0.75, 0.74, random.Random(s), "cloth", variant=1)["cloth_rgb"])
              for s in range(12)}
    assert len(seats) == 1 and len(cloths) == 1
