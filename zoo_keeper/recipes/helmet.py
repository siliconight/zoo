"""Helmet recipe: solidified hemisphere shell, optional brim and visor."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    seg = plan["params"]["segments"]
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=2.0,
            rng=rng, wear=wear))

    bm = geometry.new_bm()
    geometry.add_hemisphere(bm, (0, 0, 0), w / 2, d / 2, h, segments=seg)
    geometry.solidify(bm, 0.012)
    part(bm, "Helmet_Shell")
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, h)))

    if plan["params"].get("brim"):
        bm = geometry.new_bm()
        geometry.add_cylinder(bm, (0, 0, 0.008),
                              radius=max(w, d) / 2 + 0.035,
                              depth=0.012, segments=seg)
        part(bm, "Helmet_Brim")

    if plan["params"].get("visor"):
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, -d / 2 - 0.008, h * 0.35),
                         (w * 0.85, 0.012, h * 0.55))
        part(bm, "Helmet_Visor")

    mat = materials.make_material(
        f"M_Helmet_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_head_socket": (0, 0, 0)}}
