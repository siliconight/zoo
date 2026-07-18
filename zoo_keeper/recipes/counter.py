"""counter recipe: generic service counter (deli / pharmacy / pawn front line).

Solid body, proud countertop overhanging the customer side (-Y), recessed
kick base, optional staff-side under-shelf. Origin at floor center. The
generic sibling of the bank teller_line — same posture, no security barrier.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def _darker(c, f=0.6):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    overhang = bool(plan["params"].get("overhang", 1))
    shelf = bool(plan["params"].get("shelf", 1))
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.4, rng=rng, wear=wear))

    base_h = 0.07
    top_t = 0.045
    body_d = d * (0.85 if overhang else 1.0)
    body_y = (d - body_d) / 2 if overhang else 0.0   # body pushed to staff side

    # recessed kick base
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, body_y, base_h / 2),
                     (w * 0.96, body_d * 0.92, base_h))
    part(bm, "Counter_Base")

    # body
    body_h = h - base_h - top_t
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, body_y, base_h + body_h / 2),
                     (w, body_d, body_h))
    part(bm, "Counter_Body")

    # countertop, proud on every side, overhanging the customer face
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, h - top_t / 2),
                     (w + 0.04, d, top_t))
    part(bm, "Counter_Top")

    # staff-side under-shelf
    if shelf:
        bm = geometry.new_bm()
        geometry.add_box(bm, (0.0, body_y + body_d * 0.3, base_h + body_h * 0.5),
                         (w * 0.9, body_d * 0.35, 0.03))
        part(bm, "Counter_Shelf")

    cboxes.append(((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h)))

    top = materials.make_material(
        f"M_Counter_top_{plan['material']}", _darker(plan["color"], 0.85),
        plan["material"])
    body = materials.make_material(
        f"M_Counter_{plan['material']}", plan["color"], plan["material"])
    frame = materials.make_material(
        f"M_Counter_base_{plan['material']}", _darker(plan["color"]),
        plan["material"])
    for o in objs:
        if "Top" in o.name:
            materials.assign([o], top)
        elif "Base" in o.name:
            materials.assign([o], frame)
        else:
            materials.assign([o], body)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_register": (w * 0.15, 0.0, h),
                            "ATT_counter_front": (0.0, -d / 2, h)}}
