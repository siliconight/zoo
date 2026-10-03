"""1.17.0 -- the convenience store's hot dog roller grill.

The walker, 2026-09-28: "do the roller grill next", with photographs of two
store stations and a countertop merchandiser. Pure half
(`core/roller_grill_forms.py`): the module fills its slot exactly, no two
faces share a plane (with a control proving the check can see one), every
face wound outward, the rollers run across the width with the dogs lying
parallel in the grooves and clear of them, the grease darkens toward the
back, the columns and tags follow the width, the bun shelf the height, and
the names are invented. Built half (bpy): PASS and fit, four submissions,
nothing lit, determinism. 1.55.0: the rollers and the dogs turn about
their own axles, written into a second UV set in the engine's axes.
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


def test_bpy_six_submissions_nothing_lit_and_the_glass_is_clear(tmp_path):
    """Four until 1.55.0; the rollers and the dogs are two surfaces of their
    own now, because a part that turns on its own needs a surface of its own."""
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, R.DC_SIZES[0])
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    names = [m["name"] for m in doc["materials"]]
    assert len(names) == 6, names
    assert sorted(n for n in names if "_turn_" in n) == sorted(
        R.material_name(k) for k in ("metal_bare_turn", "metal_painted_turn")), names
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 6, [m["name"] for m in visual]
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


# --- 1.55.0: the rollers and the dogs turn ----------------------------------------------


def _accessor(doc, raw_bin, idx):
    """A glTF accessor's values, for a VEC2/VEC3 of floats in the GLB's binary chunk."""
    import struct
    acc = doc["accessors"][idx]
    bv = doc["bufferViews"][acc["bufferView"]]
    n = {"VEC2": 2, "VEC3": 3, "SCALAR": 1}[acc["type"]]
    off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = bv.get("byteStride", 4 * n)
    out = []
    for i in range(acc["count"]):
        out.append(struct.unpack_from("<%df" % n, raw_bin, off + i * stride))
    return out


def _glb_bin(path):
    import struct
    raw = open(path, "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    off = 20 + n
    m = struct.unpack("<I", raw[off:off + 4])[0]
    return raw[off + 8:off + 8 + m]


def test_the_rollers_and_the_dogs_turn_about_their_own_axles():
    """Every roller carries its axle as its pivot and so does every dog --
    the axis each prim was built on, not a guess from its bounds -- and
    nothing else on the grill turns."""
    for dims in (R.DC_SIZES[0], (0.7, 0.5, 1.3), (1.4, 0.8, 1.6)):
        got = R.plan(*dims)
        rs = R.rollers(dims[1], dims[2])
        turning = [p for p in got["prims"] if p.get("turn")]
        assert turning and all(p["part"] in ("Roller_Roller", "Roller_Dog") for p in turning)
        assert all(p.get("turn") for p in got["prims"] if p["part"] in ("Roller_Roller", "Roller_Dog"))
        rolls = [p for p in turning if p["part"] == "Roller_Roller"]
        assert sorted((round(p["turn"][1], 6), round(p["turn"][2], 6)) for p in rolls) == \
            sorted((round(y, 6), round(z, 6)) for y, z in rs)
        for p in turning:
            axis, py, pz = p["turn"]
            assert axis == "x"
            # the pivot is the prim's own axis: every vertex is one radius from it
            r = R.ROLLER_R if p["part"] == "Roller_Roller" else None
            ds = [math.hypot(v[1] - py, v[2] - pz) for v in p["verts"]]
            if r is None:
                r = ds[0]
            assert all(abs(d - r) < 1e-6 for d in ds), (p["part"], min(ds), max(ds), r)


def test_the_dogs_turn_the_other_way_at_the_rollers_surface_speed():
    rates = R.turn_rates()
    assert rates["metal_bare_turn"] == R.ROLLER_RPM * 6.0
    mean_r = sum(k[3] for k in R.KINDS) / len(R.KINDS)
    assert rates["metal_painted_turn"] == pytest.approx(-rates["metal_bare_turn"] * R.ROLLER_R / mean_r)
    assert rates["metal_painted_turn"] < 0 < rates["metal_bare_turn"]
    assert R.plan(*R.DC_SIZES[0])["facts"]["turn"] == rates


def test_a_turning_kind_s_material_name_carries_its_axis_and_rate():
    assert R.material_name("metal_bare") == "M_Roller_metal_bare"
    assert R.material_name("glass") == "M_Roller_glass"
    assert re.fullmatch(r"M_Roller_metal_bare_turn_x\d+", R.material_name("metal_bare_turn"))
    assert re.fullmatch(r"M_Roller_metal_painted_turn_xn\d+", R.material_name("metal_painted_turn"))
    assert R.material_name("metal_bare_turn").endswith("_x%d" % int(round(R.turn_rates()["metal_bare_turn"])))


def test_a_turning_kind_takes_its_base_kind_s_numbers_and_the_flat_path():
    """Read off the source: `bpylayer.materials` imports bpy at the top. A
    turning kind is its base kind less `_turn` for roughness and metallic,
    is kept off the skin library, and is NOT in the kind vocabulary -- no
    genome names it; the recipe derives it from the kind the genome named."""
    from zoo_keeper.core import skins
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "zoo_keeper", "bpylayer", "materials.py"), encoding="utf-8").read()
    assert 'TURN_SUFFIX = "_turn"' in src
    assert 'ROUGHNESS.get(base_kind(material_kind), 0.6)' in src
    assert 'METALLIC.get(base_kind(material_kind), 0.0)' in src
    assert 'pack = None if material_kind.endswith(TURN_SUFFIX) else _find_pack(material_kind)' in src
    assert "metal_bare_turn" not in skins.KNOWN_KINDS and "metal_painted_turn" not in skins.KNOWN_KINDS
    assert R.vertex_tint("roller_0.700")[0] == "metal_bare_turn"
    assert R.vertex_tint("dog_jumbo")[0] == "metal_painted_turn"
    assert R.KIND_BASE["metal_bare_turn"] == R.KIND_BASE["metal_bare"]


def test_turning_is_set_on_the_final_prim_so_a_move_cannot_leave_the_pivot_behind():
    p = P.turning(P.translate(P.cyl("A", "m", (0.0, 0.0), 0.01, 0.0, 0.1), (0.0, 0.2, 0.3)), "x", (0.2, 0.3))
    assert p["turn"] == ("x", 0.2, 0.3)
    with pytest.raises(ValueError):
        P.turning(p, "y", (0.0, 0.0))


def test_bpy_the_turning_prims_carry_their_axles_in_the_engine_s_axes(tmp_path):
    """TEXCOORD_1 on the roller and dog primitives, and on nothing else of
    the grill, AND IT AGREES WITH THE VERTICES AS SHIPPED: every corner of a
    roller is exactly one roller radius from the axle it carries, in the
    engine's (y, z), after the module was re-centred and whatever else moved
    a vertex; every dog corner one of the kinds' radii from its own. The
    first build compared the pivots with the forms' numbers and passed
    while the shipped part turned 0.7 m off its axle: the vertices had been
    re-centred and the pivots had not. The vertices are the truth here."""
    pytest.importorskip("bpy")
    res, _objs = _build(tmp_path, R.DC_SIZES[0])
    path = os.path.join(str(tmp_path), res["files"]["glb"])
    doc = _glb_json(path)
    raw = _glb_bin(path)
    radii = {round(k[3], 6) for k in R.KINDS}
    seen = {}
    for mesh in doc["meshes"]:
        for prim in mesh["primitives"]:
            if "material" not in prim:
                continue
            name = doc["materials"][prim["material"]]["name"]
            has = "TEXCOORD_1" in prim["attributes"]
            seen[name] = has
            if not has:
                continue
            pos = _accessor(doc, raw, prim["attributes"]["POSITION"])
            uv2 = _accessor(doc, raw, prim["attributes"]["TEXCOORD_1"])
            pivots = sorted({(round(a, 4), round(b, 4)) for a, b in uv2})
            ds = [math.hypot(v[1] - u[0], v[2] - u[1]) for v, u in zip(pos, uv2)]
            if "metal_bare_turn" in name:
                assert len(pivots) == R.plan(*R.DC_SIZES[0])["facts"]["rollers"], pivots
                assert all(abs(d - R.ROLLER_R) < 2e-4 for d in ds), (min(ds), max(ds))
            else:
                assert all(any(abs(d - r) < 2e-4 for r in radii) for d in ds), (min(ds), max(ds))
    assert [n for n, h in seen.items() if h] and all(("_turn_" in n) == h for n, h in seen.items()), seen
