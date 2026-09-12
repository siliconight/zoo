"""fire_hydrant: minted 2026-09-12 by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_fire_hydrant_is_discovered_and_validates():
    assert "fire_hydrant" in genome.list_species()
    assert genome.validate_genome(genome.load_species("fire_hydrant")) == []


def test_fire_hydrant_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "fire_hydrant_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "fire_hydrant",
        "fit": {"dims": [0.35, 0.35, 0.75], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "fire_hydrant"
