"""The five street trees are species of their own (roadmap 153)."""
import pytest

from zoo_keeper.core import genome, kit, tree_forms

TREES = {
    "callery_pear": (3.0, 3.0, 5.5),
    "honey_locust": (4.5, 4.5, 6.0),
    "london_plane": (5.0, 5.0, 6.5),
    "pin_oak": (4.0, 4.0, 6.5),
    "red_maple": (4.0, 4.0, 6.0),
}


@pytest.mark.parametrize("sp", sorted(TREES))
def test_each_tree_is_discovered_validates_and_names_its_form(sp):
    assert sp in genome.list_species()
    g = genome.load_species(sp)
    assert genome.validate_genome(g) == []
    assert g["params"]["form"] == sp and sp in tree_forms.FORMS
    assert g["params"]["crown"] == "volume"
    assert g["materials"]["default"] == "wood"


@pytest.mark.parametrize("sp", sorted(TREES))
def test_each_tree_plans_at_its_own_dims(sp):
    w, d, h = TREES[sp]
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": f"{sp}_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": sp, "fit": {"dims": [w, d, h], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == sp


def test_the_five_differ_in_size_and_in_silhouette():
    """A row of five identical trees with five names is a lie; the point of
    naming them is that a pear is narrow and a plane is broad."""
    widths = {sp: TREES[sp][0] for sp in TREES}
    assert len(set(widths.values())) >= 3, widths
    crowns = {tree_forms.FORMS[sp]["crown"] for sp in TREES}
    assert len(crowns) >= 3, crowns


def test_every_form_in_the_table_is_a_species():
    """The table and the genome folder agree, so a form nobody can ask for
    cannot sit in the table unnoticed."""
    assert set(tree_forms.FORMS) == set(TREES)
