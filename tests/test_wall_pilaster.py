"""wall_pilaster: minted 2026-10-30 by tools/new_species.py (roadmap 150)."""
import pytest

from zoo_keeper.core import genome, kit


def test_wall_pilaster_is_discovered_and_validates():
    assert "wall_pilaster" in genome.list_species()
    assert genome.validate_genome(genome.load_species("wall_pilaster")) == []


def test_wall_pilaster_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "wall_pilaster_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "wall_pilaster",
        "fit": {"dims": [0.6, 0.1, 7.0], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "wall_pilaster"


def test_the_pier_is_the_slots_box_exactly_and_its_shaft_stands_back():
    """FAILS ON 1.149.0: no species. Plinth and cap fill the slot; the shaft is narrower and set back from their
    front (local -Y), its back on the wall (+Y)."""
    from zoo_keeper.core import pilaster_forms as P
    w, d, h = 0.6, 0.1, 7.2
    parts = {n: (lo, hi) for n, lo, hi in P.boxes(w, d, h)}
    lo = [min(b[0][i] for b in parts.values()) for i in range(3)]
    hi = [max(b[1][i] for b in parts.values()) for i in range(3)]
    assert lo == [-w / 2, -d / 2, -h / 2] and hi == [w / 2, d / 2, h / 2]
    s_lo, s_hi = parts["Shaft"]
    # the front is local -Y (every Zoo prop's): the shaft stands back from it and its back is the wall, +Y
    assert s_lo[1] == -d / 2 + P.SHAFT_BACK and s_hi[1] == d / 2
    assert s_lo[0] == -w / 2 + P.SHAFT_INSET and s_hi[0] == w / 2 - P.SHAFT_INSET
    # the shaft abuts the plinth's top and the cap's underside, and those two faces of it are dropped
    assert s_lo[2] == parts["Plinth"][1][2] and s_hi[2] == parts["Cap"][0][2]
    assert P.hidden("Shaft", (0, 0, 1)) and P.hidden("Shaft", (0, 0, -1))
    assert not P.hidden("Shaft", (0, 1, 0)) and not P.hidden("Plinth", (0, 0, 1))


def test_it_is_the_buildings_stone_trim():
    from zoo_keeper.core import dressing
    g = genome.load_species("wall_pilaster")
    assert g["materials"]["options"] == [dressing.STONE_TRIM_KIND]
    assert all(tuple(s["color"]) == dressing.STONE_TRIM_COLOR for s in g["styles"].values())


@pytest.mark.parametrize("corner", ("min", "default", "max"))
def test_bpy_the_pier_builds_with_no_coincident_faces(corner):
    pytest.importorskip("bpy")
    from tests.test_coincident_faces import _probe_species
    rec = _probe_species("wall_pilaster", corner)
    assert rec["pairs"] == [], rec["pairs"][:3]
