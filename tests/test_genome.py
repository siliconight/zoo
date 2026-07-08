import pytest

from zoo_keeper.core import genome


PROP_SPECIES = {"desk", "chair", "helmet", "boots", "simple_car",
                "filing_cabinet", "table", "crt_tv", "atm",
                "vending_machine", "briefcase", "cash_stack",
                "soda_cup", "cheesesteak", "flat_top_grill",
                "condiment_bottle", "french_fries"}

# architectural modules — Deli Counter art/zoo wall-slot dressing
ARCH_SPECIES = {"wall", "wallEnd", "doorway", "window", "breach", "vault_door",
                "teller_line"}


def test_all_species_load_and_validate():
    species = genome.list_species()
    assert set(species) == PROP_SPECIES | ARCH_SPECIES
    for s in species:
        g = genome.load_species(s)
        assert genome.validate_genome(g) == []
        assert g["license"]["construction_knowledge"] == "CC0"


def test_unknown_species_helpful_error():
    with pytest.raises(FileNotFoundError) as e:
        genome.load_species("gazebo")
    assert "desk" in str(e.value)
