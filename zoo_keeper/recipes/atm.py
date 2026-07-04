"""ATM recipe: freestanding cash machine — body, recessed screen, keypad,
card slot, cash dispenser, optional lit top sign. Origin at floor center,
face toward -Y."""
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
    objs, cboxes = [], []
    fy = -d / 2  # front face plane

    def part(bm, name, texel=1.5):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, h / 2), (w, d, h))
    part(bm, "ATM_Body")
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, h)))

    # recessed screen, upper front
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, fy + 0.02, h * 0.74), (w * 0.6, 0.02, h * 0.16))
    part(bm, "ATM_Screen")

    # keypad panel, mid front (slightly proud)
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, fy - 0.015, h * 0.52), (w * 0.5, 0.03, h * 0.13))
    part(bm, "ATM_Keypad")

    # card slot (right) and cash dispenser (below keypad)
    bm = geometry.new_bm()
    geometry.add_box(bm, (w * 0.26, fy - 0.01, h * 0.62), (0.09, 0.03, 0.016))
    part(bm, "ATM_CardSlot")

    bm = geometry.new_bm()
    geometry.add_box(bm, (0, fy - 0.01, h * 0.34), (w * 0.5, 0.04, 0.05))
    part(bm, "ATM_CashSlot")

    if plan["params"].get("sign", 1):
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, 0, h + 0.06), (w * 0.9, d * 0.6, 0.12))
        part(bm, "ATM_Sign")
        cboxes.append(((-w * 0.45, -d * 0.3, h), (w * 0.45, d * 0.3, h + 0.12)))

    body_mat = materials.make_material(
        f"M_ATM_{plan['material']}", plan["color"], plan["material"])
    screen_mat = materials.make_material("M_ATM_screen", [0.03, 0.05, 0.08],
                                         "glass")
    dark = materials.make_material("M_ATM_trim", _darker(plan["color"], 0.45),
                                   "plastic")
    sign_mat = materials.make_material("M_ATM_sign", [0.85, 0.80, 0.35],
                                       "plastic")
    for o in objs:
        if "Screen" in o.name:
            materials.assign([o], screen_mat)
        elif "Sign" in o.name:
            materials.assign([o], sign_mat)
        elif "Body" in o.name:
            materials.assign([o], body_mat)
        else:
            materials.assign([o], dark)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_cash_slot": (0, fy, h * 0.34)}}
