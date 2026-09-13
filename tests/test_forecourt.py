"""The forecourt clutter (roadmap 153): clusters of cheap objects."""
import pytest

from zoo_keeper.core import genome, kit

KIT = {
    "bollard": (0.22, 0.22, 1.05),
    "jersey_barrier": (0.6, 3.0, 0.82),
    "pallet_stack": (1.2, 1.0, 0.95),
    "water_barrel": (0.58, 0.58, 0.88),
}


@pytest.mark.parametrize("sp", sorted(KIT))
def test_each_is_discovered_validates_and_plans_at_its_dims(sp):
    assert sp in genome.list_species()
    g = genome.load_species(sp)
    assert genome.validate_genome(g) == []
    w, d, h = KIT[sp]
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": f"{sp}_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": sp, "fit": {"dims": [w, d, h], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == sp


def test_every_one_is_cover_a_body_cannot_walk_through():
    """These exist to break a sightline at knee-to-waist height, so each
    must be tall enough to matter and declare collision."""
    for sp in KIT:
        g = genome.load_species(sp)
        assert g["collision"] is True, sp
        assert KIT[sp][2] >= 0.8, sp


def test_the_drum_is_round_and_the_barrier_is_long():
    """A cluster reads by silhouette: the drum's plan is square (a
    cylinder), the barrier is five times as long as it is wide."""
    w, d, h = KIT["water_barrel"]
    assert abs(w - d) < 1e-9
    bw, bd, _bh = KIT["jersey_barrier"]
    assert bd / bw >= 4.0
