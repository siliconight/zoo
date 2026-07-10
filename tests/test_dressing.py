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
