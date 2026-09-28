"""1.12.0 -- the convenience store's reach-in cooler wall, glowing.

The walker, 2026-09-28: "do the cooler wall next", then "we also want
glowing fridge lights". Pure half (`core/cooler_run_forms.py`): the module
fills its slot exactly (the handles end at its front), no two faces share a
plane, every face is wound outward, the doors follow the run, every glowing
face maps into the glow image, and the art is deterministic. Built half
(bpy, skipped without it): PASS and fit, three submissions over three
materials, the glow the only lit material and the glass blended.
"""
from __future__ import annotations

import itertools
import os

import pytest

from zoo_keeper.core import cooler_run_forms as C
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import prims as P

CASES = list(C.DC_SIZES) + [tuple(c) for c in itertools.product(*(C.RANGES[a] for a in ("width", "depth", "height")))]


@pytest.mark.parametrize("dims", CASES)
def test_the_cooler_fills_its_slot_and_shares_no_plane(dims):
    w, d, h = dims
    pr = C.plan(w, d, h, "cooler_run", 1)["prims"]
    lo, hi = P.bounds(pr)
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-6, (dims, lo, hi)
    assert P.coincident_pairs(pr, tol=0.0022) == []
    for p in pr:
        assert C.signed_volume(p) > 0, (p["part"], p["mat"])
    assert P.tri_count(pr) <= genome_mod.load_species("cooler_run")["budgets"]["tris_lod0"]


@pytest.mark.parametrize("dims", CASES)
def test_the_doors_follow_the_run_and_the_walk_in_is_behind(dims):
    w, d, h = dims
    g = C.plan(w, d, h)
    f = g["facts"]
    n, dw = C.doors(w)
    assert f["doors"] == n >= 1 and 0.55 <= dw <= 1.0, (n, dw)
    assert len([p for p in g["prims"] if p["mat"] == "glass"]) == n
    assert sum(s[1] for s in f["sections"]) == n
    bodies = [p for p in g["prims"] if p["part"] == "Cooler_Body"]
    assert bool(bodies) == (d > C.CAB_D + 1e-6)


def test_only_the_glow_is_lit_and_every_glowing_face_maps_into_the_image():
    g = C.plan(*C.DC_SIZES[0])
    f = g["facts"]
    art = C.glow_art(f["door_width"] - 0.024, C.DC_SIZES[0][2] - C.HEADER_H - C.KICK_H - 0.04)
    glow = [p for p in g["prims"] if p["mat"] == "glow"]
    # a panel a door, a tube a door plus one, a section a pair of doors
    n = f["doors"]
    assert len(glow) == n + (n + 1) + len(f["sections"])
    for p in glow:
        assert len(p["uvs"]) == len(p["faces"])
        for corners in p["uvs"]:
            for c in corners:
                assert c[0] == "dark" or c[0] in art["rects"], c[0]
    assert {"tube", "dark"} <= set(art["rects"])
    # the tube block is white: the brightest thing on the image
    x0, y0, _x1, _y1 = art["rects"]["tube"]
    assert art["canvas"].get(x0 + 1, y0 + 1) == (255, 255, 250)
    assert set(C.MATERIALS) >= {p["mat"] for p in g["prims"]} - {"glow"}


def test_the_glow_art_is_the_same_bytes_and_says_the_sections():
    a, b = C.glow_art(0.72, 1.74), C.glow_art(0.72, 1.74)
    assert bytes(a["canvas"].buf) == bytes(b["canvas"].buf) and a["name"] == b["name"]
    for word in C.SECTION_WORDS:
        assert word in a["said"]
    for dt in C.DOOR_TYPES:
        x0, y0, x1, y1 = a["rects"]["door_" + dt]
        px = {a["canvas"].get(x, y) for x in range(x0, x1, 7) for y in range(y0, y1, 7)}
        assert len(px) >= 5, dt          # product, not a flat panel (milk is six colours)


def test_the_genome_names_the_parts_and_validates():
    g = genome_mod.load_species("cooler_run")
    assert genome_mod.validate_genome(g) == []
    r = g["dimensions"]
    assert (r["width"]["min"], r["width"]["max"]) == C.RANGES["width"]
    parts = set(g["parts"])
    assert {p["part"] for p in C.plan(*C.DC_SIZES[0])["prims"]} <= parts


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "cooler_run", "role": "prop", "size_mod": "full", "style": 1,
            "species": "cooler_run", "material": "glass",
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


@pytest.mark.parametrize("dims", C.DC_SIZES)
def test_bpy_the_cooler_passes_and_fits(tmp_path, dims):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    parts = set(genome_mod.load_species("cooler_run")["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name
        assert "." not in o.name, o.name


def test_bpy_three_submissions_and_the_glow_is_the_lit_one(tmp_path):
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, C.DC_SIZES[0])
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    names = [m["name"] for m in doc["materials"]]
    assert len(names) == 3, names
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 3, [m["name"] for m in visual]
    lit = [m["name"] for m in doc["materials"] if (m.get("emissiveFactor") and any(m["emissiveFactor"]))
           or "emissiveTexture" in m]
    assert len(lit) == 1 and lit[0].startswith("M_Cooler_") and lit[0].endswith("_Face"), lit
    glass = [m for m in doc["materials"] if "glass" in m["name"]]
    assert len(glass) == 1 and glass[0].get("alphaMode") == "BLEND", glass


def test_bpy_the_same_file_every_build(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, C.DC_SIZES[1], variant=2)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]
