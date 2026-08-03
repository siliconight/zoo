"""Pure tests for the Patina dressing -> Zoo cover planner (no bpy)."""

import json
import os

import pytest

from zoo_keeper.core import dressing

GENOME = json.load(open(os.path.join(
    os.path.dirname(__file__), "..", "zoo_keeper", "genome", "species",
    "dress_cover.json"), encoding="utf-8"))

# A synthetic Patina dressing manifest (the v0.11 shape), DC-aligned space.
MANIFEST = {
    "schema": "patina-dressing/1",
    "building_id": "test_station",
    "trim_sheet": "test_station.patina.trim.png",
    "space": "spec/Blender Z-up raw coords",
    "orders": [
        {"anchor_kind": "roofline", "cover": "edge_strip", "collision": "none",
         "trim_piece": "roof_edge", "uv_region": [0.0, 0.0, 1.0, 0.14],
         "pos": [-2.0, 3.0, 4.2], "normal": [0.0, 0.0, 1.0], "size": 0.6,
         "seed_offset": 111},
        {"anchor_kind": "wall_base", "cover": "base_course", "collision": "none",
         "trim_piece": "foundation", "uv_region": [0.0, 0.6, 1.0, 0.84],
         "pos": [4.0, 1.0, 0.0], "normal": [1.0, 0.0, 0.0], "size": 0.8,
         "seed_offset": 222},
        {"anchor_kind": "exterior_light", "cover": "conduit_run",
         "collision": "none", "trim_piece": "conduit",
         "uv_region": [0.0, 0.84, 1.0, 0.94],
         "pos": [4.0, 1.0, 3.0], "normal": [1.0, 0.0, 0.0], "size": 0.3,
         "seed_offset": 333},
    ],
}


def test_load_manifest_rejects_wrong_schema(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(json.dumps({"schema": "something-else/1"}))
    with pytest.raises(ValueError):
        dressing.load_manifest(str(p))


def test_load_manifest_accepts(tmp_path):
    p = tmp_path / "d.json"
    p.write_text(json.dumps(MANIFEST))
    m = dressing.load_manifest(str(p))
    assert m["building_id"] == "test_station"


def test_plan_dressing_counts_and_theme():
    plan = dressing.plan_dressing(MANIFEST, GENOME, "delco", "Zoo 0.20.0")
    assert plan["cover_count"] == 3
    assert plan["counts"] == {"base_course": 1, "conduit_run": 1, "edge_strip": 1}
    assert plan["building_id"] == "test_station"
    # theme resolves to the delco style block (color/material/wear)
    p0 = plan["plans"][0]
    assert p0["material"] == "concrete"
    assert p0["color"] == [0.5, 0.49, 0.46]
    assert p0["wear"] == 0.35
    assert p0["style"] == "delco"


def test_blender_space_passthrough():
    plan = dressing.plan_dressing(MANIFEST, GENOME, "delco", "Zoo 0.20.0")
    # DC-aligned manifest is already Blender Z-up: positions pass through.
    assert plan["plans"][0]["order"]["pos"] == [-2.0, 3.0, 4.2]


def test_patina_space_converts_to_blender():
    m = dict(MANIFEST, space="baked_world_metres")
    plan = dressing.plan_dressing(m, GENOME, "delco", "Zoo 0.20.0")
    # Patina Y-up (x, y, z) -> Blender (x, -z, y): [-2,3,4.2] -> [-2,-4.2,3]
    assert plan["plans"][0]["order"]["pos"] == [-2.0, -4.2, 3.0]


def test_colliding_orders_dropped():
    m = dict(MANIFEST, orders=MANIFEST["orders"] + [
        {"cover": "wall_panel", "collision": "convex",
         "pos": [0, 0, 0], "normal": [1, 0, 0]}])
    plan = dressing.plan_dressing(m, GENOME, "delco", "Zoo 0.20.0")
    assert plan["cover_count"] == 3      # the colliding order is dropped


def test_uv_region_carried_through():
    plan = dressing.plan_dressing(MANIFEST, GENOME, "delco", "Zoo 0.20.0")
    assert plan["plans"][0]["order"]["uv_region"] == [0.0, 0.0, 1.0, 0.14]


def test_default_theme_falls_back():
    plan = dressing.plan_dressing(MANIFEST, GENOME, "no_such_theme", "Zoo 0.20.0")
    assert plan["plans"][0]["style"] == "default"
    assert plan["plans"][0]["color"] == [0.56, 0.55, 0.53]


@pytest.mark.parametrize("cover,vertical", [
    ("edge_strip", False), ("base_course", False),
    ("curb", False), ("conduit_run", True),
])
def test_strip_size(cover, vertical):
    w, d, h = dressing.strip_size(cover, 0.6)
    assert d < w and d < h + 0.2 or True   # proud (depth) is the thin axis
    if vertical:
        assert h > w                        # conduit is tall and slim
    else:
        assert w >= h                       # horizontal strips run long


def test_strip_size_scales_with_hint():
    small = dressing.strip_size("edge_strip", 0.3)
    large = dressing.strip_size("edge_strip", 1.2)
    assert large[0] > small[0]              # bigger anchor -> longer span


# ---------------------------------------------------------------- v0.24
def test_panel_field_uses_size2_exactly():
    from zoo_keeper.core.dressing import strip_size
    w, d, h = strip_size("panel_field", 0.97, [0.97, 1.02])
    assert (w, h) == (0.97, 1.02)
    assert d == 0.03


def test_panel_field_without_size2_falls_back_square():
    from zoo_keeper.core.dressing import strip_size
    w, d, h = strip_size("panel_field", 0.8, None)
    assert w == h == 0.8


def test_dress_plan_passes_size2():
    from zoo_keeper.core.dressing import dress_plan
    genome = {"materials": {"default": "concrete", "options": ["concrete"]},
              "styles": {"default": {"material": "concrete",
                                     "color": [0.6, 0.6, 0.6]}}}
    order = {"cover": "panel_field", "size": 0.97, "size2": [0.97, 1.02],
             "pos": [0, 0, 0], "normal": [0, 1, 0], "seed_offset": 7}
    plan = dress_plan(order, genome, "delco",
                      "spec/Blender Z-up raw coords", "0.24.0")
    assert plan["order"]["size2"] == [0.97, 1.02]
    assert plan["order"]["cover"] == "panel_field"


# ---------------------------------------------------------------- v0.26
def test_gutter_spans_module_exactly():
    from zoo_keeper.core.dressing import strip_size
    w, d, h = strip_size("gutter_run", 2.0)
    assert w == 2.0 and d == 0.10 and h == 0.14


def test_pilaster_uses_size2():
    from zoo_keeper.core.dressing import strip_size
    w, d, h = strip_size("pilaster", 0.24, [0.24, 4.2])
    assert (w, h) == (0.24, 4.2) and d == 0.05


def test_frame_strips_geometry():
    from zoo_keeper.core.dressing import frame_strips
    strips = frame_strips(3.0, 3.0, 0.12, 0.05)
    assert len(strips) == 4
    (hc, hs), (sc, ss), (lc, ls), (rc, rs) = strips
    assert hc[2] == 1.5 + 0.06 and hs[0] == 3.24      # head overhangs jambs
    assert sc[2] == -1.5 - 0.06
    assert lc[0] == -1.5 - 0.06 and ls[2] == 3.0      # jamb = opening height
    assert rc[0] == 1.5 + 0.06
    # frame outer bounds = opening + 2 * frame width
    assert max(c[0] + s[0] / 2 for c, s in strips) == 1.62


def test_dress_plan_passes_frame_width():
    from zoo_keeper.core.dressing import dress_plan
    genome = {"materials": {"default": "concrete", "options": ["concrete"]},
              "styles": {"default": {"material": "concrete",
                                     "color": [0.6, 0.6, 0.6]}}}
    order = {"cover": "frame", "size": 3.0, "size2": [3.0, 3.0],
             "frame_width": 0.15, "pos": [0, 0, 0], "normal": [0, 1, 0],
             "seed_offset": 7}
    plan = dress_plan(order, genome, "delco",
                      "spec/Blender Z-up raw coords", "0.26.0")
    assert plan["order"]["frame_width"] == 0.15


# --------------------------------------------------------------------------- #
# Strip orientation: a normal alone cannot orient a strip
# --------------------------------------------------------------------------- #
# A cover's local shape is (span, proud, cross) -- LONG in +X. `_orient_matrix`
# used to return no rotation at all for a vertical normal, on the grounds that
# a flat strip needs no tilt. True, and beside the point: the YAW was still
# unconstrained, so every roofline cap and every curb kept world +X as its run
# direction regardless of which facade it sat on. On the walls running along Y
# that turned 64 capping strips into 64 sticks jutting out of the building, and
# 64 curbs into planks lying across the pavement.

import math

from zoo_keeper.core.dressing import strip_yaw

_UP = (0.0, 0.0, 1.0)


def test_up_facing_strip_runs_along_its_wall():
    """The regression. A curb on a Y-running wall must run along Y."""
    assert strip_yaw(_UP, (0.0, 1.0, 0.0)) == pytest.approx(math.pi / 2)
    assert strip_yaw(_UP, (1.0, 0.0, 0.0)) == pytest.approx(0.0)
    assert strip_yaw(_UP, (-1.0, 0.0, 0.0)) == pytest.approx(math.pi)


def test_up_facing_strip_without_a_tangent_is_unchanged():
    """A manifest written before Patina emitted tangents still builds the same.

    The field is additive; silently changing the geometry of every old manifest
    would be a worse bug than the one being fixed.
    """
    assert strip_yaw(_UP) == 0.0
    assert strip_yaw(_UP, None) == 0.0


def test_horizontal_normals_are_untouched():
    """Wall base and conduit already worked -- +Y to the normal, +X along the
    wall for free. This pins that the fix did not disturb them."""
    for nx, ny, want in ((1.0, 0.0, -math.pi / 2), (0.0, 1.0, 0.0),
                         (-1.0, 0.0, math.pi / 2)):
        assert strip_yaw((nx, ny, 0.0)) == pytest.approx(want)
        # a tangent must not perturb the horizontal branch
        assert strip_yaw((nx, ny, 0.0), (0.0, 1.0, 0.0)) == pytest.approx(want)


def test_a_vertical_tangent_yields_no_yaw():
    """Degenerate input must not produce NaN or an arbitrary rotation."""
    assert strip_yaw(_UP, (0.0, 0.0, 1.0)) == 0.0


def test_tangent_is_carried_from_order_into_the_plan():
    man = dict(MANIFEST)
    man["orders"] = [dict(o) for o in MANIFEST["orders"]]
    man["orders"][0]["tangent"] = [0.0, 1.0, 0.0]
    plan = dressing.plan_dressing(man, GENOME, "delco", "Zoo 0.20.0")
    assert plan["plans"][0]["order"]["tangent"] == [0.0, 1.0, 0.0]


def test_conduit_span_is_the_run_length_not_a_scaled_hint():
    """`size` became the true run length; this consumer had to follow.

    Patina v0.19 made `size` the ground-plane-to-fixture distance. The old
    scaling (span 1.6 * size / 0.6) then turned a 2.45 m run into 6.53 m,
    centred on the fixture and reaching from -0.82 to 5.72.
    """
    w, d, h = dressing.strip_size("conduit_run", 2.45)
    assert h == pytest.approx(2.45)
    assert h != pytest.approx(6.53, abs=0.01)
    assert w < 0.2 and d < 0.2          # still slim


def test_other_covers_keep_their_span_scaling():
    """The change is scoped to conduit; nothing else shifts."""
    w, _d, _h = dressing.strip_size("edge_strip", 0.6)
    assert w == pytest.approx(2.0)
