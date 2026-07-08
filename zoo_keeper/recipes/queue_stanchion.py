"""queue_stanchion recipe: a rope/belt queue post — weighted disc base, a slim
post, a finial cap, and a belt hook. Origin at floor center. A top ATT_belt
socket lets a belt/rope link to the next stanchion."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    r_base = min(w, d) / 2.0
    base_h = 0.035

    def part(bm, name, texel=2.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    # weighted base disc
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, base_h / 2.0), r_base, base_h,
                          segments=20, axis="Z")
    part(bm, "QueueStanchion_Base")
    cboxes.append(((-r_base, -r_base, 0.0), (r_base, r_base, base_h)))

    # slim post
    post_r = 0.022
    post_top = h - 0.06
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, (base_h + post_top) / 2.0), post_r,
                          post_top - base_h, segments=14, axis="Z")
    part(bm, "QueueStanchion_Post")
    # thin full-height collision so you can't walk through the post
    cboxes.append(((-0.06, -0.06, base_h), (0.06, 0.06, post_top)))

    # finial cap
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, post_top + 0.03), post_r * 1.7, 0.06,
                          segments=16, axis="Z", radius_top=post_r * 0.6)
    part(bm, "QueueStanchion_Finial")

    # belt hook (a small tab near the top where the belt clips)
    bm = geometry.new_bm()
    geometry.add_box(bm, (post_r + 0.02, 0.0, post_top - 0.05),
                     (0.05, 0.06, 0.04))
    part(bm, "QueueStanchion_Hook")

    materials.assign(objs, materials.make_material(
        f"M_QueueStanchion_{plan['material']}", plan["color"],
        plan["material"]))

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_belt": (0.0, 0.0, post_top - 0.05)}}
