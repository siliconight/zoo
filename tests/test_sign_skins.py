"""Sign-pack library (v0.31): discovery, deterministic pick, fallbacks."""
import json

import pytest

from zoo_keeper.core import skins


def _mk_pack(root, name):
    d = root / name
    d.mkdir(parents=True)
    (d / f"{name}_albedo.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")
    (d / f"{name}_emissive.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")
    (d / f"{name}.pack.json").write_text(json.dumps({
        "schema": "pixelcoat-pack/1", "asset_id": name,
        "maps": {"albedo": f"{name}_albedo.png",
                 "emissive": f"{name}_emissive.png"},
        "meters_per_tile": 1.0}))
    return d


def test_find_sign_packs_theme_dir_wins(tmp_path):
    _mk_pack(tmp_path / "signs_delco", "sign_pawn_delco")
    _mk_pack(tmp_path / "signs_delco", "sign_deli_delco")
    _mk_pack(tmp_path / "signs", "sign_generic")
    packs = skins.find_sign_packs(str(tmp_path), "delco")
    assert [p["id"] for p in packs] == ["sign_deli_delco", "sign_pawn_delco"]
    assert all("emissive" in p["maps"] for p in packs)


def test_find_sign_packs_fallbacks(tmp_path):
    assert skins.find_sign_packs(str(tmp_path), "delco") == []
    assert skins.find_sign_packs("", "delco") == []
    _mk_pack(tmp_path / "signs", "sign_generic")
    packs = skins.find_sign_packs(str(tmp_path), "delco")
    assert [p["id"] for p in packs] == ["sign_generic"]


def test_pick_pack_deterministic_and_spread(tmp_path):
    for n in ("sign_a", "sign_b", "sign_c"):
        _mk_pack(tmp_path / "signs_delco", n)
    packs = skins.find_sign_packs(str(tmp_path), "delco")
    first = skins.pick_pack(packs, "pawn/ext_1_S_sign_1")
    again = skins.pick_pack(packs, "pawn/ext_1_S_sign_1")
    assert first["id"] == again["id"]
    picks = {skins.pick_pack(packs, f"bld_{i}/sign")["id"] for i in range(24)}
    assert len(picks) > 1  # different anchors do land on different signs
    assert skins.pick_pack([], "anything") is None
