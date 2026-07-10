"""exhaust_fan recipe: a mushroom roof fan — curb, drum body, dome cap.
Built centered; bottom at -h/2."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    z0 = -h / 2.0
    r = min(w, d) / 2.0
    objs, cboxes = [], []

    def part(bm, name, texel=2.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    curb_h = h * 0.3
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + curb_h / 2),
                     (w * 0.8, d * 0.8, curb_h))
    part(bm, "ExhaustFan_Curb")

    drum_h = h * 0.4
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + curb_h + drum_h / 2),
                          r * 0.7, drum_h, segments=12)
    part(bm, "ExhaustFan_Drum")

    bm = geometry.new_bm()
    geometry.add_hemisphere(bm, (0.0, 0.0, z0 + curb_h + drum_h),
                            r, r, h * 0.3, segments=12)
    part(bm, "ExhaustFan_Dome")
    cboxes.append(((-r, -r, z0), (r, r, h / 2)))

    mat = materials.make_material(
        f"M_ExhaustFan_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
