"""A street tree's crown of leaf cards (1.151.0, the factory's roadmap 324).

The walker, 2026-10-30, of the vertical slice: "try the card-based trees". The grown skeleton stays; every faceted
leaf mass at a tip becomes a clump of four cut-out cards in Pixelcoat's foliage pack (>= 0.65.0, whose cutout is
leaves, not discs), each card framing one tile of it. The default crown.
"""
import json
import pathlib

import pytest

from zoo_keeper.core import genome
from zoo_keeper.core import tree_forms as T

_FACTORY = pathlib.Path(__file__).resolve().parents[2]


#: every species `street_tree.py` builds: the generic tree and the five street species Lot plants by name.
#: RETRACTED, KEPT: the first draft of this test asked `street_tree` alone, passed, and the vertical slice's
#: slice-13 build shipped plate crowns unchanged -- Lot plants `honey_locust` and its siblings, each its own
#: genome with its own `crown`.
TREES = ("street_tree", "red_maple", "pin_oak", "honey_locust", "london_plane", "callery_pear")


def test_every_tree_species_defaults_to_leaf_cards():
    """FAILS ON 1.150.0: every tree's default was the faceted volume."""
    for sp in TREES:
        assert genome.load_species(sp)["params"]["crown"] == "leafcards", sp


def test_the_list_is_every_species_the_tree_recipe_builds():
    import pathlib as _p
    rec = _p.Path(genome.__file__).resolve().parents[1] / "recipes"
    builds = {f.stem for f in rec.glob("*.py")
              if f.stem == "street_tree" or "from .street_tree import build" in f.read_text(encoding="utf-8")}
    assert builds == set(TREES), sorted(builds)


def test_a_card_frames_one_foliage_tile():
    """The card's UVs span one tile of the foliage pack, so its ellipse of leaves sits in the card's middle."""
    prof = _FACTORY / "pixelcoat" / "profiles" / "materials" / "foliage_delco.json"
    if not prof.is_file():
        pytest.skip("no Pixelcoat beside this repo to read the foliage profile from")
    d = json.loads(prof.read_text(encoding="utf-8"))
    assert d["meters_per_tile"] == T.LEAF_TILE_M
    assert d["cutout"].get("leaves"), "the foliage cutout is not leaves: a card would show discs"


def test_bpy_each_card_has_its_own_back_lit_from_the_crown_and_the_crown_culls(tmp_path):
    """FAILS ON 1.151.0: one double-sided face a card, lit by its own normal -- seen from behind, Godot flips that
    normal, and on the vertical slice (slice 13b) those cards rendered near black."""
    pytest.importorskip("bpy")
    import json as _json
    import os
    import struct
    import bpy
    from mathutils import Vector
    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import kit
    slot = {"slot_id": "lp", "role": "prop", "size_mod": "full", "style": 1, "species": "london_plane",
            "material": "wood", "fit": {"dims": [5.0, 5.0, 6.5], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    crown = bpy.data.objects["StreetTree_Crown"]
    me = crown.data
    assert crown.get("zoo_own_normals") and len(me.polygons) % 2 == 0
    xs = [v.co for v in me.vertices]
    c = sum(xs, Vector()) / len(xs)
    lo, hi = min(v.z for v in xs), max(v.z for v in xs)
    from zoo_keeper.recipes import street_tree as R
    c.z = (lo + hi) / 2.0 - R.NORMAL_DROP * (hi - lo)
    # mostly up (every corner faces the sky), and leaning out: the horizontal part points away from the centre
    assert all(lp.normal.z > 0.5 for lp in me.loops)
    lean = sum(1 for lp in me.loops
               if (lp.normal.x * (me.vertices[lp.vertex_index].co.x - c.x)
                   + lp.normal.y * (me.vertices[lp.vertex_index].co.y - c.y)) > 0.0)
    assert lean >= 0.97 * len(me.loops), (lean, len(me.loops))
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    mats = {m.get("name"): m for m in _json.loads(raw[20:20 + n])["materials"]}
    foliage = [m for name, m in mats.items() if "foliage" in (name or "")]
    assert foliage and not any(m.get("doubleSided") for m in foliage), foliage
