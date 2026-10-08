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
#: THE HEADER (1.83.0): the painted band between the glass's top and the
#: roof, across the windshield and the cab's sides. The walker, 2026-10-08,
#: on 1.82.0's frames: "the windows in the front feel proportionally a little
#: too tall ... a little more of the non window part to take a little more of
#: the top bit". 1.82.0's 0.10 ran the glass almost to the roof; the P30 comp
#: carries about 0.25-0.30 m of body above its windshield.
HEADER = 0.28
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
        "z_head": z_roof - HEADER,                    # the glass's top, under the header
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


# --- the chassis (1.83.0) ------------------------------------------------------------

#: THE CHASSIS. The walker, 2026-10-08, with an underside comp: "flesh out the
#: bottom of the truck a bit...like giving it a driveshaft and rear
#: differential". 1.82.0 had nothing under the body: a person on the sidewalk
#: saw the street straight through the 0.6 m between the body and the ground.
#: What a step van carries there, every part running into what it meets: two
#: frame rails, four crossmembers, leaf springs at both axles, a front beam
#: axle, the rear axle housing with the differential in its middle, the
#: engine's sump and the transmission under the cab, the driveshaft between
#: them, an exhaust with its muffler out to the road side ahead of the rear
#: wheels, and the fuel tank on the kerb side.
RAIL_X = 0.47            # a frame rail's centre line, either side of the middle
RAIL_W = 0.07
#: A rail's bottom over the axle's centre: the axle's half-height and a
#: leaf spring between them (see `chassis`, WHAT HANGS FROM WHAT).
RAIL_ON_AXLE = 0.11
SPRING_HALF = (0.62, 0.70)   # half a leaf spring's length: front, rear
SHAFT_R = 0.045
PIPE_R = 0.035
#: The chassis's finish: black-painted steel under road grime, and the
#: exhaust's rust. No sun reaches under a van, so neither chalks.
CHASSIS = (0.032, 0.031, 0.030)
GRIME = (0.105, 0.095, 0.082)
EXHAUST = (0.150, 0.075, 0.040)


def _xbox(s, x0, x1, y0, y1, z0, z1):
    """A box on the side ``s`` (+1 or -1) of the middle, from ``x0`` to
    ``x1`` out from it: ``(lo, hi)``."""
    a, b = sorted((s * x0, s * x1))
    return ((a, y0, z0), (b, y1, z1))


def chassis(lay, za):
    """Every part under the body as `core.prims` primitives -- a box, or a
    rod for anything round -- each named in ``part`` ("rail_kerb",
    "differential", ...) with ``mat`` "frame" or "exhaust", which says how it
    is painted (`chassis_rgb`). ``za`` is the axles' height (`axle_height`).
    Pure: the recipe draws these and adds nothing of its own, so
    `prims.coincident_pairs` over them is the probe's own measurement.

    WHAT HANGS FROM WHAT. The rails stand on the springs and the springs on
    the axles, so a rail's bottom is the axle's height plus a spring, not the
    body's floor less a drop: the floor (`z_sill`, 1.5 r) and the axle (about
    0.975 r) part as the slot's height moves the wheel's radius, and a rail
    hung from the floor met the front beam's top within 1.8 mm around a
    3.0 m slot. The driveshaft and the exhaust hang from the axle for the
    same reason; what reaches up into the body (rail tops, crossmembers, the
    engine, the tank) runs from the floor."""
    from . import prims as P
    hw, zs, tw = lay["hw"], lay["z_sill"], lay["tyre_w"]
    y0, yt, y_n, y_r = lay["y0"], lay["yt"], lay["y_n"], lay["y_r"]
    y_cab, ya_f, ya_r, A = lay["y_cab"], lay["ya_f"], lay["ya_r"], lay["arch"]
    x_disc = (hw - 0.03) - tw + 0.03          # an outer wheel's steel disc, its back face
    out = []

    def box(mat, part, lo_hi):
        out.append(P.box(part, mat, lo_hi[0], lo_hi[1]))

    def rod(mat, part, p0, p1, radius, sides):
        # turned half a facet's half-angle, so no facet lies square to an
        # axis: at 0 every level 6- and 10-sided pipe had a flat top and
        # bottom, and the exhaust's elbows shared them (`prims.rod`)
        out.append(P.rod(part, mat, p0, p1, radius, segments=sides, phase=math.pi / (2 * sides)))

    r0, r1 = RAIL_X - RAIL_W / 2.0, RAIL_X + RAIL_W / 2.0
    z_rb, z_rt = za + RAIL_ON_AXLE, zs + 0.02     # a rail's bottom on the springs, its top in the body
    for s, side in ((-1.0, "kerb"), (1.0, "road")):
        # the rails run into both bumpers
        box("frame", "rail_" + side, _xbox(s, r0, r1, y0 + 0.06, yt - 0.06, z_rb, z_rt))
        # leaf springs under the rails, narrower than them so no side is
        # shared, through the axle below and into the rail above
        for end, ya, half, z_bot in (("front", ya_f, SPRING_HALF[0], za + 0.02),
                                     ("rear", ya_r, SPRING_HALF[1], za + 0.03)):
            box("frame", "spring_%s_%s" % (end, side),
                _xbox(s, RAIL_X - 0.025, RAIL_X + 0.025, ya - half, ya + half, z_bot, z_rb + 0.012))
    # crossmembers: their ends inside the rails, their tops 10 mm under the
    # rails' (two tops on one plane are a shared face). The cab's sits 0.12
    # behind the bulkhead: at 0.10 its front face lay on the cab body's rear
    # cap, y_cab + 0.06, back to back at 0 mm.
    for name, yc in (("cross_front", y_n + 0.30), ("cross_cab", y_cab + 0.12),
                     ("cross_axle", ya_r + A + 0.25), ("cross_tail", y_r - 0.25)):
        box("frame", name, ((-(r0 + 0.015), yc - 0.04, zs - 0.045), (r0 + 0.015, yc + 0.04, zs + 0.01)))
    # the front beam axle, through the tyres' hollows into the steel discs
    box("frame", "front_axle", ((-(x_disc + 0.02), ya_f - 0.04, za - 0.05),
                                (x_disc + 0.02, ya_f + 0.04, za + 0.05)))
    # the engine's sump behind it, and the transmission running back under
    # the cab: its top 5 mm under the sump's and its bottom 20 mm over it, so
    # the two share no face (hung at zs - 0.20, its bottom came within 1.0 mm
    # of the sump's at the tallest slot)
    box("frame", "engine", ((-0.24, ya_f + 0.10, za + 0.03), (0.24, ya_f + 0.78, zs + 0.02)))
    y_tr = y_cab - 0.05
    box("frame", "transmission", ((-0.13, ya_f + 0.74, za + 0.05), (0.13, y_tr, zs + 0.015)))
    # the rear axle: its housing across into the discs, the differential's
    # pumpkin in the middle, its cover behind and the pinion's nose ahead
    rod("frame", "rear_axle", (-(x_disc + 0.02), ya_r, za), (x_disc + 0.02, ya_r, za), 0.06, 10)
    rod("frame", "differential", (0.0, ya_r - 0.12, za), (0.0, ya_r + 0.10, za), 0.17, 12)
    rod("frame", "diff_cover", (0.0, ya_r + 0.09, za), (0.0, ya_r + 0.14, za), 0.14, 12)
    rod("frame", "pinion", (0.0, ya_r - 0.27, za), (0.0, ya_r - 0.11, za), 0.07, 8)
    # the driveshaft: from inside the transmission to inside the pinion's
    # nose, a U-joint's yoke at each end -- the front one's bottom 5 mm under
    # the transmission's (from the body's floor it came within 0.3 mm of it)
    z_out = za + 0.10
    rod("frame", "driveshaft", (0.0, y_tr - 0.05, z_out), (0.0, ya_r - 0.22, za), SHAFT_R, 8)
    box("frame", "yoke_front", ((-0.055, y_tr - 0.02, z_out - 0.055), (0.055, y_tr + 0.06, z_out + 0.055)))
    box("frame", "yoke_rear", ((-0.055, ya_r - 0.31, za - 0.055), (0.055, ya_r - 0.24, za + 0.055)))
    # the exhaust: out of the engine's road side under the rail, behind the
    # front spring, back to the muffler and the tailpipe, and out under the
    # road side ahead of the rear wheels
    ze, xe = z_rb - 0.05, RAIL_X + 0.19
    y_bend = ya_f + SPRING_HALF[0] + 0.08
    y_tail = ya_r - A - 0.20
    rod("exhaust", "downpipe", (0.20, y_bend, ze), (xe + PIPE_R, y_bend, ze), PIPE_R, 6)
    rod("exhaust", "pipe", (xe, y_bend - PIPE_R, ze), (xe, y_cab + 0.27, ze), PIPE_R, 6)
    rod("exhaust", "muffler", (xe, y_cab + 0.25, ze), (xe, y_cab + 0.90, ze), 0.11, 10)
    rod("exhaust", "tailpipe", (xe, y_cab + 0.88, ze), (xe, y_tail + PIPE_R, ze), PIPE_R, 6)
    rod("exhaust", "tail_out", (xe - PIPE_R, y_tail, ze), (hw - 0.04, y_tail, ze), PIPE_R, 6)
    # the fuel tank outboard of the kerb-side rail behind the cab, on two
    # straps; its top inside the body
    tx0, tx1 = r1 + 0.03, r1 + 0.42
    ty0, ty1 = y_cab + 0.35, y_cab + 1.05
    tz0 = zs - 0.36
    box("frame", "fuel_tank", _xbox(-1.0, tx0, tx1, ty0, ty1, tz0, zs + 0.02))
    for k, yc in enumerate((ty0 + 0.15, ty1 - 0.15)):
        box("frame", "tank_strap_%d" % k, _xbox(-1.0, tx0 + 0.008, tx1 + 0.008,
                                                yc - 0.025, yc + 0.025, tz0 - 0.008, zs + 0.015))
    return out


def chassis_rgb(co, normal, part):
    """The colour of a chassis part at a point: grimy black steel, or the
    exhaust's rust under the same grime."""
    x, y, z = co
    n = vnoise(y * 2.7 + 21.0, z * 3.3 + x * 1.9, 6)
    if part == "exhaust":
        return _lerp3(EXHAUST, GRIME, 0.25 + 0.35 * n)
    return _lerp3(CHASSIS, GRIME, 0.30 + 0.50 * n)


# --- the ghost (1.83.0, variant 1) --------------------------------------------------

#: THE GHOST, variant 1 -- the walker's to judge (2026-10-08: "show me
#: this"). The van ran as a water-ice truck, SKEEVY'S WOODER ICE, its name in
#: vinyl. The crew peeled the vinyl off when they bought it, and the paint
#: under the letters never saw the sun: the old name stands in the chalked
#: side as deeper black, the way a removed decal ghosts on every faded van.
#: That is the finish's own physics (`finish_rgb` chalks what the sun hits),
#: so the letters are darker than the paint around them, never lighter. A
#: vinyl name is a shop's own hand (`smooth_type.OWNERS["shop"]`).
GHOST_LINES = (("SKEEVY'S", 0.42), ("WOODER ICE", 0.24),
               ("CHERRY - LEMON - BLUE RAZZ", 0.09), ("SH 7-6969", 0.11))
GHOST_GAPS = (0.12, 0.10, 0.14, 0.12)   # the space above each line, metres
GHOST_SPAN = (3.6, 1.8)                 # the art along and up the side, metres
GHOST_PX = (1024, 512)                  # the same pixels a metre both ways
GHOST_INK = 0.55                        # the linear factor under a letter, at its darkest
#: How much of a letter's darkening survives, between this and 1, by a
#: noise about `GHOST_PATCH_M` across: vinyl never fades evenly, and the
#: first frame's even letters read as lettering somebody painted, not as
#: one somebody peeled off (2026-10-08).
GHOST_PATCH = 0.30
GHOST_PATCH_M = 0.45
GHOST_TOP = 0.22                        # the art's top edge under the roof
#: Where a face that carries no lettering samples the art: past its corner,
#: which the clamped sampler reads as the white margin.
GHOST_OUTSIDE = (-0.5, -0.5)


def _srgb8(lin):
    c = 12.92 * lin if lin <= 0.0031308 else 1.055 * lin ** (1.0 / 2.4) - 0.055
    return int(round(255.0 * c))


def ghost_centre(lay):
    """The art's centre on the box's side: ``(y, z)``, recipe space."""
    return ((lay["y_cab"] + lay["y_r"]) / 2.0, lay["z_roof"] - GHOST_TOP - GHOST_SPAN[1] / 2.0)


def ghost_uv(co, normal, lay):
    """Where a body corner samples the ghost's art. A face looking along X
    -- the box's sides, its ribs, the cab's sides -- maps by its (y, z),
    read the right way round from outside on either side; any other face
    samples the white margin."""
    x, y, z = co
    nx = normal[0]
    if abs(nx) < 0.9:
        return GHOST_OUTSIDE
    yc, zc = ghost_centre(lay)
    sy, sz = GHOST_SPAN
    u = (y - yc) / sy if nx > 0.0 else (yc - y) / sy
    return (u + 0.5, (z - zc) / sz + 0.5)


def _patch(img, ppm):
    """Fade the letters unevenly, in linear light: each pixel keeps its
    darkening times a smooth noise between `GHOST_PATCH` and 1. The noise is
    `vnoise` on a 16-pixel grid, bilinear between, so the art is the same
    pixels wherever numpy is."""
    import numpy as np
    h, w = img.a.shape[:2]
    step = 16
    gx, gy = w // step + 2, h // step + 2
    k = step / ppm / GHOST_PATCH_M
    grid = np.array([[vnoise(i * k, j * k, 7) for i in range(gx)] for j in range(gy)], dtype=np.float64)
    xs, ys = np.arange(w) / float(step), np.arange(h) / float(step)
    x0, y0 = np.floor(xs).astype(int), np.floor(ys).astype(int)
    fx, fy = (xs - x0)[None, :], (ys - y0)[:, None]
    m = ((grid[np.ix_(y0, x0)] * (1 - fx) + grid[np.ix_(y0, x0 + 1)] * fx) * (1 - fy)
         + (grid[np.ix_(y0 + 1, x0)] * (1 - fx) + grid[np.ix_(y0 + 1, x0 + 1)] * fx) * fy)
    keep = GHOST_PATCH + (1.0 - GHOST_PATCH) * m
    s = img.a[..., 0].astype(np.float64) / 255.0
    lin = np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
    lin = 1.0 - (1.0 - lin) * keep
    out = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1.0 / 2.4) - 0.055)
    img.a[...] = (out * 255.0).astype(np.float32)[..., None]


def ghost_art():
    """The ghost's art: white, the old name in `GHOST_INK`. Returns
    ``{"png", "name", "size", "lines"}``; ``lines`` holds each line's ink
    box in pixels. Raises when a line does not set: a name that silently
    dropped a line would look like a choice."""
    import hashlib

    from . import paint as PT
    from . import smooth_type as ST
    w, h = GHOST_PX
    ppm = h / GHOST_SPAN[1]
    img = PT.Img(w, h, (255, 255, 255))
    ink = _srgb8(GHOST_INK)
    face = ST.owned("shop")
    top, lines = 0.0, []
    for (text, cap), gap in zip(GHOST_LINES, GHOST_GAPS):
        top += gap
        box = (0, top * ppm, w, (top + cap) * ppm)
        got = img.text(text, box, (ink, ink, ink), face=face, cap=cap * ppm, min_cap=int(cap * ppm) - 2)
        if got is None:
            raise ValueError("the ghost's line %r does not set at %.2f m" % (text, cap))
        lines.append(got)
        top += cap
    _patch(img, ppm)
    canvas = img.to_canvas()
    # NAMED BY WHAT IT IS, not by its bytes. A hash of the PNG named one
    # art two ways (zlib builds compress the same pixels differently), and
    # a hash of the pixels still did: system Python and Blender's numpy
    # round the resampled letters a little differently (2026-10-08).
    ident = repr((GHOST_LINES, GHOST_GAPS, GHOST_SPAN, GHOST_PX, GHOST_INK,
                  GHOST_PATCH, GHOST_PATCH_M, face)).encode("utf-8")
    return {"png": canvas.png(), "name": "Van_ghost_" + hashlib.sha1(ident).hexdigest()[:8],
            "size": (w, h), "lines": lines}
