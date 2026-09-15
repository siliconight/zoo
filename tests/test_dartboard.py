"""0.91.0 -- the bar dartboard: a wall cabinet, a bristle board, and a game
kept in chalk inside the doors.

The walker, 2026-09-15: "we also need dart boards in the strip clubs. The
kind where you use chalk to keep your score", with two photos -- the cabinet
open, and a chalked door close up.

The decisions are pure (`core/dartboard_forms.py`, `core/dartboard_art.py`)
and tested here without Blender: the slot filled exactly at every corner of
each form's range and at Deli Counter's sizes, the bull at the slot's centre
height, no coincident faces, faces wound outward, the triangle budget, the
board painted at regulation radii in the regulation order, the chalk stages,
the invented brands. The built module -- fit, collision, the painted
materials in the file, determinism, the coplanar probe -- is the bpy half at
the bottom, skipped without `bpy`.
"""
from __future__ import annotations

import itertools
import json
import os
import re
import struct
import zlib

import pytest

from zoo_keeper.core import dartboard_art as A
from zoo_keeper.core import dartboard_forms as F
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import kit
from zoo_keeper.core import prims as P

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _corners(form):
    R = F.FORM_RANGES[form]
    return [tuple(c) for c in itertools.product(*(R[a] for a in ("width", "depth", "height")))]


CASES = ([(d, "open", v) for d in F.DC_SIZES for v in range(4)]
         + [(c, "open", 0) for c in _corners("open")]
         + [(c, "closed", v) for c in _corners("closed") for v in (0, 3)])


# --- the plan -----------------------------------------------------------------------


@pytest.mark.parametrize("dims,form,variant", CASES)
def test_the_cabinet_fills_its_slot_with_the_bull_at_its_centre_height(dims, form, variant):
    w, d, h = dims
    got = F.plan(w, d, h, form, variant)
    lo, hi = P.bounds(got["prims"])
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-6, (dims, lo, hi)
    # the planner filled the slot itself: fit_exact took under half a percent
    assert all(abs(s - 1.0) < 0.005 for s in got["scale"]), got["scale"]
    bx, by, bz = got["bull"]
    assert abs(bx) < 1e-6 and abs(bz - h / 2) < 1e-6, got["bull"]
    # the board faces the room from inside the cabinet: behind the front
    assert -d / 2 < by < d / 2
    if form == "open":
        assert F.OPEN_MIN <= got["angle_deg"] <= F.OPEN_MAX
    else:
        assert got["angle_deg"] == 0.0


@pytest.mark.parametrize("dims,form,variant", CASES)
def test_no_two_faces_share_a_plane_and_every_prim_is_wound_outward(dims, form, variant):
    got = F.plan(*dims, form=form, variant=variant)
    assert P.coincident_pairs(got["prims"], tol=0.0022) == []   # 0.2 mm past the probe's window: a 2.0 mm gap passes here by float and fails in Blender
    for p in got["prims"]:
        assert F.signed_volume(p) > 0, p["part"]
    assert P.tri_count(got["prims"]) <= genome_mod.load_species("dartboard")["budgets"]["tris_lod0"]


@pytest.mark.parametrize("dims", F.DC_SIZES)
def test_collision_is_the_cabinet_box_and_not_the_doors(dims):
    """The slot is the open footprint; a body is stopped by the cabinet on
    the wall, not by a door in mid-air."""
    w, d, h = dims
    got = F.plan(w, d, h, "open", 0)
    (c0, c1), = got["collision"]
    cw, cd, ch = (c1[k] - c0[k] for k in range(3))
    assert c1[1] == pytest.approx(d / 2)                      # against the wall
    assert F.CAB_W[0] <= cw <= F.CAB_W[1] + 0.02 and cw < 0.7 * w
    assert F.CAB_D[0] <= cd <= F.CAB_D[1] + 0.01 and cd < 0.5 * d
    assert c0[2] > 0.0 and c1[2] < h and (c0[2] + c1[2]) / 2 == pytest.approx(h / 2)
    doors = [p for p in got["prims"] if p["part"] == "Dartboard_Door"]
    assert len(doors) == 2
    for p in doors:
        xs = [v[0] for v in p["verts"]]
        # the door's free edge swings outside the collision box
        assert min(xs) < c0[0] - 0.1 or max(xs) > c1[0] + 0.1


def test_the_forms_and_the_variants_differ_where_they_should():
    w, d, h = F.DC_SIZES[0]
    closed = F.plan(0.7, 0.16, 0.9, "closed", 0)
    assert not [p for p in closed["prims"] if p["part"] == "Dartboard_Rail"]
    assert F.pick_form("auto", 1.1) == "open" and F.pick_form("auto", 0.7) == "closed"
    rails = []
    for v in range(4):
        got = F.plan(w, d, h, "open", v)
        darts_on_rails = sum(got["facts"]["rails"])
        assert darts_on_rails + got["facts"]["stuck"] == 6
        rails.append(tuple(got["facts"]["rails"]))
    assert len(set(rails)) >= 3
    assert {F.CABINET[v][0] for v in range(4)} == {"wood_stained", "metal_painted"}


def test_the_genome_is_the_union_of_the_forms_and_the_kit_honours_its_fields():
    g = genome_mod.load_species("dartboard")
    assert genome_mod.validate_genome(g) == []
    assert g["module_variants"] == 4
    for axis in ("width", "depth", "height"):
        lo = min(F.FORM_RANGES[f][axis][0] for f in F.FORMS)
        hi = max(F.FORM_RANGES[f][axis][1] for f in F.FORMS)
        assert (g["dimensions"][axis]["min"], g["dimensions"][axis]["max"]) == (lo, hi), axis
    for form in ("open", "closed"):
        for v in range(4):
            dress, why = kit.honour_dressing({"form": form, "variant": v}, "dartboard")
            assert not why and dress["form"] == form, why
    _d, why = kit.honour_dressing({"variant": 4}, "dartboard")
    assert why
    # Deli Counter writes `wood_stained`, the species' own: no `_m` in the stem
    assert kit.material_tag("wood_stained", "dartboard", "delco_1997") is None


# --- the board ---------------------------------------------------------------------


def test_the_board_is_painted_at_regulation_radii_in_the_regulation_order():
    c, f = A.paint_board(A.IDS[0], 0, "k")
    assert (c.w, c.h) == (A.BOARD_PX, A.BOARD_PX)
    mm = A.BOARD_D * 1000.0 / A.BOARD_PX
    half = A.BOARD_PX / 2.0

    def at(r_mm, deg):
        import math
        a = math.radians(deg)
        x = int(half + (r_mm / mm) * math.sin(a))
        y = int(half - (r_mm / mm) * math.cos(a))
        return c.get(x, y)

    def red(p):
        return p[0] > 120 and p[1] < 80 and p[2] < 80

    def green(p):
        return p[1] > 80 and p[0] < 70 and p[2] < 100

    assert A.SECTORS[:3] == (20, 1, 18) and sorted(A.SECTORS) == list(range(1, 21))
    assert A.region_at(0.0, 103.0) == ("treble", 20)
    assert A.region_at(0.0, -166.0) == ("double", 3)
    assert A.region_at(0.0, 3.0) == ("bull", None)
    assert red(at(3.0, 0))                          # the bull
    assert green(at(11.0, 45))                      # the outer bull
    assert red(at(103.0, 2))                        # treble 20: a black sector
    assert green(at(103.0, 18))                     # treble 1: a cream sector
    assert red(at(166.0, 2)) and green(at(166.0, 18))
    s20, s1 = at(60.0, 3), at(60.0, 18)
    assert sum(s20) < 200 < sum(s1)                 # 20 black, 1 cream
    assert len(f["numbers"]) == 20


@pytest.mark.parametrize("v", range(4))
def test_the_board_is_the_same_bytes_every_time_and_wears_with_the_variant(v):
    a, fa = A.paint_board(A.IDS[v], v, "k")
    b, fb = A.paint_board(A.IDS[v], v, "k")
    assert a.png() == b.png() and fa["name"] == fb["name"]
    assert fa["name"].endswith("%08x" % (zlib.crc32(bytes(a.buf)) & 0xFFFFFFFF))
    if v:
        _c0, f0 = A.paint_board(A.IDS[v], 0, "k")
        assert fa["pocks"] > f0["pocks"]


# --- the chalk ----------------------------------------------------------------------


def test_the_four_variants_are_four_stages_of_one_game():
    arts = [A.chalk_art(0.28, 0.35, A.IDS[0], v, "k") for v in range(4)]
    stages = [a["facts"]["L"]["stage"] for a in arts]
    assert stages == [s["id"] for s in A.CHALK_STAGES]
    marks = [sum(a["facts"][door]["marks"].values()) for a in arts for door in ("L",)]
    assert marks[0] == 0 and marks[3] > marks[1]
    assert "x2" not in arts[0]["facts"]["L"]["written"] and "x2" in arts[3]["facts"]["L"]["written"]
    # the two doors of one board keep different games
    assert arts[3]["facts"]["L"]["marks"] != arts[3]["facts"]["R"]["marks"]
    # a mark is 0 to 3, three closing the number
    assert all(0 <= n <= 3 for a in arts for d in "LR" for n in a["facts"][d]["marks"].values())
    for a in arts:
        assert a["canvas"].png() == A.chalk_art(0.28, 0.35, A.IDS[0], a["variant"], "k")["canvas"].png()


def test_the_grid_is_painted_and_the_chalk_is_grainy():
    a = A.chalk_art(0.28, 0.35, A.IDS[1], 3, "k")
    c = a["canvas"]
    L = a["facts"]["L"]["layout"]
    x0, y0, x1, y1 = a["rects"]["L"]
    # the painted frame is one solid colour
    assert {c.get(x, y0) for x in range(x0, x1)} == {A.PAINT}
    assert a["facts"]["L"]["heads"] in (("HOME", "AWAY"), ("01", "01"))
    assert a["facts"]["L"]["painted"][-7:] == ["20", "19", "18", "17", "16", "15", "BULL"]
    # chalk: inside the player columns there are pale pixels and slate pixels
    # side by side -- broken, not solid
    xs = L["xs"]
    col = [c.get(x, y) for y in range(L["top"], y1 - L["frame"]) for x in range(xs[0] + 2, xs[1] - 2)]
    pale = sum(1 for p in col if min(p) > 120)
    assert 0 < pale < 0.5 * len(col)


# --- the invented brands -----------------------------------------------------------------


def test_no_brand_is_a_real_dart_mark_and_every_string_is_spellable():
    from zoo_keeper.core import pixel_type_glyphs as G
    assert len(A.BRANDS) == len(A.BY_ID) >= 4
    for b in A.BRANDS:
        for text in A.painted_strings(b["id"]):
            up = text.upper()
            assert not [bad for bad in A.DENYLIST if bad in up], (text, [bad for bad in A.DENYLIST if bad in up])
            assert all(ch in G.GLYPHS for ch in text), text
    # the guard is live: it catches the obvious one
    assert any(bad in "WINMAU BLADE 5" for bad in A.DENYLIST)


def test_a_module_picks_its_brand_by_stem_without_the_variant_and_by_its_variant():
    picks = [A.pick({"params": {}, "module": {"stem": "prop_dartboard_x" + ("_n%d" % v if v else ""),
                                              "variant": v}})[0] for v in range(4)]
    assert picks == A.brand_order("prop_dartboard_x")[:4] and len(set(picks)) == 4
    assert A.pick({"params": {"brand": "pike_pro"}, "module": {"stem": "s"}})[0] == "pike_pro"


# --- the built module (bpy) --------------------------------------------------------------


def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    slot = {"slot_id": "db", "role": "prop", "size_mod": "full", "style": 1,
            "species": "dartboard", "material": "wood_stained",
            "fit": {"dims": list(dims), "pivot": "center"}}
    slot.update(fields)
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    objs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"
                   and not o.name.endswith(_COL_SUFFIXES)), key=lambda o: o.name)
    cols = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.endswith(_COL_SUFFIXES)]
    return res, objs, cols


def _glb_json(path):
    raw = open(path, "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    return json.loads(raw[20:20 + n])


def _probe(objs):
    import bpy
    import mathutils
    src = open(os.path.join(_ZOO, "tools", "coplanar_probe.py"), encoding="utf-8").read()
    ns = {"__name__": "coplanar_probe_lib"}
    exec(compile(src, "coplanar_probe.py", "exec"), ns)
    rows, _n = ns["probe"](bpy, mathutils, objs, 0.002, 1e-6, 1e-3)
    return rows


BPY_CASES = [(F.DC_SIZES[0], {}), (F.DC_SIZES[1], {"variant": 3}),
             ((1.0, 0.3, 0.8), {"form": "open"}), ((1.35, 0.42, 1.0), {"form": "open", "variant": 2}),
             ((0.7, 0.16, 0.9), {"form": "closed"}), ((0.8, 0.19, 1.0), {"form": "closed", "variant": 1})]


@pytest.mark.parametrize("dims,fields", BPY_CASES)
def test_bpy_the_module_passes_fits_and_shares_no_plane(tmp_path, dims, fields):
    pytest.importorskip("bpy")
    res, objs, cols = _build(tmp_path, dims, **fields)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    assert _probe(objs) == []
    parts = set(genome_mod.load_species("dartboard")["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name
    assert cols, "no collision proxy"


@pytest.mark.parametrize("dims", F.DC_SIZES)
def test_bpy_the_collider_is_the_cabinet_and_the_bull_is_at_the_centre(tmp_path, dims):
    pytest.importorskip("bpy")
    res, objs, cols = _build(tmp_path, dims)
    w, d, h = dims
    pts = [c.matrix_world @ v.co for c in cols for v in c.data.vertices]
    xs, ys, zs = [p.x for p in pts], [p.y for p in pts], [p.z for p in pts]
    assert max(xs) - min(xs) < 0.7 * w and max(ys) - min(ys) < 0.5 * d
    assert max(ys) == pytest.approx(d / 2, abs=1e-4)
    assert (max(zs) + min(zs)) / 2 == pytest.approx(0.0, abs=1e-4)
    import bpy
    bull = [o for o in bpy.context.scene.objects if o.name == "ATT_bull"]
    assert bull and abs(bull[0].location.z) < 1e-4 and abs(bull[0].location.x) < 1e-4


def test_bpy_the_board_and_the_chalk_are_painted_and_nothing_glows(tmp_path):
    pytest.importorskip("bpy")
    res, objs, _cols = _build(tmp_path, F.DC_SIZES[0], variant=2)
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    images = [i["name"] for i in doc["images"]]
    assert [n for n in images if n.startswith("dartboard_macdade") or n.startswith("dartboard_")]
    assert [n for n in images if n.startswith("chalk_")]
    painted = [m for m in doc["materials"] if m["name"].startswith(("M_Dartboard_Board_", "M_Dartboard_Chalk_"))]
    assert len(painted) == 2
    for m in painted:
        assert "baseColorTexture" in m.get("pbrMetallicRoughness", {})
    for m in doc["materials"]:
        assert not any(m.get("emissiveFactor", [0])) and "emissiveTexture" not in m, m["name"]
    by = {o.name: o for o in objs}
    for name in ("Dartboard_Board", "Dartboard_Chalkboard"):
        ca = by[name].data.color_attributes.get("Wear")
        assert ca is not None and min(min(c.color[:3]) for c in ca.data) >= 0.999


def test_bpy_the_same_file_every_build_and_four_variants_four_boards(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o, _c = _build(out, F.DC_SIZES[0], variant=1)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]
    arts = set()
    for v in range(4):
        out = tmp_path / ("v%d" % v)
        res, _o, _c = _build(out, F.DC_SIZES[0], variant=v)
        doc = _glb_json(os.path.join(str(out), res["files"]["glb"]))
        names = sorted(i["name"] for i in doc["images"] if re.match(r"(dartboard|chalk)_", i["name"]))
        assert len(names) == 2
        arts.add(tuple(names))
    assert len(arts) == 4
