"""crt_tv forms, planned in pure Python: a 1997 bar TV up on a wall bracket
(``bracket``) and the set standing on its feet (``stand``).

WHY A FORM. The walker's local comparison has "several TVs" over its bars,
and in 1997 a bar TV is a tube set strapped to a black steel shelf on an
arm off the wall, tipped down toward the stools. `crt_tv` could only stand
on a surface. ``form`` ``stand`` (and ``auto``, the default) is the recipe's
own box set; ``bracket`` is this.

The slot holds the set and its bracket: the wall is the slot's +Y face,
the screen faces -Y. A wall plate, an arm under the shelf with a brace up
to the plate, the shelf with a front lip, and the set on it -- a bezel box
with a curved 4:3 screen and two knobs, and the tapered tube housing behind
-- all tipped TILT_DEG about the arm's front edge.

THE SCREEN IS ON (0.90.0). The walker, after cold run 9057's club: the CRTs
should "have a light/glow from the screen as if they are on", showing "a
football or baseball game", no clear image needed. The face is a grid bulged
toward the room with its corners sunk behind the bezel, so the bezel cuts it
to a tube's rounded outline, and it carries a ballgame painted by
`core.crt_screens` as a backlit texture (`recipes/crt_tv.py` names it
``M_CRT_Screen_<art>_Face`` so Lux's power cut turns it off). Which game is
the module's variant (`crt_screens.pick_game`).

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
#: 0.88.0 - 0.89.0, a flat emissive colour, kept: a set that is on, showing a
#: dim blue picture. REFUTED THREE TIMES, all by frames: (0.32, 0.42, 0.55) at
#: 1.2 rendered as a blank white-blue panel in Cycles, (0.10, 0.17, 0.26) at
#: 1.0 as a pale panel in the Godot walk's dark basement, where it read as a
#: flat screen, and at 0.35 -- what shipped -- the walker read the set as OFF.
#: A colour with no picture in it reads as either a lamp or a dead tube.
SCREEN_EMISSIVE_0_89 = ([0.10, 0.17, 0.26], 0.35)
#: The picture's glow and its dimmed diffuse copy (`materials.
#: make_backlit_material`, the vending panel's 0.35 albedo).
#:
#: MEASURED, not chosen, the way 0.87.0 measured the vending panel: the two
#: TV modules of `strip_club_a01` (the kit stems cold run 9057 built) rebuilt
#: at each strength and swapped into two scratch copies of that run's walk --
#: Heavy Rain as it shipped, and the same copy on delco_summer_afternoon --
#: Godot 4.7 gl_compatibility, RTX 2060, `tools/look_shots.py` 1600 x 900, a
#: camera 2 m in front of each of the club's three sets. Screen pixels are
#: those that brighten by more than 8 codes from strength 0 to 1 (9,727 -
#: 11,674 a set); "pinned" is any channel >= 250, "white" all >= 235; 8-bit
#: sRGB after tonemap and Lux post, Rec.709 luma, the three sets' range.
#:
#:                  strength    0      0.5     1.0     1.5     2.0     3.0
#:   rain   luma            12-59  51-80   70-93  103-119 130-142 169-177
#:          saturation      .46-.90 .40-.52 .37-.45 .33-.38 .30-.33 .24-.25
#:          pinned %           0      0       0       0       0    .06-.11
#:          white %            0      0       0       0     0-.01  .86-1.43
#:   summer luma            14-66  62-92  84-108 121-138 150-163 191-200
#:          pinned %           0      0       0       0    .10-.69 11.2-17.3
#:          white %            0      0       0     0-.05  .45-.88 5.4-7.6
#:
#: 1.5 is the highest strength with no pinned pixel in either preset: under
#: Heavy Rain 2.0 to 8.6 x the unlit screen's luma. Its 0.05 % white under the
#: summer sun is the score bug's type. The picture's own saturation is 0.41 -
#: 0.47 in the PNG. KEPT, the stricter reading: 1.0 is the highest with neither
#: pinned NOR white anywhere (the vending panel's rule), at 70 - 93 luma in the
#: rain, and was the first value; frames of both are in the CHANGELOG.
SCREEN_EMISSION = 1.5
SCREEN_ALBEDO = 0.35
#: The face's grid, columns x rows: enough for the bulge to read as a curve
#: under smooth shading, 48 quads.
SCREEN_GRID = (8, 6)
#: The face bulges this far in front of its corners' plane at the centre...
SCREEN_BULGE = 0.014
#: ...and its corners sit this far BEHIND the bezel's face, so the bezel cuts
#: the outline round. Also clear of the 2 mm coplanar window.
SCREEN_SINK = 0.004
#: The screen's back, behind the bezel's face, inside the body.
SCREEN_BACK = 0.012

# --- the stand set -------------------------------------------------------------------
#
# MEASURED on 0.86.0 - 0.89.0, kept: the stand set drew its body the slot's full
# depth, hung two knobs 22 mm in front of it (built 0.522 m for a 0.500 m slot,
# failing `fit_depth` on the kit path at every size) and put its screen box
# from 10 to 30 mm BEHIND the body's front face, where nothing could see it.
# Now the body's front stands STAND_FRONT_SET inside the slot, the knobs fill
# exactly that depth to the slot's front, and the glass stands proud of the
# body's face.
STAND_FOOT_H = 0.02
STAND_FRONT_SET = 0.018
STAND_KNOB_R = 0.016
#: A knob is buried this far into the body, past the 2 mm coplanar window.
STAND_BURY = 0.006
STAND_SCREEN_PROUD = 0.010
STAND_SCREEN_DEPTH = 0.030


def pick_form(form):
    return form if form in FORMS else "stand"


def screen_size(w, tv_h):
    """(width, height) of a 4:3 face on a set ``w`` wide with a ``tv_h`` tall
    front: at most 70 % of the front's height and 70 % of its width, the
    other axis following, so the knobs keep a column beside it."""
    sh = min(0.70 * tv_h, 0.75 * 0.70 * w)
    return sh * 4.0 / 3.0, sh


def screen_prim(sw, sh, y_face, zc, xc=0.0, part="CRT_Screen", mat="screen"):
    """The curved face as one closed primitive: a front grid bulged toward
    -Y (``SCREEN_BULGE`` at the centre, corners ``SCREEN_SINK`` behind
    ``y_face``), a flat back grid ``SCREEN_BACK`` behind ``y_face``, and the
    four side strips. Carries ``uvs``, one (u, v) per face corner, parallel
    to ``faces``: the front grid maps the picture edge to edge (v up), every
    other face samples the picture's top-left pixel, which the vignette has
    made its darkest."""
    nu, nv = SCREEN_GRID
    yb = y_face + SCREEN_BACK
    verts, faces, uvs = [], [], []
    for j in range(nv + 1):
        v = -1.0 + 2.0 * j / nv
        for i in range(nu + 1):
            u = -1.0 + 2.0 * i / nu
            y = y_face + SCREEN_SINK - (SCREEN_BULGE + SCREEN_SINK) * (1.0 - (u * u + v * v) / 2.0)
            verts.append((xc + u * sw / 2.0, y, zc + v * sh / 2.0))
    back0 = len(verts)
    for j in range(nv + 1):
        for i in range(nu + 1):
            verts.append((xc + (-1.0 + 2.0 * i / nu) * sw / 2.0, yb,
                          zc + (-1.0 + 2.0 * j / nv) * sh / 2.0))

    def f(i, j):
        return j * (nu + 1) + i

    def b(i, j):
        return back0 + f(i, j)

    dark = (0.5 / 224.0, 1.0 - 0.5 / 168.0)
    for j in range(nv):
        for i in range(nu):
            faces.append((f(i, j), f(i + 1, j), f(i + 1, j + 1), f(i, j + 1)))
            uvs.append(((i / nu, j / nv), ((i + 1) / nu, j / nv),
                        ((i + 1) / nu, (j + 1) / nv), (i / nu, (j + 1) / nv)))
            faces.append((b(i, j), b(i, j + 1), b(i + 1, j + 1), b(i + 1, j)))
            uvs.append((dark,) * 4)
    for i in range(nu):
        faces.append((f(i, 0), b(i, 0), b(i + 1, 0), f(i + 1, 0)))          # bottom, -Z
        faces.append((f(i, nv), f(i + 1, nv), b(i + 1, nv), b(i, nv)))     # top, +Z
        uvs += [(dark,) * 4, (dark,) * 4]
    for j in range(nv):
        faces.append((f(0, j), f(0, j + 1), b(0, j + 1), b(0, j)))          # left, -X
        faces.append((f(nu, j), b(nu, j), b(nu, j + 1), f(nu, j + 1)))      # right, +X
        uvs += [(dark,) * 4, (dark,) * 4]
    p = P.mesh(part, mat, verts, faces)
    p["uvs"] = uvs
    return p


def plan_bracket(w, d, h):
    """``{"prims", "collision", "screen_centre", "screen_m", "overshoot_m"}``.

    THE TIP MOVES THE BOUNDS, so the set is drawn at design sizes that are
    corrected four times against the tipped bounds before the fit. REFUTED
    FIRST: drawing at the slot's sizes and letting `fit_exact` take the
    difference, which measured 24 to 60 mm over the slot and squeezed the
    set 10 % in height."""
    ww, dd, hh = w, d, h
    for _ in range(4):
        prims, screen_centre, _sm = _bracket(ww, dd, hh)
        lo, hi = P.bounds(prims)
        ww += w - (hi[0] - lo[0])
        dd += d - (hi[1] - lo[1])
        hh += h - (hi[2] - lo[2])
    prims, screen_centre, screen_m = _bracket(ww, dd, hh)
    lo, hi = P.bounds(prims)
    shift = (-(lo[0] + hi[0]) / 2, -d / 2 - lo[1], -lo[2])
    prims = [P.translate(p, shift) for p in prims]
    cboxes = [((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h))]
    over = _over(prims, w, d, h)
    screen_centre = tuple(screen_centre[k] + shift[k] for k in range(3))
    prims, cboxes = P.fit_exact(prims, (-w / 2, -d / 2, 0.0), (w / 2, d / 2, h), cboxes)
    return {"prims": prims, "collision": cboxes, "screen_centre": screen_centre,
            "screen_m": screen_m, "overshoot_m": over}


def _bracket(w, d, h):
    tv_d = max(0.2, d - BRACKET_D)
    shelf_t = 0.016
    drop = max(0.06, min(0.10, 0.2 * h))  # the arm and brace below the shelf
    z_s = drop                            # shelf top
    tv_h = h - z_s
    y0 = -d / 2                           # the set's front
    y_wall = d / 2
    prims = []
    # the set: bezel box, tapered housing, curved screen, knobs
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
    # a tube set's glass sits in a deep bezel (0.78 x 0.66 first read as a
    # flat panel); 0.90.0 makes it 4:3 and curved (`screen_size`)
    sw, sh = screen_size(w, tv_h)
    scz = z_s + 0.56 * tv_h
    prims.append(screen_prim(sw, sh, y0, scz))
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
    c = P.rotate_x({"verts": [(0.0, y0 - SCREEN_BULGE, scz)], "faces": [], "part": "", "mat": ""},
                   tilt, hinge)
    return prims, c["verts"][0], (sw, sh)


def _over(prims, w, d, h):
    lo, hi = P.bounds(prims)
    return max(abs(lo[0] + w / 2), abs(hi[0] - w / 2), abs(lo[1] + d / 2),
               abs(hi[1] - d / 2), abs(lo[2]), abs(hi[2] - h))


def stand_layout(w, d, h, knobs=2):
    """The stand set's parts as ``{name: [(centre, size), ...]}`` boxes and
    ``knobs`` as ``[(centre, radius, depth)]`` cylinders along Y, in the
    recipe's frame (base-up, front -Y). Exact to the slot on every axis: the
    knob caps are the slot's front plane, the body's back its back."""
    yb = -d / 2.0 + STAND_FRONT_SET          # the body's front face
    body_h = h - STAND_FOOT_H
    out = {
        "body": [((0.0, (yb + d / 2.0) / 2.0, STAND_FOOT_H + body_h / 2.0),
                  (w, d / 2.0 - yb, body_h))],
        "screen": [((0.0, yb - STAND_SCREEN_PROUD + STAND_SCREEN_DEPTH / 2.0,
                     STAND_FOOT_H + body_h * 0.56),
                    (w * 0.80, STAND_SCREEN_DEPTH, body_h * 0.64))],
        "feet": [((sx * w * 0.34, 0.0, (STAND_FOOT_H + STAND_BURY) / 2.0),
                  (w * 0.14, d * 0.5, STAND_FOOT_H + STAND_BURY)) for sx in (-1, 1)],
    }
    kd = STAND_FRONT_SET + STAND_BURY
    out["knobs"] = [((w * 0.30 - i * 0.05, -d / 2.0 + kd / 2.0, STAND_FOOT_H + body_h * 0.16),
                     STAND_KNOB_R, kd) for i in range(min(int(knobs), 4))]
    out["screen_centre"] = (0.0, yb - STAND_SCREEN_PROUD, STAND_FOOT_H + body_h * 0.56)
    return out
