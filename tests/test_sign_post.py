"""sign_post: a u-channel post and the blade it carries (0.96.0).

Minted 2026-09-12 by tools/new_species.py as a placeholder box; drawn here.
The first two tests are the ones that were here before and still hold -- the
species is discovered, validates, and plans at the authored dims -- and
everything below them fails on 0.95.0, where `sign_blade_forms` does not
exist and the genome lists no forms.

The measurements are the interior species' (`tests/test_interior_species.py`):
the dims contract, zero coincident faces at the coplanar probe's own
defaults, the budget before bevel, and determinism. What is added here is
the pipe: the slot dims Lot writes have to be INSIDE this genome's ranges or
`plan_kit` sends the post back to the greybox box, and the stem has to carry
`_f<form>` or Lot resolves a name that was never built.
"""
from __future__ import annotations

import json
import os

import pytest

from zoo_keeper.core import genome, kit
from zoo_keeper.core import prims as P
from zoo_keeper.core import sign_blade_forms as F

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _g():
    return json.load(open(os.path.join(_ZOO, "zoo_keeper", "genome", "species",
                                       "sign_post.json"), encoding="utf-8"))


def _corners():
    d = _g()["dimensions"]
    return [(d["width"][k], d["depth"][k], d["height"][k])
            for k in ("min", "default", "max")]


def _sweep():
    """Every genome corner against every form, each form at the slot Lot
    actually writes for it, and the bare pole.

    A corner is CLAMPED to the form's own `min_width`: this genome spans a
    bare pole at 0.09 m and a 30 in diamond at 1.08 m, so its minimum width
    is not a width every form can be drawn at, and sweeping the union would
    measure a sign nothing can ask for. `test_lot_never_asks_below_the_floor`
    is what keeps that from being an excuse.
    """
    out = []
    for w, d, h in _corners():
        for form in F.FORMS + (None,):
            out.append(((max(w, F.min_width(form)), d, h), form))
    out += [(F.MODULE_DIMS[f], f) for f in F.FORMS]
    out.append(((0.1, 0.1, 2.4), None))
    return out


CASES = _sweep()


def _ids(c):
    return "%s-%s" % ("x".join("%.4g" % v for v in c[0]), c[1] or "bare")


def test_sign_post_is_discovered_and_validates():
    assert "sign_post" in genome.list_species()
    assert genome.validate_genome(genome.load_species("sign_post")) == []


def test_sign_post_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "sign_post_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "sign_post",
        "fit": {"dims": [0.1, 0.1, 2.4], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "sign_post"


@pytest.mark.parametrize("case", CASES, ids=_ids)
def test_dims_contract(case):
    (w, d, h), form = case
    got = F.plan(w, d, h, form)
    lo, hi = P.bounds(got["prims"])
    assert max(abs(lo[0] + w / 2), abs(hi[0] - w / 2), abs(lo[1] + d / 2),
               abs(hi[1] - d / 2), abs(lo[2]), abs(hi[2] - h)) < 1e-9, (lo, hi)
    # the ladder is nailed to the slot's front face, so there is nothing for
    # `fit_exact` to take back on ANY form -- see `sign_blade_forms._base`
    assert got["overshoot_m"] == 0.0
    for a, b in got["collision"]:
        assert all(lo[k] - 1e-9 <= a[k] <= b[k] <= hi[k] + 1e-9
                   for k in range(3))


@pytest.mark.parametrize("case", CASES, ids=_ids)
def test_no_coincident_faces(case):
    (w, d, h), form = case
    rows = P.coincident_pairs(F.plan(w, d, h, form)["prims"])
    assert rows == [], rows[:4]


@pytest.mark.parametrize("case", CASES, ids=_ids)
def test_budget_before_bevel(case):
    (w, d, h), form = case
    budget = _g()["budgets"]["tris_lod0"]
    assert P.tri_count(F.plan(w, d, h, form)["prims"]) <= budget


def test_the_collider_is_the_post_and_only_the_post():
    """One box, no wider than the channel, and stopping below the sign: a
    body walks into a pole, never into a blade two metres over its head."""
    for form in F.FORMS:
        w, d, h = F.MODULE_DIMS[form]
        got = F.plan(w, d, h, form)
        assert len(got["collision"]) == 1
        (ax, _ay, az), (bx, _by, bz) = got["collision"][0]
        assert bx - ax <= F.POST_W + 1e-9
        assert az == 0.0 and bz < h


def test_the_post_bevel_is_capped_by_the_flange():
    """MEASURED ON THE BUILT GLB, which is the only place it showed. At the
    styles' own 0.006 the bevel ate the 8 mm flange and 32 of the post's 132
    triangles came out ZERO-AREA on the no-parking module, 28 on the other
    two -- a quarter of the post drawing nothing on every client. Neither
    `prims.tri_count` nor `build_module`'s tally counts a bevel, so the only
    signal was `tools/coplanar_probe.py` reporting fewer triangles than the
    GLB has, because it skips a degenerate normal.
    """
    for name, style in _g()["styles"].items():
        assert F.post_bevel(style["bevel"]) <= F.FLANGE_T * 0.25, name
    assert F.post_bevel(0.006) == 0.002
    assert F.post_bevel(0.001) == 0.001
    assert F.post_bevel(None) == 0.0


def test_the_module_dims_are_the_mutcd_arithmetic():
    """The sizes are the standard and the box is what they add up to. Lot
    writes these numbers from its own table (`site_furniture.BLADE_DIMS`)
    and cannot import this one, so both sides are pinned to literals."""
    got = {k: tuple(round(v, 4) for v in dims)
           for k, dims in F.MODULE_DIMS.items()}
    assert got == {"no_parking": (0.3048, 0.06, 2.4384),
                   "ped_crossing": (1.0776, 0.06, 3.2112),
                   "bus_stop": (0.3048, 0.06, 2.5908)}


@pytest.mark.parametrize("form", F.FORMS)
def test_every_form_lot_names_fits_this_genome(form):
    """The slot Lot writes has to be inside the ranges or `_species_fit`
    sends the post back to the `prop` box. 0.95.0's ranges (0.09..0.125 wide,
    2.16..3.0 tall) admit none of the three."""
    w, d, h = F.MODULE_DIMS[form]
    dims = _g()["dimensions"]
    for key, val in (("width", w), ("depth", d), ("height", h)):
        assert dims[key]["min"] <= val <= dims[key]["max"], (form, key, val)


def test_lot_never_asks_below_the_floor():
    """The per-form floor only means anything if the sizes Lot writes are
    above it -- otherwise it is a way of not measuring. Three times over on
    the one form that has a floor at all."""
    for form in F.FORMS:
        assert F.MODULE_DIMS[form][0] >= 3.0 * F.min_width(form)
    assert F.min_width("bus_stop") == 0.097
    assert F.min_width("no_parking") == 0.0


def test_the_flag_legend_gap_is_what_sets_that_floor():
    """The floor is derived, so the derivation is the test: one hair under
    it, two letters of the flag stand within the coplanar tolerance."""
    w = F.min_width("bus_stop") * 0.92
    rows = P.coincident_pairs(F.plan(w, 0.06, 2.6, "bus_stop")["prims"])
    assert [r["a"] for r in rows] == ["SignPost_Legend"]
    assert rows[0]["gap_mm"] < 2.0


def test_the_genome_lists_exactly_the_forms_the_planner_builds():
    """`auto` first and then the three blades, in that order. The order is
    the contract -- see the next test."""
    assert tuple(_g()["params"]["form"]) == ("auto",) + F.FORMS


def test_an_undressed_post_is_still_a_bare_pole():
    """THE ONE THAT WAS CAUGHT IN A FRAME. `dna._default_params` takes a
    list param's FIRST entry as the canonical default, so a `sign_post`
    module carrying no form takes whatever heads the genome's list. With the
    three blades alone in it, every plain post in the library -- and every
    specimen preview -- built a No Parking sign at the pole's own 0.1 m,
    while its stem said `w10_d10_h240` with no `_f` on it. The suite did not
    see it because every other test calls `plan` directly; this one goes the
    way a build goes.
    """
    from zoo_keeper.core import dna
    params = dna._default_params(genome.load_species("sign_post"))
    assert params["form"] == "auto"
    assert F.pick_form(params["form"]) is None
    assert F.plan(0.1, 0.1, 2.4, params["form"])["form"] is None


def test_auto_and_an_unknown_blade_both_mean_the_bare_pole():
    assert F.pick_form("auto") is None
    assert F.pick_form(None) is None
    assert F.pick_form("street_name") is None
    assert F.pick_form("no_parking") == "no_parking"


def test_the_bare_pole_is_still_the_pole():
    """A slot with no form is what every `sign_post` was until now, and it
    keeps its own section rather than being a squeezed blade post."""
    got = F.plan(0.1, 0.1, 2.4, None)
    assert got["form"] is None
    assert {p["part"] for p in got["prims"]} == {"SignPost_Post"}


def test_the_forms_reach_the_stem_and_the_module():
    """THE PIPE, both halves. A slot carrying Lot's blade as `form` plans a
    module whose stem spells `_f<form>`; the same slot on 0.95.0's genome
    dropped the field and planned the plain name, which is what made this a
    two-repo change. `lot.cover_module_stem` constructs the same string.
    """
    slots = []
    for i, form in enumerate(F.FORMS):
        w, d, h = F.MODULE_DIMS[form]
        slots.append({"slot_id": f"cover_{i}", "role": "prop",
                      "size_mod": "full", "style": 1, "species": "sign_post",
                      "form": form,
                      "fit": {"dims": [w, d, h], "pivot": "center"}})
    plan = kit.plan_kit({"building_id": "site", "slots": slots},
                        theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    assert sorted(m["stem"] for m in plan["modules"]) == [
        "prop_sign_post_delco_1997_01_w108_d6_h321_fped_crossing",
        "prop_sign_post_delco_1997_01_w30_d6_h244_fno_parking",
        "prop_sign_post_delco_1997_01_w30_d6_h259_fbus_stop"]


def test_a_form_nobody_built_still_drops_and_says_so():
    """A street-name blade (MUTCD D3-1) is what Lot cannot post yet. When it
    can, the ask must land in the gap report rather than resolving a name."""
    plan = kit.plan_kit({"building_id": "site", "slots": [{
        "slot_id": "cover_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "sign_post", "form": "street_name",
        "fit": {"dims": [0.3048, 0.06, 2.4384], "pivot": "center"}}]},
        theme="delco_1997", style=1)
    assert [f["slot_id"] for f in plan["dressing_fallbacks"]] == ["cover_0"]
    assert plan["modules"][0]["stem"] == \
        "prop_sign_post_delco_1997_01_w30_d6_h244"


def test_same_dims_same_plan():
    w, d, h = F.MODULE_DIMS["ped_crossing"]
    assert F.plan(w, d, h, "ped_crossing") == F.plan(w, d, h, "ped_crossing")


def test_the_y_ladder_keeps_every_rung_clear():
    """The rungs are not neighbours-only: eleven planes all overlap in
    projection, so the smallest gap between ANY two of them is what the
    coplanar probe measures. Three millimetres, and nothing may narrow it."""
    rungs = sorted(F._Y.values())
    gaps = [round((b - a) * 1000.0, 3)
            for a, b in zip(rungs, rungs[1:])]
    assert min(gaps) >= 3.0, gaps
    assert len(set(rungs)) == len(rungs)


def test_the_bus_stop_flag_needs_no_glyph_the_legend_set_lacks():
    """`_legend` leaves K M N V W X Y Z out on purpose (a diagonal stroke
    does not fit its grid). The one blade here that is lettered is spelled
    from what is already there, and that is a constraint on the design
    rather than a coincidence."""
    from zoo_keeper.recipes import _legend
    assert set("BUSSTOP") <= set(_legend.GLYPHS)
    assert not (set("KMNVWXYZ") & set(_legend.GLYPHS))
