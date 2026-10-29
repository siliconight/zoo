"""canopy_column: minted 2026-10-29 by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_canopy_column_is_discovered_and_validates():
    assert "canopy_column" in genome.list_species()
    assert genome.validate_genome(genome.load_species("canopy_column")) == []


def test_canopy_column_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "canopy_column_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "canopy_column",
        "fit": {"dims": [0.5, 0.5, 4.9], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "canopy_column"


import pytest  # noqa: E402

from zoo_keeper.core import canopy_forms as CC  # noqa: E402


@pytest.mark.parametrize("w,d,h", ((0.5, 0.5, 4.9), (0.4, 0.4, 5.0)))
def test_the_column_is_its_slot_a_guard_at_its_foot_and_a_shaft_to_the_soffit(w, d, h):
    """FAILS ON 1.148.0: no species, and every canopy column shipped as its greybox box."""
    (g, glo, ghi), (s, slo, shi) = CC.column_boxes(w, d, h)
    assert (glo[0], glo[1], glo[2]) == pytest.approx((-w / 2, -d / 2, -h / 2))
    assert (ghi[0], ghi[1]) == pytest.approx((w / 2, d / 2))
    assert shi[2] == pytest.approx(h / 2) and slo[2] < ghi[2]          # to the soffit, rising out of the guard
    assert shi[0] < w / 2 and shi[1] < d / 2
