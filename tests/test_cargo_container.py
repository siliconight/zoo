"""cargo_container: minted 2026-09-12 by tools/new_species.py (roadmap 150),
rebuilt as an ISO shipping container in 0.82.0.

The decisions are pure (`core/container_forms.py`) and tested here without
Blender. The built module -- exact fit per size class, the parts, zero
coincident same-facing faces, the triangle budget -- is the bpy half at the
bottom, skipped without Blender and run inside Blender 5.1 for this change.
"""
import ast
import json
import math
import os

import pytest

from zoo_keeper.core import container_forms as cf
from zoo_keeper.core import genome, kit, seeding
from zoo_keeper.recipes import _legend

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "cargo_container.py")
_GENOME = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "cargo_container.json")

#: ISO 668 nominal boxes a slot may ask for: (label, w, d, h).
NOMINAL = (("10ft", 2.438, 2.991, 2.591), ("20ft", 2.438, 6.058, 2.591),
           ("20ft_lot", 2.44, 6.06, 2.59), ("40ft", 2.438, 12.192, 2.591),
           ("40ft_hc", 2.438, 12.192, 2.896), ("45ft_hc", 2.438, 13.716, 2.896))


def _streams(key):
    return seeding.RNGStreams(seeding.root_key(key, "cargo_container", 0, "0.31.0"))


def _plan(w, d, h, style=1):
    return kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "cargo_container_0", "role": "prop", "size_mod": "full",
        "style": style, "species": "cargo_container",
        "fit": {"dims": [w, d, h], "pivot": "center"}}]}, theme="delco", style=style)


def test_cargo_container_is_discovered_and_validates():
    assert "cargo_container" in genome.list_species()
    assert genome.validate_genome(genome.load_species("cargo_container")) == []


def test_cargo_container_plans_at_its_authored_dims():
    plan = _plan(2.44, 6.06, 2.59)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "cargo_container"


@pytest.mark.parametrize("label,w,d,h", NOMINAL, ids=[n[0] for n in NOMINAL])
def test_every_nominal_box_is_inside_the_genome_range(label, w, d, h):
    """A 40 ft box is 12.192 m; the minted range stopped at 12.12, so a slot
    asking for one was outside the genome it names."""
    dims = genome.load_species("cargo_container")["dimensions"]
    for name, v in (("width", w), ("depth", d), ("height", h)):
        assert dims[name]["min"] <= v <= dims[name]["max"], (label, name)


def test_lot_asks_for_the_genome_default():
    """Lot's COVER_SPECIES parks the container at the genome's defaults."""
    dims = genome.load_species("cargo_container")["dimensions"]
    assert (dims["width"]["default"], dims["depth"]["default"],
            dims["height"]["default"]) == (2.44, 6.06, 2.59)


# --- size -------------------------------------------------------------------

@pytest.mark.parametrize("depth,height,cls,code,pockets", [
    (2.991, 2.591, "10ft", "12G1", 2), (6.058, 2.591, "20ft", "22G1", 2),
    (6.06, 2.59, "20ft", "22G1", 2), (12.192, 2.591, "40ft", "42G1", 0),
    (12.192, 2.896, "40ft", "45G1", 0), (13.716, 2.896, "45ft", "L5G1", 0),
    (6.058, 2.438, "20ft", "20G1", 2)])
def test_size_class_code_and_pockets(depth, height, cls, code, pockets):
    assert cf.length_class(depth)[0] == cls
    assert cf.size_type(depth, height) == code
    assert len(cf.pocket_centres(depth)) == pockets


def test_twenty_foot_pockets_are_2050_apart():
    a, b = cf.pocket_centres(6.058)
    assert math.isclose(b - a, 2.050)
    assert math.isclose(a, -b)


def test_check_digit_matches_the_iso_example():
    assert cf.check_digit("CSQU", "305438") == 3


# --- corrugation ---------------------------------------------------------------

@pytest.mark.parametrize("span", [2.1, 2.2, 5.6, 5.7, 11.8, 13.3])
@pytest.mark.parametrize("profile", [cf.SIDE_PROFILE, cf.ROOF_PROFILE])
def test_corrugation_fills_the_span_and_ends_on_a_crest(span, profile):
    pitch, crest, flank, depth = profile
    pts = cf.corrugation(-span / 2, span / 2, profile)
    assert math.isclose(pts[0][0], -span / 2) and math.isclose(pts[-1][0], span / 2)
    assert pts[0][1] == 0.0 and pts[-1][1] == 0.0
    us = [u for u, _o in pts]
    assert all(b > a for a, b in zip(us, us[1:])), "breakpoints must strictly increase"
    assert {o for _u, o in pts} == {0.0, -depth}
    n = round(span / pitch)
    assert abs(span / n - pitch) / pitch < 0.1


def test_door_channels_leave_a_flat_top_band():
    pts = cf.channels(0.0, 2.2, 0.45, 0.15)
    assert pts[0] == (0.0, 0.0) and pts[-1] == (2.2, 0.0)
    first_valley = min(u for u, o in pts if o < 0)
    last_valley = max(u for u, o in pts if o < 0)
    assert last_valley <= 2.2 - 0.45 and first_valley >= 0.15


def test_a_painted_polygon_is_cut_at_every_rib_and_loses_no_area():
    pts = cf.corrugation(-3.0, 3.0)
    poly = [(-0.61, 0.2), (0.37, 0.2), (0.37, 0.9), (-0.61, 0.9)]
    pieces = cf.split_at(poly, pts)
    assert math.isclose(sum(abs(cf._area(p)) for p in pieces), abs(cf._area(poly)),
                        rel_tol=1e-9)
    us = [u for u, _o in pts]
    for p in pieces:
        lo, hi = min(q[0] for q in p), max(q[0] for q in p)
        # each piece lies between two neighbouring breakpoints: one flat face
        assert not any(lo + 1e-9 < u < hi - 1e-9 for u in us), (lo, hi)


def test_no_painted_piece_is_a_sliver():
    """A glyph edge 0.3 mm from a rib break was cut into a 0.3 mm sliver --
    the one coincident pair the 0.82.0 sweep found. Every piece is at least
    `SNAP` wide wherever it touches a break."""
    pts = cf.corrugation(-5.0, 5.0)
    breaks = [u for u, _o in pts]
    for b in breaks[5:40]:
        for off in (-0.0009, -0.0003, 0.0003, 0.0009):
            poly = [(b + off, 0.0), (b + off + 0.05, 0.0), (b + off + 0.05, 0.1), (b + off, 0.1)]
            for piece in cf.split_at(poly, pts):
                us = [q[0] for q in piece]
                assert max(us) - min(us) >= cf.SNAP - 1e-12, (b, off, piece)


def test_valleys_are_darker_than_flanks_are_darker_than_crests():
    """The form shade that keeps the ribs legible under light with no
    direction (the rain walk's frames). It is built into the materials:
    cover modules import with vertex colour off, measured."""
    sh = cf.FORM_SHADE
    assert sh["crest"] == 1.0 and sh["crest"] > sh["flank"] > sh["valley"] > 0.5
    pts = cf.corrugation(-3.0, 3.0)
    kinds = [cf.segment_kind(pts, (a[0] + b[0]) / 2) for a, b in zip(pts, pts[1:])]
    assert kinds[0] == "crest" and kinds[-1] == "crest"
    assert kinds.count("valley") == round(6.0 / cf.SIDE_PROFILE[0])
    assert kinds.count("flank") == 2 * kinds.count("valley")
    door = cf.channels(0.0, 2.2, 0.45, 0.15)
    kinds = [cf.segment_kind(door, (a[0] + b[0]) / 2) for a, b in zip(door, door[1:])]
    assert kinds.count("valley") == 4


# --- paint and markings ----------------------------------------------------------

def test_every_marking_is_spelled_from_glyphs_that_exist():
    chars = set("0123456789U")
    for name, prefix in cf.CARRIERS:
        chars |= set(name) | set(prefix)
    chars |= {c for p in cf.LESSORS for c in p}
    chars |= set("GROSS TARE".replace(" ", ""))
    for depth, height in ((2.991, 2.591), (6.058, 2.591), (12.192, 2.896), (13.716, 2.896)):
        chars |= set(cf.size_type(depth, height))
    missing = sorted(chars - set(_legend.GLYPHS))
    assert not missing, missing


def test_paint_weights_sum_to_one_and_cover_the_period_palette():
    assert math.isclose(sum(v[1] for v in cf.PAINT.values()), 1.0)
    for name in ("red", "maroon", "orange", "blue", "green", "grey", "white"):
        assert name in cf.PAINT


def _module_plan(style):
    mod = _plan(2.44, 6.06, 2.59, style)["modules"][0]
    from zoo_keeper.core import dna
    return mod, dna.resolve_module_plan(mod, genome.load_species("cargo_container"),
                                        "delco", style, "0.82.0")


@pytest.mark.parametrize("style", [1, 2, 3])
def test_a_box_is_the_same_box_every_build(style):
    mod, plan = _module_plan(style)
    a = cf.resolve(plan, _streams(mod["stem"]))
    b = cf.resolve(plan, _streams(mod["stem"]))
    assert a == b


def test_boxes_differ_across_styles():
    got = []
    for style in range(1, 41):
        mod, plan = _module_plan(style)
        got.append(cf.resolve(plan, _streams(mod["stem"])))
    assert len({g["paint_name"] for g in got}) >= 5
    assert len({g["owner"] + g["serial"] for g in got}) == 40
    assert any(g["carrier"] for g in got) and any(not g["carrier"] for g in got)
    for g in got:
        assert g["check"] == cf.check_digit(g["owner"], g["serial"])
        assert g["net"] == g["gross"] - g["tare"]


def test_a_prompt_colour_wins_over_the_palette():
    _mod, plan = _module_plan(1)
    plan = dict(plan, color=[0.1, 0.2, 0.3])
    assert cf.pick_paint(plan, _streams("x").stream("p")) == ("asked", (0.1, 0.2, 0.3))


def test_white_paint_takes_dark_lettering():
    assert cf.mark_colour("white", cf.PAINT["white"][0]) == cf.MARK_DARK
    assert cf.mark_colour("red", cf.PAINT["red"][0]) == cf.MARK_WHITE


def test_carrier_names_fit_the_wall():
    for name, _p in cf.CARRIERS:
        for length, height in ((2.6, 2.59), (5.7, 2.59), (11.8, 2.9)):
            th = cf.carrier_height(name, length, height)
            assert cf.text_width(len(name), th) <= 0.72 * length + 1e-9 or th == 0.10


# --- weathering ------------------------------------------------------------------

@pytest.mark.parametrize("wear", [0.15, 0.35, 0.57])
def test_rust_never_lands_on_markings_and_stays_on_crests(wear):
    pts = cf.corrugation(-2.83, 2.94)
    taken = [(-2.5, 1.9, -1.8, 2.05), (-1.4, 0.8, 1.4, 1.4)]
    for seed in range(20):
        rng = _streams(f"rust{seed}").stream("w")
        streaks = cf.plan_rust(pts, -1.1, 1.18, wear, rng, list(taken))
        bands = cf.crest_bands(pts)
        rects = [s["rect"] for s in streaks]
        for r in rects:
            assert not any(cf.rects_overlap(r, t) for t in taken)
            assert -1.1 - 1e-9 <= r[1] < r[3] <= 1.18 + 1e-9
            assert any(a <= r[0] and r[2] <= b for a, b in bands)
        for i, a in enumerate(rects):
            for b in rects[i + 1:]:
                assert not cf.rects_overlap(a, b)


def test_a_patch_avoids_what_is_already_painted():
    taken = [(-2.5, 0.0, 2.5, 1.0)]
    for seed in range(30):
        p = cf.plan_patch((-2.8, 2.9), -1.1, 1.18, 0.57, _streams(f"p{seed}").stream("w"), taken)
        if p:
            assert not cf.rects_overlap(p["rect"], taken[0], pad=0.02)


# --- the recipe's planes, read without bpy -----------------------------------------

def _constants(path):
    ns = {}
    for node in ast.parse(open(path, encoding="utf-8").read()).body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            try:
                ns[node.targets[0].id] = eval(
                    compile(ast.Expression(node.value), path, "eval"),
                    {"__builtins__": {}}, dict(ns))
            except Exception:
                continue
    return ns


def test_nothing_on_the_door_end_stands_outside_the_castings():
    c = _constants(_RECIPE)
    assert c["CAST_INSET"] > 0
    for name in ("LEVER_END", "HUB_END", "KEEPER_END", "GUIDE_END", "RETAINER_END",
                 "HINGE_END", "REAR_POST_END", "HEADER_END", "SILL_END", "LEAF_FRONT"):
        assert c[name] > c["CAST_INSET"], name
    assert c["BAR_CENTRE"] - c["BAR_R"] > c["CAST_INSET"]


def test_painted_details_stand_clear_of_the_probe_window_even_on_a_flank():
    c = _constants(_RECIPE)
    pitch, crest, flank, depth = cf.SIDE_PROFILE
    angle = math.atan2(depth, flank)
    assert c["DETAIL_PROUD"] * math.cos(angle) > 0.002
    assert c["DETAIL_ON_DETAIL"] > 0.002


def test_the_genome_names_the_parts_the_recipe_builds():
    g = json.load(open(_GENOME, encoding="utf-8"))
    src = open(_RECIPE, encoding="utf-8").read()
    for part in g["parts"]:
        assert f'"{part}"' in src, part


# --- bpy: the built module ------------------------------------------------------------

#: Measured through the kit path at the nominal sizes, 0.82.0 (see CHANGELOG).
TRI_BUDGET = 4500


def _build(tmp_path, w, d, h, style):
    from zoo_keeper.bpylayer import build as B
    mod = _plan(w, d, h, style)["modules"][0]
    return B.build_module(mod, str(tmp_path), theme="delco", style=style,
                          options={"save_blend": False})


@pytest.mark.parametrize("label,w,d,h", NOMINAL, ids=[n[0] for n in NOMINAL])
def test_bpy_each_size_fits_its_slot_with_every_part(tmp_path, label, w, d, h):
    pytest.importorskip("bpy")
    res = _build(tmp_path, w, d, h, 1)
    checks = {c["id"]: c for c in res["report"]["checks"]}
    for cid in ("fit_width", "fit_depth", "fit_height", "fit_pivot", "collision",
                "wear_colors", "uvs", "parts_named"):
        assert checks[cid]["level"] == "pass", (label, checks[cid])
    parts = set(res["facts"]["parts"])
    for must in ("CargoContainer_Walls", "CargoContainer_Frame", "CargoContainer_Doors",
                 "CargoContainer_Hardware", "CargoContainer_Apertures",
                 "CargoContainer_Markings", "CargoContainer_Plates",
                 "CargoContainer_Warning", "CargoContainer_Rust",
                 "CargoContainer_RibFlanks", "CargoContainer_RibValleys"):
        assert must in parts, (label, must)
    assert res["facts"]["tris"] <= TRI_BUDGET, (label, res["facts"]["tris"])
    g = json.load(open(_GENOME, encoding="utf-8"))
    assert g["budgets"]["tris_lod0"] >= res["facts"]["tris"]


@pytest.mark.parametrize("label,w,d,h", NOMINAL[1:4], ids=[n[0] for n in NOMINAL[1:4]])
def test_bpy_no_two_faces_share_a_plane(tmp_path, label, w, d, h):
    bpy = pytest.importorskip("bpy")
    import mathutils
    import runpy
    import sys
    saved = sys.argv
    sys.argv = ["coplanar_probe.py", "--"]
    try:
        probe = runpy.run_path(os.path.join(_ZOO, "tools", "coplanar_probe.py"))
    finally:
        sys.argv = saved
    for style in (1, 2):
        _build(tmp_path, w, d, h, style)
        objs = probe["_visual_meshes"](bpy, bpy.context.scene)
        rows, _n = probe["probe"](bpy, mathutils, objs, 0.002, 1e-6, 1e-3)
        assert [r for r in rows if r["facing"] == "SAME"] == [], (label, style, rows[:4])
