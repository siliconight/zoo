"""sign_post: minted 2026-09-12 by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_sign_post_is_discovered_and_validates():
    assert "sign_post" in genome.list_species()
    assert genome.validate_genome(genome.load_species("sign_post")) == []


def test_sign_post_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "sign_post_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "sign_post",
        "fit": {"dims": [0.1, 0.1, 2.4], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "sign_post"
