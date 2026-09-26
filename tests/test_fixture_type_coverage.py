"""Every light-anchor type Deli Counter emits must be ACCOUNTED FOR here.

Written 2026-09-26, after cold run 9081 spent a whole run exporting a package
with no canopy light in it.

WHAT ACTUALLY HAPPENED, because the lesson is not the one it looked like.
Nothing was silent. `core.fixtures.plan` reported both new types in its
`skipped` list with the reason "no fixture species for this type", and Level
Factory's Zoo adapter turned that into a validation finding with the count, the
type names and the owner:

    [moderate] ZOO_CAPABILITY_GAP
      4 light anchor(s) of type canopy_lights, canopy_wash have no fixture
      species in Zoo ... grow the species in Zoo (FIXTURES row + genome +
      recipe); owner=zoo

The finding was raised and nobody read it. A cold run prints "0 blockers, 58
findings" and the 58 are where a new capability gap hides.

So this is not another report. It is a test that FAILS AT COMMIT TIME, before a
run is spent, when Deli Counter has a type that this module has not decided
about. Deciding means one of three things, and all three are fine:

  * a `FIXTURES` row -- something builds hardware for it;
  * a `DAYLIGHT` entry -- it is light without hardware by design;
  * a `HARDWARE_ELSEWHERE` entry -- something else already builds its hardware.

What is not fine is a fourth state where nobody chose, because that state
builds nothing and reads, on a screen, as a room that is simply dark.

IT SKIPS RATHER THAN GUESSES when the sibling checkout is not there. A test
that cannot see Deli Counter's output has learned nothing about it, and saying
so is the point.
"""
from __future__ import annotations

import glob
import json
import os

import pytest

from zoo_keeper.core import fixtures

_DC_BUILD = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "deli_counter", "build")


def _manifests() -> list[str]:
    return sorted(glob.glob(os.path.join(_DC_BUILD, "*.lights.json")))


def _accounted() -> set[str]:
    return (set(fixtures.FIXTURES)
            | set(fixtures.DAYLIGHT)
            | set(fixtures.HARDWARE_ELSEWHERE))


def test_the_sweep_is_actually_reading_manifests():
    """Guard the guard: a loop over an empty directory passes vacuously."""
    if not os.path.isdir(_DC_BUILD):
        pytest.skip("no deli_counter/build beside this checkout")
    assert len(_manifests()) >= 20, (
        "only %d lights manifest(s) found in %s" % (len(_manifests()), _DC_BUILD))


def test_every_anchor_type_deli_counter_emits_is_accounted_for():
    if not os.path.isdir(_DC_BUILD):
        pytest.skip("no deli_counter/build beside this checkout")
    seen: dict[str, str] = {}
    for path in _manifests():
        try:
            man = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for a in man.get("anchors", []) or []:
            if isinstance(a, dict) and a.get("type"):
                seen.setdefault(str(a["type"]), os.path.basename(path))

    assert seen, "no anchor types read at all"
    unaccounted = {t: where for t, where in sorted(seen.items())
                   if t not in _accounted()}
    assert not unaccounted, (
        "Deli Counter emits %d anchor type(s) this module has not decided "
        "about: %s.\nEach needs a FIXTURES row (something builds hardware), a "
        "DAYLIGHT entry (light without hardware by design) or a "
        "HARDWARE_ELSEWHERE entry (something else builds it). Leaving one "
        "undecided builds nothing and reads on screen as a dark room -- cold "
        "run 9081 spent a whole run on exactly that."
        % (len(unaccounted), unaccounted))


def test_the_canopy_pair_is_decided_and_decided_differently():
    """The two canopy types are NOT the same kind of thing, and a row that
    treated them alike would be wrong about one of them."""
    assert fixtures.FIXTURES["canopy_lights"]["species"] == "canopy_lights"
    # hardware, but no emitter marker: the grid holds 12-24 lamps and
    # max_lights_per_object is 8 on the renderer packages ship on
    assert fixtures.FIXTURES["canopy_lights"]["marker"] is False
    # its dimensions are the DECK, so the anchor's size has to travel
    assert fixtures.FIXTURES["canopy_lights"]["sized"] is True
    # and the wash has no hardware at all -- calling that "no fixture species"
    # would be a lie about the anchor rather than a fact about the table
    assert "canopy_wash" in fixtures.HARDWARE_ELSEWHERE
    assert "canopy_wash" not in fixtures.FIXTURES


def test_a_sized_placement_carries_the_anchors_footprint():
    """Without this the species builds its genome default on every canopy."""
    man = {"light_manifest_version": "1.3.0", "anchors": [{
        "id": "canopy_roof_lights", "type": "canopy_lights",
        "pos": [0.0, 0.0, 4.78], "rot_y": 0.0,
        "size": [22.0, 13.0], "drop": 4.78}]}
    plan = fixtures.plan(man)
    placements = [p for p in plan["placements"] if p["type"] == "canopy_lights"]
    assert len(placements) == 1
    assert placements[0]["size"] == [22.0, 13.0]
    assert placements[0]["marker"] is False


def test_size_means_a_footprint_only_where_the_row_says_so():
    """THE ASSERTION THIS TEST FIRST MADE WAS WRONG, and finding that out is
    why it is worth keeping.

    It asserted that a non-canopy placement carries no `size` at all. It does:
    `plan` has copied `size` onto EVERY placement since signs needed it, and
    the builder has always read it as width x HEIGHT because every sized
    placement until now was a sign panel. A canopy's size is a FOOTPRINT, and
    reading 13 m of depth as a height would have clamped to the genome's 0.5
    and built a fixture nobody meant.

    So what distinguishes them is the FIXTURES row, not the presence of a key.
    """
    man = {"light_manifest_version": "1.3.0", "anchors": [{
        "id": "room_1_lights", "type": "fluorescent",
        "pos": [0.0, 0.0, 3.0], "rot_y": 0.0,
        "size": [4.0, 4.0], "row": {"count": 1, "spacing": 0.0},
        "drop": 2.8}]}
    for p in fixtures.plan(man)["placements"]:
        assert p.get("size") == [4.0, 4.0]      # copied, as it always was
        assert not p.get("size_is_footprint")   # but it is a panel, not a deck

    deck = {"light_manifest_version": "1.3.0", "anchors": [{
        "id": "canopy_roof_lights", "type": "canopy_lights",
        "pos": [0.0, 0.0, 4.78], "rot_y": 0.0,
        "size": [22.0, 13.0], "drop": 4.78}]}
    got = fixtures.plan(deck)["placements"]
    assert len(got) == 1
    assert got[0]["size"] == [22.0, 13.0]
    assert got[0]["size_is_footprint"] is True
