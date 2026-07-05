import json
import os
import tempfile

from zoo_keeper.core import exhibit, layout

ASSETS = [
    {"name": "desk", "glb": "desk.glb", "w": 1.2, "d": 0.8, "h": 0.74,
     "category": "furniture"},
    {"name": "chair", "glb": "chair.glb", "w": 0.5, "d": 0.5, "h": 0.9,
     "category": "furniture"},
    {"name": "atm", "glb": "atm.glb", "w": 0.6, "d": 0.55, "h": 1.45,
     "category": "machine"},
    {"name": "cash", "glb": "cash.glb", "w": 0.16, "d": 0.07, "h": 0.02,
     "category": "loot"},
]


def test_zoo_grid_places_all_no_overlap():
    plan = layout.arrange(ASSETS, scheme="zoo", cols=2, gap=0.5)
    assert len(plan["members"]) == 4
    # uniform grid cell = biggest footprint + gap; 2 cols -> centers 1 apart
    xs = sorted({m["pos"][0] for m in plan["members"]})
    assert len(xs) == 2 and xs[1] - xs[0] >= 1.2  # cells don't collide
    assert all(m["pos"][1] == 0.0 for m in plan["members"])  # on the floor


def test_zoo_has_scale_reference():
    plan = layout.arrange(ASSETS, scheme="zoo")
    markers = [p for p in plan["props"] if p["type"] == "marker"]
    labels = {p["label"] for p in markers}
    assert "1.8 m" in labels and "1 m" in labels


def test_museum_pedestals_and_labels():
    plan = layout.arrange(ASSETS, scheme="museum", cols=2)
    peds = [p for p in plan["props"] if p["type"] == "pedestal"]
    labs = [p for p in plan["props"] if p["type"] == "label"]
    assert len(peds) == 4 and len(labs) == 4
    # every asset sits on top of a pedestal (y == pedestal height)
    assert all(m["pos"][1] == layout.PED_H for m in plan["members"])
    assert any("desk" in p["text"] for p in labs)


def test_arrange_sorts_by_category_then_size():
    order = [m["name"] for m in layout.arrange(ASSETS, cols=4)["members"]]
    # grouped by category (furniture, loot, machine), biggest first in group
    assert order.index("desk") < order.index("chair")  # furniture, desk bigger


def test_empty_is_safe():
    plan = layout.arrange([], scheme="zoo")
    assert plan["members"] == [] and plan["props"] == []


def _write_meta(d, fname, meta):
    with open(os.path.join(d, fname), "w") as f:
        json.dump(meta, f)


def test_scan_handles_generated_and_ingested():
    d = tempfile.mkdtemp()
    # generated (nested)
    _write_meta(d, "desk_ab12.meta.json", {
        "zoo": {"specimen_id": "desk_ab12"},
        "plan": {"species": "desk",
                 "dimensions": {"width": 1.2, "depth": 0.8, "height": 0.74}},
        "genome": {"species": "desk"},
        "files": {"glb": "desk_ab12.glb"}})
    # ingested (flat)
    _write_meta(d, "old_lamp.meta.json", {
        "specimen_id": "old_lamp", "source": "ingested",
        "species_hint": "lamp",
        "dimensions": {"width": 0.3, "depth": 0.3, "height": 1.4}})
    # zero-dim asset -> skipped
    _write_meta(d, "broken.meta.json", {
        "specimen_id": "broken",
        "dimensions": {"width": 0, "depth": 0, "height": 0}})

    assets = exhibit.scan_collection(d)
    names = {a["name"] for a in assets}
    assert names == {"desk_ab12", "old_lamp"}          # broken skipped
    lamp = next(a for a in assets if a["name"] == "old_lamp")
    assert lamp["glb"] == "old_lamp.glb" and lamp["category"] == "lamp"
    desk = next(a for a in assets if a["name"] == "desk_ab12")
    assert desk["glb"] == "desk_ab12.glb" and desk["category"] == "desk"


def test_build_exhibit_manifest_shape():
    m = exhibit.build_exhibit(ASSETS, scheme="museum", name="kit",
                              tool_version="0.11.0")
    assert m["scheme"] == "museum" and m["asset_count"] == 4
    assert m["exhibit"] == "kit" and "bounds" in m
