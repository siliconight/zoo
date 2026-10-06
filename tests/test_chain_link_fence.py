"""chain_link_fence (1.77.0): the fence at the playable edge.

The walker, 2026-10-04: a fence between playable and non-playable ground is
good feedback to the player. `core.chain_link_fence_forms` is the plan; the
recipe draws it in two submissions, steel and fabric.
"""
import math

import pytest

from zoo_keeper.core import chain_link_fence_forms as F
from zoo_keeper.core import genome, kit, skins


def test_chain_link_fence_is_discovered_and_validates():
    assert "chain_link_fence" in genome.list_species()
    assert genome.validate_genome(genome.load_species("chain_link_fence")) == []


def test_chain_link_fence_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "chain_link_fence_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "chain_link_fence",
        "fit": {"dims": [9.0, 0.0603, 1.83], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "chain_link_fence"


@pytest.mark.parametrize("width", [1.0, 3.05, 3.2, 9.0, 14.7, 60.0, 120.0])
def test_no_span_is_longer_than_ten_feet_and_the_ends_are_terminals(width):
    posts = F.posts(width)
    xs = [x for x, _od in posts]
    assert xs == sorted(xs)
    assert max(b - a for a, b in zip(xs, xs[1:])) <= F.MAX_SPAN + 1e-9
    assert posts[0][1] == posts[-1][1] == F.TERMINAL_OD
    assert all(od == F.LINE_OD for _x, od in posts[1:-1])
    # the terminals' outer faces are the run's ends: the extents are exact
    assert math.isclose(xs[0] - F.TERMINAL_OD / 2.0, -width / 2.0, abs_tol=1e-6)
    assert math.isclose(xs[-1] + F.TERMINAL_OD / 2.0, width / 2.0, abs_tol=1e-6)


def test_the_fewest_posts_that_keep_the_spans_short():
    assert len(F.posts(1.0)) == 2
    assert len(F.posts(3.05)) == 2          # 2.99 m between terminal centres
    assert len(F.posts(9.0)) == 4           # three spans of 2.98 m
    with pytest.raises(ValueError):
        F.posts(0.1)                        # not even two terminal posts


@pytest.mark.parametrize("height", [1.2, 1.83, 2.44])
def test_the_fabric_hangs_from_the_rail_to_just_above_grade(height):
    bottom, top = F.fabric_z(height)
    assert math.isclose(bottom, -height / 2.0 + F.GROUND_GAP)
    assert math.isclose(top, F.rail_z(height))
    assert math.isclose(F.rail_z(height) + F.RAIL_OD / 2.0, height / 2.0)
    # the tension wire is woven through the fabric's bottom edge, centred
    # on it, so no face of it lies near the card's (the census's 0.6 mm)
    assert F.wire_z(height) == bottom


def test_the_wire_ends_inside_the_terminal_posts():
    """Its end caps were flush with the fabric's ends (the census, 1.77.0).
    The fabric ends at the terminals' centres; the wire runs past them, but
    not out through the posts."""
    for width in (1.0, 9.0, 120.0):
        half_wire = F.wire_length(width) / 2.0
        half_fabric = (width - F.TERMINAL_OD) / 2.0
        assert half_fabric < half_wire < width / 2.0


def test_the_fabric_stays_inside_the_slot():
    """The slot's depth is a terminal post's diameter; the fabric hangs on
    one face of the line posts, inside it."""
    assert F.fabric_y() + F.FABRIC_T / 2.0 <= F.TERMINAL_OD / 2.0
    g = genome.load_species("chain_link_fence")
    assert math.isclose(g["dimensions"]["depth"]["default"], F.TERMINAL_OD)


def test_the_fabric_is_a_kind_the_skin_library_resolves():
    """Pixelcoat 0.56.0 maps `chain_link` in both level themes; a kind
    absent from KNOWN_KINDS is one no part can ask for."""
    assert "chain_link" in skins.KNOWN_KINDS
