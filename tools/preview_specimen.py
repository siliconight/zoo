"""Headless build + render of one Zoo specimen — a quick visual check.

Run inside Blender (see tools/preview_floor_ceiling.ps1):

    blender --background --python tools/preview_specimen.py -- \
        --prompt "carpet floor" --seed 1999 --out _preview \
        --render _preview/floor_carpet.png [--skins <dir> --theme delco]

Builds the specimen with the normal Zoo pipeline, then frames it and renders a
PNG with Cycles CPU (reliable headless). With --skins it shows the Pixelcoat
texture; without, the flat style colour + baked wear. Prints the build status so
the console alone confirms the species resolved even if rendering is skipped.
"""
from __future__ import annotations

import math
import os
import sys


def _arg(flag, default=None):
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    return argv[argv.index(flag) + 1] if flag in argv else default


def main():
    prompt = _arg("--prompt", "carpet floor")
    seed = int(_arg("--seed", "1999"))
    out = os.path.abspath(_arg("--out", "_preview"))
    render = os.path.abspath(_arg("--render", "preview.png"))
    skins = _arg("--skins")
    theme = _arg("--theme", "delco")

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

    lo = [1e9] * 3
    hi = [-1e9] * 3
    for o in meshes:
        for corner in o.bound_box:
            wc = o.matrix_world @ mathutils.Vector(corner[:])
            for i in range(3):
                lo[i] = min(lo[i], wc[i]); hi[i] = max(hi[i], wc[i])
    center = mathutils.Vector([(lo[i] + hi[i]) / 2 for i in range(3)])
    size = max(1e-3, max(hi[i] - lo[i] for i in range(3)))

    cam_data = bpy.data.cameras.new("PrevCam")
    cam = bpy.data.objects.new("PrevCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    dist = size * 2.4
    cam.location = center + mathutils.Vector((dist * 0.8, -dist * 0.8, dist * 0.55))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()

    sd = bpy.data.lights.new("PrevSun", "SUN")
    sd.energy = 3.5
    sun = bpy.data.objects.new("PrevSun", sd)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(55), math.radians(12), math.radians(35))

    if scene.world is None:
        scene.world = bpy.data.worlds.new("PrevWorld")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.06, 0.07, 0.09, 1.0)
        bg.inputs[1].default_value = 0.45

    scene.render.engine = "CYCLES"
    try:
        scene.cycles.device = "CPU"
        scene.cycles.samples = 48
    except Exception:
        pass
    scene.render.resolution_x = 960
    scene.render.resolution_y = 640
    scene.render.filepath = render
    bpy.ops.render.render(write_still=True)
    print(f"[preview] rendered -> {render}")


main()
