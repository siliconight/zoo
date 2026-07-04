"""Condiment squeeze bottle: tapered plastic body, cap, nozzle tip. The
flavor (ketchup/mustard/mayo/hot sauce) is set by the DNA hook via color.
Origin at floor center."""
from __future__ import annotations

from ..bpylayer import geometry, materials

SEG = 12


def build(plan, streams, collection):
    r = plan["dimensions"]["width"] / 2
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []

    def part(bm, name, texel=4.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    # squeeze body: full at the base, tapering in near the neck
    body_h = h * 0.72
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0, 0, body_h / 2), r, body_h, segments=SEG,
                          radius_top=r * 0.6)
    part(bm, "Bottle_Body")
    cboxes.append(((-r, -r, 0), (r, r, h)))

    # cap
    cap_h = h * 0.16
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0, 0, body_h + cap_h / 2), r * 0.58, cap_h,
                          segments=SEG)
    part(bm, "Bottle_Cap")

    # nozzle tip
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0, 0, body_h + cap_h + h * 0.06),
                          r * 0.22, h * 0.12, segments=8, radius_top=r * 0.08)
    part(bm, "Bottle_Nozzle")

    body_mat = materials.make_material(
        f"M_Bottle_{plan['material']}", plan["color"], plan["material"])
    cap_mat = materials.make_material("M_Bottle_cap", [0.90, 0.90, 0.92],
                                      "plastic")
    for o in objs:
        if "Cap" in o.name or "Nozzle" in o.name:
            materials.assign([o], cap_mat)
        else:
            materials.assign([o], body_mat)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_cap": (0, 0, h)}}
