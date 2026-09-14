"""pool_table, planned in pure Python: a 1990s coin-op bar table.

The seven-foot box every Delco bar and a good few basements had: a heavy
cabinet on four corner posts, wood rails with inlaid sights, black pocket
castings at the corners and the middle of each long side, rubber cushions
with angled noses, the cloth, a coin slide and a ball-return window on one
end. The game left on it is what says somebody plays here: a few balls
where they stopped and, on most seeds, a cue lying across the cloth.

Frame: metres, Z up, base-up, the table's LENGTH along x (``w``), its width
along y (``d``), ``h`` the rail top. The pocket castings define the extents
in x, y and z; everything else stands inside them.

THE RULES the interior species keep: extents exactly w x d x h; parts that
meet overlap by a few mm rather than touching; nothing within 2 mm of
another face's plane where the two overlap (`prims.coincident_pairs` in
the tests, over sizes and seeds); deterministic from the rng passed in.
"""
from __future__ import annotations

import math

from . import prims as P

SINK = 0.003
DETAIL = 0.003
RAIL_T = 0.10          # rail depth below its top
CAP_T = 0.11           # a pocket casting's depth below the table's top
CAP_RISE = 0.003       # castings stand this far above the rails
CUSHION_W = 0.045
CUSHION_DROP = 0.018   # cushion top below the rail top
#: cloth below the rail top. 0.045 first, and a ball (57 mm) stood 8 mm over
#: the castings, so `fit_exact` shrank the whole table 1 % in z to take it back
CLOTH_DROP = 0.06
BED_T = 0.095
BALL_R = 0.028

#: material key -> (linear RGB, kind). "rail" and "cabinet" are the genome's
#: wood; "cloth" is chosen per seed from CLOTHS.
MATERIALS = {
    "cap": ([0.035, 0.035, 0.035], "plastic"),
    "cushion_rubber": ([0.03, 0.03, 0.03], "rubber"),
    "pocket": ([0.012, 0.012, 0.012], "leather"),
    "sight": ([0.78, 0.76, 0.66], "plastic"),
    "steel": ([0.55, 0.56, 0.58], "metal_bare"),
    "slot": ([0.02, 0.02, 0.02], "plastic"),
    "cue_shaft": ([0.62, 0.48, 0.30], "wood"),
    "cue_butt": ([0.10, 0.04, 0.03], "wood"),
}
#: bar green, tournament blue, burgundy: the three cloths a 1997 bar table
#: came in
CLOTHS = ([0.035, 0.24, 0.09], [0.04, 0.10, 0.30], [0.26, 0.04, 0.06])
BALLS = {"ball_cue": [0.80, 0.78, 0.70], "ball_1": [0.75, 0.55, 0.04],
         "ball_2": [0.04, 0.10, 0.45], "ball_3": [0.60, 0.05, 0.04],
         "ball_4": [0.22, 0.05, 0.30], "ball_5": [0.75, 0.25, 0.03],
         "ball_6": [0.03, 0.30, 0.10], "ball_7": [0.30, 0.06, 0.04],
         "ball_8": [0.02, 0.02, 0.02]}


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def plan(w, d, h, rng):
    """``{"prims", "collision", "cloth", "overshoot_m"}``."""
    prims = []
    rail_w = _clamp(0.085 * d, 0.10, 0.14)
    pc = rail_w + 0.03                    # corner casting, square
    sc = 0.16                             # side casting's length along x
    top = h
    cap_z0 = top - CAP_T
    rail_top = top - CAP_RISE
    rail_z0 = top - RAIL_T
    cloth_z = top - CLOTH_DROP
    hx, hy = w / 2.0, d / 2.0

    # pocket castings: four corners and the middle of each long side
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = sorted((sx * hx, sx * (hx - pc)))
            y0, y1 = sorted((sy * hy, sy * (hy - pc)))
            prims.append(P.box("PoolTable_Casting", "cap", (x0, y0, cap_z0),
                               (x1, y1, top), bevel=True))
    for sy in (-1, 1):
        y0, y1 = sorted((sy * hy, sy * (hy - rail_w - 0.003)))
        prims.append(P.box("PoolTable_Casting", "cap", (-sc / 2, y0, cap_z0),
                           (sc / 2, y1, top), bevel=True))

    # rails: two segments on each long side, one on each end, reaching 5 mm
    # into the castings; 3 mm in from the extents so no face lies in a
    # casting's
    for sy in (-1, 1):
        y0, y1 = sorted((sy * (hy - 0.003), sy * (hy - rail_w)))
        for sx in (-1, 1):
            x0, x1 = sorted((sx * (sc / 2 - 0.005), sx * (hx - pc + 0.005)))
            prims.append(P.box("PoolTable_Rail", "rail", (x0, y0, rail_z0),
                               (x1, y1, rail_top), bevel=True))
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (hx - 0.003), sx * (hx - rail_w)))
        prims.append(P.box("PoolTable_Rail", "rail", (x0, -(hy - pc + 0.005), rail_z0),
                           (x1, hy - pc + 0.005, rail_top), bevel=True))

    # the bed, a centimetre under the rails all round; the cloth is its top
    bx, by = hx - rail_w + 0.01, hy - rail_w + 0.01
    prims.append(P.box("PoolTable_Bed", "cloth", (-bx, -by, cloth_z - BED_T),
                       (bx, by, cloth_z)))

    # cushions with angled noses at the pockets, 5 mm into the rail
    ci = CUSHION_W
    cz0, cz1 = cloth_z - SINK, rail_top - CUSHION_DROP
    nose = 0.035
    for sy in (-1, 1):
        yo = sy * (hy - rail_w + 0.005)
        yi = sy * (hy - rail_w - ci)
        for sx in (-1, 1):
            xa, xb = sorted((sx * (sc / 2 + 0.03), sx * (hx - pc - 0.02)))
            poly = [(xa, yo), (xb, yo), (xb - nose, yi), (xa + nose, yi)]
            if sy < 0:
                poly = [(xa + nose, yi), (xb - nose, yi), (xb, yo), (xa, yo)]
            prims.append(P.prism("PoolTable_Cushion", "cloth", poly, cz0, cz1))
    for sx in (-1, 1):
        xo = sx * (hx - rail_w + 0.005)
        xi = sx * (hx - rail_w - ci)
        ya, yb = -(hy - pc - 0.02), hy - pc - 0.02
        poly = [(xi, ya + nose), (xo, ya), (xo, yb), (xi, yb - nose)]
        if sx < 0:
            poly = [(xo, ya), (xi, ya + nose), (xi, yb - nose), (xo, yb)]
        prims.append(P.prism("PoolTable_Cushion", "cloth", poly, cz0, cz1))

    # pocket openings, dark discs DETAIL above the cloth
    for sx in (-1, 1):
        for sy in (-1, 1):
            prims.append(P.cyl("PoolTable_Pocket", "pocket",
                               (sx * (hx - rail_w - 0.004), sy * (hy - rail_w - 0.004)),
                               0.055, cloth_z - 0.02, cloth_z + DETAIL, segments=8))
    for sy in (-1, 1):
        prims.append(P.cyl("PoolTable_Pocket", "pocket", (0.0, sy * (hy - rail_w - 0.008)),
                           0.05, cloth_z - 0.02, cloth_z + DETAIL, segments=8))

    # sights inlaid in the rail tops, DETAIL proud
    rail_mid = hy - rail_w / 2.0
    seg_x0, seg_x1 = sc / 2, hx - pc
    for sy in (-1, 1):
        for sx in (-1, 1):
            for f in (1 / 3.0, 2 / 3.0):
                x = sx * (seg_x0 + (seg_x1 - seg_x0) * f)
                prims.append(P.box("PoolTable_Sight", "sight",
                                   (x - 0.012, sy * rail_mid - 0.006, rail_top - DETAIL),
                                   (x + 0.012, sy * rail_mid + 0.006, rail_top + DETAIL)))
    end_mid = hx - rail_w / 2.0
    for sx in (-1, 1):
        for f in (-1 / 3.0, 0.0, 1 / 3.0):
            y = (hy - pc) * f * 1.5
            prims.append(P.box("PoolTable_Sight", "sight",
                               (sx * end_mid - 0.006, y - 0.012, rail_top - DETAIL),
                               (sx * end_mid + 0.006, y + 0.012, rail_top + DETAIL)))

    # the cabinet, its top a centimetre into the bed; corner posts proud of
    # it to the floor
    cab_x, cab_y = hx - 0.05, hy - 0.05
    cab_top = cloth_z - BED_T + 0.01
    cab_z0 = 0.12
    prims.append(P.box("PoolTable_Cabinet", "cabinet", (-cab_x, -cab_y, cab_z0),
                       (cab_x, cab_y, cab_top), bevel=True))
    post = 0.13
    post_top = cloth_z - BED_T - 0.005
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = sorted((sx * (cab_x + 0.012), sx * (cab_x + 0.012 - post)))
            y0, y1 = sorted((sy * (cab_y + 0.012), sy * (cab_y + 0.012 - post)))
            prims.append(P.box("PoolTable_Post", "rail", (x0, y0, 0.0),
                               (x1, y1, post_top), bevel=True))

    # coin slide and ball return on the +x end
    face = cab_x
    prims.append(P.box("PoolTable_CoinPlate", "steel",
                       (face - DETAIL, -0.14, top - 0.40), (face + DETAIL, 0.14, top - 0.22)))
    prims.append(P.box("PoolTable_CoinSlide", "steel",
                       (face - 0.01, -0.10, top - 0.34), (face + 0.035, 0.10, top - 0.29)))
    prims.append(P.box("PoolTable_CoinSlot", "slot",
                       (face + 0.035 - 0.004, -0.02, top - 0.325),
                       (face + 0.035 + DETAIL, 0.02, top - 0.305)))
    prims.append(P.box("PoolTable_Return", "slot",
                       (face - DETAIL, -0.17, cab_z0 + 0.08), (face + DETAIL, 0.17, cab_z0 + 0.16)))

    # the game left on the cloth
    play_x = hx - rail_w - ci - BALL_R - 0.02
    play_y = hy - rail_w - ci - BALL_R - 0.02
    cue = None
    if rng.random() < 0.65 and 2 * play_x > 1.0:
        length = min(1.45, 2 * play_x * 0.92)
        yaw = rng.uniform(-0.35, 0.35) + (math.pi if rng.random() < 0.5 else 0.0)
        cx = rng.uniform(-0.1, 0.1) * play_x
        cy = rng.uniform(-0.5, 0.5) * play_y
        dx, dy = math.cos(yaw) * length / 2, math.sin(yaw) * length / 2
        # keep both ends on the cloth
        k = min(1.0, (play_x - abs(cx)) / max(1e-6, abs(dx)),
                (play_y - abs(cy)) / max(1e-6, abs(dy)))
        dx, dy = dx * k, dy * k
        rb, rt = 0.0145, 0.0065
        p0 = (cx - dx, cy - dy)
        p1 = (cx + dx, cy + dy)
        joint = 0.42
        pj = (p0[0] + (p1[0] - p0[0]) * joint, p0[1] + (p1[1] - p0[1]) * joint)
        rj = rb + (rt - rb) * joint
        ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        ux, uy = (p1[0] - p0[0]) / ln, (p1[1] - p0[1]) / ln

        def zc(r):
            return cloth_z + r - SINK * 0.5

        # butt and shaft stop short of the joint and a collar 3 mm fatter
        # covers the gap. REFUTED FIRST: each reaching 4 mm past the joint
        # into the other, which laid the two tapers' facets on one cone
        # (gap 0.01-0.09 mm, every seeded table with a cue)
        e = 0.002
        prims.append(P.rod("PoolTable_Cue", "cue_butt", (p0[0], p0[1], zc(rb)),
                           (pj[0] - ux * e, pj[1] - uy * e, zc(rj)), rb, rj, segments=6))
        prims.append(P.rod("PoolTable_Cue", "cue_shaft",
                           (pj[0] + ux * e, pj[1] + uy * e, zc(rj)),
                           (p1[0], p1[1], zc(rt)), rj, rt, segments=6))
        prims.append(P.rod("PoolTable_Cue", "steel",
                           (pj[0] - ux * 0.012, pj[1] - uy * 0.012, zc(rj)),
                           (pj[0] + ux * 0.012, pj[1] + uy * 0.012, zc(rj)),
                           rj + 0.003, rj + 0.003, segments=6))
        cue = (p0, p1, rb)
    balls = []
    names = list(BALLS)
    rng.shuffle(names)
    want = rng.randint(3, 7)
    chosen = ["ball_cue"] + [n for n in names if n != "ball_cue"][: want - 1]
    for name in chosen:
        for _try in range(20):
            bxp = rng.uniform(-play_x, play_x)
            byp = rng.uniform(-play_y, play_y)
            if any(math.hypot(bxp - a, byp - b) < 2 * BALL_R + 0.01 for a, b in balls):
                continue
            if cue is not None:
                (ax, ay), (qx, qy), rb = cue
                vx, vy = qx - ax, qy - ay
                t = _clamp(((bxp - ax) * vx + (byp - ay) * vy) / (vx * vx + vy * vy), 0.0, 1.0)
                if math.hypot(bxp - (ax + t * vx), byp - (ay + t * vy)) < BALL_R + rb + 0.008:
                    continue
            balls.append((bxp, byp))
            ball = P.sphere("PoolTable_Ball", name,
                            (bxp, byp, cloth_z + BALL_R - SINK), (BALL_R,) * 3,
                            u=8, v=4)
            prims.append(P.rotate_z(ball, rng.uniform(0, math.pi), (bxp, byp)))
            break

    cboxes = [((-hx, -hy, 0.0), (hx, hy, top))]
    lo, hi = P.bounds(prims)
    overshoot = max(abs(lo[0] + hx), abs(hi[0] - hx), abs(lo[1] + hy),
                    abs(hi[1] - hy), abs(lo[2]), abs(hi[2] - h))
    prims, cboxes = P.fit_exact(prims, (-hx, -hy, 0.0), (hx, hy, h), cboxes)
    return {"prims": prims, "collision": cboxes,
            "cloth": rng.randrange(len(CLOTHS)), "overshoot_m": overshoot}
