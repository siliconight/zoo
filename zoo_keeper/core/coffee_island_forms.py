"""The convenience store's coffee island, decided in pure Python: the brewers,
the carafes on their warmers, the cup towers and syrups, and the round sign
over it -- and every pixel of the sign and the brewers' badges.

Zoo 1.9.0, species `coffee_island`. Asked for by name, 2026-09-28: "do the
coffee counter next". What it has to be comes from the walker:

  * the store references (docs/SET_DRESSING_REFERENCES.md, 2026-09-15): "a
    long counter of glass coffee pots on warming burners in a row,
    orange-lidded (decaf) and black-lidded, several per blend, with the
    brewers behind"; "a CONDIMENT ISLAND -- a waist-high wood-and-steel island
    with round cup wells, towers of stacked paper cups, lids, stirrers and
    creamer"; the 1990s store's "self-serve coffee station ... under a round
    coffee sign"; the Daily News cappuccino bar's syrup row and cup stacks;
  * four photos sent with the request, 2026-09-28, of a 1985 pour-over
    brewer and its carafes -- "a good look for the carafe at least" -- and
    one of a later commercial three-warmer model. The brewer and carafe here
    are the 1985 one, described below; the commercial one is a candidate for
    a second form and is not built.

THE BREWER, as the photos show it: a brushed stainless HOOD across the top
with two warmers on it (one often standing empty); on the hood's front two
rocker switches, each beside a red lamp, and a maker's badge plaque; a
WOODGRAIN column down the right-hand third from the base to the hood; a
stainless BASE PLATE projecting a little forward, carrying a warmer in the
open BAY to the left of the column; a stainless brew FUNNEL hanging under the
hood over that warmer, with a black handle. The maker's real badge is a mark
and stays out; the plaque carries an invented one (`BADGE`).

THE CARAFE: a squat glass BULB wider than it is tall, a plastic COLLAR band
round its upper third in the lid colour -- black regular, orange decaf -- a
pour SPOUT on one side and a hooked HANDLE of the same plastic on the other,
off the collar and down. The coffee shows through the glass.

WHY AN ISLAND. Deli Counter places the piece as a free-standing volume --
`coffee_island` 3.0 x 2.0 x 1.1 in six store specs, `coffee_food_island`
4.0 x 3.0 x 1.0 in `gas_station_a02` and `fuel_stop_heist` -- which until
this species existed built as a bare `counter` or, too deep for that genome,
the plain `prop` box. People walk round it, so both long faces are served:
brewers stand back to back along the spine, and the one facing +Y is the one
facing -Y turned half round, so each reads the right way from its own side.

WHAT IS BUILT, in the recipe frame (metres, Z up, floor at 0, CENTRE pivot,
x along the island's length):

  * the ISLAND: a recessed kick, a wood body, a steel top that IS the slot's
    footprint and height -- the module fits its slot exactly, and everything
    else is dressing standing on it;
  * STATIONS along the spine, each a pair of brewers back to back (above);
  * a BURNER ROW along each long edge in front of the brewers -- a steel
    strip with two warmers a station -- when the island is deep enough;
  * the CUP END (+X): a steel cup rack with three sizes of nested cup stack
    and a lid stack, each side;
  * the SYRUP END (-X): syrup bottles with pumps, a creamer tub and a
    stirrer cup, each side;
  * the SIGN: a round double-sided disc on a post over the middle.

THE DRAW-CALL BUDGET IS THE DESIGN, not a clean-up afterwards (CLAUDE.md;
Zoo 1.8.0's service counter merge is the lesson). Every primitive's ``mat``
key belongs to one of FOUR surface kinds, colour-only variation rides the
`Wear` vertex colour (`vertex_tint`, `geometry.tint_wear`) so
`merge.pack_by_material` packs each kind into one mesh, the glass is one
see-through material, and the sign and every badge share one painted image.
Five submissions, whatever the island's size.

NO TWO FACES SHARE A PLANE (`prims.coincident_pairs` is empty): every part
that stands on another is buried into it at a depth no neighbour uses.
"""
from __future__ import annotations

import math
import re
import zlib

from . import pixel_type as pt
from . import prims as P
from .vending_forms import Canvas

#: Deli Counter's volumes (long side first), then the genome's range.
DC_SIZES = ((3.0, 2.0, 1.1), (4.0, 3.0, 1.0))
#: WIDTH FROM 2.6 m: measured, a 2.0 m island left no room for a brewer
#: station between the cup end, the syrup end and the sign post's clearance
#: -- a coffee island with no coffee. At 2.6 one pair fits.
RANGES = {"width": (2.6, 6.0), "depth": (1.4, 3.5), "height": (0.85, 1.2)}

# --- the island ---------------------------------------------------------------
BASE_H = 0.09
BASE_IN = 0.05            # the kick's recess each side
TOP_T = 0.04
TOP_LIP = 0.03            # the top past the body each side
BURY = 0.004              # a part standing on another, into it

# --- the brewer, in its own frame: u across (viewer's left to right), v
# --- forward from its back, z up from the island's top -------------------------
BREWER_W = 0.40
BREWER_D = 0.40
BREWER_GAP = 0.02         # between a back-to-back pair
PLATE_T = 0.025           # the base plate
PLATE_OUT = 0.02          # the plate past the hood's front
HOOD_Z = (0.30, 0.50)     # the hood's bottom and top
COLUMN_W = 0.15           # the woodgrain column, the right-hand side
BAY_W = BREWER_W - COLUMN_W
TOP_U = (0.09, 0.31)      # the two warmers on the hood, across
FUNNEL_Z = (0.22, 0.30)   # the funnel hangs from the hood's underside
FUNNEL_R = (0.060, 0.082) # at its bottom and top
HANDLE_OVER = 0.03        # a carafe handle past the brewer's right edge
#: The first station's centre clears the post by the brewer's half width,
#: the handle overhang and a centimetre.
SIGN_CLEAR = 0.14
STATION_PITCH = 0.48
MAX_STATIONS = 6
END_ZONE = 0.60           # each end of the top kept for cups / syrups

# --- the burner row ---------------------------------------------------------------
FRONT_ROW_MIN_HALF = 0.85 # the island's half depth for a burner row
FRONT_ROW_Y = 0.62        # a burner row's centre from the spine (|y|), at least
FRONT_ROW_EDGE = 0.22     # ...and this far in from the island's edge
FRONT_DX = 0.11           # its two carafes either side of the station
STRIP_T = 0.03

# --- a carafe (its own frame: centre on the axis, base at z = 0) ----------------
WARMER_R = 0.080
WARMER_T = 0.012
#: (z, r) up the glass bulb: a squat sphere, wider than it is tall, closing
#: to a neck under the collar.
BULB = ((0.0, 0.048), (0.018, 0.070), (0.050, 0.082), (0.085, 0.076), (0.110, 0.062))
#: (z, r) up the coffee inside it, to a little over half full.
COFFEE = ((0.008, 0.044), (0.020, 0.064), (0.050, 0.076), (0.075, 0.072))
#: (z, r) up the collar band -- the top quarter, as the photos have it; the
#: first cut covered half the bulb and read as a lid, not a band. It starts
#: 4 mm proud of the glass (r 0.065 at z 0.105).
COLLAR = ((0.105, 0.069), (0.132, 0.068), (0.146, 0.060))
HANDLE_R = 0.009
#: The handle, from the collar out and down: (r, z) points in the carafe's
#: frame along its handle side.
HANDLE_PTS = ((0.068, 0.140), (0.112, 0.150), (0.122, 0.072))
SEG = 10

# --- the ends ---------------------------------------------------------------------
CUP_SIZES = ((0.034, 0.044, 0.34), (0.038, 0.049, 0.40), (0.042, 0.054, 0.46))  # r0, r1, h
CUP_RACK_H = 0.05
SYRUPS = 4
SYRUP_R = 0.034
SYRUP_H = 0.21

# --- the sign ---------------------------------------------------------------------
POST_R = 0.024
SIGN_R = 0.32
SIGN_T = 0.035
SIGN_CZ = 1.28            # the disc's centre above the top
SIGN_SEG = 24
SIGN_PX = 256             # the disc's art is SIGN_PX square
BADGE_PX = (96, 28)       # the brewer's plaque, below the disc in the image
BADGE_M = (0.12, 0.035)   # the plaque on the hood, metres

#: Colours (linear, as the rest of Zoo's recipes) and their surface kind.
MATERIALS = {
    "wood": ((0.34, 0.22, 0.13), "wood_stained"),
    "kick": ((0.10, 0.07, 0.05), "wood_stained"),
    "grain": ((0.24, 0.14, 0.07), "wood_stained"),       # the brewer's column
    "steel": ((0.62, 0.63, 0.64), "metal_bare"),
    "warmer": ((0.18, 0.18, 0.19), "metal_bare"),
    "rocker": ((0.10, 0.07, 0.05), "plastic"),
    "lamp": ((0.55, 0.05, 0.04), "plastic"),
    "black": ((0.03, 0.03, 0.03), "plastic"),
    "lid_reg": ((0.03, 0.03, 0.03), "plastic"),
    "lid_decaf": ((0.85, 0.30, 0.04), "plastic"),
    "coffee": ((0.06, 0.03, 0.012), "plastic"),
    "cup": ((0.90, 0.88, 0.84), "plastic"),
    "cream": ((0.86, 0.82, 0.70), "plastic"),
    "syrup_a": ((0.55, 0.24, 0.05), "plastic"),     # hazelnut
    "syrup_b": ((0.80, 0.62, 0.30), "plastic"),     # vanilla
    "syrup_c": ((0.38, 0.12, 0.04), "plastic"),     # caramel
    "syrup_d": ((0.42, 0.05, 0.08), "plastic"),     # cherry
    "glass": ((0.80, 0.84, 0.85), "glass"),
}
#: The one material each kind builds with; parts carry colour / base in Wear.
KIND_BASE = {"wood_stained": (1.0, 1.0, 1.0), "metal_bare": (1.0, 1.0, 1.0),
             "plastic": (1.0, 1.0, 1.0), "glass": (0.80, 0.84, 0.85)}
GLASS_OPACITY = 0.30
_VARIANT = re.compile(r"_n\d+(?=_|$)")


def vertex_tint(mat_key):
    """``(kind, factor)``: the kind a ``mat`` key builds with and the colour
    its parts multiply into `Wear` to land on `MATERIALS`'s."""
    rgb, kind = MATERIALS[mat_key]
    return kind, tuple(c / b for c, b in zip(rgb, KIND_BASE[kind]))


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def resolve(plan_):
    """``(key, variant)``: the stem without its variant, and the variant."""
    params = plan_.get("params") or {}
    module = plan_.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    key = _VARIANT.sub("", module.get("stem") or "") or "coffee_island"
    return key, variant


# --- primitives this module needs that `prims` does not have -------------------------

def lathe(part, mat, cx, cy, z0, profile, segments=SEG):
    """A closed solid of revolution about the vertical through (cx, cy):
    ``profile`` is ``((z, r), ...)`` from the bottom up, offset by ``z0``;
    capped at both ends, faces wound outward (as `prims.cyl`)."""
    n = int(segments)
    verts = []
    for z, r in profile:
        for k in range(n):
            a = 2.0 * math.pi * k / n
            verts.append((cx + r * math.cos(a), cy + r * math.sin(a), z0 + z))
    faces = [tuple(reversed(range(n)))]
    for ring in range(len(profile) - 1):
        b0, b1 = ring * n, (ring + 1) * n
        for k in range(n):
            k1 = (k + 1) % n
            faces.append((b0 + k, b0 + k1, b1 + k1, b1 + k))
    top = (len(profile) - 1) * n
    faces.append(tuple(range(top, top + n)))
    return P.mesh(part, mat, verts, faces)


def carafe(x, y, z0, decaf, handle_dir):
    """One carafe standing on ``z0`` (buried `BURY`): the glass bulb, the
    coffee, the collar, the spout and the handle. The handle points to
    ``handle_dir`` in x (+1 or -1), the spout the other way."""
    lid = "lid_decaf" if decaf else "lid_reg"
    zb = z0 - BURY
    out = [lathe("Coffee_Carafe", "glass", x, y, zb, BULB),
           lathe("Coffee_Carafe", "coffee", x, y, zb, COFFEE),
           lathe("Coffee_Carafe", lid, x, y, zb, COLLAR)]
    # the spout: a lip out of the collar's top, opposite the handle
    sx0, sx1 = sorted((x - handle_dir * 0.055, x - handle_dir * 0.088))
    out.append(P.box("Coffee_Carafe", lid, (sx0, y - 0.016, zb + 0.128), (sx1, y + 0.016, zb + 0.142)))
    # the handle: out of the collar, then down
    pts = [(x + handle_dir * r, y, zb + z) for r, z in HANDLE_PTS]
    out.append(P.rod("Coffee_Carafe", lid, pts[0], pts[1], HANDLE_R, segments=6))
    out.append(P.rod("Coffee_Carafe", lid, pts[1], pts[2], HANDLE_R, HANDLE_R * 0.8, segments=6))
    return out


def _warmer(x, y, z, bury=BURY):
    return P.cyl("Coffee_Warmer", "warmer", (x, y), WARMER_R, z - bury, z - bury + WARMER_T,
                 segments=SEG)


# --- the brewer -------------------------------------------------------------------------

def brewer(xc, h, key, variant, station, side):
    """One brewer standing on the island's top at ``h``, its back against
    the spine and its front toward ``side`` (-1 or +1 in y), centred at
    ``xc``. Built facing -Y and turned half round for +Y, so the column is
    on the viewer's right from either side. ``(prims, carafes, decafs)``."""
    x0 = xc - BREWER_W / 2.0                      # the brewer's left, seen from -Y

    def at(u, v):                                 # the brewer frame -> world, facing -Y
        return (x0 + u, -(BREWER_GAP / 2.0 + v))

    def box(part, mat, u0, v0, z0, u1, v1, z1):
        (xa, ya), (xb, yb) = at(u0, v0), at(u1, v1)
        return P.box(part, mat, (min(xa, xb), min(ya, yb), h + z0), (max(xa, xb), max(ya, yb), h + z1))
    out = []
    D = BREWER_D
    # the base plate, the woodgrain column, the bay's back, the hood
    out.append(box("Coffee_Brewer", "steel", 0.0, 0.0, -BURY, BREWER_W, D + PLATE_OUT, PLATE_T))
    out.append(box("Coffee_Brewer", "grain", BAY_W + 0.004, 0.012, PLATE_T - 0.006,
                   BREWER_W - 0.006, D - 0.018, HOOD_Z[0] + 0.006))
    # the bay's back panel stops 4 mm short of the column: overlapping it by
    # 8 mm put their tops and bottoms 2 mm apart, one coincident pair a brewer
    out.append(box("Coffee_Brewer", "steel", 0.008, 0.004, PLATE_T - 0.008,
                   BAY_W - 0.004, 0.030, HOOD_Z[0] + 0.008))
    out.append(box("Coffee_Brewer", "steel", -0.004, -0.002, HOOD_Z[0], BREWER_W + 0.004, D + 0.004, HOOD_Z[1]))
    # the hood's face: two rockers with a red lamp beside each, and the plaque
    fv = D + 0.004
    for row, zc in enumerate((0.435, 0.365)):
        out.append(box("Coffee_Brewer", "rocker", 0.070, fv - 0.004, zc - 0.028, 0.105, fv + 0.012, zc + 0.028))
        out.append(box("Coffee_Brewer", "lamp", 0.118, fv - 0.005, zc - 0.026, 0.150, fv + 0.010, zc + 0.026))
    bu0 = BREWER_W - 0.05 - BADGE_M[0]
    out.append(badge_prim(at, h, bu0, fv, 0.42))
    # the funnel under the hood over the bay's warmer, and its handle
    bu = BAY_W / 2.0
    bvc = D / 2.0 + 0.02
    fx, fy = at(bu, bvc)
    out.append(lathe("Coffee_Funnel", "steel", fx, fy, h + FUNNEL_Z[0],
                     ((0.0, FUNNEL_R[0]), (FUNNEL_Z[1] - FUNNEL_Z[0] + 0.006, FUNNEL_R[1]))))
    out.append(box("Coffee_Funnel", "black", bu - 0.016, bvc + FUNNEL_R[1] - 0.006, 0.230,
                   bu + 0.016, bvc + FUNNEL_R[1] + 0.060, 0.265))
    # the warmers and what stands on them
    # ONE CARAFE A BREWER, in its bay under the funnel -- the one brewing.
    # The walker, 2026-09-28, on the first render: "we can have 20% as many
    # carafes". That render had 20 on a 3 m island: every warmer full. One a
    # brewer is exactly a fifth of the warmers on both of Deli Counter's
    # sizes, and every other warmer -- two on the hood, the burner row --
    # stands empty, as one in the walker's photo does. Decaf by station, not
    # by chance, so both lids are always on the island: the odd stations'.
    carafes, decafs = [], []
    wx, wy = at(bu, bvc)
    out.append(_warmer(wx, wy, h + PLATE_T))
    decaf = station % 2 == 1
    carafes += carafe(wx, wy, h + PLATE_T + WARMER_T - BURY, decaf, +1)
    decafs.append(decaf)
    for tu in TOP_U:
        tx, ty = at(tu, D / 2.0)
        out.append(_warmer(tx, ty, h + HOOD_Z[1]))
    everything = out + carafes
    if side > 0:
        # a turn keeps winding and the badge's corner mapping (`_map` copies)
        everything = [P.rotate_z(p, math.pi, about=(xc, 0.0)) for p in everything]
    return everything, len(decafs), sum(decafs)


def warmers(n_stations, front_row):
    """How many warmers the island carries: three a brewer, two a brewer
    more on a burner row."""
    return n_stations * 2 * (3 + (2 if front_row else 0))


def stations(w):
    """x centres of the brewer stations: every `STATION_PITCH` from the
    post outward, symmetric, within the run between the end zones."""
    x_hi = w / 2.0 - END_ZONE
    out = []
    x = SIGN_CLEAR + BREWER_W / 2.0 + HANDLE_OVER + 0.01
    while x + BREWER_W / 2.0 + HANDLE_OVER <= x_hi and len(out) + 2 <= MAX_STATIONS:
        out += [-x, x]
        x += STATION_PITCH
    return sorted(out)


def layout(w, d, h, key="coffee_island", variant=0):
    """Every part at slot (w, d, h): ``(island, dressing, facts)``. The
    island is the part that fits the slot; the dressing stands on it."""
    island, dress = [], []
    half_d = d / 2.0
    # --- the island ---------------------------------------------------------------
    island.append(P.box("Coffee_Kick", "kick", (-w / 2.0 + BASE_IN, -half_d + BASE_IN, 0.0),
                        (w / 2.0 - BASE_IN, half_d - BASE_IN, BASE_H + BURY)))
    island.append(P.box("Coffee_Body", "wood", (-w / 2.0 + TOP_LIP, -half_d + TOP_LIP, BASE_H),
                        (w / 2.0 - TOP_LIP, half_d - TOP_LIP, h - TOP_T + BURY)))
    island.append(P.box("Coffee_Top", "steel", (-w / 2.0, -half_d, h - TOP_T), (w / 2.0, half_d, h)))

    # --- the stations -----------------------------------------------------------------
    xs = stations(w)
    n_carafes = n_decaf = 0
    front_row = half_d >= FRONT_ROW_MIN_HALF
    for i, xc in enumerate(xs):
        for side in (-1, 1):
            prims, n, dc = brewer(xc, h, key, variant, i, side)
            dress += prims
            n_carafes += n
            n_decaf += dc
            if front_row:
                fy = side * max(FRONT_ROW_Y, half_d - FRONT_ROW_EDGE)
                dress.append(P.box("Coffee_Burner", "steel", (xc - 0.21, fy - 0.10, h - BURY - 0.002),
                                   (xc + 0.21, fy + 0.10, h + STRIP_T)))
                for dx in (-FRONT_DX, FRONT_DX):         # empty: see `brewer`
                    dress.append(_warmer(xc + dx, fy, h + STRIP_T))

    # --- the cup end (+X) -----------------------------------------------------------------
    cx0 = w / 2.0 - END_ZONE + 0.06
    for side in (-1, 1):
        ry = side * 0.22
        dress.append(P.box("Coffee_CupRack", "steel", (cx0, ry - 0.09, h - BURY),
                           (cx0 + 3 * 0.13 + 0.04, ry + 0.09, h + CUP_RACK_H)))
        for j, (r0, r1, ch) in enumerate(CUP_SIZES):
            x = cx0 + 0.08 + j * 0.13
            z0 = h + CUP_RACK_H - BURY - 0.002 * j
            dress.append(P.cyl("Coffee_Cups", "cup", (x, ry), r0, z0, z0 + ch, segments=SEG, r_top=r1))
        lx = cx0 + 0.08 + 0.13
        dress.append(P.cyl("Coffee_Cups", "cup", (lx, side * 0.40), 0.056, h - BURY - 0.001,
                           h + 0.12, segments=SEG))

    # --- the syrup end (-X) ---------------------------------------------------------------
    sx0 = -w / 2.0 + 0.12
    flavours = ("syrup_a", "syrup_b", "syrup_c", "syrup_d")
    for side in (-1, 1):
        sy = side * 0.30
        for j in range(SYRUPS):
            x = sx0 + j * 0.09
            fl = flavours[(_h(key, variant, side, j) + j) % len(flavours)]
            zb = h - BURY - 0.0015 * j
            dress.append(P.cyl("Coffee_Syrup", "glass", (x, sy), SYRUP_R, zb, zb + SYRUP_H, segments=SEG))
            dress.append(P.cyl("Coffee_Syrup", fl, (x, sy), SYRUP_R - 0.006, zb + 0.012,
                               zb + SYRUP_H * 0.8, segments=SEG))
            pz = zb + SYRUP_H - 0.006
            dress.append(P.cyl("Coffee_Syrup", "black", (x, sy), 0.022, pz, pz + 0.03, segments=8))
            dress.append(P.cyl("Coffee_Syrup", "black", (x, sy), 0.006, pz + 0.024, pz + 0.08, segments=6))
            ny0, ny1 = sorted((sy, sy + side * 0.05))
            dress.append(P.box("Coffee_Syrup", "black", (x - 0.008, ny0, pz + 0.07),
                               (x + 0.008, ny1, pz + 0.085)))
        cy_ = side * (half_d - 0.16)
        dress.append(P.box("Coffee_Condiment", "cream", (sx0 - 0.05, cy_ - 0.07, h - BURY - 0.003),
                           (sx0 + 0.13, cy_ + 0.07, h + 0.07)))
        dress.append(P.cyl("Coffee_Condiment", "cup", (sx0 + 0.24, cy_), 0.04,
                           h - BURY - 0.005, h + 0.10, segments=SEG))

    # --- the sign ------------------------------------------------------------------------
    sz = h + SIGN_CZ
    dress.append(P.cyl("Coffee_SignPost", "steel", (0.0, 0.0), POST_R, h - BURY - 0.007,
                       sz - SIGN_R + 0.02, segments=8))
    dress.append(sign_prim(sz))
    facts = {"stations": xs, "front_row": front_row, "carafes": n_carafes, "decaf": n_decaf,
             "sign_z": sz, "collision": ((-w / 2.0, -half_d, 0.0), (w / 2.0, half_d, h))}
    return island, dress, facts


def badge_prim(at, h, u0, v_face, zc):
    """The brewer's plaque on the hood's front, ``BADGE_M`` in size: a thin
    slab whose front face maps onto the badge's rows of the painted image
    (``("badge", u, v)`` corners) and whose other faces take the dark pixel.
    ``at`` is the brewer's frame; the brewer faces -Y there, so its front is
    the slab's -Y face."""
    bw, bh = BADGE_M
    (xa, ya) = at(u0, v_face - 0.004)
    (xb, yb) = at(u0 + bw, v_face + 0.006)
    x0, x1 = min(xa, xb), max(xa, xb)
    y0, y1 = min(ya, yb), max(ya, yb)
    z0, z1 = h + zc - bh / 2.0, h + zc + bh / 2.0
    p = P.box("Coffee_Badge", "sign", (x0, y0, z0), (x1, y1, z1))
    # P.box faces: 0 bottom, 1 top, 2 -Y (the front), 3 +X, 4 +Y, 5 -X
    front = 2

    def uv(i):
        x, _y, z = p["verts"][i]
        return ("badge", (x - x0) / (x1 - x0), (z - z0) / (z1 - z0))
    p["uvs"] = [tuple(uv(i) for i in f) if k == front else tuple(("dark",) for _ in f)
                for k, f in enumerate(p["faces"])]
    p["face_mats"] = ["paint"] * len(p["faces"])
    return p


def sign_prim(zc):
    """The round sign: a disc of `SIGN_SEG` sides, axis along y, centred on
    the spine at height ``zc``. Its two caps are painted -- each mapped so
    the art reads the right way round from its own side -- and its rim takes
    a dark pixel."""
    n = SIGN_SEG
    t = SIGN_T / 2.0
    verts = []
    for yy in (-t, t):
        for k in range(n):
            a = 2.0 * math.pi * k / n
            verts.append((SIGN_R * math.cos(a), yy, zc + SIGN_R * math.sin(a)))
    front = tuple(range(n))                   # y = -t; wound to face -Y
    back = tuple(reversed(range(n, 2 * n)))   # y = +t; wound to face +Y
    faces = [front, back]
    for k in range(n):
        k1 = (k + 1) % n
        faces.append((k, n + k, n + k1, k1))
    p = P.mesh("Coffee_Sign", "sign", verts, faces)

    def uv(i, mirror):
        x, _y, z = verts[i]
        u = 0.5 + (x / (2.0 * SIGN_R)) * (-1.0 if mirror else 1.0)
        return ("art", u, 0.5 + (z - zc) / (2.0 * SIGN_R))
    # seen from -Y, +x is to the viewer's right; from +Y it is to their left
    p["uvs"] = [tuple(uv(i, False) for i in front), tuple(uv(i, True) for i in back)] + \
               [tuple(("dark",) for _ in f) for f in faces[2:]]
    p["face_mats"] = ["paint"] * len(faces)
    return p


def plan(w, d, h, key="coffee_island", variant=0):
    """``{island, dressing, facts}``: the island fitted exactly to the slot
    (its top IS the slot's footprint and height, by construction)."""
    island, dress, facts = layout(w, d, h, key, variant)
    return {"island": island, "dressing": dress, "facts": facts}


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


# --- the art -------------------------------------------------------------------------------

#: The sign's colourways by variant: disc, ring, ink. Invented; not a
#: convenience chain's red-and-yellow (brands.py's rule).
COLOURWAYS = (((24, 78, 52), (226, 206, 150), (246, 238, 214)),     # bottle green, cream
              ((70, 36, 20), (226, 176, 92), (250, 236, 206)),      # roast brown, tan
              ((22, 44, 82), (214, 196, 150), (240, 236, 222)),     # navy, sand
              ((96, 22, 26), (232, 212, 170), (248, 240, 222)))     # oxblood, parchment
STORE = "FLAPPHAS"
WORDS = ("COFFEE", "FRESH BREWED")
#: The brewers' maker, invented: the walker's photos carry a real maker's
#: plaque, black with a gold rule and cream lettering, and this keeps the
#: plaque and not the mark.
BADGE = "DRIP KING"


def sign_art(variant):
    """One image for every painted surface on the island: the sign's disc
    (rows 0..SIGN_PX), the brewers' badge plaque under it, and a dark pixel
    block for rims and edges. ``{canvas, size, rects, said, name}``; rects
    are pixel boxes (x0, y0, x1, y1), row 0 at the top."""
    disc, ring, ink = COLOURWAYS[variant % len(COLOURWAYS)]
    S = SIGN_PX
    bw, bh = BADGE_PX
    H = S + bh + 6
    c = Canvas(S, H, (12, 12, 12))
    cx = cy = S / 2.0
    for y in range(S):
        for x in range(S):
            r = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r <= S / 2.0 - 1:
                c.px(x, y, ring if r > S / 2.0 - 14 else disc)
            if S / 2.0 - 20 < r <= S / 2.0 - 17:
                c.px(x, y, ring)
    said = []

    def centred(text, scale, y, colour, x0=0, width=S):
        m = pt.trim(pt.render(text, scale))
        c.mask(m, x0 + (width - len(m[0])) // 2, y, colour)
        said.append(text)
        return y + len(m)
    y = centred(STORE, 2, 44, ring)
    y = centred(WORDS[0], 4 if pt.ink_width(WORDS[0], 4) <= S - 60 else 3, y + 14, ink)
    centred(WORDS[1], 1, y + 10, ring)
    # the cup: a tapered body, a band, and three wisps of steam
    bx, by, cw, ch = S // 2 - 18, 176, 36, 38
    for yy in range(ch):
        inset = yy * 5 // ch
        c.rect(bx + inset, by + yy, bx + cw - inset, by + yy + 1, ink)
    c.rect(bx + 2, by + 12, bx + cw - 2, by + 20, ring)
    for k, sx in enumerate((bx + 8, bx + 18, bx + 28)):
        for yy in range(20):
            xx = sx + (2 if (yy // 4 + k) % 2 else -2)
            c.rect(xx, by - 26 + yy, xx + 2, by - 25 + yy, ink)
    # the badge plaque: black, a gold rule inset, cream lettering
    b = (0, S, bw, S + bh)
    c.rect(*b, (14, 12, 10))
    gold = (196, 160, 80)
    c.rect(b[0] + 2, b[1] + 2, b[2] - 2, b[1] + 3, gold)
    c.rect(b[0] + 2, b[3] - 3, b[2] - 2, b[3] - 2, gold)
    c.rect(b[0] + 2, b[1] + 2, b[0] + 3, b[3] - 2, gold)
    c.rect(b[2] - 3, b[1] + 2, b[2] - 2, b[3] - 2, gold)
    m = pt.trim(pt.render(BADGE, 1))
    c.mask(m, (bw - len(m[0])) // 2, S + (bh - len(m)) // 2, (238, 226, 196))
    said.append(BADGE)
    dark = (bw + 2, S + 1, bw + 6, S + 5)
    c.rect(*dark, (12, 12, 12))
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (S, H), "said": said,
            "rects": {"art": (0, 0, S, S), "badge": b, "dark": dark},
            "name": f"coffeesign_v{variant % len(COLOURWAYS)}_{S}x{H}_{digest:08x}"}
