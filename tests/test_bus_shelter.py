"""bus_shelter: minted 2026-09-12 by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_bus_shelter_is_discovered_and_validates():
    assert "bus_shelter" in genome.list_species()
    assert genome.validate_genome(genome.load_species("bus_shelter")) == []


def test_bus_shelter_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "bus_shelter_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "bus_shelter",
        "fit": {"dims": [3.0, 1.5, 2.5], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "bus_shelter"
