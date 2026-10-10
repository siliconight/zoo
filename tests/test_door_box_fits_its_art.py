"""A door box wears its business's band as the pack asks and at the art's own shape (1.94.0).

Roadmap 223. Pixelcoat 0.62.0 letters a business's sign smooth, in Blue Highway Condensed, at its
band's 6:1, and asks for `linear` sampling. The door box that wears the same pack (1.79.0) sampled
every pack Closest -- `skins.load_pack` dropped the hint -- and mapped the art 0..1 across a face
of its own shape: 0.6 m tall and 3.33 to 8.33 times as wide across the library's 95 door signs,
4.67 at the median. A 6:1 band's letters would stand 28% too tall on that median door.
"""
import json
import os
import struct
import zlib

import pytest

from zoo_keeper.core import skins

HERE = os.path.dirname(os.path.abspath(__file__))


def _png(path, w, h, rgb=(20, 60, 30)):
    """A flat RGB PNG, written with zlib and struct alone: Blender's Python carries no PIL."""
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))
    raw = (b"\x00" + bytes(rgb) * w) * h
    magic = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])   # not skins'; a fixture
    path.write_bytes(magic                                            # owes the code nothing
                     + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def _pack(tmp_path, w=1536, h=256, interpolation="linear"):
    d = tmp_path / "sign_jawns"
    d.mkdir()
    _png(d / "sign_jawns_albedo.png", w, h)
    hints = {"extension": "extend", "emissive": True}
    if interpolation:
        hints["interpolation"] = interpolation
    (d / "sign_jawns.pack.json").write_text(json.dumps({
        "schema": "pixelcoat-pack/2", "asset_id": "sign_jawns",
        "maps": {"albedo": "sign_jawns_albedo.png"}, "import_hints": hints}), encoding="utf-8")
    return d


def test_a_png_s_shape_is_read_from_its_header(tmp_path):
    d = _pack(tmp_path)
    assert skins.png_aspect(str(d / "sign_jawns_albedo.png")) == 6.0
    assert skins.png_aspect(str(d / "sign_jawns.pack.json")) is None


def test_the_pack_says_how_to_sample_it_and_its_shape(tmp_path):
    """FAILS on 1.93.0: `load_pack` dropped the hint and never measured the art."""
    p = skins.load_pack(str(_pack(tmp_path)))
    assert p["interpolation"] == "linear" and p["art_aspect"] == 6.0


def test_a_pack_that_does_not_say_is_sampled_as_pixels(tmp_path):
    p = skins.load_pack(str(_pack(tmp_path, 512, 128, interpolation=None)))
    assert p["interpolation"] == "nearest" and p["art_aspect"] == 4.0


def test_a_face_of_the_art_s_shape_takes_it_whole():
    assert skins.fit_uv(-1.8, -0.3, 3.6, 0.6, 6.0) == (0.0, 0.0)
    assert skins.fit_uv(1.8, 0.3, 3.6, 0.6, 6.0) == (1.0, 1.0)
    assert skins.fit_uv(1.8, 0.3, 3.6, 0.6, None) == (1.0, 1.0)


def test_a_door_box_shows_a_band_s_art_at_its_own_shape():
    """The median door box, 2.8 x 0.6 (4.67:1), and a 6:1 band: the art spans the face's width,
    is centred, and is 0.467 m of its 0.6 m height -- past it, the UV leaves 0..1 and the sign's
    EXTEND sampling repeats the art's edge. FAILS on 1.93.0: there is no `fit_uv`."""
    w, h, a = 2.8, 0.6, 6.0
    u0, v0 = skins.fit_uv(-w / 2, -h / 2, w, h, a)
    u1, v1 = skins.fit_uv(w / 2, h / 2, w, h, a)
    assert (u0, u1) == (0.0, 1.0)
    assert v0 == pytest.approx(0.5 - 0.5 * (w / h) ** -1 * a) and v1 == pytest.approx(1 - v0)
    # the art keeps its own shape: metres a UV unit across over metres a UV unit up
    assert (w / (u1 - u0)) / (h / (v1 - v0)) == pytest.approx(a)


def test_a_face_wider_than_the_art_centres_it_across():
    w, h, a = 5.0, 0.6, 6.0                              # 8.33:1, the widest door sign
    u0, v0 = skins.fit_uv(-w / 2, -h / 2, w, h, a)
    u1, v1 = skins.fit_uv(w / 2, h / 2, w, h, a)
    assert (v0, v1) == (0.0, 1.0) and u0 < 0.0 < 1.0 < u1
    assert (w / (u1 - u0)) / (h / (v1 - v0)) == pytest.approx(a)


def test_the_sign_material_samples_as_the_pack_asks():
    src = open(os.path.join(HERE, "..", "zoo_keeper", "bpylayer", "materials.py"),
               encoding="utf-8").read()
    assert 'filt = "Linear" if pack.get("interpolation") == "linear" else "Closest"' in src
    box = open(os.path.join(HERE, "..", "zoo_keeper", "recipes", "sign_box.py"),
               encoding="utf-8").read()
    assert '_planar_uv_fit(face, w, h, pack.get("art_aspect"))' in box


def test_bpy_the_door_box_exports_a_filtered_band(tmp_path):
    """Built, the face's texture leaves in the GLB with a LINEAR sampler: Level Factory pins a
    texture every sampler filters to compressed with mips (`FILTERED_TEX_PINS`)."""
    pytest.importorskip("bpy")
    import struct
    from zoo_keeper.bpylayer import build
    pack = _pack(tmp_path)
    manifest = {"light_manifest_version": "1.1.0", "building_id": "door_bpy",
                "space": "Blender Z-up, meters", "anchors": [
                    {"id": "ext_0_S_sign", "type": "sign", "source": "derived",
                     "pos": [0.0, -0.2, 2.55], "rot_y": 270.0, "size": [2.8, 0.6]}]}
    out = tmp_path / "out"
    build.build_fixtures(manifest, str(out), theme="delco",
                         options={"save_blend": False, "sign_pack": str(pack)})
    index = json.loads((out / "door_bpy_fixtures.built.json").read_text(encoding="utf-8"))
    raw = (out / index["files"]["glb"]).read_bytes()
    ln, kind = struct.unpack_from("<I4s", raw, 12)
    assert kind == b"JSON"
    j = json.loads(raw[20:20 + ln])
    faces = [m for m in j["materials"] if m["name"].endswith("_Face")]
    assert faces, [m["name"] for m in j["materials"]]
    tex = faces[0]["pbrMetallicRoughness"]["baseColorTexture"]["index"]
    sampler = j["samplers"][j["textures"][tex]["sampler"]]
    assert sampler.get("magFilter") == 9729, sampler            # LINEAR, not NEAREST (9728)
