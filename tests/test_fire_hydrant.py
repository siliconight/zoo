"""fire_hydrant: minted 2026-09-12 by tools/new_species.py (roadmap 150),
rebuilt as an American dry-barrel hydrant in 0.85.0.

The decisions are pure (`core/hydrant_forms.py`) and tested here without
Blender. The built module -- exact fit at Lot's slot and the genome's corners,
every part, the same module every build, zero coincident same-facing faces,
the triangle budget, the pumper toward -Y -- is the bpy half at the bottom,
skipped without Blender and run inside Blender 5.1 for this change.
"""
import json
import math
import os
import random

import pytest

from zoo_keeper import SEED_EPOCH
from zoo_keeper.core import dna, genome, kit, seeding
from zoo_keeper.core import hydrant_forms as hf

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "fire_hydrant.py")
_GENOME = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "fire_hydrant.json")

#: Lot's `site_furniture.SPECIES["fire_hydrant"]`, the slot every site asks for.
LOT_SLOT = (0.35, 0.35, 0.75)
#: The genome's corners: min, default, max on every axis, and the mixed ones
#: where one axis sets the scale and another takes the slack.
CORNERS = ((0.297, 0.297, 0.637), (0.35, 0.35, 0.75), (0.42, 0.42, 0.9),
           (0.297, 0.42, 0.9), (0.42, 0.297, 0.637), (0.35, 0.35, 0.637),
           (0.35, 0.35, 0.9), (0.42, 0.42, 0.637))
#: `tools/coplanar_probe.py`'s window.
PROBE_TOL = 0.002
#: The count at the genome's worst corner, (0.42, 0.42, 0.637), where the
#: stubs and so the chains are longest: 1,680 (see CHANGELOG). Lot's slot
#: builds 1,416.
TRI_BUDGET = 1700


def _random_dims(n, seed=85):
    rng = random.Random(seed)
    return [(round(rng.uniform(0.297, 0.42), 3), round(rng.uniform(0.297, 0.42), 3),
             round(rng.uniform(0.637, 0.9), 3)) for _ in range(n)]


def _kit(w, d, h, style=1):
    return kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "fire_hydrant_0", "role": "prop", "size_mod": "full",
        "style": style, "species": "fire_hydrant", "material": "metal_painted",
        "fit": {"dims": [w, d, h], "pivot": "center", "collision": "convex"}}]},
        theme="delco_1997", style=style)


def _module_plan(style, dims=LOT_SLOT):
    mod = _kit(*dims, style=style)["modules"][0]
    return mod, dna.resolve_module_plan(mod, genome.load_species("fire_hydrant"),
                                        "delco_1997", style, "0.85.0")


def _streams(stem):
    return seeding.RNGStreams(seeding.root_key(stem, "fire_hydrant", 0, SEED_EPOCH))


def test_fire_hydrant_is_discovered_and_validates():
    assert "fire_hydrant" in genome.list_species()
    assert genome.validate_genome(genome.load_species("fire_hydrant")) == []


def test_fire_hydrant_plans_at_its_authored_dims():
    plan = _kit(*LOT_SLOT)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "fire_hydrant"


def test_lot_asks_for_the_genome_default_and_the_layout_is_nominal_there():
    dims = genome.load_species("fire_hydrant")["dimensions"]
    assert (dims["width"]["default"], dims["depth"]["default"],
            dims["height"]["default"]) == LOT_SLOT == hf.NOMINAL
    L = hf.layout(*LOT_SLOT)
    assert L["k"] == 1.0
    assert math.isclose(L["lower"][1] - L["lower"][0], hf.LOWER_H, abs_tol=1e-9)
    assert math.isclose(L["outlets"]["hose"]["stub"], 0.020, abs_tol=1e-9)
    assert math.isclose(L["outlets"]["pumper"]["stub"], 0.043, abs_tol=1e-9)


# --- layout -------------------------------------------------------------------

@pytest.mark.parametrize("dims", CORNERS + tuple(_random_dims(30)))
def test_the_layout_claims_exactly_the_slot(dims):
    w, d, h = dims
    xmin, xmax, ymin, ymax, zmin, zmax = hf.extents(hf.layout(w, d, h))
    for got, want in ((xmin, -w / 2), (xmax, w / 2), (ymin, -d / 2), (ymax, d / 2),
                      (zmin, -h / 2), (zmax, h / 2)):
        assert math.isclose(got, want, abs_tol=1e-9), (dims, got, want)


@pytest.mark.parametrize("dims", CORNERS)
def test_every_stub_and_the_lower_barrel_keep_their_minimum(dims):
    L = hf.layout(*dims)
    k = L["k"]
    assert L["outlets"]["hose"]["stub"] >= hf.HOSE["stub_min"] * k
    assert L["outlets"]["pumper"]["stub"] >= hf.PUMPER["stub_min"] * k
    assert L["lower"][1] - L["lower"][0] >= 0.08 * k


@pytest.mark.parametrize("dims", [(0.35, 0.35, 0.40), (0.12, 0.9, 0.75), (0.9, 0.12, 2.0)])
def test_a_far_undersized_slot_still_fits(dims):
    """Outside the genome on purpose: the uniform scale leaves every axis at
    least its nominal slack, so the layout is exact and keeps its minimums
    for any positive slot (`layout`'s docstring has the bound)."""
    L = hf.layout(*dims)
    w, d, h = dims
    assert [round(v, 9) for v in hf.extents(L)] == [round(v, 9) for v in (
        -w / 2, w / 2, -d / 2, d / 2, -h / 2, h / 2)]
    assert L["outlets"]["hose"]["stub"] >= hf.HOSE["stub_min"] * L["k"]
    assert L["outlets"]["pumper"]["stub"] >= hf.PUMPER["stub_min"] * L["k"]


def test_the_outlets_stand_at_the_usual_height_and_clear_the_flanges():
    L = hf.layout(*LOT_SLOT)
    assert L["outlet_z"] - L["z0"] >= 0.4572                  # 18 in to the centre
    for o in L["outlets"].values():
        assert L["outlet_z"] - o["cap_r"] > L["upper_flange"][1]
        assert L["outlet_z"] + o["cap_r"] < L["bonnet_flange"][0]


def test_the_pumper_faces_minus_y_and_the_hose_outlets_face_x():
    L = hf.layout(*LOT_SLOT)
    assert L["outlet_dirs"]["pumper"] == (0.0, -1.0)
    assert sorted(L["outlet_dirs"][k] for k in ("hose_pos", "hose_neg")) == [(-1.0, 0.0), (1.0, 0.0)]
    # the pumper is the street-side reach: longer than the collar's back
    assert L["outlets"]["pumper"]["tip"] > L["collar_a"]


def test_the_barrel_tapers_and_every_joint_is_buried_past_the_probe():
    assert hf.LOWER_A[0] > hf.LOWER_A[1]
    assert hf.BURY > PROBE_TOL
    assert hf.SEGMENTS in (10, 12)


@pytest.mark.parametrize("ring,seat,column", [
    (hf.FLANGE_NUTS, hf.FLANGE_A, hf.LOWER_A[0]),
    (hf.UPPER_NUTS, hf.UPPER_FLANGE_A, hf.SECTION_A),
    (hf.BONNET_NUTS, hf.BONNET_FLANGE_A, hf.DOME[0][0])])
def test_nuts_sit_on_their_flange_clear_of_the_column(ring, seat, column):
    _n, rr, nr, _nh, _a0, _tw = ring
    column_corner = column / math.cos(math.pi / hf.SEGMENTS)
    assert rr - nr > column_corner, "a nut runs into the column"
    assert rr + nr < seat, "a nut hangs off its flange"
    assert hf.nut_face_clearance_deg(ring) >= 3.0, "a nut face is parallel to a 12-gon face"


def test_chain_ends_and_links_clear_the_probe_at_the_smallest_slot():
    k = min(hf.scale(*c) for c in CORNERS)
    assert min(hf.chain_side_gaps(k)) > PROBE_TOL


def test_a_hanging_chain_stays_above_its_floor_and_reaches_both_ends():
    p0, p1 = (0.162, 0.0, -0.08), (0.106, 0.0, -0.10)
    floor = -0.11
    links = hf.hanging_chain(p0, p1, hf.LINK_PITCH, hf.LINK_L, floor, hf.CHAIN_DROP)
    assert len(links) >= 3
    assert min(c[2] - abs(t[2]) * hf.LINK_L / 2 for c, t in links) >= floor
    assert math.dist(links[0][0], p0) <= hf.LINK_L
    assert math.dist(links[-1][0], p1) <= hf.LINK_L


# --- paint ----------------------------------------------------------------------

def test_scheme_and_flow_weights_sum_to_one():
    assert math.isclose(sum(v[2] for v in hf.SCHEMES.values()), 1.0)
    assert math.isclose(sum(v[1] for v in hf.FLOW.values()), 1.0)
    assert set(hf.FLOW) == {"AA", "A", "B", "C"}


@pytest.mark.parametrize("style", [1, 2, 3])
def test_a_hydrant_is_the_same_hydrant_every_build(style):
    mod, plan = _module_plan(style)
    a = hf.resolve(plan, _streams(mod["stem"]))
    b = hf.resolve(plan, _streams(mod["stem"]))
    assert a == b


def test_hydrants_differ_across_styles_and_coded_tops_come_from_the_flow_table():
    got = []
    for style in range(1, 41):
        mod, plan = _module_plan(style)
        got.append(hf.resolve(plan, _streams(mod["stem"]))["paint"])
    assert len({g["name"] for g in got}) >= 4
    flows = [g for g in got if g["flow"]]
    assert flows, "40 styles drew no colour-coded top"
    for g in flows:
        assert g["top"] == hf.FLOW[g["flow"]][0]
        assert g["name"].endswith("_coded")
    for g in got:
        assert g["base"] == tuple(c * hf.BASE_SHADE for c in g["body"])


def test_a_prompt_colour_paints_the_body():
    _mod, plan = _module_plan(1)
    plan = dict(plan, color=[0.1, 0.2, 0.3])
    s = hf.pick_scheme(plan, _streams("x").stream("hydrant_paint"))
    assert s["name"] == "asked" and s["body"] == (0.1, 0.2, 0.3)


def test_the_worst_slot_in_the_genome_stays_inside_the_budget():
    """Chains lengthen with the stubs, so the count is a step function of the
    slot; its maximum is where both stubs are longest at the smallest scale."""
    import itertools
    steps = (0.0, 0.25, 0.5, 0.75, 1.0)
    worst = 0
    for i, j, k in itertools.product(steps, repeat=3):
        worst = max(worst, hf.triangles(hf.layout(
            0.297 + 0.123 * i, 0.297 + 0.123 * j, 0.637 + 0.263 * k)))
    assert worst == hf.triangles(hf.layout(0.42, 0.42, 0.637)) == 1680
    assert worst <= TRI_BUDGET
    assert hf.triangles(hf.layout(*LOT_SLOT)) == 1416


def test_the_genome_names_the_parts_the_recipe_builds():
    g = json.load(open(_GENOME, encoding="utf-8"))
    src = open(_RECIPE, encoding="utf-8").read()
    assert len(g["parts"]) == 10
    for part in g["parts"]:
        assert f'"{part}"' in src, part
    assert g["budgets"]["tris_lod0"] == TRI_BUDGET


# --- bpy: the built module ------------------------------------------------------------

def _build(tmp_path, dims, style=1):
    from zoo_keeper.bpylayer import build as B
    mod = _kit(*dims, style=style)["modules"][0]
    return B.build_module(mod, str(tmp_path), theme="delco_1997", style=style,
                          options={"save_blend": False})


def _probe():
    import runpy
    import sys
    saved = sys.argv
    sys.argv = ["coplanar_probe.py", "--"]
    try:
        return runpy.run_path(os.path.join(_ZOO, "tools", "coplanar_probe.py"))
    finally:
        sys.argv = saved


@pytest.mark.parametrize("dims", CORNERS)
def test_bpy_fits_its_slot_with_every_part(tmp_path, dims):
    bpy = pytest.importorskip("bpy")
    res = _build(tmp_path, dims)
    checks = {c["id"]: c for c in res["report"]["checks"]}
    for cid in ("fit_width", "fit_depth", "fit_height", "fit_pivot", "collision",
                "wear_colors", "uvs", "parts_named", "materials", "transforms"):
        assert checks[cid]["level"] == "pass", (dims, checks[cid])
    assert res["report"]["status"] == "pass"
    f = res["facts"]
    for axis, v in zip(("width", "depth", "height"), dims):
        assert abs(f["dimensions"][axis] - v) <= 0.001, (dims, axis, f["dimensions"])
    assert max(abs(c) for c in f["center"]) <= 0.001
    g = json.load(open(_GENOME, encoding="utf-8"))
    assert sorted(f["parts"]) == sorted(g["parts"])
    assert f["tris"] <= TRI_BUDGET, (dims, f["tris"])
    assert f["tris"] == hf.triangles(hf.layout(*dims)), (dims, f["tris"])
    assert 3 <= len(f["materials"]) <= 4
    col = [o for o in bpy.context.scene.objects if o.name.endswith("-colonly")]
    assert len(col) == 1
    xs = [v.co for v in col[0].data.vertices]
    for i, v in enumerate(dims):
        assert math.isclose(max(c[i] for c in xs) - min(c[i] for c in xs), v, abs_tol=1e-4)


def test_bpy_the_pumper_cap_is_the_minus_y_face_and_the_hose_caps_the_x_faces(tmp_path):
    bpy = pytest.importorskip("bpy")
    w, d, h = LOT_SLOT
    _build(tmp_path, LOT_SLOT)
    objs = {o.name: o for o in bpy.context.scene.objects}

    def span(name, i):
        cs = [v.co[i] for v in objs[name].data.vertices]
        return min(cs), max(cs)

    assert math.isclose(span("FireHydrant_PumperCap", 1)[0], -d / 2, abs_tol=1e-4)
    lo, hi = span("FireHydrant_HoseCaps", 0)
    assert math.isclose(lo, -w / 2, abs_tol=1e-4) and math.isclose(hi, w / 2, abs_tol=1e-4)
    assert math.isclose(span("FireHydrant_Collar", 1)[1], d / 2, abs_tol=1e-4)
    assert math.isclose(span("FireHydrant_Collar", 2)[0], -h / 2, abs_tol=1e-4)
    assert math.isclose(span("FireHydrant_OperatingNut", 2)[1], h / 2, abs_tol=1e-4)


def test_bpy_the_same_module_every_build(tmp_path):
    bpy = pytest.importorskip("bpy")

    def snapshot():
        out = {}
        for o in bpy.context.scene.objects:
            if o.type == "MESH":
                out[o.name] = tuple(tuple(round(c, 6) for c in v.co) for v in o.data.vertices)
        return out

    _build(tmp_path, LOT_SLOT)
    a = snapshot()
    _build(tmp_path, LOT_SLOT)
    assert snapshot() == a


@pytest.mark.parametrize("dims", CORNERS[:3] + tuple(_random_dims(4, seed=1997)))
def test_bpy_no_two_faces_share_a_plane(tmp_path, dims):
    bpy = pytest.importorskip("bpy")
    import mathutils
    probe = _probe()
    for style in (1, 2):
        _build(tmp_path, dims, style)
        objs = probe["_visual_meshes"](bpy, bpy.context.scene)
        rows, ntri = probe["probe"](bpy, mathutils, objs, PROBE_TOL, 1e-6, 1e-3)
        assert ntri > 1000, "the probe read too few triangles to mean anything"
        assert [r for r in rows if r["facing"] == "SAME"] == [], (dims, style, rows[:4])
