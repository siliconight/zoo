import pytest

from zoo_keeper.core import genome


PROP_SPECIES = {"desk", "chair", "helmet", "boots", "simple_car",
                "filing_cabinet", "table", "crt_tv", "atm",
                "vending_machine", "briefcase", "cash_stack",
                "soda_cup", "cheesesteak", "flat_top_grill",
                "condiment_bottle", "french_fries",
                "gold_bar", "drop_safe", "queue_stanchion",
                "security_camera",
                "hvac_unit", "water_tank", "vent_stack", "exhaust_fan",
                "skylight", "satellite_dish",
                "fluorescent_fixture", "streetlight", "sign_box", "wall_pack"}

# architectural modules — Deli Counter art/zoo wall-slot dressing
ARCH_SPECIES = {"wall", "wallEnd", "doorway", "window", "breach", "vault_door",
                "teller_line", "safe_deposit_boxes", "dress_cover", "roof",
                # Phase 1 structural set (vertical-slice visual gate)
                "wallCorner", "stair_rail", "ladder", "shelving", "counter",
                # surface modules (floor/ceiling slab dressing)
                "floor", "ceiling",
                # volume module: a DC `role: "prop"` slot -- the vault, the
                # teller counter, a desk, a crate stack. It belongs HERE and
                # not in PROP_SPECIES above despite the name, and the collision
                # is worth stating: PROP_SPECIES are individually-modelled
                # objects with their own silhouettes, while this is the
                # exact-dims box Deli Counter authored, skinned by the theme.
                # The species name is forced -- `kit.slot_typename` returns the
                # slot's role verbatim, so a `prop` slot needs a `prop` species.
                "prop"}


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
