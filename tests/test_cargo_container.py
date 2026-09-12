"""cargo_container: minted 2026-09-12 by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_cargo_container_is_discovered_and_validates():
    assert "cargo_container" in genome.list_species()
    assert genome.validate_genome(genome.load_species("cargo_container")) == []


def test_cargo_container_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "cargo_container_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "cargo_container",
        "fit": {"dims": [2.44, 6.06, 2.59], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "cargo_container"
