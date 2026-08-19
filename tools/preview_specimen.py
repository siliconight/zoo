"""Headless build + render of one Zoo specimen — a quick visual check.

Run inside Blender (see tools/preview_dressing.ps1):

    blender --background --python tools/preview_specimen.py -- \
        --prompt "carpet floor" --seed 1999 --out _preview \
        --render _preview/floor_carpet.png [--skins <dir> --theme delco]

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


def _light_and_world(bpy, math_):
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
        bg.inputs[1].default_value = 0.55


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

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo not in sys.path:
        sys.path.insert(0, repo)

    from zoo_keeper.bpylayer import build
    if skins:
        from zoo_keeper.bpylayer import materials
        materials.set_skin_library(os.path.abspath(skins), theme)
        print(f"[preview] skins: {skins} (theme={theme})")

    res = build.build_specimen(
        prompt, out, seed=seed,
        options={"collision": None, "lods": False,
                 "save_blend": False, "clear_scene": True})
    print(f"[preview] prompt='{prompt}' -> specimen={res['specimen_id']} "
          f"status={res['report']['status'].upper()}")

    import bpy
    import mathutils
    scene = bpy.context.scene

    meshes = [o for o in scene.objects if o.type == "MESH"]
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

    if not no_ground:
        _ground(bpy, size=max(4.0, size * 6.0))
        _scale_post(bpy, (target.x + max(size * 0.9, 0.06),
                          target.y - max(size * 0.5, 0.04), 0.0))

    cam_data = bpy.data.cameras.new("PrevCam")
    cam_data.lens = 40.0
    cam = bpy.data.objects.new("PrevCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.location = mathutils.Vector((dist * 0.72, -dist * 0.72, eye))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()

    _light_and_world(bpy, math)

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
