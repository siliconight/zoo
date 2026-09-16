"""mailbox recipe: a kerbside collection box.

Roadmap 153, the 1990s American street. The blue steel collection box on
a corner: a boxy body about 0.6 m wide and 1.15 m tall on two short legs,
a domed lid hinged at the back, and a pull-down door on the front with a
lip over it. Unbranded -- the shape and the blue are what a player reads
from the sidewalk, and no service's markings are reproduced.

Collision is the whole body: a body walks around a mailbox. Centre pivot;
extents exactly (w, d, h).

THE DOOR AND ITS LIP ARE PUSHED THROUGH THE BODY'S FACE, not laid on it.
This is `recipes/stop_sign.py`'s defect in a second place, found by the same
census: the lip's back cap lay exactly on the body's front face (0.00 mm over
117-238 cm2) and the door's back cap 0.5 mm behind it -- 0.46 mm once
`geometry.fit_to` squeezed the depth -- so three of the five pairs the probe
reported here were one cause. `BACK_BURY` is the rung that separates them and
is derived below. The other two (the lid's foot on the body's top face, the
legs' tops on the body's underside) are BUTT JOINTS between two closed
solids, 164 mm and 220 mm inside the prop, and this release does not touch
them: see `tests/test_coincident_faces.py`, which carries them as measured
residue rather than leaving them unsaid.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

LEG = 0.07
LEG_H = 0.22
LIP = 0.05
#: How far the door stands out of the body's front face, and the lip out of
#: the door -- the relief a collection box reads by, unchanged.
DOOR_PROUD = 0.0245
LIP_PROUD = 0.04
#: HOW FAR THEIR BACK CAPS SIT INSIDE THE BODY, derived rather than chosen.
#: `tools/coplanar_probe.py` reports two overlapping faces within 2 mm of one
#: plane and floats land on that number, so the pure tests ask a tenth more
#: (`tests/test_card_shop.py`). `geometry.fit_to` squeezes this recipe's
#: authored depth -- `d + LIP_PROUD`, because the lip is what stands proud of
#: the slot -- into the slot's `d`, a factor of 0.9245 at the genome's
#: smallest depth. THAT FACTOR IS NOT THE STOP SIGN'S (0.675), which is why
#: this is derived here and not shared: one constant would be wrong in both
#: places. 2.38 mm is the floor; 2.5 mm leaves 2.31 mm in the smallest box.
#: The lip goes twice as deep as the door so the two back caps do not land on
#: each other either.
PROBE_TOL = 0.002
PROBE_CUSHION = 1.1
#: The genome's smallest depth (`genome/species/mailbox.json`, pinned by
#: tests/test_coincident_faces.py).
DEPTH_MIN = 0.49
BURY_FLOOR = PROBE_TOL * PROBE_CUSHION * (DEPTH_MIN + LIP_PROUD) / DEPTH_MIN
BACK_BURY = 0.0025


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

    # the pull-down door and its lip, on the -y face. Each keeps the front
    # plane it always had and runs BACK_BURY (the lip, twice that) through
    # the body's face, so no two of the three back planes coincide.
    door_t = DOOR_PROUD + BACK_BURY
    lip_t = LIP_PROUD + 2.0 * BACK_BURY
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, -d / 2.0 - DOOR_PROUD + door_t / 2.0,
                          z0 + LEG_H + body_h * 0.62),
                     (w * 0.72, door_t, body_h * 0.42))
    geometry.add_box(bm, (0.0, -d / 2.0 - LIP_PROUD + lip_t / 2.0,
                          z0 + LEG_H + body_h * 0.84),
                     (w * 0.76, lip_t, LIP))
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
