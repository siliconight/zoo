"""pallet_stack recipe: pallets with a wrapped load.

Roadmap 153, the forecourt. The walker's Call of Duty frames: stacked
sacks and pallets against a fence, a metre high, doing the work of cover
without being a hero asset. Two pallets with their deck boards, a load
above them, and a strap band round the load.

Collision is the whole stack -- it is knee-to-waist cover. Centre pivot;
extents exactly (w, d, h).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

DECK = 0.025
PALLET_H = 0.14
BOARDS = 4


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0
    wood, load, strap = [], [], []

    def part(bm, name, into, texel=1.2):
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel,
                                    texel=texel, rng=rng, wear=wear)
        objs.append(obj)
        into.append(obj)
        return obj

    bm = geometry.new_bm()
    for i in range(2):
        base = z0 + i * PALLET_H
        for k in range(BOARDS):
            y = -d / 2.0 + d * (k + 0.5) / BOARDS
            geometry.add_box(bm, (0.0, y, base + PALLET_H - DECK / 2.0),
                             (w, d / (BOARDS * 1.7), DECK))
        for sx in (-1, 0, 1):
            geometry.add_box(bm, (sx * (w / 2.0 - 0.06), 0.0,
                                  base + (PALLET_H - DECK) / 2.0),
                             (0.09, d, PALLET_H - DECK))
    part(bm, "PalletStack_Pallets", wood)

    load_h = h - 2 * PALLET_H
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + 2 * PALLET_H + load_h / 2.0),
                     (w * 0.94, d * 0.94, load_h))
    part(bm, "PalletStack_Load", load, texel=0.9)

    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + 2 * PALLET_H + load_h * 0.55),
                     (w * 0.97, d * 0.97, 0.05))
    part(bm, "PalletStack_Strap", strap, texel=2.0)

    cboxes.append(((-w / 2.0, -d / 2.0, z0), (w / 2.0, d / 2.0, h / 2.0)))
    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)

    timber = materials.make_material(
        f"M_PalletStack_{plan['material']}", plan["color"], plan["material"])
    sacks = materials.make_material("M_PalletStack_canvas", [0.62, 0.58, 0.46],
                                    "canvas")
    band = materials.make_material("M_PalletStack_plastic", [0.26, 0.26, 0.28],
                                   "plastic")
    materials.assign(wood, timber)
    materials.assign(load, sacks)
    materials.assign(strap, band)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
