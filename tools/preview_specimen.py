"""Headless build + render of one Zoo specimen — a quick visual check.

Run inside Blender (see tools/preview_dressing.ps1):

    blender --background --python tools/preview_specimen.py -- \
        --prompt "carpet floor" --seed 1999 --out _preview \
        --render _preview/floor_carpet.png [--skins <dir> --theme delco]
    blender --background --python tools/preview_specimen.py -- \
        --species chair --dims 2.4 0.6 0.9 --style 5 --theme delco_1997 \
        --render _preview/chair_row.png [--skins <dir>]

`--species <name>` names the species OUTRIGHT and skips keyword matching --
the door a program uses, already open in `build.build_specimen` and until now
not wired to this tool. `core.intent.parse` explains why it matters: two
species in the library could not be reached through a prompt at all, and a
prompt that resolves today does so because no better keyword match exists yet,
which is a coincidence rather than a contract. A preview script naming seven
species by prompt is seven coincidences. The prompt is still parsed for
material, colour, wear, size and era, so styling survives.

Builds the specimen with the normal Zoo pipeline, then frames it and renders a
PNG with Cycles CPU (reliable headless). With --skins it shows the Pixelcoat
texture; without, the flat style colour + baked wear. Prints the build status so
the console alone confirms the species resolved even if rendering is skipped.

WHY THERE IS A GROUND PLANE AND A RED POST IN EVERY FRAME.  The first version
framed each specimen with `dist = size * 2.4`, so every object filled the frame
whatever its real size: a 5 cm pebble and a 30 cm scrap rendered identically,
and there was no floor, so nothing showed whether a thing sat on a surface,
hovered over it or sank through it.  Four surface-dressing species were
reviewed from images like that and the review could not have caught a scale
error if one had been there.  Auto-framing is kept, because a 4 m floor module
and a 5 cm stone cannot share a camera distance -- but the frame now always
contains:

  * a ground plane at z = 0, so contact is visible;
  * a red post exactly 0.117 m tall.  That is `unassisted_step_max` from
    `lot/site_steps.py` -- the number every dressing height in this repo is
    argued against -- so the only ruler in shot is the one that matters.

--view patch renders many instances scattered on the ground at standing eye
height, which is the unit a scatter species is actually judged in: a single
specimen is never what the player sees.

--slot <slot.json> [--state <s>] builds a MODULE instead of a specimen: the
slot (one Deli Counter slots.json entry: role, fit, optional interactive) is
planned by `core.kit.plan_kit` and the module for `--state` (default: the
default state) is built by `build.build_module` -- the path a kit build takes,
and the only one that reaches an interactive module's states. A module is
centre-pivot, so it is lifted to stand on the ground plane before rendering.
`--flank <m>` stands a plain grey wall of that width either side of it, so a
wall-slot module is judged in a wall and not as a floating panel;
`--target-z <m>` aims the camera at an absolute height.

THE KIT PATH. `--species S --dims W D H [--style N]` builds the module a kit
build would ship for a Deli Counter prop slot of those dims -- `kit.plan_kit`
then `build.build_module`, the path `tools/coplanar_probe.py --species` takes
-- instead of a prompt specimen, and stands it on the ground (a module is
centre-pivot). `--stock`, `--variant` and `--form` set the slot's fields of
the same names, so a desk with office stock renders as the file
`prop_desk_<theme>_01_..._soffice_n2` that Deli Counter would instance.
`--theme` is the kit theme on this path (default delco_1997). The first
lines printed are where `zoo_keeper` was imported from and the stem built.
"""
from __future__ import annotations

import math
import os
import random
import sys

# lot/site_steps.py: R * (1 - cos(floor_max_angle)) for a 0.4 m capsule at 45.
UNASSISTED_STEP_MAX_M = 0.117


def _arg(flag, default=None):
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    return argv[argv.index(flag) + 1] if flag in argv else default


def _flag(flag):
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    return flag in argv


def _ground(bpy, size=8.0):
    me = bpy.data.meshes.new("PrevGround")
    me.from_pydata([(-size, -size, 0.0), (size, -size, 0.0),
                    (size, size, 0.0), (-size, size, 0.0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new("PrevGround", me)
    bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new("M_PrevGround")
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        # Mid grey on purpose: a dark floor flatters dressing by giving it
        # contrast it will not have on a real concrete surface.
        b.inputs["Base Color"].default_value = (0.42, 0.42, 0.43, 1.0)
        b.inputs["Roughness"].default_value = 0.95
    ob.data.materials.append(m)
    return ob


def _scale_post(bpy, at, height=UNASSISTED_STEP_MAX_M):
    me = bpy.data.meshes.new("PrevScalePost")
    r = max(0.008, height * 0.09)
    v = [(-r, -r, 0.0), (r, -r, 0.0), (r, r, 0.0), (-r, r, 0.0),
         (-r, -r, height), (r, -r, height), (r, r, height), (-r, r, height)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
         (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me.from_pydata(v, [], f)
    ob = bpy.data.objects.new("PrevScalePost", me)
    ob.location = at
    bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new("M_PrevScalePost")
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = (0.85, 0.22, 0.15, 1.0)
    ob.data.materials.append(m)
    return ob


def _light_and_world(bpy, math_, world=0.55):
    sd = bpy.data.lights.new("PrevSun", "SUN")
    sd.energy = 3.5
    try:
        sd.angle = 0.10
    except Exception:
        pass
    sun = bpy.data.objects.new("PrevSun", sd)
    bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler = (math_.radians(55), math_.radians(12),
                          math_.radians(35))
    sc = bpy.context.scene
    if sc.world is None:
        sc.world = bpy.data.worlds.new("PrevWorld")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.09, 0.10, 0.12, 1.0)
        bg.inputs[1].default_value = world


def _bounds(bpy, mathutils, meshes):
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for o in meshes:
        for corner in o.bound_box:
            wc = o.matrix_world @ mathutils.Vector(corner[:])
            for i in range(3):
                lo[i] = min(lo[i], wc[i])
                hi[i] = max(hi[i], wc[i])
    return lo, hi


def main():
    prompt = _arg("--prompt", "carpet floor")
    seed = int(_arg("--seed", "1999"))
    out = os.path.abspath(_arg("--out", "_preview"))
    render = os.path.abspath(_arg("--render", "preview.png"))
    skins = _arg("--skins")
    theme = _arg("--theme", "delco")
    view = _arg("--view", "auto")            # auto | patch
    patch_n = int(_arg("--patch", "45"))
    patch_extent = float(_arg("--patch-extent", "1.15"))
    no_ground = _flag("--no-ground")
    species = _arg("--species", None)
    # A CAMERA THAT CAN WALK AROUND THE PIECE. The auto camera stands at one
    # front-right three-quarter, at an eye height scaled from the piece's
    # size -- 3.2 m for a 4.3 m car, which is a first-floor window, not a
    # person on the sidewalk. `--azimuth` is degrees about the target in the
    # ground plane (0 = +X, 90 = +Y; the default -45 is the old camera
    # exactly), `--eye` an absolute camera height in metres, `--dist` the
    # ground-plane distance in metres. Each overrides only itself.
    azimuth = _arg("--azimuth")
    eye_arg = _arg("--eye")
    dist_arg = _arg("--dist")
    # A SLOT'S SIZE. A prompt only scales the genome's default dims, so a
    # 2.4 m row of waiting chairs -- what Deli Counter places -- could not be
    # previewed at all. `--dims W D H` (with `--species`) plans one prop slot
    # through `core.kit.plan_kit` and builds it with `build.build_module`, the
    # path a `zoo_kit_build` job takes and the one tools/coplanar_probe.py
    # uses. `--style` is the kit style index the slot carries.
    dims = None
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    if "--dims" in argv:
        i = argv.index("--dims")
        dims = [float(v) for v in argv[i + 1:i + 4]]
    style = int(_arg("--style", "1"))
    slot_path = _arg("--slot")
    state_arg = _arg("--state")
    flank = float(_arg("--flank", "0"))
    target_z = _arg("--target-z")

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo not in sys.path:
        sys.path.insert(0, repo)

    import zoo_keeper
    from zoo_keeper.bpylayer import build
    # Which Zoo built the frame: a worktree and the installed addon look
    # identical from the PNG.
    print(f"[preview] zoo_keeper {zoo_keeper.TOOL_VERSION} from "
          f"{os.path.dirname(os.path.abspath(zoo_keeper.__file__))}")
    if dims is not None and _arg("--theme") is None:
        theme = "delco_1997"
    if skins:
        from zoo_keeper.bpylayer import materials
        materials.set_skin_library(os.path.abspath(skins), theme)
        print(f"[preview] skins: {skins} (theme={theme})")

    if dims:
        if not species:
            raise SystemExit("[preview] --dims needs --species")
        from zoo_keeper.core import kit
        slot = {"slot_id": f"{species}_0", "role": "prop", "size_mod": "full",
                "style": style, "species": species,
                "fit": {"dims": dims, "pivot": "center"}}
        # the slot's dressing fields (0.84.0), as Deli Counter names them
        for field in ("stock", "variant", "form"):
            if _arg("--" + field) is not None:
                slot[field] = (int(_arg("--" + field)) if field == "variant"
                               else _arg("--" + field))
        plan = kit.plan_kit({"building_id": "preview", "slots": [slot]},
                            theme=theme, style=style)
        for line in (plan.get("species_fallbacks", [])
                     + plan.get("dressing_fallbacks", [])):
            print(f"[preview] FALLBACK {line}")
        res = build.build_module(plan["modules"][0], out, theme=theme,
                                 style=style, options={"save_blend": False})
        res["specimen_id"] = res["stem"]
        # a module is centre-pivot; stand it on the ground plane
        import bpy as _bpy
        for o in _bpy.context.scene.objects:
            if o.parent is None:
                o.location.z += dims[2] / 2.0
        _bpy.context.view_layer.update()
        print(f"[preview] dims={dims} style={style} -> module={res['stem']} "
              f"tris={res['facts'].get('tris')} "
              f"status={res['report']['status'].upper()}")
    elif slot_path:
        import json
        from zoo_keeper.core import kit
        with open(slot_path, encoding="utf-8") as fh:
            slot = json.load(fh)
        kplan = kit.plan_kit({"building_id": "preview", "slots": [slot]},
                             theme=theme, style=int(slot.get("style") or 1))
        pick = [m for m in kplan["modules"] if m["state"] == state_arg]
        if not pick:
            print(f"[preview] no module for state {state_arg!r}; planned: "
                  f"{[(m['stem'], m['state']) for m in kplan['modules']]}")
            return
        res = build.build_module(pick[0], out, theme=theme,
                                 style=int(slot.get("style") or 1),
                                 options={"save_blend": False})
        print(f"[preview] slot={os.path.basename(slot_path)} "
              f"state={state_arg!r} -> module={res['stem']} "
              f"species={pick[0]['species']} "
              f"status={res['report']['status'].upper()} "
              f"tris={res['facts'].get('tris')}")
        for c in res["report"]["checks"]:
            if c["level"] != "pass":
                print(f"[preview]   check {c['id']}: {c['level']} {c['msg']}")
    else:
        res = build.build_specimen(
            prompt, out, seed=seed, species=species,
            options={"collision": None, "lods": False,
                     "save_blend": False, "clear_scene": True})
        asked = f"species={species!r}" if species else f"prompt={prompt!r}"
        print(f"[preview] {asked} -> specimen={res['specimen_id']} "
              f"status={res['report']['status'].upper()}")

    import bpy
    import mathutils
    scene = bpy.context.scene
    bpy.context.view_layer.update()

    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    if slot_path:
        # stand the centre-pivot module on the ground, hide its collider
        vis = [o for o in scene.objects if o.type == "MESH"]
        zmin = min((o.matrix_world @ mathutils.Vector(c[:])).z
                   for o in vis for c in o.bound_box)
        for o in vis:
            o.location.z -= zmin
            if o.name.endswith(("-colonly", "-col")):
                o.hide_render = True
        fd = res["plan"]["dimensions"]
        if flank > 0.0:
            for sgn in (-1.0, 1.0):
                me = bpy.data.meshes.new("PrevFlank")
                x0 = sgn * fd["width"] / 2.0
                x1 = sgn * (fd["width"] / 2.0 + flank)
                y0, y1 = -fd["depth"] / 2.0 + 0.05, fd["depth"] / 2.0 - 0.05
                zt = fd["height"]
                vv = [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0),
                      (x0, y0, zt), (x1, y0, zt), (x1, y1, zt), (x0, y1, zt)]
                ff = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5),
                      (2, 3, 7, 6), (3, 0, 4, 7)]
                me.from_pydata(vv, [], ff)
                ob = bpy.data.objects.new("PrevFlank", me)
                scene.collection.objects.link(ob)
                mf = bpy.data.materials.new("M_PrevFlank")
                mf.use_nodes = True
                bf = mf.node_tree.nodes.get("Principled BSDF")
                if bf:
                    bf.inputs["Base Color"].default_value = (0.55, 0.53, 0.50, 1.0)
                    bf.inputs["Roughness"].default_value = 0.9
                ob.data.materials.append(mf)

    meshes = [o for o in scene.objects if o.type == "MESH"
              and o.name != "PrevFlank" and not o.name.startswith("PrevFlank")
              and not o.hide_render and not o.name.endswith(_COL_SUFFIXES)]
    if not meshes:                                  # fall back to the exported glb
        glb = None
        for v in res.get("files", {}).values():
            if str(v).lower().endswith(".glb"):
                glb = v if os.path.isabs(v) else os.path.join(res["out_dir"], v)
        if glb and os.path.isfile(glb):
            bpy.ops.import_scene.gltf(filepath=glb)
            meshes = [o for o in scene.objects if o.type == "MESH"]
    print(f"[preview] mesh objects in scene: {len(meshes)}")
    if not meshes:
        print("[preview] nothing to render (build may have failed) — see status above")
        return

    lo, hi = _bounds(bpy, mathutils, meshes)
    size = max(1e-3, max(hi[i] - lo[i] for i in range(3)))

    # ---- optional patch view: many instances, standing eye height ---------
    if view == "patch":
        rng = random.Random(seed ^ 0x5EED)
        centres = [(rng.uniform(-patch_extent, patch_extent),
                    rng.uniform(-patch_extent, patch_extent))
                   for _ in range(max(1, patch_n // 7))]
        src = list(meshes)
        for i in range(patch_n):
            if rng.random() < 0.18:                 # stray tail
                x = rng.uniform(-patch_extent, patch_extent)
                y = rng.uniform(-patch_extent, patch_extent)
            else:                                   # clustered body
                cx, cy = centres[rng.randrange(len(centres))]
                x = max(-patch_extent, min(patch_extent, cx + rng.gauss(0, 0.22)))
                y = max(-patch_extent, min(patch_extent, cy + rng.gauss(0, 0.22)))
            s = 0.65 + (rng.random() ** 2) * 0.9    # lognormal-ish size spread
            for o in src:
                dup = o.copy()                      # linked duplicate: shares mesh
                dup.location = (x, y, 0.0)
                dup.rotation_euler = (0.0, 0.0, rng.uniform(0.0, 6.2831853))
                dup.scale = (s, s, s)
                scene.collection.objects.link(dup)
        for o in src:
            o.location = (patch_extent * 3.0, 0.0, 0.0)   # move the original out
        target = mathutils.Vector((0.0, 0.0, size * 0.5))
        dist = patch_extent * 2.3
        eye = 1.55
        res_xy = (1100, 620)
    else:
        centre = mathutils.Vector([(lo[i] + hi[i]) / 2 for i in range(3)])
        target = mathutils.Vector((centre.x, centre.y, max(lo[2], 0.0)
                                   + size * 0.4))
        dist = size * 2.4
        eye = max(size * 0.75, min(1.6, size * 2.0))
        res_xy = (960, 640)
    if dist_arg is not None:
        dist = float(dist_arg) / 1.0182337649086284   # |(0.72, 0.72)|
    if eye_arg is not None:
        eye = float(eye_arg)
    if slot_path:
        # aim at the slot, not at the bounds: a swung leaf would pull the
        # bounds' centre off the doorway and no two states would frame alike
        target = mathutils.Vector((0.0, 0.0, target.z))
    if target_z is not None:
        target = mathutils.Vector((target.x, target.y, float(target_z)))

    if not no_ground:
        _ground(bpy, size=max(4.0, size * 6.0))
        _scale_post(bpy, (target.x + max(size * 0.9, 0.06),
                          target.y - max(size * 0.5, 0.04), 0.0))

    cam_data = bpy.data.cameras.new("PrevCam")
    cam_data.lens = 40.0
    cam = bpy.data.objects.new("PrevCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    if azimuth is None:
        cam.location = mathutils.Vector((dist * 0.72, -dist * 0.72, eye))
    else:
        r = dist * 1.0182337649086284
        a = math.radians(float(azimuth))
        cam.location = mathutils.Vector((target.x + r * math.cos(a),
                                         target.y + r * math.sin(a), eye))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()

    # `--world`: the environment strength. Bare metal mirrors its
    # surroundings, so under the default near-black world a steel object
    # renders black whatever its albedo; the default stays what every other
    # species was reviewed under.
    _light_and_world(bpy, math, float(_arg("--world", "0.55")))

    scene.render.engine = "CYCLES"
    try:
        scene.cycles.device = "CPU"
        scene.cycles.samples = 40
        scene.cycles.use_denoising = True
    except Exception:
        pass
    scene.render.resolution_x, scene.render.resolution_y = res_xy
    scene.render.filepath = render
    bpy.ops.render.render(write_still=True)
    print(f"[preview] rendered -> {render}  "
          f"(view={view}, ground={'no' if no_ground else 'yes'}, "
          f"ruler={UNASSISTED_STEP_MAX_M} m)")


main()
