"""bench recipe: a slatted seat on two cast ends, no back.

Roadmap 153, the waiting places. A street bench: three slats along its
length on two solid end frames, seat at the plan's height. Lot stands one
inside the bus shelter; the slot is the bench's own footprint, and the
whole thing collides -- a body sits on it or walks round it, never
through it. Centre pivot; extents exactly (w, d, h).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

END_T = 0.06         # a cast end frame's thickness along the bench
SLAT_T = 0.04
SLATS = 3


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0
    ends, slats = [], []

    def part(bm, name, into):
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel,
                                    texel=1.2, rng=rng, wear=wear)
        objs.append(obj)
        into.append(obj)
        return obj

    # two end frames, grade to the seat's underside
    leg_h = h - SLAT_T
    for tag, sx in (("L", -1), ("R", 1)):
        x = sx * (w / 2.0 - END_T / 2.0)
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, 0.0, z0 + leg_h / 2.0), (END_T, d, leg_h))
        part(bm, f"Bench_End_{tag}", ends)

    # slats along the length, the seat's top at +h/2
    gap = d * 0.06
    slat_d = (d - gap * (SLATS - 1)) / SLATS
    for i in range(SLATS):
        y = -d / 2.0 + slat_d / 2.0 + i * (slat_d + gap)
        bm = geometry.new_bm()
        geometry.add_box(bm, (0.0, y, h / 2.0 - SLAT_T / 2.0), (w, slat_d, SLAT_T))
        part(bm, f"Bench_Slat_{i + 1}", slats)

    # collision: the bench as one block
    cboxes.append(((-w / 2.0, -d / 2.0, z0), (w / 2.0, d / 2.0, h / 2.0)))

    seat = materials.make_material(
        f"M_Bench_{plan['material']}", plan["color"], plan["material"])
    iron = materials.make_material("M_Bench_metal_painted", [0.16, 0.17, 0.18],
                                   "metal_painted")
    materials.assign(slats, seat)
    materials.assign(ends, iron)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_seat_center": (0.0, 0.0, h / 2.0)}}
