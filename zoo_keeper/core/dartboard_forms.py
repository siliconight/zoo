"""dartboard, planned in pure Python: a bar's wall cabinet with a bristle
board, its doors open (``open``, the default) or shut (``closed``).

Zoo 0.91.0. The walker's photo is the cabinet every 1997 bar hung: a shallow
wooden box with a lip round its front, felt behind the board, and two doors
on brass hinges whose insides are chalkboards with a cricket grid painted on
and a rail of three darts along the bottom. The second photo is a door close
up with the chalk still on it, and a tray under the cabinet with the chalk
and an eraser in it.

WHAT IS BUILT, in the recipe frame (metres, Z up, base-up, the wall the
slot's +Y face, the board facing -Y):

  * the CABINET: top and bottom boards overhanging the sides by `OVH`, the
    two sides, a back panel, and a lip strip inside each edge of the opening;
  * the FELT on the back panel and the BOARD on the felt, a
    `BOARD_SEGMENTS`-sided disc 451 mm across wearing `dartboard_art`'s
    board, with the NUMBER RING -- a steel annulus between the numbers and
    the rim -- standing proud of its face;
  * two DOORS hinged on the cabinet's front corners, with the gently arched
    top edge of the photo (both doors together make one arch), a
    CHALKBOARD panel inset on each inner face, and -- when open -- a dart
    RAIL along its bottom holding three darts, points down;
  * four brass HINGE knuckles on the hinge axes;
  * the TRAY under the cabinet, standing out past the doors, with two or
    three sticks of CHALK and an ERASER in it;
  * a variant's DARTS stuck in the board instead of on a rail.

THE BULL IS AT THE SLOT'S CENTRE HEIGHT, by construction, so a consumer
hangs a board at regulation height by lifting the slot's centre there. The
cabinet is centred in the slot's height with `margin` above it (the arch)
and the same below it (the tray), and nothing reaches past either.

THE SLOT IS THE OPEN FOOTPRINT. Open, the doors swing `angle_deg` (a
variant's preference in 110-150, `OPEN_DEG`) and the slot is everything a
body sees: the doors' free edges set its width and depth. The planner
chooses the cabinet's width, its depth and the angle that fill the slot
(`solve`), and `prims.fit_exact` takes the last fraction of a percent.
Closed, the slot is the cabinet and the tray. COLLISION IS THE CABINET BOX
ONLY: the doors, the tray and the darts are visual, so a body that brushes
a door is not stopped by it in mid-air.

THE RULES the interior species keep: the slot exact on every axis
(`fit_exact` ends the plan); parts that meet overlap by a few mm; no two
faces within 2 mm of one plane where they overlap (`prims.coincident_pairs`
is empty -- each buried part is buried a DIFFERENT depth, because two parts
buried alike leave their buried faces on one plane); no rod thin enough for
two of its facets to face each other within 2 mm (thin rods have an odd
number of sides).
"""
from __future__ import annotations

import math

from . import dartboard_art as ART
from . import prims as P

FORMS = ("open", "closed")
#: A variant's preferred opening, degrees from shut: the walker's photo is
#: about 130; bar doors are left wherever the last player swung them.
OPEN_DEG = (130.0, 118.0, 142.0, 124.0)
OPEN_MIN, OPEN_MAX = 100.0, 165.0
#: The cabinet's own width and depth ranges (a real cabinet is 0.6-0.75 m
#: wide and 0.1-0.12 m deep).
CAB_W = (0.56, 0.78)
CAB_D = (0.08, 0.14)
#: Per-form slot ranges the planner fills without distorting the board
#: (tests/test_dartboard.py builds every corner). The genome's dimension
#: ranges are their union.
FORM_RANGES = {
    "open": {"width": (1.00, 1.35), "depth": (0.30, 0.42), "height": (0.80, 1.00)},
    "closed": {"width": (0.60, 0.80), "depth": (0.14, 0.19), "height": (0.80, 1.00)},
}
#: Deli Counter's slot, the open footprint (`level_design._PIECES`).
DC_SIZES = ((1.1, 0.36, 0.9), (1.2, 0.38, 0.92))

BOARD_R = ART.BOARD_D / 2.0
BOARD_T = 0.038
BOARD_SEGMENTS = 40
RING = (0.2015, 0.2055)      # the number ring's radii: outside the numbers, inside the brand
RING_PROUD = 0.003
T = 0.018                    # cabinet board thickness
OVH = 0.004                  # top and bottom boards past the sides and the front
BACK_T = 0.012
FELT_T = 0.010
LIP_W = 0.022
LIP_D = 0.014
DT = 0.020                   # door thickness
DOOR_FRAME = 0.030
RAIL_H = 0.030
RAIL_D = 0.032
TRAY_OUT = 0.050             # the tray's front past the cabinet's
KNUCKLE_R = 0.007
#: The arch's rise over the cabinet, and the tray's drop under it: equal, so
#: the board's centre is the slot's. A fraction of the slot's height.
MARGIN_FRAC = 0.066

#: What the cabinet is made of, per variant: stained wood or painted black.
CABINET = ((("wood_stained", (0.30, 0.19, 0.12))), (("metal_painted", (0.025, 0.024, 0.024))),
           (("wood_stained", (0.30, 0.19, 0.12))), (("metal_painted", (0.025, 0.024, 0.024))))
MATERIALS = {
    "felt": ((0.018, 0.16, 0.15), "velvet"),
    "brass": ((0.62, 0.45, 0.16), "metal_bare"),
    "wire": ((0.62, 0.62, 0.60), "metal_bare"),
    "barrel": ((0.50, 0.50, 0.50), "metal_bare"),
    "shaft": ((0.03, 0.03, 0.03), "metal_painted"),
    "chalk": ((0.86, 0.86, 0.82), "paper"),
    "eraser": ((0.36, 0.24, 0.14), "wood"),
    "eraser_pad": ((0.10, 0.10, 0.10), "velvet"),
}
#: Flight colours per variant, one set a door: (left door's, right door's).
FLIGHTS = (((0.60, 0.04, 0.03), (0.03, 0.10, 0.50)),
           ((0.80, 0.55, 0.02), (0.02, 0.02, 0.02)),
           ((0.03, 0.30, 0.08), (0.55, 0.02, 0.35)),
           ((0.04, 0.20, 0.55), (0.70, 0.30, 0.02)))
#: Darts stuck in the board per variant, as (sector, ring) aims, and how
#: many that leaves each door's rail (three a player, six in all).
STUCK = ((),
         ((20, "treble"),),
         ((20, "single"), (None, "outer_bull")),
         ((19, "treble"), (3, "single")))

#: Bury depths, each at least 3 mm from the others, so no two buried faces
#: share a plane: the sides into the boards, the back panel, the side lips,
#: the top and bottom lips into the side lips, the felt.
SB, BP, LB, TB, FB = 0.004, 0.010, 0.008, 0.005, 0.014


def pick_form(form, w=None):
    if form in FORMS:
        return form
    if w is not None and w < 0.9:
        return "closed"
    return "open"


# --- building blocks -----------------------------------------------------------------

def _xz_prism(part, mat, poly, y0, y1):
    """A prism over a convex polygon ``poly`` [(x, z)] extruded from y0 to y1
    (y0 < y1). The polygon may be either winding; faces are wound outward."""
    area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly)))
    if area < 0:
        poly = list(reversed(poly))
    n = len(poly)
    verts = [(x, y0, z) for x, z in poly] + [(x, y1, z) for x, z in poly]
    faces = [tuple(range(n)), tuple(reversed(range(n, 2 * n)))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, n + i, n + j, j))
    return P.mesh(part, mat, verts, faces)


def _y_cyl(part, mat, cx, cz, r, y0, y1, segments, phase=0.0):
    """A cylinder along Y from y0 (its -Y cap) to y1."""
    verts = []
    for y in (y0, y1):
        for k in range(segments):
            a = phase + 2.0 * math.pi * k / segments
            verts.append((cx + r * math.cos(a), y, cz + r * math.sin(a)))
    n = segments
    faces = [tuple(range(n)), tuple(reversed(range(n, 2 * n)))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, n + i, n + j, j))
    return P.mesh(part, mat, verts, faces)


def _annulus(part, mat, cx, cz, r0, r1, y0, y1, segments):
    """A flat ring along Y: front and back quads, outer and inner walls."""
    verts = []
    for y in (y0, y1):
        for r in (r1, r0):
            for k in range(segments):
                a = 2.0 * math.pi * k / segments
                verts.append((cx + r * math.cos(a), y, cz + r * math.sin(a)))
    n = segments

    def i(layer, ring, k):
        return (layer * 2 + ring) * n + (k % n)
    faces = []
    for k in range(n):
        faces.append((i(0, 0, k), i(0, 0, k + 1), i(0, 1, k + 1), i(0, 1, k)))      # front, -Y
        faces.append((i(1, 0, k), i(1, 1, k), i(1, 1, k + 1), i(1, 0, k + 1)))      # back, +Y
        faces.append((i(0, 0, k), i(1, 0, k), i(1, 0, k + 1), i(0, 0, k + 1)))      # outer
        faces.append((i(0, 1, k), i(0, 1, k + 1), i(1, 1, k + 1), i(1, 1, k)))      # inner
    return P.mesh(part, mat, verts, faces)


def signed_volume(p):
    """Six times nothing: the enclosed volume, positive when every face is
    wound outward (the check that a prim's normals point out)."""
    vs = p["verts"]
    tot = 0.0
    for f in p["faces"]:
        a = vs[f[0]]
        for k in range(1, len(f) - 1):
            b, c = vs[f[k]], vs[f[k + 1]]
            tot += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return tot / 6.0


def _dart(part_prefix, mat_flight, base, direction, roll=0.0):
    """A dart from its point ``base`` along the unit ``direction``: point,
    barrel, shaft and two crossed flights. 0.152 m long. Thin rods have an
    odd number of sides."""
    ux, uy, uz = direction
    ln = math.sqrt(ux * ux + uy * uy + uz * uz)
    ux, uy, uz = ux / ln, uy / ln, uz / ln

    def at(t):
        return (base[0] + ux * t, base[1] + uy * t, base[2] + uz * t)
    out = [P.rod(part_prefix, "barrel", at(0.0), at(0.034), 0.0012, 0.0019, segments=5),
           P.rod(part_prefix, "barrel", at(0.028), at(0.078), 0.0034, 0.0030, segments=7),
           P.rod(part_prefix, "shaft", at(0.072), at(0.118), 0.0021, segments=5)]
    # the flights: two crossed thin boxes along the axis
    ref = (0.0, 0.0, 1.0) if abs(uz) < 0.9 else (1.0, 0.0, 0.0)
    ax = (ux, uy, uz)
    s1 = P._cross(ax, ref)
    l1 = math.sqrt(P._dot(s1, s1))
    s1 = (s1[0] / l1, s1[1] / l1, s1[2] / l1)
    s2 = P._cross(ax, s1)
    c, s = math.cos(roll), math.sin(roll)
    e1 = tuple(s1[k] * c + s2[k] * s for k in range(3))
    e2 = tuple(-s1[k] * s + s2[k] * c for k in range(3))
    # the second flight's ends stand 4 mm inside the first's, or their end
    # caps lie in one plane where the two cross
    for (e, other), (t0, t1) in (((e1, e2), (0.106, 0.152)), ((e2, e1), (0.110, 0.148))):
        half_w, half_t = 0.016, 0.00125
        corners = []
        for t in (t0, t1):
            wid = half_w * (0.45 if t == t0 else 1.0)
            for sw in (-1, 1):
                for st in (-1, 1):
                    p0 = at(t)
                    corners.append(tuple(p0[k] + e[k] * sw * wid + other[k] * st * half_t
                                         for k in range(3)))
        # corners: t0 (-w,-t) (-w,+t) (+w,-t) (+w,+t), then t1 the same
        idx = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
        prim = P.mesh(part_prefix, mat_flight, corners, [tuple(f) for f in idx])
        if signed_volume(prim) < 0:
            prim["faces"] = [tuple(reversed(f)) for f in prim["faces"]]
        out.append(prim)
    return out


# --- the plan ------------------------------------------------------------------------

def _build(Wb, BD, h, d, form, variant, phi_deg):
    """Every primitive at cabinet width ``Wb`` and depth ``BD``, before the
    fit. Returns (prims, facts)."""
    M = MARGIN_FRAC * h
    Hc = h - 2.0 * M
    yb = d / 2.0
    yf = yb - BD
    zc = h / 2.0
    v = int(variant) % 4
    prims = []
    cab = "cabinet"
    # --- the cabinet box
    prims.append(P.box("Dartboard_Cabinet", cab, (-Wb / 2 - OVH, yf - OVH, M + Hc - T),
                       (Wb / 2 + OVH, yb, M + Hc)))
    prims.append(P.box("Dartboard_Cabinet", cab, (-Wb / 2 - OVH, yf - OVH, M),
                       (Wb / 2 + OVH, yb, M + T)))
    for s in (-1, 1):
        x0, x1 = sorted((s * Wb / 2, s * (Wb / 2 - T)))
        prims.append(P.box("Dartboard_Cabinet", cab, (x0, yf, M + T - SB), (x1, yb - 0.004, M + Hc - T + SB)))
    ybp0, ybp1 = yb - 0.008 - BACK_T, yb - 0.008
    prims.append(P.box("Dartboard_Cabinet", cab, (-Wb / 2 + T - BP, ybp0, M + T - BP),
                       (Wb / 2 - T + BP, ybp1, M + Hc - T + BP)))
    # the lip: side strips full height, top and bottom strips between them
    for s in (-1, 1):
        x0, x1 = sorted((s * (Wb / 2 - T + LB), s * (Wb / 2 - T - LIP_W)))
        prims.append(P.box("Dartboard_Cabinet", cab, (x0, yf + 0.003, M + T - LB),
                           (x1, yf + LIP_D, M + Hc - T + LB)))
    xl = Wb / 2 - T - LIP_W + TB
    prims.append(P.box("Dartboard_Cabinet", cab, (-xl, yf + 0.006, M + Hc - T - LIP_W),
                       (xl, yf + LIP_D - 0.003, M + Hc - T + TB)))
    prims.append(P.box("Dartboard_Cabinet", cab, (-xl, yf + 0.006, M + T - TB),
                       (xl, yf + LIP_D - 0.003, M + T + LIP_W)))
    # --- felt and board
    yfelt0 = ybp0 - FELT_T
    prims.append(P.box("Dartboard_Felt", "felt", (-Wb / 2 + T - FB, yfelt0, M + T - FB),
                       (Wb / 2 - T + FB, ybp0 + 0.008, M + Hc - T + FB)))
    yboard1 = yfelt0 + 0.004
    yboard0 = yboard1 - BOARD_T
    board = _y_cyl("Dartboard_Board", "board", 0.0, zc, BOARD_R, yboard0, yboard1,
                   BOARD_SEGMENTS, phase=math.pi / BOARD_SEGMENTS)
    uvs = []
    for f in board["faces"]:
        if f == tuple(range(BOARD_SEGMENTS)):
            uvs.append(tuple(ART.board_uv(board["verts"][i][0], board["verts"][i][2] - zc) for i in f))
        else:
            uvs.append((ART.BOARD_DARK_UV,) * len(f))
    board["uvs"] = uvs
    prims.append(board)
    prims.append(_annulus("Dartboard_NumberRing", "wire", 0.0, zc, RING[0], RING[1],
                          yboard0 - RING_PROUD, yboard0 + 0.004, BOARD_SEGMENTS))
    # --- stuck darts
    rng_roll = 0
    # a dart in the board keeps a cabinet from shutting: closed, none
    for sector, ring in (STUCK[v] if form == "open" else ()):
        cx, cz = ART._spot_centre(sector, ring)
        bx, bz = cx / 1000.0, cz / 1000.0
        if sector is None:
            bx, bz = 0.006, -0.004
        direction = (0.05 * (1 if bx >= 0 else -1), -1.0, 0.16)
        prims += _dart("Dartboard_Dart", "flight_%d" % (rng_roll % 2),
                       (bx, yboard0 + 0.010, zc + bz), direction, roll=0.3 + 0.4 * rng_roll)
        rng_roll += 1
    # --- the doors
    phi = math.radians(phi_deg) if form == "open" else 0.0
    yd1 = yf - OVH - 0.003
    yd0 = yd1 - DT
    doors = []
    rail_left = [3, 3]
    for k in range(len(STUCK[v])):
        rail_left[k % 2] -= 1
    for side_i, s in enumerate((-1, 1)):
        xh = s * (Wb / 2 + OVH + 0.001)
        xe = s * 0.002
        x0, x1 = sorted((xh, xe))
        span = Wb / 2 + OVH + 0.001 - 0.002
        top = []
        for q in range(5):
            x = xe + (xh - xe) * q / 4.0
            # the crown at the doors' meeting edges, exactly `margin` up
            rise = M * max(0.0, 1.0 - ((abs(x) - 0.002) / span) ** 2)
            top.append((x, M + Hc + rise))
        poly = [(xh, M), (xe, M)] + top
        dp = [_xz_prism("Dartboard_Door", cab, poly, yd0, yd1)]
        pz0 = M + 0.020 + RAIL_H + 0.012
        pz1 = M + Hc - DOOR_FRAME
        px0, px1 = x0 + DOOR_FRAME, x1 - DOOR_FRAME
        panel = P.box("Dartboard_Chalkboard", "chalkboard", (px0, yd1 - 0.004, pz0), (px1, yd1 + 0.004, pz1))
        rect_key = "L" if s < 0 else "R"
        puvs = []
        for fi, f in enumerate(panel["faces"]):
            if fi == 4:                        # the +Y face: the chalkboard
                puvs.append(tuple(("uv", rect_key, (px1 - panel["verts"][i][0]) / (px1 - px0),
                                   (panel["verts"][i][2] - pz0) / (pz1 - pz0)) for i in f))
            else:
                puvs.append((("uv", "edge", 0.5, 0.5),) * 4)
        panel["uvs"] = puvs
        dp.append(panel)
        if form == "open":
            dp.append(P.box("Dartboard_Rail", cab, (px0, yd1 - 0.010, M + 0.020),
                            (px1, yd1 + RAIL_D, M + 0.020 + RAIL_H)))
            n_d = rail_left[side_i]
            for j in range(n_d):
                dx = px0 + (px1 - px0) * (j + 1) / (n_d + 1)
                base = (dx, yd1 + RAIL_D / 2.0 + 0.002, M + 0.020 + RAIL_H - 0.012)
                dp += _dart("Dartboard_Dart", "flight_%d" % side_i, base, (0.0, 0.10, 1.0),
                            roll=0.6 + 0.5 * j)
        doors.append((s, xh, dp))
    for s, xh, dp in doors:
        a = s * phi
        for p in dp:
            prims.append(P.rotate_z(p, a, about=(xh, yd1)) if a else p)
        for zk in (M + 0.09, M + Hc - 0.09):
            prims.append(P.cyl("Dartboard_Hinge", "brass", (xh, yd1), KNUCKLE_R, zk - 0.03, zk + 0.03,
                               segments=8))
    # --- the tray, its chalk and its eraser
    tx0, tx1 = -Wb / 2 + 0.030, Wb / 2 - 0.030
    ytf = yf - OVH - TRAY_OUT
    tray = "cabinet"
    prims.append(P.box("Dartboard_Tray", tray, (tx0, ytf, 0.0), (tx1, yb - 0.020, 0.008)))
    prims.append(P.box("Dartboard_Tray", tray, (tx0 + 0.003, ytf + 0.003, 0.004), (tx1 - 0.003, ytf + 0.010, M - 0.012)))
    for s in (-1, 1):
        ex0, ex1 = sorted((s * (Wb / 2 - 0.033), s * (Wb / 2 - 0.041)))
        prims.append(P.box("Dartboard_Tray", tray, (ex0, ytf + 0.013, 0.0055), (ex1, yb - 0.023, M - 0.012)))
    prims.append(P.box("Dartboard_Tray", tray, (tx0 + 0.006, yf + 0.010, 0.0025), (tx1 - 0.006, yf + 0.018, M + 0.005)))
    ytm = (ytf + 0.010 + yf + 0.010) / 2.0
    chalks = 2 + (v % 2)
    for k in range(chalks):
        ln = 0.030 + 0.012 * ((v + k) % 3)
        cx = tx0 + 0.05 + k * 0.045
        ang = math.radians(8.0 * ((v + 2 * k) % 5) - 16.0)
        r = 0.0055
        rod = P.rod("Dartboard_Chalk", "chalk", (cx - ln / 2, ytm, 0.008 + r - 0.003),
                    (cx + ln / 2, ytm, 0.008 + r - 0.003), r, segments=7)
        prims.append(P.rotate_z(rod, ang, about=(cx, ytm)))
    ex = tx1 - 0.10 - 0.02 * (v % 2)
    er = math.radians(6.0 - 3.0 * v)
    pad = P.box("Dartboard_Eraser", "eraser_pad", (ex - 0.055, ytm - 0.020, 0.005), (ex + 0.055, ytm + 0.020, 0.014))
    blk = P.box("Dartboard_Eraser", "eraser", (ex - 0.050, ytm - 0.016, 0.011), (ex + 0.050, ytm + 0.016, 0.036))
    prims += [P.rotate_z(pad, er, about=(ex, ytm)), P.rotate_z(blk, er, about=(ex, ytm))]
    # the marker the recipe reads back after the fit
    prims.append({"part": "", "mat": "", "bevel": False,
                  "verts": [(0.0, yboard0, zc)], "faces": []})
    facts = {"margin": M, "cabinet_h": Hc, "yf": yf, "yb": yb, "board_face_y": yboard0,
             "collision": ((-Wb / 2 - OVH, yf - OVH, M), (Wb / 2 + OVH, yb, M + Hc)),
             "rails": rail_left if form == "open" else [0, 0],
             "stuck": len(STUCK[v]) if form == "open" else 0}
    return prims, facts


def _bounds(prims):
    return P.bounds([p for p in prims if p["faces"]])


def solve(w, d, h, form, variant=0):
    """``(Wb, BD, angle_deg)``: the cabinet and the opening that fill the
    slot. Open: over the cabinet widths, the angle that makes the width and
    then the depth that makes the depth, scored by how far each leaves its
    range and by distance from the variant's preferred angle; then three
    passes against the measured bounds. Closed: width and depth directly."""
    pref = OPEN_DEG[int(variant) % len(OPEN_DEG)]
    if form == "closed":
        Wb = min(CAB_W[1], max(CAB_W[0], w - 0.024))
        BD = min(CAB_D[1], max(CAB_D[0], d - OVH - TRAY_OUT))
        phi = 0.0
    else:
        best = None
        steps = 45
        for i in range(steps + 1):
            Wb = CAB_W[0] + (CAB_W[1] - CAB_W[0]) * i / steps
            c = 1.0 - (w - 0.035) / Wb
            c = max(-1.0, min(1.0, c))
            phi = math.degrees(math.acos(c))
            Wd = Wb / 2.0
            BD = d - Wd * math.sin(math.radians(phi)) - 0.030
            pen = (max(0.0, CAB_D[0] - BD, BD - CAB_D[1]) * 100.0
                   + max(0.0, OPEN_MIN - phi, phi - OPEN_MAX)
                   + abs(phi - pref) * 0.002)
            if best is None or pen < best[0]:
                best = (pen, Wb, BD, phi)
        _pen, Wb, BD, phi = best
        BD = min(CAB_D[1], max(CAB_D[0], BD))
    def measure(Wb_, BD_, phi_):
        lo, hi = _bounds(_build(Wb_, BD_, h, d, form, variant, phi_)[0])
        return hi[0] - lo[0], hi[1] - lo[1]

    for _ in range(10):
        bw, bd = measure(Wb, BD, phi)
        ew, ed = w - bw, d - bd
        if abs(ew) < 2e-4 and abs(ed) < 2e-4:
            break
        # the cabinet's depth takes the depth first: it moves nothing else
        BD2 = min(CAB_D[1], max(CAB_D[0], BD + ed))
        ed -= BD2 - BD
        BD = BD2
        if form == "closed":
            Wb = min(CAB_W[1], max(CAB_W[0], Wb + ew))
            continue
        # the width by the cabinet's width alone while that is in range, so
        # a variant keeps the angle it prefers; what the depth could not
        # take, and what the width's range cannot, by the angle and the
        # width together (Newton on two unknowns, a measured Jacobian)
        dw_W, dd_W = [(a - b) / 0.01 for a, b in zip(measure(Wb + 0.01, BD, phi), (bw, bd))]
        if abs(ed) < 2e-4:
            Wb2 = min(CAB_W[1], max(CAB_W[0], Wb + ew / dw_W))
            if abs(Wb2 - (Wb + ew / dw_W)) < 1e-9:
                Wb = Wb2
                continue
        dw_P, dd_P = [(a - b) / 1.0 for a, b in zip(measure(Wb, BD, phi + 1.0), (bw, bd))]
        det = dw_W * dd_P - dw_P * dd_W
        if abs(det) < 1e-9:
            break
        dW = (ew * dd_P - dw_P * ed) / det
        dP = (dw_W * ed - ew * dd_W) / det
        Wb = min(CAB_W[1], max(CAB_W[0], Wb + dW))
        phi = min(OPEN_MAX, max(OPEN_MIN, phi + dP))
    return Wb, BD, phi


def plan(w, d, h, form="auto", variant=0):
    """``{prims, collision, bull, form, angle_deg, cabinet, scale, facts}``.

    ``bull`` is the board's centre on its face, ``scale`` the per-axis factor
    `fit_exact` applied (1.0 means the planner filled the slot itself)."""
    form = pick_form(form, w)
    Wb, BD, phi = solve(w, d, h, form, variant)
    prims, facts = _build(Wb, BD, h, d, form, variant, phi)
    lo, hi = _bounds(prims)
    shift = (-(lo[0] + hi[0]) / 2.0, 0.0, 0.0)
    prims = [P.translate(p, shift) for p in prims]
    lo, hi = _bounds(prims)
    scale = (w / (hi[0] - lo[0]), d / (hi[1] - lo[1]), h / (hi[2] - lo[2]))
    (c0, c1) = facts["collision"]
    c0 = (c0[0] + shift[0], c0[1], c0[2])
    c1 = (c1[0] + shift[0], c1[1], c1[2])
    marker = prims.pop()
    solid = prims
    fitted, boxes = P.fit_exact(solid + [marker], (-w / 2, -d / 2, 0.0), (w / 2, d / 2, h), [(c0, c1)])
    marker = fitted.pop()
    return {"prims": fitted, "collision": boxes, "bull": marker["verts"][0], "form": form,
            "angle_deg": phi, "cabinet": (Wb, BD), "scale": scale, "facts": facts}


def chalk_panel_size(plan_):
    """(width, height) in metres of one door's chalkboard, before the fit."""
    Wb, _BD = plan_["cabinet"]
    M = plan_["facts"]["margin"]
    Hc = plan_["facts"]["cabinet_h"]
    x0, x1 = -(Wb / 2 + OVH + 0.001), -0.002
    return (x1 - x0 - 2 * DOOR_FRAME, (M + Hc - DOOR_FRAME) - (M + 0.020 + RAIL_H + 0.012))


def resolve_uvs(prims, rects, size):
    """Replace the chalk panels' symbolic uvs ("uv", rect, u, v) with the
    raster's (u, v) once the art's packing is known."""
    out = []
    for p in prims:
        if "uvs" in p and p["uvs"] and isinstance(p["uvs"][0][0], tuple) and len(p["uvs"][0][0]) == 4:
            q = dict(p)
            q["uvs"] = [tuple(ART.uv_of(rects[c[1]], size, c[2], c[3]) for c in face)
                        for face in p["uvs"]]
            out.append(q)
        else:
            out.append(p)
    return out
