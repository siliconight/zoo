"""1.81.0 -- the corner deli's service case.

Deli Counter's corner deli has stood a `deli_case_cover` since the recipe was
written, and no species answered to it: cold run 9189 built
`prop_delco_1997_03_w700_d110_h130_mglass`, a plain glass box. Pure half
(`core/deli_case_forms.py`): the module fills its slot exactly, no two faces
share a plane, every face is wound outward, the deck is cut a bay at a time,
the pieces lie behind the glass and under the top with their cut faces to the
customer, every glowing face maps into the glow image, and the art is
deterministic. Built half (bpy, skipped without it): PASS and fit, three
submissions over three materials, the glow the only lit material and the
glass blended, the same file every build.
"""
from __future__ import annotations

import itertools
import os

import pytest

from zoo_keeper.core import deli_case_forms as D
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import prims as P

CASES = list(D.DC_SIZES) + [tuple(c) for c in itertools.product(*(D.RANGES[a] for a in ("width", "depth", "height")))]


@pytest.mark.parametrize("dims", CASES)
def test_the_case_fills_its_slot_and_shares_no_plane(dims):
    w, d, h = dims
    pr = D.plan(w, d, h, "deli_case", 1)["prims"]
    lo, hi = P.bounds(pr)
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-6, (dims, lo, hi)
    assert P.coincident_pairs(pr, tol=0.0022) == []
    for p in pr:
        assert D.signed_volume(p) > 0, (p["part"], p["mat"])
    assert P.tri_count(pr) <= genome_mod.load_species("deli_case")["budgets"]["tris_lod0"]


@pytest.mark.parametrize("dims", CASES)
def test_the_deck_is_cut_a_bay_at_a_time_and_the_tiles_are_bounded(dims):
    w, d, h = dims
    f = D.plan(w, d, h)["facts"]
    n, bw = D.bays(w)
    assert f["bays"] == n >= 1 and 0.6 <= bw <= 1.8, (n, bw)
    assert f["tiles"] == list(range(min(n, D.TILES_MAX)))
    art = D.glow_art(w, d, h)
    assert {"bay_%d" % t for t in f["tiles"]} <= set(art["rects"])


@pytest.mark.parametrize("dims", CASES)
def test_the_pieces_lie_behind_the_glass_under_the_top(dims):
    """Every log and block on the deck's back half, inside the end panes,
    clear of the glass's inside and under the top's underside."""
    w, d, h = dims
    g = D.plan(w, d, h)
    f = g["facts"]
    y_head, _z_head = f["glass_head"]
    z_top0 = h - D.TOP_T
    xin = w / 2.0 - D.END_IN - D.END_T
    pieces = [p for p in g["prims"] if p["mat"] == "glow" and p["part"] == "DeliCase_Glow"
              and len(p["faces"]) in (6, 14) and any(c[0] != "dark" and c[0] != "solid"
                                                     and c[0].endswith("_cut")
                                                     for corners in p["uvs"] for c in corners)]
    assert len(pieces) == len(f["pieces"]) >= 1
    for p in pieces:
        lo, hi = P.bounds([p])
        assert -xin < lo[0] and hi[0] < xin, (lo, hi)
        assert lo[1] >= y_head - 1e-9 and hi[1] <= f["deck"][1], (lo, hi, y_head)
        assert hi[2] < z_top0, (hi, z_top0)


def test_a_cut_face_looks_at_the_customer():
    """The cut end of a log, and the cut face of a block, face -Y -- the
    glass -- and fill their painted cross-section edge to edge."""
    g = D.plan(*D.DC_SIZES[0])
    seen = 0
    for p in g["prims"]:
        if p["mat"] != "glow":
            continue
        for f, corners in zip(p["faces"], p["uvs"]):
            if not corners or corners[0][0] in ("dark", "solid") or not corners[0][0].endswith("_cut"):
                continue
            vs = [p["verts"][i] for i in f]
            n = P._cross(P._sub(vs[1], vs[0]), P._sub(vs[2], vs[0]))
            assert n[1] < 0 and abs(n[1]) > 10 * max(abs(n[0]), abs(n[2])), (p["part"], n)
            us = [c[1] for c in corners]
            vv = [c[2] for c in corners]
            assert min(us) >= -1e-9 and max(us) <= 1 + 1e-9 and min(vv) >= -1e-9 and max(vv) <= 1 + 1e-9
            seen += 1
    assert seen == len(g["facts"]["pieces"])


def test_only_the_glow_is_lit_and_every_glowing_face_maps_into_the_image():
    w, d, h = D.DC_SIZES[0]
    g = D.plan(w, d, h)
    art = D.glow_art(w, d, h)
    for p in g["prims"]:
        if p["mat"] != "glow":
            continue
        assert len(p["uvs"]) == len(p["faces"])
        for corners in p["uvs"]:
            for c in corners:
                region = c[1] if c[0] == "solid" else c[0]
                assert c[0] == "dark" or region in art["rects"], c
    assert {"tube", "dark"} <= set(art["rects"])
    x0, y0, _x1, _y1 = art["rects"]["tube"]
    assert art["canvas"].get(x0 + 1, y0 + 1) == (255, 255, 248)
    assert set(D.MATERIALS) >= {p["mat"] for p in g["prims"]} - {"glow"}


def test_the_glow_art_is_the_same_bytes_and_every_price_sets():
    a, b = D.glow_art(5.815, 1.1, 1.3, "deli_case", 3), D.glow_art(5.815, 1.1, 1.3, "deli_case", 3)
    assert bytes(a["canvas"].buf) == bytes(b["canvas"].buf) and a["name"] == b["name"]
    assert a["unset"] == [], a["unset"]
    x0, y0, x1, y1 = a["rects"]["bay_0"]
    px = {a["canvas"].get(x, y) for x in range(x0, x1, 5) for y in range(y0, y1, 5)}
    assert len(px) >= 40                      # pans, cards, parsley and trays, not a flat tile
    for kind in D.PIECES:
        x0, y0, x1, y1 = a["rects"][kind + "_cut"]
        assert len({a["canvas"].get(x, y) for x in range(x0, x1, 3) for y in range(y0, y1, 3)}) >= 3, kind


def test_the_variant_chooses_the_band_and_the_order():
    bands = {D.vertex_tint("trim", v)[1] for v in range(4)}
    assert len(bands) == 4
    assert D.vertex_tint("enamel", 0) == D.vertex_tint("enamel", 3)
    orders = {tuple(D.plan(5.815, 1.1, 1.3, "deli_case", v)["facts"]["pieces"]) for v in range(4)}
    assert len(orders) > 1


def test_nothing_on_the_case_names_a_brand():
    """Every word painted on the case is a price; the cold cuts and salads
    are generic names in code, never painted."""
    import re
    assert all(re.fullmatch(r"\d\.\d\d", p) for p in D.PRICES)


def test_the_genome_names_the_parts_and_validates():
    g = genome_mod.load_species("deli_case")
    assert genome_mod.validate_genome(g) == []
    r = g["dimensions"]
    for a in ("width", "depth", "height"):
        assert (r[a]["min"], r[a]["max"]) == D.RANGES[a]
    parts = set(g["parts"])
    for dims in D.DC_SIZES:
        assert {p["part"] for p in D.plan(*dims)["prims"]} <= parts
    assert D.DC_SIZES[0][0] >= r["width"]["min"] and D.DC_SIZES[1][0] <= r["width"]["max"]


def test_the_recipe_builds_from_the_plan():
    """Read as source: the recipe draws what the plan returns and carries no
    geometry of its own."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "zoo_keeper", "recipes", "deli_case.py"), encoding="utf-8").read()
    assert "DC.plan(" in src and "DC.glow_art(" in src
    assert "add_box" not in src and "P.box" not in src


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "deli_case_cover", "role": "prop", "size_mod": "full", "style": 1,
            "species": "deli_case", "material": "glass",
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


@pytest.mark.parametrize("dims", D.DC_SIZES)
def test_bpy_the_case_passes_and_fits(tmp_path, dims):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    parts = set(genome_mod.load_species("deli_case")["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name
        assert "." not in o.name, o.name


def test_bpy_three_submissions_and_the_glow_is_the_lit_one(tmp_path):
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, D.DC_SIZES[0])
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    names = [m["name"] for m in doc["materials"]]
    assert len(names) == 3, names
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 3, [m["name"] for m in visual]
    lit = [m["name"] for m in doc["materials"] if (m.get("emissiveFactor") and any(m["emissiveFactor"]))
           or "emissiveTexture" in m]
    assert len(lit) == 1 and lit[0].startswith("M_DeliCase_") and lit[0].endswith("_Face"), lit
    glass = [m for m in doc["materials"] if "glass" in m["name"]]
    assert len(glass) == 1 and glass[0].get("alphaMode") == "BLEND", glass


def test_bpy_the_same_file_every_build(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, D.DC_SIZES[0], variant=2)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]
