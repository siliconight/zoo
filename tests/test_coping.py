"""A parapet's coping (1.146.0; Patina >= 0.33.0, the factory's roadmap 324).

Patina plans one ``coping`` a parapet run -- ``size2`` = [length, width] in
plan, overhang and corners included -- and the roofline ``edge_strip``s it
replaces are gone from the manifest. Zoo stands a 10 cm solid on the parapet's
top, sunk 5 mm into it, in the covers' own concrete, so on a side that has a
base course it joins that side's mesh at no extra draw. The pure halves run
anywhere; the merge and the solid's extent are measured under Blender.
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dressing as D
from zoo_keeper.core import genome

SPACE = "spec/Blender Z-up raw coords"
TOP = 8.3                                  # bank_branch_a02's parapet top
# Patina 0.33.0's plan for bank_branch_a02 (its slots.json): N and S over the
# corners, E and W between their overhangs.
COPINGS = (((0.0, 10.9), (1.0, 0.0), 30.1, 0.3), ((14.9, 0.0), (0.0, 1.0), 21.5, 0.3),
           ((0.0, -10.9), (1.0, 0.0), 30.1, 0.3), ((-14.9, 0.0), (0.0, 1.0), 21.5, 0.3))
WALLS = (((0, 1, 0), (0.0, 11.0)), ((0, -1, 0), (0.0, -11.0)),
         ((1, 0, 0), (15.0, 0.0)), ((-1, 0, 0), (-15.0, 0.0)))


def _order(cover, pos, normal, size=1.0, **kw):
    o = {"cover": cover, "pos": list(pos), "normal": list(normal), "size": size,
         "collision": "none", "seed_offset": 1,
         "trim_piece": "roof_edge", "uv_region": [0.0, 0.0, 1.0, 1.0]}
    o.update(kw)
    return o


def _manifest():
    orders = [_order("base_course", (x, y, 0.0), n) for n, (x, y) in WALLS]
    for (x, y), (tx, ty), length, width in COPINGS:
        orders.append(_order("coping", (x, y, TOP), (0, 0, 1), size=length,
                             size2=[length, width], tangent=[tx, ty, 0.0]))
    return {"schema": "patina-dressing/1", "building_id": "t_bank",
            "space": SPACE, "orders": orders}


def _plans():
    return D.plan_dressing(_manifest(), genome.load_species("dress_cover"),
                           "delco_1997", TOOL_VERSION)["plans"]


def test_the_coping_stands_on_the_parapet_sunk_into_it():
    """FAILS ON 1.145.0: there was no coping."""
    [(center, size)] = D.coping_parts(30.1, 0.3)
    assert size == pytest.approx((30.1, 0.3, D.COPING_H))
    assert center[2] - size[2] / 2.0 == pytest.approx(-D.COPING_SINK)
    assert center[2] + size[2] / 2.0 == pytest.approx(D.COPING_H - D.COPING_SINK)
    assert D.COPING_H > D._COVER["edge_strip"]["proud"]


def test_each_coping_is_the_covers_concrete_on_its_own_side():
    """The material every other concrete cover on that side wears, and the
    side the run stands on -- so it merges where the strips it replaces did."""
    sides = {}
    for p in _plans():
        if p["order"]["cover"] == "coping":
            assert p["material"] == "concrete"
            sides[p["side"]] = p["order"]["size2"][0]
    assert sides == {"N": 30.1, "E": 21.5, "S": 30.1, "W": 21.5}


def test_bpy_the_copings_add_no_mesh_and_cap_the_ring(tmp_path):
    """Built under Blender: the four copings join their sides' concrete --
    four meshes out, as the base courses make alone -- and the solids reach
    5 cm past the parapet's outer faces and 9.5 cm above its top."""
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build as B
    res = B.build_dressing(_manifest(), str(tmp_path), theme="delco_1997",
                           options={"save_blend": False})
    st = res["merge"]
    assert st and not st["refused"], st
    assert st["parts_in"] == 8
    assert st["meshes_out"] == 4
    vs = [o.matrix_world @ v.co for o in bpy.data.objects if o.type == "MESH"
          for v in o.data.vertices]
    assert max(v.z for v in vs) == pytest.approx(TOP + D.COPING_H - D.COPING_SINK, abs=1e-4)
    assert max(v.x for v in vs) == pytest.approx(15.05, abs=1e-4)
    assert min(v.x for v in vs) == pytest.approx(-15.05, abs=1e-4)
    assert max(v.y for v in vs) == pytest.approx(11.05, abs=1e-4)
