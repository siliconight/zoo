"""What a saturated room's worth of flat art costs, measured in Blender.

    blender -b --python tools/flat_art_cost.py

Zoo 0.98.0. The walker asked for DENSITY and the standing rule is
performance over look, so the only honest way to ship this set is with the
number attached. This builds a card shop's worth of flat art through the
normal kit path (`kit.plan_kit` then `build.build_module`, the road a
`zoo_kit_build` job takes) and reports what the scene holds afterwards:
triangles, distinct images and their decoded bytes, distinct materials, and
the objects each material is spread over.

WHAT THE ROOM IS. Read off `docs/SET_DRESSING_REFERENCES.md`, "The card shop
is not dense enough" -- eight posters on the wall above the shelving in the
three forms, three banners over the runs, four hangers on the ceiling, three
aisle signs, and the two play tables' printed mats. It is a made-up census
and it is here so the figure can be argued with; change `ROOM` and re-run.

A PROBE: it prints what it measured and names no cause. The reading is in
the release note.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)

#: (species, dims, form/variant) -- one row per module the room stands.
ROOM = [
    ("poster", (0.6, 0.04, 0.9), {"form": "framed", "variant": 0}),
    ("poster", (0.6, 0.04, 0.9), {"form": "framed", "variant": 1}),
    ("poster", (0.5, 0.03, 0.7), {"form": "bare", "variant": 1}),
    ("poster", (0.5, 0.03, 0.7), {"form": "bare", "variant": 2}),
    ("poster", (0.9, 0.04, 1.3), {"form": "tilted", "variant": 2}),
    ("poster", (0.9, 0.04, 1.3), {"form": "tilted", "variant": 0}),
    ("poster", (0.6, 0.04, 0.9), {"form": "framed", "variant": 2}),
    ("poster", (0.6, 0.04, 0.9), {"form": "framed", "variant": 0}),
    ("hanging_banner", (2.4, 0.05, 0.8), {"variant": 0}),
    ("hanging_banner", (1.8, 0.05, 0.7), {"variant": 1}),
    ("hanging_banner", (1.8, 0.05, 0.7), {"variant": 2}),
    ("ceiling_hanger", (0.8, 0.06, 0.5), {"variant": 0}),
    ("ceiling_hanger", (1.0, 0.06, 0.55), {"variant": 1}),
    ("ceiling_hanger", (0.8, 0.06, 0.5), {"variant": 2}),
    ("ceiling_hanger", (0.6, 0.06, 0.45), {"variant": 3}),
    ("aisle_sign", (1.1, 0.05, 0.4), {"variant": 0}),
    ("aisle_sign", (1.1, 0.05, 0.4), {"variant": 1}),
    ("aisle_sign", (1.4, 0.05, 0.45), {"variant": 2}),
    ("folding_table", (1.8, 0.76, 0.74), {"stock": "cards", "variant": 0}),
    ("folding_table", (2.4, 0.76, 0.74), {"stock": "cards", "variant": 1}),
]


def main():
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import kit

    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    out = os.path.join(REPO, "_preview_flat", "cost")
    os.makedirs(out, exist_ok=True)
    slots = []
    for i, (sp, dims, extra) in enumerate(ROOM):
        slot = {"slot_id": f"{sp}_{i}", "role": "prop", "size_mod": "full",
                "style": 1, "species": sp,
                "fit": {"dims": list(dims), "pivot": "center"}}
        slot.update(extra)
        slots.append(slot)
    plan = kit.plan_kit({"building_id": "flatart", "slots": slots},
                        theme="delco_1997", style=1)
    assert plan["species_fallbacks"] == [], plan["species_fallbacks"]

    # ONE MODULE AT A TIME, AND MEASURED BEFORE THE NEXT ONE. `build_module`
    # clears the scene between builds, so a count taken at the end is the
    # LAST module's and not the room's -- which is what the first run of
    # this probe reported (240 triangles for twenty modules, which is one
    # folding table). Images are not purged between builds, so those DO
    # accumulate and the image figures below really are the room's.
    per = []
    tris = 0
    objects = 0
    mat_objs = {}
    art_objs = 0
    for mod in plan["modules"]:
        res = build.build_module(mod, out, theme="delco_1997", style=1,
                                 options={"save_blend": False})
        n = t = 0
        seen = set()
        for obj in bpy.data.objects:
            if obj.type != "MESH":
                continue
            n += 1
            obj.data.calc_loop_triangles()
            t += len(obj.data.loop_triangles)
            if obj.name.endswith("_Art") or "_Art_" in obj.name:
                art_objs += 1
            for slot in obj.material_slots:
                if slot.material:
                    seen.add(slot.material.name)
        for name in seen:
            mat_objs[name] = mat_objs.get(name, 0) + 1
        objects += n
        tris += t
        per.append((mod["species"], n, t))

    # BLENDER'S OWN COMPOSITOR IMAGE IS NOT A TEXTURE THIS SHIPS. "Viewer
    # Node" is 256 x 256 and was 192 KiB of the first run's total, which is
    # 7% of the figure -- the shape of mistake the repo's own rule about
    # naming what produced an artefact is for.
    images = {}
    for img in bpy.data.images:
        if img.size[0] and img.size[1] and img.name not in ("Viewer Node",
                                                            "Render Result"):
            images[img.name] = (img.size[0], img.size[1],
                                img.size[0] * img.size[1] * 3)

    print("\n=== flat art: a saturated card shop ===")
    print(f"placements         {len(ROOM)}")
    print(f"modules built      {len(plan['modules'])}  (the kit builds one "
          f"module per distinct species+dims+variant and instances it)")
    print(f"mesh objects       {objects}")
    print(f"triangles          {tris}")
    print(f"distinct materials {len(mat_objs)}")
    print(f"distinct images    {len(images)}")
    raw = sum(v[2] for v in images.values())
    print(f"image bytes (raw)  {raw} = {raw / 1048576.0:.3f} MiB decoded RGB8")
    for name, (w, h, b) in sorted(images.items()):
        print(f"    {name:44s} {w:4d} x {h:4d}  {b / 1024.0:8.1f} KiB")
    print(f"art meshes         {art_objs}  (one per module that has art, "
          f"however many quads are on it)")
    print("\nmaterials by the number of MODULES wearing them:")
    for name, n in sorted(mat_objs.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"    {n:3d}  {name}")

    print("\nper module:")
    for sp, n, t in per:
        print(f"    {sp:16s} {n:3d} objects  {t:5d} tris")

    # THE COUNTERFACTUAL, measured on the same plans rather than guessed:
    # what the art would be if every quad named its own image instead of a
    # rect in one atlas. `flat_forms` is what knows how many quads there are.
    from zoo_keeper.core import flat_forms as FF
    plans = {"poster": FF.plan_poster, "hanging_banner": FF.plan_banner,
             "ceiling_hanger": FF.plan_hanger, "aisle_sign": FF.plan_aisle_sign}
    quads = tiles = 0
    for sp, dims, extra in ROOM:
        if sp not in plans:
            continue
        got = plans[sp](dims[0], dims[1], dims[2],
                        {k: v for k, v in extra.items() if k == "form"},
                        extra.get("variant", 0), key=f"{sp}{dims[0]}{dims[1]}")
        quads += sum(1 for p in got["prims"] if p.get("tile"))
        tiles += len(got["tiles"])
    print(f"\nart quads in the flat-art species: {quads}, naming {tiles} tiles")


if __name__ == "__main__":
    main()
