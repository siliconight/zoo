"""Pure tests for the Pixelcoat skin-library resolver (no bpy)."""

import json
import os

import pytest

from zoo_keeper.core import skins


def _touch(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"\x89PNG stub")


def _pack(root, dirname, asset_id, maps, meters_per_tile=1.0,
          tileable="both", missing=()):
    d = os.path.join(root, dirname)
    os.makedirs(d, exist_ok=True)
    files = {k: f"{asset_id}_{k}.png" for k in maps}
    for k, fname in files.items():
        if k not in missing:
            _touch(os.path.join(d, fname))
    manifest = {"schema": skins.PACK_SCHEMA, "asset_id": asset_id,
                "maps": files, "meters_per_tile": meters_per_tile,
                "tileable": tileable}
    with open(os.path.join(d, f"{asset_id}.pack.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f)
    return d


def test_theme_dir_wins_over_kind_dir(tmp_path):
    root = str(tmp_path)
    _pack(root, "metal_delco", "metal_night", ["albedo", "normal"])
    _pack(root, "metal", "metal_generic", ["albedo"])
    pack = skins.find_pack(root, "metal", "delco")
    assert pack["id"] == "metal_night"
    assert set(pack["maps"]) == {"albedo", "normal"}


def test_kind_dir_fallback_for_other_theme(tmp_path):
    root = str(tmp_path)
    _pack(root, "metal_delco", "metal_night", ["albedo"])
    _pack(root, "metal", "metal_generic", ["albedo"])
    assert skins.find_pack(root, "metal", "roosevelt")["id"] == "metal_generic"


def test_no_match_returns_none(tmp_path):
    assert skins.find_pack(str(tmp_path), "plaster", "delco") is None
    assert skins.find_pack(None, "plaster", "delco") is None


def test_missing_optional_maps_dropped(tmp_path):
    d = _pack(str(tmp_path), "wood", "wood_a",
              ["albedo", "normal", "roughness"], missing=("roughness",))
    pack = skins.load_pack(d)
    assert set(pack["maps"]) == {"albedo", "normal"}


def test_manifest_without_albedo_file_raises(tmp_path):
    d = _pack(str(tmp_path), "glass", "glass_a", ["albedo"],
              missing=("albedo",))
    with pytest.raises(ValueError):
        skins.load_pack(d)


def test_legacy_albedo_dir_without_manifest(tmp_path):
    d = os.path.join(str(tmp_path), "concrete")
    _touch(os.path.join(d, "wall_albedo.png"))
    _touch(os.path.join(d, "wall_normal.png"))
    pack = skins.load_pack(d)
    assert pack["id"] == "wall"
    assert set(pack["maps"]) == {"albedo", "normal"}
    assert pack["meters_per_tile"] == 1.0
    # empty dir (no albedo, no manifest) is a quiet miss, not an error
    empty = os.path.join(str(tmp_path), "paper")
    os.makedirs(empty)
    assert skins.load_pack(empty) is None


def test_meters_per_tile_carried(tmp_path):
    d = _pack(str(tmp_path), "metal", "metal_a", ["albedo"],
              meters_per_tile=2.0)
    assert skins.load_pack(d)["meters_per_tile"] == 2.0


def test_library_report(tmp_path):
    root = str(tmp_path)
    _pack(root, "metal_delco", "metal_night", ["albedo", "normal"],
          meters_per_tile=2.0)
    d = os.path.join(root, "concrete")
    _touch(os.path.join(d, "wall_albedo.png"))
    report = skins.library_report(root, "delco")
    assert set(report["resolved"]) == {"metal", "concrete"}
    assert report["resolved"]["metal"]["meters_per_tile"] == 2.0
    assert "wood" in report["flat_fallback"]
    assert report["theme"] == "delco"
