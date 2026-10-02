"""Screens that run (1.45.0): shutters over the ATM's and the video poker's CRTs.

The walker, 2026-10-02: the lit screens are "just fixed with nothing
dynamic/alive about them". Held: a shutter stands proud of its screen, inside
it, facing the viewer; its schedule is a real one; the poker's five are over
its five cards and DEAL -- one after another, a held hand, then none; the
ATM's two are over its first two lines and take turns, never both, never
neither; a tube too small for two lines has none; and a built machine
carries the schedule in the two UV sets a consumer reads.
"""
from __future__ import annotations

import json
import os
import struct

import pytest

from zoo_keeper.core import atm_forms as A
from zoo_keeper.core import kit
from zoo_keeper.core import prims as P
from zoo_keeper.core import shutters as SH
from zoo_keeper.core import video_poker_forms as F


def _normal(p):
    a, b, c = (p["verts"][i] for i in p["faces"][0][:3])
    u = [b[k] - a[k] for k in range(3)]
    v = [c[k] - a[k] for k in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    size = sum(x * x for x in n) ** 0.5
    return tuple(x / size for x in n)


def _screen(prims, part):
    (s,) = [p for p in prims if p["part"] == part]
    return s


def _shutters(prims):
    return [p for p in prims if p.get("shutter")]


@pytest.mark.parametrize("plan,part", [(F.plan(0.65, 0.65, 1.75, 0), "VP_Screen"),
                                       (A.plan(0.6, 0.55, 1.45, 0), "ATM_Screen")])
def test_a_shutter_stands_proud_of_its_screen_inside_it_facing_out(plan, part):
    screen = _screen(plan["prims"], part)
    lo, hi = P.bounds([screen])
    shut = _shutters(plan["prims"])
    assert shut
    for p in shut:
        assert p["mat"] == SH.MAT and "tile" not in p
        assert all(abs(a - b) < 1e-9 for a, b in zip(_normal(p), _normal(screen)))
        slo, shi = P.bounds([p])
        assert abs((lo[1] - slo[1]) - SH.PROUD) < 1e-9 and abs(slo[1] - shi[1]) < 1e-12   # toward -Y
        assert lo[0] - 1e-9 <= slo[0] < shi[0] <= hi[0] + 1e-9
        assert lo[2] - 1e-9 <= slo[2] < shi[2] <= hi[2] + 1e-9
        a, b, period, _phase = p["shutter"]
        assert 0.0 <= a < b <= 1.0 and period > 0.0
    assert P.coincident_pairs(plan["prims"]) == []


def test_the_poker_deals_one_card_after_another_holds_and_clears():
    g = F.plan(0.65, 0.65, 1.75, 2)
    shut = sorted(_shutters(g["prims"]), key=lambda p: min(v[0] for v in p["verts"]))
    assert len(shut) == 5
    # left to right, each opens later than the one before and all close together
    opens = [p["shutter"][0] for p in shut]
    assert opens == sorted(opens) and len(set(opens)) == 5
    assert {p["shutter"][1] for p in shut} == {F.DEAL_HOLD}
    period = F.DEAL_PERIOD_S

    def showing(t):
        return [SH.is_open(p["shutter"], t) for p in shut]
    assert showing(0.0) == [False] * 5                          # a new deal: no cards
    assert showing(period * (F.DEAL_FIRST + 0.5 * F.DEAL_STEP)) == [True] + [False] * 4
    assert showing(period * 0.5) == [True] * 5                  # the hand, held
    assert showing(period * 0.96) == [False] * 5                # cleared
    assert showing(period * 1.5) == [True] * 5                  # and round again
    # each is over its card, a pixel wider all round
    screen = _screen(g["prims"], "VP_Screen")
    lo, hi = P.bounds([screen])
    tile = g["tiles"]["screen"][1]
    wpx, hpx = F._px(tile["w_m"]), F._px(tile["h_m"])
    for p, (bx0, by0, bx1, by1) in zip(shut, F.card_boxes(wpx, hpx)):
        slo, shi = P.bounds([p])
        u0 = (slo[0] - lo[0]) / (hi[0] - lo[0])
        u1 = (shi[0] - lo[0]) / (hi[0] - lo[0])
        v_top = 1.0 - (shi[2] - lo[2]) / (hi[2] - lo[2])
        v_foot = 1.0 - (slo[2] - lo[2]) / (hi[2] - lo[2])
        assert u0 * wpx <= bx0 and bx1 <= u1 * wpx and u1 * wpx - bx1 <= 1.0 + 1e-6
        assert v_top * hpx <= by0 and by1 <= v_foot * hpx


def test_the_atm_takes_turns_between_its_greeting_and_insert_card():
    g = A.plan(0.6, 0.55, 1.45, 1)
    shut = sorted(_shutters(g["prims"]), key=lambda p: -max(v[2] for v in p["verts"]))
    assert len(shut) == 2                                        # top line first
    assert [p["shutter"][:2] for p in shut] == [(0.0, 0.5), (0.5, 1.0)]
    for t in (0.0, 0.7, 1.4, 1.6, 2.9, 3.1, 100.3):
        both = [SH.is_open(p["shutter"], t) for p in shut]
        assert sum(both) == 1, (t, both)                         # never both, never neither
    # the two do not overlap and the first is above the second
    (alo, ahi), (blo, bhi) = P.bounds([shut[0]]), P.bounds([shut[1]])
    assert alo[2] >= bhi[2] - 1e-9


def test_a_tube_too_small_for_two_lines_has_no_shutter():
    seen = set()
    for w, d, h in ((0.5, 0.4, 1.2), (0.6, 0.55, 1.45), (0.75, 0.7, 1.65)):
        g = A.plan(w, d, h, 0)
        tile = g["tiles"]["screen"][1]
        lines, _band = A.crt_bands(A._px(tile["h_m"]), tile["greet"])
        n = len(_shutters(g["prims"]))
        assert n == (2 if len(lines) >= 2 else 0), (w, d, h, len(lines), n)
        seen.add(n)
    assert 2 in seen


def test_a_schedule_outside_its_period_or_its_screen_is_refused():
    screen = [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]
    SH.over("x", screen, (0.1, 0.1, 0.9, 0.9), (0.0, 0.5, 2.0, 0.0))
    for rect, sched in (((0.5, 0.1, 0.4, 0.9), (0.0, 0.5, 2.0, 0.0)),
                        ((0.1, 0.1, 1.2, 0.9), (0.0, 0.5, 2.0, 0.0)),
                        ((0.1, 0.1, 0.9, 0.9), (0.6, 0.5, 2.0, 0.0)),
                        ((0.1, 0.1, 0.9, 0.9), (0.0, 0.5, 0.0, 0.0))):
        with pytest.raises(ValueError):
            SH.over("x", screen, rect, sched)


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _accessor(doc, raw, idx):
    acc = doc["accessors"][idx]
    view = doc["bufferViews"][acc["bufferView"]]
    ln = struct.unpack_from("<I", raw, 12)[0]
    start = 20 + ln + 8 + view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    n = {"VEC2": 2, "VEC3": 3}[acc["type"]]
    stride = view.get("byteStride") or 4 * n
    return [struct.unpack_from("<%df" % n, raw, start + i * stride) for i in range(acc["count"])]


@pytest.mark.parametrize("species,dims", [("video_poker", (0.65, 0.65, 1.75)), ("atm", (0.6, 0.55, 1.45))])
def test_bpy_the_schedule_arrives_in_two_uv_sets(tmp_path, species, dims):
    pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build
    slot = {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1, "species": species,
            "variant": 1, "material": "metal_painted", "fit": {"dims": list(dims), "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    ln = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20:20 + ln])
    module = A if species == "atm" else F
    mat = next(i for i, m in enumerate(doc["materials"])
               if m["name"] == SH.material_name(module.SHUTTER_RGB))
    # its base colour is the tube's background (linear), its alpha nothing
    factor = doc["materials"][mat]["pbrMetallicRoughness"]["baseColorFactor"]
    assert factor[3] == 0.0
    srgb = [round(255 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055)) for c in factor[:3]]
    assert all(abs(a - b) <= 1 for a, b in zip(srgb, module.SHUTTER_RGB)), (srgb, module.SHUTTER_RGB)
    prims = [p for m in doc["meshes"] for p in m["primitives"] if p.get("material") == mat]
    assert len(prims) == 1
    attrs = prims[0]["attributes"]
    assert "TEXCOORD_0" in attrs and "TEXCOORD_1" in attrs
    uv = set(_accessor(doc, raw, attrs["TEXCOORD_0"]))
    uv2 = set(_accessor(doc, raw, attrs["TEXCOORD_1"]))
    want = {p["shutter"] for p in module.plan(*dims, 1)["prims"] if p.get("shutter")}
    assert {(round(a, 4), round(b, 4)) for a, b in uv} == {(round(a, 4), round(b, 4)) for a, b, _p, _q in want}
    assert {(round(a, 4), round(b, 4)) for a, b in uv2} == {(round(p, 4), round(q, 4)) for _a, _b, p, q in want}
