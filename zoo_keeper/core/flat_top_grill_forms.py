"""What a flat-top grill is, in numbers: ONE place, no bpy.

A heavy steel cabinet on four legs, a flat cooktop plate at counter height,
splash guards up the back and both ends, a grease trap along the front lip,
and a row of control knobs on the front face. Origin at floor centre; the
controls face -Y.

THE EXTENTS ARE EXACT (Zoo 1.80.0). The knobs stand KNOB_PROUD off the
cabinet's face, so the cabinet is that much shallower than the slot and set
back by half of it, and the knobs end on the slot's front face. Until 1.80.0
the cabinet took the whole depth and the knobs hung 35 mm past it: the module
measured 0.935 m against an exact 0.900 m slot, failed `fit_depth`, and fell
back to base in every kitchen that drew it (cold runs 9132, 9179, 9185).
"""
from __future__ import annotations

LEG_H = 0.12          # m
GUARD_H = 0.12        # m, splash guards above the cooking surface
PLATE_T = 0.03        # m, the cooktop plate
GUARD_T = 0.02        # m
KNOB_R = 0.022        # m
KNOB_LEN = 0.03       # m, along Y
KNOB_GAP = 0.005      # m, between the cabinet face and the knob
KNOB_PROUD = KNOB_GAP + KNOB_LEN   # how far the knobs stand off the face


def layout(w, d, h, n_knobs=3):
    """``[(name, shape, centre, size)]``. ``shape`` is ``"box"`` with ``size``
    ``(sx, sy, sz)``, or ``"cylinder"`` with ``size`` ``(radius, length,
    axis)``. Every part lies inside ``(-w/2..w/2, -d/2..d/2, 0..h)``, and
    together they reach every face of it."""
    surface_z = h - GUARD_H
    body_h = surface_z - PLATE_T - LEG_H
    cd = d - KNOB_PROUD               # the cabinet's depth
    cy = KNOB_PROUD / 2.0             # its centre, set back
    front = cy - cd / 2.0             # its face: -d/2 + KNOB_PROUD
    gz = surface_z + GUARD_H / 2.0
    parts = [
        ("Grill_Body", "box", (0.0, cy, LEG_H + body_h / 2.0), (w, cd, body_h)),
        ("Grill_Cooktop", "box", (0.0, cy, surface_z - PLATE_T / 2.0),
         (w * 0.98, cd * 0.98, PLATE_T)),
        ("Grill_SplashGuard_B", "box", (0.0, d / 2.0 - GUARD_T / 2.0, gz),
         (w, GUARD_T, GUARD_H)),
    ]
    for side, sx in (("L", -1), ("R", 1)):
        parts.append(("Grill_SplashGuard_%s" % side, "box",
                      (sx * (w / 2.0 - GUARD_T / 2.0), cy, gz),
                      (GUARD_T, cd, GUARD_H)))
    parts.append(("Grill_GreaseTrap", "box",
                  (0.0, front + 0.02, surface_z - PLATE_T - 0.015),
                  (w * 0.7, 0.03, 0.03)))
    for i in range(n_knobs):
        x = (i - (n_knobs - 1) / 2.0) * (w * 0.14)
        parts.append(("Grill_Knob_%d" % (i + 1), "cylinder",
                      (x, front - KNOB_GAP - KNOB_LEN / 2.0,
                       LEG_H + body_h * 0.6),
                      (KNOB_R, KNOB_LEN, "Y")))
    i = 0
    for sx in (-1, 1):
        for sy in (-1, 1):
            i += 1
            parts.append(("Grill_Leg_%d" % i, "box",
                          (sx * (w / 2.0 - 0.06), cy + sy * (cd / 2.0 - 0.06),
                           LEG_H / 2.0), (0.05, 0.05, LEG_H)))
    return parts


def bounds(parts):
    """``((x0, y0, z0), (x1, y1, z1))`` over every part."""
    lo, hi = [float("inf")] * 3, [float("-inf")] * 3
    for _name, shape, c, s in parts:
        if shape == "box":
            half = (s[0] / 2.0, s[1] / 2.0, s[2] / 2.0)
        else:
            r, length, axis = s
            half = [r, r, r]
            half["XYZ".index(axis)] = length / 2.0
        for k in range(3):
            lo[k] = min(lo[k], c[k] - half[k])
            hi[k] = max(hi[k], c[k] + half[k])
    return tuple(lo), tuple(hi)
