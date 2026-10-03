"""The front-load dumpster (Zoo 1.58.0): one atlas, one draw, an invented
hauler, and a shape that fills its slot with no two faces on one plane."""
from __future__ import annotations

import json
import os
import re
import struct

import pytest

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import card_brands as CB
from zoo_keeper.core import club_names as CN
from zoo_keeper.core import dumpster_forms as D
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import kit
from zoo_keeper.core import poster_copy as PC
from zoo_keeper.core import prims as P

SIZES = [(w, d, h) for w in (1.5, 1.83, 2.1) for d in (0.9, 1.1, 1.5) for h in (1.1, 1.3, 1.6)]
#: Real waste haulers, and the two on the walker's reference photographs,
#: which no invented name may use as a word.
REAL_HAULERS = {"WASTE", "MANAGEMENT", "REPUBLIC", "BFI", "BROWNING", "FERRIS", "ALLIED",
                "PRESTIGE", "ROZNER'S", "ROZNERS", "WASTEQUIP", "CASELLA", "COVANTA"}


def test_the_genome_and_the_kit_stem():
    g = genome_mod.load_species("dumpster")
    assert genome_mod.validate_genome(g) == []
    assert g["parts"] == ["Dumpster_Art"] and g["module_variants"] == len(D.HAULERS)
    slot = {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1, "species": "dumpster",
            "variant": 2, "material": "metal_painted",
            "fit": {"dims": [1.83, 1.1, 1.3], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "dumpster"
    assert plan["modules"][0]["stem"].endswith("_w183_d110_h130_n2")


def test_the_slot_is_filled_centred_with_no_shared_plane():
    budget = genome_mod.load_species("dumpster")["budgets"]["tris_lod0"]
    for w, d, h in SIZES:
        for v in range(len(D.HAULERS)):
            g = D.plan(w, d, h, v)
            lo, hi = P.bounds(g["prims"])
            assert (round(hi[0] - lo[0], 6), round(hi[1] - lo[1], 6)) == (round(w, 6), round(d, 6))
            assert abs(lo[2]) < 1e-9 and abs(hi[2] - h) < 1e-9, (w, d, h)
            assert abs(lo[0] + hi[0]) < 1e-9 and abs(lo[1] + hi[1]) < 1e-9
            assert P.coincident_pairs(g["prims"]) == [], (w, d, h, v)
            assert g["facts"]["tris"] <= budget
            assert g["collision"] == ((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h))


def _normal(p):
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = [p["verts"][i] for i in p["faces"][0][:3]]
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    n = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    m = sum(c * c for c in n) ** 0.5
    return tuple(c / m for c in n)


def test_every_face_points_out_of_the_thing_it_closes():
    """A quad wound the wrong way is culled and the dumpster has a hole in
    it. Each part's name says which way it faces."""
    g = D.plan(1.83, 1.1, 1.3, 0)
    want = {"Front": (0, -1), "Back": (1, 1), "SideR": (0, 1), "SideL": (0, -1), "Under": (2, -1),
            "LidL": (2, 1), "LidR": (2, 1), "LidFront": (1, -1), "LidBack": (1, 1),
            "LidEdgeR": (0, 1), "LidEdgeL": (0, -1),
            "_front": (1, -1), "_back": (1, 1), "_right": (0, 1), "_left": (0, -1),
            "_top": (2, 1), "_under": (2, -1)}
    want["Front"] = (1, -1)
    seen = set()
    for p in g["prims"]:
        n = _normal(p)
        tail = p["part"].split("Dumpster_")[1]
        key = next((k for k in sorted(want, key=len, reverse=True)
                    if tail == k or (k.startswith("_") and tail.endswith(k))), None)
        assert key is not None, p["part"]
        axis, sign = want[key]
        assert n[axis] * sign > 0.5, (p["part"], n)
        seen.add(key)
    assert {"Front", "Back", "SideR", "SideL", "LidL", "LidR", "_front", "_under"} <= seen


def test_the_front_leans_and_is_lower_than_the_back():
    g = D.plan(1.83, 1.1, 1.3, 0)
    front = next(p for p in g["prims"] if p["part"] == "Dumpster_Front")
    back = next(p for p in g["prims"] if p["part"] == "Dumpster_Back")
    foot_y, top_y = front["verts"][0][1], front["verts"][3][1]
    assert foot_y - top_y == pytest.approx(1.1 * D.LEAN)          # the foot sits back from the top
    assert back["verts"][2][2] - front["verts"][2][2] == pytest.approx(1.3 * D.FRONT_DROP)


def test_one_atlas_one_material_and_every_quad_s_tile_exists():
    g = D.plan(1.83, 1.1, 1.3, 1)
    assert {p["mat"] for p in g["prims"]} == {"paint"}
    assert {a for a, _s in g["tiles"].values()} == {"paint"}
    assert {p["tile"] for p in g["prims"]} <= set(g["tiles"])
    assert g["facts"]["materials"] == 1 and g["facts"]["tris"] == 92


def test_every_line_of_every_tile_sets_at_every_size():
    """A line the painter cannot set is dropped in silence; the sticker is
    the point of the front."""
    for w, d, h in SIZES:
        for v in range(len(D.HAULERS)):
            for k, (_a, spec) in D.plan(w, d, h, v)["tiles"].items():
                c = CA.paint(spec)
                assert not getattr(c, "unset", []), (w, d, h, v, k, c.unset)


def test_a_hauler_s_paint_is_its_own_and_reads_against_asphalt():
    paints = [hl["paint"] for hl in D.HAULERS]
    assert len(set(paints)) == len(paints)
    for hl in D.HAULERS:
        # not a grey: the most and least of its channels stand well apart
        assert max(hl["paint"]) - min(hl["paint"]) >= 60, hl["id"]


def test_the_names_are_invented():
    parts = PC.DENYLIST + tuple(CB.DENY_PARTS) + CN.DENYLIST + CN.BEER_DENYLIST
    for text in D.all_strings():
        up = text.upper()
        tokens = set(re.findall(r"[A-Z0-9']+", up))
        assert not tokens & set(CB.DENY_WORDS), text
        assert not tokens & REAL_HAULERS, text
        assert not any(bad in up for bad in parts), (text, [b for b in parts if b in up])
    for hl in D.HAULERS:
        assert re.fullmatch(r"610-555-01\d\d", hl["phone"]), hl["phone"]     # the fictional exchange


@pytest.mark.parametrize("variant", [0, 3])
def test_bpy_a_dumpster_is_one_object_one_material_and_fits(tmp_path, variant):
    bpy = pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    slot = {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1, "species": "dumpster",
            "variant": variant, "material": "metal_painted",
            "fit": {"dims": [1.83, 1.1, 1.3], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.endswith(_COL_SUFFIXES)]
    assert len(objs) == 1
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    ln, _kind = struct.unpack_from("<I4s", raw, 12)
    doc = json.loads(raw[20:20 + ln])
    assert len(doc["materials"]) == 1
