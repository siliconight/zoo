"""Does GPU instancing survive from Blender's glTF exporter into Godot?

Asked because `pennant_row` was the nominated first customer for CLAUDE.md's
"MultiMesh the large repeated sets" rule: a row is 1 batten + 44 felts + 44
bands, and 1.1.0's merge-by-material could only take it to one mesh per
COLOUR (11-13 draws) because merging cannot merge across materials. Per
instance colour was supposed to take it to 2.

THE ANSWER IS NO, AND THE FAILURE IS SILENT. Measured 2026-09-21 against
Blender 5.1.1 and Godot 4.7-stable-win64. Three instances of one triangle,
exported with `export_gpu_instances=True`, reach Godot as ONE triangle:

    exported GLB      extensionsUsed ['EXT_mesh_gpu_instancing']
                      1 node "Row", attributes TRANSLATION/ROTATION/SCALE
    Godot, runtime    GLTFDocument.append_from_file -> MeshInstance3D,
                      1 surface, 3 verts, transform at the origin
    Godot, editor     load("res://inst.glb") -> MeshInstance3D, 3 verts
    Godot, binary     the string "EXT_mesh_gpu_instancing" does not occur
                      in the engine executable at all

So the instancing node's mesh is kept, its instance table is discarded, and
the other N-1 instances stop existing. On a pennant row that is 43 of 44
pennants deleted with no error, no warning and a GLB that still validates.

THE SECOND HALF, WHICH IS WHY THIS IS AN INSTRUMENT AND NOT A BUG REPORT:
Blender only writes the extension when the instances share a PARENT, and it
collapses them onto that parent node. Flat siblings sharing one mesh -- the
obvious way to author a row -- export as N ordinary nodes and the flag does
nothing. So a "did it work?" that only checks the Blender side can answer
yes on a file Godot will empty out, and a "did it work?" that only checks
for the flag can answer no on a file that never used it.

Run both halves, or the answer is about the exporter rather than the engine.

    blender -b --python tools/instancing_probe.py -- --out probe.glb
    python tools/instancing_probe.py --read probe.glb
    godot --headless --path <project> --script instancing_probe.gd

This prints what it measured and stops. What follows from it belongs in the
reply, not here.
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys

#: The extension Blender writes and Godot 4.7 does not read.
EXT = "EXT_mesh_gpu_instancing"


def read_glb(path):
    """The glTF JSON chunk of a .glb, as a dict."""
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:4] != b"glTF":
        raise ValueError("%s is not a GLB (magic %r)" % (path, data[:4]))
    length = struct.unpack("<I", data[12:16])[0]
    return json.loads(data[20:20 + length])


def census(doc):
    """What a glTF costs to submit, and whether it claims instancing.

    Submissions are counted per (node, primitive): a node reusing a mesh
    submits it again, so counting `meshes` would under-report a file that
    shares mesh data between nodes -- which is exactly the shape an
    instancing experiment produces.
    """
    acc = doc.get("accessors", [])
    meshes = doc.get("meshes", [])
    nodes = doc.get("nodes", [])
    mesh_nodes = [n for n in nodes if "mesh" in n]
    tris = 0
    mats = set()
    for node in mesh_nodes:
        for prim in meshes[node["mesh"]]["primitives"]:
            if "indices" in prim:
                tris += acc[prim["indices"]]["count"] // 3
            else:
                tris += acc[prim["attributes"]["POSITION"]]["count"] // 3
            if "material" in prim:
                mats.add(doc["materials"][prim["material"]]["name"])
    submissions = sum(len(meshes[n["mesh"]]["primitives"]) for n in mesh_nodes)
    instanced = []
    for node in nodes:
        ext = (node.get("extensions") or {}).get(EXT)
        if ext is None:
            continue
        attrs = ext.get("attributes") or {}
        count = None
        for name in ("TRANSLATION", "ROTATION", "SCALE"):
            if name in attrs:
                count = acc[attrs[name]]["count"]
                break
        instanced.append({"node": node.get("name"), "instances": count,
                          "attributes": sorted(attrs)})
    return {
        "nodes": len(nodes),
        "mesh_nodes": len(mesh_nodes),
        "mesh_defs": len(meshes),
        "submissions": submissions,
        "materials": len(mats),
        "triangles": tris,
        "extensions_used": doc.get("extensionsUsed") or [],
        "claims_instancing": EXT in (doc.get("extensionsUsed") or []),
        "instanced_nodes": instanced,
    }


def _write(path, parented, count):
    """Build ``count`` instances of one triangle and export them.

    ``parented`` is the whole experiment: Blender's exporter writes the
    extension only for mesh objects that share a parent, and writes it ONTO
    that parent. Siblings at the scene root with the same mesh data export
    as ordinary nodes however the flag is set.
    """
    import bpy

    bpy.ops.wm.read_factory_settings(use_empty=True)
    me = bpy.data.meshes.new("Tri")
    me.from_pydata([(0, 0, 0), (1, 0, 0), (0, 0, 1)], [], [(0, 1, 2)])
    me.update()
    mat = bpy.data.materials.new("M_InstancingProbe")
    mat.use_nodes = True
    me.materials.append(mat)
    scene = bpy.context.scene.collection
    parent = None
    if parented:
        parent = bpy.data.objects.new("Row", None)
        scene.objects.link(parent)
        parent.select_set(True)
    for i in range(count):
        obj = bpy.data.objects.new("Inst%d" % i, me)
        obj.location = (i * 2.0, 0.0, 0.0)
        scene.objects.link(obj)
        if parent is not None:
            obj.parent = parent
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parent or scene.objects[0]
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB",
                              use_selection=True, export_apply=False,
                              export_yup=True, export_gpu_instances=True)
    return count


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    ap = argparse.ArgumentParser(prog="instancing_probe")
    ap.add_argument("--out", help="write a probe GLB here (needs Blender)")
    ap.add_argument("--read", help="census an existing GLB (plain Python)")
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--flat", action="store_true",
                    help="build the instances as scene-root siblings rather "
                         "than children of one parent -- the control that "
                         "shows the exporter needs the parent")
    args = ap.parse_args(argv)
    if not args.out and not args.read:
        ap.error("give --out (build) or --read (census)")
    if args.out:
        n = _write(args.out, not args.flat, args.count)
        print("[instancing_probe] wrote %s  %d bytes  %d instances  "
              "parented=%s" % (args.out, os.path.getsize(args.out), n,
                               not args.flat))
        args.read = args.read or args.out
    if args.read:
        got = census(read_glb(args.read))
        print("[instancing_probe] %s" % args.read)
        for key in ("nodes", "mesh_nodes", "mesh_defs", "submissions",
                    "materials", "triangles", "extensions_used",
                    "claims_instancing"):
            print("    %-16s %s" % (key, got[key]))
        for node in got["instanced_nodes"]:
            print("    instanced node   %r  %s instances  %s"
                  % (node["node"], node["instances"], node["attributes"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
