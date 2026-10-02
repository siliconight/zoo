"""1.13.0 -- the convenience store's island snack gondola.

The walker, 2026-09-28: "do the snack gondolas next"; the reference asks for
"four or five shelves of chip bags faced out, end caps stacked with more
chips". Pure half (`core/snack_gondola_forms.py`, `core/snack_brands.py`):
the module fills its slot exactly, no two faces share a plane, every face
wound outward, the bays, end caps and bags follow the run, both faces and
both end caps face out, every bag's faces map into the art, and the brands
are invented. Built half (bpy, skipped without it): PASS and fit, two
submissions over two materials, determinism.
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
from zoo_keeper.core import snack_gondola_forms as S

CASES = list(S.DC_SIZES) + [tuple(c) for c in itertools.product(*(S.RANGES[a] for a in ("width", "depth", "height")))]


@pytest.mark.parametrize("dims", CASES)
def test_the_gondola_fills_its_slot_and_shares_no_plane(dims):
    w, d, h = dims
    pr = S.plan(w, d, h, "snack_gondola", 1)["prims"]
    lo, hi = P.bounds(pr)
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-6, (dims, lo, hi)
    assert P.coincident_pairs(pr, tol=0.0022) == []
    for p in pr:
        assert S.signed_volume(p) > 0, (p["part"], p["mat"])
    assert P.tri_count(pr) <= genome_mod.load_species("snack_gondola")["budgets"]["tris_lod0"]


@pytest.mark.parametrize("dims", CASES)
def test_bays_end_caps_and_bags_follow_the_run(dims):
    w, d, h = dims
    g = S.plan(w, d, h)
    f = g["facts"]
    assert f["end_caps"] == (w >= S.ENDCAP_MIN_W)
    assert f["bay_width"] <= S.BAY_MAX + 1e-9
    bags = [p for p in g["prims"] if p["mat"] == "bag"]
    assert len(bags) == f["bags"] >= 2 * f["bays"] * (f["shelves"] - 0)
    assert f["shelves"] >= 3 if h >= 1.5 else f["shelves"] >= 2


def test_both_faces_and_both_end_caps_face_out():
    """A bag's printed front is its four crowned quads; their normal must
    point away from the gondola -- -Y on one face, +Y on the other, -X and
    +X on the end caps."""
    w, d, h = S.DC_SIZES[0]
    pr = S.plan(w, d, h)["prims"]
    seen = set()
    for p in (q for q in pr if q["mat"] == "bag"):
        a, b, c = (p["verts"][i] for i in p["faces"][p["front"][0]][:3])
        u = [b[k] - a[k] for k in range(3)]
        v = [c[k] - a[k] for k in range(3)]
        n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        cx = sum(q[0] for q in p["verts"]) / len(p["verts"])
        cy = sum(q[1] for q in p["verts"]) / len(p["verts"])
        if abs(n[1]) >= abs(n[0]):
            assert n[1] * cy > 0, (cx, cy, n)
            seen.add("+y" if cy > 0 else "-y")
        else:
            assert n[0] * cx > 0, (cx, cy, n)
            seen.add("+x" if cx > 0 else "-x")
    assert seen == {"+y", "-y", "+x", "-x"}


def test_every_bag_face_maps_into_the_art():
    art = S.bag_art()
    for p in (q for q in S.plan(*S.DC_SIZES[2])["prims"] if q["mat"] == "bag"):
        assert len(p["uvs"]) == len(p["faces"])
        # 1.40.0: a stock item names its own front faces -- a bag's four
        # crowned quads, a carton's one
        fronts = [c for k in p["front"] for c in p["uvs"][k]]
        assert all(c[0].startswith("tile_") and c[0] in art["rects"] for c in fronts)
        assert all(0.0 <= c[1] <= 1.0 and 0.0 <= c[2] <= 1.0 for c in fronts)
        others = [c for k, f in enumerate(p["uvs"]) if k not in p["front"] for c in f]
        assert all(c[0].startswith("solid_") and c[0] in art["rects"] for c in others)


def test_the_art_is_the_same_bytes_and_says_the_brands():
    a, b = S.bag_art(), S.bag_art()
    assert bytes(a["canvas"].buf) == bytes(b["canvas"].buf) and a["name"] == b["name"]
    # 1.40.0: the chips first and as they were, then every boxed product
    # and every candy bag; a carton says the YUMMYJAWNS mark too
    assert a["said"][:len(SB.BRANDS)] == [br["short"] for br in SB.BRANDS]
    for br in SB.BOXED + CB.BRANDS:
        assert br["short"] in a["said"], br["id"]
    assert a["said"].count(SB.CAKE_MARK) == len(SB.BOXED_IDS["cake"])


def test_no_two_tiles_overlap_and_every_tile_is_inside_the_art():
    a = S.bag_art()
    W, H = a["size"]
    tiles = [(n, r) for n, r in a["rects"].items()]
    for n, (x0, y0, x1, y1) in tiles:
        assert 0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H, n
    for (n, r), (m, q) in itertools.combinations(tiles, 2):
        assert r[2] <= q[0] or q[2] <= r[0] or r[3] <= q[1] or q[3] <= r[1], (n, m)


def test_one_face_is_the_chip_aisle_and_the_other_is_sections():
    """1.40.0. The walker's 90s snack references: "fruit snacks, lunch kits,
    snack cakes on shelves, candy". The -Y face is chips; the +Y face
    cycles the four sections a bay each; the end caps are chips."""
    w, d, h = S.DC_SIZES[0]
    g = S.plan(w, d, h)
    f = g["facts"]
    assert sum(f["stock"].values()) == f["bags"]
    assert set(f["stock"]) == {"chips"} | set(S.SECTIONS), f["stock"]
    kind_of = {i: "chips" for i in SB.IDS}
    kind_of.update({i: "candy" for i in CB.IDS})
    kind_of.update({b["id"]: b["kind"] for b in SB.BOXED})
    for p in (q for q in g["prims"] if q["mat"] == "bag"):
        brand = p["uvs"][p["front"][0]][0][0][len("tile_"):]
        cy = sum(v[1] for v in p["verts"]) / len(p["verts"])
        cx = sum(v[0] for v in p["verts"]) / len(p["verts"])
        if abs(cx) > f["run"] / 2.0 or cy < 0:           # an end cap, or the chip aisle
            assert kind_of[brand] == "chips", (brand, cx, cy)
        else:
            assert kind_of[brand] in S.SECTIONS, (brand, cx, cy)
    # the shortest run is one bay: still one section, whatever it is
    f1 = S.plan(S.RANGES["width"][0], 1.0, 1.6)["facts"]
    assert len(set(f1["stock"]) - {"chips"}) == 1, f1["stock"]


def test_a_shelf_of_snack_cakes_is_one_flavour_and_the_next_is_another():
    """ "four to six of each flavour side by side ... from two metres it
    reads as stripes of colour" (docs/proposals/GAS_STATION_SHOP.md)."""
    w, d, h = S.DC_SIZES[0]
    cakes = set(SB.BOXED_IDS["cake"])
    by_shelf = {}
    for p in (q for q in S.plan(w, d, h)["prims"] if q["mat"] == "bag"):
        brand = p["uvs"][p["front"][0]][0][0][len("tile_"):]
        if brand in cakes:
            cx = sum(v[0] for v in p["verts"]) / len(p["verts"])
            z = round(min(v[2] for v in p["verts"]), 3)
            by_shelf.setdefault((round(cx / S.BAY_MAX), z), []).append((cx, brand))
    assert by_shelf
    for (_bay, _z), row in by_shelf.items():
        assert 4 <= len(row) <= 6, len(row)
    # one bay's shelves, bottom to top: neighbours differ
    bay = sorted({b for b, _z in by_shelf})[0]
    stack = [sorted(by_shelf[k])[0][1] for k in sorted(by_shelf) if k[0] == bay]
    assert all(a != b for a, b in zip(stack, stack[1:])), stack


def test_every_boxed_product_is_invented_and_legible():
    ids = {b["id"] for b in SB.BRANDS} | set(CB.IDS)
    for br in SB.BOXED:
        assert br["id"] not in ids
        ids.add(br["id"])
        assert br["kind"] in SB.BOXED_KINDS and len(br["short"]) <= 6
        up = SB.words(br).upper()
        toks = set(re.findall(r"[A-Z0-9&'!]+", up))
        for w_ in SB.DENY_WORDS + CB.DENY_WORDS:
            assert w_ not in toks, (br["id"], w_)
        for part in SB.DENY_PARTS + CB.DENY_PARTS:
            assert part not in up, (br["id"], part)
    assert SB.CAKE_MARK not in SB.DENY_WORDS


def test_every_snack_brand_is_invented_and_legible():
    ids = set()
    for br in SB.BRANDS:
        assert br["id"] not in ids
        ids.add(br["id"])
        assert br["design"] in SB.DESIGNS and len(br["short"]) <= 6
        up = SB.words(br).upper()
        toks = set(re.findall(r"[A-Z0-9&'!]+", up))
        for w_ in SB.DENY_WORDS:
            assert w_ not in toks, (br["id"], w_)
        for part in SB.DENY_PARTS:
            assert part not in up, (br["id"], part)


def test_the_genome_names_the_parts_and_validates():
    g = genome_mod.load_species("snack_gondola")
    assert genome_mod.validate_genome(g) == []
    r = g["dimensions"]
    assert (r["width"]["min"], r["width"]["max"]) == S.RANGES["width"]
    assert {p["part"] for p in S.plan(*S.DC_SIZES[0])["prims"]} <= set(g["parts"])


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "gondola_aisle_1", "role": "prop", "size_mod": "full", "style": 1,
            "species": "snack_gondola", "material": "metal",
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


@pytest.mark.parametrize("dims", S.DC_SIZES)
def test_bpy_the_gondola_passes_and_fits(tmp_path, dims):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    parts = set(genome_mod.load_species("snack_gondola")["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name
        assert "." not in o.name, o.name


def test_bpy_two_submissions(tmp_path):
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, S.DC_SIZES[0])
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    assert len(doc["materials"]) == 2, [m["name"] for m in doc["materials"]]
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 2, [m["name"] for m in visual]
    painted = [m["name"] for m in doc["materials"] if "baseColorTexture" in m.get("pbrMetallicRoughness", {})
               and m["name"].startswith("M_Snack_snackbags_")]
    assert len(painted) == 1
    lit = [m["name"] for m in doc["materials"] if m.get("emissiveFactor") and any(m["emissiveFactor"])]
    assert lit == []


def test_bpy_the_same_file_every_build(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, S.DC_SIZES[1], variant=2)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]
