"""box_truck: minted 2026-09-12 by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_box_truck_is_discovered_and_validates():
    assert "box_truck" in genome.list_species()
    assert genome.validate_genome(genome.load_species("box_truck")) == []


def test_box_truck_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "box_truck_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "box_truck",
        "fit": {"dims": [2.4, 6.0, 2.8], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "box_truck"
