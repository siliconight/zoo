"""Vending machine recipe: tall body, big tinted front glass, a coin/button
side panel, and a dispense tray. Origin at floor center, face toward -Y."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def _darker(c, f=0.55):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    fy = -d / 2

    def part(bm, name, texel=1.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, h / 2), (w, d, h))
    part(bm, "Vending_Body")
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, h)))

    # large tinted display window on the left ~2/3 of the front
    gx = -w * 0.16
    bm = geometry.new_bm()
    geometry.add_box(bm, (gx, fy + 0.02, h * 0.6), (w * 0.6, 0.03, h * 0.72))
    part(bm, "Vending_Glass")

    # right-hand selection / coin panel
    px = w * 0.32
    bm = geometry.new_bm()
    geometry.add_box(bm, (px, fy - 0.01, h * 0.62), (w * 0.26, 0.02, h * 0.7))
    part(bm, "Vending_Panel")

    bm = geometry.new_bm()
    geometry.add_box(bm, (px, fy - 0.03, h * 0.7), (0.03, 0.03, 0.06))
    part(bm, "Vending_CoinSlot")

    # dispense tray at the bottom
    bm = geometry.new_bm()
    geometry.add_box(bm, (gx, fy - 0.005, h * 0.12), (w * 0.5, 0.05, h * 0.12))
    part(bm, "Vending_Tray")

    body_mat = materials.make_material(
        f"M_Vending_{plan['material']}", plan["color"], plan["material"])
    glass_mat = materials.make_material("M_Vending_glass", [0.05, 0.07, 0.06],
                                        "glass")
    dark = materials.make_material("M_Vending_trim",
                                   _darker(plan["color"]), "plastic")
    for o in objs:
        if "Glass" in o.name:
            materials.assign([o], glass_mat)
        elif "Body" in o.name:
            materials.assign([o], body_mat)
        else:
            materials.assign([o], dark)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_tray": (gx, fy, h * 0.12)}}
