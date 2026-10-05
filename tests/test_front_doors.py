"""An Empty's front door: painted per house, and an iron security door (1.72.0).

Deli Counter (>= 0.182.0) authors each Empty's front-door finish and writes it
on the doorway's slot as `door`; it rides in the module's name as
`_e<finish>` and paints the leaf. Patina (>= 0.28.0) orders a
`security_door` where the house has one; it is built here, in the bars' black
iron. The pure halves run anywhere; the leaf's material is read under Blender.
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, doors, genome, kit, skins
from zoo_keeper.core import dressing as D

OPENING = {"kind": "door", "width": 1.0, "height": 2.3, "sill": 0.0}


def _slot(**kw):
    s = {"slot_id": "ext_0_S_open0", "role": "doorway", "size_mod": "full", "style": 1,
         "material": "brick", "fit": {"dims": [1.0, 0.3, 3.1], "pivot": "center",
                                      "openings": [dict(OPENING)], "collision": "convex"}}
    s.update(kw)
    return s


def _module(**kw):
    plan = kit.plan_kit({"building_id": "t", "slots": [_slot(**kw)]}, theme="delco_1997", style=1)
    return plan["modules"][0]


def test_the_finishes_are_known_kinds_in_the_contract_order():
    assert tuple(doors.FINISHES) == ("navy", "oxblood", "green", "black", "white", "stained")
    for kind, _tint in doors.FINISHES.values():
        assert kind in skins.KNOWN_KINDS


def test_a_painted_front_door_is_its_own_module():
    """FAILS ON 1.71.0: the finish reached no name."""
    m = _module(glazing="facade", door="navy")
    assert "_enavy" in m["stem"] and m["door"] == "navy"
    plain = _module(glazing="facade")
    assert plain["stem"] != m["stem"] and "_enavy" not in plain["stem"] and plain.get("door") is None


def test_only_a_facade_doorway_takes_a_finish():
    """The control: an enterable doorway's slot with the field set is unchanged."""
    assert _module(door="navy").get("door") is None
    assert _module(door="purple", glazing="facade").get("door") is None


def test_the_plan_carries_the_finish_to_the_recipe():
    m = _module(glazing="facade", door="oxblood")
    plan = dna.resolve_module_plan(m, genome.load_species("doorway"), "delco_1997", 1, TOOL_VERSION)
    assert plan.get("door") == "oxblood"


def test_the_leaf_is_painted_in_its_finish_and_names_itself_for_it():
    assert doors.leaf_material("navy", (0, 0, 0)) == ("M_Door_navy", (0.13, 0.17, 0.27), "metal_painted")
    assert doors.leaf_material("stained", (0.1, 0.2, 0.3)) == ("M_Door_stained", (0.1, 0.2, 0.3), "wood_panel")
    assert doors.leaf_material(None, (0.1, 0.2, 0.3)) == ("M_Door_wood_panel", (0.1, 0.2, 0.3), "wood_panel")


def test_the_security_door_hangs_in_the_reveal_in_front_of_the_leaf():
    """Every part inside the opening, 2 cm in front of the leaf (set back 8 cm
    from the face) and behind the face but for the lock box's 4 mm."""
    parts = D.security_door_parts(1.0, 2.3)
    for (x, y, z), (sx, sy, sz) in parts:
        assert abs(x) + sx / 2.0 <= 0.5 - 0.004
        assert abs(z) + sz / 2.0 <= 1.15 + 1e-9
        assert y - sy / 2.0 >= -0.08 + 0.019
        assert y + sy / 2.0 <= 0.0045
    uprights = [p for p in parts if p[1][2] > 1.5 and p[1][0] < 0.03]
    assert len(uprights) >= 5


def test_the_security_door_is_the_bars_black_iron():
    order = {"cover": "security_door", "pos": [0, 0, 0], "normal": [0, 1, 0], "size": 1.0,
             "size2": [1.0, 2.3], "collision": "none", "seed_offset": 1}
    plan = D.dress_plan(order, genome.load_species("dress_cover"), "delco_1997",
                        "spec/Blender Z-up raw coords", TOOL_VERSION)
    assert plan["material"] == "metal_painted" and plan["color"] == [round(c, 4) for c in D.IRON_COLOR]


def test_bpy_a_navy_door_s_leaf_is_painted_metal(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build as B
    B.build_module(_module(glazing="facade", door="navy"), str(tmp_path / "out"),
                   theme="delco_1997", style=1, options={"save_blend": False})
    leaves = {o.name: o.data.materials[0].name for o in bpy.data.objects
              if o.type == "MESH" and "Leaf" in o.name}
    assert leaves and all("navy" in m or "metal_painted" in m for m in leaves.values()), leaves
