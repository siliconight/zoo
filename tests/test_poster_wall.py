"""The wall posters (1.30.0): the copy, the art, the three checks, the run.

The walker, 2026-09-29/30: posters in strip clubs, bars, alleys and stores,
by the three guides in the root repo's docs/reference/. What is held here:

  * the copy is invented, clean of real names, and every character of it is
    in the face it is set in (a missing glyph draws `?` silently);
  * every row of every family SETS -- its headline and its small line both
    fit the family's sheet (the first cut set neither on a letter-size
    handbill, and nothing said so);
  * every poster passes the art guide's three tests as `poster_checks`
    measures them, at the thresholds that module states;
  * a run fills its slot without stretching, repeats no sheet while the copy
    lasts, shares no plane, and is one object with one material.
"""
from __future__ import annotations

import json
import os
import struct

import pytest

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import card_brands as CB
from zoo_keeper.core import club_names as CN
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import kit
from zoo_keeper.core import pixel_type as pt
from zoo_keeper.core import poster_art as PA
from zoo_keeper.core import poster_checks as K
from zoo_keeper.core import poster_copy as PC
from zoo_keeper.core import poster_wall_forms as F
from zoo_keeper.core import prims as P

KEYS = ("a", "b", "c", "d")
#: The face each string is set in (`poster_art`).
HEAD_FACE = {"club": "m5x7", "bar": "m5x7", "alley": "bold", "store": "m5x7"}
SMALL_FACE = {"club": "small", "bar": "m5x7", "alley": "m5x7", "store": "small"}


def _size(family):
    wm, hm = PA.SIZES_M[family]
    return int(round(wm * CA.TEXEL)), int(round(hm * CA.TEXEL))


# --- the copy ------------------------------------------------------------------------


def test_every_string_is_in_its_face():
    for fam in PC.FAMILIES:
        for head, small in PC.COPY[fam]:
            for text, face in ((head, HEAD_FACE[fam]), (small, SMALL_FACE[fam])):
                missing = {ch for ch in text if ch != " " and ch not in pt._table(face).GLYPHS}
                assert not missing, (fam, text, face, missing)
    for text in PC.DATES:
        assert all(ch == " " or ch in pt._table("m5x7").GLYPHS for ch in text), text
    for text in CN.NAMES:
        assert all(ch == " " or ch in pt._table("small").GLYPHS for ch in text), text
    for text in ("SALE", "NOW", "HOT", "WOW", "$"):
        assert all(ch in pt._table("m5x7").GLYPHS or ch in pt._table("bold").GLYPHS for ch in text)


def test_the_copy_is_invented():
    """Each list the way its owner applies it: `card_brands.DENY_WORDS` as
    whole words (PRO is a card brand and not a crime inside PROBABLY), every
    other list as a substring."""
    import re
    parts = PC.DENYLIST + tuple(CB.DENY_PARTS) + CN.DENYLIST + CN.BEER_DENYLIST
    for text in PC.all_strings():
        up = text.upper()
        tokens = set(re.findall(r"[A-Z0-9']+", up))
        for bad in CB.DENY_WORDS:
            assert bad not in tokens, (text, bad)
        for bad in parts:
            assert bad not in up, (text, bad)


def test_the_denylist_can_fail():
    assert any(bad in "A WAWA RUN" for bad in PC.DENYLIST)


def test_the_phones_are_fiction():
    # 555-0100 to 555-0199 is the block reserved for fiction
    assert all(p[4:8] == "555-" and p[8:10] == "01" for p in PC.PHONES)


# --- the art -------------------------------------------------------------------------


@pytest.mark.parametrize("family", PC.FAMILIES)
def test_every_row_sets_both_lines(family):
    w, h = _size(family)
    for row in range(len(PC.COPY[family])):
        for key in KEYS:
            _c, info = PA.paint(family, w, h, row, key)
            assert info["title"] is not None, (family, row, key, info["headline"])
            assert info["small_at"] is not None, (family, row, key, info["small"])


@pytest.mark.parametrize("family", PC.FAMILIES)
def test_every_poster_passes_the_three_tests(family):
    """The art guide's thumbnail, grayscale and blur tests, as measured by
    `poster_checks`: the headline at 5 m, the focal image off its ground, the
    blurred masses spanning a value group."""
    w, h = _size(family)
    for row in range(len(PC.COPY[family])):
        for key in KEYS:
            c, info = PA.paint(family, w, h, row, key)
            m = K.measure(c, info, CA.TEXEL)
            tag = (family, row, key, info["headline"], m)
            assert m["title_ratio"] is not None and m["title_ratio"] >= K.TITLE_RATIO, tag
            assert m["focal_step"] is not None and m["focal_step"] >= K.FOCAL_STEP, tag
            assert m["mass_spread"] >= K.MASS_SPREAD, tag


def test_the_checks_can_fail():
    """A poster that is one flat colour fails all three, so the checks are
    measuring something."""
    from zoo_keeper.core.vending_forms import Canvas
    c = Canvas(100, 140, (120, 120, 120))
    m = K.measure(c, {"title": (5, 5, 95, 40), "focal": (20, 50, 80, 110), "ground": (120, 120, 120)},
                  CA.TEXEL)
    assert m["title_ratio"] < K.TITLE_RATIO and m["focal_step"] < K.FOCAL_STEP
    assert m["mass_spread"] < K.MASS_SPREAD


def test_the_same_poster_every_time():
    w, h = _size("club")
    a, _ = PA.paint("club", w, h, 3, "k")
    b, _ = PA.paint("club", w, h, 3, "k")
    assert bytes(a.buf) == bytes(b.buf)


# --- the run -------------------------------------------------------------------------


@pytest.mark.parametrize("family", PC.FAMILIES)
@pytest.mark.parametrize("w", [0.5, 1.0, 2.4, 4.0, 6.0])
def test_a_run_fills_its_slot_unstretched_and_shares_no_plane(family, w):
    for courses in ((1, 2) if family == "alley" else (1,)):
        h, d = F.band_height(family, courses), 0.03
        for v in range(4):
            g = F.plan(w, d, h, family, v, "t")
            lo, hi = P.bounds(g["prims"])
            assert abs(lo[0] + w / 2) <= F.FIT_TOL and abs(hi[0] - w / 2) <= F.FIT_TOL, (lo, hi)
            assert abs(lo[2]) <= F.FIT_TOL and abs(hi[2] - h) <= F.FIT_TOL, (lo, hi)
            assert hi[1] - lo[1] <= d, (lo, hi)
            assert P.coincident_pairs(g["prims"]) == []
            sw, sh = g["facts"]["sheet_m"]
            ratio = PA.SIZES_M[family][0] / PA.SIZES_M[family][1]
            assert abs(sw / sh - ratio) < 1e-3 or g["facts"]["sheets"] <= 2


def test_no_sheet_repeats_in_a_run_while_the_copy_lasts():
    g = F.plan(4.0, 0.03, F.band_height("club"), "club", 0, "t")
    rows = g["facts"]["rows"]
    assert len(rows) == len(set(rows)) == g["facts"]["sheets"]


def test_the_genome_and_the_kit_stem():
    g = genome_mod.load_species("poster_wall")
    assert genome_mod.validate_genome(g) == []
    assert g["params"]["form"] == list(PC.FAMILIES)
    slot = {"slot_id": "pw", "role": "prop", "size_mod": "full", "style": 1, "species": "poster_wall",
            "form": "alley", "variant": 3, "fit": {"dims": [2.4, 0.01, 0.814], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    assert plan["modules"][0]["stem"].endswith("_falley_n3")


# --- built -----------------------------------------------------------------------------


def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    slot = {"slot_id": "pw", "role": "prop", "size_mod": "full", "style": 1,
            "species": "poster_wall", "fit": {"dims": list(dims), "pivot": "center"}}
    slot.update(fields)
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.endswith(_COL_SUFFIXES)]
    return res, objs


@pytest.mark.parametrize("family", PC.FAMILIES)
def test_bpy_a_run_is_one_object_one_material_and_fits(tmp_path, family):
    pytest.importorskip("bpy")
    dims = (2.4, 0.01, F.band_height(family, 2 if family == "alley" else 1))
    res, objs = _build(tmp_path, dims, form=family, variant=1)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    assert len(objs) == 1, [o.name for o in objs]
    assert len({s.material.name for o in objs for s in o.material_slots}) == 1
    got = res["facts"]["dimensions"]
    assert abs(got["width"] - dims[0]) <= F.FIT_TOL and abs(got["height"] - dims[2]) <= F.FIT_TOL
    assert res["facts"]["tris"] <= res["plan"]["budgets"]["tris_lod0"]
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    ln, _kind = struct.unpack_from("<I4s", raw, 12)
    doc = json.loads(raw[20:20 + ln])
    assert len(doc["images"]) == 1 and not any(m.get("emissiveFactor") and max(m["emissiveFactor"]) > 0
                                                for m in doc["materials"])
