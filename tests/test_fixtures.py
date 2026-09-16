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


# --- the club set's hardware (v0.94) ------------------------------------------


def _wash(aid="main_floor_wash_1", pos=(-14.25, -1.5, 3.2), color="amber"):
    return {"id": aid, "type": "club_wash", "source": "derived",
            "pos": list(pos), "rot_y": 0.0, "room": "main_floor",
            "color": color, "radius": 4.667, "row": {"count": 1, "spacing": 0.0},
            "drop": 3.2, "reacts_to_alarm": True}


def _stage(aid="main_floor_stage", pos=(-1.5, -5.0, 3.2),
           target=(-6.0, -5.0, 1.68), count=2):
    return {"id": aid, "type": "stage_light", "source": "derived",
            "pos": list(pos), "rot_y": 90.0, "room": "main_floor",
            "color": "amber", "target": list(target), "radius": 1.5,
            "row": {"count": count, "spacing": 1.2}, "cycle_s": 4.0,
            "drop": 3.2, "reacts_to_alarm": True}


def test_a_club_wash_and_a_stage_light_now_have_hardware():
    """Walked 2026-09-16: "it doesn't look like that light is coming out of
    any viewable light fixtures". Before 0.94 both came back skipped with
    "no fixture species for this type"."""
    plan = fixtures.plan(_manifest([_wash(), _stage()]))
    assert plan["counts"] == {"club_fixture": 3}      # 1 wash + a 2-lamp row
    forms = sorted(p["params"]["form"] for p in plan["placements"])
    assert forms == ["can", "par", "par"]
    # HANG, not above: a club anchor's pos is the CEILING PLANE, and 'above'
    # (bottom at the emitter, body upward) buried the whole can in the slab
    # -- shot at the walker's own station and looked at before this line was
    # written. 'hang' drops it under the ceiling, mouth down, and unlike
    # 'below' it does not stretch the fixture to grade.
    assert all(p["mount"] == "hang" for p in plan["placements"])
    assert not plan["skipped"]


def test_the_club_hardware_carries_no_emitter_marker_on_purpose():
    """The marker path hands `rig_for_anchor` only {type, id, drop}: a wash
    would lose its colour and radius, a stage light its target. Their light
    stays on `bake_club`, and a marker here would DOUBLE it."""
    plan = fixtures.plan(_manifest([_wash(), _stage(), _fluoro(), _street()]))
    by_type = {}
    for p in plan["placements"]:
        by_type.setdefault(p["type"], set()).add(p["marker"])
    assert by_type["club_wash"] == {False}
    assert by_type["stage_light"] == {False}
    # and nothing that shipped before this changed
    assert by_type["fluorescent"] == {True}
    assert by_type["streetlight"] == {True}


def test_a_par_can_points_at_the_anchors_own_target():
    """rot_y on a stage_light is the ROW's axis, not the barrel's. A can
    that does not point at the target the light aims at is a prop."""
    plan = fixtures.plan(_manifest([_stage(count=1)]))
    p = plan["placements"][0]
    # target is 4.5 m west and 1.52 m below: bearing 180, tilt off plumb
    # atan(4.5 / 1.52) = 71.34 degrees
    assert p["rot_z"] == pytest.approx(180.0, abs=1e-3)
    assert p["tilt_deg"] == pytest.approx(
        math.degrees(math.atan2(4.5, 1.52)), abs=1e-3)
    # ...and the anchor's own rot_y (90) is NOT what shipped
    assert p["rot_z"] != 90.0


def test_a_stage_light_with_no_target_hangs_plumb_rather_than_failing():
    a = _stage(count=1)
    del a["target"]
    p = fixtures.plan(_manifest([a]))["placements"][0]
    assert p["tilt_deg"] == 0.0
    assert p["rot_z"] == 90.0          # the anchor's own, untouched


def test_a_target_at_or_above_the_fixture_clamps_instead_of_flipping():
    """A stage light that has to aim UP is a manifest error; swinging the
    barrel over the top would hide it."""
    from zoo_keeper.core import club_fixture_forms as cff
    assert cff.tilt_for((0, 0, 3.2), (4, 0, 3.2))[1] == 90.0
    assert cff.tilt_for((0, 0, 3.2), (4, 0, 5.0))[1] == 90.0
    assert cff.tilt_for((0, 0, 3.2), (0, 0, 0.0)) == (0.0, 0.0)


def test_the_lens_wears_the_pools_own_colour():
    plan = fixtures.plan(_manifest([_wash(color="magenta")]))
    assert plan["placements"][0]["gel"] == "magenta"
    from zoo_keeper.core import club_fixture_forms as cff
    assert cff.gel("magenta") == cff.GEL["magenta"]
    # an unknown name is the warm lamp, never a guess and never a failure --
    # Lux owns that palette and this is a second copy of it
    assert cff.gel("chartreuse") == cff.GEL_DEFAULT
    assert cff.gel(None) == cff.GEL_DEFAULT


def test_the_club_types_with_hardware_elsewhere_say_so():
    """"no fixture species for this type" was a lie about all three: a neon
    IS its sign, a back_bar is the bar's own bulbs, a room_ambient is a
    probe."""
    anchors = [{"id": "n", "type": "neon", "pos": [0, 0, 2.2], "rot_y": 0.0},
               {"id": "b", "type": "back_bar", "pos": [0, 0, 1.7], "rot_y": 0.0},
               {"id": "r", "type": "room_ambient", "pos": [0, 0, 1.6],
                "rot_y": 0.0}]
    plan = fixtures.plan(_manifest(anchors))
    assert plan["placements"] == []
    assert {s["type"] for s in plan["skipped"]} == {"neon", "back_bar",
                                                    "room_ambient"}
    for s in plan["skipped"]:
        assert s["reason"].startswith("hardware built elsewhere")


def test_the_can_and_the_par_put_their_lit_face_at_the_anchor():
    """Mount 'above' is bottom-at-the-emitter, and the lens is the bottom:
    the light Lux bakes at the anchor comes out of the face a player sees."""
    from zoo_keeper.core import club_fixture_forms as cff
    for form in cff.FORMS:
        got = cff.plan(form, 0.16, 0.16, 0.25)
        lens = [p for p in got["parts"] if p["part"] == "lens"]
        assert len(lens) == 1
        # within the lens plate's own half-thickness of the fixture's bottom
        assert lens[0]["center"][2] <= -0.25 / 2.0 + got["facts"]["throat"] + 0.02
        assert got["facts"]["lens_r"] > 0.0
        assert got["facts"]["parts"] >= 3


# --- the club's hardware, built in Blender (v0.94) ----------------------------


def _club_manifest():
    return {"light_manifest_version": "1.2.0", "building_id": "club_bpy",
            "space": "Blender Z-up, meters", "anchors": [
                {"id": "wash", "type": "club_wash", "pos": [0.0, 0.0, 3.2],
                 "rot_y": 0.0, "color": "magenta", "radius": 4.0,
                 "row": {"count": 1, "spacing": 0.0}, "drop": 3.2},
                {"id": "stage", "type": "stage_light", "pos": [6.0, 0.0, 3.2],
                 "rot_y": 90.0, "color": "amber", "target": [2.0, 0.0, 1.0],
                 "row": {"count": 1, "spacing": 0.0}, "drop": 3.2},
                {"id": "tube", "type": "fluorescent", "pos": [-6.0, 0.0, 3.2],
                 "rot_y": 0.0, "row": {"count": 2, "spacing": 2.0},
                 "drop": 3.2}]}


def _built(tmp_path):
    import json
    import os
    from zoo_keeper.bpylayer import build
    res = build.build_fixtures(_club_manifest(), str(tmp_path), theme="delco",
                               options={"save_blend": False})
    with open(os.path.join(str(tmp_path), "club_bpy_fixtures.built.json"),
              encoding="utf-8") as fh:
        index = json.load(fh)
    return res, index, os.path.join(str(tmp_path), index["files"]["glb"])


def _gltf(path):
    import json
    import struct
    raw = open(path, "rb").read()
    assert raw[:4] == b"glTF"
    ln, kind = struct.unpack_from("<I4s", raw, 12)
    assert kind == b"JSON"
    return json.loads(raw[20:20 + ln])


def test_bpy_the_club_gets_hardware_and_no_marker_with_it(tmp_path):
    """Walked 2026-09-16: "it doesn't look like that light is coming out of
    any viewable light fixtures". A marker as well would DOUBLE the light,
    because the manifest bake already makes it."""
    pytest.importorskip("bpy")
    res, index, glb = _built(tmp_path)
    assert res["counts"]["club_fixture"] == 2
    # one marker for the two-lamp fluorescent row, none for the club
    assert index["emitter_markers"] == 2
    assert index["markerless_fixtures"] == 2
    assert index["fixtures_built"] == 4
    j = _gltf(glb)
    names = [n["name"] for n in j["nodes"]]
    assert any(n.startswith("ClubFixture") for n in names)
    assert sum(1 for n in names if n.startswith("LuxEmit")) == 2
    assert not any(n.startswith("LuxEmit_club") or n.startswith("LuxEmit_stage")
                   for n in names)


def test_bpy_the_lens_is_emissive_in_the_anchors_own_gel(tmp_path):
    """A white-hot lens under a magenta pool is the disagreement the frame
    showed. `_Lens` so Lux's power cut takes it with the room."""
    pytest.importorskip("bpy")
    from zoo_keeper.core import club_fixture_forms as cff
    _res, _index, glb = _built(tmp_path)
    j = _gltf(glb)
    lit = {m["name"]: m for m in j["materials"]
           if m["name"].startswith("M_ClubFixture") and m["name"].endswith("_Lens")}
    assert len(lit) == 2, sorted(lit)
    got = set()
    for m in lit.values():
        ef = m["emissiveFactor"]
        assert any(v > 0.0 for v in ef)
        base = m["pbrMetallicRoughness"]["baseColorFactor"][:3]
        got.add(tuple(round(v, 2) for v in base))
    assert got == {tuple(round(v, 2) for v in cff.GEL["magenta"]),
                   tuple(round(v, 2) for v in cff.GEL["amber"])}


def test_bpy_a_par_can_leans_at_its_target_and_hangs_below_the_ceiling(tmp_path):
    """The anchor IS the ceiling plane, so a fixture mounted `above` it is
    inside the slab -- measured in a frame before the mount was `hang`. And
    a par can that does not point at the target the light aims at is a prop.
    """
    pytest.importorskip("bpy")
    import bpy
    _res, _index, _glb = _built(tmp_path)
    objs = {}
    for o in bpy.context.scene.objects:
        if o.type != "MESH" or not o.name.startswith("ClubFixture"):
            continue
        pts = [o.matrix_world @ v.co for v in o.data.vertices]
        objs[o.name] = pts
    assert objs, sorted(o.name for o in bpy.context.scene.objects)
    # WHAT POKES ABOVE THE CEILING PLANE, and how much. A `hang` fixture
    # pivots about its own TOP, which is the anchor, so a can hanging plumb
    # has nothing above it -- but a par can tilted 73 degrees off plumb
    # sweeps its barrel rim and clamp up past that point. MEASURED at this
    # manifest: 0.146 m, which is inside the 0.1-0.2 m gap Deli Counter
    # leaves between a room's ceiling and the slab over it, so the clamp is
    # half-buried in the tiles the way a bolted fixture is and nothing
    # reaches the floor above. Held to the gap, not to zero.
    top = max(p.z for pts in objs.values() for p in pts)
    assert 3.2 <= top <= 3.2 + 0.2, top
    # ...and the whole of it hangs within a fixture's depth below it
    bottom = min(p.z for pts in objs.values() for p in pts)
    assert 3.2 - 0.6 <= bottom < 3.2
    # THE PAR CAN LEANS TOWARD ITS TARGET. The anchor is at x 6.0 and the
    # target at x 2.0, and a `hang` fixture pivots about its TOP -- so it is
    # the barrel and the lens that swing toward -x while the clamp stays
    # over the anchor. (Written the other way round first, from the `above`
    # mount it no longer uses, and the build said so: 5.648 to 6.057.)
    par = [pts for name, pts in objs.items() if any(p.x > 5.0 for p in pts)]
    assert par, sorted(objs)
    xs = [p.x for pts in par for p in pts]
    assert 6.0 - min(xs) > max(xs) - 6.0, (min(xs), max(xs))
    # and it really is off plumb: a can hanging straight down would be
    # symmetric about its anchor to the millimetre
    assert (6.0 - min(xs)) - (max(xs) - 6.0) > 0.2, (min(xs), max(xs))
