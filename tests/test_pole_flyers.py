"""Flyers on a pole (1.34.0): a sleeve of handbills, one atlas, one draw.

The walker, 2026-09-30: six photographs of flyers on real poles, after cold run
9118 showed a flat 0.30 m bill on a 0.12 m pole reading as a small sign; and
their faded-'80s palette guide, "only if it helps, temper this". What is held:

  * every form fills its slot -- the sleeve's diameter and band -- by
    construction, centred, at every pole size Lot asks for, with no two
    sheets sharing a plane, inside the genome's triangle budget;
  * the paper curves round the pole and every facet faces out;
  * the newest layer is printed as painted; only older layers fade, and the
    fade takes bright ink before dark;
  * a run is one object with one material (built, in Blender).
"""
from __future__ import annotations

import json
import math
import os
import struct

import pytest

from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import kit
from zoo_keeper.core import pole_flyers_forms as F
from zoo_keeper.core import prims as P
from zoo_keeper.core.vending_forms import Canvas

#: Lot's poles: a streetlight's 0.06 m radius and a sign post's 0.05 m
#: half-width, each sleeved; and a wooden utility pole's, for the day there is one.
DIAMETERS = (0.09, 0.13, 0.156, 0.30, 0.40)


def _genome():
    return genome_mod.load_species("pole_flyers")


def test_the_genome_and_the_kit_stem():
    g = _genome()
    assert genome_mod.validate_genome(g) == []
    assert g["params"]["form"] == list(F.FORMS)
    slot = {"slot_id": "p", "role": "prop", "size_mod": "full", "style": 1, "species": "pole_flyers",
            "form": "wrap", "variant": 2, "material": "paper",
            "fit": {"dims": [0.156, 0.156, 1.9], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "site", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    assert plan["modules"][0]["stem"] == "prop_pole_flyers_delco_1997_01_w16_d16_h190_fwrap_n2"


@pytest.mark.parametrize("form", F.FORMS)
@pytest.mark.parametrize("d", DIAMETERS)
def test_every_form_fills_its_slot_centred_with_no_shared_plane(form, d):
    budget = _genome()["budgets"]["tris_lod0"]
    # the default band, and the genome's ends: a 0.30 m band scales the sheets
    # down; 2.4 m is the triangle budget's measured corner
    for h in (0.3, F.HEIGHT[form], 2.4):
        for v in range(4):
            g = F.plan(d, d, h, form, v, f"k{v}")
            lo, hi = P.bounds(g["prims"])
            for got, want in ((hi[0] - lo[0], d), (hi[1] - lo[1], d), (hi[2] - lo[2], h)):
                assert abs(got - want) <= F.FIT_TOL, (form, d, h, v, got, want)
            assert abs((hi[0] + lo[0]) / 2) <= F.FIT_TOL and abs((hi[1] + lo[1]) / 2) <= F.FIT_TOL
            assert abs(lo[2]) <= F.FIT_TOL
            assert P.coincident_pairs(g["prims"]) == [], (form, d, h, v)
            assert g["facts"]["tris"] <= budget, (form, g["facts"]["tris"])


@pytest.mark.parametrize("form", F.FORMS)
def test_the_paper_curves_round_the_pole_and_faces_out(form):
    g = F.plan(0.156, 0.156, F.HEIGHT[form], form, 1, "k")
    for p in g["prims"]:
        vs = p["verts"]
        for a, b, c, _d in p["faces"]:
            ax, ay, az = vs[a]
            u = [vs[b][i] - vs[a][i] for i in range(3)]
            w = [vs[c][i] - vs[a][i] for i in range(3)]
            n = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
            mx, my = (vs[a][0] + vs[b][0]) / 2, (vs[a][1] + vs[b][1]) / 2
            assert n[0] * mx + n[1] * my > 0, (form, p["tile"])      # outward
            assert abs(math.hypot(ax, ay) - math.hypot(*vs[b][:2])) < 1e-9  # on one circle


@pytest.mark.parametrize("form", F.FORMS)
def test_the_newest_layer_is_printed_and_only_older_paper_fades(form):
    """The walker: "only if it helps, temper this". Every form shows fresh
    paper on its outer layers, and the fade falls on the older ones only."""
    g = F.plan(0.156, 0.156, F.HEIGHT[form], form, 0, "k")
    pieces = g["facts"]["pieces"]
    fades = {t["fade"] for t in g["tiles"].values()}
    assert 0.0 in fades
    for piece, tile in zip(pieces, g["tiles"].values()):
        assert tile["fade"] == F.FADE[piece["layer"]]
    assert all(F.FADE[layer] == 0.0 for layer in (F.LAYERS - 1, F.LAYERS - 2))


@pytest.mark.parametrize("form", F.FORMS)
def test_one_bill_a_pole_is_loud(form):
    """1.41.0, the walker: "if anything its just too much color". Every
    sheet names its stock; the loud ones all carry ONE bill; and the newest
    layer shows it."""
    for variant in range(4):
        g = F.plan(0.3, 0.3, 1.6, form, variant, "pole")
        tiles = list(g["tiles"].values())
        assert all(t["stock"] in ("loud", "plain") for t in tiles)
        loud_rows = {t["row"] for t in tiles if t["stock"] == "loud"}
        assert len(loud_rows) == 1, (form, variant, loud_rows)
        assert any(t["stock"] == "loud" and not t["fade"] for t in tiles), (form, variant)
        assert sum(t["stock"] == "plain" for t in tiles) >= 2, (form, variant)


def test_fading_takes_bright_ink_before_dark():
    c = Canvas(2, 1, (0, 0, 0))
    c.px(0, 0, (250, 240, 60))      # day-glo yellow
    c.px(1, 0, (40, 30, 30))        # dark title ink
    before = [c.get(0, 0), c.get(1, 0)]
    F.fade(c, 0.6)
    moved = [sum(abs(a - b) for a, b in zip(before[i], c.get(i, 0))) for i in range(2)]
    lum = lambda p: 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
    # the dark ink stays dark enough to read; the bright field moves more
    # toward the paper's value than the ink does
    assert lum(c.get(1, 0)) < 110
    k_bright = 0.6 * (0.35 + 0.65 * lum(before[0]) / 255)
    k_dark = 0.6 * (0.35 + 0.65 * lum(before[1]) / 255)
    assert k_bright > k_dark and all(m > 0 for m in moved)


def test_a_pair_keeps_paper_on_the_back_so_the_slot_is_filled():
    g = F.plan(0.156, 0.156, F.HEIGHT["pair"], "pair", 0, "k")
    backs = [p for p in g["facts"]["pieces"] if abs(p["centre"] - (-F.FRONT)) < 1e-6]
    assert backs and backs[0]["scrap"] and backs[0]["layer"] < F.LAYERS - 2


def test_the_same_pole_every_time():
    a = F.plan(0.156, 0.156, 1.9, "wrap", 3, "k")
    b = F.plan(0.156, 0.156, 1.9, "wrap", 3, "k")
    assert a["prims"] == b["prims"] and a["tiles"] == b["tiles"]


def test_an_unknown_form_is_refused():
    with pytest.raises(ValueError):
        F.plan(0.156, 0.156, 1.0, "billboard", 0)


# --- built -----------------------------------------------------------------------------


@pytest.mark.parametrize("form", F.FORMS)
def test_bpy_a_pole_is_one_object_one_material_and_fits(tmp_path, form):
    bpy = pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    h = F.HEIGHT[form]
    slot = {"slot_id": "p", "role": "prop", "size_mod": "full", "style": 1, "species": "pole_flyers",
            "form": form, "variant": 1, "material": "paper",
            "fit": {"dims": [0.156, 0.156, h], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "site", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.endswith(_COL_SUFFIXES)]
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    assert len(objs) == 1 and len({s.material.name for o in objs for s in o.material_slots}) == 1
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    ln, _kind = struct.unpack_from("<I4s", raw, 12)
    doc = json.loads(raw[20:20 + ln])
    assert len(doc["images"]) == 1
    assert not any(m.get("emissiveFactor") and max(m["emissiveFactor"]) > 0 for m in doc["materials"])
