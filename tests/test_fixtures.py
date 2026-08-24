"""Tests for the pure light-fixture planner (v0.28)."""

import math

import pytest

from zoo_keeper.core import fixtures


def _manifest(anchors, scope=("building_id", "gs")):
    m = {"light_manifest_version": "1.0.0",
         "space": "Blender Z-up, meters", "rig_library": "lux",
         "anchors": anchors}
    m[scope[0]] = scope[1]
    return m


def _fluoro(aid="sales_ceiling", pos=(0.0, 0.0, 4.1), rot=0.0,
            count=5, spacing=3.0):
    return {"id": aid, "type": "fluorescent", "source": "derived",
            "pos": list(pos), "rot_y": rot,
            "row": {"count": count, "spacing": spacing},
            "reacts_to_alarm": True}


def _street(aid="site/path_0_lights", pos=(10.0, 0.0, 6.0), rot=90.0,
            count=4, spacing=10.0):
    return {"id": aid, "type": "streetlight", "source": "derived",
            "pos": list(pos), "rot_y": rot,
            "row": {"count": count, "spacing": spacing},
            "reacts_to_alarm": False}


def test_row_expands_centered_like_lux():
    # LuxFluorescentRig: start = -(count-1)/2 * spacing. Housings must land
    # exactly on the lamps.
    pts = fixtures.row_points(_fluoro(count=5, spacing=3.0))
    xs = [p[0] for p in pts]
    assert xs == [-6.0, -3.0, 0.0, 3.0, 6.0]
    assert all(p[1] == 0.0 and p[2] == 4.1 for p in pts)
    # centered: mean of the row is the anchor
    assert abs(sum(xs) / len(xs)) < 1e-9


def test_rot_y_direction_convention():
    # rot_y is degrees about up, 0 == +X (DC convention); 90 runs along +Y.
    pts = fixtures.row_points(_fluoro(rot=90.0, count=3, spacing=2.0))
    assert [round(p[1], 4) for p in pts] == [-2.0, 0.0, 2.0]
    assert all(abs(p[0]) < 1e-9 for p in pts)


def test_rowless_anchor_is_single_point():
    a = _fluoro(count=1, spacing=0.0)
    assert fixtures.row_points(a) == [[0.0, 0.0, 4.1]]
    del a["row"]
    assert fixtures.row_points(a) == [[0.0, 0.0, 4.1]]


def test_plan_maps_types_to_species_and_mount():
    plan = fixtures.plan(_manifest([_fluoro(count=2), _street(count=1)]))
    by_species = {p["species"]: p for p in plan["placements"]}
    assert by_species["fluorescent_fixture"]["mount"] == "above"
    assert by_species["streetlight"]["mount"] == "below"
    assert plan["counts"] == {"fluorescent_fixture": 2, "streetlight": 1}
    assert plan["scope_id"] == "gs"


def test_daylight_and_unknown_types_skip_with_reason():
    win = {"id": "wall_S_window_1", "type": "window", "pos": [1, 2, 1.5],
           "rot_y": 90.0, "size": [1.2, 1.0]}
    neon = {"id": "bar_neon", "type": "neon", "pos": [0, 0, 3.0]}
    plan = fixtures.plan(_manifest([win, neon, _fluoro(count=1)]))
    skipped = {s["id"]: s["reason"] for s in plan["skipped"]}
    assert "wall_S_window_1" in skipped        # daylight: no hardware
    assert "bar_neon" in skipped               # honest miss, never guessed
    assert len(plan["placements"]) == 1


def test_types_filter():
    plan = fixtures.plan(_manifest([_fluoro(count=2), _street(count=3)]),
                         types=["streetlight"])
    assert plan["counts"] == {"streetlight": 3}
    assert any("fixture-types" in s["reason"] for s in plan["skipped"])


def test_site_manifest_scope_and_streetlight_row():
    # A Lot-merged site manifest: scope keys off 'site'; the path row is
    # centered on the midpoint anchor and runs along rot_y.
    plan = fixtures.plan(_manifest([_street(count=4, spacing=10.0)],
                                   scope=("site", "wawa_block")))
    assert plan["scope_id"] == "wawa_block"
    ys = sorted(p["pos"][1] for p in plan["placements"])
    assert ys == [-15.0, -5.0, 5.0, 15.0]
    assert all(p["pos"][0] == 10.0 and p["pos"][2] == 6.0
               for p in plan["placements"])


def test_pole_height_reaches_grade_clamped():
    dims = {"min": 3.0, "max": 9.0, "default": 6.0}
    assert fixtures.pole_height_for(6.0, dims) == 6.0
    assert fixtures.pole_height_for(2.0, dims) == 3.0     # clamp up
    assert fixtures.pole_height_for(20.0, dims) == 9.0    # clamp down
    assert fixtures.pole_height_for(0.0, dims) == 6.0     # malformed: default
    assert fixtures.pole_height_for(None, dims) == 6.0


def test_deterministic_and_unique_seed_offsets():
    m = _manifest([_fluoro(count=3), _street(count=2)])
    a, b = fixtures.plan(m), fixtures.plan(m)
    assert a == b
    keys = [(p["anchor_id"], p["slot"]) for p in a["placements"]]
    assert len(keys) == len(set(keys))
    offs = [p["seed_offset"] for p in a["placements"]]
    assert len(offs) == len(set(offs))


def test_rejects_non_lights_manifest():
    with pytest.raises(ValueError):
        fixtures.plan({"slots": []})
    with pytest.raises(ValueError):
        fixtures.plan({"light_manifest_version": "1.0.0"})


def test_reacts_to_alarm_rides_through():
    plan = fixtures.plan(_manifest([_fluoro(count=1), _street(count=1)]))
    flags = {p["species"]: p["reacts_to_alarm"] for p in plan["placements"]}
    assert flags == {"fluorescent_fixture": True, "streetlight": False}


def test_row_direction_matches_rotation_for_any_angle():
    a = _fluoro(rot=45.0, count=2, spacing=math.sqrt(2.0))
    p0, p1 = fixtures.row_points(a)
    assert round(p1[0] - p0[0], 4) == 1.0
    assert round(p1[1] - p0[1], 4) == 1.0


# --- v0.29 facade hardware (sign + wall_pack, DC lights.json 1.1) ------------

def _sign(aid="ext_0_S_sign", pos=(6.0, -0.2, 2.55), rot=270.0,
          size=(2.0, 0.6)):
    return {"id": aid, "type": "sign", "source": "derived",
            "pos": list(pos), "rot_y": rot, "size": list(size),
            "reacts_to_alarm": True}


def _pack(aid="ext_0_N_pack_1", pos=(6.0, 12.15, 2.45), rot=90.0):
    return {"id": aid, "type": "wall_pack", "source": "derived",
            "pos": list(pos), "rot_y": rot, "reacts_to_alarm": True}


def test_facade_types_map_with_mounts():
    plan = fixtures.plan(_manifest([_sign(), _pack()]))
    by = {p["species"]: p for p in plan["placements"]}
    assert by["sign_box"]["mount"] == "center"
    assert by["wall_pack"]["mount"] == "above"
    assert by["sign_box"]["rot_z"] == 270.0


def test_sign_size_rides_through_to_the_placement():
    plan = fixtures.plan(_manifest([_sign(size=(2.0, 0.6)), _pack()]))
    sign = next(p for p in plan["placements"] if p["species"] == "sign_box")
    assert sign["size"] == [2.0, 0.6]
    pack = next(p for p in plan["placements"] if p["species"] == "wall_pack")
    assert "size" not in pack


def test_clamp_dim_respects_genome_range():
    dim = {"min": 0.8, "max": 6.0, "default": 2.0}
    assert fixtures.clamp_dim(2.0, dim) == 2.0
    assert fixtures.clamp_dim(0.2, dim) == 0.8
    assert fixtures.clamp_dim(9.0, dim) == 6.0


def test_facade_anchors_are_rowless_single_points():
    plan = fixtures.plan(_manifest([_sign(), _pack()]))
    assert len(plan["placements"]) == 2
    assert plan["counts"] == {"sign_box": 1, "wall_pack": 1}


# --- v0.30 emitter marker contract -----------------------------------------

def test_marker_name_contract():
    p = {"type": "fluorescent", "anchor_id": "lobby", "slot": 0}
    assert fixtures.marker_name(p) == "LuxEmit_fluorescent"
    assert fixtures.marker_name({"type": "wall_pack"}) == "LuxEmit_wall_pack"


def test_marker_prefix_is_stable_api():
    # Lux's LuxFixtureSpawner discovers markers by this prefix; changing it
    # is a cross-tool breaking change (bump both sides together).
    assert fixtures.MARKER_PREFIX == "LuxEmit"


def test_marker_per_placement_including_rows():
    m = {"light_manifest_version": "1.1", "building_id": "t",
         "anchors": [{"id": "a", "type": "fluorescent",
                      "pos": [0, 0, 3], "rot_y": 0,
                      "row": {"count": 5, "spacing": 3.0}}]}
    plan = fixtures.plan(m)
    # one marker per PLACEMENT (per lamp), not per anchor — rows expanded
    names = [fixtures.marker_name(p) for p in plan["placements"]]
    assert len(names) == 5
    assert set(names) == {"LuxEmit_fluorescent"}


# --------------------------------------------------------------------------- #
# v0.50: the marker path is the shipping path, so it carries what the
# manifest knows (roadmap 54/57). `drop` rides every per-lamp placement, and
# the below-grade `pendant` type gets hardware instead of a silent skip --
# a skipped anchor emits no marker, and no marker means a dark basement.
# --------------------------------------------------------------------------- #

def test_pendant_anchors_get_hardware_not_a_skip():
    p = fixtures.plan(_manifest([
        {"id": "cellar_bulbs", "type": "pendant", "pos": [0, 0, 2.7],
         "row": {"count": 2, "spacing": 5.0}, "drop": 3.3}]))
    assert not p["skipped"]
    assert len(p["placements"]) == 2
    for pl in p["placements"]:
        assert pl["species"] == "pendant_fixture"
        assert pl["mount"] == "above"


def test_drop_rides_every_lamp_placement():
    p = fixtures.plan(_manifest([
        {"id": "hall_ceiling", "type": "fluorescent", "pos": [0, 0, 5.6],
         "row": {"count": 3, "spacing": 10.0}, "drop": 5.6},
        {"id": "old_row", "type": "fluorescent", "pos": [0, 0, 3.2],
         "row": {"count": 1}}]))
    drops = {pl["anchor_id"]: pl["drop"] for pl in p["placements"]}
    assert drops["hall_ceiling"] == 5.6
    # a pre-0.97 manifest without drop stays honest at 0.0 (the rig's
    # fallback range), never a crash and never a guess
    assert drops["old_row"] == 0.0
    per_lamp = [pl["drop"] for pl in p["placements"]
                if pl["anchor_id"] == "hall_ceiling"]
    assert per_lamp == [5.6, 5.6, 5.6]
