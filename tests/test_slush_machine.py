"""1.15.0 -- the convenience store's frozen drink station.

The walker, 2026-09-28: "do the slush machine next"; the references ask for
a twin-hopper machine with clear barrels, one red and one blue, a branded
topper, a mascot on the front panel, a pull tap per hopper, a tube of cups,
a six-bottle syrup rail with a pump each, a numbered instruction panel, a
drip tray and a straw caddy. Pure half (`core/slush_machine_forms.py`): the
module fills its slot exactly, no two faces share a plane, every face wound
outward, the barrels and rail follow the width, a red and a blue barrel
always, every glowing face maps into the art, the brand is invented. Built
half (bpy, skipped without it): PASS and fit, three submissions over three
materials, the glow is Lux's, the glass is see-through, determinism.
"""
from __future__ import annotations

import itertools
import os
import re

import pytest

from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import prims as P
from zoo_keeper.core import slush_machine_forms as S

CASES = list(S.DC_SIZES) + [tuple(c) for c in itertools.product(*(S.RANGES[a] for a in ("width", "depth", "height")))]


@pytest.mark.parametrize("dims", CASES)
def test_the_station_fills_its_slot_and_shares_no_plane(dims):
    w, d, h = dims
    pr = S.plan(w, d, h)["prims"]
    lo, hi = P.bounds(pr)
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-6, (dims, lo, hi)
    assert P.coincident_pairs(pr, tol=0.0022) == []
    for p in pr:
        assert S.signed_volume(p) > 0, (p["part"], p["mat"])
    assert P.tri_count(pr) <= genome_mod.load_species("slush_machine")["budgets"]["tris_lod0"]


def test_the_coincidence_check_can_see_a_pair_here():
    """A clean reading is only evidence if the instrument can see a pair on
    this geometry: a box 1 mm over the counter top is one."""
    pr = S.plan(*S.DC_SIZES[0])["prims"]
    ctl = pr + [P.box("x", "steel", (-0.2, -0.3, S.CTR_H + 0.001), (0.2, -0.1, S.CTR_H + 0.1))]
    assert P.coincident_pairs(ctl, tol=0.0022) != []


@pytest.mark.parametrize("dims", CASES)
def test_barrels_and_rail_follow_the_width(dims):
    w, d, h = dims
    f = S.plan(w, d, h)["facts"]
    assert f["bowls"] == (3 if w >= S.need(3, True) else 2)
    assert f["rail"] == (w >= S.need(f["bowls"], True))
    assert len(f["syrups"]) == (S.N_BOTTLES if f["rail"] else 0)
    assert S.BOWL_H_MIN <= f["bowl_height"] <= S.BOWL_H_MAX
    # the zones stand in order along the station and inside it
    edges = [x for z in ("cups", "rail", "machine") if z in f["zones"] for x in f["zones"][z]]
    assert edges == sorted(edges) and edges[0] >= -w / 2 and edges[-1] <= w / 2 + 1e-9


@pytest.mark.parametrize("variant", range(4))
def test_there_is_always_a_red_and_a_blue_barrel(variant):
    f = S.plan(*S.DC_SIZES[0], variant=variant)["facts"]
    assert set(f["flavours"]) == {"cherry", "blue"}
    wide = S.plan(2.6, 0.7, 2.0, variant=variant)["facts"]
    assert {"cherry", "blue"} <= set(wide["flavours"]) and len(set(wide["flavours"])) == 3


def test_the_default_station_is_the_references_whole_list():
    g = S.plan(*S.DC_SIZES[0])
    f = g["facts"]
    parts = {p["part"] for p in g["prims"]}
    assert f["bowls"] == 2 and f["rail"]
    for part in ("Slush_Tube", "Slush_Cups", "Slush_Rail", "Slush_Syrup", "Slush_Tap", "Slush_Barrel", "Slush_Glow"):
        assert part in parts, part
    # a pull handle a barrel, in its flavour's colour
    handles = [p for p in g["prims"] if p["part"] == "Slush_Tap" and p["mat"].startswith("flav_")]
    assert sorted(p["mat"] for p in handles) == sorted("flav_" + fl for fl in f["flavours"])


@pytest.mark.parametrize("dims", [S.DC_SIZES[0], (1.0, 0.6, 1.8), (2.6, 0.9, 2.4)])
def test_every_glowing_face_maps_into_the_art(dims):
    g = S.plan(*dims)
    f = g["facts"]
    art = S.glow_art(dims[0], f["bowls"], f["flavours"], f["rail"])
    W, H = art["size"]
    for x0, y0, x1, y1 in art["rects"].values():
        assert 0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H
    glows = [p for p in g["prims"] if p["mat"] == "glow"]
    assert glows
    for p in glows:
        assert len(p["uvs"]) == len(p["faces"])
        for face in p["uvs"]:
            for c in face:
                assert c[0] in art["rects"], c
                if len(c) == 3:
                    assert -1e-9 <= c[1] <= 1 + 1e-9 and -1e-9 <= c[2] <= 1 + 1e-9, c


def test_the_art_is_the_same_bytes_and_says_the_words():
    a = S.glow_art(1.6, 2, ("cherry", "blue"), True)
    b = S.glow_art(1.6, 2, ("cherry", "blue"), True)
    assert bytes(a["canvas"].buf) == bytes(b["canvas"].buf) and a["name"] == b["name"]
    for words in S.TOPPER_WORDS + S.PANEL_WORDS:
        assert words in a["said"]
    assert [s for s in a["said"] if s[:1].isdigit()] == ["1 SELECT CUP SIZE", "2 ADD FLAVOR", "3 PULL TO FILL"]


#: Real frozen-drink and convenience marks, none of which may appear.
DENY = ("ICEE", "SLURPEE", "SLUSHIE", "SLUSH PUPPIE", "7-ELEVEN", "WAWA", "SHEETZ", "BUNN",
        "FROZEN COKE", "COCA", "PEPSI", "ICEE BEAR", "SLURP")


def test_the_brand_is_invented():
    words = " ".join(S.TOPPER_WORDS + S.PANEL_WORDS + S.STEPS).upper()
    words += " " + " ".join(v[0] for v in S.FLAVOURS.values())
    for mark in DENY:
        assert not re.search(r"\b" + re.escape(mark) + r"\b", words), mark


def test_the_genome_names_the_parts_and_validates():
    g = genome_mod.load_species("slush_machine")
    assert genome_mod.validate_genome(g) == []
    r = g["dimensions"]
    for a in ("width", "depth", "height"):
        assert (r[a]["min"], r[a]["max"]) == S.RANGES[a]
    for w, d, h in S.DC_SIZES:
        assert r["width"]["min"] <= w <= r["width"]["max"] and r["height"]["min"] <= h <= r["height"]["max"]
    got = set()
    for dims in CASES:
        got |= {p["part"] for p in S.plan(*dims)["prims"]}
    assert got == set(g["parts"])


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "slush_machine", "role": "prop", "size_mod": "full", "style": 1,
            "species": "slush_machine", "material": "metal",
            "fit": {"dims": list(dims), "pivot": "center"}}
    slot.update(fields)
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == [], plan["dressing_fallbacks"]
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    objs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"
                   and not o.name.endswith(_COL_SUFFIXES)), key=lambda o: o.name)
    return res, objs


def _glb_json(path):
    import json
    import struct
    raw = open(path, "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    return json.loads(raw[20:20 + n])


@pytest.mark.parametrize("dims", [S.DC_SIZES[0], (2.6, 0.9, 2.4)])
def test_bpy_the_station_passes_and_fits(tmp_path, dims):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    parts = set(genome_mod.load_species("slush_machine")["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name
        assert "." not in o.name, o.name


def test_bpy_three_submissions_the_glow_is_lux_and_the_glass_is_clear(tmp_path):
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, S.DC_SIZES[0])
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    names = [m["name"] for m in doc["materials"]]
    assert len(names) == 3, names
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 3, [m["name"] for m in visual]
    lit = [m["name"] for m in doc["materials"] if m.get("emissiveFactor") and any(m["emissiveFactor"])]
    assert len(lit) == 1 and lit[0].startswith("M_Slush_slushglow_") and lit[0].endswith("_Face"), lit
    clear = [m["name"] for m in doc["materials"] if m.get("alphaMode") == "BLEND"]
    assert clear == ["M_Slush_glass"], names


def test_bpy_the_same_file_every_build(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, S.DC_SIZES[0], variant=2)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]


# --- 1.52.0: drawn, not stamped --------------------------------------------------------


def test_every_line_sets_and_the_mascot_is_drawn_with_curves():
    """The mascot was a 16 x 20 bitmap stamped at a whole scale; it is drawn
    now (`_mascot`), so the panel holds grey where a curve crosses a pixel.
    And every word on every tile sets, at every width the planner takes."""
    from zoo_keeper.core import paint as PT
    im = PT.Img(120, 150, (16, 40, 150))
    S._mascot(im, (10, 5, 110, 145))
    greys = int(((im.a > 20) & (im.a < 235)).any(axis=2).sum())
    assert greys > 400
    assert not hasattr(S, "MASCOT") and not hasattr(S, "_stamp_mascot")
    for w, n, rail in ((1.0, 2, False), (1.6, 2, True), (2.6, 3, True)):
        for variant in range(4):
            a = S.glow_art(w, n, S.BOWL_SETS[variant][:n], rail, "k", variant)
            assert a["unset"] == [], (w, variant, a["unset"])


def test_the_lettering_is_the_brand_s_and_the_maker_s():
    from zoo_keeper.core import smooth_type as ST
    assert S.BRAND_FACE in ST.FACES
    assert S.TAG_FACE == ST.owned("print_italic")
    assert S.MAKER_FACE == ST.owned("maker") and S.MAKER_SMALL == ST.owned("maker_small")


def test_the_glow_image_has_gutters_each_tile_bleeds_into():
    from zoo_keeper.core import card_art as CA
    a = S.glow_art(1.6, 2, ("cherry", "blue"), True)
    G, c = CA.SMOOTH_GUTTER, a["canvas"]
    for key, (x0, y0, x1, y1) in a["rects"].items():
        y = (y0 + y1) // 2
        assert c.get(x0 - G // 2, y) == c.get(x0, y) and c.get(x1 - 1 + G // 2, y) == c.get(x1 - 1, y), key
    # the churn tile is seamless left to right: its last column meets its first
    x0, y0, x1, y1 = a["rects"]["slush_cherry"]
    assert x1 - x0 == S.SLUSH_TILE == y1 - y0


# --- 1.55.0: the churn moves -------------------------------------------------------------


def test_the_churn_tile_is_the_flavour_and_its_ice_and_no_band():
    """The bands are drawn moving by the consumer now; the tile carries
    none, so a still band under a moving one cannot happen."""
    for fl, (_name, cols, _rgb) in S.FLAVOURS.items():
        base, light, dark, ice = cols
        im = S.PT.Img(S.SLUSH_TILE, S.SLUSH_TILE, base)
        S._churn(im, (0, 0, S.SLUSH_TILE, S.SLUSH_TILE), cols)
        px = {tuple(int(round(c)) for c in im.a[y, x]) for y in range(S.SLUSH_TILE) for x in range(S.SLUSH_TILE)}
        assert px <= {tuple(base), tuple(ice)}, (fl, px - {tuple(base), tuple(ice)})
        assert tuple(ice) in px and tuple(base) in px


def test_every_churn_corner_says_where_it_is_round_the_barrel():
    """The slush's side facets carry (u round, v up) into the churn tile, u
    by segment with the seam's far side at 1 and v from the band's bottom
    to its top; the slush's cap and the solid blocks carry no such place."""
    g = S.plan(*S.DC_SIZES[0])
    slush = [p for p in g["prims"] if p["part"] == "Slush_Glow"
             and any(len(c) == 3 and c[0].startswith("slush_") for face in p["uvs"] for c in face)]
    assert len(slush) == g["facts"]["bowls"]
    for p in slush:
        side = [c for face in p["uvs"] for c in face if len(c) == 3 and c[0].startswith("slush_")]
        other = [c for face in p["uvs"] for c in face if not (len(c) == 3 and c[0].startswith("slush_"))]
        assert side and other
        us = sorted({round(c[1], 6) for c in side})
        assert us[0] == 0.0 and us[-1] == 1.0 and len(us) == S.SEG + 1, us
        assert {round(c[2], 6) for c in side} == {0.0, 1.0}
        assert all(len(c) == 1 for c in other)
    assert S.CHURN_PERIOD_S > 0.0
