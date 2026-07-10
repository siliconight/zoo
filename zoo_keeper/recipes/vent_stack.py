"""vent_stack recipe: a roof vent stack — base plate, stack, rain cap.
``profile`` param: round (metal flue) or square (reads as a brick chimney).
Built centered; bottom at -h/2."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    square = plan["params"].get("profile", "round") == "square"
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    z0 = -h / 2.0
    r = min(w, d) / 2.0
    objs, cboxes = [], []

    def part(bm, name, texel=1.5):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + 0.03), (w * 1.3, d * 1.3, 0.06))
    part(bm, "VentStack_Base")

    stack_h = h * 0.86
    bm = geometry.new_bm()
    if square:
        geometry.add_box(bm, (0.0, 0.0, z0 + 0.06 + stack_h / 2),
                         (w, d, stack_h))
    else:
        geometry.add_cylinder(bm, (0.0, 0.0, z0 + 0.06 + stack_h / 2),
                              r * 0.8, stack_h, segments=10)
    part(bm, "VentStack_Stack")
    cboxes.append(((-w / 2, -d / 2, z0), (w / 2, d / 2, z0 + 0.06 + stack_h)))

    bm = geometry.new_bm()
    if square:
        geometry.add_box(bm, (0.0, 0.0, h / 2 - 0.03), (w * 1.25, d * 1.25, 0.06))
    else:
        geometry.add_cylinder(bm, (0.0, 0.0, h / 2 - 0.04),
                              r * 1.05, 0.08, segments=10)
    part(bm, "VentStack_Cap")

    mat = materials.make_material(
        f"M_VentStack_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
