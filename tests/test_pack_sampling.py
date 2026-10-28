"""A pack material samples its textures as the pack asks (1.144.0, the factory's roadmap 324).

`skins.load_pack` has read a pack's `interpolation` hint since 1.94.0 and the sign path honoured it; the pack material
(`materials._textured`) hardcoded Closest, so a pack asking for `linear` was sampled nearest anyway -- the retro look's
sampling, kept after realism replaced it. A pack that does not say keeps Closest. FAILS ON 1.143.0.

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_pack_sampling.py'])))"
"""
from __future__ import annotations

import struct
import zlib

import pytest


def _png(path, rgb=(128, 96, 64)):
    """A 2 x 2 RGB PNG, written by hand so the test needs no imaging library."""
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    rows = b"".join(b"\x00" + bytes(rgb) * 2 for _ in range(2))
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))
    return str(path)


def _filters(tmp_path, name, interpolation):
    from zoo_keeper.bpylayer import materials
    maps = {k: _png(tmp_path / ("%s_%s.png" % (name, k))) for k in ("albedo", "roughness", "normal")}
    pack = {"maps": maps, "meters_per_tile": 1.0}
    if interpolation is not None:
        pack["interpolation"] = interpolation
    mat = materials._textured(name, pack, "metal")
    return {n.interpolation for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}


def test_bpy_a_pack_asking_for_linear_is_sampled_linear(tmp_path):
    pytest.importorskip("bpy")
    assert _filters(tmp_path, "zoo_t_linear", "linear") == {"Linear"}


def test_bpy_a_pack_that_does_not_say_keeps_closest(tmp_path):
    pytest.importorskip("bpy")
    assert _filters(tmp_path, "zoo_t_unsaid", None) == {"Closest"}
    assert _filters(tmp_path, "zoo_t_nearest", "nearest") == {"Closest"}
