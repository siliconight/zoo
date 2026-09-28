"""1.9.0 -- the convenience store's coffee island.

The walker, 2026-09-28: "do the coffee counter next", from the store
references (docs/SET_DRESSING_REFERENCES.md, 2026-09-15): brewers with
carafes on warmers, orange and black lids, cup towers, syrups, a round
coffee sign.

Pure half (`core/coffee_island_forms.py`): the island fits its slot exactly,
the dressing stands on it and inside its footprint, no two faces share a
plane, faces wound outward, the stations clear the sign post, the budget,
the tints, the sign's art. Built half (bpy, skipped without it): PASS and
fit, five submissions over five materials, glass see-through, the sign
painted and the only textured part, determinism.
"""
from __future__ import annotations

import itertools
import os

import pytest

from zoo_keeper.core import coffee_island_forms as C
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import prims as P


def _corners():
    return [tuple(c) for c in itertools.product(*(C.RANGES[a] for a in ("width", "depth", "height")))]


CASES = list(C.DC_SIZES) + _corners()


@pytest.mark.parametrize("dims", CASES)
def test_the_island_fits_its_slot_and_shares_no_plane(dims):
    w, d, h = dims
    g = C.plan(w, d, h, "coffee_island", 1)
    lo, hi = P.bounds(g["island"])
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-9, (dims, lo, hi)
    lo2, hi2 = P.bounds(g["dressing"])
    # the dressing stands on the top and inside the footprint
    assert lo2[2] >= h - 0.012 and lo2[0] > -w / 2 and hi2[0] < w / 2
    assert lo2[1] > -d / 2 and hi2[1] < d / 2
    everything = g["island"] + g["dressing"]
    assert P.coincident_pairs(everything, tol=0.0022) == []
    for p in everything:
        assert C.signed_volume(p) > 0, (p["part"], p["mat"])
    assert P.tri_count(everything) <= genome_mod.load_species("coffee_island")["budgets"]["tris_lod0"]


@pytest.mark.parametrize("dims", CASES)
def test_there_is_always_coffee_and_the_post_is_clear(dims):
    w, d, h = dims
    f = C.plan(w, d, h)["facts"]
    assert len(f["stations"]) >= 2 and len(f["stations"]) <= C.MAX_STATIONS
    # ONE CARAFE A BREWER (the walker, 2026-09-28: "we can have 20% as many
    # carafes"): the one brewing, in the bay; every other warmer is empty
    assert f["carafes"] == 2 * len(f["stations"])
    assert f["decaf"] == 2 * (len(f["stations"]) // 2)
    for x in f["stations"]:
        assert abs(x) - C.BREWER_W / 2.0 - C.HANDLE_OVER >= C.SIGN_CLEAR - 1e-9, x
    # the front burner row exists exactly when the island is deep enough
    assert f["front_row"] == (d / 2.0 >= C.FRONT_ROW_MIN_HALF)


def test_a_fifth_of_the_warmers_carry_a_carafe_on_deli_counters_islands():
    for dims in C.DC_SIZES:
        f = C.plan(*dims)["facts"]
        assert f["carafes"] / C.warmers(len(f["stations"]), f["front_row"]) == pytest.approx(0.2)


def test_both_faces_are_served_and_the_decaf_is_mixed():
    g = C.plan(*C.DC_SIZES[0], "coffee_island", 2)
    carafes = [p for p in g["dressing"] if p["part"] == "Coffee_Carafe" and p["mat"] == "glass"]
    ys = [sum(v[1] for v in p["verts"]) / len(p["verts"]) for p in carafes]
    assert any(y > 0 for y in ys) and any(y < 0 for y in ys)
    f = g["facts"]
    assert 0 < f["decaf"] < f["carafes"]
    lids = {p["mat"] for p in g["dressing"] if p["mat"].startswith("lid_")}
    assert lids == {"lid_reg", "lid_decaf"}


def test_four_kinds_and_every_colour_survives_the_tint():
    kinds = set()
    for mk, (rgb, kind) in C.MATERIALS.items():
        k2, factor = C.vertex_tint(mk)
        assert k2 == kind
        assert tuple(b * f for b, f in zip(C.KIND_BASE[kind], factor)) == pytest.approx(tuple(rgb)), mk
        assert all(0.0 <= f <= 1.0 for f in factor), (mk, factor)
        kinds.add(kind)
    assert kinds == {"wood_stained", "metal_bare", "plastic", "glass"}
    used = {p["mat"] for p in C.plan(*C.DC_SIZES[1])["dressing"]} | {p["mat"] for p in C.plan(*C.DC_SIZES[1])["island"]}
    assert used - {"sign"} <= set(C.MATERIALS), used - set(C.MATERIALS)


def test_the_sign_reads_from_both_sides():
    sp = next(p for p in C.plan(*C.DC_SIZES[0])["dressing"] if p["part"] == "Coffee_Sign")
    front, back = sp["uvs"][0], sp["uvs"][1]
    fverts = [sp["verts"][i] for i in sp["faces"][0]]
    bverts = [sp["verts"][i] for i in sp["faces"][1]]
    # the front cap faces -Y, the back +Y
    assert all(v[1] < 0 for v in fverts) and all(v[1] > 0 for v in bverts)
    # seen from -Y, +x reads rightward (u grows with x); from +Y it is mirrored
    fx = sorted(zip((v[0] for v in fverts), (c[1] for c in front)))
    bx = sorted(zip((v[0] for v in bverts), (c[1] for c in back)))
    assert fx[0][1] < fx[-1][1] and bx[0][1] > bx[-1][1]
    assert all(c == ("dark",) for f in sp["uvs"][2:] for c in f)


def test_the_sign_art_is_the_same_bytes_and_says_the_store():
    a, b = C.sign_art(1), C.sign_art(1)
    assert bytes(a["canvas"].buf) == bytes(b["canvas"].buf) and a["name"] == b["name"]
    assert a["said"] == [C.STORE, "COFFEE", "FRESH BREWED", C.BADGE]
    assert len({C.sign_art(v)["name"] for v in range(4)}) == 4
    # the disc is the colourway, the corners are not painted
    S = C.SIGN_PX
    c = a["canvas"]
    disc = C.COLOURWAYS[1][0]
    assert c.get(S // 2, S // 2 + 70) == disc or c.get(S // 2 - 60, S // 2) == disc
    assert c.get(0, 0) == (12, 12, 12)


def test_every_brewer_reads_the_right_way_from_its_own_side():
    """The +Y brewer is the -Y one turned half round: its column is on the
    viewer's right from either side, and its badge faces its own side."""
    g = C.plan(*C.DC_SIZES[0])
    cols = [p for p in g["dressing"] if p["part"] == "Coffee_Brewer" and p["mat"] == "grain"]
    xs = C.plan(*C.DC_SIZES[0])["facts"]["stations"]
    for p in cols:
        cx = sum(v[0] for v in p["verts"]) / len(p["verts"])
        cy = sum(v[1] for v in p["verts"]) / len(p["verts"])
        xc = min(xs, key=lambda s: abs(s - cx))
        # facing -Y (cy < 0) the viewer's right is +x; facing +Y it is -x
        assert (cx - xc) * (-1 if cy < 0 else 1) < 0, (cx, cy, xc)
    badges = [p for p in g["dressing"] if p["part"] == "Coffee_Badge"]
    assert len(badges) == 2 * len(xs)
    for b in badges:
        k = next(i for i, f in enumerate(b["uvs"]) if f[0][0] == "badge")
        n_y = sum(b["verts"][i][1] for i in b["faces"][k]) / 4.0 - sum(v[1] for v in b["verts"]) / 8.0
        cy = sum(v[1] for v in b["verts"]) / 8.0
        assert n_y * cy > 0, "a badge's painted face must face away from the spine"


def test_the_genome_names_the_parts_and_validates():
    g = genome_mod.load_species("coffee_island")
    assert genome_mod.validate_genome(g) == []
    r = g["dimensions"]
    assert (r["width"]["min"], r["width"]["max"]) == C.RANGES["width"]
    assert (r["depth"]["min"], r["depth"]["max"]) == C.RANGES["depth"]
    parts = set(g["parts"])
    got = {p["part"] for p in C.plan(*C.DC_SIZES[0])["island"] + C.plan(*C.DC_SIZES[0])["dressing"]}
    assert got <= parts, got - parts


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "coffee_island", "role": "prop", "size_mod": "full", "style": 1,
            "species": "coffee_island", "material": "metal",
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
def test_bpy_the_island_passes_and_fits(tmp_path, dims):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    parts = set(genome_mod.load_species("coffee_island")["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name
        assert "." not in o.name, o.name


def test_bpy_five_submissions_five_materials(tmp_path):
    """The design, held: wood, bare steel, plastic, glass, the sign."""
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, C.DC_SIZES[1])
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    names = [m["name"] for m in doc["materials"]]
    assert len(names) == 5, names
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 5, [m["name"] for m in visual]
    glass = [m for m in doc["materials"] if "glass" in m["name"]]
    assert len(glass) == 1 and glass[0].get("alphaMode") == "BLEND", glass
    lit = [m["name"] for m in doc["materials"] if m.get("emissiveFactor") and any(m["emissiveFactor"])]
    assert lit == [], lit
    painted = [m["name"] for m in doc["materials"] if "baseColorTexture" in m.get("pbrMetallicRoughness", {})
               and m["name"].startswith("M_Coffee_Sign_")]
    assert len(painted) == 1


def test_bpy_the_same_file_every_build(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, C.DC_SIZES[0], variant=2)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]
