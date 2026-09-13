"""mailbox recipe: a kerbside collection box.

Roadmap 153, the 1990s American street. The blue steel collection box on
a corner: a boxy body about 0.6 m wide and 1.15 m tall on two short legs,
a domed lid hinged at the back, and a pull-down door on the front with a
lip over it. Unbranded -- the shape and the blue are what a player reads
from the sidewalk, and no service's markings are reproduced.

Collision is the whole body: a body walks around a mailbox. Centre pivot;
extents exactly (w, d, h).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

LEG = 0.07
LEG_H = 0.22
LIP = 0.05


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0
    body_parts, dark = [], []

    def part(bm, name, into, texel=1.2):
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel,
                                    texel=texel, rng=rng, wear=wear)
        objs.append(obj)
        into.append(obj)
        return obj

    # legs
    bm = geometry.new_bm()
    for sx in (-1, 1):
        geometry.add_box(bm, (sx * (w / 2.0 - LEG), 0.0, z0 + LEG_H / 2.0),
                         (LEG, d * 0.7, LEG_H))
    part(bm, "Mailbox_Legs", dark)

    # body: from the legs to under the lid, its top face tapered back so
    # the lid sits on a slope the way a collection box's does
    body_h = (h - LEG_H) * 0.72
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + LEG_H + body_h / 2.0), (w, d, body_h))
    part(bm, "Mailbox_Body", body_parts)

    # the domed lid: a box tapered to the front, hinged at the back
    lid_h = h - LEG_H - body_h
    bm = geometry.new_bm()
    verts = geometry.add_box(bm, (0.0, d * 0.06, h / 2.0 - lid_h / 2.0),
                             (w, d * 0.88, lid_h))
    geometry.taper_z(verts, 0.82, 1.0)
    part(bm, "Mailbox_Lid", body_parts)

    # the pull-down door and its lip, on the -y face
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, -d / 2.0 - 0.012, z0 + LEG_H + body_h * 0.62),
                     (w * 0.72, 0.025, body_h * 0.42))
    geometry.add_box(bm, (0.0, -d / 2.0 - 0.02, z0 + LEG_H + body_h * 0.84),
                     (w * 0.76, 0.04, LIP))
    part(bm, "Mailbox_Door", dark, texel=1.6)

    cboxes.append(((-w / 2.0, -d / 2.0, z0), (w / 2.0, d / 2.0, h / 2.0)))

    blue = materials.make_material(
        f"M_Mailbox_{plan['material']}", plan["color"], plan["material"])
    trim = materials.make_material("M_Mailbox_trim", [0.13, 0.15, 0.18],
                                   "metal_painted")
    materials.assign(body_parts, blue)
    materials.assign(dark, trim)
    # the slot is exact; the detail is not (geometry.fit_to)
    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
