"""Chair row layout: every box `recipes/chair.py` builds, without Blender.

Recipe frame: base-up (z 0 .. h), centred in x and y, the back at +y and the
sitter facing -y. `build.build_module` re-centres on the visual bounds, so the
extents here are exactly (w, d, h) -- the seat reaches both y faces and the
outer bays reach both x faces -- and an inset that shrank those extents would
be halved by the re-centre and moved onto the front.

WHY THE BACK STANDS OFF THE BOUNDING BOX. Cold run 9052, `bank_branch_a02`
lobby, three 2.4 m rows against exterior walls: "z fighting on the [chairs]
on the steel" (the walker). Measured by reassembling the walk copy's
`site.tscn` in Blender and running tools/coplanar_probe.py across the placed
nodes: every row's four back panels lay SAME-facing, gap 0.00 mm, on the wall
module's inner face -- 1.04 m2 per row. Deli Counter 0.127.0's `_wall_slots`
puts a piece's back 0.12 m from the wall centreline and the wall is 0.30 m
thick, so the module's back plane stands 0.03 m inside the wall; this recipe's
back panel was 0.03 m thick and flush with that plane, so its front face was
the wall's face. The burial is Deli Counter's defect. What is Zoo's is a
large visible face at a round depth behind the plane every wall-slotted
module is placed by: the panel now stands `BACK_INSET` in front of it, which
clears both the flush placement a corrected slot would give and the 0.03 m
one shipped today.

THE PROBE'S OTHER 26 ROWS were OPP contacts inside the module (a seat's end
against its neighbour's, a back on a seat, a leg under a seat). Interior
contacts cannot be seen and were not what the walker reported. They are gone
anyway: bays stand `BAY_GAP` apart, so a row reads as four chairs rather than
one plank with seams, and legs and backs run `SEAT_BURY` into the seat.
"""
from __future__ import annotations

from ._bays import bays

SEAT_T = 0.04
LEG_S = 0.035
SEAT_H = 0.45
BACK_T = 0.03
#: How far the back panel's rear face stands in front of the module's back
#: plane. tools/coplanar_probe.py reports coincidence within 2 mm; this is
#: simple_car's TRIM_PROUD, the same depth-buffer argument.
BACK_INSET = 0.006
#: Clear space between neighbouring chairs in a row (seat and back).
BAY_GAP = 0.012
#: Legs, arm posts and the back run this far into the seat, so their end
#: faces sit inside it rather than on its surface.
SEAT_BURY = 0.005
#: The back is this much narrower than its seat at each end. Buried in the
#: seat at the full seat width, its end faces would share the seat's end
#: planes over the buried strip.
BACK_SIDE_INSET = 0.004
LEG_INSET = 0.03
ARM_T = 0.03
ARM_POST = 0.024


def seat_height(h: float) -> float:
    """The chair's own 0.45, or the authored height less a hand."""
    return min(SEAT_H, max(0.25, h - 0.12))


def layout(w: float, d: float, h: float, bay_max: float, legs: int = 4,
           has_arms: bool = False) -> dict:
    """``{"seat_h", "parts": [(name, [(centre, size), ...])], "collision"}``.

    Each part is one object of one or more axis-aligned boxes; ``centre`` and
    ``size`` are (x, y, z) in metres, recipe frame.
    """
    seat_h = seat_height(h)
    runs = bays(w, bay_max)
    n = len(runs)
    parts = []
    for bi, (bx, bw) in enumerate(runs):
        tag = "" if n == 1 else f"_B{bi + 1}"
        x0 = bx - bw / 2.0 + (BAY_GAP / 2.0 if bi > 0 else 0.0)
        x1 = bx + bw / 2.0 - (BAY_GAP / 2.0 if bi < n - 1 else 0.0)
        cx, cw = (x0 + x1) / 2.0, x1 - x0
        parts.append((f"Chair_Seat{tag}", [
            ((cx, 0.0, seat_h - SEAT_T / 2.0), (cw, d, SEAT_T))]))
        back_z0 = seat_h - SEAT_BURY
        back_y = d / 2.0 - BACK_INSET - BACK_T / 2.0
        parts.append((f"Chair_Back{tag}", [
            ((cx, back_y, (back_z0 + h) / 2.0),
             (cw - 2.0 * BACK_SIDE_INSET, BACK_T, h - back_z0))]))
        leg_top = seat_h - SEAT_T + SEAT_BURY
        corners = [(-1, -1), (1, -1), (-1, 1), (1, 1)][:legs]
        for i, (sx, sy) in enumerate(corners, start=1):
            lx = cx + sx * (cw / 2.0 - LEG_INSET - LEG_S / 2.0)
            ly = sy * (d / 2.0 - LEG_INSET - LEG_S / 2.0)
            parts.append((f"Chair_Leg_{i}{tag}", [
                ((lx, ly, leg_top / 2.0), (LEG_S, LEG_S, leg_top))]))
        if has_arms:
            arm_h = seat_h + 0.22
            for side, sx in (("L", -1), ("R", 1)):
                ax = cx + sx * (cw / 2.0 - ARM_T / 2.0)
                post_z0 = seat_h - SEAT_BURY
                post_z1 = arm_h                    # inside the rail, not on it
                parts.append((f"Chair_Arm_{side}{tag}", [
                    ((ax, 0.0, arm_h), (ARM_T, d * 0.8, ARM_T)),
                    ((ax, -d * 0.32, (post_z0 + post_z1) / 2.0),
                     (ARM_POST, ARM_POST, post_z1 - post_z0)),
                ]))
    # collision: the row as one block below the seat, and the back panel
    collision = [((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, seat_h)),
                 ((-w / 2.0, d / 2.0 - BACK_INSET - BACK_T, seat_h),
                  (w / 2.0, d / 2.0, h))]
    return {"seat_h": seat_h, "parts": parts, "collision": collision}
