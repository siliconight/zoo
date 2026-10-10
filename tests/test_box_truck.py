"""box_truck: minted 2026-09-12 by tools/new_species.py (roadmap 150) as a placeholder box, and
DRAWN in 1.92.0 (roadmap 219 note 5): a 1990s cab-over delivery truck in one of four invented
Delco fleets.

The decisions are pure (`core/box_truck_forms.py`) and tested here without Blender. The built
module -- exact fit, every part, no two faces sharing a plane, the triangle budget, five materials
-- is the bpy half at the bottom, skipped without Blender and run inside Blender 5.1 for this
change.
"""
import json
import os

import pytest

from zoo_keeper.core import box_truck_forms as BT
from zoo_keeper.core import genome, kit

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GENOME = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "box_truck.json")
SLOT = (2.4, 6.0, 2.8)


def _plan(w, d, h, variant=0):
    slot = {"slot_id": "box_truck_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "box_truck", "fit": {"dims": [w, d, h], "pivot": "center"}}
    if variant:
        slot["variant"] = variant
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


def test_box_truck_is_discovered_and_validates():
    assert "box_truck" in genome.list_species()
    assert genome.validate_genome(genome.load_species("box_truck")) == []


def test_box_truck_plans_at_its_authored_dims():
    plan = _plan(*SLOT)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "box_truck"


# --- the shape, without Blender ------------------------------------------------------------------

def test_the_slot_is_its_mirrors_bumpers_and_lamps():
    """Width is the mirror heads, depth the bumpers, height the clearance lamps: the box stands
    inside the width by BOX_OUT, the cab by MIRROR_OUT, the roof under the height by ROOF_LAMP."""
    w, d, h = SLOT
    lay = BT.layout(w, d, h)
    assert lay["y0"] == pytest.approx(-d / 2.0) and lay["yt"] == pytest.approx(d / 2.0)
    assert lay["hb"] == pytest.approx(w / 2.0 - BT.BOX_OUT)
    assert lay["hc"] == pytest.approx(w / 2.0 - BT.MIRROR_OUT)
    assert lay["z_box1"] == pytest.approx(h - BT.ROOF_LAMP)


def test_a_cab_over_sits_over_its_front_wheels_and_under_its_box():
    for w, d, h in (SLOT, (1.92, 4.8, 2.24), (3.0, 7.5, 3.5)):
        lay = BT.layout(w, d, h)
        assert lay["y_n"] < lay["ya_f"] < lay["y_c"], (w, d, h)        # the front axle under the cab
        assert lay["y_b"] < lay["ya_r"] < lay["y_r"], (w, d, h)        # the rear axle under the box
        assert lay["z_cab1"] < lay["z_box1"], (w, d, h)                # the box towers over the cab
        assert lay["hc"] < lay["hb"], (w, d, h)                        # and is wider


def test_it_is_cover_all_along_its_length():
    """Lot parks it across a lane (roadmap 22): solid taller than 1.3 m from end to end. The cab
    and the box both stand higher than that at every size the genome allows."""
    for w, d, h in ((1.92, 4.8, 2.24), SLOT, (3.0, 7.5, 3.5)):
        lay = BT.layout(w, d, h)
        assert lay["z_cab1"] > 1.3 and lay["z_box1"] > 1.3, (w, d, h)


def test_a_longer_slot_is_a_longer_box_behind_the_same_cab():
    a, b = BT.layout(2.4, 6.0, 2.8), BT.layout(2.4, 7.5, 2.8)
    assert (a["y_c"] - a["y_n"]) == pytest.approx(b["y_c"] - b["y_n"])
    assert (b["y_r"] - b["y_b"]) > (a["y_r"] - a["y_b"])


def test_the_cabs_plan_corners_are_round():
    lay = BT.layout(*SLOT)
    assert BT.cab_half_width(lay, lay["y_n"]) == pytest.approx(lay["hc"] - BT.CAB_ROUND)
    assert BT.cab_half_width(lay, lay["y_n"] + BT.CAB_ROUND) == pytest.approx(lay["hc"])
    assert BT.cab_half_width(lay, lay["y_ws"]) == pytest.approx(lay["hc"])   # the pillars stand on it


# --- the fleets -----------------------------------------------------------------------------------

#: Marks a delivery truck in the 1990s would really have carried. None may appear: the brand
#: rule is invented Delco names only.
REAL = ("U-HAUL", "UHAUL", "RYDER", "PENSKE", "BUDGET", "WAWA", "TASTYKAKE", "YUENGLING",
        "EAGLES", "ISUZU", "CHEVROLET", "CHEVY", "GMC", "FORD", "MACK", "FEDEX", "UPS")


def test_four_fleets_four_variants_each_its_own():
    g = json.load(open(_GENOME, encoding="utf-8"))
    assert g["module_variants"] == len(BT.FLEETS) == 4
    assert len({f["id"] for f in BT.FLEETS}) == 4
    assert len({f["cab"] for f in BT.FLEETS}) == 4
    assert [BT.fleet(v)["id"] for v in range(8)] == [f["id"] for f in BT.FLEETS] * 2


def test_no_fleet_carries_a_real_mark():
    for f in BT.FLEETS:
        words = " ".join(t for t, _cap in f["lines"]).upper()
        for mark in REAL:
            assert mark not in words.split() and mark + "'S" not in words, (f["id"], mark)


def test_every_fleets_livery_sets():
    """`livery_art` raises when a line does not set; every line of every fleet sets, and the art
    is named for what it is, so the four are four images."""
    names = set()
    for v in range(len(BT.FLEETS)):
        art = BT.livery_art(v)
        assert art["size"] == BT.LIVERY_PX
        assert len(art["lines"]) == len(BT.fleet(v)["lines"])
        assert art["png"][:8] == b"\x89PNG\r\n\x1a\n"
        names.add(art["name"])
    assert len(names) == 4


def test_the_livery_lands_on_the_boxs_sides_and_nowhere_else():
    lay = BT.layout(*SLOT)
    yc, zc = BT.livery_centre(lay)
    for nx in (1.0, -1.0):
        u, v = BT.livery_uv((nx * lay["hb"], yc, zc), (nx, 0.0, 0.0), lay)
        assert u == pytest.approx(0.5) and v == pytest.approx(0.5)
    # read the right way round from outside on either side: forward is further along the art
    # on the +X side and back along it on the -X side
    u_pos, _ = BT.livery_uv((lay["hb"], yc + 0.5, zc), (1.0, 0.0, 0.0), lay)
    u_neg, _ = BT.livery_uv((-lay["hb"], yc + 0.5, zc), (-1.0, 0.0, 0.0), lay)
    assert u_pos > 0.5 > u_neg
    # the cab's side, the box's roof and its rear door take the white margin
    assert BT.livery_uv((lay["hc"], lay["y_n"] + 0.8, 1.2), (1.0, 0.0, 0.0), lay) == BT.LIVERY_OUTSIDE
    assert BT.livery_uv((0.0, yc, lay["z_box1"]), (0.0, 0.0, 1.0), lay) == BT.LIVERY_OUTSIDE
    assert BT.livery_uv((0.0, lay["y_r"], zc), (0.0, 1.0, 0.0), lay) == BT.LIVERY_OUTSIDE


def test_the_cab_wears_its_fleets_colour_exactly():
    """The cab samples the art's margin, the box's own white; its corner colour is set against
    that white, so their product is the fleet's colour. High on the cab, out of the grime."""
    lay = BT.layout(*SLOT)
    for v, f in enumerate(BT.FLEETS):
        rgb = BT.finish_rgb((0.0, lay["y_n"] + 0.8, lay["z_cab1"] - 0.05), (0.0, 0.0, 1.0), lay, v)
        margin = [BT._srgb_to_lin(c) for c in BT.BOX_WHITE]
        want = [BT._srgb_to_lin(c) for c in f["cab"]]
        for got_c, m, w_c in zip(rgb, margin, want):
            assert got_c * m == pytest.approx(w_c, rel=1e-6), (f["id"], rgb)
            assert 0.0 <= got_c < 1.0


def test_grime_rises_from_the_road():
    lay = BT.layout(*SLOT)
    low = BT.finish_rgb((lay["hb"], 0.5, lay["z_box0"] + 0.02), (1.0, 0.0, 0.0), lay, 0)
    high = BT.finish_rgb((lay["hb"], 0.5, lay["z_box1"] - 0.6), (1.0, 0.0, 0.0), lay, 0)
    assert sum(low) < sum(high)


# --- bpy: the built module ------------------------------------------------------------------------

#: Measured through the kit path at the genome's default slot, 1.92.0 (see CHANGELOG).
TRI_BUDGET = 8800
PARTS = ("BoxTruck_Body", "BoxTruck_Trim", "BoxTruck_Tyres", "BoxTruck_Bright", "BoxTruck_Headlamps",
         "BoxTruck_AmberLamps", "BoxTruck_TailLamps", "BoxTruck_Plate", "BoxTruck_Wheels",
         "BoxTruck_Interior", "BoxTruck_Chassis", "BoxTruck_Windshield", "BoxTruck_DoorGlass_L",
         "BoxTruck_DoorGlass_R")


def _build(tmp_path, w, d, h, variant=0):
    from zoo_keeper.bpylayer import build as B
    mod = _plan(w, d, h, variant)["modules"][0]
    return B.build_module(mod, str(tmp_path), theme="delco", style=1, options={"save_blend": False})


@pytest.mark.parametrize("w,d,h", ((1.92, 4.8, 2.24), SLOT, (3.0, 7.5, 3.5)))
def test_bpy_it_fits_its_slot_with_every_part(tmp_path, w, d, h):
    pytest.importorskip("bpy")
    res = _build(tmp_path, w, d, h)
    checks = {c["id"]: c for c in res["report"]["checks"]}
    for cid in ("fit_width", "fit_depth", "fit_height", "fit_pivot", "collision", "wear_colors",
                "uvs", "parts_named"):
        assert checks[cid]["level"] == "pass", ((w, d, h), checks[cid])
    assert set(PARTS) <= set(res["facts"]["parts"])
    assert res["facts"]["tris"] <= TRI_BUDGET, res["facts"]["tris"]
    g = json.load(open(_GENOME, encoding="utf-8"))
    assert g["budgets"]["tris_lod0"] >= res["facts"]["tris"]


def test_bpy_five_materials_five_draws(tmp_path):
    pytest.importorskip("bpy")
    res = _build(tmp_path, *SLOT, variant=2)
    mats = set(res["facts"]["materials"])
    assert len(mats) == 5, mats
    assert any("nanas_basement" in m for m in mats), mats


@pytest.mark.parametrize("w,d,h", ((1.92, 4.8, 2.24), SLOT, (3.0, 7.5, 3.5)))
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
