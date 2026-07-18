"""wallCorner recipe: L-shaped corner module joining two wall runs.

Leg A runs along +X (length = width), leg B along +Y (length = depth), both
`params.thickness` thick (0 = derive 0.3), sharing the corner column so the
seam is interior. Pivot at the OUTSIDE corner, ground level — the corner
drops onto the meeting point of two DC wall runs with no offset math.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    la = plan["dimensions"]["width"]       # leg A length (+X)
    lb = plan["dimensions"]["depth"]       # leg B length (+Y)
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    t = float(plan["params"].get("thickness", 0.0)) or 0.3
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.2, rng=rng, wear=wear))

    # leg A: from the pivot along +X, thickness toward +Y
    bm = geometry.new_bm()
    geometry.add_box(bm, (la / 2, t / 2, h / 2), (la, t, h))
    part(bm, "Corner_LegA")
    cboxes.append(((0.0, 0.0, 0.0), (la, t, h)))

    # leg B: from the pivot along +Y, thickness toward +X, minus the shared
    # corner column so the two legs don't z-fight
    if lb > t:
        bm = geometry.new_bm()
        geometry.add_box(bm, (t / 2, t + (lb - t) / 2, h / 2), (t, lb - t, h))
        part(bm, "Corner_LegB")
        cboxes.append(((0.0, t, 0.0), (t, lb, h)))

    mat = materials.make_material(
        f"M_Corner_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
