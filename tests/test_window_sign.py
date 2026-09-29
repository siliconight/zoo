"""The store window neon (1.27.0) and the counter accent's hardware row.

A neon sign in its `window` form hangs in a store's window facing the
street: a beer from `club_names.WINDOW_NAMES` in red or blue, its tubes on
standoffs in front of a clear sheet, two chains from the sheet's top to the
slot's top. The wall form -- every club sign already shipped -- must not
move; `test_club_bpy.MAIN_DIGESTS` holds its built bytes and the plans are
compared here.
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import club_names as CN
from zoo_keeper.core import fixtures, kit
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import neon_forms as NF
from zoo_keeper.core import prims as P

_CORNERS = [(1.0, 0.06, 0.45), (1.0, 0.06, 0.5), (1.4, 0.1, 0.6), (3.0, 0.25, 1.2), (3.0, 0.06, 0.45)]


def _exact(prims, w, d, h, tol=1e-6):
    lo, hi = P.bounds(prims)
    assert abs(lo[0] + w / 2) < tol and abs(hi[0] - w / 2) < tol, (lo, hi)
    assert abs(lo[1] + d / 2) < tol and abs(hi[1] - d / 2) < tol, (lo, hi)
    assert abs(lo[2]) < tol and abs(hi[2] - h) < tol, (lo, hi)


def _part(got, name):
    return [p for p in got["prims"] if p["part"] == name]


# --- the names ------------------------------------------------------------------


def test_every_window_name_is_spelled_from_the_font_and_is_on_no_denylist():
    assert len(set(CN.WINDOW_NAMES)) == len(CN.WINDOW_NAMES)
    for name in CN.WINDOW_NAMES:
        assert name == name.upper() and name.strip() == name
        assert set(name) <= set(NF.FONT_5X7), name
        for bad in CN.DENYLIST + CN.BEER_DENYLIST:
            assert bad not in name, (name, bad)


def test_the_beer_denylist_can_fail():
    assert any(bad in "ROLLING ROCK EXTRA PALE" for bad in CN.BEER_DENYLIST)


def test_a_window_sign_sells_beer_and_a_wall_sign_names_the_club():
    for v in range(len(CN.WINDOW_NAMES)):
        assert NF.plan_sign(1.0, 0.06, 0.5, v, form="window")["text"] == CN.WINDOW_NAMES[v]
    assert NF.plan_sign(1.0, 0.06, 0.5, 0)["text"] == CN.NAMES[0]
    assert not set(CN.WINDOW_NAMES) & set(CN.NAMES)


def test_a_window_sign_is_red_or_blue():
    for v in range(4):
        got = NF.plan_sign(1.0, 0.06, 0.5, v, form="window")
        text, border = got["colours"]["text"], got["colours"]["border"]
        assert (text, border) in CN.WINDOW_PALETTES
        for rgb in (text, border):
            # red leads or blue leads; neither is a pink, a white or a green
            assert rgb[0] > 0.9 and rgb[2] < 0.1 or rgb[2] > 0.9 and rgb[0] < 0.2, rgb


# --- the shape ------------------------------------------------------------------


@pytest.mark.parametrize("dims", _CORNERS)
def test_every_window_sign_fills_its_slot_exactly_and_clean(dims):
    for v in range(len(CN.WINDOW_NAMES)):
        got = NF.plan_sign(*dims, variant=v, form="window")
        _exact(got["prims"], *dims)
        # fit_exact at a scale of 1: nothing was stretched to reach the slot
        assert got["overshoot_m"] < 1e-9, (dims, v)
        assert P.coincident_pairs(got["prims"]) == [], (v, got["text"])


@pytest.mark.parametrize("dims", _CORNERS)
def test_it_hangs_from_two_chains_off_a_sheet_short_of_the_top(dims):
    w, d, h = dims
    got = NF.plan_sign(*dims, variant=2, form="window")
    sheet = P.bounds(_part(got, "NeonSign_Backer"))
    chains = _part(got, "NeonSign_Chain")
    assert len(chains) == 2
    top = h * (1.0 - NF.HANG_FRAC)
    assert sheet[1][2] == pytest.approx(top, abs=1e-6)
    for c in chains:
        lo, hi = P.bounds([c])
        assert hi[2] == pytest.approx(h, abs=1e-6)       # reaches the slot's top
        assert lo[2] < top                                 # and is sunk into the sheet
        assert sheet[0][1] <= lo[1] and hi[1] <= sheet[1][1]
    xs = sorted((P.bounds([c])[0][0] + P.bounds([c])[1][0]) / 2 for c in chains)
    assert xs[0] < 0 < xs[1]
    # the lettering stays on the sheet, clear of the chains' span
    tubes = P.bounds(_part(got, "NeonSign_Tubes"))
    assert tubes[1][2] < top and tubes[0][2] > 0.0


def test_the_tubes_face_the_street_and_the_sheet_is_behind_them():
    got = NF.plan_sign(1.0, 0.06, 0.5, 0, form="window")
    tubes = P.bounds(_part(got, "NeonSign_Tubes"))
    sheet = P.bounds(_part(got, "NeonSign_Backer"))
    assert tubes[0][1] == pytest.approx(-0.03, abs=1e-6)   # the slot's front, -Y
    assert tubes[1][1] < sheet[0][1]


def test_the_window_form_adds_a_part_and_no_material():
    wall = NF.plan_sign(1.4, 0.1, 0.6, 3)
    window = NF.plan_sign(1.4, 0.1, 0.6, 3, form="window")
    assert {p["mat"] for p in window["prims"]} == {p["mat"] for p in wall["prims"]}
    assert {p["part"] for p in window["prims"]} - {p["part"] for p in wall["prims"]} == {"NeonSign_Chain"}


def test_the_wall_form_is_the_default_and_unchanged_by_asking_for_it():
    for dims in _CORNERS:
        for v in (0, 7, 23):
            assert NF.plan_sign(*dims, v) == NF.plan_sign(*dims, v, form="wall")


# --- the genome and the kit -------------------------------------------------------


def test_the_genome_lists_both_forms_wall_first():
    g = genome_mod.load_species("neon_sign")
    assert genome_mod.validate_genome(g) == []
    assert g["params"]["form"] == list(NF.FORMS) == ["wall", "window"]
    assert "NeonSign_Chain" in g["parts"]


def test_the_kit_stems_a_window_sign_apart_from_a_wall_sign():
    def stem(fields):
        slot = {"slot_id": "s", "role": "prop", "size_mod": "full", "style": 1,
                "species": "neon_sign", "fit": {"dims": [1.0, 0.06, 0.5], "pivot": "center"}}
        slot.update(fields)
        plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
        assert plan["dressing_fallbacks"] == []
        return plan["modules"][0]["stem"]
    assert stem({"form": "window", "variant": 3}).endswith("_fwindow_n3")
    assert stem({"variant": 3}).endswith("_n3") and "_fwindow" not in stem({"variant": 3})


# --- the counter accent's hardware ----------------------------------------------------


def test_a_counter_accent_hangs_a_pendant_not_a_skip():
    p = fixtures.plan({"light_manifest_version": "1.0.0", "space": "Blender Z-up, meters",
                       "rig_library": "lux", "building_id": "gs", "anchors": [
        {"id": "sales_floor_counter_accent", "type": "counter_accent", "pos": [0, -8.5, 3.2],
         "row": {"count": 1, "spacing": 0.0}, "drop": 3.2}]})
    assert not p["skipped"]
    assert [(pl["species"], pl["mount"]) for pl in p["placements"]] == [("pendant_fixture", "above")]
