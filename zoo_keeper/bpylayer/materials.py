"""Export-safe Principled materials: flat vertex-color wear by default,
Pixelcoat texture packs when a skin library is set.

Flat path (unchanged since forever): constant base color + best-effort
Color Attribute multiply for in-Blender preview. Godot reads COLOR_0 via
'Vertex Color -> Use as Albedo'.

Skin path (v0.27): ``set_skin_library(dir, theme)`` points the factory at
a folder of Pixelcoat packs (see ``core.skins`` for layout + resolution
order). When ``make_material`` finds a pack for a material kind it builds
an image-textured material instead — albedo (Closest interpolation, the
pixel-art look), normal (OpenGL Y+, Non-Color), stepped roughness
(Non-Color), optional emissive — shared per (kind, theme) across every
species. No pack -> flat, exactly as before: the art pass stays
progressive, matching DC's greybox fallback.

Density: mesh UVs are world meters * texel (geometry.cube_project_uv). A
Mapping node scales UVs by 1/meters_per_tile from the pack manifest, so a
pack authored as "one tile = 2 m" repeats every 2 m at texel 1.0 (the
glTF exporter emits this as KHR_texture_transform, which Godot 4 reads).

WEAR AND THE SKIN PATH. This docstring used to say the wear multiply "is
skipped on textured materials to keep the exporter's texture detection
unambiguous". Skipping it did not skip a preview -- it silently flattened the
shipped wear. Measured on Blender 5.1, one cover built twice from the same
mesh whose ``Wear`` corner attribute held 0.7011-0.9823 both times:

    flat material     (reads vertex colour)  -> COLOR_0  0.7011 .. 0.9823
    textured material (reads none)           -> COLOR_0  1.0000 .. 1.0000

Same exporter, same ``export_vertex_color="ACTIVE"`` request, same active
colour attribute, same mesh data. A material that does not read vertex colour
gets its COLOR_0 written out white -- so every cover on every skinned building
shipped with no wear at all, which is why 2098 covers measured as one flat
tone. The multiply is wired on BOTH paths now, and the texture detection it
was omitted to protect is checked by measurement instead
(``tools/wear_probe.py`` reports the exported image count and whether
baseColorTexture survived).
"""
from __future__ import annotations

import bpy

from .geometry import WEAR_LAYER

# THE KIND VOCABULARY. Keep in sync with core.skins.KNOWN_KINDS -- and now
# actually enforced by tests/test_kind_vocabulary.py, which also checks that
# every kind a genome names appears here. `tar` was missing from both lists
# since the roof species shipped, so roofs silently took the 0.6 default below.
ROUGHNESS = {"laminate": 0.55, "wood": 0.65, "metal": 0.35, "plastic": 0.45,
             "leather": 0.70, "rubber": 0.85, "canvas": 0.90, "carbon": 0.30,
             "glass": 0.05, "glass_facade": 0.08, "paper": 0.80,
             "concrete": 0.92, "plaster": 0.88,
             "brick": 0.90, "tile": 0.35, "drywall": 0.90, "ceiling_tile": 0.92,
             # Fieldstone: a broken face with mortar between, above concrete
             # (0.92) and brick (0.90). A stone wall that catches a highlight
             # reads as wet plastic at every angle.
             "stone": 0.94,
             # Vinyl/aluminium lap siding sits by `wood` (0.65), not by
             # `plastic` (0.45): it leaves the factory with a low sheen and
             # chalks within a decade, which is the state the late 1990s
             # found it in.
             "siding": 0.66,
             # An asphalt shingle is stone granule bonded to felt, so it is a
             # MINERAL surface beside concrete rather than a bituminous one;
             # `tar` (0.90) is the binder underneath, not what light hits.
             "shingle": 0.93,
             "carpet": 0.98, "dirt": 0.97, "tar": 0.90,
             # Velvet (0.87.0, the club chairs): a cut pile, as matte as
             # carpet. Its colour is the chair's: Pixelcoat 0.43.0's pack is
             # tintable, so the genome's colour rides the textured path too.
             "velvet": 0.96,
             # A tablecloth's linen (0.89.0): finer and a shade less matte
             # than canvas (0.90). Tintable in the same way.
             "cloth": 0.85,
             # THE CLUB SURFACES (Pixelcoat 0.42.0, measured there at the
             # pack size): the medallion carpet's pile 0.95, the flocked
             # damask's paper 0.66 with the flock matte over it, stained bar
             # wood 0.50, sun-faded paint over block 0.88. Each is the
             # fallback for a socket the pack does not texture; every one of
             # these packs ships a roughness map.
             "carpet_club": 0.95, "wallpaper_club": 0.66, "wood_stained": 0.50,
             "paint_block": 0.88,
             # Layer 3 surface dressing: loose stone and plant matter, both
             # fully matte -- a dressing scatter that catches a specular
             # highlight reads as wet plastic at every viewing angle.
             "gravel": 0.95, "vegetation": 0.85,
             # foliage: a leaf-cluster CUTOUT for a tree's crown cards; the
             # pack's alpha is tested, not blended (see `_textured`)
             "foliage": 0.85,
             # Prop metal (see skins.KNOWN_KINDS). Semi-gloss enamel sits
             # duller than the bare sheet it covers; brushed/polished stock
             # sits tighter than the generic `metal` average.
             "metal_painted": 0.45, "metal_bare": 0.28,
             # THE CARD SHOP'S SURFACES (Pixelcoat 0.44.0). `wood_panel` is
             # the printed hardboard panelling of a 1970s-90s shop's lower
             # wall: the sheen is the factory lacquer's and not the grain's,
             # so it sits beside `wood_stained` (0.50) rather than bare
             # `wood` (0.65). `slatwall` is melamine-faced board and takes
             # `laminate`'s 0.55 exactly -- it is a separate KIND so it can
             # resolve its own pack (the grooves are in the texture), not
             # because it reflects differently from a laminate counter.
             "wood_panel": 0.52, "slatwall": 0.55}
# `metal_painted` is listed at 0.0 rather than left to the .get() default:
# the whole reason it is a separate kind from `metal_bare` is this number, and
# a value that matters should not be inferred from an omission.
METALLIC = {"metal": 0.85, "carbon": 0.30,
            "metal_painted": 0.0, "metal_bare": 0.90}

_SKINS = {"dir": None, "theme": "delco", "wet": False}


def set_skin_library(skins_dir, theme="delco", wet=False):
    """Point the material factory at a folder of Pixelcoat packs. Call
    once per session (the CLI does it when --skins is given); pass None
    to go back to flat materials.

    ``wet`` asks every pack for its wet variant. A pack that carries none is
    unaffected, so this is safe to set for a whole build: only the surfaces
    whose grammar declared wetness change, and the decision about which those
    are already lives in the grammar."""
    _SKINS["dir"] = skins_dir
    _SKINS["theme"] = theme
    _SKINS["wet"] = bool(wet)


def get_skin_library():
    """(dir, theme) the factory was pointed at — recipes with non-kind
    resolution needs (sign faces) read the library through this."""
    return _SKINS["dir"], _SKINS["theme"]


def _find_pack(material_kind):
    if not _SKINS["dir"]:
        return None
    from ..core import skins  # pure; imported lazily to keep flat path lean
    return skins.find_pack(_SKINS["dir"], material_kind, _SKINS["theme"],
                           wet=_SKINS["wet"])


def make_material(name, base_color, material_kind):
    """Same signature as always — recipes never know whether they got a
    flat or a textured material. With a skin library set, all parts of a
    kind share one textured material named for the pack (the genome's
    per-specimen color rides only the flat path; textured paint jobs are
    the pack's job)."""
    pack = _find_pack(material_kind)
    if pack:
        # A TINTABLE pack is achromatic on purpose: it carries grain, wear and
        # sheen, and the mesh supplies the hue. Such a material CANNOT be
        # shared across colours, so the cache key carries the colour and one
        # material exists per (kind, theme, colour). A normal pack still
        # collapses to one material per (kind, theme) -- which is the whole
        # point for a wall, and the reason the docstring above says the
        # genome's colour rides only the flat path. It now also rides the
        # textured path, but ONLY when the pack asked for it.
        tint = _tint_key(base_color) if pack.get("tintable") else None
        skin_name = f"M_Skin_{material_kind}_{_SKINS['theme']}"
        # THE NAME CARRIES THE VARIANT, and it has to. This cache is keyed on
        # the name, so without a suffix a wet and a dry build in one process
        # would collide and the second would silently get the first's
        # material. The name also travels into the GLB, where Level Factory's
        # greybox-skin gate reads it. Only a pack that actually substituted
        # something is marked, so a wet build does not rename every wall it
        # left dry.
        if pack.get("wet"):
            skin_name += "_wet"
        if tint is not None:
            skin_name += "_" + tint
        mat = bpy.data.materials.get(skin_name)
        if mat:
            return mat
        print(f"[zoo] skin: {material_kind} <- {pack['id']} ({pack['dir']})"
              + (f"  tinted #{tint}" if tint else ""))
        from ..core import skins
        if (material_kind in skins.SEE_THROUGH_KINDS
                and not skins.is_see_through(pack)):
            # Said once per material (the cache above returns before this),
            # and not fixed here: the opacity is the pack's to declare. This
            # line is what the delco_1997 build did not print while every
            # window in it exported OPAQUE.
            print(f"[zoo] WARNING: {material_kind} is a see-through kind and "
                  f"pack {pack['id']} declares no blended "
                  f"import_hints.transparency -- every '{material_kind}' "
                  f"surface of theme {_SKINS['theme']} exports OPAQUE")
        return _textured(skin_name, pack, material_kind,
                         tint=(tuple(base_color) if tint else None))

    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    rgba = (*base_color, 1.0)
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = ROUGHNESS.get(material_kind, 0.6)
    bsdf.inputs["Metallic"].default_value = METALLIC.get(material_kind, 0.0)
    try:  # preview-only wear multiply; harmless if node API differs
        attr = tree.nodes.new("ShaderNodeVertexColor")
        attr.layer_name = WEAR_LAYER
        mix = tree.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        mix.inputs[6].default_value = rgba          # A
        tree.links.new(attr.outputs["Color"], mix.inputs[7])   # B
        tree.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    except Exception:
        pass
    return mat


def make_see_through_material(name, tint, opacity, material_kind="glass"):
    """Glazing that is transparent whatever the skin library says about it.

    `make_material` makes a pane see-through only when the kind's Pixelcoat
    pack carries ``import_hints.transparency``; without one, or without a
    library, the pane is exported alphaMode OPAQUE. MEASURED on walk 9048's
    `prop_simple_car_delco_1997_01_w175_d430_h145.glb`: the car's glass was
    `M_Skin_glass_delco_1997`, OPAQUE, because the delco `glass` pack
    (`glass_delco`, Pixelcoat 0.16.0) has no transparency hint -- the rockay
    glass packs do (`glass_wavy`: blend, opacity 0.5). For a window in a
    hollow facade that can be the right answer. For a car it is not: the
    whole point of the glass is the cabin behind it.

    So, in order:
      * a pack that is authored see-through is used as it is;
      * a pack that is not keeps its albedo (the grime and tint the theme
        gave glass) under its own material name with ``_see_through``
        appended, blended at ``opacity`` -- the building's opaque glass
        material is never touched;
      * no pack: a flat tinted pane at ``opacity``.

    The blend rides the same `_textured` transparency branch as an authored
    pack, so the glTF exporter writes alphaMode BLEND either way.

    REFUTED, kept above what replaced it: this said Godot "imports that as
    BaseMaterial3D transparency ALPHA, which also keeps the pane out of the
    shadow pass so daylight reaches the cabin". Godot 4.7 imports BLEND as
    transparency 4, ALPHA_DEPTH_PRE_PASS, and a depth-prepass pane casts a
    shadow as solid as an opaque one -- measured in GL Compatibility on a
    delco_1997 window module under a shadowed sun, ground under the pane at
    0.463 of open ground both opaque and blended, 1.000 with the pane hidden.
    glTF has no word for "casts no shadow"; Level Factory's import script
    (`zoo_worldskin.gd`, 0.84.0) moves blended materials to ALPHA, which does
    not cast.

    SINCE PIXELCOAT 0.40.0 every theme's `glass` pack is authored see-through
    (delco_1997's at 0.38, this helper's own car opacity), so on a themed
    build the first branch below is the one taken and the car wears the
    theme's glass. The forced and flat branches remain for a library that
    has no `glass` pack or predates that release.
    """
    from ..core import skins
    opacity = max(0.05, min(0.95, float(opacity)))
    pack = _find_pack(material_kind)
    if pack and skins.is_see_through(pack):
        return make_material(name, tint, material_kind)
    if pack:
        skin_name = f"M_Skin_{material_kind}_{_SKINS['theme']}_see_through"
        mat = bpy.data.materials.get(skin_name)
        if mat:
            return mat
        print(f"[zoo] skin: {material_kind} <- {pack['id']} ({pack['dir']})"
              f"  see-through at opacity {opacity:.2f} (the pack is opaque)")
        forced = dict(pack)
        forced["transparency"] = {"alpha_mode": "blend", "opacity": opacity,
                                  "ior": 1.5}
        return _textured(skin_name, forced, material_kind)
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*tint, 1.0)
    bsdf.inputs["Roughness"].default_value = ROUGHNESS.get(material_kind, 0.05)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Alpha"].default_value = opacity
    try:
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = 1.5
    except Exception:
        pass
    for _attr, _val in (("blend_method", "BLEND"),
                        ("surface_render_method", "BLENDED")):
        try:
            setattr(mat, _attr, _val)
        except Exception:
            pass
    return mat


def make_emissive_material(name, color, strength=2.0):
    """Self-lit surface (fixture diffusers, streetlight lenses, sign faces).

    Plain Principled with Emission Color/Strength — exports as glTF emissive
    (+ KHR_materials_emissive_strength), which Godot 4 imports as
    StandardMaterial3D emission. Lux's LEVEL role keeps imported standard
    materials, so the face stays lit under any preset and contributes to a
    LightmapGI bake on the pc2000 path. No wear-preview mix and callers
    should paint the mesh with wear=0: a lit lens doesn't grime, and a
    white COLOR_0 keeps the albedo multiply neutral in Godot."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    rgba = (*color, 1.0)
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = 0.35
    try:  # Blender 4.x socket names; older builds fall back below
        bsdf.inputs["Emission Color"].default_value = rgba
        bsdf.inputs["Emission Strength"].default_value = float(strength)
    except KeyError:
        try:
            bsdf.inputs["Emission"].default_value = rgba
        except KeyError:
            pass
    return mat


def make_emissive_textured_material(name, pack, strength=2.2):
    """Sign face from a Pixelcoat sign pack: the albedo drives Base Color
    AND Emission Color (glTF emissive texture), so the artwork is what
    glows. Name must keep the ``_Face`` suffix — Lux's emissive binder
    matches by suffix, and the power cut has to kill branded signs exactly
    like flat ones. Roughness map linked when the pack ships one. Cached by
    name; callers make the name unique per pack."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = 0.35
    maps = pack["maps"]

    def tex_node(path, non_color=False):
        node = tree.nodes.new("ShaderNodeTexImage")
        node.image = _load_image(path, non_color)
        node.interpolation = "Closest"
        node.extension = "EXTEND"          # a sign face never tiles
        return node

    albedo = tex_node(maps["albedo"])
    tree.links.new(albedo.outputs["Color"], bsdf.inputs["Base Color"])
    try:  # Blender 4.x sockets; the flat fallback path mirrors this
        tree.links.new(albedo.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = float(strength)
    except KeyError:
        try:
            tree.links.new(albedo.outputs["Color"], bsdf.inputs["Emission"])
        except KeyError:
            pass
    if "roughness" in maps:
        rough = tex_node(maps["roughness"], non_color=True)
        tree.links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
    return mat


def image_from_png(name, png_bytes):
    """A PACKED image from PNG bytes a recipe painted (0.87.0: the vending
    machine's panel). Cached by name, so callers put the pixels' identity in
    it. The bytes pass through a temporary file only because
    `bpy.data.images.load` takes a path; once packed, the exporter embeds the
    packed PNG, so the GLB carries exactly these bytes.

    THE FILE IS NAMED ``<name>.png``, in a fresh directory. The glTF exporter
    names an image after its file's basename, not `Image.name`: the first
    build used `mkstemp` and shipped an image called `zoo_a3xvb95d`, which
    is a different GLB every build and a randomly named PNG in every Godot
    import that extracts it."""
    img = bpy.data.images.get(name)
    if img is not None:
        return img
    import os
    import shutil
    import tempfile
    folder = tempfile.mkdtemp(prefix="zoo_png_")
    path = os.path.join(folder, name + ".png")
    try:
        with open(path, "wb") as fh:
            fh.write(png_bytes)
        img = bpy.data.images.load(path)
        img.pack()
        img.name = name
    finally:
        shutil.rmtree(folder, ignore_errors=True)
    return img


def make_backlit_material(name, image, strength, albedo_factor):
    """A lit face whose artwork is its own light: ``image`` drives Emission
    Color at ``strength`` and, dimmed by ``albedo_factor``, Base Color.

    Different from `make_emissive_textured_material` in the dimming, and on
    purpose: that one sets base colour and emission to the same full artwork,
    so under a bright room the diffuse term adds a second copy of the panel on
    top of its glow. A backlit plastic panel is not a mirror of the room.

    The multiply is the same Mix node `_tint_multiply` uses, which the glTF
    exporter folds into ``baseColorFactor`` (measured, see there). Nearest
    filter, clamped: a panel never tiles. Name with a Lux suffix (`_Face`,
    `_Lens`) so the emissive binder finds it."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = 0.35
    bsdf.inputs["Metallic"].default_value = 0.0
    tex = tree.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Closest"
    tex.extension = "EXTEND"
    f = float(albedo_factor)
    base = _tint_multiply(tree, tex.outputs["Color"], (f, f, f), name)
    tree.links.new(base, bsdf.inputs["Base Color"])
    # A DARK FACE LINKS NO EMISSION AT ALL, because strength 0 is not dark
    # once it leaves Blender. With the texture linked and Emission Strength
    # 0, the glTF exporter drops `emissiveFactor` and keeps
    # `emissiveTexture`; Godot 4.7 imports that as emission ON, energy 1.0,
    # colour white (readback of the file, 0.87.0), where the glTF default
    # factor would be black. Frames of strength 0 and strength 1 matched to
    # the decimal in a Godot walk copy.
    if float(strength) > 0.0:
        sock = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        tree.links.new(tex.outputs["Color"], bsdf.inputs[sock])
        bsdf.inputs["Emission Strength"].default_value = float(strength)
    else:
        bsdf.inputs["Emission Strength"].default_value = 0.0
    return mat


def make_painted_material(name, image, roughness):
    """A face whose artwork is PAINT on it, not light: ``image`` drives Base
    Color at full strength, nothing drives emission, roughness is the
    surface's (0.91.0: a dartboard's sisal, a chalkboard's slate, a
    cigarette machine's pack rows).

    `make_backlit_material` at strength 0 is not this, and was not used for
    it: it multiplies the artwork by its albedo factor (a backlit panel's
    0.35) and sets roughness 0.35, which a chalkboard is not. Same image
    node settings as that one -- nearest filter, clamped, a panel never
    tiles -- so the pixel art stays crisp. No colour attribute is read: the
    recipe paints these faces with a white COLOR_0, which Level Factory's
    import multiplies by, so the artwork arrives as painted."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = float(roughness)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Emission Strength"].default_value = 0.0
    tex = tree.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Closest"
    tex.extension = "EXTEND"
    tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def _load_image(path, non_color=False):
    img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        try:  # colorspace name varies across OCIO configs
            img.colorspace_settings.name = "Non-Color"
        except Exception:
            pass
    return img


def _tint_key(base_color):
    """Stable 6-hex cache key for a base colour. Pure; unit-testable without
    bpy, which is why it is not inlined into `make_material`."""
    return "".join("%02x" % max(0, min(255, int(round(float(c) * 255.0))))
                   for c in tuple(base_color)[:3])


def _tint_multiply(tree, color_socket, tint, label):
    """Insert ``albedo * tint`` for an achromatic pack and return the socket.

    VERIFIED AT THE EXPORT BOUNDARY on Blender 5.1.1 (hash b70da489d7f4).
    glTF computes base colour as ``baseColorFactor * baseColorTexture *
    COLOR_0``. This node is the Blender spelling of the FACTOR term, and the
    exporter has to fold it back into one. It does. `tools/tint_probe.py`
    exported two materials off one tintable pack and read the GLB back:

        M_Probe_red   baseColorFactor [0.620, 0.140, 0.140, 1.000]  texture yes
        M_Probe_blue  baseColorFactor [0.140, 0.260, 0.550, 1.000]  texture yes

    Those are the genome colours to three decimals, and baseColorTexture
    survived the extra node. This was written down as UNKNOWN until it was
    measured, because the failure mode -- exporter silently drops the factor,
    every tinted prop renders in the pack own near-white, nothing logs -- is
    the same shape that hid the flat wear for a whole art pass.

    RE-RUN THE PROBE ON A BLENDER UPGRADE. The fold is the exporter choice,
    not a guarantee of the format. If a future version drops it, the fallback
    is to multiply the tint into the loaded image pixels once per colour --
    slower and heavier, but a plain texture cannot be dropped.

    On failure this returns the original socket and SAYS SO, rather than
    leaving a half-wired graph.
    """
    try:
        mix = tree.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        tree.links.new(color_socket, mix.inputs[6])            # A: albedo
        mix.inputs[7].default_value = (float(tint[0]), float(tint[1]),
                                       float(tint[2]), 1.0)    # B: tint
        return mix.outputs[2]
    except Exception as exc:
        print(f"[zoo] WARNING: {label}: could not wire the tint multiply "
              f"({type(exc).__name__}: {exc}) -- this material will render in "
              f"the pack's own colour and ignore the genome")
        return color_socket


def _wear_multiply(tree, color_socket, label):
    """Insert ``albedo * COLOR_0`` and return the socket for Base Color.

    glTF defines COLOR_0 as a multiplier against baseColorFactor and
    baseColorTexture, so this node is the Blender spelling of what the runtime
    does anyway. It is also load-bearing for the export: a material that reads
    no vertex colour ships COLOR_0 as flat white (see the module docstring).

    On failure this returns the original socket so the texture still links --
    but it SAYS SO. A silent fallback here is what hid the flat wear for a
    whole art pass, and the same shape has hidden three other defects in this
    pipeline.
    """
    try:
        attr = tree.nodes.new("ShaderNodeVertexColor")
        attr.layer_name = WEAR_LAYER
        mix = tree.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        tree.links.new(color_socket, mix.inputs[6])            # A: albedo
        tree.links.new(attr.outputs["Color"], mix.inputs[7])   # B: wear
        return mix.outputs[2]
    except Exception as exc:
        print(f"[zoo] WARNING: {label}: could not wire the wear multiply "
              f"({type(exc).__name__}: {exc}) -- this material will export "
              f"COLOR_0 as flat white and its covers will carry no wear")
        return color_socket


def _textured(name, pack, material_kind, tint=None):
    """Image-textured Principled from a Pixelcoat pack.

    Image Texture -> MULTIPLY by the wear colour attribute -> Base Color. The
    multiply used to be omitted here on the theory that anything between the
    texture and Base Color would confuse the exporter's texture detection;
    omitting it cost every skinned cover its wear, and the detection is now
    verified by ``tools/wear_probe.py`` rather than assumed.
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    # Kind-level defaults still set: they are the fallback response for
    # any socket a pack doesn't texture.
    bsdf.inputs["Roughness"].default_value = ROUGHNESS.get(material_kind, 0.6)
    bsdf.inputs["Metallic"].default_value = METALLIC.get(material_kind, 0.0)
    maps = pack["maps"]

    def tex_node(path, non_color=False):
        node = tree.nodes.new("ShaderNodeTexImage")
        node.image = _load_image(path, non_color)
        node.interpolation = "Closest"       # pixel art stays pixel art
        node.extension = "REPEAT"
        return node

    vector_out = None
    mpt = pack.get("meters_per_tile") or 1.0
    if abs(mpt - 1.0) > 1e-9:
        try:  # UV scale -> KHR_texture_transform on export
            uv = tree.nodes.new("ShaderNodeUVMap")
            uv.uv_map = "UVMap"
            mapping = tree.nodes.new("ShaderNodeMapping")
            s = 1.0 / mpt
            mapping.inputs["Scale"].default_value = (s, s, s)
            tree.links.new(uv.outputs["UV"], mapping.inputs["Vector"])
            vector_out = mapping.outputs["Vector"]
        except Exception:
            vector_out = None

    def link_vector(node):
        if vector_out is not None:
            tree.links.new(vector_out, node.inputs["Vector"])

    albedo = tex_node(maps["albedo"])
    link_vector(albedo)
    color_socket = albedo.outputs["Color"]
    if tint is not None:
        color_socket = _tint_multiply(tree, color_socket, tint, name)
    tree.links.new(_wear_multiply(tree, color_socket, name),
                   bsdf.inputs["Base Color"])

    if "roughness" in maps:
        rough = tex_node(maps["roughness"], non_color=True)
        link_vector(rough)
        tree.links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])

    if "normal" in maps:
        try:
            nrm = tex_node(maps["normal"], non_color=True)
            link_vector(nrm)
            nmap = tree.nodes.new("ShaderNodeNormalMap")
            nmap.inputs["Strength"].default_value = 1.0
            tree.links.new(nrm.outputs["Color"], nmap.inputs["Color"])
            tree.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
        except Exception:
            pass

    if "emissive" in maps:
        try:
            emi = tex_node(maps["emissive"])
            link_vector(emi)
            sock = ("Emission Color" if "Emission Color" in bsdf.inputs
                    else "Emission")                 # Blender 4.x vs older
            tree.links.new(emi.outputs["Color"], bsdf.inputs[sock])
            bsdf.inputs["Emission Strength"].default_value = 1.0
        except Exception:
            pass

    # See-through glass: honor a Pixelcoat pack's transparency hint
    # (import_hints.transparency = {opacity, ior}). opacity < 1 sets the
    # Principled Alpha + a blended surface so the glTF exporter writes
    # alphaMode=BLEND and Godot imports a transparent material. Facade glass
    # ships no hint (opaque). The blend-method attribute name varies across
    # Blender versions, so set both known spellings best-effort.
    from ..core import skins
    trans = pack.get("transparency")
    # A CUTOUT pack (road paint, foliage: `alpha_mode: scissor`) carries its
    # alpha in the albedo and asks to be tested, not blended. The glTF
    # exporter writes alphaMode=MASK when the Alpha socket is fed through a
    # Math > Greater Than against a constant (its `detect_alpha_clip`), so
    # that is the node placed here; Godot imports MASK as alpha scissor.
    if trans and trans.get("alpha_mode") == "scissor":
        try:
            clip = tree.nodes.new("ShaderNodeMath")
            clip.operation = "GREATER_THAN"
            clip.inputs[1].default_value = 0.5
            tree.links.new(albedo.outputs["Alpha"], clip.inputs[0])
            tree.links.new(clip.outputs["Value"], bsdf.inputs["Alpha"])
        except Exception:
            pass
        for _attr, _val in (("blend_method", "CLIP"),
                            ("surface_render_method", "DITHERED")):
            try:
                setattr(mat, _attr, _val)
            except Exception:
                pass
        try:
            mat.use_backface_culling = False       # a card reads from both sides
        except Exception:
            pass
    elif skins.is_see_through(pack):
        try:
            bsdf.inputs["Alpha"].default_value = float(trans["opacity"])
        except Exception:
            pass
        try:
            if "IOR" in bsdf.inputs:
                bsdf.inputs["IOR"].default_value = float(trans.get("ior", 1.45))
        except Exception:
            pass
        for _attr, _val in (("blend_method", "BLEND"),
                            ("surface_render_method", "BLENDED")):
            try:
                setattr(mat, _attr, _val)
            except Exception:
                pass

    return mat


def assign(objs, mat):
    for obj in objs:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
