"""price_pylon form `bank` (1.138.0): a bank's time-and-temperature sign, the gas pylon's frame with a bank's faces.

The walker's bank list, outside (the factory's docs/reference/BANK_INTERIOR_COMPS.md: "a bank's street sign that
flashed the time and the temperature, from 1951 on"). FAILS ON 1.137.0, whose pylon has one form.
"""
import pytest

from zoo_keeper.core import genome, kit
from zoo_keeper.core import price_pylon_forms as PP
from zoo_keeper.core import storefront_names as SN
from zoo_keeper.core import teller_line_forms as TF

CORNERS = [(PP.RANGES["width"][0], PP.RANGES["height"][0]), (2.4, 6.5), PP.DC_SIZES[0][::2]]


def test_the_genome_offers_the_bank_form_and_sixteen_variants():
    g = genome.load_species("price_pylon")
    assert g["params"]["form"] == ["auto", "bank"] and g["module_variants"] == TF.VARIANTS == 16
    got, why = kit.honour_dressing({"form": "bank", "variant": 15}, "price_pylon")
    assert got == {"form": "bank", "stock": None, "variant": 15} and not why


@pytest.mark.parametrize("w,h", CORNERS)
@pytest.mark.parametrize("variant", range(16))
def test_every_word_sets_at_every_size(w, h, variant):
    a = PP.art(w, h, variant, "bank")
    assert a["unset"] == [], (w, h, variant, a["unset"])
    clock, temp = PP.READINGS[variant % len(PP.READINGS)]
    assert a["said"] == [TF.bank_said(variant)["text"], clock, f"{temp}F", PP.BANK_STRIP]
    # one image, laid out as the gas pylon's: the same three faces where the geometry maps them
    gas = PP.art(w, h, variant % 4)
    assert a["size"] == gas["size"] and a["rects"] == gas["rects"]


def test_the_sign_names_the_bank_its_door_does():
    for business in ["bank_branch_a0%d" % i for i in range(1, 8)] + ["credit_union_a01", "bank_job"]:
        sign = SN.sign_for(business)
        a = PP.art(2.4, 6.5, TF.variant_for(business), "bank")
        assert a["said"][0] == sign["text"], business


def test_the_bank_art_is_its_own_and_repeatable():
    a, b = PP.art(2.4, 6.5, 5, "bank"), PP.art(2.4, 6.5, 5, "bank")
    assert bytes(a["canvas"].buf) == bytes(b["canvas"].buf) and a["name"] == b["name"]
    assert a["name"] != PP.art(2.4, 6.5, 5)["name"] and a["name"].startswith("pylon_bank_v5_")
    # the gas pylon is the pylon it was: its art takes no form
    assert PP.art(2.4, 6.5, 1)["said"][0] == PP.STORE
