"""Move a GLB's embedded images out to files beside it, shared by content.

WHY THIS EXISTS. Blender's glTF exporter has one GLB mode and it embeds every
image in the binary chunk, so a pack texture used by sixty modules is written
sixty times. That is a disk cost on its own, and it is not only a disk cost:
Godot imports each GLB independently and builds a separate texture resource
from each copy, so sixty embeds are sixty textures resident on the GPU.

MEASURED 2026-09-21, Godot 4.7, GL Compatibility, twenty single-quad GLBs each
carrying one 512x512 RGBA image, counted by distinct texture RID in the loaded
scene tree and by `RENDERING_INFO_TEXTURE_MEM_USED` over an empty-scene
baseline:

    twenty GLBs, IDENTICAL embedded bytes    20 textures   27,962,000 B
    twenty GLBs, DIFFERENT embedded bytes    20 textures   27,962,000 B
    twenty GLBs -> one external PNG           1 texture     1,398,100 B
    one GLB instanced twenty times            1 texture     1,398,100 B

The first two rows are the answer: byte-identical and distinct payloads cost
exactly the same, so the engine does not deduplicate. The third row is this
module. The fourth is the floor, and the third reaching it is the point.

glTF 2.0 allows `images[].uri` to be a relative path, so a GLB plus a texture
folder beside it is a standard asset that Blender, Godot and three.js all read
with no tooling present -- which is the rule a Zoo module has to satisfy. The
filename carries a hash of the pixels, so two modules that use one pack
texture name one file, and two that do not never collide.

IDEMPOTENT. An image that already has a `uri` is left alone, so running this
twice is the same as running it once.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path

#: Default folder, relative to the GLB, that the textures are written into and
#: the rewritten URIs point at.
TEX_DIR = "_tex"

_MAGIC = 0x46546C67
_JSON = 0x4E4F534A
_BIN = 0x004E4942

#: glTF 2.0 names exactly these two image mime types. Anything else is a file
#: this module has not been shown, and it refuses rather than guessing an
#: extension -- a wrong extension is a texture Godot imports as the wrong
#: thing, which is worse than not having moved it.
_EXT = {"image/png": ".png", "image/jpeg": ".jpg"}

_SAFE = re.compile(r"[^A-Za-z0-9_.-]+")


class GlbFormatError(ValueError):
    """The file is not a GLB this module knows how to rewrite."""


def _pad4(n: int) -> int:
    return (-n) % 4


def _split(data: bytes) -> tuple[dict, bytes]:
    if len(data) < 12 or struct.unpack_from("<I", data, 0)[0] != _MAGIC:
        raise GlbFormatError("not a GLB (bad magic)")
    off, js, binc = 12, None, b""
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        body = data[off + 8:off + 8 + clen]
        if len(body) != clen:
            raise GlbFormatError("truncated chunk")
        if ctype == _JSON:
            js = json.loads(body.decode("utf-8"))
        elif ctype == _BIN:
            binc = body
        off += 8 + clen + _pad4(clen)
    if js is None:
        raise GlbFormatError("no JSON chunk")
    return js, binc


def _join(js: dict, binc: bytes) -> bytes:
    body = json.dumps(js, separators=(",", ":"), allow_nan=False).encode("utf-8")
    body += b" " * _pad4(len(body))
    binc += b"\0" * _pad4(len(binc))
    out = struct.pack("<III", _MAGIC, 2, 12 + 8 + len(body) + 8 + len(binc))
    out += struct.pack("<II", len(body), _JSON) + body
    if binc:
        out += struct.pack("<II", len(binc), _BIN) + binc
    return out


def _view_refs(js: dict):
    """Yield every ``(container, key)`` in the document that indexes a bufferView.

    Listed rather than walked, because a walk that matches on the KEY NAME
    would also rewrite a `bufferView` field inside an unknown extension whose
    indices this function is not rebuilding. Everything here is core glTF 2.0.
    """
    for a in js.get("accessors", []):
        if "bufferView" in a:
            yield a, "bufferView"
        sp = a.get("sparse")
        if sp:
            for part in ("indices", "values"):
                if part in sp and "bufferView" in sp[part]:
                    yield sp[part], "bufferView"
    for im in js.get("images", []):
        if "bufferView" in im:
            yield im, "bufferView"


def _unsupported_extensions(js: dict) -> list[str]:
    """Extensions that index the binary chunk themselves.

    Compacting the chunk under one of these would move bytes it still points
    at. None is emitted by the exporter Zoo runs, so this is a guard rather
    than a case to handle.
    """
    risky = {"EXT_meshopt_compression", "KHR_draco_mesh_compression"}
    return sorted(risky.intersection(js.get("extensionsUsed", []) or []))


def externalise(data: bytes, prefix: str = "",
                tex_dir: str = TEX_DIR) -> tuple[bytes, dict[str, bytes]]:
    """Rewrite one GLB's embedded images to ``uri`` references.

    Returns the new GLB bytes and ``{relative_uri: image_bytes}``. The binary
    chunk is rebuilt from the views that survive rather than spliced, so a
    document whose views are out of order or overlapping cannot leave a stale
    offset behind.
    """
    js, binc = _split(data)
    images = js.get("images", [])
    if not images:
        return data, {}
    bad = _unsupported_extensions(js)
    if bad:
        raise GlbFormatError("indexes the binary chunk: " + ", ".join(bad))

    views = js.get("bufferViews", [])
    drop: set[int] = set()
    files: dict[str, bytes] = {}

    for idx, im in enumerate(images):
        if "uri" in im or "bufferView" not in im:
            continue
        mime = im.get("mimeType", "")
        if mime not in _EXT:
            raise GlbFormatError(f"image {idx}: unknown mimeType {mime!r}")
        v = views[im["bufferView"]]
        start = v.get("byteOffset", 0)
        blob = binc[start:start + v["byteLength"]]
        if len(blob) != v["byteLength"]:
            raise GlbFormatError(f"image {idx}: bufferView runs past the chunk")
        stem = _SAFE.sub("_", str(im.get("name") or f"image{idx}")).strip("_")
        name = f"{prefix}{stem or f'image{idx}'}_{hashlib.sha1(blob).hexdigest()[:8]}{_EXT[mime]}"
        uri = f"{tex_dir}/{name}" if tex_dir else name
        files[uri] = blob
        drop.add(im["bufferView"])
        im.pop("bufferView")
        im.pop("mimeType")
        im["uri"] = uri

    if not files:
        return data, {}

    # An image bufferView that something else also reads is not this module's
    # to remove. Nothing in a Blender export shares one, but a silent drop
    # would corrupt a mesh, so it is checked rather than assumed. The
    # externalised images have had their `bufferView` popped by now, so
    # anything still pointing into `drop` is mesh data.
    for holder, key in _view_refs(js):
        if holder[key] in drop:
            raise GlbFormatError("an image bufferView is shared with mesh data")

    keep = [i for i in range(len(views)) if i not in drop]
    remap = {old: new for new, old in enumerate(keep)}
    new_bin = bytearray()
    new_views = []
    for old in keep:
        v = dict(views[old])
        start = v.get("byteOffset", 0)
        blob = binc[start:start + v["byteLength"]]
        if len(blob) != v["byteLength"]:
            raise GlbFormatError(f"bufferView {old} runs past the chunk")
        v["byteOffset"] = len(new_bin)
        new_bin += blob + b"\0" * _pad4(len(blob))
        new_views.append(v)
    for holder, key in _view_refs(js):
        holder[key] = remap[holder[key]]

    js["bufferViews"] = new_views
    if new_bin:
        js["buffers"] = [{"byteLength": len(new_bin)}]
    else:
        js.pop("buffers", None)
    return _join(js, bytes(new_bin)), files


def externalise_file(path, tex_dir: str = TEX_DIR, prefix: str = "") -> dict:
    """Apply `externalise` to a GLB on disk, writing textures into ``tex_dir``.

    A texture file that already exists with the same name is not rewritten:
    the name carries the hash of its contents, so an identical name is an
    identical file, and leaving it alone is what makes sixty modules share one.
    """
    path = Path(path)
    before = path.stat().st_size
    new_data, files = externalise(path.read_bytes(), prefix=prefix,
                                  tex_dir=tex_dir)
    written, shared = 0, 0
    for uri, blob in files.items():
        dest = path.parent / uri
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_file() and dest.stat().st_size == len(blob):
            shared += 1
            continue
        dest.write_bytes(blob)
        written += 1
    if files:
        path.write_bytes(new_data)
    return {"glb": str(path), "images": len(files), "written": written,
            "shared": shared, "bytes_before": before,
            "bytes_after": path.stat().st_size, "tex_dir": tex_dir}
