"""1.16.0 -- the registers on the counters have their green display.

The walker, 2026-09-28: "I also want the cash registers in these buildings
(where we have cash registers) to have that glowing green/black screen".
The registers the stores and bars stand were three beige boxes; both
counters now build `counter_register.station`: the keys at the clerk's end,
a lit operator display facing the clerk, a lit customer display facing the
customer, and a pole display. Pure half, then the built half (bpy).
"""
from __future__ import annotations

import os

import pytest

from zoo_keeper.core import back_bar_forms as BB
from zoo_keeper.core import counter_register as CREG
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import prims as P
from zoo_keeper.core import register_forms as RF
from zoo_keeper.core import service_counter_forms as SC


def _normal(p, k):
    a, b, c = (p["verts"][i] for i in p["faces"][k][:3])
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def _lit_face(p):
    return next(k for k, f in enumerate(p["uvs"]) if f[0][0] != "bezel")


def test_a_station_has_three_lit_windows_facing_the_right_people():
    solid, lit = CREG.station(0.4, 0.17, 1.08)
    assert sorted(p["uvs"][_lit_face(p)][0][0] for p in lit) == ["customer", "operator", "pole"]
    for p in lit:
        k = _lit_face(p)
        region = p["uvs"][k][0][0]
        ny = _normal(p, k)[1]
        # the customer (-Y) reads the customer window and the pole; the clerk (+Y) the operator's
        assert (ny < 0) == (region in ("customer", "pole")), (region, ny)
        assert p["mat"] == "vfd"
    assert P.coincident_pairs(solid + lit, tol=0.0022) == []


def test_the_digits_are_not_mirrored_on_either_side():
    """u must grow to the viewer's right: +x seen from -Y, -x seen from +Y."""
    _solid, lit = CREG.station(0.0, 0.0, 1.0)
    for p in lit:
        k = _lit_face(p)
        corners = [(p["verts"][i][0], c[1]) for i, c in zip(p["faces"][k], p["uvs"][k])]
        lo_x = min(corners)[1]
        hi_x = max(corners)[1]
        facing_minus_y = _normal(p, k)[1] < 0
        assert (hi_x > lo_x) == facing_minus_y, (p["uvs"][k][0][0], corners)


def test_the_keys_are_at_the_clerks_end_and_the_hump_at_the_customers():
    solid, _lit = CREG.station(0.0, 0.0, 1.0)
    keys = [p for p in solid if p["part"] == "Counter_RegisterKeys"]
    hx0, hy0, _z0, hx1, hy1, _z1 = CREG.hump(0.0, 0.0, 1.0)
    assert P.bounds(keys)[0][1] > hy1, "the keypad stands between the hump and the clerk"


def test_both_counters_build_the_same_register():
    h = 1.08
    _in, on_bar = BB.counter_fitout(4.0, 0.8, h, {"ATT_register": (0.6, 0.0, h)}, 4.0)
    solid, lit = CREG.station(0.6, 0.8 / 2.0 - CREG.REG_D / 2.0 - 0.06, h)
    reg = [p for p in on_bar if p["part"].startswith("Counter_Register")]
    assert [p["verts"] for p in reg] == [p["verts"] for p in solid + lit]
    assert (BB.REG_W, BB.REG_D, BB.REG_H, BB.REG_SCREEN_H) == (CREG.REG_W, CREG.REG_D, CREG.REG_H, CREG.REG_SCREEN_H)


def test_the_service_counter_carries_the_windows_and_shares_no_plane():
    from tests.test_service_counter import _fit
    _in, on_top, facts, _tw = _fit(6.0, 0.9, 1.1)
    lit = [p for p in on_top if p["mat"] == "vfd"]
    assert len(lit) == 3 * len(facts["registers"])
    assert P.coincident_pairs([p for p in on_top], tol=0.0022) == []


def test_the_display_art_sets_every_window_and_is_the_same_bytes():
    for price in RF.PRICES:
        A = CREG.art(price)
        W, H = A["size"]
        for r in ("customer", "operator", "pole", "bezel"):
            x0, y0, x1, y1 = A["rects"][r]
            assert 0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H
        # the customer's digits at the largest scale 1.0.0's display holds
        assert A["said"]["customer"][1] >= 2 and price.endswith(A["said"]["customer"][0][-4:])
        assert bytes(CREG.art(price)["canvas"].buf) == bytes(A["canvas"].buf)


def test_the_genome_names_the_new_parts():
    parts = set(genome_mod.load_species("counter")["parts"])
    assert {"Counter_RegisterPole", "Counter_RegisterHead", "Counter_RegisterScreen"} <= parts


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, form, dims):
    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import kit
    slot = {"slot_id": "register_counter", "role": "prop", "size_mod": "full", "style": 1,
            "species": "counter", "material": "wood", "form": form,
            "fit": {"dims": list(dims), "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    import json
    import struct
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    return res, json.loads(raw[20:20 + n])


@pytest.mark.parametrize("form,dims", [("service", (6.0, 0.9, 1.1)), ("bar", (4.0, 0.8, 1.08))])
def test_bpy_one_lit_display_material_a_counter(tmp_path, form, dims):
    pytest.importorskip("bpy")
    res, doc = _build(tmp_path, form, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    vfd = [m for m in doc["materials"] if m["name"].startswith("M_Counter_VFD_")]
    assert len(vfd) == 1 and vfd[0]["name"].endswith("_Face"), [m["name"] for m in doc["materials"]]
    assert any(vfd[0].get("emissiveFactor") or [0])
