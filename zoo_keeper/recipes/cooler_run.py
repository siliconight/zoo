"""cooler_run recipe: the convenience store's reach-in cooler wall.

Planned in pure Python by `core.cooler_run_forms` -- the cabinet, every door,
shelf and tube, the sign band, and the glow's art -- and executed here. See
that module for what the walker asked for and what the layout measured.

THREE SUBMISSIONS WHATEVER THE LENGTH. The steel parts build with one
painted-metal material, each carrying its colour in its `Wear` attribute
(`geometry.tint_wear`), so `merge.pack_by_material` packs them into one mesh;
the glass is one see-through material (built under a placeholder name first:
`make_see_through_material` returns any material already carrying its name,
and `prim_mesh.build` makes an opaque one -- Zoo 1.9.0's coffee island
measured that as solid glass); and everything that glows -- product panels,
tubes, the sign band -- is ONE object on ONE backlit image,
``M_Cooler_<art>_Face``, which Lux's power cut takes.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import cooler_run_forms as CR


def _kind_material_name(kind):
    return f"M_Cooler_{kind}"


def _build_steel_and_glass(prims, plan, rng, collection):
    out = []
    for mk in sorted({p["mat"] for p in prims}):
        kind, factor = CR.vertex_tint(mk)
        mname = _kind_material_name(kind) + ("_build" if kind == "glass" else "")
        built = prim_mesh.build([p for p in prims if p["mat"] == mk], collection, plan, rng,
                                {mk: (mname, list(CR.KIND_BASE[kind]), kind)}, texel=1.0)
        if kind == "glass":
            materials.assign(built, materials.make_see_through_material(
                _kind_material_name("glass"), list(CR.KIND_BASE["glass"]), CR.GLASS_OPACITY))
        for o in built:
            geometry.tint_wear(o, factor)
        out.extend(built)
    return out


def _glow(prims, art, mat, collection, streams):
    """Every glowing part as one object: each face's corners are
    ``(region, u, v)`` into that rect of the glow image, or ``("dark",)``.
    White `Wear`, no wear: the art is the light."""
    W, H = art["size"]

    def region(name):
        x0, y0, x1, y1 = art["rects"][name]
        return (x0 / W, 1.0 - y1 / H, x1 / W, 1.0 - y0 / H)
    rects = {}
    d = region("dark")
    dark_uv = ((d[0] + d[2]) / 2.0, (d[1] + d[3]) / 2.0)
    t = region("tube")
    tube_uv = ((t[0] + t[2]) / 2.0, (t[1] + t[3]) / 2.0)
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    for p in prims:
        vs = [bm.verts.new(v) for v in p["verts"]]
        for f, corners in zip(p["faces"], p["uvs"]):
            face = bm.faces.new([vs[i] for i in f])
            for loop, c in zip(face.loops, corners):
                if c[0] == "dark":
                    loop[uv].uv = dark_uv
                elif c[0] == "tube":
                    loop[uv].uv = tube_uv            # a solid white block: no stretch to show
                else:
                    r = rects.get(c[0]) or rects.setdefault(c[0], region(c[0]))
                    loop[uv].uv = (r[0] + (r[2] - r[0]) * c[1], r[1] + (r[3] - r[1]) * c[2])
    bm.normal_update()
    geometry.shade_by_angle(bm, 1.0)
    geometry.wear_colors(bm, streams.stream("cooler_glow"), 0.0)
    obj = geometry.bm_to_object(bm, "Cooler_Glow", collection, finish=False)
    obj.data.materials.append(mat)
    return obj


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    key, variant = CR.resolve(plan)
    got = CR.plan(w, d, h, key, variant)
    f = got["facts"]
    rng = streams.stream("wear")
    solid = [p for p in got["prims"] if p["mat"] != "glow"]
    objs = _build_steel_and_glass(solid, plan, rng, collection)
    panel_h = h - CR.HEADER_H - CR.KICK_H - 0.04
    A = CR.glow_art(f["door_width"] - 0.024, panel_h, key, variant)
    image = materials.image_from_png(A["name"], A["canvas"].png())
    # 1.51.0: the products are painted and shaded and the image is sampled
    # with filtering; its tiles bleed into their gutters for it
    glow = materials.make_backlit_material(f"M_Cooler_{A['name']}_Face", image,
                                           CR.GLOW_EMISSION, CR.GLOW_ALBEDO, smooth=True)
    objs.append(_glow([p for p in got["prims"] if p["mat"] == "glow"], A, glow, collection, streams))
    print(f"[cooler_run] doors={f['doors']} door_w={f['door_width']:.3f} "
          f"types={f['door_types']} sections={[s[0] for s in f['sections']]} "
          f"cabinet={f['cabinet_depth']:.2f} art={A['name']}")
    return {"objects": objs, "collision_boxes": [f["collision"]], "attachments": {},
            "cooler_run": {"doors": f["doors"], "sections": [s[0] for s in f["sections"]],
                           "art": A["name"]}}
