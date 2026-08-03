"""Where does the wear colour die? Measure it at all three boundaries.

WHAT THIS IS FOR. ``tools/vertex_variation.py`` measured a shipped dressing
GLB and found COLOR_0 uniformly 1.0 on every vertex of all 1884 covers --
zero spread between covers and zero spread inside one -- while the ``rockay``
style declares ``wear: 0.29``. One fix has already been tried and did not
move the number: making the ``Wear`` layer the ACTIVE colour attribute in
``bm_to_object``. That it changed nothing is itself information, and it means
guessing again is the wrong move.

Wear has to cross three boundaries to reach a file, and each fails silently:

  1. COMPUTED -> MESH.  ``wear_colors`` writes a corner colour layer. If the
     style's wear never reaches ``bm_to_object``, or the byte-colour
     conversion saturates, the mesh itself is already white and no export
     setting can help.
  2. MESH -> EXPORTED LAYER.  Blender carries TWO indices, an *active* colour
     attribute (what you edit) and a *render/default* one, and the glTF
     exporter does not necessarily read the one this code sets. A mesh can
     hold correct wear and still export a different layer.
  3. EXPORTER -> FILE.  ``export_glb`` calls the exporter with
     ``export_vertex_color="ACTIVE"`` inside a ``try/except TypeError`` that
     silently retries WITHOUT it. On a Blender whose exporter does not take
     that keyword, the fallback runs and the default applies -- and on 4.1+
     the default is ``MATERIAL``, which exports a colour attribute only when
     a material actually reads one through a Color Attribute node. Zoo's
     materials do not. That path produces exactly what was measured.

This probe builds ONE real cover through the real recipe, then reports what
is true at each boundary in turn. Whichever boundary the number goes white
at is the defect; the other two are exonerated.

    blender --background --python tools\\wear_probe.py
    blender --background --python tools\\wear_probe.py -- --theme rockay

WHAT IT DELIBERATELY DOES NOT DO. It does not fix anything, and it does not
read the shipped GLB -- the shipped file cannot tell you which boundary broke,
which is why three sessions of reasoning about it produced a wrong diagnosis.

WHAT A NONZERO EXIT MEANS. Blender was not the interpreter (exit 2), or the
build/export raised (exit 2). White wear is a finding and exits 0.
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    ap = argparse.ArgumentParser(prog="wear_probe")
    ap.add_argument("--theme", default="rockay",
                    help="style block in genome/species/dress_cover.json")
    ap.add_argument("--cover", default="panel_field",
                    help="cover kind to build (the loudest family is the "
                         "most useful one to probe)")
    ap.add_argument("--keep", help="write the probe GLB here instead of a "
                                   "temp file that is deleted")
    ap.add_argument("--skins", help="Pixelcoat pack folder, as the dressing "
                    "job passes it. THIS IS BOUNDARY 2b: the flat material "
                    "path wires a ShaderNodeVertexColor on the wear layer "
                    "into Base Color, and `_textured` deliberately does not "
                    "(\"the in-Blender wear-preview mix is skipped on "
                    "textured materials\"). Run the probe both ways.")
    return ap.parse_args(argv)


# --------------------------------------------------------------------------- #
# boundary 3: read COLOR_0 back out of a GLB, with no numpy and no assumptions
# --------------------------------------------------------------------------- #

_COMPONENT = {5121: ("<B", 1, 255.0), 5123: ("<H", 2, 65535.0),
              5126: ("<f", 4, 1.0)}
_COUNT = {"VEC3": 3, "VEC4": 4}


def glb_textures(path):
    """(image_count, materials_with_baseColorTexture) actually in the file.

    Wiring a node between the albedo texture and Base Color is what the skin
    path was avoiding, on the theory that it would confuse the exporter's
    texture detection. That theory cost every cover its wear, so the
    replacement is not a better theory -- it is this measurement. A fix that
    restores COLOR_0 and drops baseColorTexture is a worse bug, and it shows
    up here as images 0.
    """
    with open(path, "rb") as fh:
        data = fh.read()
    off = 12
    doc = None
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        if ctype == 0x4E4F534A:
            doc = json.loads(data[off + 8:off + 8 + clen].decode("utf-8"))
            break
        off += 8 + clen + ((4 - clen % 4) % 4)
    if doc is None:
        return 0, 0
    n_base = sum(
        1 for m in doc.get("materials", [])
        if (m.get("pbrMetallicRoughness") or {}).get("baseColorTexture"))
    return len(doc.get("images", [])), n_base


def glb_color0(path):
    """(n_meshes_with_color, lo, hi, mean) over every COLOR_0 in the file."""
    with open(path, "rb") as fh:
        data = fh.read()
    doc = blob = None
    off = 12
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        body = data[off + 8:off + 8 + clen]
        if ctype == 0x4E4F534A:
            doc = json.loads(body.decode("utf-8"))
        elif ctype == 0x004E4942:
            blob = body
        off += 8 + clen + ((4 - clen % 4) % 4)
    if doc is None:
        return 0, None, None, None
    lo, hi, total, n = 1e9, -1e9, 0.0, 0
    meshes = 0
    for mesh in doc.get("meshes", []):
        for prim in mesh.get("primitives", []):
            ci = prim.get("attributes", {}).get("COLOR_0")
            if ci is None:
                continue
            meshes += 1
            a = doc["accessors"][ci]
            bv = doc["bufferViews"][a["bufferView"]]
            fmt, width, norm = _COMPONENT[a["componentType"]]
            comps = _COUNT[a["type"]]
            stride = bv.get("byteStride") or width * comps
            base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
            for i in range(a["count"]):
                for c in range(3):          # RGB only; alpha is not wear
                    v = struct.unpack_from(
                        fmt, blob, base + i * stride + c * width)[0] / norm
                    lo, hi = min(lo, v), max(hi, v)
                    total += v
                    n += 1
    if not n:
        return meshes, None, None, None
    return meshes, lo, hi, total / n


def describe(name, lo, hi, mean):
    if lo is None:
        print("  %-28s ABSENT" % name)
        return
    flat = "  <-- FLAT WHITE" if lo > 0.999 else ""
    print("  %-28s lo %.4f  hi %.4f  mean %.4f%s"
          % (name, lo, hi, mean, flat))


def stats(values):
    if not values:
        return None, None, None
    return min(values), max(values), sum(values) / len(values)


def main():
    args = parse_args()
    try:
        import bpy
    except ImportError:
        sys.stderr.write("wear_probe must run inside Blender:\n"
                         "  blender --background --python tools/wear_probe.py\n")
        return 2

    from zoo_keeper import TOOL_VERSION, recipes
    from zoo_keeper.bpylayer import build as build_mod, export, geometry
    from zoo_keeper.bpylayer import materials
    from zoo_keeper.core import dressing as dressing_mod
    from zoo_keeper.core import genome as genome_mod
    from zoo_keeper.core import seeding

    print("=" * 70)
    print("blender %s   zoo %s   theme %s   cover %s   skins %s"
          % (bpy.app.version_string, TOOL_VERSION, args.theme, args.cover,
             args.skins or "<none: flat material path>"))
    print("=" * 70)
    if args.skins:
        materials.set_skin_library(os.path.abspath(args.skins), args.theme)

    # ---------------------------------------------------------------- setup
    genome = genome_mod.load_species("dress_cover")
    style = (genome.get("styles", {}).get(args.theme)
             or genome.get("styles", {}).get("default") or {})
    print("\nSTYLE BLOCK as authored")
    print("  wear %-8s ambient %-8s bevel %s"
          % (style.get("wear"), style.get("ambient"), style.get("bevel")))

    order = {"cover": args.cover, "size": 1.17, "size2": [1.17, 1.17],
             "pos": [0.0, 0.0, 0.0], "normal": [0.0, 1.0, 0.0],
             "collision": "none", "seed_offset": 12345}
    plan = dressing_mod.dress_plan(order, genome, args.theme,
                                   "spec/Blender Z-up raw coords",
                                   TOOL_VERSION)
    print("\nBOUNDARY 0 -- style -> plan (what the recipe is actually handed)")
    for key in ("wear", "ambient", "bevel"):
        got = plan.get(key, "<absent>")
        note = ""
        if key in style and key not in plan:
            note = "  <-- AUTHORED IN THE STYLE, DROPPED BY dress_plan"
        print("  plan[%r] = %s%s" % (key, got, note))

    build_mod.clear_scene()
    coll = bpy.data.collections.new("probe")
    bpy.context.scene.collection.children.link(coll)
    streams = seeding.RNGStreams(
        seeding.root_key("probe_cover_0", "dress_cover", 12345, TOOL_VERSION))
    result = recipes.get("dress_cover")(plan, streams, coll)
    obj = result["objects"][0]
    mesh = obj.data

    # ------------------------------------------- boundary 1: computed -> mesh
    print("\nBOUNDARY 1 -- computed -> mesh")
    attrs = list(mesh.color_attributes)
    if not attrs:
        print("  NO COLOUR ATTRIBUTE AT ALL -- wear_colors never ran, or its "
              "layer did not survive bm.to_mesh")
    for a in attrs:
        vals = [0.0] * (len(a.data) * 4)
        a.data.foreach_get("color", vals)
        rgb = [vals[i] for i in range(len(vals)) if i % 4 != 3]
        lo, hi, mean = stats(rgb)
        print("  attribute %-10r domain %-7s type %-11s corners %d"
              % (a.name, a.domain, a.data_type, len(a.data)))
        describe("    values", lo, hi, mean)

    # -------------------------------------- boundary 2: mesh -> which layer
    print("\nBOUNDARY 2 -- mesh -> the layer the exporter will pick")
    ca = mesh.color_attributes
    for label, attr in (("active_color (edited)", getattr(ca, "active_color", None)),
                        ("render/default color", _render_attr(mesh))):
        print("  %-24s %s" % (label, attr.name if attr else "<none>"))
    print("  wear layer is %r" % geometry.WEAR_LAYER)
    active_ok = getattr(ca, "active_color", None) is not None and \
        ca.active_color.name == geometry.WEAR_LAYER
    render = _render_attr(mesh)
    render_ok = render is not None and render.name == geometry.WEAR_LAYER
    if not active_ok:
        print("  MISMATCH: the ACTIVE attribute is not the wear layer")
    if not render_ok:
        print("  MISMATCH: the RENDER/DEFAULT attribute is not the wear layer")
        print("            (bm_to_object sets active_color only; if the glTF "
              "exporter reads the render index, that is boundary 2)")

    # ------------------------------- boundary 2b: does the MATERIAL read it
    print("\nBOUNDARY 2b -- does the material reference the wear layer")
    mat = mesh.materials[0] if mesh.materials else None
    print("  material %r  images %d"
          % (mat.name if mat else "<none>",
             len([n for n in (mat.node_tree.nodes if mat and mat.node_tree
                              else []) if n.type == "TEX_IMAGE"])))
    skinned = bool(mat and mat.name.startswith("M_Skin_"))
    if args.skins and not skinned:
        print("  SKINS DID NOT RESOLVE. --skins was given and the material is "
              "still the flat one, so `find_pack` found no pack for kind %r "
              "under theme %r at that path. This run tested the FLAT path; "
              "nothing below says anything about the skinned one."
              % (plan["material"], args.theme))
        print("    point --skins at the folder CONTAINING the "
              "<kind>_<theme>/ pack directories, not at a pack itself")
    vc_nodes = [n for n in (mat.node_tree.nodes if mat and mat.node_tree else [])
                if n.type in ("VERTEX_COLOR", "ATTRIBUTE")]
    if vc_nodes:
        for n in vc_nodes:
            print("  reads vertex colour via %s layer %r"
                  % (n.type, getattr(n, "layer_name",
                                     getattr(n, "attribute_name", "?"))))
    else:
        print("  MATERIAL DOES NOT READ VERTEX COLOUR AT ALL")
        print("    On this exporter the vertex-colour mode 'MATERIAL' exports "
              "a colour attribute only when a material reads one. If the "
              "'ACTIVE' request is not taking effect, a textured cover is "
              "exactly the case that loses its wear while a flat one keeps it.")

    # --------------------------------------- boundary 3: exporter -> file
    print("\nBOUNDARY 3 -- exporter -> file")
    props = bpy.ops.export_scene.gltf.get_rna_type().properties
    has_kw = "export_vertex_color" in props
    print("  exporter accepts export_vertex_color: %s" % has_kw)
    if has_kw:
        items = getattr(props["export_vertex_color"], "enum_items", None)
        print("    choices %s   default %r"
              % ([i.identifier for i in items] if items else "?",
                 getattr(props["export_vertex_color"], "default", "?")))
    else:
        print("    -> export_glb's `except TypeError` FALLBACK IS FIRING, and "
              "the export runs with this build's DEFAULT vertex-colour rule")
        for alt in ("export_all_vertex_colors", "export_colors",
                    "export_active_vertex_color_when_no_material"):
            if alt in props:
                print("    this build's actual keyword: %r (default %r)"
                      % (alt, getattr(props[alt], "default", "?")))

    out = args.keep or os.path.join(tempfile.mkdtemp(), "wear_probe.glb")
    export.export_glb(out, coll)
    meshes, lo, hi, mean = glb_color0(out)
    n_img, n_base = glb_textures(out)
    print("  exported %s" % os.path.basename(out))
    print("  primitives carrying COLOR_0: %d" % meshes)
    describe("COLOR_0 in the file", lo, hi, mean)
    print("  images in the file: %d   materials with baseColorTexture: %d"
          % (n_img, n_base))
    if skinned and not n_base:
        print("  TEXTURE LOST: a skinned cover exported with no "
              "baseColorTexture. Whatever restored the wear broke the skin; "
              "that trade is not worth taking.")

    # ------------------------------------------------------------- verdict
    print("\nVERDICT")
    mesh_white = True
    if attrs:
        wear_attr = ca.get(geometry.WEAR_LAYER) or attrs[0]
        vals = [0.0] * (len(wear_attr.data) * 4)
        wear_attr.data.foreach_get("color", vals)
        rgb = [vals[i] for i in range(len(vals)) if i % 4 != 3]
        mesh_white = min(rgb) > 0.999
    file_white = lo is None or lo > 0.999
    if mesh_white:
        print("  BOUNDARY 1. The mesh is already white in Blender. The export "
              "is innocent; wear_colors is producing no darkening for this "
              "cover (check wear value, and whether a bevelled box has any "
              "concave vertices at all).")
    elif file_white and lo is not None:
        print("  BOUNDARY 2 or 3. The mesh holds real wear and the file does "
              "not. Read the two lines above: a layer mismatch is boundary 2, "
              "a fallback firing is boundary 3.")
    elif lo is None:
        print("  BOUNDARY 3. The mesh holds real wear and the file carries no "
              "COLOR_0 at all -- the exporter dropped it.")
    elif not skinned:
        print("  CLEAN on the FLAT path. This does not clear the shipped "
              "build: the dressing job runs with --skins, which takes the "
              "`_textured` branch and wires no vertex-colour node. Re-run "
              "with a --skins path that actually resolves a pack before "
              "concluding anything.")
    else:
        print("  CLEAN on the SKINNED path too. Both material paths carry "
              "wear to the file, so the difference is elsewhere in "
              "build_dressing -- the 1884-object export or the matrix_world "
              "assignment are what is left.")
    if not args.keep:
        try:
            os.remove(out)
        except OSError:
            pass
    return 0


def _render_attr(mesh):
    """The attribute Blender renders with -- NOT the same index as active.

    Blender exposes ``active_color`` (the one you paint) and a separate
    render/default colour. Which of the two the glTF exporter's "ACTIVE" mode
    reads is the whole question at boundary 2, so report both by name rather
    than assuming.
    """
    ca = mesh.color_attributes
    for attr in ("render_color_index", "default_color_index"):
        idx = getattr(ca, attr, None)
        if isinstance(idx, int) and 0 <= idx < len(ca):
            return ca[idx]
    name = getattr(mesh.attributes, "default_color_name", None)
    return ca.get(name) if name else None


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                      # a probe must say why
        sys.stderr.write("wear_probe failed: %s: %s\n"
                         % (type(exc).__name__, exc))
        raise
