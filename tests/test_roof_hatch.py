"""roof_hatch: the curb and lid that stand around a roof ladder's opening (factory roadmap 170).

Pure: the genome, the plan, and the state the lid is this species' own art for.
"""
from zoo_keeper.core import genome, kit


def test_roof_hatch_is_discovered_and_validates():
    assert "roof_hatch" in genome.list_species()
    g = genome.load_species("roof_hatch")
    assert genome.validate_genome(g) == []
    assert g["license"]["construction_knowledge"] == "CC0"


def test_the_lid_is_the_species_own_state_art():
    """Deli Counter's `hatch` machine maps both states to this species; without `state_art`
    Zoo would defer `closed` as identical art and the lid could never shut."""
    assert kit.state_art_for("roof_hatch") == frozenset({"closed"})


def _slot(state_geometry=None):
    slot = {"slot_id": "roof_hatch_13_-9", "role": "prop", "size_mod": "full", "style": 1,
            "species": "roof_hatch", "material": "metal",
            "fit": {"dims": [1.66, 1.66, 0.2], "pivot": "center", "collision": "none"}}
    if state_geometry is not None:
        slot["interactive"] = {"id": "b:if:00000000", "kind": "hatch",
                               "states": ["open", "closed"], "default": "open",
                               "state_geometry": state_geometry,
                               "collision_per_state": {"open": False, "closed": True}}
    return slot


def test_roof_hatch_plans_at_deli_counters_dims():
    """1.5 m hole + 0.08 m curb a side (deli_counter/roof_hatch.py), 0.2 m tall."""
    plan = kit.plan_kit({"building_id": "t", "slots": [_slot()]}, theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "roof_hatch"


def test_an_interactive_hatch_builds_its_closed_lid_too():
    """The slot's machine maps both states to roof_hatch; the closed variant is built, not deferred."""
    variants = list(kit.slot_variants(
        _slot({"open": "roof_hatch", "closed": "roof_hatch"}), "roof_hatch",
        state_art=lambda sp: kit.state_art_for(sp)))
    states = [(v[0], v[1], v[3]) for v in variants]
    assert ("roof_hatch", None, False) in states
    assert ("roof_hatch", "closed", False) in states
