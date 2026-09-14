"""crt_tv form ``bracket``, planned in pure Python: a 1997 bar TV up on a
wall bracket.

WHY A FORM. The walker's local comparison has "several TVs" over its bars,
and in 1997 a bar TV is a tube set strapped to a black steel shelf on an
arm off the wall, tipped down toward the stools. `crt_tv` could only stand
on a surface. ``form`` ``stand`` (and ``auto``, the default) is the recipe's
own box set, untouched; ``bracket`` is this.

The slot holds the set and its bracket: the wall is the slot's +Y face,
the screen faces -Y. A wall plate, an arm under the shelf with a brace up
to the plate, the shelf with a front lip, and the set on it -- a bezel box
with a bulged screen and two knobs, and the tapered tube housing behind --
all tipped TILT_DEG about the arm's front edge. The screen is LIT: a set
over a bar is on. It is an emissive key (`recipes/crt_tv.py` names it
``M_CRT_Screen_Face`` so Lux's power cut turns it off).

THE RULES the interior species keep: extents exactly w x d x h (the tip
changes the bounds, so `prims.fit_exact` ends the plan, within a percent);
parts that meet overlap by a few mm; no two faces within 2 mm of one plane
where they overlap. Frame: metres, Z up, base-up, front -Y.
"""
from __future__ import annotations

import math

from . import prims as P

FORMS = ("stand", "bracket")
BRACKET_D = 0.14          # the plate and the arm behind the set
TILT_DEG = 8.0
#: THE HOUSING IS NOT `plastic` ON PURPOSE. delco_1997's plastic pack
#: (`plastic_delco`) is a red-orange that is not tintable, so a black set
#: built as plastic rendered as a red box -- seen in the first contact sheet.
#: Painted metal is tintable and a matte near-black reads as a black cabinet
#: at any distance a bar TV is seen from.
MATERIALS = {
    "bracket": ([0.03, 0.03, 0.03], "metal_painted"),
    "housing": ([0.035, 0.035, 0.04], "metal_painted"),
    "knob": ([0.10, 0.10, 0.10], "metal_painted"),
}
#: a set that is on, showing a dim blue picture. REFUTED TWICE, both by
#: frames: (0.32, 0.42, 0.55) at 1.2 rendered as a blank white-blue panel in
#: Cycles, and (0.10, 0.17, 0.26) at 1.0 as a pale panel in the Godot walk's
#: dark basement, where it read as a flat screen
SCREEN_EMISSIVE = ([0.10, 0.17, 0.26], 0.35)


def pick_form(form):
    return form if form in FORMS else "stand"


def plan_bracket(w, d, h):
    """``{"prims", "collision", "screen_centre", "overshoot_m"}``.

    THE TIP MOVES THE BOUNDS, so the set is drawn at design sizes that are
    corrected four times against the tipped bounds before the fit. REFUTED
    FIRST: drawing at the slot's sizes and letting `fit_exact` take the
    difference, which measured 24 to 60 mm over the slot and squeezed the
    set 10 % in height."""
    ww, dd, hh, oz = w, d, h, 0.0
    for _ in range(4):
        prims, screen_centre = _bracket(ww, dd, hh)
        lo, hi = P.bounds(prims)
        ww += w - (hi[0] - lo[0])
        dd += d - (hi[1] - lo[1])
        hh += h - (hi[2] - lo[2])
    prims, screen_centre = _bracket(ww, dd, hh)
    lo, hi = P.bounds(prims)
    shift = (-(lo[0] + hi[0]) / 2, -d / 2 - lo[1], -lo[2])
    prims = [P.translate(p, shift) for p in prims]
    del oz
    cboxes = [((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h))]
    over = _over(prims, w, d, h)
    screen_centre = tuple(screen_centre[k] + shift[k] for k in range(3))
    prims, cboxes = P.fit_exact(prims, (-w / 2, -d / 2, 0.0), (w / 2, d / 2, h), cboxes)
    return {"prims": prims, "collision": cboxes, "screen_centre": screen_centre,
            "overshoot_m": over}


def _bracket(w, d, h):
    tv_d = max(0.2, d - BRACKET_D)
    shelf_t = 0.016
    drop = max(0.06, min(0.10, 0.2 * h))  # the arm and brace below the shelf
    z_s = drop                            # shelf top
    tv_h = h - z_s
    y0 = -d / 2                           # the set's front
    y_wall = d / 2
    prims = []
    # the set: bezel box, tapered housing, bulged screen, knobs
    bez_d = 0.55 * tv_d
    prims.append(P.box("CRT_Body", "housing", (-w / 2, y0, z_s - 0.003),
                       (w / 2, y0 + bez_d, z_s + tv_h)))
    yb0, yb1 = y0 + bez_d - 0.01, y0 + tv_d
    a, b = 0.40 * w, 0.24 * w
    zc = z_s + 0.5 * tv_h
    za0, za1 = z_s + 0.03, z_s + 0.92 * tv_h
    zb0, zb1 = zc - 0.26 * tv_h, zc + 0.30 * tv_h
    hv = [(-a, yb0, za0), (a, yb0, za0), (a, yb0, za1), (-a, yb0, za1),
          (-b, yb1, zb0), (b, yb1, zb0), (b, yb1, zb1), (-b, yb1, zb1)]
    hf = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    prims.append(P.mesh("CRT_Body", "housing", hv, hf))
    # a tube set's glass sits inside a deep bezel (0.78 x 0.66 first read as
    # a flat panel)
    sw, sh = 0.70 * w, 0.60 * tv_h
    scz = z_s + 0.56 * tv_h
    prims.append(P.box("CRT_Screen", "screen", (-sw / 2, y0 - 0.008, scz - sh / 2),
                       (sw / 2, y0 + 0.012, scz + sh / 2)))
    # two knobs in the bezel beside the screen, 16 mm proud
    kx = sw / 2 + (w / 2 - sw / 2) / 2
    kr = min(0.012, 0.3 * (w / 2 - sw / 2))
    for kz in (scz - 0.25 * sh, scz - 0.02 * sh):
        prims.append(P.rod("CRT_Knob", "knob", (kx, y0 + 0.006, kz), (kx, y0 - 0.016, kz), kr,
                           segments=8))
    # the shelf and its lip
    sx = w / 2 - 0.02
    prims.append(P.box("CRT_Bracket", "bracket", (-sx, y0 + 0.03, z_s - shelf_t),
                       (sx, y0 + tv_d - 0.02, z_s)))
    prims.append(P.box("CRT_Bracket", "bracket", (-sx + 0.004, y0 - 0.014, z_s - shelf_t - 0.004),
                       (sx - 0.004, y0 + 0.034, z_s + 0.045)))
    # tip the set, shelf and lip down toward the room about the arm's front
    hinge = (y0 + tv_d - 0.02, z_s - shelf_t)
    tilt = math.radians(TILT_DEG)          # front edge down
    prims = [P.rotate_x(p, tilt, hinge) for p in prims]
    # the arm, brace and wall plate stay square to the wall
    # the arm's bottom 9 mm or more off the plate's: at a 0.3 m set it had
    # sat 1 mm under it, one SAME pair
    prims.append(P.box("CRT_Bracket", "bracket", (-0.025, y0 + tv_d - 0.20, z_s - shelf_t - 0.035),
                       (0.025, y_wall - 0.008, z_s - shelf_t - 0.008)))
    prims.append(P.box("CRT_Bracket", "bracket", (-0.09, y_wall - 0.012, 0.0),
                       (0.09, y_wall, z_s + 0.16)))
    prims.append(P.rod("CRT_Bracket", "bracket", (0.0, y_wall - 0.006, 0.012),
                       (0.0, y0 + tv_d - 0.12, z_s - shelf_t - 0.03), 0.011, segments=8))
    c = P.rotate_x({"verts": [(0.0, y0, scz)], "faces": [], "part": "", "mat": ""}, tilt, hinge)
    return prims, c["verts"][0]


def _over(prims, w, d, h):
    lo, hi = P.bounds(prims)
    return max(abs(lo[0] + w / 2), abs(hi[0] - w / 2), abs(lo[1] + d / 2),
               abs(hi[1] - d / 2), abs(lo[2]), abs(hi[2] - h))
