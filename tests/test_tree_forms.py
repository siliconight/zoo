"""The street trees' forms (roadmap 153): a species is a trunk, branches at
its own angles, twigs and leaf mass at the tips; the table shapes, the
slot sizes.
"""
import json
import os

from zoo_keeper.core import genome, tree_forms

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
