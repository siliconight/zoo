"""A house's own brick (1.73.0): `brick_brown` and `brick_orange` are kinds.

Pixelcoat (>= 0.57.0) paints them; Deli Counter (>= 0.183.0) builds two of
its rowhome Empties in them. `dna.resolve_module_plan` keeps a slot's material
only when it is in `skins.KNOWN_KINDS` -- a kind absent from it built in the
genome's default and said nothing, which is how `carpet_club` once came out
concrete -- so the kinds are listed here, and a module built in one carries
it in its name.
"""
from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, kit, skins


def _module(material):
    slot = {"slot_id": "ext_0_S_seg0", "role": "wall", "size_mod": "full", "style": 1,
            "material": material, "material_in": "drywall",
            "fit": {"dims": [2.0, 0.3, 3.1], "pivot": "center", "collision": "convex"}}
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)["modules"][0]


def test_both_bricks_are_known_kinds():
    """FAILS ON 1.72.0: neither was."""
    for kind in ("brick_brown", "brick_orange"):
        assert kind in skins.KNOWN_KINDS


def test_a_wall_in_a_house_brick_is_its_own_module_and_keeps_its_kind():
    red, brown, orange = _module("brick"), _module("brick_brown"), _module("brick_orange")
    assert len({red["stem"], brown["stem"], orange["stem"]}) == 3
    assert "_mbrick_brown" in brown["stem"] and "_mbrick_orange" in orange["stem"]
    plan = dna.resolve_module_plan(brown, genome.load_species("wall"), "delco_1997", 1, TOOL_VERSION)
    assert plan["material"] == "brick_brown"
