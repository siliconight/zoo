"""The ATM (1.35.0): a 1990s freestanding surcharge ATM, two atlases, two draws.

The walker, 2026-09-29: "Convenient stores should also have ATMs". What is
held: the slot is filled by construction, centred, with no face sharing a
plane; every face points where its part faces (the first cut wound the
screen's recess inside out); every line of every tile SETS at every size the
genome allows (the first cut's greetings did not, and `fit_text` drops what it
cannot fit, silently); every name is invented and none echoes a real ATM
network; and a built ATM is two objects, two materials, its glow a `_Face`.
"""
from __future__ import annotations

import json
import os
import re
import struct

import pytest

from zoo_keeper.core import atm_forms as A
from zoo_keeper.core import card_art as CA
from zoo_keeper.core import card_brands as CB
from zoo_keeper.core import club_names as CN
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import kit
from zoo_keeper.core import poster_copy as PC
from zoo_keeper.core import prims as P

SIZES = [(w, d, h) for w in (0.5, 0.6, 0.75) for d in (0.4, 0.55, 0.7) for h in (1.2, 1.45, 1.65)]
#: Real ATM networks of the period, which no invented name may use as a word.
REAL_NETWORKS = {"MAC", "PLUS", "CIRRUS", "STAR", "HONOR", "NYCE", "PULSE", "MAESTRO",
                 "INTERLINK", "EXPLORE", "TYME", "MOST"}


def _normal(p, f):
    vs = [p["verts"][i] for i in f]
    a, b, c = vs[0], vs[1], vs[2]
    u = [b[i] - a[i] for i in range(3)]
    w = [c[i] - a[i] for i in range(3)]
    n = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
    L = sum(x * x for x in n) ** 0.5
    return tuple(x / L for x in n)


def test_the_genome_and_the_kit_stem():
    g = genome_mod.load_species("atm")
    assert genome_mod.validate_genome(g) == []
    assert g["parts"] == ["ATM_Art", "ATMGlow_Art"] and g["module_variants"] == 4
    slot = {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1, "species": "atm",
            "variant": 2, "material": "metal_painted",
            "fit": {"dims": [0.6, 0.55, 1.45], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    assert plan["modules"][0]["stem"] == "prop_atm_delco_1997_01_w60_d55_h145_n2"


@pytest.mark.parametrize("sign", [True, False])
def test_the_slot_is_filled_centred_with_no_shared_plane(sign):
    budget = genome_mod.load_species("atm")["budgets"]["tris_lod0"]
    for w, d, h in SIZES:
        for v in range(4):
            g = A.plan(w, d, h, v, sign)
            lo, hi = P.bounds(g["prims"])
            assert (round(hi[0] - lo[0], 6), round(hi[1] - lo[1], 6)) == (round(w, 6), round(d, 6))
            assert abs(lo[2]) < 1e-9 and abs(hi[2] - h) < 1e-9, (w, d, h, sign)
            assert abs(lo[0] + hi[0]) < 1e-9 and abs(lo[1] + hi[1]) < 1e-9
            assert P.coincident_pairs(g["prims"]) == [], (w, d, h, v, sign)
            assert g["facts"]["tris"] <= budget


def test_every_face_points_where_its_part_faces():
    """Outward for the shell, INTO the hole for the screen's recess (the
    first cut wound all four of those out), up and toward the customer for
    the keypad ledge."""
    want = {"_front": (0, -1, 0), "_back": (0, 1, 0), "_left": (-1, 0, 0), "_right": (1, 0, 0),
            "_top": (0, 0, 1), "Well_B": (0, 0, 1), "Well_T": (0, 0, -1), "Well_L": (1, 0, 0),
            "Well_R": (-1, 0, 0), "Fascia": (0, -1, 0), "Bezel": (0, -1, 0), "Screen": (0, -1, 0),
            "ATM_Sign": (0, -1, 0), "CabinetTop": (0, 0, 1), "LedgeSideL": (-1, 0, 0),
            "LedgeSideR": (1, 0, 0)}
    g = A.plan(0.6, 0.55, 1.45, 0)
    seen = set()
    for p in g["prims"]:
        n = _normal(p, p["faces"][0])
        if p["part"] == "ATM_Keypad":
            assert n[1] < -0.3 and n[2] > 0.3, n
            continue
        key = next(k for k in want if k in p["part"])
        seen.add(key)
        assert all(abs(n[i] - want[key][i]) < 1e-6 for i in range(3)), (p["part"], n)
    assert {"Well_B", "Well_T", "Well_L", "Well_R", "Screen", "ATM_Sign"} <= seen


def test_two_atlases_two_materials_the_glow_is_the_screen_and_the_topper():
    g = A.plan(0.6, 0.55, 1.45, 1)
    assert {p["mat"] for p in g["prims"]} == {"paint", "glow"}
    assert {k for k, (a, _s) in g["tiles"].items() if a == "glow"} == {"screen", "topper"}
    assert {p["tile"] for p in g["prims"] if p["mat"] == "glow"} == {"screen", "topper"}
    assert not {k for k, (a, _s) in A.plan(0.6, 0.55, 1.45, 1, sign=False)["tiles"].items()
                if k == "topper"}


def test_every_line_of_every_tile_sets_at_every_size():
    """A line `fit_text` cannot set is dropped in silence; the first cut lost
    three screens' greetings that way."""
    for w, d, h in SIZES:
        for v in range(4):
            for k, (_a, spec) in A.plan(w, d, h, v)["tiles"].items():
                c = CA.paint(spec)
                assert not getattr(c, "unset", []), (w, d, h, v, k, c.unset)
    # and the greeting is on every screen (a small tube drops lines from the end)
    for v in range(4):
        spec = A.plan(0.5, 0.4, 1.2, v)["tiles"]["screen"][1]
        assert spec["greet"] == A.NETWORKS[v][1]


def test_the_names_are_invented():
    parts = PC.DENYLIST + tuple(CB.DENY_PARTS) + CN.DENYLIST + CN.BEER_DENYLIST
    for text in A.all_strings():
        up = text.upper()
        tokens = set(re.findall(r"[A-Z0-9']+", up))
        assert not tokens & set(CB.DENY_WORDS), text
        assert not tokens & REAL_NETWORKS, text
        assert not any(bad in up for bad in parts), (text, [b for b in parts if b in up])


@pytest.mark.parametrize("variant", [0, 3])
def test_bpy_an_atm_is_two_objects_two_materials_and_fits(tmp_path, variant):
    bpy = pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    slot = {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1, "species": "atm",
            "variant": variant, "material": "metal_painted",
            "fit": {"dims": [0.6, 0.55, 1.45], "pivot": "center"}}
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
