"""skylight recipe: a low curb-mounted skylight — curb frame and a glass top
slab. Built centered; bottom at -h/2."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    z0 = -h / 2.0
    objs, cboxes = [], []

    curb_h = h * 0.7
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + curb_h / 2), (w, d, curb_h))
    objs.append(geometry.bm_to_object(
        bm, "Skylight_Curb", collection, bevel=bevel, texel=1.5,
        rng=rng, wear=wear))
    cboxes.append(((-w / 2, -d / 2, z0), (w / 2, d / 2, h / 2)))

    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + curb_h + (h - curb_h) / 2),
                     (w * 0.92, d * 0.92, h - curb_h))
    glass_obj = geometry.bm_to_object(
        bm, "Skylight_Glass", collection, bevel=bevel, texel=1.5,
        rng=rng, wear=0.05)
    objs.append(glass_obj)

    curb_mat = materials.make_material(
        f"M_Skylight_{plan['material']}", plan["color"], plan["material"])
    materials.assign([objs[0]], curb_mat)
    glass_mat = materials.make_material(
        "M_Skylight_glass", [0.10, 0.14, 0.18], "glass")
    materials.assign([glass_obj], glass_mat)
    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
