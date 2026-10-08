"""The getaway van's numbers and its finish, pure (Zoo 1.82.0, roadmap 206).

`recipes/step_van.py` builds the crew's van; everything here is the part of
it that needs no Blender, so the suite can test it: where each part stands
for a given slot (`layout`) and what colour the paint is at a given point
(`finish_rgb`). The recipe imports bpy; this module must not.

The walker, 2026-10-07: "a Box Truck. Like a Chevrolet P30. Matte
Black....faded, with patina, like a worn in truck...that's been on many
jobs" -- parked at the mission's spawn. The comps, read for format only:
docs/reference/GETAWAY_VAN_COMPS.md at the factory root.

FRAME AND UNITS. Recipe space before `build.build_module` re-centres it:
metres, X across (the passenger side, the kerb side, at -X), Y along (the
nose at -Y), Z up from the ground at 0.
"""
from __future__ import annotations

import math

#: The mirror heads stand this far outside the body's side: the slot's width
#: is the heads' outer faces, the body is the slot less twice this.
MIRROR_OUT = 0.15
#: The amber clearance lamps on the cab roof's front edge stand this tall;
#: the slot's height is their tops, the roof is the slot less this.
ROOF_LAMP = 0.05
#: The bumpers stand this far ahead of the nose and behind the rear doors.
BUMPER_FWD = 0.10
BUMPER_BACK = 0.12
#: Cab: from the grille face to the windshield's base, the windshield's rake
#: (its top stands this far behind its base), and the windshield base to the
#: bulkhead. A P30's front overhang (bumper to front axle) is about 0.8-0.9 m
#: and its cab about 1.4-1.5 m.
NOSE_LEN = 0.62
WS_RAKE = 0.16
CAB_LEN = 1.45
#: The front axle sits just behind the windshield's base, under the dash.
FRONT_AXLE_BEHIND_WS = 0.10
#: The rear axle's distance ahead of the rear doors, at the default 6.8 m.
REAR_AXLE_AHEAD = 1.55
#: Roof edge radius (box and cab roof alike, so the two read as one roof).
ROOF_ROUND = 0.09
#: Headliner: the cab roof slab's thickness under the roof.
CAB_ROOF_T = 0.10
#: How far the cab's lower body stands inside the box's side: the seam a
#: P30's cab makes against its body, and the gap that keeps two solids off
#: one plane.
CAB_INSET = 0.004
#: How far the cab roof stands inside the box's side and above its roof.
#: DERIVED, not chosen: the roof edge is a 3-segment arc, so its facets face
#: 15, 45 and 75 degrees between the side (0) and the top (90), and the two
#: roofs' facets must stay at least 2 mm apart (tools/coplanar_probe.py's
#: window) along EVERY one of those normals. The first draft shifted the cab
#: roof by (-4, +4) mm -- exactly along the 45-degree facet -- and the probe
#: read two 20.47 cm2 SAME pairs there. A 12 mm shift at 120 degrees clears
#: all five: 6.0, 3.1, 3.1, 8.5 and 10.4 mm.
CAB_ROOF_INSET = 0.006
CAB_ROOF_RISE = 0.0104

#: The paint, from deep to chalked. Near-black where the sun did not reach,
#: chalked toward a warm charcoal on the roof and the upper panels. BASE is
#: the genome's style colour, and the recipe passes the PLAN's colour in, so
#: editing the genome repaints the van (a knob the recipe ignored would be
#: the inert-genome defect tests/test_material_options_closed.py names).
#: The chalk derives from the base rather than standing beside it: full sun
#: takes paint `CHALK_T` of the way to `SUN_BLEACH`, the warm pale grey
#: oxidised paint goes. At the default base that is (0.100, 0.096, 0.092),
#: the chalk the frames were judged at; a red van would chalk toward a
#: faded red, not toward charcoal.
BASE = (0.030, 0.030, 0.033)
SUN_BLEACH = (0.310, 0.294, 0.269)
CHALK_T = 0.25
DUST = (0.190, 0.175, 0.150)
RUST = (0.215, 0.085, 0.040)
PRIMER = (0.330, 0.328, 0.312)
#: How the sun's chalk climbs a side panel: black first, faded second. The
#: first draft chalked the sides linearly toward the roof (0.18 + 0.82 *
#: up^1.4) and read as a cloudy mid-grey van in its first frame -- the walker
#: asked for "Matte Black....faded", in that order.
SIDE_SUN = (0.08, 0.62, 1.8)          # floor, gain, exponent: f = floor + gain * up^exp
ROOF_SUN = 0.70                       # the roof and hood, which the sun hits square


def _clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def layout(W, L, H):
    """Where every part of a van built to a W x L x H slot stands.

    Pure. Every number derives from the slot and the module constants above,
    so a longer slot is a longer box behind the same cab, not a stretched cab.
    """
    hw = W / 2.0 - MIRROR_OUT
    z_roof = H - ROOF_LAMP
    r = _clamp(0.41 * H / 3.05, 0.36, 0.44)          # wheel radius
    z_sill = round(r * 1.5, 4)                        # body bottom between arches
    z_belt = round(z_roof * 0.475, 4)                 # windshield and side-glass base
    z_nose = round(z_belt - 0.32, 4)                  # the hood's front edge
    y0, yt = -L / 2.0, L / 2.0                        # bumper outer faces
    y_n = y0 + BUMPER_FWD                             # the grille face
    y_r = yt - BUMPER_BACK                            # the rear doors' face
    y_ws = y_n + NOSE_LEN                             # windshield base
    y_wt = y_ws + WS_RAKE                             # windshield top
    y_cab = y_ws + CAB_LEN                            # bulkhead
    ya_f = y_ws + FRONT_AXLE_BEHIND_WS
    ya_r = y_r - REAR_AXLE_AHEAD * (L / 6.8)
    arch = r + 0.11                                   # arch half-length along Y
    z_arch = 2.0 * r + 0.07                           # arch top
    tyre_w = 0.24
    return {
        "W": W, "L": L, "H": H, "hw": hw, "r": r, "tyre_w": tyre_w,
        "z_roof": z_roof, "z_sill": z_sill, "z_belt": z_belt, "z_nose": z_nose,
        "y0": y0, "yt": yt, "y_n": y_n, "y_r": y_r, "y_ws": y_ws, "y_wt": y_wt,
        "y_cab": y_cab, "ya_f": ya_f, "ya_r": ya_r, "arch": arch, "z_arch": z_arch,
        # the door the crew uses, on the kerb side (-X): behind the front arch
        # to the bulkhead
        "y_door0": ya_f + arch + 0.04, "y_door1": y_cab - 0.05,
        # one filled dent, grey primer, on the kerb side's rear quarter: the
        # side the crew walks up to every time
        "primer": (-1.0, y_r - 0.95, 1.20, 0.30),
    }


def axle_height(r, seg):
    """The axle's height that sets a ``seg``-sided tyre of tread radius ``r``
    on the ground. A lathe puts a vertex every 360/seg degrees from the
    axle's level, so one points straight down only when seg is a multiple of
    4; otherwise the lowest stands at r * cos(180/seg) and an axle at r
    floats the van. Measured on the first build at the default 14: 3.040 m
    tall in its 3.05 m slot, 10.3 mm off the ground."""
    return -r * min(math.sin(2.0 * math.pi * k / seg) for k in range(seg))


def _hash(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFF) / float(0xFFFFFF)


def vnoise(x, y, seed=0):
    """Smooth value noise in [0, 1]: deterministic from position alone, so
    the crew's van is the same van in every level and every build."""
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = x - ix, y - iy
    sx, sy = fx * fx * (3.0 - 2.0 * fx), fy * fy * (3.0 - 2.0 * fy)
    a, b = _hash(ix, iy, seed), _hash(ix + 1, iy, seed)
    c, d = _hash(ix, iy + 1, seed), _hash(ix + 1, iy + 1, seed)
    return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy


def _lerp3(a, b, t):
    return tuple(a[k] + (b[k] - a[k]) * t for k in range(3))


def chalk(base):
    """The colour ``base`` paint fades to in full sun."""
    return _lerp3(base, SUN_BLEACH, CHALK_T)


def _seg_dist(py, pz, ay, az, by, bz):
    dy, dz = by - ay, bz - az
    t = _clamp(((py - ay) * dy + (pz - az) * dz) / max(1e-12, dy * dy + dz * dz))
    return math.hypot(py - (ay + t * dy), pz - (az + t * dz))


def arch_distance(y, z, ya, lay):
    """Distance in the side plane from (y, z) to the rim of the arch over the
    axle at ``ya``: its top edge and its two sides down to the sill."""
    A, za, zs = lay["arch"], lay["z_arch"], lay["z_sill"]
    return min(_seg_dist(y, z, ya - A, za, ya + A, za),
               _seg_dist(y, z, ya - A, 0.0, ya - A, za),
               _seg_dist(y, z, ya + A, 0.0, ya + A, za))


def finish_rgb(co, normal, lay, base=BASE):
    """The paint's colour at a point of the body, before the wear darkening
    Zoo multiplies in: the van's history, in four layers over ``base``, the
    plan's colour.

      * SUN: near-black low down and in the shade, chalked toward a warm
        charcoal on the roof, the hood and the upper panels, mottled the way
        oxidised paint goes.
      * DUST: road dust on the lower third, thicker toward the ground.
      * RUST: bloom around each arch and along the rocker, on the sides only.
      * PRIMER: one filled dent in grey primer on the kerb side.
    """
    x, y, z = co
    nx, ny, nz = normal
    zr = lay["z_roof"]
    up = _clamp((z - 0.55) / max(1e-6, zr - 0.55))
    roof = _clamp((nz - 0.55) / 0.45)
    floor, gain, ex = SIDE_SUN
    sun = max(floor + gain * up ** ex, ROOF_SUN * roof)
    mott = 0.78 + 0.44 * vnoise(y * 0.85 + 11.0, z * 1.6 + (3.0 if x > 0 else 0.0), 1)
    c = _lerp3(base, chalk(base), _clamp(sun * mott))
    dust = _clamp((0.95 - z) / 0.45) * (0.45 + 0.55 * vnoise(y * 2.3, z * 3.1 + 7.0, 2))
    c = _lerp3(c, DUST, 0.60 * dust)
    side = _clamp((abs(nx) - 0.5) / 0.5)
    if side > 0.0 and z < 1.35:
        d = min(arch_distance(y, z, lay["ya_f"], lay), arch_distance(y, z, lay["ya_r"], lay),
                max(0.0, z - lay["z_sill"]) * 2.0)
        n = vnoise(y * 4.0 + 5.0, z * 5.0, 3)
        rust = _clamp(1.0 - d / 0.15) * _clamp((n - 0.38) / 0.40)
        c = _lerp3(c, RUST, 0.85 * rust * side)
    px, py, pz, prad = lay["primer"]
    if x * px > 0.0 and side > 0.0:
        # an irregular edge: a filled dent sanded by hand, not a stencil (the
        # first frame's smooth ellipse read as a pasted grey rectangle)
        e = ((y - py) / prad) ** 2 + ((z - pz) / (prad * 0.7)) ** 2
        e += 0.45 * (vnoise(y * 6.0 + 2.0, z * 6.0 + 9.0, 4) - 0.5)
        c = _lerp3(c, PRIMER, 0.60 * _clamp((1.0 - e) / 0.25) * side)
    return c
