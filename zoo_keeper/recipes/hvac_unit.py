"""hvac_unit recipe: a rooftop RTU — curb base, main cabinet, fan cowl on top,
side intake grille, and a conduit drop. Built centered so the bbox is
(w, d, h); sits on a roof plane, bottom at -h/2."""
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

    def part(bm, name, texel=1.5):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    curb_h = h * 0.16
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + curb_h / 2), (w * 0.9, d * 0.9, curb_h))
    part(bm, "Hvac_Curb")

    cab_h = h * 0.66
    cab_z = z0 + curb_h + cab_h / 2
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, cab_z), (w, d, cab_h))
    part(bm, "Hvac_Cabinet")
    cboxes.append(((-w / 2, -d / 2, z0), (w / 2, d / 2, z0 + curb_h + cab_h)))

    cowl_h = h - curb_h - cab_h
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (-w * 0.22, 0.0, z0 + curb_h + cab_h + cowl_h / 2),
                          min(w, d) * 0.28, cowl_h, segments=12)
    part(bm, "Hvac_FanCowl")

    bm = geometry.new_bm()
    geometry.add_box(bm, (w * 0.30, -d / 2 + 0.015, cab_z),
                     (w * 0.34, 0.03, cab_h * 0.6))
    part(bm, "Hvac_Grille")

    bm = geometry.new_bm()
    geometry.add_box(bm, (w / 2 - 0.05, d * 0.3, z0 + (curb_h + cab_h) * 0.5),
                     (0.06, 0.06, curb_h + cab_h))
    part(bm, "Hvac_Conduit")

    mat = materials.make_material(
        f"M_Hvac_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
