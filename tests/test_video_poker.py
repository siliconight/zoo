"""The video-poker cabinet (1.39.0): a 1997 tavern upright, two atlases, two draws.

The walker, 2026-09-30, "PA Skill Games" in stores, bars and strip clubs, the
1997 period version agreed. Held, as the ATM's are: the slot is filled
centred with no shared plane at every size; every face points where its part
faces; two atlases, the glow on the CRT and the marquee only; every line of
every tile SETS at every size (`fit_text` drops what it cannot set, silently;
the first draft lost HOLD on every narrow unit's buttons and "10S" on its
cards); every name is invented, none a real maker or the Pennsylvania mark;
and a built cabinet is two objects, two materials, its glow a `_Face`.
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
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import kit
from zoo_keeper.core import poster_copy as PC
from zoo_keeper.core import prims as P
from zoo_keeper.core import video_poker_forms as F

SIZES = [(w, d, h) for w in (0.55, 0.65, 0.8) for d in (0.5, 0.65, 0.8) for h in (1.55, 1.75, 1.95)]
#: Real makers and marks of the trade, which no word on it may be.
REAL = {"IGT", "BALLY", "WILLIAMS", "ARISTOCRAT", "KONAMI", "WMS", "PACE", "O-MATIC",
        "POM", "PACE-O-MATIC", "PENNSYLVANIA", "SKILL", "GREENWOOD", "MILES", "BANILLA",
        "PARAGON", "TOUCHTUNES", "MEGATOUCH", "MERIT", "VGT"}


def test_the_genome_and_the_kit_stem():
    g = genome_mod.load_species("video_poker")
    assert genome_mod.validate_genome(g) == []
    assert g["parts"] == ["VideoPoker_Art", "VideoPokerGlow_Art", "VideoPoker_Shutter"]
    assert g["module_variants"] == 4
    slot = {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1, "species": "video_poker",
            "variant": 2, "material": "metal_painted",
            "fit": {"dims": [0.65, 0.65, 1.75], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == [] and plan["species_fallbacks"] == []
    assert plan["modules"][0]["stem"] == "prop_video_poker_delco_1997_01_w65_d65_h175_n2"


def test_the_slot_is_filled_centred_with_no_shared_plane():
    budget = genome_mod.load_species("video_poker")["budgets"]["tris_lod0"]
    for w, d, h in SIZES:
        for v in range(4):
            g = F.plan(w, d, h, v)
            lo, hi = P.bounds(g["prims"])
            assert [round(hi[k] - lo[k], 6) for k in range(3)] == [w, d, h]
            assert abs(lo[0] + hi[0]) < 1e-9 and abs(lo[1] + hi[1]) < 1e-9 and abs(lo[2]) < 1e-9
            assert P.coincident_pairs(g["prims"]) == [], (w, d, h, v)
            assert g["facts"]["tris"] <= budget


def test_every_face_points_where_its_part_faces():
    # 1.46.0: `machine_parts`' cabinet; `_machine_faces` reads each part's
    # direction off its name
    from tests import _machine_faces as MF
    g = F.plan(0.65, 0.65, 1.75, 0)
    seen = MF.check(g["prims"], sloped=("VP_Deck", "VP_Button"), screens=("VP_Screen",))
    assert {"Well_B", "Well_T", "Well_L", "Well_R", "Screen", "Sign", "Chamfer", "sloped",
            "Under", "Shutter"} <= seen


def test_two_atlases_the_glow_is_the_screen_and_the_marquee():
    g = F.plan(0.65, 0.65, 1.75, 1)
    # 1.45.0: and the deal's shutters, which are neither atlas
    assert {p["mat"] for p in g["prims"]} == {"paint", "glow", "shutter"}
    # 1.46.0: and the buttons, which are lit caps standing off the deck
    assert {k for k, (a, _s) in g["tiles"].items() if a == "glow"} == {
        "screen", "marquee", "btn_bet", "btn_deal", "btn_hold"}


def test_every_line_of_every_tile_sets_at_every_size():
    for w, d, h in SIZES:
        for v in range(4):
            for k, (_a, spec) in F.plan(w, d, h, v)["tiles"].items():
                c = CA.paint(spec)
                assert not getattr(c, "unset", []), (w, d, h, v, k, c.unset)


def test_the_names_are_invented():
    parts = PC.DENYLIST + tuple(CB.DENY_PARTS) + CN.DENYLIST + CN.BEER_DENYLIST
    for text in F.all_strings():
        up = text.upper()
        tokens = set(re.findall(r"[A-Z0-9'-]+", up))
        assert not tokens & REAL, text
        assert not any(bad in up for bad in parts), (text, [b for b in parts if b in up])
    for name, _f, _i in F.BRANDS:
        assert not set(name.split()) & set(CB.DENY_WORDS), name


@pytest.mark.parametrize("variant", [0, 3])
def test_bpy_a_cabinet_is_two_objects_two_materials_and_fits(tmp_path, variant):
    bpy = pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    slot = {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1, "species": "video_poker",
            "variant": variant, "material": "metal_painted",
            "fit": {"dims": [0.65, 0.65, 1.75], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.endswith(_COL_SUFFIXES)]
    assert len(objs) == 3                # 1.45.0: paint, glow, and the screen's shutters
    assert sum(o.name.endswith("_Shutter") for o in objs) == 1
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    ln, _kind = struct.unpack_from("<I4s", raw, 12)
    doc = json.loads(raw[20:20 + ln])
    mats = doc["materials"]
    assert len(mats) == 3
    shut = [m for m in mats if m["name"].startswith("M_Shutter_Screen")]
    # alpha 0 leaves Blender's exporter as MASK (measured: BLEND was asked
    # for), which is what is wanted anyway -- under the cutoff, nothing drawn
    assert len(shut) == 1 and shut[0].get("alphaMode") == "MASK"
    assert shut[0]["pbrMetallicRoughness"]["baseColorFactor"][3] == 0.0
    lit = [m for m in mats if m.get("emissiveFactor") and max(m["emissiveFactor"]) > 0]
    assert len(lit) == 1 and lit[0]["name"].endswith("_Face"), [m["name"] for m in mats]
