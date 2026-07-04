import pytest

from zoo_keeper.core import genome


def test_all_species_load_and_validate():
    species = genome.list_species()
    assert set(species) == {"desk", "chair", "helmet", "boots", "simple_car",
                            "filing_cabinet"}
    for s in species:
        g = genome.load_species(s)
        assert genome.validate_genome(g) == []
        assert g["license"]["construction_knowledge"] == "CC0"


def test_unknown_species_helpful_error():
    with pytest.raises(FileNotFoundError) as e:
        genome.load_species("gazebo")
    assert "desk" in str(e.value)
