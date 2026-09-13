"""The street trees' forms (roadmap 153): a species is a trunk, branches at
its own angles, twigs and leaf mass at the tips; the table shapes, the
slot sizes.
"""
import json
import os

from zoo_keeper.core import genome, tree_forms

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_every_form_carries_a_third_order_of_branching():
    """The walker's frames: the crown is tracery, which is branch, twig and
    twiglet -- a form with no twiglets is a form that reads as blobs."""
    for name, f in tree_forms.FORMS.items():
        assert f.get("twiglets", 0) >= 1, name
        assert f["twigs"] >= 3, name
        assert f["cluster"] <= 0.25, (name, f["cluster"])


def test_every_form_names_a_shape_and_the_angles_run_low_to_high():
    for name, f in tree_forms.FORMS.items():
        assert 0.2 <= f["first_branch"] < f["leader"] <= 1.0, name
        assert 3 <= f["branches"] <= 10 and 1 <= f["twigs"] <= 4, name
        lo, mid, hi = f["angles"]
        assert 0 < hi <= mid <= lo <= 120, (name, f["angles"])    # upper limbs rise more
        assert 0.1 <= f["cluster"] <= 0.5 and 0.5 <= f["reach"] <= 1.0, name
        assert f["crown"] in ("oval", "pyramid", "vase", "flat"), name
        for k in range(f["branches"]):
            assert 0 < tree_forms.branch_angle(f, k, f["branches"]) <= 120
        for z in (0.0, 0.5, 1.0):
            assert 0.2 <= tree_forms.envelope(f, z) <= 1.0, (name, z)


def test_the_pin_oak_droops_low_and_rises_high_and_the_pear_rises_tight():
    oak = tree_forms.form("pin_oak")
    assert tree_forms.branch_angle(oak, 0, 7) > 90 > tree_forms.branch_angle(oak, 6, 7)
    assert tree_forms.envelope(oak, 0.0) > tree_forms.envelope(oak, 1.0)     # a pyramid
    pear = tree_forms.form("callery_pear")
    assert max(pear["angles"]) < 40
    assert tree_forms.envelope(pear, 1.0) > tree_forms.envelope(pear, 0.0)   # a vase


def test_an_unknown_species_is_the_commonest_street_tree():
    assert tree_forms.form(None) == tree_forms.FORMS[tree_forms.DEFAULT]
    assert tree_forms.form("elm_of_no_record") == tree_forms.FORMS["red_maple"]


def test_the_genome_names_a_form_the_table_holds():
    g = genome.load_species("street_tree")
    assert g["params"].get("form") in tree_forms.FORMS
    assert g["params"].get("crown") == "volume"
    assert g["budgets"]["tris_lod0"] >= 2136   # measured: a red maple builds 2,136 tris


#: What Blender actually built for each form, 2026-09-13, read off the
#: exported glTF rather than off a report. The derivation is checked
#: against these rather than against itself.
#:
#: THE THIRD ORDER (0.73.0). The walker's reference frames asked for many
#: thin branches and many small leaf masses, so a twig now forks into
#: twiglets and every mass but a branch's own tip is one cheap box. The
#: count is no longer one number per tip: it is the pieces, each with its
#: own price (`tree_forms.TRIS_*`), and the five builds land on it exactly.
#:
#: WHAT IT COST TO GET THERE, kept because it is the lesson: with twigs as
#: cylinders the same trees came to 8,952 / 6,960 / 5,448 / 8,076 / 7,200
#: -- a street prop no level could afford -- and with twigs as BEVELLED
#: boxes, 44 tris each instead of 12, red maple was 5,184 against a
#: derived 2,880. A twig two centimetres across needs neither a cylinder
#: nor a bevel; the trunk and the branches keep both.
#:
#: BEFORE THE THIRD ORDER (0.71.0): 1,992 / 2,352 / 2,532 / 2,712 / 3,072,
#: which `84 + 108 * tips` reproduced exactly.
MEASURED_TRIS = {"london_plane": 2208, "red_maple": 2880, "honey_locust": 2640,
                 "pin_oak": 3216, "callery_pear": 3552}


def test_the_triangle_count_is_derived_and_matches_every_measured_build():
    for sp, tris in MEASURED_TRIS.items():
        f = tree_forms.FORMS[sp]
        assert tree_forms.tri_count(f) == tris, (sp, tree_forms.tri_count(f), tris)
    # and the derivation is the pieces, not a curve fitted to five points
    f = tree_forms.FORMS["red_maple"]
    b, tw, tl = f["branches"], f["twigs"], f["twiglets"]
    assert tree_forms.limbs(f) == 2 + b                      # cylinders
    assert tree_forms.sticks(f) == b * tw * (1 + tl)         # thin boxes
    assert tree_forms.big_tips(f) == 1 + b
    assert tree_forms.small_tips(f) == b * (1 + tw + tw * tl)
    assert tree_forms.tips(f) == tree_forms.big_tips(f) + tree_forms.small_tips(f)
    assert tree_forms.tri_count(f) == (
        tree_forms.TRIS_GRATE
        + tree_forms.TRIS_LIMB * tree_forms.limbs(f)
        + tree_forms.TRIS_TWIG * tree_forms.sticks(f)
        + tree_forms.TRIS_CLUSTER * tree_forms.big_tips(f)
        + tree_forms.TRIS_SMALL_CLUSTER * tree_forms.small_tips(f))


def test_the_leaf_colour_rides_the_style_so_a_row_can_differ():
    """A module is built once per stem and instanced, so two trees differ
    only if they are two modules -- and the style index is already in the
    stem. Lot plants style 1, 2 or 3 and gets green, gold and orange."""
    seen = {tuple(tree_forms.leaf_color(s)) for s in (1, 2, 3)}
    assert len(seen) == 3
    assert tree_forms.leaf_color(1) == tree_forms.leaf_color(1 + len(tree_forms.LEAF_PALETTE))
    green, gold = tree_forms.leaf_color(1), tree_forms.leaf_color(2)
    assert gold[0] > green[0] and green[1] >= gold[1] * 0.8


def test_every_genome_carries_the_budget_its_form_derives():
    for sp, f in tree_forms.FORMS.items():
        g = genome.load_species(sp)
        assert g["budgets"]["tris_lod0"] == tree_forms.tri_budget(f), sp
        assert g["budgets"]["tris_lod0"] > tree_forms.tri_count(f), sp
