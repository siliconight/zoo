"""trash_bags: a heap of filled garbage bags (Zoo 1.93.0, roadmap 219 note 11).

The decisions are pure (`core/trash_bag_forms.py`) and tested here without Blender. The built
module -- exact fit, one part, one material, no two faces sharing a plane at every variant -- is
the bpy half at the bottom, skipped without Blender and run inside Blender 5.1 for this change.
"""
import json
import math
import os

import pytest

from zoo_keeper.core import genome, kit
from zoo_keeper.core import trash_bag_forms as TB

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GENOME = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "trash_bags.json")
SLOT = (1.4, 0.8, 0.75)
SIZES = ((0.8, 0.6, 0.5), SLOT, (2.0, 1.2, 1.0))


def _plan(w, d, h, variant=0):
    slot = {"slot_id": "trash_bags_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "trash_bags", "fit": {"dims": [w, d, h], "pivot": "center"}}
    if variant:
        slot["variant"] = variant
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


def test_trash_bags_is_discovered_and_validates():
    assert "trash_bags" in genome.list_species()
    assert genome.validate_genome(genome.load_species("trash_bags")) == []
    plan = _plan(*SLOT)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "trash_bags"


def test_four_heaps_one_a_variant():
    g = json.load(open(_GENOME, encoding="utf-8"))
    assert g["module_variants"] == TB.VARIANTS == 4
    heaps = [TB.heap(*SLOT, variant=v) for v in range(4)]
    assert len({repr(hp) for hp in heaps}) == 4          # four different heaps
    assert TB.heap(*SLOT, variant=5) == TB.heap(*SLOT, variant=1)


@pytest.mark.parametrize("w,d,h", SIZES)
def test_a_heap_is_a_row_on_the_ground_and_more_on_top(w, d, h):
    for v in range(4):
        bags = TB.heap(w, d, h, v)
        # the thrown-on bags rest INTO the row, so their centres sit under half the slot's
        # height: they are told from the row by standing above the middle of the centres' range
        zs = [b["centre"][2] for b in bags]
        mid = (min(zs) + max(zs)) / 2.0
        low = [b for b in bags if b["centre"][2] < mid]
        top = [b for b in bags if b["centre"][2] >= mid]
        assert len(low) >= 2 and len(top) >= 1, (w, d, h, v)
        xs = sorted(b["centre"][0] for b in low)
        assert xs[0] < 0.0 < xs[-1]                       # the row spans the slot's width
        for b in bags:                                    # every bag inside the slot, before the fit
            cx, cy, cz = b["centre"]
            assert abs(cx) <= w / 2.0 and abs(cy) <= d / 2.0 and 0.0 < cz < h, (w, d, h, v, b)


def test_no_two_flat_bottoms_share_a_plane():
    """The bottom row's undersides stand 3 mm apart, so the probe's 2 mm window never sees two of
    them on one plane."""
    bags = TB.heap(*SLOT, variant=0)
    bottoms = sorted(b["centre"][2] - b["radii"][2] * TB.FLAT for b in bags[:3])
    assert all(b2 - b1 >= 0.0029 for b1, b2 in zip(bottoms, bottoms[1:])), bottoms


def test_mostly_black_and_now_and_then_another():
    seen = [b["colour"] for v in range(4) for b in TB.heap(*SLOT, variant=v)]
    assert seen.count("black") > len(seen) // 2
    assert set(seen) <= set(TB.COLOURS)


def test_a_bag_is_pressed_flat_spread_and_gathered():
    radii, seed = (0.2, 0.18, 0.24), 99
    bottom = TB.shape((0.0, 0.0, -0.24), radii, seed)
    assert -0.24 * TB.FLAT - 0.01 < bottom[2] <= -0.24 * TB.FLAT + 1e-9   # squeezed, not clamped
    belly = TB.shape((0.2, 0.0, -0.05), radii, seed)
    assert math.hypot(belly[0], belly[1]) > 0.2 * (1.0 - TB.LUMP)        # spread, give or take a lump
    neck = TB.shape((0.2 * math.sin(0.35), 0.0, 0.24 * math.cos(0.35)), radii, seed)
    assert math.hypot(neck[0], neck[1]) < 0.2 * math.sin(0.35)           # gathered toward the axis


def test_the_shape_is_the_same_every_time():
    p = (0.11, -0.07, 0.15)
    assert TB.shape(p, (0.2, 0.18, 0.24), 7) == TB.shape(p, (0.2, 0.18, 0.24), 7)


# --- bpy: the built module ------------------------------------------------------------------------

def _build(tmp_path, w, d, h, variant=0):
    from zoo_keeper.bpylayer import build as B
    mod = _plan(w, d, h, variant)["modules"][0]
    return B.build_module(mod, str(tmp_path), theme="delco", style=1, options={"save_blend": False})


@pytest.mark.parametrize("w,d,h", SIZES)
def test_bpy_it_fits_its_slot_in_one_part_and_one_material(tmp_path, w, d, h):
    pytest.importorskip("bpy")
    res = _build(tmp_path, w, d, h)
    checks = {c["id"]: c for c in res["report"]["checks"]}
    for cid in ("fit_width", "fit_depth", "fit_height", "fit_pivot", "collision", "wear_colors",
                "parts_named"):
        assert checks[cid]["level"] == "pass", ((w, d, h), checks[cid])
    assert res["facts"]["parts"] == ["TrashBags_Heap"]
    assert len(set(res["facts"]["materials"])) == 1, res["facts"]["materials"]
    g = json.load(open(_GENOME, encoding="utf-8"))
    assert g["budgets"]["tris_lod0"] >= res["facts"]["tris"]


@pytest.mark.parametrize("variant", range(4))
def test_bpy_no_two_faces_share_a_plane(tmp_path, variant):
    """The probe's first heap found one pair: a bag's bottom clamped onto one plane folded two of
    its triangles back to back (`trash_bag_forms.shape` keeps the retraction). Every variant is
    probed."""
    bpy = pytest.importorskip("bpy")
    import mathutils
    import runpy
    import sys
    saved = sys.argv
    sys.argv = ["coplanar_probe.py", "--"]
    try:
        probe = runpy.run_path(os.path.join(_ZOO, "tools", "coplanar_probe.py"))
    finally:
        sys.argv = saved
    _build(tmp_path, *SLOT, variant=variant)
    objs = probe["_visual_meshes"](bpy, bpy.context.scene)
    rows, _n = probe["probe"](bpy, mathutils, objs, 0.002, 1e-6, 1e-3)
    assert rows == [], (variant, rows[:4])
