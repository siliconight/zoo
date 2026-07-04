"""Filing cabinet recipe: a vertical file — body box, N stacked drawer
fronts (proud toward -Y) with bar handles, and a recessed kick base.

Layout (origin at floor center, drawers face -Y). Reuses the same proud-front
+ bar-handle construction as the desk pedestal.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def _darker(c, f=0.62):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    n_drawers = plan["params"]["drawers"]
    has_base = plan["params"].get("base", 1)
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.5,
            rng=rng, wear=wear))

    base_h = 0.06 if has_base else 0.0

    # recessed kick base
    if has_base:
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, 0, base_h / 2), (w * 0.94, d * 0.94, base_h))
        part(bm, "Cabinet_Base")
        cboxes.append(((-w * 0.47, -d * 0.47, 0),
                       (w * 0.47, d * 0.47, base_h)))

    # main body
    body_h = h - base_h
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, base_h + body_h / 2), (w, d, body_h))
    part(bm, "Cabinet_Body")
    cboxes.append(((-w / 2, -d / 2, base_h), (w / 2, d / 2, h)))

    # stacked drawer fronts, proud of the front face (-Y)
    gap = 0.015
    dh = (body_h - gap * (n_drawers + 1)) / n_drawers
    front_y = -d / 2 - 0.009
    for i in range(n_drawers):
        z = base_h + gap + dh / 2 + i * (dh + gap)
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, front_y, z), (w - 0.04, 0.018, dh))
        part(bm, f"Cabinet_Drawer_{i + 1}")
        # horizontal bar pull, upper third of the drawer face
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, front_y - 0.02, z + dh * 0.28),
                         (w * 0.4, 0.022, 0.02))
        part(bm, f"Cabinet_Handle_{i + 1}")

    # materials: body + drawer fronts share the cabinet color; base and
    # handles are the darker frame tone.
    surface = materials.make_material(
        f"M_Cabinet_{plan['material']}", plan["color"], plan["material"])
    frame = materials.make_material(
        f"M_Cabinet_frame_{plan['material']}", _darker(plan["color"]),
        plan["material"])
    frame_objs = [o for o in objs if "Base" in o.name or "Handle" in o.name]
    materials.assign([o for o in objs if o not in frame_objs], surface)
    materials.assign(frame_objs, frame)

    return {
        "objects": objs,
        "collision_boxes": cboxes,
        "attachments": {"ATT_top_center": (0, 0, h)},
    }
