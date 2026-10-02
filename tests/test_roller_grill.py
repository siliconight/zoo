"""1.17.0 -- the convenience store's hot dog roller grill.

The walker, 2026-09-28: "do the roller grill next", with photographs of two
store stations and a countertop merchandiser. Pure half
(`core/roller_grill_forms.py`): the module fills its slot exactly, no two
faces share a plane (with a control proving the check can see one), every
face wound outward, the rollers run across the width with the dogs lying
parallel in the grooves and clear of them, the grease darkens toward the
back, the columns and tags follow the width, the bun shelf the height, and
the names are invented. Built half (bpy): PASS and fit, four submissions,
nothing lit, determinism.
"""
from __future__ import annotations

import itertools
import math
import os
import re

import pytest

from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import prims as P
from zoo_keeper.core import roller_grill_forms as R

CASES = list(R.DC_SIZES) + [tuple(c) for c in itertools.product(*(R.RANGES[a] for a in ("width", "depth", "height")))]


@pytest.mark.parametrize("dims", CASES)
def test_the_grill_fills_its_slot_and_shares_no_plane(dims):
    w, d, h = dims
    pr = R.plan(w, d, h)["prims"]
    lo, hi = P.bounds(pr)
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-6, (dims, lo, hi)
    assert P.coincident_pairs(pr, tol=0.0022) == []
    for p in pr:
        assert R.signed_volume(p) > 0, (p["part"], p["mat"])
    assert P.tri_count(pr) <= genome_mod.load_species("roller_grill")["budgets"]["tris_lod0"]


def test_the_coincidence_check_can_see_a_pair_here():
    pr = R.plan(*R.DC_SIZES[0])["prims"]
    ctl = pr + [P.box("x", "top", (-0.2, -0.25, R.CAB_H + 0.001), (0.2, -0.22, R.CAB_H + 0.05))]
    assert P.coincident_pairs(ctl, tol=0.0022) != []


def _axis(p):
    xs = [v[0] for v in p["verts"]]
    ys = [v[1] for v in p["verts"]]
    return max(xs) - min(xs), max(ys) - min(ys)


@pytest.mark.parametrize("dims", CASES)
def test_rollers_run_across_and_the_dogs_lie_parallel_in_the_grooves(dims):
    """The countertop photograph: every roller across the width, each dog in
    the groove between two, parallel to them, REST_GAP clear of both."""
    w, d, h = dims
    got = R.plan(w, d, h)
    rolls = [p for p in got["prims"] if p["part"] == "Roller_Roller"]
    dogs = [p for p in got["prims"] if p["part"] == "Roller_Dog"]
    assert len(rolls) == got["facts"]["rollers"] and dogs
    for p in rolls + dogs:
        dx, dy = _axis(p)
        assert dx > 3 * dy, p["part"]
    rs = R.rollers(d, h)
    for p in dogs:
        cy = sum(v[1] for v in p["verts"]) / len(p["verts"])
        cz = sum(v[2] for v in p["verts"]) / len(p["verts"])
        near = sorted(rs, key=lambda r: abs(r[0] - cy))[:2]
        assert min(r[0] for r in near) < cy < max(r[0] for r in near)
        for ry, rz in near:
            assert math.hypot(cy - ry, cz - rz) > R.ROLLER_R + 0.0089, "a dog is into a roller"


def test_the_grease_darkens_toward_the_back():
    rolls = [p for p in R.plan(*R.DC_SIZES[0])["prims"] if p["part"] == "Roller_Roller"]
    rolls.sort(key=lambda p: sum(v[1] for v in p["verts"]))
    tints = [R.vertex_tint(p["mat"])[1][0] for p in rolls]
    assert tints == sorted(tints, reverse=True) and tints[-1] < tints[0] * 0.6


@pytest.mark.parametrize("dims", CASES)
def test_columns_tags_and_the_bun_shelf_follow_the_slot(dims):
    w, d, h = dims
    got = R.plan(w, d, h)
    f = got["facts"]
    tags = [p for p in got["prims"] if p["part"] == "Roller_Tag"]
    divs = [p for p in got["prims"] if p["part"] == "Roller_Divider"]
    assert len(tags) == f["columns"] and len(divs) == f["columns"] - 1
    assert len(set(f["kinds"])) == f["columns"]
    assert f["shelf"] == (h - (R.CAB_H + R.PAN_H) >= R.SHELF_ROOM) and (f["buns"] > 0) == f["shelf"]


def test_the_default_is_the_photographs_three_columns_and_a_bun_shelf():
    f = R.plan(*R.DC_SIZES[0])["facts"]
    assert f["columns"] == 3 and f["shelf"]


def test_every_painted_face_maps_into_the_art():
    for dims in (R.DC_SIZES[0], (0.7, 0.5, 1.3), (1.4, 0.8, 1.6)):
        A = R.art(*dims)
        W, H = A["size"]
        for x0, y0, x1, y1 in A["rects"].values():
            assert 0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H
        for p in (q for q in R.plan(*dims)["prims"] if q["mat"] == "paint"):
            assert len(p["uvs"]) == len(p["faces"])
            for face in p["uvs"]:
                for c in face:
                    assert c[0] in A["rects"], c


#: Real marks from the references, none of which may appear.
DENY = ("BIG BITE", "7-ELEVEN", "ELEVEN", "WAWA", "SHEETZ", "NATHAN", "HEBREW NATIONAL", "OSCAR MAYER",
        "BALL PARK", "STAR", "ROLLER BITES")


def test_the_names_are_invented():
    words = " ".join(list(R.PANEL_WORDS) + [k[1] for k in R.KINDS]).upper()
    for mark in DENY:
        assert not re.search(r"\b" + re.escape(mark) + r"\b", words), mark
    a = R.art(*R.DC_SIZES[0])
    assert a["said"] == list(R.PANEL_WORDS) + [k[1] for k in R.KINDS]
    assert bytes(R.art(*R.DC_SIZES[0])["canvas"].buf) == bytes(a["canvas"].buf)


def test_the_genome_names_the_parts_and_validates():
    g = genome_mod.load_species("roller_grill")
    assert genome_mod.validate_genome(g) == []
    for a in ("width", "depth", "height"):
        assert (g["dimensions"][a]["min"], g["dimensions"][a]["max"]) == R.RANGES[a]
    got = set()
    for dims in CASES:
        got |= {p["part"] for p in R.plan(*dims)["prims"]}
    assert got == set(g["parts"])


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "roller_grill", "role": "prop", "size_mod": "full", "style": 1,
            "species": "roller_grill", "material": "metal",
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


@pytest.mark.parametrize("dims", [R.DC_SIZES[0], (1.4, 0.8, 1.6)])
def test_bpy_the_grill_passes_and_fits(tmp_path, dims):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    parts = set(genome_mod.load_species("roller_grill")["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name
        assert "." not in o.name, o.name


def test_bpy_four_submissions_nothing_lit_and_the_glass_is_clear(tmp_path):
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, R.DC_SIZES[0])
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    names = [m["name"] for m in doc["materials"]]
    assert len(names) == 4, names
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 4, [m["name"] for m in visual]
    assert [m["name"] for m in doc["materials"] if m.get("emissiveFactor") and any(m["emissiveFactor"])] == []
    assert [m["name"] for m in doc["materials"] if m.get("alphaMode") == "BLEND"] == ["M_Roller_glass"]


def test_bpy_the_same_file_every_build(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, R.DC_SIZES[0], variant=1)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]


# --- 1.53.0: drawn and lettered by owner, behind a filtered sampler --------------------


def test_every_line_sets_and_the_lettering_has_owners():
    from zoo_keeper.core import smooth_type as ST
    assert R.SHOP_FACE == ST.owned("shop") and R.MAKER_FACE == ST.owned("maker")
    for w, d, h in (R.DC_SIZES[0], (0.7, 0.5, 1.3), (1.4, 0.8, 1.6)):
        for variant in range(4):
            a = R.art(w, d, h, variant)
            assert a["unset"] == [], (w, variant, a["unset"])
            assert a["said"] == list(R.PANEL_WORDS) + [k[1] for k in R.KINDS]


def test_the_art_has_gutters_each_tile_bleeds_into():
    from zoo_keeper.core import card_art as CA
    a = R.art(*R.DC_SIZES[0])
    G, c = CA.SMOOTH_GUTTER, a["canvas"]
    for key, (x0, y0, x1, y1) in a["rects"].items():
        y = (y0 + y1) // 2
        assert c.get(x0 - G // 2, y) == c.get(x0, y) and c.get(x1 - 1 + G // 2, y) == c.get(x1 - 1, y), key
    x0, y0, _x1, _y1 = a["rects"]["edge"]
    assert c.get(x0 + 2, y0 + 2) == R.PANEL_BLACK
