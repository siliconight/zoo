"""A wall module with a room face (1.38.0).

Cold run 9120, finding 3: stone inside the gas station. An exterior wall in an
outside-only finish now carries `material_in` (Deli Counter 0.166.0), and the
module builds its room face -- local -Y, measured through Deli Counter's
placement basis on all four facings -- in it. Held: the room face is in the
stem and the key, so the one- and two-material walls are two builds; a kind
nobody knows is dropped; and built, every structure face pointing -Y on the -Y
half is the interior finish and every face pointing +Y is the wall's, the
opening's jambs included.
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import kit


def _slot(**kw):
    s = {"slot_id": "ext_0_N_seg0", "role": "wall", "size_mod": "full", "style": 1,
         "material": "stone", "material_in": "drywall",
         "fit": {"dims": [2.0, 0.3, 3.9], "pivot": "center"}}
    s.update(kw)
    return s


def test_the_room_face_is_its_own_build():
    plan = kit.plan_kit({"building_id": "t", "slots": [_slot(), _slot(slot_id="b", material_in=None)]},
                        theme="delco_1997", style=1)
    stems = sorted(m["stem"] for m in plan["modules"])
    assert stems == ["wall_delco_1997_01_w200_mstone", "wall_delco_1997_01_w200_mstone_idrywall"]


def test_an_unknown_kind_or_a_volume_carries_no_room_face():
    plan = kit.plan_kit({"building_id": "t", "slots": [
        _slot(material_in="not_a_kind"),
        {"slot_id": "p", "role": "prop", "size_mod": "full", "style": 1, "material_in": "drywall",
         "fit": {"dims": [1.0, 1.0, 1.0], "pivot": "center"}}]}, theme="delco_1997", style=1)
    assert all("_i" not in m["stem"].split("_mstone")[-1] for m in plan["modules"])
    assert all(not m.get("material_in") for m in plan["modules"])


@pytest.mark.parametrize("role,openings", [("wall", []),
                                           ("window", [{"kind": "window", "width": 1.2,
                                                        "height": 1.2, "sill": 0.9}])])
def test_bpy_the_minus_y_face_is_the_room_and_the_plus_y_face_is_the_wall(tmp_path, role, openings):
    bpy = pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    slot = _slot(role=role)
    slot["fit"]["openings"] = openings
    if role == "window":
        slot["fit"]["dims"] = [2.0, 0.3, 3.0]      # inside the window genome's height range
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    room = wall = jamb = 0
    for o in bpy.context.scene.objects:
        if o.type != "MESH" or o.name.endswith(_COL_SUFFIXES) or "Glass" in o.name:
            continue
        names = [m.name for m in o.data.materials]
        for poly in o.data.polygons:
            mat = names[poly.material_index]
            if poly.normal.y < -0.9 and poly.center.y < 0.0:
                room += 1
                assert "drywall" in mat, (o.name, mat)
            elif poly.normal.y > 0.9:
                wall += 1
                assert "drywall" not in mat, (o.name, mat)
            elif abs(poly.normal.y) < 0.1:
                jamb += 1
                assert "drywall" not in mat, (o.name, mat)
    assert room and wall and jamb
