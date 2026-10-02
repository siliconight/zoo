"""The convenience store's hot dog roller grill, decided in pure Python: the
bun cabinet, the grill, the rollers, the dogs, the tags and the hood.

Zoo 1.17.0, species `roller_grill`. Asked for by name, 2026-09-28: "do the
roller grill next". The references:

  * docs/proposals/GAS_STATION_SHOP.md, "Roller dogs": "A slanted bank of
    chrome rollers turning under a clear hood, sausages in three or four
    distinct colours and thicknesses laid across them -- pale, tan, deep
    red -- small labelled flag signs pushed in between the rows to name
    each one, grease darkening the rollers toward the back, and a printed
    'Buns' panel across the front of the cabinet below." NOT
    `flat_top_grill`: "a customer-facing display case at the till".
  * the walker's photographs, the same day: two store stations (zones of
    one kind each split by dividers, a black tube tag lying on the rollers
    naming each, a printed panel across the front, a warm-buns drawer
    below, a glass guard on posts) and a countertop merchandiser (rollers
    across the width with three columns of dogs in the grooves, a black
    control panel with two dials, two lights and a switch, a glass case on
    top with a shelf of buns).

HOW THE DOGS LIE -- a refutation kept. The first cut had rollers across the
width and dogs in the grooves; the store photographs then read, for a
moment, as rollers running front to back with the dogs across them, and
the countertop photograph settled it the first way: every roller runs
across the width, the ends show at the cheeks, and each dog rests in the
groove between two rollers, parallel to them, which is what turns it. The
proposal's "laid across them" is laid ON the bank.

WHAT IS BUILT, in the recipe frame (metres, Z up, floor 0, CENTRE pivot,
the customer at -Y):

  * the BUN CABINET, counter height, its front a printed warm-buns panel;
  * the GRILL: a steel pan, a black printed control panel across its front
    with two knobs, tall cheeks at both ends, and ROLLERS across the width
    in a bank climbing gently toward the back, each a shade greasier than
    the one in front of it;
  * COLUMNS across the width, one kind each -- pale, tan, deep red and a
    thin rolled one -- a dog in every groove but where one was sold, a
    chrome DIVIDER lying on the rollers between columns, and a black TAG in
    each column's front groove naming the kind;
  * the HOOD: four posts, glass sides and top, a glass front over the upper
    half (the lower half open to reach in with tongs), and when there is
    room a glass SHELF of buns.

FOUR SUBMISSIONS whatever the width: chrome (`metal_bare`, the grease in
the `Wear` colour), painted (`metal_painted`: cabinet, knobs, dogs, buns,
colours in `Wear`), the glass, and one painted image for the panels and the
tags.

NO TWO FACES SHARE A PLANE (`prims.coincident_pairs` empty); every part
meeting another is buried into it, and a dog, a divider or a tag stands
`REST_GAP` off the rollers it lies on rather than tangent to them.
"""
from __future__ import annotations

import math
import zlib

from . import card_art as CA
from . import paint as PT
from . import prims as P
from . import smooth_type as ST

#: Deli Counter's volume (long side first), then the genome's range.
DC_SIZES = ((1.0, 0.6, 1.4),)
RANGES = {"width": (0.7, 1.4), "depth": (0.5, 0.8), "height": (1.3, 1.6)}

BURY = 0.004
CAB_H = 0.86              # the bun cabinet's top
CAB_TOP_T = 0.03
KICK_H = 0.08
PAN_H = 0.07              # the grill's pan on the cabinet
PAN_IN = 0.04             # the pan inset from the cabinet's edges
PANEL_D = 0.012           # the control panel's thickness on the pan's front
CHEEK_W = 0.04
CHEEK_UP = 0.05           # the cheeks stand this far over the back roller
ROLLER_R = 0.0125
ROLLER_PITCH = 0.034
ROLLER_SEG = 8
RISE_DEG = 7.0            # the bank's climb toward the back
REST_GAP = 0.005          # a dog, divider or tag stands this far off the rollers
COL_MIN = 0.26            # a column's least width: three at the default 1.0 m, the countertop photograph's count
DIVIDER_R = 0.005
TAG_L, TAG_S = 0.11, 0.018
HOOD_T = 0.006
SHELF_T = 0.010           # the bun shelf, thick enough to bury a bun 5 mm and clear its underside
BUN_CROWN = 0.015
POST = 0.016
SHELF_ROOM = 0.42         # the hood's height over the pan that earns a bun shelf
BUN_L, BUN_W, BUN_H = 0.15, 0.06, 0.045

#: The kinds, column by column: (id, tag text, colour (linear), dog radius,
#: dog length). "pale, tan, deep red" and a thin rolled one.
KINDS = (
    ("jumbo", "BIG JAWN", (0.52, 0.20, 0.10), 0.0150, 0.170),
    ("cheezy", "CHEEZY", (0.78, 0.56, 0.36), 0.0120, 0.150),
    ("spicy", "HOT LINK", (0.40, 0.05, 0.04), 0.0130, 0.160),
    ("taquito", "TAQUITO", (0.72, 0.48, 0.18), 0.0100, 0.140),
)
PANEL_WORDS = ("NICE BUNS", "WARM ALL DAY")

MATERIALS = {
    "chrome": ((0.80, 0.80, 0.82), "metal_bare"),
    "cabinet": ((0.62, 0.05, 0.05), "metal_painted"),
    "black": ((0.02, 0.02, 0.022), "metal_painted"),
    "top": ((0.66, 0.67, 0.68), "metal_painted"),
    "bun": ((0.78, 0.50, 0.22), "metal_painted"),
    "glass": ((0.80, 0.86, 0.88), "glass"),
}
for _k, _t, _c, _r, _l in KINDS:
    MATERIALS["dog_" + _k] = (_c, "metal_painted")
KIND_BASE = {"metal_bare": (1.0, 1.0, 1.0), "metal_painted": (1.0, 1.0, 1.0), "glass": (0.80, 0.86, 0.88)}
GLASS_OPACITY = 0.18
#: Grease: the front roller is `chrome` at 1.0, the back one at this.
GREASE_BACK = 0.45
#: 1.53.0: the same densities, the art drawn and lettered in smooth faces
#: and sampled with filtering (`card_art.atlas` gutters round each tile).
TEXEL = 400
TAG_TEXEL = 800


def vertex_tint(mat_key):
    """``(kind, factor)``; a roller's key carries its grease factor."""
    if mat_key.startswith("roller_"):
        f = float(mat_key.split("_")[1])
        return "metal_bare", tuple(c * f for c in MATERIALS["chrome"][0])
    rgb, kind = MATERIALS[mat_key]
    return kind, tuple(c / b for c, b in zip(rgb, KIND_BASE[kind]))


def resolve(plan_):
    params = plan_.get("params") or {}
    module = plan_.get("module") or {}
    return int(module.get("variant") or params.get("variant") or 0)


def painted_box(part, lo, hi, region, face=2):
    """A box on the painted image: its -Y face (``face`` 2) maps onto
    ``region`` edge to edge; every other face takes the ``edge`` block."""
    p = P.box(part, "paint", lo, hi)
    x0, _y0, z0 = lo
    x1, _y1, z1 = hi

    def uv(i):
        x, _y, z = p["verts"][i]
        return (region, (x - x0) / (x1 - x0), (z - z0) / (z1 - z0))
    p["uvs"] = [tuple(uv(i) for i in f) if k == face else tuple(("edge",) for _ in f)
                for k, f in enumerate(p["faces"])]
    return p


def geometry(w, d, h):
    """The numbers the parts and the art are both drawn from."""
    px0, px1 = -w / 2.0 + PAN_IN, w / 2.0 - PAN_IN
    py0, py1 = -d / 2.0 + PAN_IN + PANEL_D, d / 2.0 - PAN_IN
    zp = CAB_H + PAN_H
    ci = (px1 - px0) / 2.0 - 0.006 - CHEEK_W          # the cheeks' inner faces at +/- ci
    return {"px0": px0, "px1": px1, "py0": py0, "py1": py1, "zp": zp, "ci": ci}


def rollers(d, h):
    """``[(y, z_axis)]`` of every roller, front to back, climbing at
    `RISE_DEG` or less: the back cheek stays under the bun shelf or the
    hood's top."""
    G = geometry(1.0, d, h)
    y0 = G["py0"] + 0.03
    y1 = G["py1"] - 0.03
    n = max(4, int((y1 - y0) / ROLLER_PITCH) + 1)
    z0 = G["zp"] + ROLLER_R + 0.006
    span = (n - 1) * ROLLER_PITCH
    ceiling = shelf_z(h) - 0.06 if shelf_z(h) else h - 0.10
    room = ceiling - CHEEK_UP - z0
    rise = max(0.0, min(math.tan(math.radians(RISE_DEG)), room / span))
    return [(y0 + k * ROLLER_PITCH, z0 + k * ROLLER_PITCH * rise) for k in range(n)]


def shelf_z(h):
    """The bun shelf's underside, or None when the hood is too low for it."""
    room = h - (CAB_H + PAN_H)
    return CAB_H + PAN_H + room * 0.55 if room >= SHELF_ROOM else None


def columns(ci):
    """``[(x0, x1)]``: the width between the cheeks in columns of at least
    `COL_MIN`, at most one a kind."""
    run = 2.0 * ci
    n = max(1, min(len(KINDS), int(run / COL_MIN)))
    cw = run / n
    return [(-ci + k * cw, -ci + (k + 1) * cw) for k in range(n)]


def layout(w, d, h, variant=0):
    out = []
    G = geometry(w, d, h)
    px0, px1, py0, py1, zp, ci = G["px0"], G["px1"], G["py0"], G["py1"], G["zp"], G["ci"]
    # --- the bun cabinet ------------------------------------------------------------------
    out.append(P.box("Roller_Cabinet", "black", (-w / 2.0 + 0.03, -d / 2.0 + 0.05, 0.0),
                     (w / 2.0 - 0.03, d / 2.0 - 0.03, KICK_H + BURY)))
    out.append(P.box("Roller_Cabinet", "cabinet", (-w / 2.0 + 0.012, -d / 2.0 + 0.012, KICK_H),
                     (w / 2.0 - 0.012, d / 2.0 - 0.012, CAB_H - CAB_TOP_T + BURY)))
    out.append(P.box("Roller_Cabinet", "top", (-w / 2.0, -d / 2.0, CAB_H - CAB_TOP_T), (w / 2.0, d / 2.0, CAB_H)))
    out.append(painted_box("Roller_Panel", (-w / 2.0 + 0.05, -d / 2.0 + 0.009, KICK_H + 0.05),
                           (w / 2.0 - 0.05, -d / 2.0 + 0.012 + BURY, CAB_H - CAB_TOP_T - 0.05), "buns"))
    # --- the grill ----------------------------------------------------------------------------
    out.append(P.box("Roller_Grill", "chrome", (px0, py0, CAB_H - BURY), (px1, py1, zp)))
    # the control panel across the pan's front, printed, and its two knobs
    out.append(painted_box("Roller_Panel", (px0 + 0.006, py0 - PANEL_D, CAB_H + 0.006),
                           (px1 - 0.006, py0 + BURY, zp - 0.006), "controls"))
    for kx in knob_x(w):
        out.append(P.translate(P.lay_along_y(P.cyl("Roller_Knob", "black", (0.0, 0.0), 0.017, 0.0, 0.022, segments=10)),
                               (kx, py0 - PANEL_D - 0.022 + BURY, (CAB_H + zp) / 2.0)))
    rs = rollers(d, h)
    cz1 = rs[-1][1] + CHEEK_UP
    for s in (-1, 1):
        x0_, x1_ = sorted((s * ci, s * (ci + CHEEK_W)))
        # 8 mm behind the pan's front: at 4 mm the cheek's front was the
        # control panel's buried back plane
        out.append(P.box("Roller_Grill", "chrome", (x0_, py0 + 0.008, zp - 0.008), (x1_, py1 - 0.006, cz1)))
    n = len(rs)
    for k, (ry, rz) in enumerate(rs):
        g = 1.0 - (1.0 - GREASE_BACK) * k / max(1, n - 1)
        out.append(P.translate(P.lay_along_x(P.cyl("Roller_Roller", "roller_%.3f" % g, (0.0, 0.0), ROLLER_R,
                                                   -ci - 0.006, ci + 0.006, segments=ROLLER_SEG)),
                               (0.0, ry, rz)))

    def rest(g, r):
        """``(y, z)`` of the axis of a round thing of radius ``r`` lying in
        groove ``g``, `REST_GAP` off both rollers."""
        (ya, za), (yb, zb) = rs[g], rs[g + 1]
        half = math.hypot(yb - ya, zb - za) / 2.0
        lift = math.sqrt(max(0.0, (ROLLER_R + r + REST_GAP) ** 2 - half ** 2))
        return (ya + yb) / 2.0, (za + zb) / 2.0 + lift

    # --- the columns: a kind each, a tag in the front groove, dogs behind ------------------
    cols = columns(ci)
    grooves = n - 1
    dogs = 0
    kinds = []
    for c, (cx0, cx1) in enumerate(cols):
        kid, text, _col, r, length = KINDS[(c + variant) % len(KINDS)]
        kinds.append(kid)
        length = min(length, cx1 - cx0 - 0.04)
        mx = (cx0 + cx1) / 2.0
        ty, tz = rest(0, TAG_S / 2.0)
        out.append(painted_box("Roller_Tag", (mx - TAG_L / 2.0, ty - TAG_S / 2.0, tz - TAG_S / 2.0),
                               (mx + TAG_L / 2.0, ty + TAG_S / 2.0, tz + TAG_S / 2.0), "tag_" + kid))
        for g in range(1, grooves):
            if (g * 7 + c * 3 + variant) % 6 == 0:             # one was sold
                continue
            y, z = rest(g, r)
            x0 = mx - length / 2.0 + (0.008 if g % 2 else -0.008)
            out.append(P.rod("Roller_Dog", "dog_" + kid, (x0, y, z), (x0 + length, y, z), r, segments=6))
            dogs += 1
    # the dividers, chrome rods lying on the bank between columns
    (ya, za), (yb, zb) = rs[0], rs[-1]
    for cx0, _cx1 in cols[1:]:
        lift = ROLLER_R + DIVIDER_R + REST_GAP
        out.append(P.rod("Roller_Divider", "chrome", (cx0, ya, za + lift), (cx0, yb, zb + lift), DIVIDER_R, segments=6))
    # --- the hood ---------------------------------------------------------------------------------
    # every pane buried in the posts and at least 4 mm from every face it
    # passes; the posts stand outside the pan on the cabinet; the top
    # overhangs the posts 6 mm
    zt = h
    xa, xb = px0 - 0.020, px0 - 0.004
    fy = (py0 + 0.004, py0 + 0.004 + POST)
    by = (py1 + 0.004, py1 + 0.004 + POST)
    for x0_, x1_ in ((xa, xb), (-xb, -xa)):
        for y0_, y1_ in (fy, by):
            out.append(P.box("Roller_Hood", "chrome", (x0_, y0_, CAB_H - BURY), (x1_, y1_, zt - 0.007)))
    mid = (xa + xb) / 2.0
    zs = shelf_z(h)
    front_lo = zs if zs else (zp + zt) / 2.0
    # 4 mm thick: at 6 its back was 1 mm off the side panes' front ends
    out.append(P.box("Roller_Hood", "glass", (mid, fy[0] + 0.005, front_lo), (-mid, fy[0] + 0.009, zt - 0.003)))
    for sx in (-1, 1):
        x0_, x1_ = sorted((sx * (mid - 0.003), sx * (mid + 0.003)))
        out.append(P.box("Roller_Hood", "glass", (x0_, fy[1] - 0.004, CAB_H + 0.010), (x1_, by[0] + 0.005, zt - 0.003)))
    out.append(P.box("Roller_Hood", "glass", (xa - 0.006, fy[0] - 0.006, zt - 0.010), (-xa + 0.006, by[1] + 0.006, zt)))
    buns = 0
    if zs:
        sx0, sx1 = mid + 0.008, -mid - 0.008
        sy0, sy1 = fy[1] + 0.010, by[0] - 0.004
        out.append(P.box("Roller_Hood", "glass", (sx0, sy0, zs), (sx1, sy1, zs + SHELF_T)))
        nb = max(1, int((sx1 - sx0 - 0.02) / (BUN_L + 0.012)))
        rows = max(1, min(2, int((sy1 - sy0 - 0.02) / (BUN_W + 0.02))))
        for i in range(nb):
            for j in range(rows):
                bx = sx0 + 0.01 + i * (BUN_L + 0.012) + (0.006 if j else 0.0)
                byy = sy0 + 0.02 + j * (BUN_W + 0.02)
                # `pillow`'s crown is METRES over the box's top: at 0.4 the
                # first cut's buns stood 150 mm out of the slot
                out.append(P.pillow("Roller_Bun", "bun", (bx, byy, zs + SHELF_T - 0.005),
                                    (bx + BUN_L, byy + BUN_W, zs + SHELF_T + BUN_H - BUN_CROWN), BUN_CROWN))
                buns += 1
    facts = {"rollers": n, "columns": len(cols), "kinds": kinds, "dogs": dogs, "buns": buns,
             "shelf": zs is not None,
             "collision": ((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h))}
    return out, facts


def knob_x(w):
    G = geometry(w, 0.6, 1.4)
    span = G["px1"] - G["px0"]
    return (G["px0"] + span * 0.55, G["px0"] + span * 0.72)


def plan(w, d, h, variant=0):
    prims, facts = layout(w, d, h, variant)
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


# --- the painted image ----------------------------------------------------------------------

RED = (200, 24, 30)
CREAM = (250, 238, 206)
BROWN = (120, 60, 20)
YELLOW = (255, 208, 40)
WHITE = (250, 250, 246)
INK = (20, 18, 18)
PANEL_BLACK = (16, 16, 18)
STEEL = (170, 172, 176)
#: WHOSE VOICE (1.52.0, `smooth_type.OWNERS`). The warm-buns panel is the
#: shop's own joke, in the shop's face; the control panel's marks and the
#: tags on the rollers are the grill maker's.
SHOP_FACE = ST.owned("shop")
SHOP_COPY = ST.owned("shop_copy")
MAKER_FACE = ST.owned("maker")


def _lift(rgb, by):
    return tuple(max(0.0, min(255.0, c + by)) for c in rgb)


def _outlined(im, text, box, face, colour, outline, cap=None):
    x0, y0, x1, y1 = box
    for dx, dy in ((-1.5, 0), (1.5, 0), (0, -1.5), (0, 1.5), (-1, -1), (1, 1), (-1, 1), (1, -1)):
        im.text(text, (x0 + dx, y0 + dy, x1 + dx, y1 + dy), outline, face, cap=cap)
    return im.text(text, box, colour, face, cap=cap)


def _dog_in_bun(im, box):
    """A hot dog in a bun, drawn: the bun's two halves, the dog between
    them, a squiggle of mustard."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    im.rrect((x0, y0 + h * 0.45, x1, y1), h * 0.25, (214, 160, 90))
    im.vgrad((x0 + 1, y0 + h * 0.47, x1 - 1, y1 - 1), (232, 184, 112), (190, 136, 70))
    im.rrect((x0 + w * 0.06, y0 + h * 0.18, x1 - w * 0.06, y0 + h * 0.62), h * 0.22, (150, 40, 26))
    im.vgrad((x0 + w * 0.08, y0 + h * 0.2, x1 - w * 0.08, y0 + h * 0.6), (180, 60, 40), (120, 30, 20))
    for i in range(5):
        cx = x0 + w * (0.18 + 0.16 * i)
        im.disc(cx, y0 + h * (0.36 if i % 2 else 0.44), h * 0.07, YELLOW)


def _ring(im, cx, cy, r, rgb, t=1.5):
    im.disc(cx, cy, r, rgb)
    im.disc(cx, cy, r - t, PANEL_BLACK)


def art(w, d, h, variant=0):
    """ONE image: the cabinet's buns panel (`buns`), the grill's control
    panel (`controls`), a tag a kind (`tag_*`), and an `edge` block --
    packed with a gutter each tile bleeds into, because the image is sampled
    with filtering (1.52.0). ``{canvas, size, rects, name, said, unset}``."""
    G = geometry(w, d, h)
    BW = int(round((w - 0.10) * TEXEL))
    BH = int(round((CAB_H - CAB_TOP_T - 0.10 - KICK_H) * TEXEL))
    CW = int(round((G["px1"] - G["px0"] - 0.012) * TEXEL))
    CH = int(round((PAN_H - 0.012) * TEXEL))
    TW, TH = int(round(TAG_L * TAG_TEXEL)), int(round(TAG_S * TAG_TEXEL))
    tiles, said = [], []
    # --- the warm-buns panel: cream card, red rules, a dog each end ------------------------
    im = PT.Img(BW, BH, CREAM)
    im.vgrad((0, 0, BW, BH), _lift(CREAM, 4), _lift(CREAM, -14))
    b = max(3, BH // 50)
    im.rect((0, 0, BW, b), RED)
    im.rect((0, BH - b, BW, BH), RED)
    for i in range(0, BW, b * 5):
        im.rect((i, BH - b * 4, i + b * 2.5, BH - b * 2), RED)
    # the name across the whole card, the dogs flanking the line under it
    dw = min(BW * 0.2, BH * 0.9)
    dy = BH * 0.62 + (BH - b * 5 - BH * 0.62 - dw * 0.5) / 2.0
    _dog_in_bun(im, (b * 3, dy, b * 3 + dw, dy + dw * 0.5))
    _dog_in_bun(im, (BW - b * 3 - dw, dy, BW - b * 3, dy + dw * 0.5))
    _outlined(im, PANEL_WORDS[0], (b * 3, b * 2, BW - b * 3, BH * 0.6), SHOP_FACE, RED, BROWN)
    im.text(PANEL_WORDS[1], (b * 4 + dw, BH * 0.62, BW - b * 4 - dw, BH - b * 5), BROWN, SHOP_COPY,
            tracking=0.08)
    im.edge_dark((0, 0, BW, BH), BH * 0.1, 0.12)
    said += list(PANEL_WORDS)
    tiles.append(("buns", im.to_canvas()))
    # --- the control panel: black, a little dog, two lights, two dials, a switch -----------
    im = PT.Img(CW, CH, PANEL_BLACK)
    im.vgrad((0, 0, CW, CH), _lift(PANEL_BLACK, 14), _lift(PANEL_BLACK, -6))
    im.rect((0, 0, CW, 1.5), STEEL)
    _dog_in_bun(im, (6, CH * 0.25, 6 + CH * 1.3, CH * 0.75))
    for lx in (0.26, 0.36):
        im.disc(CW * lx, CH / 2.0, CH * 0.12, (90, 10, 10))
        im.disc(CW * lx, CH / 2.0, CH * 0.08, (240, 40, 40))
        im.disc(CW * lx - CH * 0.03, CH / 2.0 - CH * 0.03, CH * 0.025, (255, 200, 200), 0.8)
    px0 = G["px0"] + 0.006
    for kx in knob_x(w):
        u = (kx - px0) * TEXEL
        _ring(im, u, CH / 2.0, CH / 2.0 - 2, (230, 120, 30), 2)
        _ring(im, u, CH / 2.0, CH / 2.0 - 5, (200, 30, 30), 1.5)
        for a in range(-135, 136, 45):
            t = math.radians(a - 90)
            im.disc(u + math.cos(t) * (CH / 2.0 - 1), CH / 2.0 + math.sin(t) * (CH / 2.0 - 1), 1.2, WHITE)
    sw = (CW * 0.90 - CH * 0.18, CH * 0.2, CW * 0.90 + CH * 0.18, CH * 0.8)
    im.rrect(sw, 2, (230, 30, 30))
    im.bevel(sw, 1, 30.0, 40.0)
    tiles.append(("controls", im.to_canvas()))
    # --- the tags: black tubes, the name in white, a red cap each end --------------------
    for kid, text, _col, _r, _l in KINDS:
        im = PT.Img(TW, TH, PANEL_BLACK)
        im.vgrad((0, 0, TW, TH), _lift(PANEL_BLACK, 30), _lift(PANEL_BLACK, -6))
        cap = max(3, TH // 8)
        im.rect((0, 0, cap, TH), RED)
        im.rect((TW - cap, 0, TW, TH), RED)
        box = (cap + 3, TH * 0.18, TW - cap - 3, TH * 0.82)
        if im.text(text, box, WHITE, MAKER_FACE, min_cap=int(TH * 0.3)) is None:
            im.unset.pop()
            im.text(text.split()[-1], box, WHITE, MAKER_FACE)
        tiles.append(("tag_" + kid, im.to_canvas()))
        said.append(text)
    tiles.append(("edge", PT.Img(24, 24, PANEL_BLACK).to_canvas()))
    A = CA.atlas(tiles, "rollerart", gutter=CA.SMOOTH_GUTTER, bleed=True)
    A["said"] = said
    A["unset"] = [s for _k, c in tiles for s in getattr(c, "unset", [])]
    return A
