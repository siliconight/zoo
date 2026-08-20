"""Does the tint survive the glTF export? Read it back out of the file.

WHY THIS EXISTS. `materials._tint_multiply` inserts `albedo * tint` between
the image texture and Base Color. glTF computes base colour as
``baseColorFactor * baseColorTexture * COLOR_0``, so the exporter has to fold
that node back into the FACTOR term. It is free not to. If it gives up, it
does so QUIETLY: every tinted prop renders in the pack's own near-white, no
warning is printed, and nothing fails. That is the same shape of silent
failure that hid the flat wear for a whole art pass (see tools/wear_probe.py),
which is why this is measured and not assumed.

WHAT IT DOES. Builds the smallest scene that can answer the question -- two
cubes, one tintable pack, two different genome colours -- exports it, and
reads the GLB's own JSON chunk back. It deliberately does NOT drive the
species pipeline: a failure there would be a different finding and would
muddy this one.

    blender --background --python tools\\tint_probe.py -- --pack <pack dir>

Build a tintable pack to point it at:

    cd pixelcoat
    python -m pixelcoat.cli.main proc-pack profiles/materials/plastic_neutral.json --out _probe --size 128

WHAT THE EXITS MEAN
    0  the question was answered (either way -- a dropped factor is a
       finding, and findings exit 0)
    2  blender was not the interpreter, or the pack could not be read
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Two colours far apart in every channel, so a collapsed pair is unmistakable.
RED = (0.62, 0.14, 0.14)
BLUE = (0.14, 0.26, 0.55)


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    ap = argparse.ArgumentParser(prog="tint_probe")
    ap.add_argument("--pack", required=True,
                    help="a Pixelcoat pack DIRECTORY whose manifest sets "
                         "tintable=true (bypasses theme resolution on "
                         "purpose: this probe tests the exporter, not the "
                         "resolver)")
    ap.add_argument("--keep", help="write the probe GLB here instead of a "
                                   "temp file that is deleted")
    return ap.parse_args(argv)


# --------------------------------------------------------------------------- #
# read the answer out of the file, with no assumptions about the exporter
# --------------------------------------------------------------------------- #

def glb_json(path):
    """The JSON chunk of a .glb, parsed. Raises on a malformed container."""
    with open(path, "rb") as f:
        magic, version, _total = struct.unpack("<III", f.read(12))
        if magic != 0x46546C67:
            raise ValueError("%s is not a GLB (magic %#x)" % (path, magic))
        length, ctype = struct.unpack("<II", f.read(8))
        if ctype != 0x4E4F534A:
            raise ValueError("first chunk of %s is not JSON" % path)
        return json.loads(f.read(length).decode("utf-8"))


def materials_report(doc):
    """[(name, baseColorFactor, has_baseColorTexture)] for every material."""
    out = []
    for m in doc.get("materials", []):
        pbr = m.get("pbrMetallicRoughness") or {}
        out.append((m.get("name", "?"),
                    pbr.get("baseColorFactor"),
                    "baseColorTexture" in pbr))
    return out


def close(a, b, tol=0.02):
    return a is not None and abs(float(a) - float(b)) <= tol


# --------------------------------------------------------------------------- #

def main():
    try:
        import bpy  # noqa: F401
    except ImportError:
        sys.stderr.write(
            "tint_probe must run inside Blender:\n"
            "  blender --background --python tools/tint_probe.py -- --pack DIR\n")
        return 2

    import bpy
    import tempfile

    args = parse_args()

    from zoo_keeper.core import skins
    from zoo_keeper.bpylayer import materials, export

    pack = skins.load_pack(os.path.abspath(args.pack))
    if pack is None:
        sys.stderr.write("no pack in %s\n" % args.pack)
        return 2
    print("pack       : %s" % pack["id"])
    print("tintable   : %r" % pack.get("tintable"))
    if pack.get("tintable") is not True:
        print("")
        print("FINDING: that pack is not tintable, so this probe cannot ask "
              "the question. Build one from a grammar whose `tintable` is "
              "true (profiles/materials/plastic_neutral.json).")
        return 0

    # smallest scene that can answer the question
    bpy.ops.wm.read_factory_settings(use_empty=True)
    coll = bpy.data.collections.new("TintProbe")
    bpy.context.scene.collection.children.link(coll)
    made = []
    for tag, rgb in (("red", RED), ("blue", BLUE)):
        mesh = bpy.data.meshes.new("Probe_" + tag)
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], [],
                         [(0, 1, 2, 3)])
        mesh.update()
        obj = bpy.data.objects.new("Probe_" + tag, mesh)
        obj.location = (len(made) * 2.0, 0, 0)
        coll.objects.link(obj)
        mat = materials._textured("M_Probe_" + tag, pack, "plastic", tint=rgb)
        obj.data.materials.append(mat)
        made.append((tag, rgb, mat.name))

    tmp = args.keep or os.path.join(tempfile.mkdtemp(), "tint_probe.glb")
    export.export_glb(tmp, coll)

    doc = glb_json(tmp)
    rows = materials_report(doc)

    print("")
    print("  %-16s %-34s %s" % ("MATERIAL", "baseColorFactor", "baseColorTexture"))
    print("  " + "-" * 74)
    for name, factor, has_tex in rows:
        f = "None (exporter dropped it)" if factor is None else \
            "[" + ", ".join("%.3f" % v for v in factor) + "]"
        print("  %-16s %-34s %s" % (name, f, "yes" if has_tex else "NO"))

    # ---- the verdict --------------------------------------------------------
    print("")
    by_name = {n: (f, t) for n, f, t in rows}
    verdict_ok = True
    for tag, rgb, matname in made:
        got = by_name.get(matname)
        if got is None:
            print("FINDING: material %r is not in the file at all." % matname)
            verdict_ok = False
            continue
        factor, has_tex = got
        if not has_tex:
            print("FINDING: %s lost its baseColorTexture. The extra node "
                  "broke texture detection -- this is worse than losing the "
                  "tint." % matname)
            verdict_ok = False
        if factor is None:
            print("FINDING: %s has no baseColorFactor. The tint was DROPPED "
                  "silently; this prop would render in the pack's own "
                  "near-white." % matname)
            verdict_ok = False
        elif not all(close(factor[i], rgb[i]) for i in range(3)):
            print("FINDING: %s baseColorFactor is %s, wanted ~%s. The tint "
                  "reached the file but not intact."
                  % (matname, factor[:3], list(rgb)))
            verdict_ok = False

    if verdict_ok and len({tuple(by_name[m][0][:3]) for _, _, m in made}) < 2:
        print("FINDING: both materials exported the SAME baseColorFactor. "
              "The colours collapsed -- check the cache key in "
              "make_material, not the exporter.")
        verdict_ok = False

    print("")
    if verdict_ok:
        print("TINT SURVIVES THE EXPORT. baseColorFactor carries the genome "
              "colour and baseColorTexture is intact on both materials.")
    else:
        print("TINT DOES NOT SURVIVE. Fall back to multiplying the tint into "
              "the loaded image pixels once per colour (see the docstring on "
              "materials._tint_multiply) -- a plain texture cannot be "
              "dropped.")
    if args.keep:
        print("probe GLB kept at %s" % tmp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
