"""The interior species (0.84.0): carton_stack, furnace, dust_sheet,
pool_table, booth_seat.

"Need a lot more species for this room, its just a bunch of chairs and
tables with nothing on it, boring" (the walker, in a country_club_a01
basement, cold run 9052).

Each species is planned in pure Python (`core/*_forms.py`) as the same
vertex and face lists `bpylayer.prim_mesh` builds, so these measure what
ships, before the recipe's bevel:

  * the DIMS CONTRACT -- bounds exactly the slot's w x d x h, base-up;
  * DETERMINISM -- one rng seed, one plan; different seeds, different plans;
  * ZERO COINCIDENT FACES -- `prims.coincident_pairs`, the pure port of
    tools/coplanar_probe.py at its defaults (2 mm, 1 mm^2), SAME and OPP;
  * the BUDGET -- pre-bevel triangles against the genome's tris_lod0 (the
    beveled counts, measured in Blender, are in each genome's notes and in
    tests/test_interior_bpy.py);
  * the FIT the planner took back with `prims.fit_exact`, so a planner that
    misses the slot by centimetres and is squeezed into it fails here.

Sizes are each genome's min, default and max corners plus the ones the
renders were judged at.
"""
from __future__ import annotations

import json
import os
import random

import pytest

from zoo_keeper.core import (booth_forms, carton_forms, drape_forms, furnace_forms,
                             genome, intent, kit, pool_table_forms)
from zoo_keeper.core import prims as P

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECIES = ("carton_stack", "furnace", "dust_sheet", "pool_table", "booth_seat")


def _g(sp):
    return json.load(open(os.path.join(_ZOO, "zoo_keeper", "genome", "species",
                                       sp + ".json"), encoding="utf-8"))


def _corners(sp):
    d = _g(sp)["dimensions"]
    out = []
    for k in ("min", "default", "max"):
        out.append((d["width"][k], d["depth"][k], d["height"][k]))
    return out


def _plan(sp, dims, seed, form=None):
    rng = random.Random(seed)
    w, d, h = dims
    if sp == "carton_stack":
        return carton_forms.plan(w, d, h, rng)
    if sp == "furnace":
        return furnace_forms.plan(w, d, h, form or "auto")
    if sp == "dust_sheet":
        return drape_forms.plan(w, d, h, rng)
    if sp == "pool_table":
        return pool_table_forms.plan(w, d, h, rng)
    return booth_forms.plan(w, d, h, rng, form or "auto")


def _cases():
    extra = {
        "carton_stack": [(1.2, 0.8, 1.4), (0.5, 0.45, 1.8), (0.7, 1.2, 0.6)],
        "furnace": [(0.9, 1.0, 2.4), (0.6, 0.6, 2.4), (1.2, 1.2, 3.0)],
        "dust_sheet": [(2.0, 0.9, 0.85), (1.2, 0.6, 1.8), (0.9, 0.9, 1.0)],
        "pool_table": [(2.4, 1.35, 0.8)],
        "booth_seat": [(2.4, 1.4, 1.2), (2.0, 0.9, 0.85), (1.4, 0.8, 0.75)],
    }
    forms = {"furnace": furnace_forms.FORMS, "booth_seat": booth_forms.FORMS}
    out = []
    for sp in SPECIES:
        for dims in _corners(sp) + extra[sp]:
            for form in forms.get(sp, (None,)):
                out.append((sp, dims, form))
    return out


CASES = _cases()
SEEDS = range(6)


def _ids(c):
    return "%s-%s-%s" % (c[0], "x".join(str(v) for v in c[1]), c[2] or "auto")


@pytest.mark.parametrize("case", CASES, ids=_ids)
def test_dims_contract(case):
    sp, (w, d, h), form = case
    for seed in SEEDS:
        got = _plan(sp, (w, d, h), seed, form)
        lo, hi = P.bounds(got["prims"])
        assert max(abs(lo[0] + w / 2), abs(hi[0] - w / 2), abs(lo[1] + d / 2),
                   abs(hi[1] - d / 2), abs(lo[2]), abs(hi[2] - h)) < 1e-9, (seed, lo, hi)
        # fit_exact is for details a few mm proud, not for a plan that missed
        assert got["overshoot_m"] <= 0.012, (seed, got["overshoot_m"])
        for a, b in got["collision"]:
            assert all(lo[k] - 1e-9 <= a[k] <= b[k] <= hi[k] + 1e-9 for k in range(3))


@pytest.mark.parametrize("case", CASES, ids=_ids)
def test_no_coincident_faces(case):
    sp, dims, form = case
    for seed in SEEDS:
        rows = P.coincident_pairs(_plan(sp, dims, seed, form)["prims"])
        assert rows == [], (seed, rows[:4])


@pytest.mark.parametrize("case", CASES, ids=_ids)
def test_budget_before_bevel(case):
    sp, dims, form = case
    budget = _g(sp)["budgets"]["tris_lod0"]
    for seed in SEEDS:
        assert P.tri_count(_plan(sp, dims, seed, form)["prims"]) <= budget


@pytest.mark.parametrize("sp", SPECIES)
def test_same_seed_same_plan(sp):
    dims = _corners(sp)[1]
    assert _plan(sp, dims, 11) == _plan(sp, dims, 11)


@pytest.mark.parametrize("sp", ("carton_stack", "dust_sheet", "pool_table", "booth_seat"))
def test_seeds_make_different_pieces(sp):
    """`module_variants` is 4 for these: the variant index is the seed, so
    the seed must actually change the geometry."""
    dims = _corners(sp)[1]
    digests = {json.dumps(_plan(sp, dims, s)["prims"]) for s in range(4)}
    assert len(digests) == 4


def test_furnace_auto_form_reads_the_footprint():
    assert furnace_forms.pick_form("auto", 0.6, 0.6) == "water_heater"
    assert furnace_forms.pick_form("auto", 0.9, 1.0) == "furnace"
    assert furnace_forms.pick_form("water_heater", 1.2, 1.2) == "water_heater"


def test_booth_auto_form_reads_the_height_and_depth():
    assert booth_forms.pick_form("auto", 1.8, 0.75, 1.15) == "booth"
    assert booth_forms.pick_form("auto", 2.0, 0.9, 0.85) == "sofa"
    assert booth_forms.plan(2.4, 1.4, 1.2, random.Random(0))["sides"] == 2
    assert booth_forms.plan(1.8, 0.75, 1.15, random.Random(0))["sides"] == 1


def test_dust_sheet_draws_every_profile():
    seen = set()
    for dims in ((0.9, 0.9, 1.0), (2.0, 0.9, 0.85), (1.2, 0.6, 1.8), (1.0, 0.8, 0.6)):
        for s in range(30):
            seen.add(drape_forms.plan(*dims, random.Random(s))["profile"])
    assert seen == set(drape_forms.PROFILES)


def test_carton_stack_draws_both_boxes():
    parts = set()
    for s in range(20):
        parts |= {p["part"] for p in carton_forms.plan(1.2, 0.8, 1.4, random.Random(s))["prims"]}
    assert {"Carton_Body", "Carton_Tape", "Banker_Body", "Banker_Lid"} <= parts


@pytest.mark.parametrize("sp", SPECIES)
def test_genome_recipe_and_keywords(sp):
    g = genome.load_species(sp)
    assert genome.validate_genome(g) == []
    assert os.path.exists(os.path.join(_ZOO, "zoo_keeper", "recipes", sp + ".py"))
    assert "delco" in g["styles"]
    assert intent.parse(sp.replace("_", " ")).species == sp


@pytest.mark.parametrize("words,sp", [
    ("cardboard boxes", "carton_stack"), ("water heater", "furnace"),
    ("boiler", "furnace"), ("drop cloth", "dust_sheet"),
    ("billiards", "pool_table"), ("pool table", "pool_table"),
    ("couch", "booth_seat"), ("booth", "booth_seat"),
    ("phone booth", "payphone"), ("table", "table")])
def test_keywords_route(words, sp):
    assert intent.parse(words).species == sp


def test_forms_ride_the_kit_as_slot_fields():
    """A slot's `form` reaches the stem and the module when the species
    lists it, and a form it does not list drops the dressing, said."""
    plan = kit.plan_kit({"building_id": "t", "slots": [
        {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1,
         "species": "furnace", "form": "water_heater",
         "fit": {"dims": [0.9, 1.0, 2.4], "pivot": "center"}},
        {"slot_id": "b", "role": "prop", "size_mod": "full", "style": 1,
         "species": "booth_seat", "form": "water_heater",
         "fit": {"dims": [1.8, 0.75, 1.15], "pivot": "center"}}]},
        theme="delco_1997", style=1)
    stems = sorted(m["stem"] for m in plan["modules"])
    assert stems == ["prop_booth_seat_delco_1997_01_w180_d75_h115",
                     "prop_furnace_delco_1997_01_w90_d100_h240_fwater_heater"]
    assert [f["slot_id"] for f in plan["dressing_fallbacks"]] == ["b"]
