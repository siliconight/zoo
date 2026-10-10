"""litter_bin: minted 2026-09-12 by tools/new_species.py (roadmap 150) as a placeholder box, and
DRAWN in 1.92.0 (roadmap 219 note 5): a 1990s municipal street bin, one atlas and one material.

The shape and the paint are pure (`core/litter_bin_forms.py`) and tested here without Blender. The
built module -- exact fit, one part, one material, no two faces sharing a plane -- is the bpy half
at the bottom, skipped without Blender and run inside Blender 5.1 for this change.
"""
import os

import pytest

from zoo_keeper.core import card_art, genome, kit
from zoo_keeper.core import litter_bin_forms as LB

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLOT = (0.6, 0.6, 1.0)


def _plan(w, d, h):
    return kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "litter_bin_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "litter_bin", "fit": {"dims": [w, d, h], "pivot": "center"}}]},
        theme="delco", style=1)


def test_litter_bin_is_discovered_and_validates():
    assert "litter_bin" in genome.list_species()
    assert genome.validate_genome(genome.load_species("litter_bin")) == []


def test_litter_bin_plans_at_its_authored_dims():
    plan = _plan(*SLOT)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "litter_bin"


def test_every_prim_is_a_quad_on_the_one_atlas():
    got = LB.plan(*SLOT)
    assert got["facts"]["materials"] == 1
    for p in got["prims"]:
        assert p["mat"] == "paint", p["part"]
        assert p["tile"] in got["tiles"], (p["part"], p["tile"])
    assert got["facts"]["tris"] == 84


def test_the_slot_is_its_lid_and_its_collision_the_whole_body():
    w, d, h = SLOT
    got = LB.plan(w, d, h)
    pts = [v for p in got["prims"] for v in p["verts"]]
    assert min(v[0] for v in pts) == pytest.approx(-w / 2.0)
    assert max(v[0] for v in pts) == pytest.approx(w / 2.0)
    assert min(v[1] for v in pts) == pytest.approx(-d / 2.0)
    assert max(v[1] for v in pts) == pytest.approx(d / 2.0)
    assert min(v[2] for v in pts) == pytest.approx(0.0)
    assert max(v[2] for v in pts) == pytest.approx(h)
    assert got["collision"] == ((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h))


def test_every_tile_paints_and_the_placard_sets():
    """`card_art.paint` sends a `litter_` tile here; the placard's two lines set, and the line is
    the brand rule's invented voice, not a real township's."""
    got = LB.plan(*SLOT)
    for _key, (_mat, spec) in got["tiles"].items():
        c = card_art.paint(spec)
        assert c.w > 0 and c.h > 0, spec["kind"]
        assert getattr(c, "unset", []) == [], (spec["kind"], c.unset)
    assert [t for t, _s in LB.PLACARD_LINES] == ["LITTER", "KEEP DELCO CLASSY-ISH"]


def test_an_unknown_tile_is_refused():
    with pytest.raises(ValueError):
        LB.paint({"kind": "litter_nothing", "w_m": 0.1, "h_m": 0.1})


# --- bpy: the built module ------------------------------------------------------------------------

def _build(tmp_path, w, d, h):
    from zoo_keeper.bpylayer import build as B
    mod = _plan(w, d, h)["modules"][0]
    return B.build_module(mod, str(tmp_path), theme="delco", style=1, options={"save_blend": False})


@pytest.mark.parametrize("w,d,h", ((0.48, 0.48, 0.8), SLOT, (0.78, 0.78, 1.3)))
def test_bpy_it_fits_its_slot_in_one_part_and_one_material(tmp_path, w, d, h):
    pytest.importorskip("bpy")
    res = _build(tmp_path, w, d, h)
    checks = {c["id"]: c for c in res["report"]["checks"]}
    for cid in ("fit_width", "fit_depth", "fit_height", "fit_pivot", "collision", "uvs", "parts_named"):
        assert checks[cid]["level"] == "pass", ((w, d, h), checks[cid])
    assert "LitterBin_Art" in res["facts"]["parts"]
    assert len(set(res["facts"]["materials"])) == 1, res["facts"]["materials"]


@pytest.mark.parametrize("w,d,h", ((0.48, 0.48, 0.8), SLOT, (0.78, 0.78, 1.3)))
def test_bpy_no_two_faces_share_a_plane(tmp_path, w, d, h):
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
    _build(tmp_path, w, d, h)
    objs = probe["_visual_meshes"](bpy, bpy.context.scene)
    rows, _n = probe["probe"](bpy, mathutils, objs, 0.002, 1e-6, 1e-3)
    assert rows == [], ((w, d, h), rows[:4])
