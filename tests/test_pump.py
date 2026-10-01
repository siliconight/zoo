"""The pump (1.36.0): a 1997 two-sided mechanical gas pump, two atlases, two draws.

Minted 2026-09-12 by tools/new_species.py (roadmap 150) as a placeholder box;
drawn after cold run 9120's FLAPPHAS walk, the walker: "pumps first". What is
held: the slot is filled by construction, centred, with no face sharing a
plane, over the whole genome range (the first cut's hose met the body's end
at a narrow slot, and its trigger guard thinned to 1.75 mm); the faces are
the slot's two LONG sides and each reads REGULAR, PLUS, SUPER left to right;
every face points out of its part, the hose's included; the hose clears the
holster, the price window and the base; every line of every tile SETS (the
first cut dropped the 9/10 and the plate on most sizes, silently); the prices
and the brand are the pylon's; every name is invented; and a built pump is
two objects, two materials, its glow a `_Face`.
"""
from __future__ import annotations

import json
import os
import re
import struct

import pytest

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import card_brands as CB
from zoo_keeper.core import club_names as CN
from zoo_keeper.core import genome
from zoo_keeper.core import kit
from zoo_keeper.core import poster_copy as PC
from zoo_keeper.core import price_pylon_forms as PY
from zoo_keeper.core import prims as P
from zoo_keeper.core import pump_forms as F

G = genome.load_species("pump")
_D = G["dimensions"]
SIZES = [(w, d, h) for w in (_D["width"]["min"], 1.0, 1.2, _D["width"]["max"])
         for d in (_D["depth"]["min"], 1.0, 1.2, _D["depth"]["max"])
         for h in (_D["height"]["min"], 1.4, _D["height"]["max"])]
#: Real fuel brands of the period and the region, which no word on it may be.
REAL_FUEL = {"SUNOCO", "MOBIL", "EXXON", "SHELL", "GULF", "TEXACO", "CITGO", "AMOCO", "ARCO",
             "BP", "WAWA", "SHEETZ", "GETTY", "HESS", "LUKOIL", "CHEVRON", "VALERO", "SPEEDWAY",
             "MARATHON", "PHILLIPS", "CONOCO", "ESSO", "SINCLAIR", "UNOCAL", "FINA"}


def _normal(p, f):
    vs = [p["verts"][i] for i in f]
    a, b, c = vs[0], vs[1], vs[2]
    u = [b[i] - a[i] for i in range(3)]
    w = [c[i] - a[i] for i in range(3)]
    n = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
    L = sum(x * x for x in n) ** 0.5
    return tuple(x / L for x in n)


def _centre(vs):
    return tuple(sum(v[k] for v in vs) / len(vs) for k in range(3))


def test_pump_is_discovered_and_validates():
    assert "pump" in genome.list_species()
    assert genome.validate_genome(G) == []
    assert G["parts"] == ["Pump_Art", "PumpGlow_Art"] and G["module_variants"] == 4


def test_pump_plans_at_its_authored_dims():
    """Every slot the library authors (1.0 x 1.2 x 1.4, 42 of them in six
    gas station specs) and Lot's rotated sites' (1.2 x 1.0) plan as a pump."""
    for dims, stem in (([1.0, 1.2, 1.4], "prop_pump_delco_1997_01_w100_d120_h140"),
                       ([1.2, 1.0, 1.4], "prop_pump_delco_1997_01_w120_d100_h140")):
        plan = kit.plan_kit({"building_id": "t", "slots": [{
            "slot_id": "pump_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "pump", "fit": {"dims": dims, "pivot": "center"}}]},
            theme="delco_1997", style=1)
        assert plan["species_fallbacks"] == [] and plan["dressing_fallbacks"] == []
        assert plan["modules"][0]["stem"] == stem


def test_the_slot_is_filled_centred_with_no_shared_plane():
    budget = G["budgets"]["tris_lod0"]
    for w, d, h in SIZES:
        for v in range(4):
            g = F.plan(w, d, h, v)
            lo, hi = P.bounds(g["prims"])
            assert [round(hi[k] - lo[k], 6) for k in range(3)] == [w, d, h], (w, d, h)
            assert abs(lo[0] + hi[0]) < 1e-9 and abs(lo[1] + hi[1]) < 1e-9 and abs(lo[2]) < 1e-9
            assert P.coincident_pairs(g["prims"]) == [], (w, d, h, v)
            assert g["facts"]["tris"] <= budget


@pytest.mark.parametrize("dims,axis", [((1.0, 1.2, 1.4), 0), ((1.2, 1.0, 1.4), 1),
                                       ((0.8, 1.6, 2.2), 0), ((1.6, 0.8, 1.2), 1)])
def test_the_faces_are_the_long_sides_and_read_left_to_right(dims, axis):
    """A car fuels at either lane: DC's islands run along Y, so its slot is
    1.0 x 1.2 and the faces are +-X; Lot's rotated sites hand Zoo 1.2 x 1.0
    and they are +-Y. From either face the viewer reads REGULAR at the left."""
    g = F.plan(*dims)
    heads = [p for p in g["prims"] if p["part"].endswith("_Header")]
    assert len(heads) == 2
    for hd in heads:
        n = _normal(hd, hd["faces"][0])
        assert abs(abs(n[axis]) - 1.0) < 1e-9, (hd["part"], n)
        side = hd["part"].split("_")[1]                  # A or B
        dials = {int(p["part"].split("_")[1][1:]): _centre(p["verts"]) for p in g["prims"]
                 if p["part"].startswith(f"Pump_{side}") and p["part"].endswith("_Dial")}
        # the viewer's right, for a face whose outward normal is n: up x n
        right = (-n[1], n[0], 0.0)
        along = [sum(dials[i][k] * right[k] for k in range(3)) for i in range(3)]
        assert along[0] < along[1] < along[2], (hd["part"], along)


def test_every_face_points_out_of_its_part():
    """Out of the body for the panels and the header; INTO the hole for the
    window's walls (the ATM's first cut wound those out); away from the hose's
    centreline for every side of the tube, and along it for its caps."""
    g = F.plan(1.0, 1.2, 1.4)
    for p in g["prims"]:
        part = p["part"]
        if part.endswith("_Hose"):
            vs = p["verts"]
            n_rings = len(vs) // 4
            for k, f in enumerate(p["faces"]):
                nrm = _normal(p, f)
                if k < (n_rings - 1) * 4:
                    i = k // 4
                    c = _centre(vs[i * 4:(i + 2) * 4])
                    fc = _centre([vs[j] for j in f])
                    assert sum(nrm[a] * (fc[a] - c[a]) for a in range(3)) > 0, (part, k)
                else:
                    first = k == (n_rings - 1) * 4
                    here = _centre(vs[0:4] if first else vs[-4:])
                    there = _centre(vs[4:8] if first else vs[-8:-4])
                    assert sum(nrm[a] * (here[a] - there[a]) for a in range(3)) > 0, (part, k)
            continue
        if part.startswith("Pump_Base") or part.startswith("Pump_Body") or part.startswith("Pump_HeaderBox"):
            continue
        n = _normal(p, p["faces"][0])
        fc = _centre(p["verts"])
        if "_Well_" in part:
            # a wall of the window's recess faces the window's centre line
            dial = next(q for q in g["prims"] if q["part"] == part.split("_Well_")[0] + "_Dial")
            dc = _centre(dial["verts"])
            assert sum(n[a] * (dc[a] - fc[a]) for a in (1, 2)) > 0 or \
                sum(n[a] * (dc[a] - fc[a]) for a in (0, 2)) > 0, part
        elif part.endswith(("_PanelB", "_PanelT", "_PanelL", "_PanelR", "_Dial", "_Header")):
            assert abs(fc[0] * n[0] + fc[1] * n[1]) > 0 and fc[0] * n[0] + fc[1] * n[1] > 0, (part, n)


def test_the_hose_clears_the_holster_the_window_and_the_base():
    for w, d, h in SIZES:
        g = F.plan(w, d, h)
        f = g["facts"]
        zb = h * F.BASE
        prims = {p["part"]: p for p in g["prims"]}
        for name, p in prims.items():
            if not name.endswith("_Hose"):
                continue
            g_ = name[:-len("_Hose")]
            hol = P.bounds([q for k, q in prims.items() if k.startswith(g_ + "_Holster")])
            win = P.bounds([prims[g_ + "_Dial"]])
            vs = p["verts"][:-4]                         # the last ring is in the body
            assert min(v[2] for v in p["verts"]) >= zb + 0.02, (w, d, h, name)
            for v in vs:
                inside_hol = all(hol[0][k] - 1e-9 <= v[k] <= hol[1][k] + 1e-9 for k in range(3))
                assert not inside_hol, (w, d, h, name, v)
                # never over the window: nothing of the hose inside its
                # outline as the viewer sees it
                ax = 1 if f["faces"] == "x" else 0
                inside_win = (win[0][ax] - 1e-9 <= v[ax] <= win[1][ax] + 1e-9
                              and win[0][2] - 1e-9 <= v[2] <= win[1][2] + 1e-9)
                assert not inside_win, (w, d, h, name, v)


def test_the_hose_never_folds_through_itself():
    """At a joint turning by theta, the tube's inner side is shortened by
    r * tan(theta / 2) at each end; a segment shorter than that crosses
    itself. The first cut's cubic drew a 3.5 cm segment turning 69 degrees,
    and a resampling of it a 121-degree cusp. Every joint, every size."""
    import math
    for w, d, h in SIZES:
        for p in F.plan(w, d, h)["prims"]:
            if not p["part"].endswith("_Hose"):
                continue
            vs = p["verts"]
            c = [_centre(vs[i * 4:(i + 1) * 4]) for i in range(len(vs) // 4)]
            for i in range(1, len(c) - 1):
                a = [c[i][k] - c[i - 1][k] for k in range(3)]
                b = [c[i + 1][k] - c[i][k] for k in range(3)]
                la, lb = math.dist(c[i], c[i - 1]), math.dist(c[i + 1], c[i])
                cos = max(-1.0, min(1.0, sum(a[k] * b[k] for k in range(3)) / (la * lb)))
                theta = math.acos(cos)
                assert theta < math.radians(120), (w, d, h, p["part"], i, math.degrees(theta))
                cut = 2.0 * F.HOSE_R * math.tan(theta / 2.0)
                assert min(la, lb) > cut, (w, d, h, p["part"], i, la, lb, cut)


def test_two_atlases_two_materials_the_glow_is_the_wheels_and_the_header():
    g = F.plan(1.0, 1.2, 1.4, 1)
    assert {p["mat"] for p in g["prims"]} == {"paint", "glow"}
    glow = {k for k, (a, _s) in g["tiles"].items() if a == "glow"}
    assert glow == {"dial0", "dial1", "dial2", "header"}
    assert {p["tile"] for p in g["prims"] if p["mat"] == "glow"} == glow


def test_every_line_of_every_tile_sets_at_every_size():
    """A line `fit_text` cannot set is dropped in silence; the first cut lost
    the 9/10 and the plate that way on most of the range."""
    for w, d, h in SIZES:
        for v in range(4):
            for k, (_a, spec) in F.plan(w, d, h, v)["tiles"].items():
                c = CA.paint(spec)
                assert not getattr(c, "unset", []), (w, d, h, v, k, c.unset)


def test_the_prices_and_the_brand_are_the_pylon_s():
    for v in range(4):
        g = F.plan(1.0, 1.2, 1.4, v)
        assert tuple(g["tiles"][f"dial{i}"][1]["price"] for i in range(3)) == PY.PRICE_SETS[v]
        assert g["tiles"]["header"][1]["variant"] == v
    assert F.all_strings().count(PY.STORE) == 1


def test_the_names_are_invented():
    parts = PC.DENYLIST + tuple(CB.DENY_PARTS) + CN.DENYLIST + CN.BEER_DENYLIST
    for text in F.all_strings():
        up = text.upper()
        tokens = set(re.findall(r"[A-Z0-9']+", up))
        assert not tokens & set(CB.DENY_WORDS), text
        assert not tokens & REAL_FUEL, text
        assert not any(bad in up for bad in parts), (text, [b for b in parts if b in up])


@pytest.mark.parametrize("dims", [(1.0, 1.2, 1.4), (1.2, 1.0, 1.4)])
def test_bpy_a_pump_is_two_objects_two_materials_and_fits(tmp_path, dims):
    bpy = pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    slot = {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1, "species": "pump",
            "material": "metal_painted", "fit": {"dims": list(dims), "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.endswith(_COL_SUFFIXES)]
    assert len(objs) == 2
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    ln, _kind = struct.unpack_from("<I4s", raw, 12)
    doc = json.loads(raw[20:20 + ln])
    mats = doc["materials"]
    assert len(mats) == 2
    lit = [m for m in mats if m.get("emissiveFactor") and max(m["emissiveFactor"]) > 0]
    assert len(lit) == 1 and lit[0]["name"].endswith("_Face"), [m["name"] for m in mats]
