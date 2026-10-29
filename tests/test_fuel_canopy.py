"""fuel_canopy: minted 2026-10-29 by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_fuel_canopy_is_discovered_and_validates():
    assert "fuel_canopy" in genome.list_species()
    assert genome.validate_genome(genome.load_species("fuel_canopy")) == []


def test_fuel_canopy_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "fuel_canopy_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "fuel_canopy",
        "fit": {"dims": [22.0, 13.0, 0.9], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "fuel_canopy"


import pytest  # noqa: E402

from zoo_keeper.core import price_pylon_forms as PF  # noqa: E402
from zoo_keeper.core import canopy_forms as FC  # noqa: E402

DECKS = ((22.0, 13.0, 0.9), (24.0, 10.0, 0.4))        # the two decks Deli Counter's specs author


def _span(boxes, axis):
    return min(lo[axis] for _n, lo, _hi in boxes), max(hi[axis] for _n, _lo, hi in boxes)


@pytest.mark.parametrize("w,d,h", DECKS)
def test_the_deck_is_the_slot_exactly_and_its_soffit_is_the_lamps_plane(w, d, h):
    """The canopy's lamps hang 2 cm under the slot's bottom (Deli Counter lights._CANOPY_DROP): the soffit's
    underside must be that bottom, and nothing may stand outside the slot."""
    b = FC.boxes(w, d, h)
    assert _span(b, 0) == pytest.approx((-w / 2, w / 2))
    assert _span(b, 1) == pytest.approx((-d / 2, d / 2))
    assert _span(b, 2) == pytest.approx((-h / 2, h / 2))
    soffit = [x for x in b if x[0] == "Soffit"]
    assert soffit and soffit[0][1][2] == pytest.approx(-h / 2)


@pytest.mark.parametrize("w,d,h", DECKS)
def test_no_two_parts_of_one_colour_overlap_and_the_soffit_and_cap_abut_the_ring(w, d, h):
    """Overlap is a volume shared by two boxes; abutting boxes share a face and no volume. The soffit and the cap
    stand on the ring's inner faces, so their undersides and the ring's are never one plane over shared ground."""
    b = FC.boxes(w, d, h)

    def vol(p, q):
        out = 1.0
        for i in range(3):
            out *= max(0.0, min(p[2][i], q[2][i]) - max(p[1][i], q[1][i]))
        return out

    ring = [x for x in b if x[0] in ("Fascia", "FasciaEnds")]
    for part in [x for x in b if x[0] in ("Soffit", "Cap")]:
        assert all(vol(part, r) == pytest.approx(0.0, abs=1e-12) for r in ring), part
    for i, p in enumerate(ring):
        for q in ring[i + 1:]:
            assert vol(p, q) == pytest.approx(0.0, abs=1e-12)


def test_the_fascia_and_the_stripe_are_the_stores_colours():
    for v in range(len(PF.COLOURWAYS)):
        field, rule, _ink = PF.COLOURWAYS[v]
        f, s = FC.colours(v)
        assert f == pytest.approx(tuple(c / 255 for c in field)) and s == pytest.approx(tuple(c / 255 for c in rule))


@pytest.mark.parametrize("w,d,h", DECKS)
def test_bpy_the_deck_builds_to_its_slot_in_one_material(tmp_path, w, d, h):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "canopy_roof", "role": "prop", "size_mod": "full", "style": 1, "species": "fuel_canopy",
        "fit": {"dims": [w, d, h], "pivot": "center"}}]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")]
    assert {m.name for o in meshes for m in o.data.materials} and \
        len({m.name for o in meshes for m in o.data.materials}) == 1
