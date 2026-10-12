"""utility_pole: the wooden distribution pole (roadmap 240, Zoo 1.104.0).

Pure Python: `core.utility_pole_forms` is what the recipe builds vertex for
vertex (`bpylayer.prim_mesh`), so the extents, the faces, the materials and
the numbers Lot mirrors are measured here without Blender.
"""
import pytest

from zoo_keeper.core import genome, kit
from zoo_keeper.core import prims as P
from zoo_keeper.core import utility_pole_forms as F


def test_utility_pole_is_discovered_and_validates():
    assert "utility_pole" in genome.list_species()
    assert genome.validate_genome(genome.load_species("utility_pole")) == []


@pytest.mark.parametrize("form", F.FORMS)
def test_each_form_plans_at_its_module_dims_and_keeps_its_form(form):
    w, d, h = F.MODULE_DIMS[form]
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "utility_pole_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "utility_pole", "form": form,
        "fit": {"dims": [w, d, h], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan.get("dressing_fallbacks", []) == []
    m = plan["modules"][0]
    assert m["species"] == "utility_pole"
    # `kit.honour_dressing` reads `auto` as no form at all: the plain module,
    # which the recipe builds as `auto`; any other form rides on the module
    assert m.get("form") == (None if form == "auto" else form)


def test_the_numbers_lot_mirrors_are_these():
    """Lot's `site_furniture` mirrors these (neither repo can import the
    other): a change here fails this test before it moves a level, and Lot's
    own test pins the same literals."""
    assert F.MODULE_DIMS == {"auto": (0.3, 3.67, 10.4),
                             "transformer": (0.46, 3.67, 10.4)}
    assert F.POLE_AT == {"auto": (0.0, 0.615), "transformer": (0.0, 0.615)}
    assert F.LENS_AT == (-2.171, 7.401)
    assert F.WIRES == {"primary_0": (-1.07, 10.297), "primary_1": (-0.41, 10.297),
                       "primary_2": (1.07, 10.297), "neutral": (0.24, 9.3),
                       "secondary": (0.24, 7.95), "comm_0": (0.24, 6.4),
                       "comm_1": (0.24, 6.0)}


@pytest.mark.parametrize("form", F.FORMS)
def test_the_plan_fills_its_slot_exactly(form):
    w, d, h = F.MODULE_DIMS[form]
    got = F.plan(w, d, h, form)
    assert got["overshoot_m"] < 1e-4
    lo, hi = P.bounds(got["prims"])
    for a, (want_lo, want_hi) in enumerate(((-w / 2, w / 2), (-d / 2, d / 2), (0.0, h))):
        assert abs(lo[a] - want_lo) < 1e-6 and abs(hi[a] - want_hi) < 1e-6, (a, lo, hi)


@pytest.mark.parametrize("form", F.FORMS)
def test_no_two_faces_coincide(form):
    got = F.plan(*F.MODULE_DIMS[form], form)
    assert P.coincident_pairs(got["prims"]) == []


@pytest.mark.parametrize("form", F.FORMS)
def test_four_materials_whatever_it_carries(form):
    got = F.plan(*F.MODULE_DIMS[form], form)
    assert {p["mat"] for p in got["prims"]} == {"wood", "steel", "porcelain", "lens"}


@pytest.mark.parametrize("form", F.FORMS)
def test_the_collision_is_the_pole_alone(form):
    w, d, h = F.MODULE_DIMS[form]
    got = F.plan(w, d, h, form)
    assert len(got["collision"]) == 1
    (x0, y0, z0), (x1, y1, z1) = got["collision"][0]
    px, py = F.POLE_AT[form]
    r = F.POLE_D_BASE / 2.0
    assert (round(x0, 6), round(x1, 6)) == (round(px - r, 6), round(px + r, 6))
    assert (round(y0, 6), round(y1, 6)) == (round(py - r, 6), round(py + r, 6))
    assert (z0, z1) == (0.0, h)


def test_the_lens_hangs_under_the_head_toward_the_road():
    w, d, h = F.MODULE_DIMS["auto"]
    got = F.plan(w, d, h, "auto")
    lens = [p for p in got["prims"] if p["mat"] == "lens"]
    assert len(lens) == 1
    (lx0, ly0, lz0), (lx1, ly1, lz1) = P.bounds(lens)
    px, py = F.POLE_AT["auto"]
    ly, lz = F.LENS_AT
    assert abs((ly0 + ly1) / 2.0 - (py + ly)) < 1e-6      # where Lot hangs the light
    assert abs(lz0 - lz) < 1e-6
    assert py + ly < py - 2.0                             # two metres toward the road
    head_bottom = F.LAMP_MOUNT_Z + F.LAMP_RISE - F.HEAD_H / 2.0
    assert head_bottom - lz1 >= 0.003                     # hovering, not touching


def test_the_wires_stack_so_a_span_clears_the_road():
    """Lowest to highest: the cables, the cobra-head, the secondary, the
    can's bottom, the neutral, the primaries -- and the lowest cable stands
    high enough to clear 4.7 m (NESC, communication over a road) at the
    middle of a span Lot sags a few percent."""
    comm = min(z for name, (y, z) in F.WIRES.items() if name.startswith("comm"))
    head_top = F.LAMP_MOUNT_Z + F.LAMP_RISE + F.HEAD_H / 2.0
    assert max(F.COMM_Z) < F.LAMP_MOUNT_Z < head_top < F.SECONDARY_Z
    assert F.SECONDARY_Z + F.SPOOL_H < F.CAN_TOP_Z - F.CAN_H < F.CAN_TOP_Z < F.NEUTRAL_Z
    assert F.NEUTRAL_Z < F.WIRES["primary_0"][1] < F.POLE_H
    assert comm - 0.02 * 36.0 >= 4.7


@pytest.mark.parametrize("form", F.FORMS)
def test_within_its_triangle_budget(form):
    got = F.plan(*F.MODULE_DIMS[form], form)
    assert got["facts"]["tris"] <= genome.load_species("utility_pole")["budgets"]["tris_lod0"]


def test_an_unknown_form_says_so():
    with pytest.raises(ValueError):
        F.pick_form("streetlight")
    assert F.pick_form(None) == "auto"
