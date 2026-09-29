"""1.19.0 -- the gas station's roadside price pylon.

The walker, 2026-09-28: "do the price pylon next". Pure half: the module
fills its slot exactly, no two faces share a plane, every face wound
outward, both faces read (the back reversed), the prices print to the
nine-tenths, the brand is the store's own and invented. Built half (bpy):
PASS and fit, two submissions, one lit face material Lux's power cut takes.
"""
from __future__ import annotations

import itertools
import os
import re

import pytest

from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import price_pylon_forms as PP
from zoo_keeper.core import prims as P

CASES = list(PP.DC_SIZES) + [tuple(c) for c in itertools.product(*(PP.RANGES[a] for a in ("width", "depth", "height")))]


@pytest.mark.parametrize("dims", CASES)
def test_the_pylon_fills_its_slot_and_shares_no_plane(dims):
    w, d, h = dims
    pr = PP.plan(w, d, h)["prims"]
    lo, hi = P.bounds(pr)
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-6, (dims, lo, hi)
    assert P.coincident_pairs(pr, tol=0.0022) == []
    for p in pr:
        assert PP.signed_volume(p) > 0, p["part"]
    assert P.tri_count(pr) <= genome_mod.load_species("price_pylon")["budgets"]["tris_lod0"]


def test_the_coincidence_check_can_see_a_pair_here():
    pr = PP.plan(*PP.DC_SIZES[0])["prims"]
    ctl = pr + [P.box("x", "post", (-0.1, -0.1, PP.PLINTH_H + 0.001), (0.1, 0.1, PP.PLINTH_H + 0.2))]
    assert P.coincident_pairs(ctl, tol=0.0022) != []


def test_both_faces_read_the_back_reversed():
    """Seen from +Y, +X is on the viewer's left: the back face's u must run
    the other way, or FLAPPHAS reads mirrored from half the road."""
    for p in (q for q in PP.plan(*PP.DC_SIZES[0])["prims"] if q["mat"] == "glow"):
        fx = [(p["verts"][i][0], c[1]) for i, c in zip(p["faces"][2], p["uvs"][2])]
        bx = [(p["verts"][i][0], c[1]) for i, c in zip(p["faces"][4], p["uvs"][4])]
        assert max(fx)[1] > min(fx)[1] and max(bx)[1] < min(bx)[1]


def test_the_cabinets_stack_brand_prices_strip_over_the_posts():
    b = PP.bands(6.5)
    assert b["brand"][1] == pytest.approx(6.5)
    assert b["strip"][0] < b["strip"][1] < b["price"][0] < b["price"][1] < b["brand"][0]
    assert b["strip"][0] > PP.PLINTH_H + 2.0, "a person walks under the sign"


def test_the_prices_print_to_the_nine_tenths_and_the_art_is_the_same_bytes():
    grades = [g for g, _c in PP.GRADES]
    for v in range(4):
        a = PP.art(2.4, 6.5, v)
        rows = [s for s in a["said"] if s.split()[0] in grades]
        assert len(rows) == 3 and all(s.endswith("9/10") for s in rows), rows
        assert [float(s.split()[1]) for s in rows] == sorted(float(s.split()[1]) for s in rows)
        assert bytes(PP.art(2.4, 6.5, v)["canvas"].buf) == bytes(a["canvas"].buf)
        W, H = a["size"]
        for x0, y0, x1, y1 in a["rects"].values():
            assert 0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H


DENY = ("WAWA", "SUNOCO", "EXXON", "MOBIL", "SHELL", "GETTY", "GULF", "CITGO", "7-ELEVEN", "SHEETZ", "TEXACO")


def test_the_brand_is_the_stores_own_and_invented():
    assert PP.STORE == "FLAPPHAS"
    words = " ".join([PP.STORE, PP.STRIP] + [g for g, _c in PP.GRADES])
    for mark in DENY:
        assert not re.search(r"\b" + re.escape(mark) + r"\b", words), mark


def test_the_genome_names_the_parts_and_validates():
    g = genome_mod.load_species("price_pylon")
    assert genome_mod.validate_genome(g) == []
    for a in ("width", "depth", "height"):
        assert (g["dimensions"][a]["min"], g["dimensions"][a]["max"]) == PP.RANGES[a]
    assert {p["part"] for p in PP.plan(*PP.DC_SIZES[0])["prims"]} == set(g["parts"])


def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "price_pylon", "role": "prop", "size_mod": "full", "style": 1,
            "species": "price_pylon", "material": "metal",
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


@pytest.mark.parametrize("dims", [PP.DC_SIZES[0], (3.4, 0.8, 9.0)])
def test_bpy_the_pylon_passes_and_fits(tmp_path, dims):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    parts = set(genome_mod.load_species("price_pylon")["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name
        assert "." not in o.name, o.name


def test_bpy_two_submissions_and_the_face_is_lux_s(tmp_path):
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, PP.DC_SIZES[0])
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    names = [m["name"] for m in doc["materials"]]
    assert len(names) == 2, names
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 2
    lit = [m["name"] for m in doc["materials"] if m.get("emissiveFactor") and any(m["emissiveFactor"])]
    assert len(lit) == 1 and lit[0].startswith("M_Pylon_pylon_") and lit[0].endswith("_Face"), lit


def test_bpy_the_same_file_every_build(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, PP.DC_SIZES[0], variant=1)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]


# --------------------------------------------------------------------------- #
# 1.25.0: the type is set as large as the face allows
# --------------------------------------------------------------------------- #

def _ink_rows(A, rect, colour):
    c = A["canvas"]
    x0, y0, x1, y1 = rect
    rows = [y for y in range(y0, y1) if any(c.get(x, y) == colour for x in range(x0, x1))]
    return (min(rows), max(rows)) if rows else None


def test_the_name_fills_half_its_face_and_the_dollars_their_row():
    A = PP.art(2.4, 6.5, 0)
    x0, y0, x1, y1 = A["rects"]["brand"]
    ink = PP.COLOURWAYS[0][2]
    top, bot = _ink_rows(A, A["rects"]["brand"], ink)
    # 1.19.0 set FLAPPHAS 21 px tall in a 112 px face
    assert bot - top + 1 >= 0.35 * (y1 - y0), (top, bot)
    assert top > y0 + 4 and bot < y1 - 4                     # inside the rules
    px0, py0, px1, py1 = A["rects"]["price"]
    row = (py1 - py0) // len(PP.GRADES)
    t, b = _ink_rows(A, (int(px1 * PP.DIGITS_AT), py0 + 1, int(px1 * 0.8), py0 + row), PP.INK)
    assert b - t + 1 >= row // 2, (t, b, row)                # 1.19.0: 14 of 40


def test_the_prices_fit_beside_the_grades_and_inside_the_face():
    from zoo_keeper.core import pixel_type as pt
    A = PP.art(2.4, 6.5, 0)
    FW = A["rects"]["price"][2]
    chip = max(6, FW // 16)
    gs = min(PP._scale(g, FW * 0.38, 34, "m5x7", 2) for g, _c in PP.GRADES)
    label_end = chip + 4 + max(pt.ink_width(g, gs, "m5x7") for g, _c in PP.GRADES)
    dx = int(FW * PP.DIGITS_AT)
    assert label_end < dx
    for dollars in PP.PRICE_SETS[0]:
        ds = PP._scale(dollars, FW * PP.DIGITS_W, 34, PP.HEAD_FACE, 5)
        assert ds >= 3, dollars                                 # 1.19.0: 2
        end = dx + pt.ink_width(dollars, ds, PP.HEAD_FACE) + 3 + pt.ink_width("9/10", max(1, ds // 2), "m5x7")
        assert end <= FW, (dollars, end, FW)
