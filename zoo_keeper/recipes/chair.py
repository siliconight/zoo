"""Chair recipe: seat slab, back panel, post legs, optional arms."""
from __future__ import annotations

from ..bpylayer import geometry, materials

SEAT_T = 0.04
LEG_S = 0.035
SEAT_H = 0.45


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, rng=rng, wear=wear))

    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, SEAT_H - SEAT_T / 2), (w, d, SEAT_T))
    part(bm, "Chair_Seat")
    cboxes.append(((-w / 2, -d / 2, SEAT_H - SEAT_T), (w / 2, d / 2, SEAT_H)))

    back_h = h - SEAT_H
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, d / 2 - 0.015, SEAT_H + back_h / 2),
                     (w, 0.03, back_h))
    part(bm, "Chair_Back")
    cboxes.append(((-w / 2, d / 2 - 0.03, SEAT_H), (w / 2, d / 2, h)))

    n_legs = plan["params"]["legs"]
    inset = 0.03
    corners = [(-1, -1), (1, -1), (-1, 1), (1, 1)][:n_legs]
    for i, (sx, sy) in enumerate(corners, start=1):
        x = sx * (w / 2 - inset - LEG_S / 2)
        y = sy * (d / 2 - inset - LEG_S / 2)
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, y, (SEAT_H - SEAT_T) / 2),
                         (LEG_S, LEG_S, SEAT_H - SEAT_T))
        part(bm, f"Chair_Leg_{i}")
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, SEAT_H)))

    if plan["params"].get("has_arms"):
        arm_h = SEAT_H + 0.22
        for side, sx in (("L", -1), ("R", 1)):
            x = sx * (w / 2 - 0.015)
            bm = geometry.new_bm()
            geometry.add_box(bm, (x, 0, arm_h), (0.03, d * 0.8, 0.03))
            geometry.add_box(bm, (x, -d * 0.32, (arm_h + SEAT_H) / 2),
                             (0.03, 0.03, arm_h - SEAT_H))
            part(bm, f"Chair_Arm_{side}")

    mat = materials.make_material(
        f"M_Chair_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_seat_center": (0, 0, SEAT_H)}}
