"""Briefcase recipe: flat hard-shell case lying on its side, arched top
handle, front latches. Origin at floor center; thickness runs up +Z, so the
case rests on the ground and the handle points up."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def _darker(c, f=0.55):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]      # long side (X)
    d = plan["dimensions"]["depth"]      # short side (Y)
    th = plan["dimensions"]["height"]    # thickness (Z)
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    n_latch = plan["params"].get("latches", 2)
    objs, cboxes = [], []

    def part(bm, name, texel=2.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, th / 2), (w, d, th))
    part(bm, "Case_Body")
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, th)))

    # arched handle above the top face: two posts + a bar
    for side, sx in (("L", -1), ("R", 1)):
        bm = geometry.new_bm()
        geometry.add_box(bm, (sx * w * 0.18, 0, th + 0.03), (0.02, 0.02, 0.06))
        part(bm, f"Case_HandlePost_{side}")
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, th + 0.06), (w * 0.4, 0.022, 0.022))
    part(bm, "Case_HandleBar")

    # latches on the front face (-Y), near the seam
    xs = [0.0] if n_latch == 1 else [-w * 0.24, w * 0.24]
    for i, x in enumerate(xs):
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, -d / 2 - 0.006, th * 0.5),
                         (0.04, 0.016, 0.028))
        part(bm, f"Case_Latch_{i + 1}")

    body_mat = materials.make_material(
        f"M_Case_{plan['material']}", plan["color"], plan["material"])
    metal = materials.make_material("M_Case_metal",
                                    _darker(plan["color"], 0.7)
                                    if plan["material"] == "metal"
                                    else [0.62, 0.62, 0.64], "metal")
    bodies = [o for o in objs if "Body" in o.name]
    materials.assign(bodies, body_mat)
    materials.assign([o for o in objs if o not in bodies], metal)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_handle": (0, 0, th + 0.06)}}
