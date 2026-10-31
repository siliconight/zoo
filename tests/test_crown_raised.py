"""A street tree's crown is raised clear of the sidewalk (1.155.0, the factory's roadmap 324).

The vertical slice's built trees hung leaf cards down to 0.53 m (pin oak), 0.91 m (London plane) and 1.16 m (red
maple): a body walked through cards at eye height, and every sightline down a sidewalk was screened by them. A street
tree is pruned to 8 ft (2.44 m) over a walk -- the walker's tree guide: a "Raised crown" on a street edge.
FAILS ON 1.154.0: there is no `crown_lift`, and every species' lowest card hangs under the clearance.
"""
import pytest

from zoo_keeper.core import tree_forms as T

TREES = ("street_tree", "red_maple", "pin_oak", "honey_locust", "london_plane", "callery_pear")


def test_the_lift_brings_the_lowest_card_to_the_clearance_and_keeps_the_top():
    z0 = -3.25
    clumps = [(-2.0, 0.7), (0.0, 0.8), (2.5, 0.75)]
    k, anchor = T.crown_lift(clumps, z0)
    assert 0.0 < k < 1.0 and anchor == pytest.approx(2.5)

    def lift(z):
        return anchor - (anchor - z) * k

    # every card, placed by its centre and keeping its size, clears; the lowest exactly; the top card unmoved
    assert min(lift(z) - h for z, h in clumps) == pytest.approx(z0 + T.CROWN_CLEAR_M)
    assert lift(2.5) == pytest.approx(2.5)
    assert T.squeeze(-0.9, 3.25, z0) == pytest.approx((3.25 - (z0 + T.CROWN_CLEAR_M)) / (3.25 + 0.9))
    # order and proportion: a three-zone crown stays three zones
    zs = [lift(z) for z, _h in clumps]
    assert zs == sorted(zs)


def test_a_crown_already_clear_is_left_as_it_is():
    assert T.crown_lift([(1.0, 0.5), (2.0, 0.5)], -3.0)[0] == 1.0
    assert T.crown_lift([], -3.0)[0] == 1.0
    assert T.CROWN_CLEAR_M == pytest.approx(8 * 0.3048, abs=1e-3)


def test_a_young_tree_is_lifted_only_as_far_as_its_crown_keeps_its_shape():
    """A tree too short to hold a crown above the clearance is not crushed into a band at its top: pressed past half
    its height a crown stacks its cards (the generic tree at its smallest corner went 6 -> 187 coincident pairs)."""
    z0 = -2.0                                    # a 4 m tree: its top card clears, its lowest cannot without crushing
    k, _anchor = T.crown_lift([(-1.5, 0.4), (0.0, 0.4), (1.5, 0.4)], z0)
    assert k == T.LIFT_K_MIN
    assert T.squeeze(-1.0, 2.0, z0) == 1.0       # the last correction never becomes a second lift


@pytest.mark.parametrize("species", TREES)
def test_bpy_no_leaf_hangs_under_the_clearance(tmp_path, species):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import kit
    # a slot inside every species' genome (a callery pear's width stops at 4.8 m; past it the kit builds a panel)
    h = 6.5
    slot = {"slot_id": "t", "role": "prop", "size_mod": "full", "style": 1, "species": species,
            "material": "wood", "fit": {"dims": [4.0, 4.0, h], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    crown = bpy.data.objects["StreetTree_Crown"]
    lowest = min((crown.matrix_world @ v.co).z for v in crown.data.vertices)
    assert lowest - (-h / 2.0) >= T.CROWN_CLEAR_M - 0.02, (species, lowest + h / 2.0)
