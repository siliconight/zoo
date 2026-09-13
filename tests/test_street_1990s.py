"""The 1990s American street kit (roadmap 153): the traffic control a
junction carries and the four kerb objects that date the decade."""
import pytest

from zoo_keeper.core import genome, kit

KIT = {
    "mailbox": (0.6, 0.7, 1.15),
    "newspaper_box": (0.42, 0.45, 1.15),
    "parking_meter": (0.22, 0.14, 1.35),
    "payphone": (0.75, 0.5, 2.3),
    "stop_sign": (0.75, 0.08, 2.85),
    "traffic_signal": (8.0, 0.62, 6.5),
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


def test_nothing_in_the_kit_is_a_placeholder_box():
    """Every one of these was shaped; a genome whose notes still say
    'placeholder' would mean a recipe nobody drew."""
    for sp in KIT:
        notes = genome.load_species(sp)["license"]["notes"]
        assert "placeholder" not in notes.lower(), sp
        assert "REFERENCE:" in notes, sp


def test_the_mailbox_is_blue_and_the_signal_glows():
    assert genome.load_species("mailbox")["styles"]["default"]["color"][2] > 0.35
    st = genome.load_species("traffic_signal")["styles"]["default"]
    assert st["emissive_strength"] > 0
