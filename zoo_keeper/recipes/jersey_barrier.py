"""jersey_barrier recipe: a precast concrete traffic barrier.

Roadmap 153, the forecourt. The walker's Call of Duty frames: a concrete
barrier dragged across a lane is the cheapest thing on the street and one
of the most legible -- it says somebody closed this off. The profile is
the object: a wide foot, a steep lower slope to about a third of the
height, then a near-vertical face to a narrow top. Built as three stacked
boxes with the lower one tapered, which is the shape at this scale.

Collision is the whole barrier: it is waist-high cover, and cover a body
can walk through is the one defect this pipeline keeps measuring for.
Centre pivot; extents exactly (w, d, h).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

TOP_FRAC = 0.34       # of the width, at the top
FOOT_H = 0.16         # the splayed foot
SLOPE_H = 0.22        # the steep lower slope


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]      # across the barrier
    d = plan["dimensions"]["depth"]      # along it
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0

    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + FOOT_H / 2.0), (w, d, FOOT_H))
    slope = geometry.add_box(bm, (0.0, 0.0, z0 + FOOT_H + SLOPE_H / 2.0),
                             (w, d, SLOPE_H))
    geometry.taper_z(slope, 0.62, 1.0)
    body_h = h - FOOT_H - SLOPE_H
    body = geometry.add_box(bm, (0.0, 0.0, z0 + FOOT_H + SLOPE_H + body_h / 2.0),
                            (w * 0.62, d, body_h))
    geometry.taper_z(body, TOP_FRAC / 0.62, 1.0)
    obj = geometry.bm_to_object(bm, "JerseyBarrier_Body", collection,
                                bevel=bevel, texel=1.1, rng=rng, wear=wear)
    objs.append(obj)
    cboxes.append(((-w / 2.0, -d / 2.0, z0), (w / 2.0, d / 2.0, h / 2.0)))

    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)
    mat = materials.make_material(
        f"M_JerseyBarrier_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
