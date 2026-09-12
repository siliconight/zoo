"""bench: minted 2026-09-12 by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_bench_is_discovered_and_validates():
    assert "bench" in genome.list_species()
    assert genome.validate_genome(genome.load_species("bench")) == []


def test_bench_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "bench_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "bench",
        "fit": {"dims": [1.8, 0.5, 0.45], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "bench"
