"""canopy_lights: the downlight grid in a fuel canopy's soffit.

Minted 2026-09-26 after cold run 9080's package was measured and found to have
a 22 x 13 m canopy with zero light hardware over it -- every one of the 20 Lux
fixture holders within 45 m sat on the shop.

The grid maths is pure, so it is tested here without Blender. What it must keep
is the thing that made this ONE prop rather than one per lamp: the lamp count
rises with the deck and the draw calls do not.
"""
import importlib.util
from pathlib import Path

from zoo_keeper.core import genome, kit

_SRC = Path(__file__).resolve().parents[1] / "zoo_keeper" / "recipes" / "canopy_lights.py"


def _grid():
    """`_grid` out of the recipe, without importing the bpy-backed package."""
    src = _SRC.read_text(encoding="utf-8")
    body = src.split("def _grid", 1)[1].split("\n\n\ndef build", 1)[0]
    ns: dict = {}
    exec("def _grid" + body, ns)          # noqa: S102 - our own source
    return ns["_grid"]


def test_canopy_lights_is_discovered_and_validates():
    assert "canopy_lights" in genome.list_species()
    assert genome.validate_genome(genome.load_species("canopy_lights")) == []


def test_it_plans_at_the_authored_canopy_size():
    """`deli_counter/specs/gas_station.json` authors `canopy_roof` at
    24.0 x 10.0 x 0.4, and this species is placed across that whole deck."""
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "canopy_lights_0", "role": "prop", "size_mod": "full",
        "style": 1, "species": "canopy_lights",
        "fit": {"dims": [24.0, 10.0, 0.3], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "canopy_lights"


def test_the_grid_covers_the_deck_and_insets_from_the_edges():
    g = _grid()
    for span in (10.0, 13.0, 22.0, 24.0):
        cs = g(span, 3.5, 2)
        assert cs, span
        # every lamp inside the deck, none on its edge
        assert min(cs) > -span / 2.0
        assert max(cs) < span / 2.0
        # symmetric about the centre, so the grid reads as laid out rather
        # than as having drifted to one end
        assert abs(min(cs) + max(cs)) < 1e-9
        # evenly spaced
        if len(cs) > 2:
            steps = [round(b - a, 9) for a, b in zip(cs, cs[1:])]
            assert len(set(steps)) == 1, (span, steps)


def test_a_small_canopy_still_gets_more_than_one_lamp():
    """A single row down the middle of a forecourt reads as a corridor."""
    g = _grid()
    assert len(g(4.0, 3.5, 2)) == 2
    assert len(g(1.0, 3.5, 2)) == 2


def test_the_pitch_stays_near_target_as_the_deck_grows():
    """Derived, not chosen: a bigger deck gets more lamps, not sparser ones."""
    g = _grid()
    last = 0
    for span in (6.0, 10.0, 14.0, 20.0, 24.0, 30.0):
        cs = g(span, 3.5, 2)
        assert len(cs) >= last, span
        last = len(cs)
        pitch = span / len(cs)
        assert 1.5 <= pitch <= 4.0, (span, pitch)


def test_the_whole_grid_is_two_objects():
    """THE REASON THIS IS ONE PROP. Two meshes for the deck, whatever the
    lamp count -- a species placed once per lamp would submit two draw calls
    each, so the authored 24 x 10 deck would cost 42 instead of 2."""
    src = _SRC.read_text(encoding="utf-8")
    # one bmesh per material, both filled inside the grid loop
    assert src.count("geometry.new_bm()") == 2
    assert src.count("geometry.bm_to_object(") == 2
    assert '"objects": [lenses, housings]' in src


def test_the_lens_is_not_coplanar_with_the_soffit():
    """This package already carries a PRESENTATION_ZFIGHT finding. A lit face
    flush with the deck it sits in is that defect by construction."""
    src = _SRC.read_text(encoding="utf-8")
    assert "_PROUD_M" in src
    ns: dict = {}
    for line in src.splitlines():
        if line.startswith("_PROUD_M"):
            exec(line, ns)       # noqa: S102 - our own source
    assert ns["_PROUD_M"] > 0.0


def test_it_carries_no_collision():
    """It is in the deck, five metres up. Nothing traverses a soffit."""
    g = genome.load_species("canopy_lights")
    assert g["collision"] is False
