"""The backdrop tree with a silhouette (Zoo 1.97.0, roadmap 228 step F) -- pure, no bpy.

The walker, on cold run 9227's parkland: "those trees in the distance are a little lazy imo
(giant lolipops vs. trees)". `backdrop_forms.tree_plan` is the trunk, the limbs and the lobes
the recipe builds; these hold its proportions, its forms and its budget.
"""
import math

from zoo_keeper.core import backdrop_forms as BF
from zoo_keeper.core import genome


def _inside(p, c, r):
    return sum(((p[k] - c[k]) / r[k]) ** 2 for k in range(3)) <= 1.0 + 1e-9


def test_the_form_follows_the_slots_proportions():
    assert BF.tree_form(8.0, 8.0) == "oak"            # 1.0: squat
    assert BF.tree_form(7.0, 10.0) == "maple"         # 1.43: round
    assert BF.tree_form(4.0, 9.0) == "elm"            # 2.25: tall
    assert BF.tree_form(5.0, 7.0) == "maple"          # 1.4: the three sizes of 1.96.0 are all maples
    assert set(BF.TREE_FORM_ROWS) == {"oak", "maple", "elm"}


def test_the_foot_stands_on_the_ground_and_the_top_lobe_touches_the_top():
    for w, h in ((5.0, 7.0), (7.0, 10.0), (9.0, 13.0), (4.0, 9.0), (8.0, 8.0)):
        p = BF.tree_plan(w, h, 0)
        foot, top, rf, rt = p["trunk"]
        assert foot[2] == -h / 2.0 and rf > rt > 0.0
        lo, hi = BF.tree_plan_bounds(p)
        assert abs(hi[2] - h / 2.0) < 1e-9, (w, h, hi)
        assert lo[2] == -h / 2.0


def test_every_limb_ends_inside_a_lobe_and_every_lobe_is_above_the_fork():
    for w, h in ((5.0, 7.0), (7.0, 10.0), (4.0, 9.0), (8.0, 8.0)):
        p = BF.tree_plan(w, h, 123)
        fork_z = p["trunk"][1][2]
        for root, tip, r0, r1 in p["limbs"]:
            assert root[2] == fork_z and tip[2] > fork_z
            assert any(_inside(tip, c, r) for c, r in p["lobes"]), (w, h, tip)
        for c, r in p["lobes"]:
            assert c[2] - r[2] > fork_z - 1e-9, "daylight under the crown: no lobe reaches the fork"
        assert len(p["lobes"]) == BF.TREE_LIMBS * 3 + 1


def test_the_lobes_reach_about_the_width_and_the_fit_does_the_rest():
    # before the recipe's fit the plan's spread is within a fifth of the slot's, so the fit
    # scales the look rather than remaking it
    for w, h in ((5.0, 7.0), (7.0, 10.0), (9.0, 13.0), (4.0, 9.0), (8.0, 8.0)):
        lo, hi = BF.tree_plan_bounds(BF.tree_plan(w, h, 45))
        for k in range(2):
            assert 0.8 * w <= hi[k] - lo[k] <= 1.2 * w, (w, h, k, hi[k] - lo[k])


def test_the_seed_turns_the_limbs_and_nothing_else():
    a, b = BF.tree_plan(7.0, 10.0, 0), BF.tree_plan(7.0, 10.0, 90)
    assert a["trunk"] == b["trunk"] and a["form"] == b["form"]
    assert [l[1] for l in a["limbs"]] != [l[1] for l in b["limbs"]]
    assert all(abs(math.hypot(*l[1][:2]) - math.hypot(*m[1][:2])) < 1e-9
               for l, m in zip(a["limbs"], b["limbs"]))     # the same reach, turned


def test_the_estimate_fits_the_budget():
    assert BF.tree_tris_estimate() <= genome.load_species("backdrop_tree")["budgets"]["tris_lod0"]
    assert BF.tree_tris_estimate() > 500            # a silhouette costs more than a sphere's 132
