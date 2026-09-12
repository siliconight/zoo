"""Chair recipe: seat slab, back panel, post legs, optional arms.

BAYS (roadmap 44). Deli Counter's `waiting_seats` (5.0 x 2.0 x 0.6),
`bench_row` (2.8 x 1.0 x 0.9) and `booth_seating` (2.0 x 1.2 x 1.1) are
ROWS of seating; a chair is 0.4-0.6 m wide. `_bays.bays` divides the width
into seats of at most `bay_max` (genome params), each with its own seat,
back, legs and arms -- a row of joined chairs, which is what a waiting
room has. The seat height is the smaller of the chair's own 0.45 and the
authored height less a hand, so a 0.6 m bench is a bench and not a stool
with a two-centimetre back. One bay is the chair this recipe always built.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ._bays import bay_max_of, bays

SEAT_T = 0.04
LEG_S = 0.035
SEAT_H = 0.45


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, rng=rng, wear=wear))

    seat_h = min(SEAT_H, max(0.25, h - 0.12))
    n_legs = plan["params"]["legs"]
    runs = bays(w, bay_max_of(plan))
    for bi, (bx, bw) in enumerate(runs):
        tag = "" if len(runs) == 1 else f"_B{bi + 1}"
        bm = geometry.new_bm()
        geometry.add_box(bm, (bx, 0, seat_h - SEAT_T / 2), (bw, d, SEAT_T))
        part(bm, f"Chair_Seat{tag}")
        back_h = h - seat_h
        bm = geometry.new_bm()
        geometry.add_box(bm, (bx, d / 2 - 0.015, seat_h + back_h / 2),
                         (bw, 0.03, back_h))
        part(bm, f"Chair_Back{tag}")
        inset = 0.03
        corners = [(-1, -1), (1, -1), (-1, 1), (1, 1)][:n_legs]
        for i, (sx, sy) in enumerate(corners, start=1):
            x = bx + sx * (bw / 2 - inset - LEG_S / 2)
            y = sy * (d / 2 - inset - LEG_S / 2)
            bm = geometry.new_bm()
            geometry.add_box(bm, (x, y, (seat_h - SEAT_T) / 2),
                             (LEG_S, LEG_S, seat_h - SEAT_T))
            part(bm, f"Chair_Leg_{i}{tag}")
        if plan["params"].get("has_arms"):
            arm_h = seat_h + 0.22
            for side, sx in (("L", -1), ("R", 1)):
                x = bx + sx * (bw / 2 - 0.015)
                bm = geometry.new_bm()
                geometry.add_box(bm, (x, 0, arm_h), (0.03, d * 0.8, 0.03))
                geometry.add_box(bm, (x, -d * 0.32, (arm_h + seat_h) / 2),
                                 (0.03, 0.03, arm_h - seat_h))
                part(bm, f"Chair_Arm_{side}{tag}")
    # collision: the row as one block below the seat, and the back panel
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, seat_h)))
    cboxes.append(((-w / 2, d / 2 - 0.03, seat_h), (w / 2, d / 2, h)))
    mat = materials.make_material(
        f"M_Chair_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_seat_center": (0, 0, seat_h)}}
