"""A module's pack textures live beside it, not sixty times inside it.

WHAT THESE TESTS ARE FOR. Blender's GLB writer embeds every image, and Godot
builds a separate GPU texture from every embedded copy -- it does not
deduplicate. MEASURED 2026-09-21 on cold run 9066's shipped package
(`LF_club_block_005.portable-godot`, 215 GLBs), Godot 4.7, GL Compatibility:

    embedded, as shipped      1,841 texture resources   332,867,236 B
    externalised by this      157 texture resources      47,090,266 B

and the twenty-GLB controls that establish the mechanism are in
`core/gltf_textures`'s own docstring.

Every test here fails on a tree without that module, which is the point: on
1.1.1 there is nothing to import.
"""
from __future__ import annotations

import json
import struct

import pytest

from zoo_keeper.core import gltf_textures


def _glb(images, extra_json=None):
    """A minimal but structurally real GLB: one quad, plus ``images`` blobs.

    The quad's vertex data is written BEFORE and AFTER the image views on
    purpose, so a rewrite that compacts the binary chunk has to remap indices
    in both directions to keep the mesh intact.
    """
    pos = struct.pack("<12f", -1, 0, -1, 1, 0, -1, 1, 0, 1, -1, 0, 1)
    idx = struct.pack("<6H", 0, 1, 2, 0, 2, 3)
    blobs = [pos] + list(images) + [idx]
    views, binc = [], bytearray()
    for b in blobs:
        views.append({"buffer": 0, "byteOffset": len(binc), "byteLength": len(b)})
        binc += b + b"\0" * ((-len(b)) % 4)
    doc = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0},
                                    "indices": 1, "material": 0}]}],
        "materials": [{"pbrMetallicRoughness": {
            "baseColorTexture": {"index": 0}}}],
        "textures": [{"source": i} for i in range(len(images))],
        "images": [{"bufferView": 1 + i, "mimeType": "image/png",
                    "name": f"pack_tex_{i}"} for i in range(len(images))],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": 4, "type": "VEC3",
             "min": [-1, 0, -1], "max": [1, 0, 1]},
            {"bufferView": len(blobs) - 1, "componentType": 5123, "count": 6,
             "type": "SCALAR"},
        ],
        "bufferViews": views,
        "buffers": [{"byteLength": len(binc)}],
    }
    if extra_json:
        doc.update(extra_json)
    js = json.dumps(doc, separators=(",", ":")).encode("utf-8")
    js += b" " * ((-len(js)) % 4)
    out = struct.pack("<III", 0x46546C67, 2,
                      12 + 8 + len(js) + 8 + len(binc))
    out += struct.pack("<II", len(js), 0x4E4F534A) + js
    out += struct.pack("<II", len(binc), 0x004E4942) + binc
    return bytes(out), pos, idx


PNG_A = b"\x89PNG\r\n\x1a\n" + b"A" * 400
PNG_B = b"\x89PNG\r\n\x1a\n" + b"B" * 600


def _parse(data):
    off, js, binc = 12, None, b""
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        body = data[off + 8:off + 8 + clen]
        if ctype == 0x4E4F534A:
            js = json.loads(body.decode("utf-8"))
        elif ctype == 0x004E4942:
            binc = body
        off += 8 + clen + ((-clen) % 4)
    return js, binc


def test_embedded_images_become_uris():
    data, _, _ = _glb([PNG_A, PNG_B])
    out, files = gltf_textures.externalise(data)
    js, _ = _parse(out)
    assert len(files) == 2
    for im in js["images"]:
        assert "uri" in im and "bufferView" not in im
        assert im["uri"].startswith(gltf_textures.TEX_DIR + "/")
    assert set(files) == {im["uri"] for im in js["images"]}
    assert sorted(files.values(), key=len) == [PNG_A, PNG_B]


def test_the_pixels_are_the_same_pixels():
    """The bytes written out are the bytes that were embedded, unchanged.

    This is the whole safety argument for the change: nothing recompresses,
    resizes or reformats, so a texture cannot silently stop looking like the
    one Pixelcoat authored.
    """
    data, _, _ = _glb([PNG_A])
    _, files = gltf_textures.externalise(data)
    assert list(files.values()) == [PNG_A]


def test_one_texture_in_two_modules_names_one_file():
    a, _, _ = _glb([PNG_A])
    b, _, _ = _glb([PNG_A, PNG_B])
    _, fa = gltf_textures.externalise(a)
    _, fb = gltf_textures.externalise(b)
    shared = set(fa) & set(fb)
    assert len(shared) == 1, "the same pixels must produce the same filename"
    assert fa[next(iter(shared))] == PNG_A


def test_different_pixels_never_collide():
    a, _, _ = _glb([PNG_A])
    b, _, _ = _glb([PNG_B])
    _, fa = gltf_textures.externalise(a)
    _, fb = gltf_textures.externalise(b)
    assert set(fa).isdisjoint(set(fb))


def test_mesh_data_survives_the_compaction():
    """The image views are removed from the middle of the binary chunk.

    A rewrite that shifts offsets without remapping accessor indices leaves a
    file that still opens and draws the wrong thing, which no size check would
    catch.
    """
    data, pos, idx = _glb([PNG_A, PNG_B])
    out, _ = gltf_textures.externalise(data)
    js, binc = _parse(out)
    assert len(js["bufferViews"]) == 2
    got = []
    for acc in js["accessors"]:
        v = js["bufferViews"][acc["bufferView"]]
        got.append(binc[v["byteOffset"]:v["byteOffset"] + v["byteLength"]])
    assert got == [pos, idx]
    assert js["buffers"][0]["byteLength"] == len(binc)


def test_running_it_twice_changes_nothing():
    data, _, _ = _glb([PNG_A])
    once, files = gltf_textures.externalise(data)
    twice, again = gltf_textures.externalise(once)
    assert twice == once
    assert again == {}
    assert files


def test_an_unknown_mime_type_refuses_rather_than_guessing():
    data, _, _ = _glb([PNG_A])
    js, binc = _parse(data)
    js["images"][0]["mimeType"] = "image/webp"
    body = json.dumps(js, separators=(",", ":")).encode("utf-8")
    body += b" " * ((-len(body)) % 4)
    rebuilt = struct.pack("<III", 0x46546C67, 2,
                          12 + 8 + len(body) + 8 + len(binc))
    rebuilt += struct.pack("<II", len(body), 0x4E4F534A) + body
    rebuilt += struct.pack("<II", len(binc), 0x004E4942) + binc
    with pytest.raises(gltf_textures.GlbFormatError):
        gltf_textures.externalise(rebuilt)


def test_an_extension_that_indexes_the_chunk_refuses():
    data, _, _ = _glb(
        [PNG_A], {"extensionsUsed": ["EXT_meshopt_compression"]})
    with pytest.raises(gltf_textures.GlbFormatError):
        gltf_textures.externalise(data)


def test_a_file_with_no_images_is_returned_untouched():
    data, _, _ = _glb([])
    out, files = gltf_textures.externalise(data)
    assert out == data and files == {}


def test_on_disk_two_modules_write_the_shared_texture_once(tmp_path):
    for name, imgs in (("a.glb", [PNG_A]), ("b.glb", [PNG_A, PNG_B])):
        data, _, _ = _glb(imgs)
        (tmp_path / name).write_bytes(data)
    first = gltf_textures.externalise_file(tmp_path / "a.glb")
    second = gltf_textures.externalise_file(tmp_path / "b.glb")
    assert first == {**first, "written": 1, "shared": 0}
    assert second["written"] == 1 and second["shared"] == 1
    assert len(list((tmp_path / gltf_textures.TEX_DIR).iterdir())) == 2
    assert second["bytes_after"] < second["bytes_before"]


def test_export_glb_shares_textures_by_default():
    """The wiring, read from the source rather than from memory.

    `bpylayer.export` imports bpy at module scope and cannot be imported in a
    test run, so the check is on its text: a pass that is written and never
    called is the defect this asserts against.
    """
    import ast
    import pathlib

    src = (pathlib.Path(gltf_textures.__file__).parents[1]
           / "bpylayer" / "export.py")
    tree = ast.parse(src.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "export_glb")
    args = [a.arg for a in fn.args.args]
    assert "share_textures" in args
    default = fn.args.defaults[args.index("share_textures") - (
        len(args) - len(fn.args.defaults))]
    assert default.value is True
    assert "_share_textures" in ast.dump(fn)
