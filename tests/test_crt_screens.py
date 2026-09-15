"""0.90.0 -- the bar TV is on, showing a ballgame; the stand set fits its slot.

The walker, after cold run 9057's strip club: "I also want the CRTs in the
Strip club to have a light/glow from the screen as if they are on...but we
dont have to have a clear image on them...it would be a football or baseball
game tho". 0.88.0 - 0.89.0 lit the bracket set's glass a flat (0.10, 0.17,
0.26) x 0.35, which read as off.

The decisions are pure (`core/crt_screens.py`, `core/crt_forms.py`) and are
tested here without Blender: the picture's bytes, its softness, the sport per
variant, the invented score bugs, the curved face and the stand set's exact
layout. The built module -- fit, glow in the file, COLOR_0, determinism,
coplanar faces -- is the bpy half at the bottom, skipped without `bpy`.
"""
from __future__ import annotations

import itertools
import json
import os
import re
import struct
import zlib

import pytest

from zoo_keeper.core import crt_forms as K
from zoo_keeper.core import crt_screens as CS
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import kit
from zoo_keeper.core import prims as P

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Deli Counter's `wall_tv` sizes (level_design._PIECES), then the genome's
#: corners.
DC_SIZES = ((0.6, 0.55, 0.5), (0.7, 0.6, 0.55))


def _corners():
    dims = genome_mod.load_species("crt_tv")["dimensions"]
    axes = [(dims[a]["min"], dims[a]["max"]) for a in ("width", "depth", "height")]
    out = [tuple(dims[a]["default"] for a in ("width", "depth", "height"))]
    out += [tuple(c) for c in itertools.product(*axes)]
    return out


CORNERS = list(DC_SIZES) + _corners()

#: WHAT A SCORE BUG MUST NEVER SAY. Real teams' abbreviations in the leagues
#: a 1997 Delaware County bar shows (NFL, MLB, NBA, NHL), the Philadelphia
#: teams by name and nickname, the local colleges, leagues and conferences,
#: and the networks and stations that carried the games. Whole tokens.
DENY = set("""
ARI ATL BAL BUF CAR CHI CIN CLE DAL DEN DET GB HOU IND JAX JAC KC LA LAC LAR LV
MIA MIN NE NO NYG NYJ OAK PHI PHL PIT SD SEA SF STL TB TEN WAS WSH
ANA AZ BOS CHC CWS CHW COL FLA KCR LAD MIL MON MTL NYM NYY SDP SFG TEX TOR
BKN BRK CHA GSW LAL MEM NOP NJ NJN NJD OKC ORL PHX POR SAC SAS UTA VAN WPG
EDM CGY QUE HFD FLA NYI NYR CBJ NSH
EAGLES EAGS IGGLES BIRDS PHILLIES PHILS SIXERS 76ERS FLYERS UNION
PSU PENN TEMPLE TEMP NOVA VILLANOVA SJU HAWKS LAS LASALLE DREXEL WIDENER SWAT HAV
NFL MLB NBA NHL NCAA AFC NFC AL NL ABC CBS NBC FOX ESPN ESPN2 TNT TBS WGN
PRISM SPECTRUM KYW WCAU WPVI WTXF WPHL WIP UPN WB MNF SNF
""".split())
#: Substrings no abbreviation may carry, even inside an invented word.
DENY_PARTS = ("EAGL", "IGGL", "PHIL", "SIXER", "FLYER", "ESPN", "NFL", "MLB")


# --- the picture -----------------------------------------------------------------


@pytest.mark.parametrize("gid", [g[0] for g in CS.GAMES])
def test_the_picture_is_the_same_bytes_every_time_and_a_real_png(gid):
    a, fa = CS.paint(gid)
    b, fb = CS.paint(gid)
    assert bytes(a.buf) == bytes(b.buf) and a.png() == b.png()
    png = a.png()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", png[16:24]) == (CS.W, CS.H)
    assert (CS.W * 3) == (CS.H * 4)                      # 4:3
    assert fa["name"] == fb["name"]
    assert fa["name"].endswith("%08x" % (zlib.crc32(bytes(a.buf)) & 0xFFFFFFFF))


def _luma(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


@pytest.mark.parametrize("gid", [g[0] for g in CS.GAMES])
def test_the_picture_is_soft_scanlined_and_dark_at_the_corners(gid):
    """NOT a clear image. Measured on 0.90.0: no two horizontal neighbours
    differ by more than 96 codes in any channel (white type on the bug's navy
    is 224 crisp); odd rows 0.80 of even rows; the corner 0.47-0.63 of the
    centre."""
    c, _f = CS.paint(gid)
    W, H = c.w, c.h
    worst = max(max(abs(c.get(x, y)[k] - c.get(x + 1, y)[k]) for k in range(3))
                for y in range(0, H, 2) for x in range(W - 1))
    assert worst < 128, worst
    even = sum(_luma(c.get(x, y)) for y in range(0, H, 2) for x in range(W))
    odd = sum(_luma(c.get(x, y)) for y in range(1, H, 2) for x in range(W))
    assert odd / even == pytest.approx(CS.SCANLINE, abs=0.02)
    centre = sum(_luma(c.get(x, y)) for y in range(H // 2 - 10, H // 2 + 10)
                 for x in range(W // 2 - 10, W // 2 + 10)) / 400.0
    corner = sum(_luma(c.get(x, y)) for y in range(H - 10, H) for x in range(W - 10, W)) / 100.0
    assert corner < 0.7 * centre


@pytest.mark.parametrize("gid", [g[0] for g in CS.GAMES])
def test_the_picture_is_a_ballgame_on_grass_under_a_score_bug(gid):
    c, f = CS.paint(gid)
    game = CS.BY_ID[gid]
    assert f["sport"] == game[1] and f["scene"] in CS.SCENES[game[1]]
    # the lower half of the frame is mostly the field: green dominant
    green = sum(1 for y in range(c.h // 2, c.h) for x in range(c.w)
                if c.get(x, y)[1] > c.get(x, y)[0] and c.get(x, y)[1] > c.get(x, y)[2])
    assert green > 0.45 * c.w * (c.h // 2), green
    # the bug is in the top-left corner and dark behind its type
    x0, y0, x1, y1 = f["bug_rect"]
    assert x1 <= c.w * 0.45 and y1 <= c.h * 0.35
    assert f["bug"] == CS.bug_lines(gid)
    assert f["bug"][0].split()[0] == game[3] and f["bug"][1].split()[0] == game[4]


def test_both_sports_and_all_four_scenes_are_on_the_table():
    assert {g[1] for g in CS.GAMES} == set(CS.SPORTS) == {"football", "baseball"}
    assert {(g[1], g[2]) for g in CS.GAMES} == {(s, sc) for s in CS.SPORTS for sc in CS.SCENES[s]}
    assert len(CS.GAMES) == len(CS.BY_ID)


def test_no_score_bug_names_a_real_team_league_network_or_station():
    said = set(CS.TEAMS)
    for g in CS.GAMES:
        for line in CS.bug_lines(g[0]):
            said |= set(re.findall(r"[A-Z0-9]+", line.upper()))
        said |= set(g[0].upper().split("_"))
    assert said & DENY == set(), sorted(said & DENY)
    for word in said:
        assert not any(p in word for p in DENY_PARTS), word
    # the teams are the table's, and every bug is spellable in the face
    from zoo_keeper.core import pixel_type_glyphs as G
    for g in CS.GAMES:
        assert g[3] in CS.TEAMS and g[4] in CS.TEAMS and g[3] != g[4]
        for line in CS.bug_lines(g[0]):
            assert all(ch in G.GLYPHS for ch in line), line


def test_no_jersey_is_green_on_green():
    for team, (jersey, _trim) in CS.TEAMS.items():
        assert not (jersey[1] > jersey[0] + 20 and jersey[1] > jersey[2] + 20), team


# --- which game --------------------------------------------------------------------


def _module_plan(dims=DC_SIZES[0], variant=0, form="bracket"):
    slot = {"slot_id": "tv", "role": "prop", "size_mod": "full", "style": 1, "species": "crt_tv",
            "fit": {"dims": list(dims), "pivot": "center"}, "form": form}
    if variant:
        slot["variant"] = variant
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    from zoo_keeper.core import dna
    return plan["modules"][0], dna


def test_the_genome_has_four_variants_and_the_kit_honours_them():
    g = genome_mod.load_species("crt_tv")
    assert g["module_variants"] == 4
    assert genome_mod.validate_genome(g) == []
    for v in range(4):
        mod, _dna = _module_plan(variant=v)
        assert mod["stem"].endswith("_fbracket" + ("_n%d" % v if v else "")), mod["stem"]
    dress, why = kit.honour_dressing({"form": "bracket", "variant": 4}, "crt_tv")
    assert why and dress == {"form": None, "stock": None, "variant": None}


@pytest.mark.parametrize("key", ["prop_crt_tv_delco_1997_01_w60_d55_h50_fbracket",
                                 "prop_crt_tv_delco_1997_01_w70_d60_h55_fbracket", "k", "other"])
def test_variants_alternate_sports_and_never_repeat_a_game(key):
    order = CS.game_order(key)
    assert sorted(order) == sorted(CS.BY_ID)
    sports = [CS.BY_ID[i][1] for i in order]
    assert all(sports[k] != sports[k + 1] for k in range(len(sports) - 1))
    assert len(set(order[:4])) == 4


def test_a_module_picks_by_its_stem_without_the_variant_and_by_its_variant():
    picks = []
    for v in range(4):
        plan = {"params": {}, "module": {"stem": "prop_crt_tv_x_fbracket" + ("_n%d" % v if v else ""),
                                         "variant": v}}
        picks.append(CS.pick_game(plan))
    assert picks == CS.game_order("prop_crt_tv_x_fbracket")[:4]
    assert {CS.BY_ID[p][1] for p in picks[:2]} == {"football", "baseball"}
    assert CS.pick_game({"params": {"game": "wdr_scr"}, "module": {"stem": "s"}}) == "wdr_scr"
    # the two sizes the club recipe places open on different games
    a = CS.game_order("prop_crt_tv_delco_1997_01_w60_d55_h50_fbracket")[0]
    b = CS.game_order("prop_crt_tv_delco_1997_01_w70_d60_h55_fbracket")[0]
    assert a != b


# --- the bracket set's face ----------------------------------------------------------


@pytest.mark.parametrize("dims", CORNERS)
def test_the_bracket_set_claims_its_slot_with_a_curved_four_by_three_face(dims):
    got = K.plan_bracket(*dims)
    lo, hi = P.bounds(got["prims"])
    w, d, h = dims
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-6, (dims, lo, hi)
    assert P.coincident_pairs(got["prims"]) == []
    assert P.tri_count(got["prims"]) <= genome_mod.load_species("crt_tv")["budgets"]["tris_lod0"]
    sw, sh = got["screen_m"]
    assert sw / sh == pytest.approx(4.0 / 3.0)
    screens = [p for p in got["prims"] if p["part"] == "CRT_Screen"]
    assert len(screens) == 1 and len(screens[0]["uvs"]) == len(screens[0]["faces"])
    for f, uv in zip(screens[0]["faces"], screens[0]["uvs"]):
        assert len(f) == len(uv) and all(0.0 <= c <= 1.0 for q in uv for c in q)


def test_the_face_bulges_toward_the_room_and_its_corners_sink_behind_the_bezel():
    p = K.screen_prim(0.4, 0.3, -0.25, 0.3)
    nu, nv = K.SCREEN_GRID
    front = p["verts"][:(nu + 1) * (nv + 1)]
    corners = [front[0], front[nu], front[-1], front[-1 - nu]]
    centre = front[(nv // 2) * (nu + 1) + nu // 2]
    assert all(c[1] == pytest.approx(-0.25 + K.SCREEN_SINK) for c in corners)
    assert centre[1] == pytest.approx(-0.25 - K.SCREEN_BULGE)
    # the picture is mapped edge to edge on the front grid, v up
    front_uvs = [uv for f, uv in zip(p["faces"], p["uvs"]) if all(i < len(front) for i in f)]
    us = [q[0] for uv in front_uvs for q in uv]
    vs = [q[1] for uv in front_uvs for q in uv]
    assert (min(us), max(us), min(vs), max(vs)) == (0.0, 1.0, 0.0, 1.0)
    bottom_left = next(uv for f, uv in zip(p["faces"], p["uvs"]) if f[0] == 0)
    assert bottom_left[0] == (0.0, 0.0)


def test_the_glow_is_a_picture_now_and_brighter_than_the_dead_tube():
    assert K.SCREEN_EMISSION > K.SCREEN_EMISSIVE_0_89[1]
    assert 0.0 < K.SCREEN_ALBEDO < 1.0


# --- the stand set ---------------------------------------------------------------------


def _stand_bounds(L):
    lo, hi = [1e9] * 3, [-1e9] * 3
    for key in ("body", "screen", "feet"):
        for c, s in L[key]:
            for k in range(3):
                lo[k] = min(lo[k], c[k] - s[k] / 2)
                hi[k] = max(hi[k], c[k] + s[k] / 2)
    for c, r, depth in L["knobs"]:
        for k, half in ((0, r), (1, depth / 2), (2, r)):
            lo[k] = min(lo[k], c[k] - half)
            hi[k] = max(hi[k], c[k] + half)
    return lo, hi


@pytest.mark.parametrize("dims", _corners())
@pytest.mark.parametrize("knobs", [0, 2, 4])
def test_the_stand_set_fits_its_slot_and_its_glass_can_be_seen(dims, knobs):
    """0.86.0 - 0.89.0: knobs 22 mm past the slot's front and the screen box
    10-30 mm behind the body's face."""
    w, d, h = dims
    L = K.stand_layout(w, d, h, knobs)
    lo, hi = _stand_bounds(L)
    want_lo = [-w / 2, -d / 2, 0.0]
    want_hi = [w / 2, d / 2, h]
    for k in range(3):
        assert hi[k] == pytest.approx(want_hi[k], abs=1e-9), (k, hi)
        # with no knobs the glass is the frontmost thing, inside the slot
        if k == 1 and knobs == 0:
            assert lo[k] > want_lo[k] - 1e-9
        else:
            assert lo[k] == pytest.approx(want_lo[k], abs=1e-9), (k, lo)
    body_front = L["body"][0][0][1] - L["body"][0][1][1] / 2
    (sc, ss), = L["screen"]
    assert sc[1] - ss[1] / 2 < body_front - 0.005          # proud of the face
    assert sc[1] + ss[1] / 2 > body_front                  # and into it
    for c, _r, depth in L["knobs"]:
        assert c[1] + depth / 2 >= body_front + K.STAND_BURY - 1e-9
    body_bottom = L["body"][0][0][2] - L["body"][0][1][2] / 2
    for c, s in L["feet"]:
        assert c[2] + s[2] / 2 >= body_bottom + K.STAND_BURY - 1e-9


# --- the built module (bpy) --------------------------------------------------------------


def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    slot = {"slot_id": "tv", "role": "prop", "size_mod": "full", "style": 1,
            "species": "crt_tv", "fit": {"dims": list(dims), "pivot": "center"}}
    slot.update(fields)
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    objs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"
                   and not o.name.endswith(_COL_SUFFIXES)), key=lambda o: o.name)
    return res, objs


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


@pytest.mark.parametrize("dims", CORNERS[:6])
@pytest.mark.parametrize("form", ["stand", "bracket"])
def test_bpy_both_forms_fit_pass_and_share_no_plane(tmp_path, dims, form):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims, form=form)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    assert abs(got["width"] - dims[0]) <= 0.001 and abs(got["depth"] - dims[1]) <= 0.001, got
    assert abs(got["height"] - dims[2]) <= 0.001, got
    assert _probe(objs) == []


def test_bpy_the_stand_sets_glass_is_in_front_of_its_body(tmp_path):
    pytest.importorskip("bpy")
    _res, objs = _build(tmp_path, (0.55, 0.5, 0.42), form="stand")
    by = {o.name: o for o in objs}

    def front(o):
        return min((o.matrix_world @ v.co).y for v in o.data.vertices)
    assert front(by["CRT_Screen"]) < front(by["CRT_Body"]) - 0.005


@pytest.mark.parametrize("dims", DC_SIZES)
def test_bpy_the_screen_glows_with_its_picture_and_the_file_says_so(tmp_path, dims):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims, form="bracket")
    lit = [o for o in objs if any(s.material and s.material.name.endswith("_Face")
                                  for s in o.material_slots)]
    assert [o.name for o in lit] == ["CRT_Screen"]
    ca = lit[0].data.color_attributes.get("Wear")
    assert ca is not None and min(min(c.color[:3]) for c in ca.data) >= 0.999
    assert lit[0].data.uv_layers
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    faces = [m for m in doc["materials"] if m["name"].endswith("_Face")]
    assert len(faces) == 1 and faces[0]["name"].startswith("M_CRT_Screen_crt_")
    m = faces[0]
    assert "emissiveTexture" in m and m["emissiveFactor"] == [1, 1, 1]
    strength = (m.get("extensions") or {}).get("KHR_materials_emissive_strength", {}).get(
        "emissiveStrength", 1.0)
    assert strength == pytest.approx(K.SCREEN_EMISSION)
    assert [i["name"] for i in doc["images"] if i["name"].startswith("crt_")]
    others = [x for x in doc["materials"] if not x["name"].endswith("_Face")]
    assert all(not any(x.get("emissiveFactor", [0])) and "emissiveTexture" not in x for x in others)


def test_bpy_the_same_file_every_build_and_four_variants_four_games(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, DC_SIZES[0], form="bracket", variant=1)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]
    games = []
    for v in range(4):
        out = tmp_path / ("v%d" % v)
        res, _o = _build(out, DC_SIZES[0], form="bracket", variant=v)
        doc = _glb_json(os.path.join(str(out), res["files"]["glb"]))
        names = [i["name"] for i in doc["images"] if i["name"].startswith("crt_")]
        assert len(names) == 1
        games.append(re.match(r"crt_([a-z]+_[a-z]+)_\d+x\d+_[0-9a-f]{8}$", names[0]).group(1))
    assert len(set(games)) == 4
    assert [CS.BY_ID[g][1] for g in games[:2]] in (["football", "baseball"], ["baseball", "football"])
