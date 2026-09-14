"""booth_seat, planned in pure Python: where people sat -- a bar or diner
booth, or a 1990s couch.

  * ``booth`` -- wood end panels the full height, a recessed kick, an
    upholstered seat on a fascia, a high back of channel-tufted cushions
    leaning back a few degrees, and a wood cap rail over the back. One seat
    facing -Y, or two back to back on a shared spine when the slot is deep
    enough for both (BACK_TO_BACK_DEPTH).
  * ``sofa`` -- short turned feet, a skirted base, two arms with a rolled
    top, a frame back, crowned seat and back cushions (the back ones
    leaning back), and on most seeds a throw pillow tipped against one arm.

``auto`` is the booth when the slot is AUTO_BOOTH_HEIGHT or taller (a
booth's back is a head's height; a couch's is a shoulder's), the sofa
otherwise.

THE RULES the interior species keep: extents exactly w x d x h; parts that
meet overlap by a few mm; no two faces within 2 mm of one plane where they
overlap (`prims.coincident_pairs`, over sizes, forms and seeds, in the
tests); deterministic from the rng passed in.

Frame: metres, Z up, base-up, length along x, a single seat facing -Y.
"""
from __future__ import annotations

import math

from . import prims as P

FORMS = ("booth", "sofa")
AUTO_BOOTH_HEIGHT = 1.0
BACK_TO_BACK_DEPTH = 1.05
SINK = 0.003
BURY = 0.005          # a part reaching into a panel or arm
END_CLEAR = 0.0035    # between the end planes of parts that interpenetrate
SEAT_H = 0.46

#: material key -> (linear RGB, kind); "upholstery" is the genome's colour
MATERIALS = {
    "frame": ([0.24, 0.14, 0.07], "wood"),        # booth panels, cap, kick
    "foot": ([0.10, 0.06, 0.035], "wood"),        # sofa feet
    # a throw pillow: cream against any of the 1990s upholstery colours
    "accent": ([0.62, 0.56, 0.42], "canvas"),
}


def pick_form(form, w, d, h):
    if form in FORMS:
        return form
    return "booth" if h >= AUTO_BOOTH_HEIGHT else "sofa"


def plan(w, d, h, rng, form="auto"):
    """``{"prims", "collision", "form", "sides", "overshoot_m"}``."""
    form = pick_form(form, w, d, h)
    if form == "booth":
        prims, cboxes, sides = _booth(w, d, h, rng)
    else:
        prims, cboxes, sides = _sofa(w, d, h, rng)
    lo, hi = P.bounds(prims)
    overshoot = max(abs(lo[0] + w / 2), abs(hi[0] - w / 2), abs(lo[1] + d / 2),
                    abs(hi[1] - d / 2), abs(lo[2]), abs(hi[2] - h))
    prims, cboxes = P.fit_exact(prims, (-w / 2, -d / 2, 0.0), (w / 2, d / 2, h),
                                cboxes)
    return {"prims": prims, "collision": cboxes, "form": form, "sides": sides,
            "overshoot_m": overshoot}


def _mirror_y(p):
    """Mirror a primitive through y = 0, keeping its faces outward."""
    q = dict(p)
    q["verts"] = [(v[0], -v[1], v[2]) for v in p["verts"]]
    q["faces"] = [tuple(reversed(f)) for f in p["faces"]]
    return q


def _booth(w, d, h, rng):
    prims, cboxes = [], []
    end_t = 0.045
    inner = w / 2 - end_t
    # each part reaches a different depth into the end panels: at one shared
    # depth the kick, seat base, back and cap laid their end faces in one
    # plane inside the panel wherever their heights overlapped
    xin = inner + BURY
    x_kick, x_back, x_cap = xin + 0.004, xin + 0.008, xin + 0.012
    for sx in (-1, 1):
        x0, x1 = sorted((sx * w / 2, sx * inner))
        prims.append(P.box("Booth_EndPanel", "frame", (x0, -d / 2, 0.0), (x1, d / 2, h),
                           bevel=True))
    sides = 2 if d >= BACK_TO_BACK_DEPTH else 1
    cap_top = h - 0.012
    if sides == 2:
        back_t = 0.10
        spine_y0, spine_y1 = -back_t / 2, back_t / 2
        # a single seat's parts are drawn for the front half and mirrored
        seat_front = -d / 2 + 0.02
        back_face = spine_y0
        prims.append(P.box("Booth_Back", "frame", (-x_back, spine_y0, 0.094),
                           (x_back, spine_y1, cap_top - 0.03), bevel=True))
        prims.append(P.box("Booth_Cap", "frame", (-x_cap, spine_y0 - 0.02, cap_top - 0.035),
                           (x_cap, spine_y1 + 0.02, cap_top), bevel=True))
    else:
        back_t = 0.12
        seat_front = -d / 2 + 0.02
        back_face = d / 2 - 0.004 - back_t
        prims.append(P.box("Booth_Back", "frame", (-x_back, back_face, 0.094),
                           (x_back, d / 2 - 0.004, cap_top - 0.03), bevel=True))
        prims.append(P.box("Booth_Cap", "frame", (-x_cap, back_face - 0.02, cap_top - 0.035),
                           (x_cap, d / 2 - 0.008, cap_top), bevel=True))
    half = []
    sd = back_face - seat_front                  # seat depth to the back face
    # the kick, recessed; its bottom 4 mm off the floor so it shares no
    # plane with the end panels' bottoms where it reaches into them
    half.append(P.box("Booth_Kick", "frame", (-x_kick, seat_front + 0.06, 0.004),
                      (x_kick, back_face + BURY + 0.004, 0.10)))
    half.append(P.box("Booth_SeatBase", "upholstery", (-xin, seat_front + 0.02, 0.10 - SINK),
                      (xin, back_face + BURY, SEAT_H - 0.09)))
    # seat cushions along the run, 6 mm off the panels and each other
    n_seat = max(1, int(round(2 * inner / 0.9)))
    gap = 0.006
    span = (2 * inner - gap * (n_seat + 1)) / n_seat
    seat_ends = []
    for k in range(n_seat):
        x0 = -inner + gap + k * (span + gap)
        seat_ends += [x0, x0 + span]
        half.append(P.pillow("Booth_Seat", "upholstery",
                             (x0, seat_front, SEAT_H - 0.09 - SINK),
                             (x0 + span, back_face - 0.05, SEAT_H - 0.012), 0.012,
                             bevel=True))
    # channel-tufted back, leaning back LEAN about the back face's foot
    lean = math.radians(rng.uniform(5.0, 9.0))
    n_ch = max(2, int(round(2 * inner / rng.uniform(0.2, 0.28))))
    span = (2 * inner - gap * (n_ch + 1)) / n_ch
    ch_top = cap_top - 0.07
    ch_gap = gap + 0.004         # off the seat cushions' end planes
    span = (2 * inner - ch_gap * 2 - gap * (n_ch - 1)) / n_ch
    for k in range(n_ch):
        x0 = -inner + ch_gap + k * (span + gap)
        x1 = x0 + span
        # a channel's foot reaches down into the seat cushions, so an end of
        # one within END_CLEAR of a seat cushion's end would lie in its
        # plane (measured: 0.0 and 1.33 mm, where both runs split at x = 0)
        for e in seat_ends:
            if abs(x0 - e) < END_CLEAR:
                x0 = e + END_CLEAR
            if abs(x1 - e) < END_CLEAR:
                x1 = e - END_CLEAR
        ch = _channel(x0, x1 - x0, back_face, SEAT_H - 0.03, ch_top)
        # turned about its buried TOP edge, so its foot comes forward and its
        # top stays in the frame. REFUTED FIRST: turned about its foot, which
        # swung the top 10 cm back -- straight through a back-to-back
        # booth's 10 cm spine and into the other side's channels
        half.append(P.rotate_x(ch, -lean, (back_face + 0.02, ch_top)))
    prims += half
    cboxes.append(((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h)))
    if sides == 2:
        prims += [_mirror_y(p) for p in half]
    return prims, cboxes, sides


def _channel(x0, span, back_face, z0, z1):
    """One tufted channel of a booth back: a slab whose FRONT (the sitter's
    side, -Y) is crowned 14 mm down its middle."""
    depth = 0.07
    crown = 0.014
    xm = x0 + span / 2
    yb = back_face + 0.02                 # buried in the back frame
    yf = back_face - depth
    verts = [(x0, yb, z0), (x0 + span, yb, z0), (x0 + span, yb, z1), (x0, yb, z1),
             (x0, yf, z0), (xm, yf - crown, z0), (x0 + span, yf, z0),
             (x0, yf, z1), (xm, yf - crown, z1), (x0 + span, yf, z1)]
    faces = [(0, 3, 2, 1),                  # back
             (4, 5, 8, 7), (5, 6, 9, 8),    # crowned front, two facets
             (0, 1, 6, 5, 4),               # bottom
             (3, 7, 8, 9, 2),               # top
             (0, 4, 7, 3), (1, 2, 9, 6)]    # ends
    return P.mesh("Booth_BackCushion", "upholstery", verts, faces, bevel=True)


def _sofa(w, d, h, rng):
    prims, cboxes = [], []
    arm_w = max(0.14, min(0.22, 0.1 * w))
    rr = arm_w / 2 + 0.012                  # the rolled arm's radius
    arm_h = min(h - 0.12, max(SEAT_H + 0.12, 0.72 * h))
    seat_top = min(SEAT_H, arm_h - 0.1)
    inner = w / 2 - arm_w
    # feet under the arms
    for sx in (-1, 1):
        for sy in (-1, 1):
            prims.append(P.cyl("Sofa_Foot", "foot",
                               (sx * (w / 2 - arm_w / 2), sy * (d / 2 - 0.08)),
                               0.028, 0.0, 0.09, segments=8, r_top=0.022))
    # the base between the arms, and the arms
    prims.append(P.box("Sofa_Base", "upholstery", (-(inner + BURY), -d / 2 + 0.05, 0.087),
                       (inner + BURY, d / 2 - 0.02, 0.30), bevel=True))
    for sx in (-1, 1):
        x0, x1 = sorted((sx * inner, sx * (w / 2 - 0.012)))
        prims.append(P.box("Sofa_Arm", "upholstery", (x0, -d / 2 + 0.035, 0.08),
                           (x1, d / 2 - 0.024, arm_h - rr), bevel=True))
        # the roll: a cylinder along Y whose outer edge is the slot's side
        cx = sx * (w / 2 - rr)
        roll = P.cyl("Sofa_ArmRoll", "upholstery", (cx, -(arm_h - rr)), rr,
                     -d / 2, d / 2 - 0.03, segments=10)
        prims.append(P.lay_along_y(roll))
    # frame back, its rear the slot's back
    back_front = d / 2 - 0.20
    # 4 mm further into the arms than the base, whose side faces it would
    # otherwise share where the two overlap inside the arm
    prims.append(P.box("Sofa_Back", "upholstery", (-(inner + BURY + 0.004), back_front, 0.25),
                       (inner + BURY + 0.004, d / 2, h - 0.14), bevel=True))
    n = 2 if w < 1.9 else 3
    gap = 0.008
    span = (2 * inner - gap * (n + 1)) / n
    lean = math.radians(rng.uniform(10.0, 16.0))
    for k in range(n):
        x0 = -inner + gap + k * (span + gap)
        # seat cushion, its back end into the back cushion
        prims.append(P.pillow("Sofa_Seat", "upholstery", (x0, -d / 2 + 0.01, 0.30 - 0.012),
                              (x0 + span, back_front - 0.03, seat_top - 0.015),
                              0.015, bevel=True))
        # back cushion: a crowned slab turned about its top back edge so its
        # foot sits forward on the seat, 4 mm narrower each side than the
        # seat cushion below so their end faces are not one plane
        cush = _channel(x0 + 0.004, span - 0.008, back_front + 0.02,
                        seat_top - 0.04, h - 0.01)
        cush = P.recolour(cush, part="Sofa_BackCushion")
        cush = P.rotate_x(cush, -lean, (back_front + 0.04, h - 0.01))
        top = max(v[2] for v in cush["verts"])
        prims.append(P.translate(cush, (0.0, 0.0, h - top)))
    if rng.random() < 0.7:
        sx = rng.choice((-1, 1))
        # no taller than the room above the seat: 0.36 on a 0.75 m couch
        # stood 11 cm over the slot and fit_exact squeezed the sofa to fit it
        size = min(0.36, 0.85 * (h - seat_top))
        cx = sx * (inner - size * 0.35 - 0.03)
        cy = back_front - 0.18
        pil = P.pillow("Sofa_Pillow", "accent", (cx - size / 2, cy - 0.06, seat_top - 0.02),
                       (cx + size / 2, cy + 0.06, seat_top - 0.02 + size), 0.03, bevel=True)
        pil = P.rotate_y(pil, sx * math.radians(rng.uniform(18, 30)), (cx, seat_top))
        pil = P.rotate_z(pil, math.radians(rng.uniform(-12, 12)), (cx, cy))
        # tipped against the arm it may lean over it on a narrow couch
        # (3 cm past the slot at 0.9 m wide): kept between the arms
        plo, phi = P.bounds([pil])
        shift = min(0.0, inner - phi[0]) + max(0.0, -inner - plo[0])
        prims.append(P.translate(pil, (shift, 0.0, 0.0)))
    cboxes.append(((-w / 2, -d / 2, 0.0), (w / 2, d / 2, arm_h)))
    cboxes.append(((-w / 2, back_front, arm_h), (w / 2, d / 2, h)))
    return prims, cboxes, 1
