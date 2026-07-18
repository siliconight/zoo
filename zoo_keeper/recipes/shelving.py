"""shelving recipe: freestanding shelf unit (store gondola / stockroom rack).

Two side uprights, N evenly spaced shelf boards, optional back panel.
Origin at floor center; shelves open toward -Y (customer/picking side).
Proportions read the identity: wide+low+wood = retail gondola, tall+deep+
metal = stockroom racking — same recipe, different plan.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def _darker(c, f=0.7):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    n_shelves = max(2, int(plan["params"]["shelves"]))
    back = bool(plan["params"].get("back", 1))
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.4, rng=rng, wear=wear))

    up = 0.05
    for side, x in (("L", -w / 2 + up / 2), ("R", w / 2 - up / 2)):
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, 0.0, h / 2), (up, d, h))
        part(bm, f"Shelf_Upright_{side}")

    board = 0.035
    for i in range(n_shelves):
        z = board / 2 + i * (h - board) / (n_shelves - 1)
        bm = geometry.new_bm()
        geometry.add_box(bm, (0.0, 0.0, z), (w - up * 2, d * 0.96, board))
        part(bm, f"Shelf_Board_{i + 1}")

    if back:
        bm = geometry.new_bm()
        geometry.add_box(bm, (0.0, d / 2 - 0.01, h / 2), (w - up * 2, 0.02, h))
        part(bm, "Shelf_Back")

    # collision: the full unit as one solid (cover object; per-shelf collision
    # is loot-system territory, not the shell's)
    cboxes.append(((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h)))

    surface = materials.make_material(
        f"M_Shelf_{plan['material']}", plan["color"], plan["material"])
    frame = materials.make_material(
        f"M_Shelf_frame_{plan['material']}", _darker(plan["color"]),
        plan["material"])
    frame_objs = [o for o in objs if "Upright" in o.name or "Back" in o.name]
    materials.assign([o for o in objs if o not in frame_objs], surface)
    materials.assign(frame_objs, frame)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_shelf_top": (0.0, 0.0, h)}}
