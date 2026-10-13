"""stoop_railing (1.105.0): the iron railing either side of a rowhouse stoop.

Factory roadmap 240, the walker's calls of 2026-10-13: "3 risers, concrete, railings both sides --
build the railings". `core.stoop_railing_forms` is the plan, drawn from a slot's box alone in two forms
(a level section along the landing, a flight down the steps); the recipe builds the same lists through
`bpylayer.prim_mesh`. Pure: nothing here needs Blender.
"""
import math

import pytest

from zoo_keeper.core import genome, kit, prims
from zoo_keeper.core import stoop_railing_forms as F

IN = 0.0254
#: the two sections Deli Counter 0.212.0 writes for a three-riser stoop (7 in risers, 11 in treads,
#: a 0.9 m landing): the level along the landing and the flight from its edge to a post on the
#: bottom tread
LEVEL = (0.9, 0.038, 0.9144)
FLIGHT = (0.5248, 0.038, 1.27)
SIZES = [(w, d, h) for w in (0.3, 0.5248, 0.9, 1.4, 2.0)
         for d in (0.03, 0.038, 0.06) for h in (0.85, 0.9144, 1.27, 1.6)]


def test_stoop_railing_is_discovered_and_validates():
    assert "stoop_railing" in genome.list_species()
    g = genome.load_species("stoop_railing")
    assert genome.validate_genome(g) == []
    # Deli Counter writes the railing's colliders: the module carries none
    assert g["collision"] is False
    assert g["params"]["form"] == list(F.FORMS)


@pytest.mark.parametrize("form,dims", [("level", LEVEL), ("flight", FLIGHT)])
def test_both_forms_plan_at_the_sizes_deli_counter_writes(form, dims):
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "stoop_rail_w_" + form, "role": "prop", "size_mod": "full", "style": 1,
        "species": "stoop_railing", "form": form, "material": "metal_painted",
        "fit": {"dims": list(dims), "pivot": "center", "collision": "none"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    (m,) = plan["modules"]
    assert m["species"] == "stoop_railing"
    assert m.get("form") == form, m


def test_the_numbers_are_the_codes():
    # IRC R311.7.8.1: 34 to 38 in over the nosings; R312.1.3: no 4 in sphere through a guard
    assert 34 * IN <= F.RAIL_H <= 38 * IN and abs(F.RAIL_H - 36 * IN) < 1e-4
    assert abs(F.PICKET_CLEAR - 4 * IN) < 1e-4
    # the bottom rail's underside inside the stair's 6 in triangle rule
    assert F.BOTTOM_Z - F.RAIL_T / 2 < 6 * IN


@pytest.mark.parametrize("form", F.FORMS)
@pytest.mark.parametrize("w,d,h", SIZES)
def test_the_extents_are_exactly_the_slots(form, w, d, h):
    got = F.plan(w, d, h, form)
    lo, hi = prims.bounds(got["prims"])
    for a, (want_lo, want_hi) in enumerate(((-w / 2, w / 2), (-d / 2, d / 2), (-h / 2, h / 2))):
        assert math.isclose(lo[a], want_lo, abs_tol=1e-9) and math.isclose(hi[a], want_hi, abs_tol=1e-9)


@pytest.mark.parametrize("form", F.FORMS)
@pytest.mark.parametrize("w,d,h", SIZES)
def test_no_face_lies_on_another(form, w, d, h):
    assert prims.coincident_pairs(F.plan(w, d, h, form)["prims"]) == []


def test_the_coincidence_check_can_see_a_pair():
    """The control: a picket laid with its face on a post's is a pair the probe reports."""
    a = prims.box(F.PART, F.MAT, (0.0, -0.01, 0.0), (0.03, 0.01, 1.0))
    b = prims.box(F.PART, F.MAT, (0.03, -0.008, 0.1), (0.046, 0.008, 0.9))
    assert prims.coincident_pairs([a, b])


@pytest.mark.parametrize("form", F.FORMS)
@pytest.mark.parametrize("w,d,h", SIZES)
def test_every_clear_gap_is_inside_four_inches(form, w, d, h):
    top_w, post, _bottom_w, picket = F.members(d)
    x0, x1 = -w / 2 + post, (w / 2 - post if form == "level" else w / 2)
    xs = F.pickets(x0, x1, picket)
    edges = [x0] + [e for xc in xs for e in (xc - picket / 2, xc + picket / 2)] + [x1]
    gaps = [b - a for a, b in zip(edges[::2], edges[1::2])]
    assert max(gaps) <= F.PICKET_CLEAR + 1e-9, gaps
    assert min(gaps) > 0.0
    # and equal, as a fabricator spaces them
    assert max(gaps) - min(gaps) < 1e-9


def test_the_flight_runs_rail_height_over_its_post_to_the_landing_rail():
    w, d, h = FLIGHT
    got = F.plan(w, d, h, "flight")
    lo, hi = got["facts"]["rail_top"]
    # at the post, RAIL_H over the post's foot (the bottom tread); at the high end, the box's top --
    # where the level section's rail is RAIL_H over the landing
    assert math.isclose(lo, -h / 2 + F.RAIL_H, abs_tol=1e-9)
    assert math.isclose(hi, h / 2, abs_tol=1e-9)
    # a stoop's flight of two 7 in risers on 11 in treads, its post 5 cm onto the bottom tread
    assert 30.0 < got["facts"]["pitch_deg"] < 40.0
    # and the level section's rail is the same height over its landing
    lv = F.plan(*LEVEL, "level")
    assert math.isclose(lv["facts"]["rail_top"][0], LEVEL[2] / 2 - F.POST_PROUD, abs_tol=1e-9)


@pytest.mark.parametrize("form", F.FORMS)
def test_one_material_one_part_one_submission(form):
    got = F.plan(*(LEVEL if form == "level" else FLIGHT), form)
    assert {p["mat"] for p in got["prims"]} == {F.MAT}
    assert {p["part"] for p in got["prims"]} == {F.PART}
    # inside the genome's budget
    assert got["facts"]["tris"] <= genome.load_species("stoop_railing")["budgets"]["tris_lod0"]


def test_an_unknown_form_is_refused_and_auto_is_level():
    assert F.form_of(None) == F.form_of("auto") == "level"
    with pytest.raises(ValueError):
        F.plan(*LEVEL, "spiral")
