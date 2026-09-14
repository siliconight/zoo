"""The club species (0.87.0), planned in pure Python: club_stage,
cocktail_table, club_chair, bar_stool, neon_sign and crt_tv's bracket form.

What the planners promise and a build cannot drift from (`prims` lists are
built vertex for vertex): exact extents at the genome's corners, no
coincident faces, a triangle count inside the genome's budget, the same
plan from the same seed, the forms and heights the docstrings state, the
dressing fields the kit honours, and a name table that is invented and
spellable. The bpy half is tests/test_club_bpy.py.
"""
from __future__ import annotations

import itertools
import math
import os
import random
import re

import pytest

from zoo_keeper.core import club_forms as CF
from zoo_keeper.core import club_names as CN
from zoo_keeper.core import crt_forms as KF
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import intent, kit
from zoo_keeper.core import neon_forms as NF
from zoo_keeper.core import prims as P
from zoo_keeper.recipes import _surface_stock as S

CLUB = ("club_stage", "cocktail_table", "club_chair", "bar_stool", "neon_sign")


def _corners(sp):
    g = genome_mod.load_species(sp)
    dims = g["dimensions"]
    axes = [(dims[a]["min"], dims[a]["default"], dims[a]["max"]) for a in ("width", "depth", "height")]
    out = {tuple(a[1] for a in axes)}
    for pick in itertools.product((0, 2), repeat=3):
        out.add(tuple(axes[k][pick[k]] for k in range(3)))
    return sorted(out)


def _exact(prims, w, d, h, tol=1e-6):
    lo, hi = P.bounds(prims)
    assert abs(lo[0] + w / 2) < tol and abs(hi[0] - w / 2) < tol, (lo, hi)
    assert abs(lo[1] + d / 2) < tol and abs(hi[1] - d / 2) < tol, (lo, hi)
    assert abs(lo[2]) < tol and abs(hi[2] - h) < tol, (lo, hi)


def _plan(sp, dims, form="auto", seed=0, variant=0):
    rng = random.Random(seed)
    if sp == "club_stage":
        return CF.plan_stage(*dims, rng, form)
    if sp == "cocktail_table":
        return CF.plan_table(*dims, rng, form)
    if sp == "club_chair":
        return CF.plan_chair(*dims, rng)
    if sp == "bar_stool":
        return CF.plan_stool(*dims, rng)
    if sp == "neon_sign":
        return NF.plan_sign(*dims, variant=variant)
    raise KeyError(sp)


_CASES = ([("club_stage", d, f) for d in _corners("club_stage") for f in CF.STAGE_FORMS]
          + [("cocktail_table", d, f) for d in _corners("cocktail_table") for f in CF.TABLE_FORMS]
          + [("club_chair", d, "auto") for d in _corners("club_chair")]
          + [("bar_stool", d, "auto") for d in _corners("bar_stool")]
          + [("neon_sign", d, "auto") for d in _corners("neon_sign")])


def _id(case):
    sp, dims, form = case
    return "%s-%s-%s" % (sp, "x".join("%g" % v for v in dims), form)


# --- the genomes --------------------------------------------------------------


@pytest.mark.parametrize("sp", CLUB)
def test_the_species_is_discovered_and_its_genome_validates(sp):
    g = genome_mod.load_species(sp)
    assert g["species"] == sp
    assert genome_mod.validate_genome(g) == []
    assert "delco" in g["styles"]


def test_the_contract_names_are_the_ones_deli_counter_will_write():
    """The five names are a contract; a rename breaks a resolver on the other
    side that nothing here can see."""
    assert set(CLUB) <= set(genome_mod.list_species())
    assert genome_mod.load_species("club_stage")["params"]["form"] == ["auto", "round", "runway", "bar_stage"]
    assert genome_mod.load_species("cocktail_table")["params"]["form"] == ["auto", "cloth", "bare"]
    assert genome_mod.load_species("crt_tv")["params"]["form"] == ["auto", "stand", "bracket"]


@pytest.mark.parametrize("prompt,species", [
    ("club stage", "club_stage"), ("strip club stage", "club_stage"), ("pole stage", "club_stage"),
    ("cocktail table", "cocktail_table"), ("tub chair", "club_chair"), ("club chair", "club_chair"),
    ("bar stool", "bar_stool"), ("neon sign", "neon_sign"),
    # what already routed keeps routing
    ("chair", "chair"), ("stool", "chair"), ("table", "table"), ("couch", "booth_seat"),
    ("tv", "crt_tv"), ("lit sign", "sign_box")])
def test_keywords_route_and_steal_nothing(prompt, species):
    assert intent.parse(prompt).species == species


@pytest.mark.parametrize("sp,dims,fields,suffix", [
    ("club_stage", (8.0, 4.0, 3.6), {"form": "bar_stage", "stock": "bar", "variant": 1}, "_fbar_stage_sbar_n1"),
    ("club_stage", (8.0, 4.0, 0.8), {"form": "runway"}, "_frunway"),
    ("cocktail_table", (0.75, 0.75, 0.74), {"form": "bare", "stock": "bar", "variant": 3}, "_fbare_sbar_n3"),
    ("club_chair", (0.78, 0.75, 0.78), {"variant": 2}, "_n2"),
    ("bar_stool", (0.42, 0.42, 0.76), {"variant": 3}, "_n3"),
    ("neon_sign", (1.4, 0.1, 0.6), {"variant": 23}, "_n23"),
    ("crt_tv", (0.55, 0.62, 0.5), {"form": "bracket"}, "_fbracket"),
])
def test_the_kit_honours_the_dressing_fields(sp, dims, fields, suffix):
    slot = {"slot_id": sp, "role": "prop", "size_mod": "full", "style": 1, "species": sp,
            "fit": {"dims": list(dims), "pivot": "center"}}
    slot.update(fields)
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    assert plan["modules"][0]["stem"].endswith(suffix), plan["modules"][0]["stem"]


@pytest.mark.parametrize("sp,fields", [
    ("club_chair", {"stock": "bar"}), ("bar_stool", {"form": "round"}),
    ("neon_sign", {"variant": 24}), ("club_stage", {"stock": "office"}),
    ("cocktail_table", {"form": "round"})])
def test_a_field_the_species_cannot_honour_drops_all_three_and_says_so(sp, fields):
    got, why = kit.honour_dressing(dict(fields), sp)
    assert got == {"form": None, "stock": None, "variant": None} and why


def test_deli_counters_current_club_volumes_fit_the_genomes():
    """strip_club_a01's stage 8 x 4 x 0.8, a03's 7 x 3.5 x 0.8 (read from
    deli_counter/specs 2026-09-14): a stage slot built today fits."""
    for dims in ((8.0, 4.0, 0.8), (7.0, 3.5, 0.8)):
        hint, why = kit._species_fit("club_stage", dims)
        assert hint == "club_stage", why


# --- extents, faces, budgets, determinism -----------------------------------


@pytest.mark.parametrize("case", _CASES, ids=_id)
def test_every_plan_claims_exactly_its_slot_with_no_shared_planes(case):
    sp, dims, form = case
    got = _plan(sp, dims, form)
    _exact(got["prims"], *dims)
    assert got["overshoot_m"] <= 0.012, got["overshoot_m"]
    assert P.coincident_pairs(got["prims"]) == []
    lo = (-dims[0] / 2 - 1e-6, -dims[1] / 2 - 1e-6, -1e-6)
    hi = (dims[0] / 2 + 1e-6, dims[1] / 2 + 1e-6, dims[2] + 1e-6)
    for a, b in got["collision"]:
        assert all(lo[k] <= a[k] <= b[k] <= hi[k] for k in range(3)), (a, b)


@pytest.mark.parametrize("case", _CASES, ids=_id)
def test_every_plan_is_inside_its_budget_with_room_for_stock(case):
    sp, dims, form = case
    budget = genome_mod.load_species(sp)["budgets"]["tris_lod0"]
    got = _plan(sp, dims, form)
    stock = 0
    if sp == "club_stage":
        stock = sum(_stock_tris(r[:4], r[4], r[5]) for r in got["stock_regions"])
    elif sp == "cocktail_table":
        stock = sum(_stock_tris(r[:4], r[4], None) for r in got["stock_regions"])
    assert P.tri_count(got["prims"]) + stock <= budget, (P.tri_count(got["prims"]), stock, budget)


def _stock_tris(rect, z0, facing):
    worst = 0
    for seed in range(8):
        got = S.plan_surface(random.Random(seed), "bar", *rect, z0, facing=facing)
        worst = max(worst, P.tri_count(got["prims"]))
    return worst


def test_the_longest_name_is_the_neon_budget():
    budget = genome_mod.load_species("neon_sign")["budgets"]["tris_lod0"]
    worst = max(P.tri_count(NF.plan_sign(1.4, 0.1, 0.6, v)["prims"]) for v in range(len(CN.NAMES)))
    assert worst <= budget
    assert worst > 0.9 * budget, "the budget is the measured worst name, not a guess"


@pytest.mark.parametrize("sp,form", [("club_stage", "round"), ("club_stage", "bar_stage"),
                                     ("cocktail_table", "cloth"), ("club_chair", "auto"),
                                     ("bar_stool", "auto")])
def test_a_plan_is_the_same_plan_every_time(sp, form):
    dims = _corners(sp)[len(_corners(sp)) // 2]
    a, b = _plan(sp, dims, form, seed=7), _plan(sp, dims, form, seed=7)
    assert a["prims"] == b["prims"]


def test_seeds_change_what_the_seed_is_for():
    cloths = {tuple(CF.plan_table(0.75, 0.75, 0.74, random.Random(s))["cloth_rgb"]) for s in range(30)}
    velvets = {tuple(CF.plan_chair(0.78, 0.75, 0.78, random.Random(s))["velvet_rgb"]) for s in range(30)}
    seats = {tuple(CF.plan_stool(0.42, 0.42, 0.76, random.Random(s))["seat_rgb"]) for s in range(30)}
    assert len(cloths) == len(CF.CLOTHS) and len(velvets) == len(CF.VELVETS) and len(seats) == len(CF.SEATS)


# --- the stage ---------------------------------------------------------------


@pytest.mark.parametrize("h,platform,rail,pole", [
    (0.45, 0.45, None, None), (0.8, 0.8, None, None), (0.9, 0.9, None, None),
    (1.0, 0.64, 1.0, None), (1.16, 0.8, 1.16, None), (1.5, 0.8, 1.16, 1.5), (3.6, 0.8, 1.16, 3.6)])
def test_the_stage_heights_follow_the_slot(h, platform, rail, pole):
    got = CF.stage_heights(h)
    assert got[0] == pytest.approx(platform)
    assert (got[1] is None) == (rail is None) and (rail is None or got[1] == pytest.approx(rail))
    assert (got[2] is None) == (pole is None) and (pole is None or got[2] == pytest.approx(pole))


def test_steps_are_the_fewest_that_keep_a_walkable_ramp():
    """A ramp over the steps must stay under `floor_max_angle` (45) -- the
    agent contract's reason Deli Counter gives stairs a smooth collider."""
    for k in range(46):
        p = 0.45 + 0.01 * k
        n = CF.n_steps(p)
        assert 1 <= n <= CF.MAX_STEPS
        assert CF.step_pitch_deg(p) <= CF.MAX_PITCH_DEG + 1e-9, p
        if n > 1:
            assert math.degrees(math.atan2(p, (n - 1) * CF.TREAD)) > CF.MAX_PITCH_DEG


def test_auto_is_round_when_squarish_and_a_runway_when_long_never_a_bar():
    assert CF.pick_stage_form("auto", 4.0, 4.0 + 3 * CF.TREAD, 3.6) == "round"
    assert CF.pick_stage_form("auto", 8.0, 4.0, 0.8) == "runway"
    assert all(CF.pick_stage_form("auto", w, d, 3.6) != "bar_stage"
               for w in (2.0, 5.0, 14.0) for d in (2.0, 5.0, 8.0))


@pytest.mark.parametrize("form", ("round", "runway", "bar_stage"))
def test_a_tall_stage_has_its_poles_to_the_slot_top_and_a_low_one_none(form):
    tall = CF.plan_stage(8.0, 4.0, 3.6, random.Random(0), form)
    low = CF.plan_stage(8.0, 4.0, 0.8, random.Random(0), form)
    assert tall["poles"] and tall["pole_top"] == 3.6
    top = max(v[2] for p in tall["prims"] if p["part"] == "Stage_Pole" for v in p["verts"])
    assert top == pytest.approx(3.6)
    assert not low["poles"] and not any(p["part"] == "Stage_Pole" for p in low["prims"])


def test_the_rail_has_a_gap_where_the_steps_come_up():
    got = CF.plan_stage(4.0, 4.0, 3.6, random.Random(0), "round")
    steps = [v for p in got["prims"] if p["part"] == "Stage_Steps" for v in p["verts"]]
    sx0, sx1 = min(v[0] for v in steps), max(v[0] for v in steps)
    front = max(v[1] for v in steps)
    rail = [v for p in got["prims"] if p["part"] in ("Stage_Rail", "Stage_RailPosts") for v in p["verts"]]
    assert rail and got["posts"] >= 4
    assert not any(sx0 < v[0] < sx1 and v[1] < front + 0.3 for v in rail)


def test_every_stage_lights_its_lip_and_every_step():
    got = CF.plan_stage(4.0, 4.0, 3.6, random.Random(0), "round")
    ropes = [p for p in got["prims"] if p["mat"] == "rope"]
    step_tops = {round(max(v[2] for v in p["verts"]), 4) for p in got["prims"] if p["part"] == "Stage_Steps"}
    rope_zs = [max(v[2] for v in p["verts"]) for p in ropes]
    for t in step_tops:
        assert any(abs(z - t) < 0.02 for z in rope_zs), t
    assert "rope" in CF.STAGE_EMISSIVE and all(p["part"] == "Stage_RopeLight" for p in ropes)


def test_a_bar_stage_is_a_bar_round_a_raised_deck():
    got = CF.plan_stage(8.0, 4.0, 3.6, random.Random(0), "bar_stage")
    parts = {p["part"] for p in got["prims"]}
    assert {"Bar_Top", "Bar_Armrest", "Bar_FootRail", "Bar_Fascia", "Stage_Carpet",
            "Stage_RopeLight", "Stage_Pole"} <= parts
    assert got["bar_top"] < got["platform"] == CF.BAR_DECK
    assert len(got["poles"]) == 2 and len(got["stock_regions"]) == 2
    got2 = CF.plan_stage(4.0, 3.0, 3.6, random.Random(0), "bar_stage")
    assert len(got2["poles"]) == 1


# --- the table ----------------------------------------------------------------


@pytest.mark.parametrize("form", CF.TABLE_FORMS)
def test_bar_stock_never_leaves_the_round_top(form):
    for dims in _corners("cocktail_table"):
        got = CF.plan_table(*dims, random.Random(1), form)
        r = got["top_radius"]
        for seed in range(6):
            rng = random.Random(seed)
            for x0, x1, y0, y1, z0 in got["stock_regions"]:
                st = S.plan_surface(rng, "bar", x0, x1, y0, y1, z0, host_rgb=got["cloth_rgb"])
                for x, y in P.footprint_xy(st["prims"]):
                    assert math.hypot(x / (dims[0] / 2) * r, y / (dims[1] / 2) * r) <= r


def test_a_cloth_reaches_the_floor_and_a_bare_table_shows_its_base():
    cloth = CF.plan_table(0.75, 0.75, 0.74, random.Random(0), "cloth")
    bare = CF.plan_table(0.75, 0.75, 0.74, random.Random(0), "bare")
    assert {p["part"] for p in cloth["prims"]} == {"Table_Cloth"}
    assert {"Table_Top", "Table_Base"} <= {p["part"] for p in bare["prims"]}
    assert CF.pick_table_form("auto") == "cloth"


# --- chair and stool ------------------------------------------------------------


def test_the_tub_chairs_back_is_highest_behind_and_falls_to_the_arms():
    got = CF.plan_chair(0.78, 0.75, 0.78, random.Random(0))
    back = [v for p in got["prims"] if p["part"] == "ClubChair_Back" for v in p["verts"]]
    behind = max(v[2] for v in back if v[1] > 0.25)
    front = max(v[2] for v in back if v[1] < -0.1)
    assert behind == pytest.approx(0.78) and front < behind - 0.1
    assert got["seat_z"] < front


def test_a_stool_has_a_footring_you_can_reach():
    got = CF.plan_stool(0.42, 0.42, 0.76, random.Random(0))
    assert 0.18 <= got["ring_z"] <= 0.76 - 0.35
    assert {"BarStool_Footring", "BarStool_Column", "BarStool_Seat"} <= {p["part"] for p in got["prims"]}


# --- the neon sign and its names --------------------------------------------


def test_the_genome_variants_are_the_name_table():
    assert genome_mod.load_species("neon_sign")["module_variants"] == len(CN.NAMES)
    assert len(set(CN.NAMES)) == len(CN.NAMES)
    assert [CN.name_for(v) for v in range(len(CN.NAMES))] == list(CN.NAMES)


def test_every_name_is_spelled_from_the_font_and_is_on_no_denylist():
    for name in CN.NAMES:
        assert name == name.upper() and name.strip() == name
        assert set(name) <= set(NF.FONT_5X7), name
        for bad in CN.DENYLIST:
            assert bad not in name, (name, bad)


def test_the_denylist_can_fail():
    assert any(bad in "LOU TURK'S" for bad in CN.DENYLIST)


def test_the_font_copy_matches_pixelcoat_when_it_is_beside_this_repo():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    roots = [os.environ.get("GABAGOOL_FACTORY", ""), os.path.dirname(here)]
    src = None
    for r in roots:
        p = os.path.join(r, "pixelcoat", "pixelcoat", "core", "signage.py")
        if r and os.path.isfile(p):
            src = open(p, encoding="utf-8").read()
            break
    if src is None:
        pytest.skip("pixelcoat is not beside this repo (set GABAGOOL_FACTORY)")
    body = src[src.index("_FONT = {"):src.index("}", src.index("_FONT = {"))]
    theirs = dict(re.findall(r'"(.)": (\[[^\]]*\])', body))
    assert len(theirs) == len(NF.FONT_5X7)
    for ch, rows in theirs.items():
        assert eval(rows) == NF.FONT_5X7[ch], ch   # a literal list of strings


@pytest.mark.parametrize("ch", sorted(set("".join(CN.NAMES)) - {" "}))
def test_a_glyph_skeleton_covers_every_lit_pixel_and_no_dark_one(ch):
    runs, dots = NF.glyph_runs(ch)
    rows = NF.FONT_5X7[ch]
    lit = {(c, r) for r in range(7) for c in range(5) if rows[r][c] == "1"}
    covered = set(dots)
    for (c0, r0), (c1, r1) in runs:
        n = max(abs(c1 - c0), abs(r1 - r0))
        for k in range(n + 1):
            covered.add((c0 + (c1 - c0) * k // n, r0 + (r1 - r0) * k // n))
    assert covered == lit


def test_long_names_break_into_lines_and_short_ones_do_not():
    assert NF.plan_sign(1.4, 0.1, 0.6, CN.NAMES.index("LIVE GIRLS"))["lines"] == ["LIVE", "GIRLS"]
    assert len(NF.plan_sign(1.4, 0.1, 0.6, CN.NAMES.index("BOTTOMS UP ON BALTIMORE PIKE"))["lines"]) == 3
    assert NF.plan_sign(3.0, 0.1, 0.45, CN.NAMES.index("LIVE GIRLS"))["lines"] == ["LIVE GIRLS"]


@pytest.mark.parametrize("dims", [(1.0, 0.06, 0.45), (1.4, 0.1, 0.6), (3.0, 0.25, 1.2), (3.0, 0.06, 0.45)])
def test_every_name_builds_clean_at_the_corners(dims):
    for v in range(len(CN.NAMES)):
        got = NF.plan_sign(*dims, variant=v)
        _exact(got["prims"], *dims)
        assert P.coincident_pairs(got["prims"]) == [], (v, got["text"])
        assert {p["mat"] for p in got["prims"] if p["part"] in ("NeonSign_Tubes", "NeonSign_Border")} \
            == {"text", "border"}


# --- crt_tv bracket ----------------------------------------------------------------


@pytest.mark.parametrize("dims", [(0.35, 0.35, 0.3), (0.55, 0.62, 0.5), (0.9, 0.62, 0.7), (0.35, 0.62, 0.7),
                                  (0.9, 0.35, 0.3)])
def test_a_bracket_tv_claims_its_slot_tipped_toward_the_room(dims):
    got = KF.plan_bracket(*dims)
    _exact(got["prims"], *dims)
    assert got["overshoot_m"] < 1e-4
    assert P.coincident_pairs(got["prims"]) == []
    screen = [v for p in got["prims"] if p["part"] == "CRT_Screen" for v in p["verts"]]
    top = [v for v in screen if v[2] > got["screen_centre"][2]]
    bottom = [v for v in screen if v[2] < got["screen_centre"][2]]
    # tipped: the screen's top edge stands further into the room than its bottom
    assert min(v[1] for v in top) < min(v[1] for v in bottom)
    plate = [v for p in got["prims"] if p["part"] == "CRT_Bracket" for v in p["verts"]]
    assert max(v[1] for v in plate) == pytest.approx(dims[1] / 2)
    assert KF.pick_form("auto") == "stand"
