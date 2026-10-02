"""The video store's tape racks (1.43.0): wall, island, back room; two draws.

The walker, 2026-09-29: "a new building type: a VHS movie rental store";
2026-10-02: MACDADE MOVIES, the curtained back room "suggestive only", the
rest from the era. Pure half (`core/video_rack_forms.py`): the module fills
its slot exactly, no two faces share a plane, every face wound outward, the
boxes face out, a wall carries a genre board a bay and an island none, the
back room rents only its own, every tile is inside the art and every word
sets, and every title is invented. Built half (bpy, skipped without it):
PASS and fit, two submissions over two materials, determinism.
"""
from __future__ import annotations

import itertools
import math
import os
import re

import pytest

from zoo_keeper.core import candy_brands as CB
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import prims as P
from zoo_keeper.core import snack_brands as SB
from zoo_keeper.core import storefront_names as SN
from zoo_keeper.core import video_rack_forms as V

CASES = [(d, f) for d in V.DC_SIZES for f in V.FORMS] + [
    (tuple(c), f) for c in itertools.product(*(V.RANGES[a] for a in ("width", "depth", "height")))
    for f in V.FORMS]

#: Rental chains (Philadelphia's own first), studios, and the film titles a
#: parody reaches for, as whole words or phrases.
REAL = ("BLOCKBUSTER", "HOLLYWOOD VIDEO", "WEST COAST VIDEO", "MOVIES UNLIMITED", "MOVIE GALLERY",
        "FAMILY VIDEO", "SUNCOAST", "WAWA", "DISNEY", "PARAMOUNT", "UNIVERSAL", "WARNER",
        "COLUMBIA", "MIRAMAX", "ROCKY", "DIE HARD", "ROBOCOP", "TERMINATOR", "ALIEN", "PREDATOR",
        "STAR WARS", "STAR TREK", "JAWS", "GHOSTBUSTERS", "RAMBO", "TOP GUN", "HOME ALONE",
        "THE BLOB", "THE THING", "MANNEQUIN", "TRADING PLACES", "WITNESS", "PLAYBOY", "PENTHOUSE",
        "HUSTLER", "VIVID")


@pytest.mark.parametrize("dims,form", CASES)
def test_the_rack_fills_its_slot_and_shares_no_plane(dims, form):
    w, d, h = dims
    for variant in (0, 1, 4):
        pr = V.plan(w, d, h, form, variant)["prims"]
        lo, hi = P.bounds(pr)
        for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
            assert abs(a - b) < 1e-6, (dims, form, lo, hi)
        assert P.coincident_pairs(pr, tol=0.0022) == []
        for p in pr:
            assert V.signed_volume(p) > 0, (p["part"], p["mat"])
        assert P.tri_count(pr) <= genome_mod.load_species("video_rack")["budgets"]["tris_lod0"]


def _normal(p, k):
    a, b, c = (p["verts"][i] for i in p["faces"][k][:3])
    u = [b[j] - a[j] for j in range(3)]
    v = [c[j] - a[j] for j in range(3)]
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def test_every_face_maps_into_the_art_and_no_two_tiles_overlap():
    art = V.rack_art()
    W, H = art["size"]
    for form in V.FORMS:
        dims = V.DC_SIZES[3] if form == "island" else V.DC_SIZES[0]
        for p in (q for q in V.plan(*dims, form, 1)["prims"] if q["mat"] == "art"):
            assert len(p["uvs"]) == len(p["faces"])
            for k, f in enumerate(p["uvs"]):
                for c in f:
                    assert c[0] in art["rects"], c[0]
                    assert (len(c) == 3) == (k in p["front"])
    tiles = list(art["rects"].items())
    for n, (x0, y0, x1, y1) in tiles:
        assert 0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H, n
    for (n, r), (m, q) in itertools.combinations(tiles, 2):
        assert r[2] <= q[0] or q[2] <= r[0] or r[3] <= q[1] or q[3] <= r[1], (n, m)


def test_the_art_is_the_same_bytes_and_says_every_word():
    a, b = V.rack_art(), V.rack_art()
    assert bytes(a["canvas"].buf) == bytes(b["canvas"].buf) and a["name"] == b["name"]
    for t in V.TITLES:
        for word in t[2]:
            assert word in a["said"], (t[0], word)
            assert len(word) <= 6, (t[0], word)
    for g in V.BOARDS:
        assert V.BOARDS[g][0] in a["said"]
    assert len({t[0] for t in V.TITLES}) == len(V.TITLES)
    for g in V.GENRES + ("adult",):
        assert len(V.BY_GENRE[g]) >= 5, g


def test_every_title_is_invented():
    for text in V.all_words():
        up = text.upper()
        toks = set(re.findall(r"[A-Z0-9&'!]+", up))
        for w_ in SB.DENY_WORDS + CB.DENY_WORDS:
            assert w_ not in toks, (text, w_)
        for part in SB.DENY_PARTS + CB.DENY_PARTS:
            assert part not in up, (text, part)
        for real in REAL:
            assert not re.search(r"(?<![A-Z])" + re.escape(real) + r"(?![A-Z])", up), (text, real)


def test_the_door_says_the_walkers_name():
    for business in ("video_store_a01 video_store", "lf_video_block_001_9080 video_store"):
        s = SN.sign_for(business)
        assert s["kind"] == "video" and s["text"] == V.STORE == "MACDADE MOVIES"
    # and it claims nothing it should not
    assert SN.sign_for("card_shop_a01 card_shop")["kind"] == "card"
    assert SN.sign_for("pawn_shop_a01")["kind"] == "pawn"


def test_the_genome_names_the_parts_and_validates():
    g = genome_mod.load_species("video_rack")
    assert genome_mod.validate_genome(g) == []
    r = g["dimensions"]
    for axis in ("width", "depth", "height"):
        assert (r[axis]["min"], r[axis]["max"]) == V.RANGES[axis]
    assert tuple(g["params"]["form"]) == V.FORMS
    assert g["module_variants"] == len(V.GENRES)
    for form in V.FORMS:
        assert {p["part"] for p in V.plan(*V.DC_SIZES[0], form)["prims"]} <= set(g["parts"])
    with pytest.raises(ValueError):
        V.plan(3.0, 0.45, 2.0, "shelf")


def _tile(p):
    return p["uvs"][p["front"][0]][0][0]


def _art(form, variant=0, dims=None):
    dims = dims or (V.DC_SIZES[3] if form == "island" else V.DC_SIZES[0])
    g = V.plan(*dims, form, variant)
    return g, [q for q in g["prims"] if q["mat"] == "art"], dims


def test_every_front_faces_out_of_its_rack():
    """A wall, the back room's and the display rack are shopped from -Y; an
    island from both faces, and its two aisle-end signs look along the
    aisle. A display box leans back, so its front looks a little UP."""
    lean = math.sin(math.radians(V.LEAN_DEG))
    for form, want in (("wall", {"-y"}), ("adult", {"-y"}), ("display", {"-y"}),
                       ("island", {"-y", "+y", "-x", "+x"})):
        g, art, (w, d, h) = _art(form)
        seen = set()
        for p in art:
            n = _normal(p, p["front"][0])
            size = sum(c * c for c in n) ** 0.5
            n = [c / size for c in n]
            if _tile(p).startswith("tile_"):
                assert form == "display" and abs(n[2] - lean) < 1e-6, (form, n)
            else:
                assert abs(n[2]) < 1e-9, (form, _tile(p), n)
            if abs(n[0]) > abs(n[1]):
                assert _tile(p).startswith("cap_"), _tile(p)
                # the sign's face IS the slot's end
                x = max(v[0] for v in p["verts"]) if n[0] > 0 else min(v[0] for v in p["verts"])
                assert abs(abs(x) - w / 2.0) < 1e-9
                seen.add("+x" if n[0] > 0 else "-x")
            else:
                seen.add("+y" if n[1] > 0 else "-y")
        assert seen == want, (form, seen)


def test_the_sections_run_in_order_and_new_releases_is_the_display_racks():
    w, d, h = V.DC_SIZES[2]
    for variant in range(6):
        g, art, _d = _art("wall", variant, V.DC_SIZES[2])
        heads = [_tile(p) for p in art if _tile(p).startswith("head_")]
        assert len(heads) == g["facts"]["bays"] == 4
        assert heads == ["head_" + x for x in g["facts"]["genres"]]
        assert g["facts"]["genres"] == [V.AISLE_GENRES[(variant + i) % len(V.AISLE_GENRES)] for i in range(4)]
        assert "new" not in g["facts"]["genres"] and "adult" not in g["facts"]["genres"]
    g, art, _d = _art("display")
    assert set(g["facts"]["genres"]) == {"new"}
    assert {_tile(p) for p in art if _tile(p).startswith("head_")} == {"head_new"}
    g, art, _d = _art("island")
    assert not [p for p in art if _tile(p).startswith("head_")]
    assert sorted(_tile(p) for p in art if _tile(p).startswith("cap_")) == sorted(
        "cap_" + x for x in (g["facts"]["genres"][0], g["facts"]["genres"][g["facts"]["bays"] - 1]))


def test_a_bay_rents_its_section_and_the_back_room_only_its_own():
    genre_of = {t[0]: t[1] for t in V.TITLES}
    g, art, (w, d, h) = _art("wall", 2)
    bw = g["facts"]["bay_width"]
    for p in art:
        if _tile(p).startswith("spines_"):
            cx = sum(v[0] for v in p["verts"]) / len(p["verts"])
            assert _tile(p) == "spines_" + g["facts"]["genres"][int((cx + w / 2.0) // bw)]
    _g, art, _d = _art("adult", 2)
    assert {_tile(p) for p in art} <= {"spines_adult", "head_adult"} | set(V.TAGS)
    _g, art, _d = _art("display", 2)
    for p in art:
        assert _tile(p) == "head_new" or genre_of[_tile(p)[5:]] == "new", _tile(p)
    # and no other form rents the back room's
    for form in ("wall", "island", "display"):
        for variant in range(6):
            _g, art, _d = _art(form, variant)
            assert not [p for p in art if "adult" in _tile(p)], (form, variant)


def test_spines_out_pack_a_shelf():
    """The walker's photographs: shelves are dense rows of tape SPINES, top
    edges uneven. Thirty tapes a metre of shelf or more; each block a whole
    number of tapes showing its own stretch of the strip; blocks 3 mm apart
    or more (touching, two share a plane); more than one height."""
    g, art, (w, d, h) = _art("wall", 1)
    blocks = [p for p in art if _tile(p).startswith("spines_")]
    shelves, heights = {}, set()
    for p in blocks:
        xs = [v[0] for v in p["verts"]]
        zs = [v[2] for v in p["verts"]]
        n = round((max(xs) - min(xs)) / V.SPINE_W)
        assert abs((max(xs) - min(xs)) - n * V.SPINE_W) < 1e-9 and n >= 2
        u = sorted({c[1] for c in p["uvs"][p["front"][0]]})
        assert 0.0 <= u[0] < u[1] <= 1.0 and abs((u[1] - u[0]) - n / float(V.STRIP_SPINES)) < 1e-9
        heights.add(round(max(zs) - min(zs), 4))
        bay = int((min(xs) + w / 2.0) // g["facts"]["bay_width"])
        shelves.setdefault((bay, round(min(zs), 3)), []).append((min(xs), max(xs), n))
    assert len(heights) >= 2
    assert sum(n for row in shelves.values() for _a, _b, n in row) == g["facts"]["tapes"]
    for row in shelves.values():
        row.sort()
        assert len(row) >= 2
        for (a0, a1, _n), (b0, _b1, _m) in zip(row, row[1:]):
            assert b0 - a1 >= 0.003 - 1e-9
        assert sum(n for _a, _b, n in row) >= 30 * g["facts"]["bay_width"] * 0.9, row


def test_the_display_rack_faces_its_boxes_out_three_or_four_a_title():
    g, art, (w, d, h) = _art("display")
    rows = {}
    for p in (q for q in art if _tile(q).startswith("tile_")):
        cx = sum(v[0] for v in p["verts"]) / len(p["verts"])
        z = round(min(v[2] for v in p["verts"]), 2)
        rows.setdefault((int((cx + w / 2.0) // g["facts"]["bay_width"]), z), []).append((cx, _tile(p)))
    assert rows and g["facts"]["boxes"] == sum(len(r) for r in rows.values())
    for row in rows.values():
        runs = [len(list(grp)) for _t, grp in itertools.groupby(t for _x, t in sorted(row))]
        assert all(n in (3, 4) for n in runs[:-1]), runs      # the last run is what the shelf had left


def test_a_unit_is_painted_one_colour_and_the_display_rack_is_black():
    assert [V.unit_colour("wall", v) for v in range(4)] == list(V.UNIT_COLOURS)
    assert V.unit_colour("island", 5) == V.UNIT_COLOURS[1]
    assert V.unit_colour("display", 2) == V.WIRE == V.unit_colour("adult", 2)
    assert len(set(V.UNIT_COLOURS)) == len(V.UNIT_COLOURS) == 4
    unit = V.UNIT_COLOURS[0]
    _k, steel = V.vertex_tint("steel", unit)
    _k, kick = V.vertex_tint("kick", unit)
    _k, lip = V.vertex_tint("lip", unit)
    assert steel == unit and all(a < b for a, b in zip(kick, steel)) and all(a > b for a, b in zip(lip, steel))
    # with no unit it is the grey 1.43.0 shipped
    assert V.vertex_tint("steel")[1] == V.MATERIALS["steel"][0]
    assert V.plan(*V.DC_SIZES[0], "wall", 3)["facts"]["unit"] == V.UNIT_COLOURS[3]


def test_a_shelf_carries_a_tag_or_two_inside_its_lip():
    g, art, _d = _art("wall", 0)
    tags = [p for p in art if _tile(p) in V.TAGS]
    lips = [p for p in g["prims"] if p["part"] == "VideoRack_Lip"]
    assert len(lips) <= len(tags) <= 2 * len(lips)
    assert {_tile(p) for p in tags} == set(V.TAGS)
    for t in tags:
        lo, hi = P.bounds([t])
        host = [l for l in lips if P.bounds([l])[0][0] <= lo[0] and hi[0] <= P.bounds([l])[1][0]
                and P.bounds([l])[0][2] < lo[2] and hi[2] < P.bounds([l])[1][2]]
        assert len(host) == 1, (lo, hi)
        assert lo[1] < P.bounds(host)[0][1] < hi[1]            # proud of its face, and into it
    assert not [p for p in _art("display")[1] if _tile(p) in V.TAGS]


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "tape_wall_r0123abcd_1", "role": "prop", "size_mod": "full", "style": 1,
            "species": "video_rack", "material": "metal",
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


@pytest.mark.parametrize("dims,form", [(V.DC_SIZES[0], "wall"), (V.DC_SIZES[3], "island"),
                                       (V.DC_SIZES[1], "adult"), (V.DC_SIZES[0], "display")])
def test_bpy_a_rack_passes_fits_and_is_two_submissions(tmp_path, dims, form):
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, objs = _build(tmp_path, dims, form=form, variant=2)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    parts = set(genome_mod.load_species("video_rack")["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    assert len(doc["materials"]) == 2, [m["name"] for m in doc["materials"]]
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 2, [m["name"] for m in visual]
    lit = [m["name"] for m in doc["materials"] if m.get("emissiveFactor") and any(m["emissiveFactor"])]
    assert lit == []


def test_bpy_the_same_file_every_build(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, V.DC_SIZES[0], form="wall", variant=3)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]
