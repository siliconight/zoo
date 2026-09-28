"""The convenience store's frozen drink station, decided in pure Python: the
stand, the twin-hopper machine, the cup tubes, the syrup rail, and every
pixel of what glows.

Zoo 1.15.0, species `slush_machine`. Asked for by name, 2026-09-28: "do the
slush machine next". The references (docs/proposals/GAS_STATION_SHOP.md,
"The frozen drink machine is its own object and it is loud"): a twin-hopper
slush dispenser with clear barrels showing the product itself -- one red,
one blue, visibly churning -- a branded topper above, a cartoon mascot on
the front panel, a pull tap per hopper, and a tube of stacked cups beside
it; the second adds a six-bottle syrup rail with a labelled pump per
flavour, a numbered "1 select cup size, 2 add flavor, 3 pull to fill"
panel, a drip tray, and a straw caddy. "It is the most SATURATED object in
a 1990s convenience store ... A grey box in that corner loses the whole
read."

WHAT IS BUILT, in the recipe frame (metres, Z up, floor 0, CENTRE pivot,
x along the station, the customer at -Y, the wall behind at +Y). Left to
right as the customer reads it, which is the order the instructions give:

  * a counter-height STAND: kick, carcass, laminate top, a backsplash, and
    the mascot panel across its front, lit;
  * the CUP TUBES, a large and a medium, clear, with cups stacked up out of
    them, and a straw caddy behind;
  * the SYRUP RAIL (when the station is wide enough): a riser along the
    backsplash, six bottles with a pump each -- the pump head in the
    flavour's colour -- a lit strip naming each flavour under its bottle,
    and the lit instruction panel above;
  * the MACHINE: a tower at the back, a base, two clear barrels (three on
    a wide station) with the slush inside them, a lid on each, a tap and a
    pull handle in the flavour's colour over a drip tray, and the topper,
    lit.

THE SLUSH GLOWS, and that is the design, not a shortcut. The barrels of
colour are what a dark shop has to catch the eye, so the slush is on the
backlit image with the topper and the panels: a churn-striped tile per
flavour wrapped once round each barrel. Real machines light the barrel
from the lid; the emission stands in for that at no light's cost, and
Lux's power cut takes it (the material ends `_Face`).

THREE SUBMISSIONS whatever the width: painted steel (every opaque part,
its colour in the `Wear` vertex colour), the glass (barrels and tubes),
and the glow (topper, mascot panel, instruction panel, flavour strip,
slush).

NO TWO FACES SHARE A PLANE among these primitives (`prims.coincident_pairs`
is empty); every part meeting another is buried into it, and parts buried
into one surface stop at different depths where their footprints overlap.

THE BRAND IS INVENTED. FROZEN JAWN is FLAPPHAS's own frozen drink, in the
walker's Delco slang: funny, a bit crass, no real mark.
"""
from __future__ import annotations

import math
import re
import zlib

from . import pixel_type as pt
from . import prims as P
from .vending_forms import Canvas

#: Deli Counter's volume (long side first), then the genome's range.
DC_SIZES = ((1.6, 0.7, 2.0),)
RANGES = {"width": (1.0, 2.6), "depth": (0.6, 0.9), "height": (1.8, 2.4)}

BURY = 0.004
# --- the stand ---------------------------------------------------------------------------
CTR_H = 0.90              # the counter top
SLAB_T = 0.04
KICK_H = 0.10
SPLASH_T = 0.02
SPLASH_UP = 0.62          # the backsplash above the counter
# --- zones along the station -----------------------------------------------------------------
M_END = 0.04
GAP = 0.03
CUPS_W = 0.26
RAIL_W = 0.50
# --- the machine -----------------------------------------------------------------------------
BOWL_R = 0.12
BOWL_PITCH = 0.28
MSIDE = 0.03
TOWER_D = 0.14
BASE_H = 0.22             # a cup stands under the tap: 16 cm clear over the tray
TRAY_D = 0.12
LID_H = 0.04
TOPPER_H = 0.30
BOWL_H_MAX = 0.50
BOWL_H_MIN = 0.30
FILL = 0.78               # the slush's level, a fraction of the barrel
SEG = 16
# --- the rail ---------------------------------------------------------------------------------
BOTTLE_PITCH = 0.08
RISER_D = 0.14
RISER_H = 0.06
N_BOTTLES = 6
# --- cups ---------------------------------------------------------------------------------------
TUBES = ((0.052, 0.50, "cup_white"), (0.044, 0.42, "cup_red"))   # radius, height, key
CUP_PITCH = 0.03

#: Flavours: (id, name on the strip, slush colours (base, light, dark, ice), steel tint).
FLAVOURS = {
    "cherry": ("CHERRY", ((196, 18, 34), (238, 74, 88), (132, 8, 20), (255, 196, 204)), (0.62, 0.02, 0.04)),
    "blue": ("BLUE", ((22, 84, 226), (86, 150, 255), (10, 42, 150), (200, 226, 255)), (0.02, 0.10, 0.62)),
    "lime": ("LIME", ((70, 200, 40), (150, 240, 110), (30, 120, 20), (220, 255, 200)), (0.08, 0.48, 0.03)),
    "grape": ("GRAPE", ((120, 36, 170), (180, 100, 230), (70, 16, 110), (230, 200, 250)), (0.20, 0.03, 0.34)),
    "orange": ("ORANGE", ((240, 120, 20), (255, 180, 90), (170, 70, 10), (255, 230, 190)), (0.80, 0.24, 0.02)),
    "cola": ("COLA", ((90, 40, 20), (150, 90, 50), (50, 20, 10), (220, 190, 170)), (0.10, 0.03, 0.01)),
}
#: The barrels, by variant: always a red and a blue, the walker's reference;
#: the third is for a wide station.
BOWL_SETS = (("cherry", "blue", "lime"), ("blue", "cherry", "orange"),
             ("cherry", "blue", "grape"), ("blue", "cherry", "lime"))
RAIL_ORDER = ("cherry", "blue", "lime", "grape", "orange", "cola")

TOPPER_WORDS = ("FROZEN JAWN", "FREEZE YOUR JAWN OFF")
PANEL_WORDS = ("FROZEN JAWN", "COLDER THAN YOUR EX")
STEPS = ("SELECT CUP SIZE", "ADD FLAVOR", "PULL TO FILL")

#: Colours (linear) and surface kind of every non-glowing part.
MATERIALS = {
    "cabinet": ((0.03, 0.08, 0.34), "metal_painted"),
    "laminate": ((0.80, 0.80, 0.77), "metal_painted"),
    "black": ((0.02, 0.02, 0.022), "metal_painted"),
    "steel": ((0.62, 0.63, 0.65), "metal_painted"),
    "tray": ((0.48, 0.49, 0.50), "metal_painted"),
    "white": ((0.86, 0.86, 0.85), "metal_painted"),
    "label": ((0.86, 0.82, 0.70), "metal_painted"),
    "cup_white": ((0.88, 0.88, 0.86), "metal_painted"),
    "cup_red": ((0.66, 0.04, 0.05), "metal_painted"),
    "straw_red": ((0.70, 0.04, 0.05), "metal_painted"),
    "straw_white": ((0.88, 0.88, 0.86), "metal_painted"),
    "glass": ((0.80, 0.86, 0.88), "glass"),
}
for _f, (_n, _c, _tint) in FLAVOURS.items():
    MATERIALS["flav_" + _f] = (_tint, "metal_painted")
KIND_BASE = {"metal_painted": (1.0, 1.0, 1.0), "glass": (0.80, 0.86, 0.88)}
GLASS_OPACITY = 0.22
#: The glow's emission and its dimmed diffuse copy, the cooler wall's
#: (`cooler_run_forms.GLOW_EMISSION`): judged on the walk there, and this is
#: the same kind of backlit plastic.
GLOW_EMISSION = 1.0
GLOW_ALBEDO = 0.6
#: Pixels a metre, per region: each region maps to its own rect, so each is
#: sized for the lettering on it rather than to one compromise.
TEXEL_PANEL = 160
TEXEL_TOPPER = 240
TEXEL_STEPS = 300
TEXEL_RAIL = 600
SLUSH_TILE = 48
_VARIANT = re.compile(r"_n\d+(?=_|$)")


def vertex_tint(mat_key):
    rgb, kind = MATERIALS[mat_key]
    return kind, tuple(c / b for c, b in zip(rgb, KIND_BASE[kind]))


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def resolve(plan_):
    params = plan_.get("params") or {}
    module = plan_.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    key = _VARIANT.sub("", module.get("stem") or "") or "slush_machine"
    return key, variant


def machine_width(n):
    return n * BOWL_PITCH + 2.0 * MSIDE


def need(n, rail):
    zones = 3 if rail else 2
    return 2.0 * M_END + CUPS_W + machine_width(n) + (RAIL_W if rail else 0.0) + GAP * (zones - 1)


def zones(w):
    """``(n_bowls, rail, {zone: (x0, x1)})``: three barrels when a station
    holds them and the rail; the rail when it fits; the slack split between
    the gaps, so the cups hold the left end and the machine the right."""
    n = 3 if need(3, True) <= w + 1e-9 else 2
    rail = need(n, True) <= w + 1e-9
    slack = w - need(n, rail)
    g = GAP + slack / (2.0 if rail else 1.0)
    x = -w / 2.0 + M_END
    out = {"cups": (x, x + CUPS_W)}
    x += CUPS_W + g
    if rail:
        out["rail"] = (x, x + RAIL_W)
        x += RAIL_W + g
    out["machine"] = (x, x + machine_width(n))
    return n, rail, out


def bowl_height(h):
    room = h - TOPPER_H - 0.02 - LID_H - CTR_H - BASE_H
    return max(BOWL_H_MIN, min(BOWL_H_MAX, room))


def glow_box(part, lo, hi, region, face=2, other="side"):
    """A box on the glow image: face ``face`` (P.box order: 0 bottom, 1 top,
    2 -Y, 3 +X, 4 +Y, 5 -X) maps edge to edge onto ``region``, every other
    face takes the solid ``other`` block."""
    p = P.box(part, "glow", lo, hi)
    x0, y0, z0 = lo
    x1, y1, z1 = hi

    def uv(i):
        x, _y, z = p["verts"][i]
        return (region, (x - x0) / (x1 - x0), (z - z0) / (z1 - z0))
    p["uvs"] = [tuple(uv(i) for i in f) if k == face else tuple((other,) for _ in f)
                for k, f in enumerate(p["faces"])]
    return p


def lathe(part, mat, cx, cy, z0, profile, segments=SEG, phase=0.0):
    """A closed solid of revolution about the vertical through (cx, cy):
    ``profile`` is ``((z, r), ...)`` from the bottom up, offset by ``z0``;
    capped at both ends, faces wound outward (as `prims.cyl`). Each side
    quad carries ``(ring, k)`` in ``p['bands']`` so a caller can map it."""
    n = int(segments)
    verts = []
    for z, r in profile:
        for k in range(n):
            a = 2.0 * math.pi * k / n + phase
            verts.append((cx + r * math.cos(a), cy + r * math.sin(a), z0 + z))
    faces = [tuple(reversed(range(n)))]
    bands = [None]
    for ring in range(len(profile) - 1):
        b0, b1 = ring * n, (ring + 1) * n
        for k in range(n):
            k1 = (k + 1) % n
            faces.append((b0 + k, b0 + k1, b1 + k1, b1 + k))
            bands.append((ring, k))
    top = (len(profile) - 1) * n
    faces.append(tuple(range(top, top + n)))
    bands.append(None)
    p = P.mesh(part, mat, verts, faces)
    p["bands"] = bands
    return p


def slush(part, cx, cy, z0, profile, flavour, side_rings):
    """The slush in a barrel, on the glow image: the side bands in
    ``side_rings`` wrap the flavour's churn tile once round (u by segment,
    v by height), everything else takes its solid colour."""
    p = lathe(part, "glow", cx, cy, z0, profile)
    n = SEG
    za = profile[side_rings[0]][0]
    zb = profile[side_rings[-1] + 1][0]
    uvs = []
    for f, band in zip(p["faces"], p["bands"]):
        if band is not None and band[0] in side_rings:
            _ring, k = band
            cs = []
            for i in f:
                z = p["verts"][i][2] - z0
                kk = (i % n)
                u = kk / float(n)
                if kk == 0 and k == n - 1:
                    u = 1.0                     # the seam's far side
                cs.append(("slush_" + flavour, u, (z - za) / (zb - za)))
            uvs.append(tuple(cs))
        else:
            uvs.append(tuple(("top_" + flavour,) for _ in f))
    p["uvs"] = uvs
    del p["bands"]
    return p


def _plain(p):
    p.pop("bands", None)
    return p


def layout(w, d, h, key="slush_machine", variant=0):
    """Every part at slot (w, d, h): ``(prims, facts)``. The module IS the
    slot's box: the counter top's plan and the topper's top."""
    out = []
    n, rail, zs = zones(w)
    flavours = BOWL_SETS[variant % len(BOWL_SETS)][:n]
    yf, yk = -d / 2.0, d / 2.0
    ys = yk - SPLASH_T                     # the backsplash's front
    top = CTR_H
    # --- the stand ------------------------------------------------------------------------
    out.append(P.box("Slush_Stand", "laminate", (-w / 2.0, yf, top - SLAB_T), (w / 2.0, yk - 0.012, top)))
    out.append(P.box("Slush_Stand", "cabinet", (-w / 2.0 + 0.012, yf + 0.03, KICK_H),
                     (w / 2.0 - 0.012, yk - 0.03, top - SLAB_T + BURY)))
    out.append(P.box("Slush_Stand", "black", (-w / 2.0 + 0.03, yf + 0.07, 0.0),
                     (w / 2.0 - 0.03, yk - 0.05, KICK_H + BURY)))
    out.append(P.box("Slush_Stand", "steel", (-w / 2.0 + 0.005, ys, top - 0.01), (w / 2.0 - 0.005, yk, top + SPLASH_UP)))
    out.append(glow_box("Slush_Glow", (-w / 2.0 + 0.06, yf + 0.022, KICK_H + 0.05),
                        (w / 2.0 - 0.06, yf + 0.03 + BURY, top - SLAB_T - 0.05), "panel"))
    # --- the cups ----------------------------------------------------------------------------
    cx0 = zs["cups"][0]
    ty = ys - 0.20
    tx = cx0 + 0.010
    for r, th, ck in TUBES:
        rb = r + 0.010
        x = tx + rb
        out.append(_plain(P.cyl("Slush_Cups", "black", (x, ty), rb, top - BURY, top + 0.02, segments=SEG)))
        out.append(_plain(lathe("Slush_Tube", "glass", x, ty, top + 0.012, ((0.0, r), (th - 0.012, r)))))
        prof = []
        z = 0.0
        stack = th - 0.012 + 0.025 - 0.012      # from 12 mm up to 25 mm over the tube
        while z + CUP_PITCH <= stack + 1e-9:
            # two rings a cup: the wall flaring out to the rim, stepping in
            prof += [(z, r - 0.010), (z + CUP_PITCH - 0.004, r - 0.006)]
            z += CUP_PITCH
        prof.append((z, r - 0.010))
        out.append(_plain(lathe("Slush_Cups", ck, x, ty, top + 0.024, prof, segments=10, phase=0.13)))
        tx = x + rb + 0.008
    # the straw caddy, behind the tubes
    sx, sy = cx0 + 0.13, ys - 0.06
    out.append(_plain(P.cyl("Slush_Cups", "black", (sx, sy), 0.035, top - BURY, top + 0.13, segments=10)))
    for i in range(7):
        a = 2.0 * math.pi * i / 7.0 + 0.3
        dx, dy = 0.015 * math.cos(a), 0.015 * math.sin(a)
        out.append(_plain(P.rod("Slush_Cups", "straw_red" if i % 2 else "straw_white",
                                (sx + dx, sy + dy, top + 0.03),
                                (sx + 2.2 * dx, sy + 2.2 * dy, top + 0.25), 0.0035, segments=5)))
    # --- the syrup rail ---------------------------------------------------------------------
    rail_names = []
    if rail:
        rx0, rx1 = zs["rail"]
        out.append(P.box("Slush_Rail", "white", (rx0, ys - RISER_D, top - BURY), (rx1, ys + BURY, top + RISER_H)))
        out.append(glow_box("Slush_Glow", (rx0 + 0.01, ys - RISER_D - 0.008, top + 0.010),
                            (rx1 - 0.01, ys - RISER_D + BURY, top + 0.050), "rail"))
        out.append(glow_box("Slush_Glow", (rx0 + 0.01, ys - 0.012, top + 0.40),
                            (rx1 - 0.01, ys + BURY, top + SPLASH_UP - 0.03), "steps"))
        by_ = ys - RISER_D / 2.0
        z0 = top + RISER_H - BURY
        for i, fl in enumerate(RAIL_ORDER[:N_BOTTLES]):
            bx = (rx0 + rx1) / 2.0 + (i - (N_BOTTLES - 1) / 2.0) * BOTTLE_PITCH
            out.append(_plain(lathe("Slush_Syrup", "flav_" + fl, bx, by_, z0,
                                    ((0.0, 0.030), (0.006, 0.032), (0.165, 0.032), (0.195, 0.015), (0.225, 0.013)),
                                    segments=12)))
            out.append(_plain(lathe("Slush_Syrup", "label", bx, by_, z0, ((0.05, 0.036), (0.13, 0.036)), segments=12)))
            out.append(_plain(P.cyl("Slush_Syrup", "black", (bx, by_), 0.019, z0 + 0.215, z0 + 0.245, segments=10)))
            out.append(_plain(P.rod("Slush_Syrup", "steel", (bx, by_, z0 + 0.24), (bx, by_, z0 + 0.29), 0.005, segments=5)))
            out.append(_plain(P.cyl("Slush_Syrup", "flav_" + fl, (bx, by_), 0.017, z0 + 0.285, z0 + 0.315, segments=10)))
            out.append(_plain(P.rod("Slush_Syrup", "black", (bx, by_ - 0.010, z0 + 0.300),
                                    (bx, by_ - 0.055, z0 + 0.293), 0.005, segments=5)))
            rail_names.append(fl)
    # --- the machine -------------------------------------------------------------------------
    mx0, mx1 = zs["machine"]
    yb = ys - 0.01                          # the machine's back
    by = yb - TOWER_D - 0.01 - BOWL_R       # the barrels' centre line
    bfront = by - BOWL_R
    bh = bowl_height(h)
    z_base = top + BASE_H
    z_t0 = h - TOPPER_H
    # the parts buried into the counter top stop at 4, 8 and 12 mm: the
    # tower's and the base's footprints overlap by BURY, and so do the
    # base's and the tray's
    out.append(P.box("Slush_Machine", "steel", (mx0 + 0.006, yb - TOWER_D, top - 0.004), (mx1 - 0.006, yb, z_t0 + BURY)))
    out.append(P.box("Slush_Machine", "steel", (mx0 + 0.012, bfront - 0.03, top - 0.008),
                     (mx1 - 0.012, yb - TOWER_D + BURY, z_base)))
    out.append(P.box("Slush_Machine", "tray", (mx0 + 0.02, bfront - 0.03 - TRAY_D, top - 0.012),
                     (mx1 - 0.02, bfront - 0.03 + BURY, top + 0.035)))
    out.append(P.box("Slush_Machine", "black", (mx0 + 0.035, bfront - 0.03 - TRAY_D + 0.012, top + 0.030),
                     (mx1 - 0.035, bfront - 0.03 - 0.008, top + 0.039)))
    zb0 = z_base - BURY
    rs = BOWL_R - 0.008
    for i, fl in enumerate(flavours):
        bx = mx0 + MSIDE + BOWL_PITCH * (i + 0.5)
        out.append(_plain(lathe("Slush_Barrel", "glass", bx, by, zb0,
                                ((0.0, BOWL_R - 0.02), (0.02, BOWL_R), (bh - 0.02, BOWL_R), (bh, BOWL_R - 0.01)))))
        fz = FILL * bh
        out.append(slush("Slush_Glow", bx, by, zb0,
                         ((0.012, rs - 0.012), (0.024, rs), (fz, rs), (fz + 0.025, rs * 0.55), (fz + 0.035, 0.02)),
                         fl, (1,)))
        out.append(_plain(P.cyl("Slush_Barrel", "white", (bx, by), BOWL_R + 0.006, zb0 + bh - 0.015,
                                zb0 + bh + LID_H, segments=SEG)))
        # the tap out of the barrel's foot, its nozzle, the pull handle
        tfront = bfront - 0.09
        out.append(P.box("Slush_Tap", "white", (bx - 0.03, tfront, z_base + 0.012), (bx + 0.03, bfront + 0.02, z_base + 0.07)))
        out.append(_plain(P.cyl("Slush_Tap", "black", (bx, tfront + 0.025), 0.012, z_base - 0.03,
                                z_base + 0.012 + BURY, segments=8)))
        out.append(_plain(P.rod("Slush_Tap", "flav_" + fl, (bx, tfront + 0.015, z_base + 0.065),
                                (bx, tfront - 0.02, z_base + 0.18), 0.008, 0.014, segments=6)))
    out.append(glow_box("Slush_Glow", (mx0, bfront - 0.012, z_t0), (mx1, yb - 0.006, h), "topper"))
    facts = {"bowls": n, "rail": rail, "flavours": list(flavours), "syrups": rail_names,
             "bowl_height": bh, "zones": zs, "machine_width": mx1 - mx0,
             "panel": (w - 0.12, top - SLAB_T - 0.05 - KICK_H - 0.05),
             "collision": ((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h))}
    return out, facts


def plan(w, d, h, key="slush_machine", variant=0):
    """``{prims, facts}`` -- the slot filled exactly."""
    prims, facts = layout(w, d, h, key, variant)
    return {"prims": prims, "facts": facts}


def signed_volume(p):
    vs = p["verts"]
    tot = 0.0
    for f in p["faces"]:
        a = vs[f[0]]
        for k in range(1, len(f) - 1):
            b, c = vs[f[k]], vs[f[k + 1]]
            tot += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return tot / 6.0


# --- the glow -----------------------------------------------------------------------------------

#: The mascot, a slush cup with a face: 16 x 20, one letter a pixel.
#: s straw, b slush dome, k black, w white, r red, p tongue, y cheeks.
MASCOT = (
    "..........ss....",
    ".........ss.....",
    "........ss......",
    "....bbbbsbbb....",
    "...bbbbbbbbbb...",
    "..bbbbbbbbbbbb..",
    "..kkkkkkkkkkkk..",
    "..wwwwwwwwwwww..",
    "..wkkwwwwwwkkw..",
    "..wkwwwwwwwkww..",
    "..wwwwwwwwwwww..",
    "k.ywkkkkkkkkwy.k",
    ".kwwkrrrrrrkwwk.",
    "..rrrkrppprkrr..",
    "..rrrrkpppkrrr..",
    "...wwwwkkkwwww..",
    "...rrrrrrrrrr...",
    "....wwwwwwww....",
    "....rrrrrrrr....",
    ".....kk..kk.....",
)
_MASCOT_RGB = {"s": (250, 210, 40), "b": (70, 150, 255), "k": (16, 16, 20), "w": (250, 250, 246),
               "r": (214, 24, 36), "p": (255, 130, 160), "y": (255, 170, 170)}
#: The headline face. NOT `bold`: its N is its H with a three-pixel
#: diagonal, and under the red outline FROZEN JAWN read as "FROZEH JAWH" in
#: the first render of this atlas. Monogram's N is a clean diagonal.
HEAD_FACE = "monogram"
PANEL_BG = (16, 40, 150)
ACCENT = (214, 24, 36)
YELLOW = (255, 214, 40)
WHITE = (252, 252, 246)


def _stamp_mascot(c, x0, y0, k):
    for j, row in enumerate(MASCOT):
        for i, ch in enumerate(row):
            if ch != ".":
                c.rect(x0 + i * k, y0 + j * k, x0 + (i + 1) * k, y0 + (j + 1) * k, _MASCOT_RGB[ch])


def _scale(text, width, height, face, cap):
    for k in range(cap, 0, -1):
        if pt.ink_width(text, k, face) <= width and pt.line(face) * k <= height:
            return k
    return 0


def _headline(c, text, x0, y0, width, height, face, colour, outline, cap=3):
    """``text`` on one line, or its words one a line, whichever is larger;
    a tie keeps one line."""
    words = text.split()
    one = _scale(text, width, height, face, cap)
    rows = height // max(1, len(words))
    many = min(_scale(w_, width, rows, face, cap) for w_ in words) if len(words) > 1 else 0
    if many > one:
        for j, w_ in enumerate(words):
            _words(c, w_, x0, y0 + j * rows, width, rows, face, colour, outline, cap=many)
        return many
    _words(c, text, x0, y0, width, height, face, colour, outline, cap=one)
    return one


def _words(c, text, x0, y0, width, height, face, colour, outline=None, cap=3):
    """Centre ``text`` in the box at the largest scale that fits; the mask
    is returned so a caller can see what was said (None when nothing fits)."""
    s = _scale(text, width, height, face, cap)
    if not s:
        return None
    m = pt.trim(pt.render(text, s, face))
    ox, oy = x0 + (width - len(m[0])) // 2, y0 + (height - len(m)) // 2
    if outline:
        c.mask(m, ox, oy, outline, grow=1)
    c.mask(m, ox, oy, colour)
    return m


def _churn(c, x0, y0, cols):
    """The slush tile: diagonal churn bands, seamless left to right, with a
    dither of ice through them."""
    base, light, dark, ice = cols
    S = SLUSH_TILE
    for y in range(S):
        for x in range(S):
            t = (x + y // 2) % 16
            rgb = light if t < 3 else dark if 8 <= t < 10 else base
            if (x * 7 + y * 13) % 29 == 0:
                rgb = ice
            c.px(x0 + x, y0 + y, rgb)


def glow_art(w, n, flavours, rail, key="slush_machine", variant=0):
    """ONE image for everything that glows: the mascot panel (`panel`), the
    topper (`topper`), the instruction panel (`steps`) and flavour strip
    (`rail`) when there is a rail, a churn tile (`slush_*`) and a solid
    (`top_*`) per barrel flavour, and the topper's sides (`side`).
    ``{canvas, size, rects, name, said}``; rects are pixel boxes, row 0 at
    the top."""
    pw = w - 0.12
    ph = CTR_H - SLAB_T - 0.05 - KICK_H - 0.05
    PW, PH = int(round(pw * TEXEL_PANEL)), int(round(ph * TEXEL_PANEL))
    TW, TH = int(round(machine_width(n) * TEXEL_TOPPER)), int(round(TOPPER_H * TEXEL_TOPPER))
    SW, SH = int(round((RAIL_W - 0.02) * TEXEL_STEPS)), int(round((SPLASH_UP - 0.03 - 0.40) * TEXEL_STEPS))
    RW, RH = int(round((RAIL_W - 0.02) * TEXEL_RAIL)), int(round(0.04 * TEXEL_RAIL))
    tiles = len(flavours)
    # the tiles, then a 6 px block a flavour on an 8 px pitch, then the side
    W = max(PW, TW + (SW if rail else 0), RW if rail else 0, tiles * (SLUSH_TILE + 8) + 16)
    H = PH + max(TH, SH if rail else 0) + (RH if rail else 0) + SLUSH_TILE + 4
    c = Canvas(W, H, (14, 14, 16))
    rects, said = {}, []
    # --- the mascot panel ------------------------------------------------------------------
    c.rect(0, 0, PW, PH, PANEL_BG)
    c.rect(0, 0, PW, 3, ACCENT)
    c.rect(0, PH - 3, PW, PH, ACCENT)
    k = max(1, min((PH - 8) // len(MASCOT), (PW // 3) // len(MASCOT[0])))
    mw = len(MASCOT[0]) * k
    _stamp_mascot(c, 6, (PH - len(MASCOT) * k) // 2, k)
    tx0, tw = 6 + mw + 6, PW - (6 + mw + 6) - 4
    _headline(c, PANEL_WORDS[0], tx0, 4, tw, (PH - 8) * 2 // 3, HEAD_FACE, WHITE, ACCENT)
    _words(c, PANEL_WORDS[1], tx0, 4 + (PH - 8) * 2 // 3, tw, (PH - 8) // 3, "m5x7", YELLOW, cap=2)
    said += list(PANEL_WORDS)
    rects["panel"] = (0, 0, PW, PH)
    # --- the topper ----------------------------------------------------------------------------
    y = PH
    c.rect(0, y, TW, y + TH, PANEL_BG)
    c.rect(0, y, TW, y + 2, (120, 190, 255))
    c.rect(0, y + TH - 2, TW, y + TH, (120, 190, 255))
    body = TH * 3 // 4
    _headline(c, TOPPER_WORDS[0], 2, y + 2, TW - 4, body - 2, HEAD_FACE, WHITE, ACCENT)
    _words(c, TOPPER_WORDS[1], 2, y + body, TW - 4, TH - body - 2, "m5x7", YELLOW, cap=1)
    said += list(TOPPER_WORDS)
    rects["topper"] = (0, y, TW, y + TH)
    # --- the instruction panel and the flavour strip ------------------------------------------------
    if rail:
        sx = TW
        c.rect(sx, y, sx + SW, y + SH, WHITE)
        c.rect(sx, y, sx + SW, y + 3, ACCENT)
        row = (SH - 6) // 3
        for j, text in enumerate(STEPS):
            ry = y + 4 + j * row
            b = min(row - 2, 12)
            c.rect(sx + 4, ry + (row - b) // 2, sx + 4 + b, ry + (row - b) // 2 + b, ACCENT)
            _words(c, str(j + 1), sx + 4, ry + (row - b) // 2, b, b, "small", WHITE, cap=1)
            if _words(c, text, sx + 8 + b, ry, SW - 12 - b, row, "bold", PANEL_BG, cap=1) is None:
                _words(c, text, sx + 8 + b, ry, SW - 12 - b, row, "m5x7", PANEL_BG, cap=1)
            said.append(f"{j + 1} {text}")
        rects["steps"] = (sx, y, sx + SW, y + SH)
        y2 = y + max(TH, SH)
        c.rect(0, y2, RW, y2 + RH, (24, 24, 30))
        pitch = BOTTLE_PITCH * TEXEL_RAIL
        for i, fl in enumerate(RAIL_ORDER[:N_BOTTLES]):
            cx = RW / 2.0 + (i - (N_BOTTLES - 1) / 2.0) * pitch
            name, cols, _t = FLAVOURS[fl]
            x0 = int(cx - pitch / 2.0) + 2
            c.rect(x0, y2 + 2, int(cx + pitch / 2.0) - 2, y2 + RH - 2, cols[0])
            _words(c, name, x0, y2 + 2, int(pitch) - 4, RH - 4, "m5x7", WHITE, (0, 0, 0), cap=2)
            said.append(name)
        rects["rail"] = (0, y2, RW, y2 + RH)
        y3 = y2 + RH
    else:
        y3 = y + TH
    # --- the slush tiles, the solid blocks ------------------------------------------------------------
    for i, fl in enumerate(flavours):
        x0 = i * SLUSH_TILE
        if "slush_" + fl in rects:
            continue
        cols = FLAVOURS[fl][1]
        _churn(c, x0, y3, cols)
        rects["slush_" + fl] = (x0, y3, x0 + SLUSH_TILE, y3 + SLUSH_TILE)
    bx = tiles * SLUSH_TILE + 4
    for i, fl in enumerate(flavours):
        r = (bx + i * 8, y3, bx + i * 8 + 6, y3 + 6)
        c.rect(*r, FLAVOURS[fl][1][0])
        rects["top_" + fl] = r
    r = (bx, y3 + 10, bx + 6, y3 + 16)
    c.rect(*r, PANEL_BG)
    rects["side"] = r
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H), "rects": rects, "said": said,
            "name": f"slushglow_v{variant % 4}_{W}x{H}_{digest:08x}"}
