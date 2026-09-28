"""price_pylon recipe: the gas station's roadside price sign.

Planned in pure Python by `core.price_pylon_forms` -- the plinth, the posts,
the cabinets and the glow's art -- and executed here. See that module for
the references.

THREE SUBMISSIONS: the steel and concrete build with one painted material,
each part's colour in its `Wear` attribute (`geometry.tint_wear`), so
`merge.pack_by_material` packs them into one mesh; every lit face -- brand,
prices and strip, both sides -- is ONE object on ONE backlit image,
``M_Pylon_<art>_Face``, which Lux's power cut takes.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import price_pylon_forms as PP


def _glow(prims, art, mat, collection, streams):
    W, H = art["size"]

    def region(name):
        x0, y0, x1, y1 = art["rects"][name]
        return (x0 / W, 1.0 - y1 / H, x1 / W, 1.0 - y0 / H)
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    for p in prims:
        vs = [bm.verts.new(v) for v in p["verts"]]
        for f, corners in zip(p["faces"], p["uvs"]):
            face = bm.faces.new([vs[i] for i in f])
            for loop, c in zip(face.loops, corners):
                r = region(c[0])
                if len(c) == 1:
                    loop[uv].uv = ((r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0)
                else:
                    loop[uv].uv = (r[0] + (r[2] - r[0]) * c[1], r[1] + (r[3] - r[1]) * c[2])
    bm.normal_update()
    geometry.shade_by_angle(bm, 1.0)
    geometry.wear_colors(bm, streams.stream("pylon_glow"), 0.0)
    obj = geometry.bm_to_object(bm, "Pylon_Face", collection, finish=False)
    obj.data.materials.append(mat)
    return obj


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    variant = PP.resolve(plan)
    got = PP.plan(w, d, h, variant)
    f = got["facts"]
    rng = streams.stream("wear")
    objs = []
    steel = [p for p in got["prims"] if p["mat"] != "glow"]
    for mk in sorted({p["mat"] for p in steel}):
        kind, factor = PP.vertex_tint(mk)
        mine = [dict(p, part=f"{p['part']}_{mk}") for p in steel if p["mat"] == mk]
        built = prim_mesh.build(mine, collection, plan, rng,
                                {mk: ("M_Pylon_steel", list(PP.KIND_BASE[kind]), kind)}, texel=1.0)
        for o in built:
            geometry.tint_wear(o, factor)
        objs.extend(built)
    A = PP.art(w, h, variant)
    glow = materials.make_backlit_material(
        f"M_Pylon_{A['name']}_Face", materials.image_from_png(A["name"], A["canvas"].png()),
        PP.GLOW_EMISSION, PP.GLOW_ALBEDO)
    objs.append(_glow([p for p in got["prims"] if p["mat"] == "glow"], A, glow, collection, streams))
    print(f"[price_pylon] prices={f['prices']} art={A['name']}")
    return {"objects": objs, "collision_boxes": [f["collision"]], "attachments": {},
            "price_pylon": {"prices": f["prices"], "art": A["name"]}}
