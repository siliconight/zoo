"""Tintable packs: the achromatic-by-intent flag and its cache key (no bpy).

Why these tests exist. `make_material` discards the genome's per-specimen
colour the moment a pack resolves -- all objects of a kind share one cached
material. Correct for a brick wall, wrong for a bumper. The fix cannot key on
material KIND, because `metal` serves both a rusted storefront facade and 42
prop species, so it keys on the PACK: a grammar declares `tintable`,
Pixelcoat writes it into the manifest, Zoo reads it here.

The shader-graph half of that lives behind bpy and is covered by
`tools/tint_probe.py`, not by these tests. What IS covered here is every
decision made before a node is created.
"""

import json
import os

import pytest

from zoo_keeper.core import skins


def _touch(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"\x89PNG stub")


def _pack(root, dirname, asset_id, tintable=None):
    d = os.path.join(root, dirname)
    os.makedirs(d, exist_ok=True)
    _touch(os.path.join(d, f"{asset_id}_albedo.png"))
    manifest = {"schema": skins.PACK_SCHEMA, "asset_id": asset_id,
                "maps": {"albedo": f"{asset_id}_albedo.png"},
                "meters_per_tile": 1.0, "tileable": "both"}
    if tintable is not None:
        manifest["tintable"] = tintable
    with open(os.path.join(d, f"{asset_id}.pack.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f)
    return d


def test_tintable_true_is_surfaced(tmp_path):
    root = str(tmp_path)
    _pack(root, "plastic_delco", "plastic_neutral", tintable=True)
    assert skins.find_pack(root, "plastic", "delco")["tintable"] is True


def test_tintable_false_is_surfaced(tmp_path):
    root = str(tmp_path)
    _pack(root, "metal_delco", "metal_rusted_street", tintable=False)
    assert skins.find_pack(root, "metal", "delco")["tintable"] is False


def test_pack_written_before_0_13_defaults_to_not_tintable(tmp_path):
    """THE COMPATIBILITY CASE. Every pack on disk today predates the flag.
    A missing key must mean False, or the first build after this patch
    repaints every skinned surface by the mesh colour."""
    root = str(tmp_path)
    _pack(root, "brick_delco", "brick_delco", tintable=None)
    pack = skins.find_pack(root, "brick", "delco")
    assert "tintable" in pack, "the key must be present even when absent from disk"
    assert pack["tintable"] is False


def test_legacy_manifestless_pack_is_not_tintable(tmp_path):
    """The 0.1-era layout has no manifest at all to carry the flag."""
    root = str(tmp_path)
    d = os.path.join(root, "wood_delco")
    _touch(os.path.join(d, "wood_delco_albedo.png"))
    assert skins.find_pack(root, "wood", "delco")["tintable"] is False


def test_tintable_is_coerced_to_a_bool(tmp_path):
    """A hand-edited manifest can carry a truthy string. The consumer branches
    on identity (`is True`), so a leaked 'false' string would tint."""
    root = str(tmp_path)
    _pack(root, "plastic_delco", "p", tintable="false")
    got = skins.find_pack(root, "plastic", "delco")["tintable"]
    assert isinstance(got, bool)


# --------------------------------------------------------------------------- #
# The cache key. `bpylayer.materials` imports bpy at module scope, so the key
# function is read with `ast` and exec'd in isolation -- the same technique
# `test_kind_vocabulary.py` uses, and for the same reason.
# --------------------------------------------------------------------------- #

import ast


def _load_tint_key():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(os.path.dirname(here), "zoo_keeper", "bpylayer",
                       "materials.py")
    tree = ast.parse(open(src, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_tint_key":
            mod = ast.Module(body=[node], type_ignores=[])
            ast.fix_missing_locations(mod)
            ns = {}
            exec(compile(mod, src, "exec"), ns)
            return ns["_tint_key"]
    raise AssertionError("materials.py has no _tint_key")


def test_tint_key_is_hex_and_stable():
    k = _load_tint_key()
    assert k([1.0, 1.0, 1.0]) == "ffffff"
    assert k([0.0, 0.0, 0.0]) == "000000"
    assert k([0.62, 0.14, 0.14]) == k([0.62, 0.14, 0.14])


def test_two_colours_that_differ_get_two_materials():
    """THE CASE THE REAL DATA WOULD NOT HAVE CAUGHT. vending_machine ships a
    red default and a blue style; if the key collapsed them, the second built
    machine would silently reuse the first one's material."""
    k = _load_tint_key()
    red = k([0.62, 0.14, 0.14])
    blue = k([0.14, 0.26, 0.55])
    assert red != blue


def test_tint_key_clamps_out_of_range():
    """Genome colours are authored by hand and are not validated as 0..1."""
    k = _load_tint_key()
    assert k([2.0, -1.0, 0.5]) == "ff0080"


def test_tint_key_ignores_alpha():
    k = _load_tint_key()
    assert k([0.5, 0.5, 0.5, 1.0]) == k([0.5, 0.5, 0.5])
