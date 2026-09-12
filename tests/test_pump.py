"""pump: minted 2026-09-12 by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_pump_is_discovered_and_validates():
    assert "pump" in genome.list_species()
    assert genome.validate_genome(genome.load_species("pump")) == []


def test_pump_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "pump_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "pump",
        "fit": {"dims": [1.0, 1.2, 1.4], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "pump"
