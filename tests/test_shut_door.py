"""An Empty's door is shut (1.61.0).

A doorway tagged `glazing: "facade"` (Deli Counter >= 0.178.0) is filled with a
painted panel leaf; an untagged doorway stays an open frame, as every
enterable building's does. Built under Blender, as `test_storefront.py`
builds; skipped where bpy is absent. The pure half -- that the tag reaches
the plan as `glazing_kind: "glass_facade"` and keeps the module apart --
runs anywhere.
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, kit

DOOR = {"kind": "door", "width": 1.0, "height": 2.3, "sill": 0.0}


def _slot(glazing):
    s = {"slot_id": "ext_0_S_open0", "role": "doorway", "size_mod": "full", "style": 1,
         "material": "brick", "fit": {"dims": [1.6, 0.3, 3.1], "pivot": "center",
                                      "openings": [DOOR], "collision": "convex"}}
    if glazing:
        s["glazing"] = glazing
    return s


def _module(glazing):
    plan = kit.plan_kit({"building_id": "t", "slots": [_slot(glazing)]},
                        theme="delco_1997", style=1)
    return next(m for m in plan["modules"] if not m["stem"].endswith("_open"))


def test_a_tagged_doorway_plans_as_a_facade_opening():
    mod = _module("facade")
    assert mod.get("glazing") == "facade"
    plan = dna.resolve_module_plan(mod, genome.load_species("doorway"), "delco_1997", 1, TOOL_VERSION)
    assert plan.get("glazing_kind") == "glass_facade"


def _built_names(tmp_path, glazing):
    import bpy
    from zoo_keeper.bpylayer import build as B
    B.build_module(_module(glazing), str(tmp_path / "out"), theme="delco_1997", style=1,
                   options={"save_blend": False})
    return {o.name: (o.data.materials[0].name if o.data.materials else None)
            for o in bpy.data.objects if o.type == "MESH"}


def test_bpy_a_facade_doorway_is_shut_and_an_enterable_one_is_not(tmp_path):
    """FAILS ON 1.60.0: no leaf either way."""
    pytest.importorskip("bpy")
    shut = _built_names(tmp_path / "f", "facade")
    leaves = {n: m for n, m in shut.items() if "Leaf" in n}
    # the KIND, not a name: with no skin library the fallback is
    # `M_Door_wood_panel`, with the theme's it is `M_Skin_wood_panel_<theme>`
    assert leaves and all("wood_panel" in (m or "") for m in leaves.values()), shut
    open_ = _built_names(tmp_path / "e", None)
    assert not [n for n in open_ if "Leaf" in n], sorted(open_)
