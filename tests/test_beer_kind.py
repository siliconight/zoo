"""A beer distributor's door names it (1.157.0).

The walker, 2026-10-31: "liquor store should have neon beer company signs". Deli Counter 0.297.0 builds a beer
distributor -- Pennsylvania's 1999 case-beer shop -- and its band and its door read from this table, as every shop's
do. FAILS ON 1.156.0: no `beer` kind; a `beer_distributor` shows a street number over its door.
"""
from zoo_keeper.core import storefront_names as SN


def test_a_beer_distributor_is_named_from_the_beer_kind():
    said = SN.sign_for("beer_distributor_a01")
    assert said["kind"] == "beer" and said["text"] in ("BEER WORLD", "CASE LOT BEER")
    assert SN.trade_for("beer_distributor_a01")["text"] == "BEER"


def test_a_brewery_is_still_a_brewery():
    assert SN.sign_for("brewery_a01")["kind"] == "brewery"
