"""A storey's flight (1.129.0): `stoop_railing`'s flight form, as tall as a storey's rise and its rail, plans as the
species. For a switchback's upper flight (the walker's walk of cold run 9386, finding 6). FAILS ON 1.128.0."""
from zoo_keeper.core import kit


def test_a_storeys_flight_rail_plans_as_the_species():
    slot = {"slot_id": "stair_rake_0", "role": "prop", "size_mod": "full", "style": 1, "material": "metal_painted",
            "species": "stoop_railing", "form": "flight",
            "fit": {"dims": [5.2339, 0.05, 3.6 + 0.9144], "pivot": "center", "collision": "none"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["modules"][0]["species"] == "stoop_railing", plan.get("species_fallbacks")
    assert not plan.get("species_fallbacks"), plan["species_fallbacks"]
