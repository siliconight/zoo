"""A building's covers merge one SIDE at a time (1.68.0).

Patina's covers reached the level as one mesh each. Measured on cold run
9154's package: 3,370 cover instances in gas_block_001, and hiding them all
took the worst view from 8,690 draws / 27.33 ms p95 to 5,571 / 17.74 ms.
They merge now -- per side of the building, per material, never per
building: the export culls by occlusion, and one mesh holding a building's
front and back covers keeps the back drawn whenever the front is seen.

The side is decided here, pure: a wall-facing cover by its normal, an
up-facing one -- a curb at the wall's foot, an edge strip on the roof -- by
where it stands. Built under Blender the groups become meshes; that half is
skipped where bpy is absent.
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dressing, genome

# A rowhome's footprint, 6.3 m by 12.3 m, in Deli Counter's facings:
# N = +y, E = +x, S = -y, W = -x -- read off `ext_<storey>_<facing>_*` slot
# ids against their own orders' normals in cold run 9154's manifests.
HX, HY = 3.15, 6.15
WALLS = (((0, 1, 0), (0.0, HY)), ((0, -1, 0), (0.0, -HY)),
         ((1, 0, 0), (HX, 0.0)), ((-1, 0, 0), (-HX, 0.0)))


def _order(cover, pos, normal, size=1.0, **kw):
    o = {"cover": cover, "pos": list(pos), "normal": list(normal), "size": size,
         "collision": "none", "seed_offset": 1,
         "trim_piece": "flashing", "uv_region": [0.0, 0.0, 1.0, 1.0]}
    o.update(kw)
    return o


def _manifest():
    orders = []
    for normal, (x, y) in WALLS:            # a base course and a gutter a wall
        orders.append(_order("base_course", (x, y, 0.0), normal))
        orders.append(_order("gutter_run", (x, y, 8.92), normal))
    # a downspout front and back, as Patina 0.25.0 orders them
    orders.append(_order("downspout", (-3.0, HY, 4.4), (0, 1, 0), size=8.85))
    orders.append(_order("downspout", (-3.0, -HY, 4.4), (0, -1, 0), size=8.85))
    # up-facing: a curb ring at the foot and an edge-strip ring on the roof
    for z, cover in ((0.0, "curb"), (9.0, "edge_strip")):
        for x in (-2.5, 0.0, 2.5):
            orders.append(_order(cover, (x, HY + 0.2, z), (0, 0, 1), tangent=[1, 0, 0]))
            orders.append(_order(cover, (x, -HY - 0.2, z), (0, 0, 1), tangent=[1, 0, 0]))
        for y in (-5.0, -2.5, 0.0, 2.5, 5.0):
            orders.append(_order(cover, (HX + 0.2, y, z), (0, 0, 1), tangent=[0, 1, 0]))
            orders.append(_order(cover, (-HX - 0.2, y, z), (0, 0, 1), tangent=[0, 1, 0]))
    return {"schema": "patina-dressing/1", "building_id": "t_row",
            "space": "spec/Blender Z-up raw coords", "orders": orders}


def _plan():
    return dressing.plan_dressing(_manifest(), genome.load_species("dress_cover"),
                                  "delco_1997", TOOL_VERSION)


def test_every_cover_plan_names_its_side():
    """FAILS ON 1.67.0: a plan carried no side."""
    plans = _plan()["plans"]
    assert plans and all(p["side"] in dressing.SIDES for p in plans)


def test_a_wall_cover_takes_the_side_its_normal_leaves():
    want = {(0, 1): "N", (0, -1): "S", (1, 0): "E", (-1, 0): "W"}
    walls = [p for p in _plan()["plans"] if abs(p["order"]["normal"][2]) < 0.5]
    assert len(walls) == 10
    for p in walls:
        n = p["order"]["normal"]
        assert p["side"] == want[(round(n[0]), round(n[1]))], (p["order"]["cover"], n)


def test_an_up_facing_cover_takes_the_side_it_stands_nearest():
    """Measured in units of the footprint's half-size, so a long building's
    end curbs go to its end and not its flank."""
    box = (0.0, 0.0, HX, HY)
    assert dressing.cover_side((0, 0, 1), (0.0, HY + 0.2, 0.0), box) == "N"
    assert dressing.cover_side((0, 0, 1), (2.5, -HY - 0.2, 9.0), box) == "S"
    assert dressing.cover_side((0, 0, 1), (-HX - 0.2, -5.0, 9.0), box) == "W"
    # (3.35, 5.0): in raw metres 5.0 along y beats 3.35 across x and would say
    # N; against the half-sizes it is 1.06 out on x and 0.81 on y -- the flank
    assert dressing.cover_side((0, 0, 1), (HX + 0.2, 5.0, 0.0), box) == "E"


def test_the_ground_ring_and_the_roof_ring_split_four_ways():
    """Grouped by normal alone, every curb and roof edge of a building would
    be one group -- a mesh the size of the building, drawn whenever any of
    it is. 32 of these 42 covers face up; a real rowhome's are 60 of 103."""
    up = [p for p in _plan()["plans"] if p["order"]["cover"] in ("curb", "edge_strip")]
    assert len(up) == 32
    assert {p["side"] for p in up} == set(dressing.SIDES)


def test_a_side_gathers_every_cover_on_it_whatever_its_kind():
    """The group is the side, not the cover kind: the north wall's base
    course, the curbs and roof edges at the north end, and the north gutter
    and downspout are the north side's two groups, concrete and metal."""
    north = {}
    for p in _plan()["plans"]:
        if p["side"] == "N":
            north.setdefault(p["material"], set()).add(p["order"]["cover"])
    assert north == {"concrete": {"base_course", "curb", "edge_strip"},
                     "metal_painted": {"gutter_run", "downspout"}}, north


def test_footprint_is_the_box_the_covers_stand_in():
    assert dressing.footprint([(-1.0, -2.0, 0.0), (3.0, 4.0, 9.0)]) == (1.0, 1.0, 2.0, 3.0)
    # one cover still decides, rather than dividing by zero
    one = dressing.footprint([(0.0, 0.0, 0.0)])
    assert dressing.cover_side((0, 0, 1), (0.0, 0.0, 0.0), one) in dressing.SIDES


def test_bpy_one_mesh_a_side_per_material(tmp_path):
    """Built under Blender: every cover goes into the merge (none refused for
    a transform -- they are built in place), and what comes out is one mesh
    per (side, material)."""
    pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build as B
    res = B.build_dressing(_manifest(), str(tmp_path), theme="delco_1997",
                           options={"save_blend": False})
    st = res["merge"]
    assert st and not st["refused"], st
    plans = _plan()["plans"]
    assert st["parts_in"] == len(plans) == 42
    assert st["meshes_out"] == len({(p["side"], p["material"]) for p in plans}) == 8
