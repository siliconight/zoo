"""The aisle sign's `grocery` form: a supermarket's numbered aisle marker (1.131.0).

The walker, 2026-10-26: grocery comps with a numbered sign over every aisle naming what is down it (the factory's
docs/reference/GROCERY_STORE_COMPS.md). `aisle_sign` was the card shop's hand-lettered marker board, its words card
shop words. The `grocery` form prints the aisle's number -- the variant's, aisle 1 at variant 0 -- large in a ruled
box and two lines of categories beside it, white on blue; the card shop's form is unchanged.

FAILS ON 1.130.0: the genome has no `grocery` form and four variants, and `card_brands` has no grocery lines.

Run:  python -m pytest tests/test_grocery_aisle_sign.py
"""
import json
import os

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import card_brands as CB
from zoo_keeper.core import flat_art as FA
from zoo_keeper.core import flat_forms as FF

GENOME = os.path.join(os.path.dirname(__file__), "..", "zoo_keeper", "genome", "species", "aisle_sign.json")


def test_the_genome_offers_the_form_and_a_variant_an_aisle():
    g = json.load(open(GENOME, encoding="utf-8"))
    assert g["params"]["form"] == ["auto", "grocery"]
    assert g["module_variants"] == len(CB.GROCERY_AISLE_SAYS) == 12


def test_the_variant_is_the_aisles_number_and_its_lines():
    for v in (0, 4, 11):
        got = FF.plan_aisle_sign(1.4, 0.05, 0.6, {"form": "grocery"}, v)
        face = got["tiles"]["face"]
        assert face["number"] == v + 1 == got["facts"]["number"]
        assert tuple(face["lines"]) == CB.GROCERY_AISLE_SAYS[v]


def test_the_marker_is_printed_white_on_blue():
    got = FF.plan_aisle_sign(1.4, 0.05, 0.6, {"form": "grocery"}, 2)
    c = CA.paint(dict(got["tiles"]["face"]))
    px = [tuple(c.buf[i:i + 3]) for i in range(0, len(c.buf), 3)]
    blue = sum(1 for p in px if p == FA.GROCERY_GROUND)
    ink = sum(1 for p in px if p == FA.GROCERY_INK)
    assert blue > ink > 0


def test_each_grocery_variant_is_its_own_module():
    """`test_flat_art`'s rule for a variant -- a different module in geometry, not only in its tile -- held to the
    grocery form's twelve."""
    shapes = set()
    for v in range(len(CB.GROCERY_AISLE_SAYS)):
        got = FF.plan_aisle_sign(1.4, 0.05, 0.6, {"form": "grocery"}, v)
        shapes.add(tuple(sorted((p["part"], tuple(p["verts"][0])) for p in got["prims"])))
    assert len(shapes) == len(CB.GROCERY_AISLE_SAYS)


def test_the_card_shops_form_is_unchanged():
    got = FF.plan_aisle_sign(1.1, 0.05, 0.4, {}, 0)
    assert got["tiles"]["face"]["kind"] == "aisle" and "number" not in got["tiles"]["face"]
    assert got["facts"]["says"] == CB.AISLE_SAYS[0]


def test_every_grocery_line_is_painted_and_held_by_the_denylist():
    painted = CA.painted_strings()
    for pair in CB.GROCERY_AISLE_SAYS:
        for line in pair:
            assert line in painted, line
