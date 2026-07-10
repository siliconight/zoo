"""water_tank recipe: a rooftop water tank — four legs, cylindrical tank,
stepped cap. Built centered; bottom at -h/2."""
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

    def part(bm, name, texel=1.2):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    leg_h = h * 0.28
    bm = geometry.new_bm()
    for sx in (-1, 1):
        for sy in (-1, 1):
            geometry.add_box(bm, (sx * r * 0.62, sy * r * 0.62,
                                  z0 + leg_h / 2), (0.09, 0.09, leg_h))
    part(bm, "WaterTank_Legs")

    tank_h = h * 0.62
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + leg_h + tank_h / 2),
                          r, tank_h, segments=14)
    part(bm, "WaterTank_Tank")
    cboxes.append(((-r, -r, z0), (r, r, z0 + leg_h + tank_h)))

    cap_h = h - leg_h - tank_h
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + leg_h + tank_h + cap_h * 0.3),
                          r * 0.92, cap_h * 0.6, segments=14)
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + leg_h + tank_h + cap_h * 0.8),
                          r * 0.45, cap_h * 0.4, segments=10)
    part(bm, "WaterTank_Cap")

    mat = materials.make_material(
        f"M_WaterTank_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
