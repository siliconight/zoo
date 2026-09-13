"""parking_meter recipe: a single-space post meter.

Roadmap 153, the 1990s American street. The decade's meter is one head on
one post per space -- the multi-space kiosk is a later thing, and a row of
single meters down a kerb is half of what dates a street. A 1.2 m post, a
domed head with a display window on each side, and a coin slot.

Collision is the post and the head as one column: narrow enough that a
body brushes past it, tall enough to be a thing and not a trip hazard.
Centre pivot; extents exactly (w, d, h).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

POST_D = 0.055


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]      # the head, across the kerb
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0
    body, glass = [], []

    def part(bm, name, into, texel=1.6):
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel,
                                    texel=texel, rng=rng, wear=wear)
        objs.append(obj)
        into.append(obj)
        return obj

    head_h = h * 0.26
    post_h = h - head_h
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + 0.02), 0.07, 0.04, segments=8)
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + post_h / 2.0), POST_D / 2.0,
                          post_h, segments=8)
    # the head, its top tapered to a dome
    verts = geometry.add_box(bm, (0.0, 0.0, z0 + post_h + head_h * 0.42),
                             (w, d, head_h * 0.84))
    top = geometry.add_box(bm, (0.0, 0.0, h / 2.0 - head_h * 0.08),
                           (w, d, head_h * 0.16))
    geometry.taper_z(top, 0.55, 1.0)
    geometry.add_box(bm, (0.0, 0.0, z0 + post_h + head_h * 0.9),
                     (w * 0.3, d * 0.12, 0.05))              # the coin slot
    part(bm, "ParkingMeter_Body", body)

    # the display window, both faces
    bm = geometry.new_bm()
    for sy in (-1, 1):
        geometry.add_box(bm, (0.0, sy * (d / 2.0 + 0.006),
                              z0 + post_h + head_h * 0.5),
                         (w * 0.66, 0.015, head_h * 0.44))
    part(bm, "ParkingMeter_Window", glass, texel=1.0)

    cboxes.append(((-w / 2.0, -d / 2.0, z0), (w / 2.0, d / 2.0, h / 2.0)))

    paint = materials.make_material(
        f"M_ParkingMeter_{plan['material']}", plan["color"], plan["material"])
    pane = materials.make_material("M_ParkingMeter_glass", [0.7, 0.75, 0.76],
                                   "glass")
    materials.assign(body, paint)
    materials.assign(glass, pane)
    # the slot is exact; the detail is not (geometry.fit_to)
    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
