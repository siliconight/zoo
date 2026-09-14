"""carton_stack, planned in pure Python: cardboard cartons and banker's boxes
stacked in columns, the way a basement or a stockroom floor holds them.

"Just a bunch of chairs and tables with nothing on it" (the walker, in a
country_club_a01 basement on cold run 9052). A storage floor reads as one
because of what is stacked on it, and a stack is the cheap cluster
SET_DRESSING_REFERENCES asks for: one simple shape repeated with variation,
the grouping doing the work.

THE SHAPE. Columns along x; a column is one footprint, or two (front and
back) when the slot is 0.8 m deep or more; each footprint is a stack. A box
is a kraft carton (a tape strip over its top and down both ends, sometimes a
label on its front) or a banker's box (a lid LID_LIP wider than its body, a
dark hand hole in each end). Upper cartons are turned a degree or three by a
seeded rule and set in from the box below -- nothing here is aligned by
nature.

THE RULES, the ones `recipes/_shelf_stock.py` keeps:

  * EXACT EXTENTS. Every footprint's base box fills its footprint, the
    footprints tile the slot with GAP between, and one column is exactly h.
    The details that stand proud past that (tape, labels) are taken back
    out by `prims.fit_exact`, a scale within a percent of 1.
  * NOTHING SHARES A PLANE. Neighbouring footprints keep GAP apart, and
    every box with what stands proud of it stays inside its own footprint.
    A box rests SINK below the top of what it stands on and is turned at
    least MIN_TURN from it, so no side of it is parallel to a side of the
    box below. Details stand DETAIL proud. `tests/test_interior_species.py` runs the coincident-face
    measurement over 40 seeds and several sizes.
  * DETERMINISTIC from the rng passed in.

Frame: metres, Z up, base-up (the kit re-centres), -Y the front. Colours for
kraft and banker come from `_shelf_stock.PALETTE`.
"""
from __future__ import annotations

import math

from . import prims as P
from ..recipes import _shelf_stock

#: Between neighbouring footprints. 0.006 first: tape and labels stand
#: DETAIL proud on both sides of a gap, so across a 6 mm gap two tapes met
#: back to back at 0.0 mm (30 of 240 seeded stacks). Twice DETAIL plus the
#: probe's 2 mm tolerance plus a millimetre is what it has to be.
GAP = 2 * 0.003 + 0.002 + 0.004
SINK = 0.003         # a box's bottom inside the box below it
DETAIL = 0.003       # tape, label and hand holes stand this proud
LID_LIP = 0.006      # a banker's lid overhangs its body on every side
LID_H = 0.05
#: A lid's top stands this far above its body's top. 0.004 first: the box
#: stacked on it sinks SINK into the lid, so its bottom face stood 1 mm from
#: the lower body's top face, back to back (the pure probe's OPP row).
LID_RISE = 0.006
#: A banker's box body is 0.31 x 0.39 x 0.26; a footprint takes one only
#: when each side (less the lid lip) is within this range, so a stretched
#: "banker" never reads as a crate.
BANKER_SIDE = (0.29, 0.64)
BANKER_H = 0.26
TAPE_W = 0.05
MIN_CARTON = 0.12
LABEL_EDGE = 0.02
MAX_YAW = math.radians(3.0)
MIN_TURN = math.radians(1.0)

#: material key -> (linear RGB, kind)
MATERIALS = {
    "kraft": tuple(_shelf_stock.PALETTE["kraft"]),
    "banker": tuple(_shelf_stock.PALETTE["banker"]),
    # packing tape a shade lighter than the kraft it is on
    "tape": ([0.46, 0.34, 0.18], "plastic"),
    # a paper shipping label, and the dark inside of a box through a hand hole
    "label": ([0.80, 0.78, 0.70], "paper"),
    "hole": ([0.035, 0.03, 0.025], "paper"),
}


def _yaw_box(part, mat, cx, cy, sx, sy, z0, z1, yaw, bevel=False):
    b = P.box(part, mat, (cx - sx / 2, cy - sy / 2, z0),
              (cx + sx / 2, cy + sy / 2, z1), bevel)
    return P.rotate_z(b, yaw, (cx, cy)) if yaw else b


def _carton(out, cx, cy, sx, sy, z0, hgt, yaw, label_at=None):
    """A kraft carton from z0 to z0 + hgt. Returns its top (the body's; the
    tape stands DETAIL above it)."""
    z1 = z0 + hgt
    out.append(_yaw_box("Carton_Body", "kraft", cx, cy, sx, sy, z0, z1, yaw))
    tw = min(TAPE_W, 0.3 * min(sx, sy))
    if sx >= sy:
        tsx, tsy = sx + 2 * DETAIL, tw
    else:
        tsx, tsy = tw, sy + 2 * DETAIL
    out.append(_yaw_box("Carton_Tape", "tape", cx, cy, tsx, tsy,
                        z1 - min(0.03, hgt * 0.3), z1 + DETAIL, yaw))
    if label_at is not None and hgt >= 0.15:
        fx, fz = label_at
        lw, lh = min(0.16, sx * 0.45), min(0.09, hgt * 0.3)
        # kept LABEL_EDGE in from the carton's sides: flush with one, the
        # label's end face lay 1.9 mm from the side face it stands proud of
        lx = cx + fx * max(0.0, sx - lw - 2 * LABEL_EDGE) / 2.0
        lz = z0 + hgt * fz
        lab = P.box("Carton_Label", "label",
                    (lx - lw / 2, cy - sy / 2 - DETAIL, lz - lh / 2),
                    (lx + lw / 2, cy - sy / 2 + DETAIL, lz + lh / 2))
        out.append(P.rotate_z(lab, yaw, (cx, cy)) if yaw else lab)
    return z1


def _banker(out, cx, cy, sx, sy, z0, hgt, yaw):
    """A banker's box whose LID is sx by sy and whose lid top is z0 + hgt.
    Returns the lid top."""
    bx, by = sx - 2 * LID_LIP, sy - 2 * LID_LIP
    z_top = z0 + hgt
    z_body = z_top - LID_RISE
    out.append(_yaw_box("Banker_Body", "banker", cx, cy, bx, by, z0, z_body, yaw))
    out.append(_yaw_box("Banker_Lid", "banker", cx, cy, sx, sy,
                        z_body - LID_H + LID_RISE, z_top, yaw))
    hz = z_body - LID_H - 0.035
    if hz - 0.016 > z0 + 0.02:
        ends = ((0, -1), (0, 1)) if bx <= by else ((-1, 0), (1, 0))
        for ex, ey in ends:
            if ey:
                lo = (cx - 0.045, cy + ey * by / 2 - DETAIL, hz - 0.016)
                hi = (cx + 0.045, cy + ey * by / 2 + DETAIL, hz + 0.016)
            else:
                lo = (cx + ex * bx / 2 - DETAIL, cy - 0.045, hz - 0.016)
                hi = (cx + ex * bx / 2 + DETAIL, cy + 0.045, hz + 0.016)
            hb = P.box("Banker_Hole", "hole", lo, hi)
            out.append(P.rotate_z(hb, yaw, (cx, cy)) if yaw else hb)
    return z_top


def _split(rng, total, lo, hi, gap):
    """Widths filling ``total`` exactly with ``gap`` between, each within
    [lo, hi] where ``total`` allows it."""
    if total <= hi:
        return [total]
    out = []
    left = total
    while left > hi:
        wdt = rng.uniform(lo, hi)
        if left - wdt - gap < lo:
            wdt = (left - gap) / 2.0
            return out + [wdt, left - gap - wdt]
        out.append(wdt)
        left -= wdt + gap
    return out + [left]


def _heights(rng, top, lo, hi, sink_each=SINK, max_n=99):
    """Box heights for a stack whose top is exactly ``top`` when each box
    above the first sinks ``sink_each`` into the one below; at most
    ``max_n`` boxes, however tall that makes each."""
    n = max(1, min(max_n, int(round(top / rng.uniform(lo, hi)))))
    while n > 1 and top / n < lo * 0.7:
        n -= 1
    raw = [rng.uniform(0.8, 1.2) for _ in range(n)]
    usable = top + sink_each * (n - 1)
    s = sum(raw)
    return [usable * r / s for r in raw]


def _upper_pose(rng, band, lower_yaw, min_set_in, max_set_in, inflate):
    """Size, centre and yaw for a box stacked above the base of a footprint.

    ``band`` is the footprint ``(cx, cy, sx, sy)``. The box is set in from
    the band by ``min_set_in``..``max_set_in`` a side and turned by at least
    MIN_TURN (either way) and at most MAX_YAW from the box below, and its
    footprint grown by ``inflate`` (what stands proud of it) stays inside
    the band.

    WHY A MINIMUM TURN. A stacked box sinks SINK into the one below, so the
    two boxes' side faces share a 3 mm band of height. Turned alike, a side
    of each could lie within the coincident-face tolerance there; turned a
    degree apart, no two of them are parallel at all.
    """
    cx, cy, sx, sy = band
    for _try in range(24):
        nsx = sx - 2 * rng.uniform(min_set_in, max_set_in)
        nsy = sy - 2 * rng.uniform(min_set_in, max_set_in)
        turn = rng.uniform(MIN_TURN, MAX_YAW) * rng.choice((-1.0, 1.0))
        nyaw = lower_yaw + turn
        if abs(nyaw) > MAX_YAW:
            nyaw = lower_yaw - turn
        room_x = max(0.0, (sx - nsx) / 2 - inflate)
        room_y = max(0.0, (sy - nsy) / 2 - inflate)
        ncx = cx + rng.uniform(-0.6, 0.6) * room_x
        ncy = cy + rng.uniform(-0.6, 0.6) * room_y
        poly = P.rect_poly(ncx, ncy, nsx + 2 * inflate, nsy + 2 * inflate, nyaw)
        if P.poly_inside_rect(poly, cx - sx / 2, cx + sx / 2,
                              cy - sy / 2, cy + sy / 2):
            return nsx, nsy, ncx, ncy, nyaw
    return None


def _carton_stack(out, rng, cx, cy, sx, sy, top):
    """Kraft cartons on a footprint: the base box fills it, each box above
    is a little smaller than the footprint, set somewhere on it and turned.
    Returns the top of the stack (exactly ``top`` unless the footprint is
    too small to stack on, when one box takes the whole height)."""
    band = (cx, cy, sx, sy)
    heights = _heights(rng, top, 0.2, 0.42)
    poses = [(sx, sy, cx, cy, 0.0)]
    for _k in heights[1:]:
        got = _upper_pose(rng, band, poses[-1][4], 0.012, 0.05, DETAIL + 0.001)
        if got is None or min(got[0], got[1]) < MIN_CARTON:
            break
        poses.append(got)
    if len(poses) < len(heights):
        heights = _heights(rng, top, 0.2, 0.42, max_n=len(poses))
    z = 0.0
    for k, (hgt, (bsx, bsy, bcx, bcy, yaw)) in enumerate(zip(heights, poses)):
        if k:
            z -= SINK
        label = ((rng.uniform(-1, 1), rng.uniform(0.35, 0.65))
                 if rng.random() < 0.35 else None)
        z = _carton(out, bcx, bcy, bsx, bsy, z, hgt, yaw, label)
    return z


def _banker_stack(out, rng, cx, cy, sx, sy, top):
    """Banker's boxes on a footprint: the base lid is the footprint's size,
    so it reaches the footprint's edges; each box above is a lid 1-3 cm
    smaller, set somewhere on the one below and turned a degree or two.

    REFUTED FIRST: every lid the footprint's full size, turned up to a
    degree. A degree on a 0.6 m lid swings its corner 5 mm past the
    footprint, into the GAP the neighbour keeps -- measured as a lid-to-lid
    pair 0.6 mm apart on a 1.6 x 1.2 x 1.8 stack, seed 0. Then all of them
    unturned, which the render showed as a filing cabinet, not a stack.
    """
    band = (cx, cy, sx, sy)
    heights = _heights(rng, top, BANKER_H * 0.85, BANKER_H * 1.15)
    poses = [(sx, sy, cx, cy, 0.0)]
    for _k in heights[1:]:
        got = _upper_pose(rng, band, poses[-1][4], 0.008, 0.02, 0.001)
        if got is None:
            break
        poses.append(got)
    if len(poses) < len(heights):
        heights = _heights(rng, top, BANKER_H * 0.85, 9.0, max_n=len(poses))
    z = 0.0
    for k, (hgt, (bsx, bsy, bcx, bcy, yaw)) in enumerate(zip(heights, poses)):
        if k:
            z -= SINK
        z = _banker(out, bcx, bcy, bsx, bsy, z, hgt, yaw)
    return z


def plan(w, d, h, rng, style="auto"):
    """Primitives and collision boxes for a carton stack of exactly w x d x h.

    ``style``: ``mixed``, ``kraft`` or ``banker`` (``auto`` draws one).
    Returns ``{"prims", "collision", "style"}``; collision is one box per
    footprint, to that footprint's top.
    """
    if style in (None, "", "auto"):
        style = rng.choice(("mixed", "mixed", "kraft", "banker"))
    prims, cboxes = [], []
    rows = 2 if d >= 0.8 else 1
    row_d = (d - GAP * (rows - 1)) / rows
    widths = _split(rng, w, 0.34, 0.62, GAP)
    tall = (rng.randrange(len(widths)), rng.randrange(rows))
    x = -w / 2.0
    for ci, cw in enumerate(widths):
        cx = x + cw / 2.0
        for ri in range(rows):
            y0 = -d / 2.0 + ri * (row_d + GAP)
            cy = y0 + row_d / 2.0
            if (ci, ri) == tall:
                top = h
            else:
                top = min(h - 0.02, max(min(h, 0.2), h * rng.uniform(0.4, 0.98)))
            fits_banker = (BANKER_SIDE[0] <= cw - 2 * LID_LIP <= BANKER_SIDE[1]
                           and BANKER_SIDE[0] <= row_d - 2 * LID_LIP <= BANKER_SIDE[1]
                           and top >= BANKER_H * 0.85)
            banker = fits_banker and (style == "banker" or
                                      (style == "mixed" and rng.random() < 0.45))
            if banker:
                got = _banker_stack(prims, rng, cx, cy, cw, row_d, top)
            else:
                got = _carton_stack(prims, rng, cx, cy, cw, row_d, top)
            cboxes.append(((x, y0, 0.0), (x + cw, y0 + row_d, got)))
        x += cw + GAP
    raw_lo, raw_hi = P.bounds(prims)
    overshoot = max(max(abs(raw_lo[0] + w / 2), abs(raw_hi[0] - w / 2)),
                    max(abs(raw_lo[1] + d / 2), abs(raw_hi[1] - d / 2)),
                    abs(raw_lo[2]), abs(raw_hi[2] - h))
    prims, cboxes = P.fit_exact(prims, (-w / 2, -d / 2, 0.0), (w / 2, d / 2, h),
                                cboxes)
    return {"prims": prims, "collision": cboxes, "style": style,
            # how far the plan missed the slot before fit_exact took it back
            "overshoot_m": overshoot}
