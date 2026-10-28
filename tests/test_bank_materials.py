"""The bank's pieces on the surfaces they are made of (1.139.0). delco_1997 maps `metal` to `metal_rusted_street`
(pixelcoat/profiles/themes/delco_1997.json), and a minted species took `metal` and the generic options: the drive-up's
canopy and station were built on rust, the cash cart, camera and clock on wood. FAILS ON 1.138.0.
"""
import pytest

from zoo_keeper.core import genome

#: species -> the kind it is made of
OWN = {"drive_up_canopy": "metal_painted", "drive_up_tube": "metal_painted", "night_drop": "metal_bare",
       "cash_cart": "metal_bare", "clearance_bar": "metal_painted", "wall_clock": "plastic", "planter": "plaster"}


@pytest.mark.parametrize("species", sorted(OWN))
def test_a_bank_piece_defaults_to_its_own_surface_and_every_style_agrees(species):
    g = genome.load_species(species)
    assert g["materials"]["default"] == OWN[species]
    assert "metal" not in g["materials"]["options"] and "wood" not in g["materials"]["options"]
    for name, s in (g.get("styles") or {}).items():
        assert s.get("material", OWN[species]) == OWN[species], (species, name)


def test_the_teller_line_offers_the_wood_every_library_line_asks_for():
    assert "wood" in genome.load_species("teller_line")["materials"]["options"]
