"""The box truck's numbers, its fleets and its livery, pure (Zoo 1.92.0, roadmap 219 note 5).

The walker, walking club_block_014 on 2026-10-09: "i dont know what this giant grey box is". It
was `box_truck`, still the placeholder silhouette `tools/new_species.py` minted on 2026-09-12: one
solid box, parked by Lot as cover between buildings (roadmap 22). `recipes/box_truck.py` now draws
it; everything here is the part of it that needs no Blender, so the suite can test it: where each
part stands for a given slot (`layout`), which fleet a variant is (`FLEETS`), the livery's art
(`livery_art`) and where on it a corner samples (`livery_uv`), and what colour the paint is
(`finish_rgb`). The recipe imports bpy; this module must not.

WHAT A BOX TRUCK IS HERE: a 1990s cab-over delivery truck. The cab sits over the front wheels, a
flat face with a big windshield, a third or less of the length; a taller cargo box behind it on the
frame, with a roll-up door at the rear and a step bumper under it; single front wheels, dual rears.
No maker's mark anywhere. It is NOT the crew's step van (`van_forms`), which is one-of-a-kind and
parked at the spawn: these are the street's working trucks, white boxes in four invented Delco
fleets, the way every lot in the county had one.

FRAME AND UNITS. Recipe space before `build.build_module` re-centres it: metres, X across (the
kerb side at -X), Y along (the nose at -Y), Z up from the ground at 0.
"""
from __future__ import annotations

import math

from . import van_forms

#: The mirror heads stand this far outside the cab's side: the slot's width is the heads' outer
#: faces. The box is wider than the cab, as a box truck's is: its side stands BOX_OUT inside the
#: slot's half-width, so its corner caps reach the slot.
MIRROR_OUT = 0.17
BOX_OUT = 0.03
#: The box's clearance lamps stand this tall on its roof's front edge: the slot's height is their
#: tops.
ROOF_LAMP = 0.04
#: The bumpers stand this far ahead of the cab's face and behind the box's rear frame.
BUMPER_FWD = 0.10
BUMPER_BACK = 0.16
#: The cab, face to back wall, and the gap between it and the box. A 1990s cab-over's cab is
#: about 1.5 m long.
CAB_LEN = 1.55
CAB_GAP = 0.10
#: A cab-over sits over its front wheels: the axle stands this far behind the cab's face.
FRONT_AXLE_BEHIND = 0.62
#: The rear axle's distance ahead of the box's rear, at the default 6.0 m slot.
REAR_AXLE_AHEAD = 1.45
#: The cab's plan corners and roof edge are rounded this much; the box's roof edge this much.
CAB_ROUND = 0.12
BOX_ROUND = 0.03
#: The windshield's top stands this far behind its base.
WS_RAKE = 0.10
#: The cab roof stands this far under the box's top: the box towers over its cab.
CAB_UNDER_BOX = 0.30
#: The glass's top under the cab roof, and the belt line's share of the cab's height.
HEADER = 0.12
BELT = 0.50
#: The cab's skirt above the ground; the frame's top and the box floor's underside, in tread
#: radii.
CAB_SKIRT_R = 1.25
FRAME_R = 1.55
#: The box floor's sills and crossmembers stand this deep on the frame.
BOX_SILL = 0.12


def _clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def layout(W, L, H):
    """Where every part of a box truck built to a W x L x H slot stands.

    Pure. Every number derives from the slot and the module constants above, so a longer slot is
    a longer box behind the same cab, not a stretched cab."""
    hb = W / 2.0 - BOX_OUT                            # the box's side
    hc = W / 2.0 - MIRROR_OUT                         # the cab's side
    r = _clamp(0.40 * H / 2.8, 0.34, 0.44)            # wheel radius
    z_frame = round(r * FRAME_R, 4)
    z_box0 = round(z_frame + BOX_SILL, 4)             # the box floor's underside
    z_box1 = H - ROOF_LAMP                            # the box's roof
    z_cab1 = min(z_box1 - CAB_UNDER_BOX, 2.55)        # the cab's roof
    z_cab0 = round(r * CAB_SKIRT_R, 4)                # the cab's skirt
    z_belt = round(z_cab0 + (z_cab1 - z_cab0) * BELT, 4)
    y0, yt = -L / 2.0, L / 2.0                        # bumper outer faces
    y_n = y0 + BUMPER_FWD                             # the cab's face
    y_c = y_n + CAB_LEN                               # the cab's back wall
    y_b = y_c + CAB_GAP                               # the box's front
    y_r = yt - BUMPER_BACK                            # the box's rear frame
    ya_f = y_n + FRONT_AXLE_BEHIND
    ya_r = y_r - REAR_AXLE_AHEAD * (L / 6.0)
    arch = r + 0.10                                   # arch half-length along Y
    z_arch = 2.0 * r + 0.06                           # arch top
    return {
        "W": W, "L": L, "H": H, "hb": hb, "hc": hc, "r": r, "tyre_w": 0.22,
        "z_frame": z_frame, "z_box0": z_box0, "z_box1": z_box1,
        "z_cab0": z_cab0, "z_cab1": z_cab1, "z_belt": z_belt, "z_head": z_cab1 - HEADER,
        "y0": y0, "yt": yt, "y_n": y_n, "y_c": y_c, "y_b": y_b, "y_r": y_r,
        # the windshield's base stands behind the plan corners' rounding, so its pillars stand
        # on the cab's full width rather than overhanging the curve
        "y_ws": y_n + CAB_ROUND, "y_wt": y_n + CAB_ROUND + WS_RAKE,
        "ya_f": ya_f, "ya_r": ya_r, "arch": arch, "z_arch": z_arch,
        # the cab's doors: behind the windshield's pillar to the back wall's
        "y_door0": y_n + 0.32, "y_door1": y_c - 0.10,
    }


def cab_half_width(lay, y):
    """The cab's half-width at ``y``: its plan corners are quarter circles of `CAB_ROUND`."""
    d = y - lay["y_n"]
    if d >= CAB_ROUND:
        return lay["hc"]
    t = (CAB_ROUND - max(0.0, d)) / CAB_ROUND
    return lay["hc"] - CAB_ROUND * (1.0 - math.sqrt(max(0.0, 1.0 - t * t)))


# ------------------------------------------------------------------------------------------------
# The fleets
# ------------------------------------------------------------------------------------------------

#: THE FLEETS, invented, Delco, PG-13 (the brand rule: never a real mark). Each is the box side's
#: lines -- text and cap height, metres -- the cab's paint and the lettering's ink, sRGB 0..255.
#: A box truck is a white box on a coloured cab, and the box carries the name; the stripe along
#: its foot is the cab's colour. Four, as the dumpsters' haulers are, chosen to stand off asphalt,
#: brick and painted block.
FLEETS = (
    {"id": "blue_route_movers",
     "lines": (("BLUE ROUTE", 0.36), ("MOVERS", 0.26), ("WE'VE ONLY DROPPED ONE PIANO", 0.10),
               ("610-555-0128", 0.10)),
     "cab": (36, 70, 148), "ink": (28, 52, 116)},
    {"id": "hoagie_haul",
     "lines": (("HOAGIE HAUL", 0.40), ("WIT OR WITOUT. WE DELIVER.", 0.12),
               ("610-555-0184", 0.10)),
     "cab": (132, 38, 44), "ink": (110, 28, 34)},
    {"id": "nanas_basement",
     "lines": (("NANA'S BASEMENT", 0.30), ("SELF STORAGE", 0.20),
               ("WE DON'T ASK WHAT'S IN THE BOXES", 0.09), ("610-555-0151", 0.10)),
     "cab": (34, 104, 62), "ink": (22, 76, 44)},
    {"id": "down_the_shore_rentals",
     "lines": (("DOWN THE SHORE", 0.30), ("PARTY RENTALS", 0.20),
               ("TENTS. TABLES. NO REFUNDS.", 0.10), ("610-555-0196", 0.10)),
     "cab": (186, 104, 36), "ink": (128, 66, 18)},
)
#: The gaps above each line, metres: the first is the margin under the box's roof.
LINE_GAP = 0.10
#: The box's paint: a fleet white, a little warm, never clean.
BOX_WHITE = (232, 230, 222)
#: The stripe along the box's foot: its height, and its gap above the floor's line.
STRIPE = (0.16, 0.10)
#: The art covers the box's side: its span along and up it, metres, and its pixels -- the same
#: pixels a metre both ways, about Zoo's sign texel.
LIVERY_SPAN = (3.8, 1.6)
LIVERY_PX = (1024, 432)
#: Where a face that carries no lettering samples the art: past its corner, which the clamped
#: sampler reads as the white margin.
LIVERY_OUTSIDE = (-0.5, -0.5)


def fleet(variant):
    return FLEETS[int(variant or 0) % len(FLEETS)]


def _srgb_to_lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def livery_centre(lay):
    """The art's centre on the box's side: ``(y, z)``, recipe space."""
    return ((lay["y_b"] + lay["y_r"]) / 2.0, (lay["z_box0"] + lay["z_box1"]) / 2.0)


def livery_uv(co, normal, lay):
    """Where a corner samples the livery. A face looking along X on the BOX -- its sides -- maps
    by its (y, z), read the right way round from outside on either side; anything else, the cab
    included, samples the white margin."""
    x, y, z = co
    if abs(normal[0]) < 0.9 or y < lay["y_b"] - 0.01:
        return LIVERY_OUTSIDE
    yc, zc = livery_centre(lay)
    sy, sz = LIVERY_SPAN
    u = (y - yc) / sy if normal[0] > 0.0 else (yc - y) / sy
    return (u + 0.5, (z - zc) / sz + 0.5)


def livery_art(variant):
    """The box side's art for a fleet: white, the stripe along the foot in the cab's colour, the
    name and its lines in the fleet's ink. Returns ``{"png", "name", "size", "lines"}``; raises
    when a line does not set, because a name that silently dropped a line would look like a
    choice."""
    import hashlib

    from . import paint as PT
    from . import smooth_type as ST
    f = fleet(variant)
    w, h = LIVERY_PX
    ppm = h / LIVERY_SPAN[1]
    img = PT.Img(w, h, BOX_WHITE)
    face = ST.owned("shop")
    top, lines = 0.0, []
    for text, cap in f["lines"]:
        top += LINE_GAP
        box = (int(0.06 * w), top * ppm, int(0.94 * w), (top + cap) * ppm)
        got = img.text(text, box, f["ink"], face=face, cap=cap * ppm, min_cap=int(cap * ppm) - 2)
        if got is None:
            raise ValueError("fleet %s's line %r does not set at %.2f m" % (f["id"], text, cap))
        lines.append(got)
        top += cap
    s_h, s_gap = STRIPE
    img.rect((0, h - (s_gap + s_h) * ppm, w, h - s_gap * ppm), f["cab"])
    ident = repr((f["id"], f["lines"], f["cab"], f["ink"], BOX_WHITE, STRIPE, LIVERY_SPAN,
                  LIVERY_PX, LINE_GAP, face)).encode("utf-8")
    return {"png": img.to_canvas().png(), "name": "BoxTruck_" + f["id"] + "_" +
            hashlib.sha1(ident).hexdigest()[:8], "size": (w, h), "lines": lines}


# ------------------------------------------------------------------------------------------------
# The finish
# ------------------------------------------------------------------------------------------------

#: Road grime on the lower body, and how high it reaches; the roof's streaks under the drip rail.
GRIME = (0.30, 0.27, 0.22)
GRIME_TOP = 0.95
STREAK = 0.10


def finish_rgb(co, normal, lay, variant):
    """The linear colour a body corner is painted, multiplied into the livery's art by the
    material: the box white, the cab its fleet's colour, both dulled by road grime low down and
    streaked under the box's roof. Deterministic from position alone (`van_forms.vnoise`)."""
    x, y, z = co
    f = fleet(variant)
    if y < lay["y_b"] - 0.01:
        # THE CAB SAMPLES THE ART'S MARGIN, which is the box's own white, not 1.0: the material
        # multiplies the two, so the cab's colour is set against that white and lands exactly on
        # the fleet's. Every channel stays under 1 for the four fleets.
        base = tuple(_srgb_to_lin(c) / _srgb_to_lin(m) for c, m in zip(f["cab"], BOX_WHITE))
    else:
        base = (1.0, 1.0, 1.0)                        # the art carries the box's own white
    n = van_forms.vnoise(y * 2.2, z * 3.1, 11)
    low = _clamp((GRIME_TOP - z) / GRIME_TOP) * (0.55 + 0.45 * n)
    rgb = [b + (g - b) * low * 0.6 for b, g in zip(base, GRIME)]
    if y >= lay["y_b"] and lay["z_box1"] - z < 0.45 and abs(normal[2]) < 0.5:
        s = STREAK * van_forms.vnoise(y * 9.0, 0.5, 23)
        rgb = [c * (1.0 - s) for c in rgb]
    return tuple(rgb)


#: The chassis and running gear's colour: grime over black.
CHASSIS_RGB = (0.035, 0.034, 0.032)
