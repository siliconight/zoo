"""An Empty's shut front door has panels and a knob (1.124.0). The walker, walking cold run 9386: "many of the
rowhome doors dont have doorknobs?" -- the leaf was one flat box.

The pure half holds the sizes; the bpy half builds a facade doorway and finds the hardware where a hand would reach
it. It skips without Blender and was run inside Blender 5.1.1 for this change, from the repo root:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_door_hardware.py'])))"
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import doors as A


def test_the_knob_is_where_a_hand_reaches_it():
    assert 0.85 <= A.KNOB_Z <= 1.05
    assert 0.05 <= A.KNOB_FROM_EDGE <= 0.09
    assert A.SINK > 0.0 and A.PANEL_PROUD > A.SINK
    name, colour, kind = A.HARDWARE
    assert name.startswith("M_Door_hardware") and kind == "metal_painted"


@pytest.mark.parametrize("finish", [None, "navy", "stained"])
def test_bpy_a_facade_door_has_panels_and_a_knob(finish, tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.core import kit
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    slot = {"slot_id": "d", "role": "doorway", "size_mod": "full", "style": 1, "material": "brick",
            "glazing": "facade",
            "fit": {"dims": [2.0, 0.3, 3.3], "pivot": "center",
                    "openings": [{"kind": "door", "width": 1.0, "height": 2.2, "sill": 0.0}],
                    "collision": "convex"}}
    if finish:
        slot["door"] = finish
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    B.build_module(plan["modules"][0], str(tmp_path / "out"), theme="delco_1997", style=1,
                   options={"save_blend": False})
    names = [o.name for o in bpy.data.objects if o.type == "MESH"]
    hw = [o for o in bpy.data.objects if o.type == "MESH" and o.name.endswith("_LeafHardware")]
    panels = [o for o in bpy.data.objects if o.type == "MESH" and o.name.endswith("_LeafPanels")]
    assert hw and panels, names
    assert hw[0].data.materials[0].name == A.HARDWARE[0]


def test_the_hardware_is_the_stoop_railings_own_iron():
    """1.127.0: the knob shares the railing's material, so a front with a stoop merges it (FAILS ON 1.126.0)."""
    import json
    import os
    g = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zoo_keeper",
                                    "genome", "species", "stoop_railing.json"), encoding="utf-8"))
    name, colour, kind = A.HARDWARE
    assert kind == g["materials"]["default"] == "metal_painted"
    assert {tuple(s["color"]) for s in g["styles"].values()} == {tuple(colour)}, (colour, g["styles"])
