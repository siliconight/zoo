"""CRT TV recipe: chunky plastic body, recessed dark screen, small feet and
tuning knobs. 1990s tube-television silhouette. Origin at floor center,
screen faces -Y."""
from __future__ import annotations

from ..bpylayer import geometry, materials

FOOT_H = 0.02


def _darker(c, f=0.6):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    n_knobs = plan["params"].get("knobs", 2)
    objs, cboxes = [], []

    def part(bm, name, texel=2.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    body_h = h - FOOT_H
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, FOOT_H + body_h / 2), (w, d, body_h))
    part(bm, "CRT_Body")
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, h)))

    # recessed screen on the front face (-Y), sits just inside the bezel
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, -d / 2 + 0.02, FOOT_H + body_h * 0.56),
                     (w * 0.80, 0.02, body_h * 0.64))
    part(bm, "CRT_Screen")

    # tuning knobs, lower-right of the front face
    for i in range(min(n_knobs, 4)):
        bm = geometry.new_bm()
        geometry.add_cylinder(
            bm, (w * 0.30 - i * 0.05, -d / 2 - 0.012, FOOT_H + body_h * 0.16),
            radius=0.016, depth=0.02, segments=12, axis="Y")
        part(bm, f"CRT_Knob_{i + 1}")

    # two feet
    for side, sx in (("L", -1), ("R", 1)):
        bm = geometry.new_bm()
        geometry.add_box(bm, (sx * w * 0.34, 0, FOOT_H / 2),
                         (w * 0.14, d * 0.5, FOOT_H))
        part(bm, f"CRT_Foot_{side}")

    body_mat = materials.make_material(
        f"M_CRT_{plan['material']}", plan["color"], plan["material"])
    screen_mat = materials.make_material(
        "M_CRT_screen", [0.03, 0.04, 0.05], "glass")
    knob_mat = materials.make_material(
        "M_CRT_knob", _darker(plan["color"], 0.4), "plastic")
    screens = [o for o in objs if "Screen" in o.name]
    knobs = [o for o in objs if "Knob" in o.name or "Foot" in o.name]
    materials.assign(screens, screen_mat)
    materials.assign(knobs, knob_mat)
    materials.assign([o for o in objs if o not in screens and o not in knobs],
                     body_mat)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_screen_center": (0, -d / 2, FOOT_H + body_h * 0.56)}}
