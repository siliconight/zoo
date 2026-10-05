"""An Empty's roof: a TV antenna, and on the odd house a satellite dish (1.74.0).

Deli Counter (>= 0.185.0) authors which houses have them and writes them on
the roof slot with the house's front; Patina (>= 0.29.0) orders them on the
roof, set back from the front parapet, with the antenna's boom toward the
transmitter and the dish's bowl toward the satellite as the order's tangent.
Built here in the gutters' white aluminium, so on a side that has gutters
they merge into that side's metal mesh at no extra draw. The pure halves run
anywhere; the merge is counted under Blender.
"""
import math

import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dressing as D
from zoo_keeper.core import genome

SPACE = "spec/Blender Z-up raw coords"
HX, HY = 3.15, 6.15
WALLS = (((0, 1, 0), (0.0, HY)), ((0, -1, 0), (0.0, -HY)),
         ((1, 0, 0), (HX, 0.0)), ((-1, 0, 0), (-HX, 0.0)))


def _order(cover, pos, normal, size=1.0, **kw):
    o = {"cover": cover, "pos": list(pos), "normal": list(normal), "size": size,
         "collision": "none", "seed_offset": 1,
         "trim_piece": "frame", "uv_region": [0.0, 0.0, 1.0, 1.0]}
    o.update(kw)
    return o


def _roof_orders():
    # set back from the south (front) parapet, as Patina orders them
    return [_order("tv_antenna", (0.5, -4.2, 9.3), (0, 0, 1), size=2.0,
                   size2=[2.0, 2.8], tangent=[-0.574, 0.819, 0.0]),
            _order("sat_dish", (-1.2, -5.0, 9.3), (0, 0, 1), size=0.5,
                   size2=[0.5, 1.2], tangent=[-0.515, -0.857, 0.0])]


def _manifest():
    orders = []
    for normal, (x, y) in WALLS:            # a base course and a gutter a wall
        orders.append(_order("base_course", (x, y, 0.0), normal))
        orders.append(_order("gutter_run", (x, y, 8.92), normal))
    return {"schema": "patina-dressing/1", "building_id": "t_row",
            "space": SPACE, "orders": orders + _roof_orders()}


def _plans():
    return D.plan_dressing(_manifest(), genome.load_species("dress_cover"),
                           "delco_1997", TOOL_VERSION)["plans"]


def test_the_antenna_and_dish_are_the_gutters_white_aluminium():
    """FAILS ON 1.73.0: neither was painted metal, so each would have been a
    surface of its own in the style's concrete."""
    for p in _plans():
        if p["order"]["cover"] in ("tv_antenna", "sat_dish"):
            assert p["material"] == "metal_painted"
            assert p["color"] == [round(c, 4) for c in D.METAL_COLOR]


def test_they_join_the_front_side_and_its_gutter():
    """Up-facing, they take the side they stand nearest: set back from the
    front parapet, that is the front, whose gutter is the same material."""
    groups = {}
    for p in _plans():
        groups.setdefault((p["side"], p["material"]), set()).add(p["order"]["cover"])
    assert groups[("S", "metal_painted")] == {"gutter_run", "tv_antenna", "sat_dish"}


def test_the_antenna_stands_on_the_roof_and_tapers_toward_the_transmitter():
    parts = D.antenna_parts(2.0, 2.8)
    assert min(z - sz / 2.0 for (_x, _y, z), (_sx, _sy, sz) in parts) == pytest.approx(0.001)
    assert max(z + sz / 2.0 for (_x, _y, z), (_sx, _sy, sz) in parts) == pytest.approx(2.8)
    elements = [p for p in parts if p[1][0] == D.ANT_ELEMENT]
    assert len(elements) == 10
    xs = [c[0] for c, _s in elements]
    spans = [s[1] for _c, s in elements]
    assert xs == sorted(xs) and spans == sorted(spans, reverse=True)
    assert spans[0] == pytest.approx(D.ANT_LONG) and spans[-1] == pytest.approx(D.ANT_SHORT)
    boom = [p for p in parts if p[1][0] == pytest.approx(2.0)]
    assert len(boom) == 1 and boom[0][0][0] > 0.0      # more of it ahead of the mast


def test_the_mast_overlaps_its_plate_rather_than_sharing_a_face():
    plate, mast = D.antenna_parts(2.0, 2.8)[:2]
    plate_top = plate[0][2] + plate[1][2] / 2.0
    mast_foot = mast[0][2] - mast[1][2] / 2.0
    assert mast_foot == pytest.approx(plate_top - 0.001)


def test_the_dish_stands_clear_of_the_roof_and_looks_ahead():
    mount, head, bc = D.dish_parts(1.2)
    assert bc[2] == pytest.approx(1.2) and bc[0] > 0.0
    assert min(z - sz / 2.0 for (_x, _y, z), (_sx, _sy, sz) in mount) == pytest.approx(0.001)
    t = math.radians(D.DISH_TILT)
    rx, _ry, rz = D.DISH_R
    assert bc[2] - math.hypot(rx * math.sin(t), rz * math.cos(t)) > 0.5
    lnb = max(head, key=lambda p: p[0][0])
    assert lnb[0][0] == pytest.approx(D.DISH_FOCUS)


def test_bpy_the_roof_fixtures_add_no_mesh(tmp_path):
    """Built under Blender: the antenna and dish go into the merge with
    everything else, and the meshes out are the same eight -- four sides by
    concrete and metal -- that the walls' covers make without them."""
    pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build as B
    res = B.build_dressing(_manifest(), str(tmp_path), theme="delco_1997",
                           options={"save_blend": False})
    st = res["merge"]
    assert st and not st["refused"], st
    assert st["parts_in"] == len(_plans()) == 10
    assert st["meshes_out"] == 8
