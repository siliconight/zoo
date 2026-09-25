"""Zoo chooses the wet variant of a skin pack (no bpy).

Pixelcoat has written `wet_albedo`, `wet_roughness` and `wetness` into every
ground pack since 0.47.0 and nothing read them: `MAP_KEYS` is a fixed
allow-list and the wet names were not in it. This is the chooser, and it works
at RESOLUTION time -- `load_pack` returns a pack whose `albedo` and `roughness`
point at the wet files, so `bpylayer/materials.py` is untouched and the
exporter bakes the wet textures exactly as it bakes the dry ones.

WHY THAT SHAPE. LF 0.110.0 measured a wet `next_pass` at 2.27-4.29 us per ADDED
draw call -- +8.05 ms at the worst station of a real package -- because a
second pass re-rasterises the same triangles. Swapping which texture a material
samples adds no material and no submission. The structural half of that claim
is asserted below as "the map count does not change"; the measured half is a
rebuilt package whose draw calls read the same as dry, which needs Level
Factory to turn this on and is not this file.
"""

import json
import os

import pytest

from zoo_keeper.core import skins


def _touch(path, body=b"\x89PNG stub"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(body)


def _pack(root, dirname, asset_id, maps, missing=()):
    """A pack whose manifest names `maps`; anything in `missing` is named but
    not written, which is the case the dry resolver already guards."""
    d = os.path.join(root, dirname)
    os.makedirs(d, exist_ok=True)
    files = {k: f"{asset_id}_{k}.png" for k in maps}
    for k, fname in files.items():
        if k not in missing:
            _touch(os.path.join(d, fname), f"pixels:{k}".encode())
    with open(os.path.join(d, f"{asset_id}.pack.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": skins.PACK_SCHEMA, "asset_id": asset_id,
                   "maps": files, "meters_per_tile": 2.0,
                   "tileable": ["x", "y"]}, f)
    return d


GROUND = ["albedo", "roughness", "wetness", "wet_albedo", "wet_roughness"]
WALL = ["albedo", "roughness", "normal"]


# --------------------------------------------------------------------------- #
# Choosing
# --------------------------------------------------------------------------- #

def test_asking_wet_points_albedo_and_roughness_at_the_wet_files(tmp_path):
    root = str(tmp_path)
    _pack(root, "asphalt_delco_1997", "asphalt_delco", GROUND)
    wet = skins.find_pack(root, "asphalt", "delco_1997", wet=True)
    assert os.path.basename(wet["maps"]["albedo"]) == \
        "asphalt_delco_wet_albedo.png"
    assert os.path.basename(wet["maps"]["roughness"]) == \
        "asphalt_delco_wet_roughness.png"


def test_not_asking_leaves_the_dry_maps_exactly_as_they_were(tmp_path):
    """The regression guard. Every build that does not ask for wet must
    resolve byte-for-byte what it always did."""
    root = str(tmp_path)
    _pack(root, "asphalt_delco_1997", "asphalt_delco", GROUND)
    dry = skins.find_pack(root, "asphalt", "delco_1997")
    assert os.path.basename(dry["maps"]["albedo"]) == \
        "asphalt_delco_albedo.png"
    assert os.path.basename(dry["maps"]["roughness"]) == \
        "asphalt_delco_roughness.png"
    assert dry["wet"] == ()


def test_a_pack_with_no_wet_maps_is_unaffected_by_asking(tmp_path):
    """THE PROPERTY THAT MAKES A WHOLE-BUILD FLAG SAFE. Walls, glass and
    interiors carry no wet maps, so a wet build dresses the ground and leaves
    the rest alone without anybody listing which is which -- the decision
    already lives in the grammar, and restating it here would be a second
    place to get it wrong."""
    root = str(tmp_path)
    _pack(root, "brick_delco_1997", "brick_delco", WALL)
    dry = skins.find_pack(root, "brick", "delco_1997")
    wet = skins.find_pack(root, "brick", "delco_1997", wet=True)
    assert dry["maps"] == wet["maps"]
    assert wet["wet"] == ()


def test_the_marker_names_what_was_substituted(tmp_path):
    """A caller that must not silently ship the dry surface can check this
    rather than infer it from the pack id."""
    root = str(tmp_path)
    _pack(root, "asphalt_delco_1997", "asphalt_delco", GROUND)
    wet = skins.find_pack(root, "asphalt", "delco_1997", wet=True)
    assert set(wet["wet"]) == {"albedo", "roughness"}


def test_only_the_maps_that_exist_are_substituted(tmp_path):
    """A pack naming a wet map it did not write falls back to the dry one --
    the same rule the dry maps already follow, for the same reason: a resolved
    path that is not on disk is worse than the surface it replaced."""
    root = str(tmp_path)
    _pack(root, "asphalt_delco_1997", "asphalt_delco", GROUND,
          missing=("wet_roughness",))
    wet = skins.find_pack(root, "asphalt", "delco_1997", wet=True)
    assert os.path.basename(wet["maps"]["albedo"]).startswith("asphalt_delco_wet")
    assert os.path.basename(wet["maps"]["roughness"]) == \
        "asphalt_delco_roughness.png"
    assert wet["wet"] == ("albedo",)


# --------------------------------------------------------------------------- #
# What must NOT change, because the whole point is that it costs nothing
# --------------------------------------------------------------------------- #

def test_the_map_count_does_not_change(tmp_path):
    """The structural half of the draw-call claim. A wet pack resolves the
    SAME number of maps -- it swaps which image two of them point at. No extra
    texture slot, so no extra material, so no extra submission. The measured
    half is a rebuilt package whose draw calls read the same as dry."""
    root = str(tmp_path)
    _pack(root, "asphalt_delco_1997", "asphalt_delco", GROUND)
    dry = skins.find_pack(root, "asphalt", "delco_1997")
    wet = skins.find_pack(root, "asphalt", "delco_1997", wet=True)
    assert set(dry["maps"]) == set(wet["maps"])


def test_the_pack_identity_and_scale_are_untouched(tmp_path):
    root = str(tmp_path)
    _pack(root, "asphalt_delco_1997", "asphalt_delco", GROUND)
    dry = skins.find_pack(root, "asphalt", "delco_1997")
    wet = skins.find_pack(root, "asphalt", "delco_1997", wet=True)
    for key in ("id", "dir", "meters_per_tile", "tileable", "tintable"):
        assert dry[key] == wet[key], key


def test_the_wet_maps_are_not_in_MAP_KEYS(tmp_path):
    """They are resolved by substitution, not by being listed. Adding them to
    MAP_KEYS would hand every consumer two more textures to wire and would be
    the extra material this design exists to avoid."""
    assert "wet_albedo" not in skins.MAP_KEYS
    assert "wet_roughness" not in skins.MAP_KEYS
    assert set(skins.WET_SUBSTITUTIONS) <= set(skins.MAP_KEYS)


# --------------------------------------------------------------------------- #
# The material name, read as text (this suite has no bpy)
# --------------------------------------------------------------------------- #

def _materials_source():
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, "..", "zoo_keeper", "bpylayer", "materials.py")
    with open(p, encoding="utf-8") as f:
        return f.read()


def test_a_wet_material_is_named_apart_from_its_dry_twin():
    """`make_material` caches on the name, so without a suffix a wet and a dry
    build in one process would collide and the second would silently get the
    first's material. The name also travels into the GLB, where Level
    Factory's greybox-skin gate reads it."""
    src = _materials_source()
    assert 'if pack.get("wet"):' in src
    assert 'skin_name += "_wet"' in src


def test_the_suffix_is_conditional_on_a_substitution_having_happened():
    """A wet build must not rename every wall it left dry -- the marker is
    empty for a pack that carried no wet maps, and the suffix hangs off it."""
    src = _materials_source()
    i = src.index('if pack.get("wet"):')
    assert 'skin_name += "_wet"' in src[i:i + 200]


def test_the_flag_reaches_the_resolver():
    src = _materials_source()
    assert 'wet=_SKINS["wet"]' in src
    assert '_SKINS = {"dir": None, "theme": "delco", "wet": False}' in src
