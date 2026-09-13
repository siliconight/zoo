"""payphone recipe: a half-booth on a pedestal.

Roadmap 153, the 1990s American street, and the object that dates it
hardest. Not the full glass booth -- by the nineties a Delco sidewalk
carried the open half-hood: a back panel on a post, a shallow hood over
it, and the instrument with a handset on a hook and a coin box under it.

The hood's underside is where a light would go if a level ever lit one;
`ATT_hood` is there for it. Collision is the pedestal and the instrument
as one column against the back panel, so a body cannot stand inside the
hood. Centre pivot; extents exactly (w, d, h).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

POST_D = 0.08
HOOD_T = 0.05


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0
    shell, instrument, dark = [], [], []

    def part(bm, name, into, texel=1.3):
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel,
                                    texel=texel, rng=rng, wear=wear)
        objs.append(obj)
        into.append(obj)
        return obj

    back_y = d / 2.0 - 0.03
    # post and back panel
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, back_y, z0 + h * 0.22), (POST_D, POST_D, h * 0.44))
    geometry.add_box(bm, (0.0, back_y, z0 + h * 0.70), (w, 0.05, h * 0.56))
    part(bm, "Payphone_Back", shell)

    # the hood over it
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, d * 0.06, h / 2.0 - HOOD_T / 2.0),
                     (w, d * 0.88, HOOD_T))
    part(bm, "Payphone_Hood", shell)

    # the instrument: a face plate, the coin box below it, the handset on a
    # hook to one side
    face_z = z0 + h * 0.66
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, back_y - 0.09, face_z), (w * 0.62, 0.14, h * 0.26))
    geometry.add_box(bm, (0.0, back_y - 0.08, face_z - h * 0.24),
                     (w * 0.34, 0.12, h * 0.2))
    part(bm, "Payphone_Instrument", instrument)
    bm = geometry.new_bm()
    geometry.add_box(bm, (-w * 0.26, back_y - 0.12, face_z + h * 0.02),
                     (0.07, 0.07, h * 0.17))
    geometry.add_box(bm, (0.0, back_y - 0.155, face_z + h * 0.09),
                     (w * 0.3, 0.05, 0.035))                  # the cradle
    part(bm, "Payphone_Handset", dark, texel=1.8)

    cboxes.append(((-w / 2.0, back_y - 0.16, z0), (w / 2.0, d / 2.0, h * 0.42)))

    paint = materials.make_material(
        f"M_Payphone_{plan['material']}", plan["color"], plan["material"])
    steel = materials.make_material("M_Payphone_metal_bare", [0.42, 0.43, 0.45],
                                    "metal_bare")
    black = materials.make_material("M_Payphone_plastic", [0.09, 0.09, 0.1],
                                    "plastic")
    materials.assign(shell, paint)
    materials.assign(instrument, steel)
    materials.assign(dark, black)
    # the slot is exact; the detail is not (geometry.fit_to)
    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_hood": (0.0, 0.0, h / 2.0 - HOOD_T)}}
