"""1.142.0 -- the bank's three reads-wrong (the factory's docs/findings/bank_interior/, frame 18), built.

* A glass wall's storefront frames in aluminium (`arch.SF_FRAME_FOR`): the bank's mullions and the band over its glass
  drew in the opaque curtain-wall skin and read as dark brown bars. A brick shop front's frame keeps its brick.
* A vault rack's money (`shelving`'s ``vault`` stock) is one material whatever its denominations, and the rack passes
  its budget at Deli Counter's widest.

The deposit wall's painted steel is a genome change, checked in `test_safe_deposit_boxes.py`. Run the bpy half in
Blender:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_vault_money_and_frames.py'])))"
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import arch, kit


def test_a_glass_wall_is_what_frames_in_aluminium():
    assert arch.SF_FRAME_FOR == {"glass", "glass_facade"}
    assert arch.SF_FRAME_KIND == "metal_painted"          # a building piece: bare steel mirrors the dark room
    assert min(arch.SF_FRAME_RGB) >= 0.6                  # clear anodised, not the bronze it read as


def _clear():
    import bpy
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def _storefront(tmp_path, material):
    import bpy
    from zoo_keeper.bpylayer import build as B
    _clear()
    slot = {"slot_id": "s", "role": "wall", "size_mod": "full", "style": 2, "material": material,
            "glazing": "storefront", "fit": {"dims": [2.0, 0.3, 3.9], "pivot": "center", "openings": [],
                                             "collision": "convex"}}
    m = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)["modules"][0]
    res = B.build_module(m, str(tmp_path / material), theme="delco_1997", style=1, options={"save_blend": False})
    return res, {o.name: o.data.materials[0].name for o in bpy.data.objects
                 if o.type == "MESH" and o.data.materials and not o.name.endswith("-colonly")}


def test_bpy_a_glass_storefront_frames_in_aluminium_and_a_brick_one_in_brick(tmp_path):
    pytest.importorskip("bpy")
    res, mats = _storefront(tmp_path, "glass")
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    frame = {n: m for n, m in mats.items() if any(k in n for k in ("Kick", "Header", "Mullion"))}
    assert len(frame) >= 4, sorted(mats)
    assert set(frame.values()) == {"M_Storefront_frame"}, frame
    _res, mats = _storefront(tmp_path, "brick")
    frame = {n: m for n, m in mats.items() if any(k in n for k in ("Kick", "Header", "Mullion"))}
    assert frame and "M_Storefront_frame" not in frame.values(), frame


def _rack(tmp_path, dims, stock):
    import bpy
    from zoo_keeper.bpylayer import build as B
    _clear()
    slot = {"slot_id": "shelf_cash_0", "role": "prop", "size_mod": "full", "style": 1, "species": "shelving",
            "fit": {"dims": list(dims), "pivot": "center"}}
    if stock:
        slot["stock"] = stock
    m = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)["modules"][0]
    res = B.build_module(m, str(tmp_path / m["stem"]), theme="delco", style=1, options={"save_blend": False})
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")]
    return m, res, meshes


@pytest.mark.parametrize("dims", [(1.2, 0.5, 1.8), (1.8, 0.5, 1.9), (2.4, 0.6, 2.1)])
def test_bpy_a_vault_rack_is_money_on_one_material(tmp_path, dims):
    pytest.importorskip("bpy")
    m, res, meshes = _rack(tmp_path, dims, "vault")
    assert "vault" in m["stem"], m["stem"]
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    stock = [o for o in meshes if o.name.startswith("Shelf_Stock_")]
    assert any(o.name == "Shelf_Stock_notes" for o in stock), sorted(o.name for o in meshes)
    assert {s.material.name for o in stock for s in o.material_slots} == {"M_Shelf_vault_stock"}
    # the frame's two and the money's one
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 3


def test_bpy_an_unstocked_rack_is_the_back_office_it_was(tmp_path):
    pytest.importorskip("bpy")
    m, res, meshes = _rack(tmp_path, (1.8, 0.5, 1.9), None)
    assert "vault" not in m["stem"]
    names = {o.name for o in meshes}
    assert "Shelf_Stock_notes" not in names
    assert any(s.material.name.startswith("M_Shelf_stock_") for o in meshes for s in o.material_slots)
