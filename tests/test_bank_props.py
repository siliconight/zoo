"""Bank prop tests (pure -- no Blender).

The four props (gold_bar, drop_safe, queue_stanchion, security_camera) are
bottom-center props, not wall modules. These tests check they load + validate,
resolve from prompts, and carry the right anchor + collision policy.
"""
import pytest

from zoo_keeper.core import genome, intent

BANK_PROPS = ["gold_bar", "drop_safe", "queue_stanchion", "security_camera"]


@pytest.mark.parametrize("sp", BANK_PROPS)
def test_prop_loads_and_validates(sp):
    g = genome.load_species(sp)
    assert genome.validate_genome(g) == []
    assert g["license"]["construction_knowledge"] == "CC0"


def test_prompts_resolve_to_the_right_prop():
    assert intent.parse("a gold bar on the table").species == "gold_bar"
    assert intent.parse("a drop safe under the counter").species == "drop_safe"
    assert intent.parse("a queue stanchion").species == "queue_stanchion"
    assert intent.parse("a security camera on the wall").species \
        == "security_camera"


def test_anchor_types_match_how_each_prop_sits():
    def anchor(sp):
        return genome.load_species(sp)["connectors"]["anchor"]["type"]
    assert anchor("gold_bar") == "surface"       # loot on a surface
    assert anchor("drop_safe") == "floor"        # stands on the floor
    assert anchor("queue_stanchion") == "floor"  # stands on the floor
    assert anchor("security_camera") == "wall"   # mounts to a wall


def test_gold_bar_is_a_pickup_no_collision():
    assert genome.load_species("gold_bar").get("collision") is False
    # the solid props do collide
    for sp in ("drop_safe", "queue_stanchion", "security_camera"):
        assert genome.load_species(sp).get("collision") is True


def test_stanchion_has_a_belt_socket_to_link_the_next_one():
    g = genome.load_species("queue_stanchion")
    assert "ATT_belt" in g["connectors"]["sockets"]
