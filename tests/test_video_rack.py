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


def test_a_wall_faces_one_way_and_an_island_both():
    for form, want in (("wall", {"-y"}), ("adult", {"-y"}), ("island", {"-y", "+y"})):
        dims = V.DC_SIZES[3] if form == "island" else V.DC_SIZES[0]
        seen = set()
        for p in (q for q in V.plan(*dims, form, 0)["prims"] if q["mat"] == "art"):
            n = _normal(p, p["front"][0])
            assert abs(n[0]) < 1e-9 and abs(n[2]) < 1e-9, n
            seen.add("+y" if n[1] > 0 else "-y")
            # a box's front looks away from the rack's middle (an island) or
            # its back board (a wall)
            cy = sum(v[1] for v in p["verts"]) / len(p["verts"])
            if form == "island":
                assert n[1] * cy > 0, (cy, n)
        assert seen == want, (form, seen)


def test_a_wall_has_a_genre_board_a_bay_and_an_island_none():
    w, d, h = V.DC_SIZES[2]
    for variant in range(6):
        g = V.plan(w, d, h, "wall", variant)
        heads = [p["uvs"][2][0][0] for p in g["prims"] if p["mat"] == "art"
                 and p["uvs"][2][0][0].startswith("head_")]
        assert len(heads) == g["facts"]["bays"] == 4
        assert heads == ["head_" + x for x in g["facts"]["genres"]]
        # the genres run in order from the variant's start
        assert g["facts"]["genres"] == [V.GENRES[(variant + i) % len(V.GENRES)] for i in range(4)]
        # and a bay's boxes are its board's genre
        assert "adult" not in g["facts"]["genres"]
    isl = V.plan(*V.DC_SIZES[3], "island", 0)
    assert not [p for p in isl["prims"] if p["mat"] == "art" and p["uvs"][2][0][0].startswith("head_")]


def test_a_bay_rents_its_genre_and_the_back_room_only_its_own():
    genre_of = {t[0]: t[1] for t in V.TITLES}
    w, d, h = V.DC_SIZES[0]
    g = V.plan(w, d, h, "wall", 2)
    bw = g["facts"]["bay_width"]
    for p in (q for q in g["prims"] if q["mat"] == "art"):
        tile = p["uvs"][2][0][0]
        if not tile.startswith("tile_"):
            continue
        cx = sum(v[0] for v in p["verts"]) / len(p["verts"])
        bay = int((cx + w / 2.0) // bw)
        assert genre_of[tile[5:]] == g["facts"]["genres"][bay], (tile, bay)
    back = V.plan(w, d, h, "adult", 2)
    tiles = {p["uvs"][2][0][0] for p in back["prims"] if p["mat"] == "art"}
    assert tiles and all(t == "head_adult" or genre_of[t[5:]] == "adult" for t in tiles), tiles
    # and no other form rents the back room's
    for form in ("wall", "island"):
        for variant in range(6):
            dims = V.DC_SIZES[3] if form == "island" else V.DC_SIZES[2]
            for p in V.plan(*dims, form, variant)["prims"]:
                if p["mat"] == "art" and p["uvs"][2][0][0].startswith("tile_"):
                    assert genre_of[p["uvs"][2][0][0][5:]] != "adult"


def test_a_title_has_three_or_four_facings():
    w, d, h = V.DC_SIZES[0]
    g = V.plan(w, d, h, "wall", 0)
    rows = {}
    for p in (q for q in g["prims"] if q["mat"] == "art" and q["uvs"][2][0][0].startswith("tile_")):
        cx = sum(v[0] for v in p["verts"]) / len(p["verts"])
        z = round(min(v[2] for v in p["verts"]), 3)
        rows.setdefault((int((cx + w / 2.0) // g["facts"]["bay_width"]), z), []).append((cx, p["uvs"][2][0][0]))
    assert rows
    for row in rows.values():
        runs = [len(list(grp)) for _t, grp in itertools.groupby(t for _x, t in sorted(row))]
        assert all(n in (3, 4) for n in runs[:-1]), runs      # the last run is what the shelf had left


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
                                       (V.DC_SIZES[1], "adult")])
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
