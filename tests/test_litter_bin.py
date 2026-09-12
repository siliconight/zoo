"""litter_bin: minted 2026-09-12 by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_litter_bin_is_discovered_and_validates():
    assert "litter_bin" in genome.list_species()
    assert genome.validate_genome(genome.load_species("litter_bin")) == []


def test_litter_bin_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "litter_bin_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "litter_bin",
        "fit": {"dims": [0.6, 0.6, 1.0], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "litter_bin"
