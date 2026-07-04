"""Boots recipe: mirrored pair — sole, foot, toe, shaft."""
from __future__ import annotations

from ..bpylayer import geometry, materials

SHAFT_H = {"ankle": 0.14, "mid": 0.22, "tall": 0.38}


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    shaft_h = SHAFT_H.get(plan["params"]["shaft_style"], 0.20)
    pair = plan["params"].get("pair", 2)
    sole_t, foot_h = 0.025, 0.07
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=3.0,
            rng=rng, wear=wear))

    sides = [("L", -1), ("R", 1)][:pair]
    gap = w * 0.65
    for tag, sx in sides:
        x = sx * gap
        # sole
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, 0, sole_t / 2), (w, d, sole_t))
        part(bm, f"Boot_{tag}_Sole")
        # foot body (heel-to-mid), toe box lower in front (-Y)
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, d * 0.12, sole_t + foot_h / 2),
                         (w * 0.94, d * 0.72, foot_h))
        geometry.add_box(bm, (x, -d * 0.34, sole_t + foot_h * 0.35),
                         (w * 0.90, d * 0.30, foot_h * 0.7))
        part(bm, f"Boot_{tag}_Foot")
        # shaft over the heel
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, d * 0.24, sole_t + foot_h + shaft_h / 2),
                         (w * 0.90, d * 0.44, shaft_h))
        part(bm, f"Boot_{tag}_Shaft")
        top = sole_t + foot_h + shaft_h
        cboxes.append(((x - w / 2, -d / 2, 0), (x + w / 2, d / 2, top)))

    mat = materials.make_material(
        f"M_Boots_{plan['material']}", plan["color"], plan["material"])
    sole_mat = materials.make_material(
        "M_Boots_sole_rubber", [0.06, 0.06, 0.06], "rubber")
    soles = [o for o in objs if o.name.endswith("_Sole")]
    materials.assign([o for o in objs if o not in soles], mat)
    materials.assign(soles, sole_mat)

    att = {"ATT_foot_l": (-gap, 0, sole_t)}
    if pair == 2:
        att["ATT_foot_r"] = (gap, 0, sole_t)
    return {"objects": objs, "collision_boxes": cboxes, "attachments": att}
