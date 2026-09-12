"""bus_shelter recipe: four posts, a roof, a glazed back and two glazed ends.

Roadmap 153, the waiting places. A bus shelter is a steel frame with a
flat roof and glass on three sides; the fourth side, the long one, is
open to the kerb so people step out to the bus. Lot places it with its
back (+y in this frame) toward the buildings and its open face toward
the road, and stands the bench inside it.

Extents are exactly (w, d, h): the posts stand at the corners, the roof
spans the full width and depth, the roof's top is +h/2. Collision is the
posts, the back pane and the two end panes -- the roof is above a body
and the open face is open. Centre pivot like every module.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

POST = 0.06          # square steel post
ROOF_T = 0.08
PANE_T = 0.02
SILL = 0.25          # glass starts this far above grade (a kick panel's height)


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0
    frame, panes = [], []

    def part(bm, name, into, texel=1.2):
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel,
                                    texel=texel, rng=rng, wear=wear)
        objs.append(obj)
        into.append(obj)
        return obj

    # posts at the four corners, grade to the roof's underside
    post_h = h - ROOF_T
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), start=1):
        x = sx * (w / 2.0 - POST / 2.0)
        y = sy * (d / 2.0 - POST / 2.0)
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, y, z0 + post_h / 2.0), (POST, POST, post_h))
        part(bm, f"BusShelter_Post_{i}", frame)
        cboxes.append(((x - POST / 2.0, y - POST / 2.0, z0),
                       (x + POST / 2.0, y + POST / 2.0, z0 + post_h)))

    # roof: the full footprint, its top at +h/2
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, h / 2.0 - ROOF_T / 2.0), (w, d, ROOF_T))
    part(bm, "BusShelter_Roof", frame)

    # glass: the back (toward +y, the buildings) and both ends, from the
    # sill to the roof; the front (-y, the kerb) is open
    pane_h = post_h - SILL
    zc = z0 + SILL + pane_h / 2.0
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, d / 2.0 - POST - PANE_T / 2.0, zc),
                     (w - 2 * POST, PANE_T, pane_h))
    part(bm, "BusShelter_Back", panes, texel=0.5)
    cboxes.append(((-w / 2.0, d / 2.0 - POST - PANE_T, z0),
                   (w / 2.0, d / 2.0 - POST, z0 + post_h)))
    for tag, sx in (("L", -1), ("R", 1)):
        x = sx * (w / 2.0 - POST - PANE_T / 2.0)
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, 0.0, zc), (PANE_T, d - 2 * POST, pane_h))
        part(bm, f"BusShelter_End_{tag}", panes, texel=0.5)
        cboxes.append(((x - PANE_T / 2.0, -d / 2.0, z0),
                       (x + PANE_T / 2.0, d / 2.0, z0 + post_h)))

    steel = materials.make_material(
        f"M_BusShelter_{plan['material']}", plan["color"], plan["material"])
    glass = materials.make_material("M_BusShelter_glass", [0.72, 0.8, 0.82], "glass")
    materials.assign(frame, steel)
    materials.assign(panes, glass)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
