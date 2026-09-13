"""newspaper_box recipe: a coin-operated news rack.

Roadmap 153, the 1990s American street -- the decade's own object. A
steel rack about 0.4 m wide on a pedestal foot: a hopper body, a sloped
window at the top where the front page shows, a coin slot and a handle.
Racks stand in twos and threes outside a store, which is `site_furniture`'s
business; this is one of them. Unbranded: the window is where a paper's
masthead would be, and nothing is reproduced on it.

Collision is the whole rack. Centre pivot; extents exactly (w, d, h).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

FOOT_H = 0.06
PEDESTAL = 0.55       # of the width


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0
    shell, glass, trim = [], [], []

    def part(bm, name, into, texel=1.3):
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel,
                                    texel=texel, rng=rng, wear=wear)
        objs.append(obj)
        into.append(obj)
        return obj

    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + FOOT_H / 2.0), (w * 0.9, d * 0.9, FOOT_H))
    ped_h = h * 0.34
    geometry.add_box(bm, (0.0, 0.0, z0 + FOOT_H + ped_h / 2.0),
                     (w * PEDESTAL, d * PEDESTAL, ped_h))
    part(bm, "NewspaperBox_Pedestal", trim)

    # the hopper: the body from the pedestal up, its front face leaning back
    body_h = h - FOOT_H - ped_h
    bm = geometry.new_bm()
    verts = geometry.add_box(bm, (0.0, 0.0, z0 + FOOT_H + ped_h + body_h / 2.0),
                             (w, d, body_h))
    geometry.taper_z(verts, 0.92, 1.0)
    part(bm, "NewspaperBox_Body", shell)

    # the window the front page shows through, and the handle over it
    win_z = z0 + FOOT_H + ped_h + body_h * 0.62
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, -d / 2.0 - 0.008, win_z),
                     (w * 0.74, 0.02, body_h * 0.46))
    part(bm, "NewspaperBox_Window", glass, texel=1.0)
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, -d / 2.0 - 0.03, win_z + body_h * 0.30),
                     (w * 0.62, 0.05, 0.035))
    geometry.add_box(bm, (w * 0.30, -d / 2.0 - 0.02, win_z - body_h * 0.28),
                     (0.05, 0.03, 0.08))                      # the coin slot
    part(bm, "NewspaperBox_Handle", trim, texel=1.8)

    cboxes.append(((-w / 2.0, -d / 2.0, z0), (w / 2.0, d / 2.0, h / 2.0)))

    paint = materials.make_material(
        f"M_NewspaperBox_{plan['material']}", plan["color"], plan["material"])
    pane = materials.make_material("M_NewspaperBox_glass", [0.72, 0.78, 0.8],
                                   "glass")
    dark = materials.make_material("M_NewspaperBox_trim", [0.16, 0.16, 0.17],
                                   "metal_bare")
    materials.assign(shell, paint)
    materials.assign(glass, pane)
    materials.assign(trim, dark)
    # the slot is exact; the detail is not (geometry.fit_to)
    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
