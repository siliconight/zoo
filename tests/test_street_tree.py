"""street_tree: minted 2026-09-12 by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_street_tree_is_discovered_and_validates():
    assert "street_tree" in genome.list_species()
    assert genome.validate_genome(genome.load_species("street_tree")) == []


def test_street_tree_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "street_tree_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "street_tree",
        "fit": {"dims": [4.0, 4.0, 6.0], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "street_tree"
