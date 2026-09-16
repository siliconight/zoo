"""What is left out on a top: the stock a desk, a table, a counter or a
filing cabinet carries, planned in pure Python so the layout is unit-tested.

"Its just a bunch of chairs and tables with nothing on it, boring" (the
walker, in a country_club_a01 basement on cold run 9052). Zoo's tables have
had an ``ATT_surface_center`` socket and its desks, counters and filing
cabinets theirs for months, and nothing ever read one. `_shelf_stock.py` is
the precedent for stock built INTO the host recipe -- deterministic, no
overhang, no shared planes, contrast-tested -- and this is its twin for a
top surface. The host calls `plan_surface` once per bay of its top from its
own "stock" stream, so the host's wear noise is exactly what it was, and a
host whose ``stock`` param is ``none`` (the genome default) never draws
from that stream at all: its geometry is byte for byte what it was.

WHO LIVES HERE. The ``stock`` flavour is the room's, and Deli Counter knows
the room (see `kit.DRESSING_FIELDS`):

  * ``office``  -- a CRT and its keyboard facing the sitter, folders with
    forms on them, a desk phone, a mug, a pencil cup;
  * ``bar``     -- beer bottles in a loose knot, pints on coasters, an
    ashtray with two butts in it, a napkin holder;
  * ``bar_dense`` -- THE CLUB'S BAR TOP (0.92.0), and not a denser draw
    of the flavour above: LANES, not clusters. The walker's photo is a
    liquor row along the WHOLE top with towers of rocks glasses and
    cocktail glasses among it, and a speed rail of spouted bottles on the
    service (+Y) run. A cluster planner cannot draw a row, and making
    ``bar`` dense would have moved every cocktail table and stage rail in
    the library, which the same photo is not about;
  * ``kitchen`` -- ketchup and mustard with the salt and pepper, a tray
    with soda cups on it, a napkin holder;
  * ``vault``   -- cash straps in columns, zippered deposit bags, ledgers;
  * ``storage`` -- a carton or a banker's box, a clipboard, forms;
  * ``cards``   -- THE CARD SHOP'S PLAY TABLE (0.95.0): a playmat with a
    printed border and a deck of cards on it, piles of loose cards, deck
    boxes, and dice. NOT TEXTURED, and that is a limit rather than a
    choice: `prim_mesh.build_stock` has no textured path, so a mat is a
    colour with a border and not art -- the same trade this module's own
    `bar_dense` records for its bottle labels. What the textured version
    would buy is the game's frame on a mat nobody is nearer than a metre
    to; what it would cost is one atlas per host and an exception to the
    rule that stock is flat.

CLUSTERS, NOT SCATTER (SET_DRESSING_REFERENCES). A top gets a few clusters,
about one per AREA_PER_CLUSTER of its area; a cluster is a group of items
placed together about one anchor (the workstation is a monitor with its
keyboard in front of it, not a monitor here and a keyboard somewhere).

OFF KILTER, BY A SEEDED RULE. Every item is turned off its cluster's line
by up to ``min(MAX_JITTER_DEG, JITTER_K / size)`` degrees, ``size`` its
longest side in metres -- a mug any way at all, a 0.4 m monitor about five
degrees -- and items stacked in one (folders, straps, ledgers) turn at
least MIN_TURN_DEG from the one below, so no two of their sides are
parallel.

THE RULES EVERY ITEM KEEPS, each a thing a render or a z-buffer punishes:

  * NOTHING OVERHANGS. Every vertex lies inside the top less EDGE.
  * NOTHING SHARES A PLANE. Item footprints (their rotated bounds, grown by
    DETAIL) keep MIN_GAP apart, so no face of one item can lie in a face of
    another where the two overlap. An item's lowest faces sit SINK below
    the top, inside it; no part of an item has a face between the top and
    SINK + 4 mm above it. `tests/test_surface_stock.py` runs the
    coincident-face measurement over items and the host top for every
    flavour, many tops and seeds.
  * IT CONTRASTS. A finish has candidate colours -- a light and a dark --
    and takes whichever contrasts most with the host's top colour; the
    tests hold a luminance ratio of at least 1.4 (`_shelf_stock`'s number)
    against every style colour of every host.
  * DETERMINISTIC from the rng passed in.

Coordinates: metres in the host's frame, base-up, -Y the host's front;
``facing`` is the yaw (radians) that turns an item's front (-Y) toward the
person using the top. Colours are linear RGB.
"""
from __future__ import annotations

import math

from ..core import carton_forms as CF
from ..core import liquor_brands as LB
from ..core import prims as P
from ..core.brands import srgb_to_linear

FLAVOURS = ("office", "bar", "kitchen", "vault", "storage", "bar_dense",
            "cards")
EDGE = 0.02            # items stay this far inside the top's edges
MIN_GAP = 0.012        # between item footprints (each grown by DETAIL)
SINK = 0.003           # an item's lowest faces sit this far inside the top
DETAIL = 0.003
MIN_TURN_DEG = 1.0
MAX_JITTER_DEG = 15.0
JITTER_K = 2.0         # degrees x metres: the off-kilter rule's constant
HEADROOM = 0.02

#: finish -> ([candidate linear RGB, ...], kind). The first candidate is the
#: one the object "is"; the others exist for a host it would vanish against.
FINISHES = {
    "beige_plastic": ([[0.62, 0.58, 0.48], [0.10, 0.10, 0.11]], "plastic"),
    "key_plastic": ([[0.30, 0.28, 0.24], [0.62, 0.58, 0.48]], "plastic"),
    "screen": ([[0.02, 0.03, 0.03]], "plastic"),
    "led": ([[0.05, 0.40, 0.08]], "plastic"),
    # forms: white paper, and the pink copy of a carbon set for a light top
    "paper": ([[0.82, 0.80, 0.74], [0.62, 0.30, 0.34]], "paper"),
    "manila": ([[0.60, 0.46, 0.22], [0.07, 0.20, 0.11]], "paper"),
    "mug": ([[0.80, 0.78, 0.72], [0.05, 0.08, 0.24], [0.30, 0.05, 0.07]], "plastic"),
    "pencil": ([[0.75, 0.55, 0.05]], "wood"),
    "glass_brown": ([[0.16, 0.07, 0.02]], "plastic"),
    "glass_green": ([[0.03, 0.14, 0.05]], "plastic"),
    "bottle_cap": ([[0.60, 0.58, 0.50], [0.30, 0.05, 0.05]], "metal_painted"),
    "beer": ([[0.55, 0.32, 0.05], [0.14, 0.06, 0.02]], "plastic"),
    "foam": ([[0.82, 0.78, 0.66]], "plastic"),
    "coaster": ([[0.78, 0.74, 0.62], [0.30, 0.06, 0.05]], "paper"),
    "ashtray": ([[0.12, 0.12, 0.13], [0.60, 0.42, 0.12]], "plastic"),
    "ash": ([[0.42, 0.41, 0.40]], "paper"),
    "butt": ([[0.78, 0.60, 0.30]], "paper"),
    "steel": ([[0.55, 0.56, 0.58], [0.15, 0.15, 0.16]], "metal_bare"),
    "napkin": ([[0.85, 0.84, 0.80], [0.60, 0.30, 0.20]], "paper"),
    "ketchup": ([[0.55, 0.05, 0.03]], "plastic"),
    # [0.45, 0.30, 0.02] second first: 1.30-1.38 against the mid-brown tops
    "mustard": ([[0.80, 0.60, 0.03], [0.25, 0.16, 0.01]], "plastic"),
    "cap_white": ([[0.82, 0.80, 0.75], [0.12, 0.12, 0.12]], "plastic"),
    "shaker": ([[0.55, 0.57, 0.56], [0.20, 0.21, 0.21]], "plastic"),
    "cup": ([[0.80, 0.18, 0.14], [0.80, 0.76, 0.66]], "paper"),
    "lid": ([[0.82, 0.80, 0.76], [0.12, 0.12, 0.12]], "plastic"),
    "straw": ([[0.80, 0.14, 0.12]], "plastic"),
    "tray": ([[0.45, 0.10, 0.08], [0.10, 0.20, 0.30], [0.60, 0.45, 0.20]], "plastic"),
    # a light and a mid green alone failed three mid-grey tops (1.32-1.39)
    "cash": ([[0.30, 0.40, 0.25], [0.62, 0.70, 0.55], [0.10, 0.15, 0.08]], "paper"),
    "band": ([[0.75, 0.62, 0.30], [0.10, 0.25, 0.45]], "paper"),
    "bag": ([[0.52, 0.40, 0.24], [0.06, 0.08, 0.20], [0.30, 0.30, 0.30]], "canvas"),
    # THE CARD TABLE. A playmat is rubber-backed cloth, near black with a
    # printed border; the card stacks are the long edge of a deck, which is
    # white board whatever the game; a deck box is moulded plastic in a
    # strong colour and a die is a light chip. Two candidates each, as the
    # module's contrast rule wants, and the mat's pale alternative is for a
    # black cloth table -- the form this species ships by default.
    "playmat": ([[0.035, 0.038, 0.045], [0.34, 0.30, 0.26]], "cloth"),
    "mat_edge": ([[0.42, 0.10, 0.10], [0.10, 0.28, 0.45], [0.75, 0.62, 0.15]], "cloth"),
    "card_edge": ([[0.80, 0.78, 0.72], [0.20, 0.19, 0.18]], "paper"),
    "card_back": ([[0.24, 0.12, 0.06], [0.06, 0.10, 0.28]], "paper"),
    "deck_box": ([[0.45, 0.06, 0.08], [0.06, 0.20, 0.42], [0.72, 0.66, 0.12]], "plastic"),
    "die": ([[0.82, 0.80, 0.74], [0.12, 0.12, 0.14]], "plastic"),
    "ledger_cloth": ([[0.08, 0.20, 0.12], [0.34, 0.07, 0.06], [0.05, 0.05, 0.05]], "paper"),
    "pages": ([[0.80, 0.76, 0.62], [0.30, 0.26, 0.20]], "paper"),
    "masonite": ([[0.36, 0.22, 0.10], [0.62, 0.48, 0.30]], "wood"),
    "kraft": ([list(CF.MATERIALS["kraft"][0]), [0.60, 0.46, 0.26]], "paper"),
    "banker": ([list(CF.MATERIALS["banker"][0]), [0.30, 0.30, 0.28]], "paper"),
    "tape": ([list(CF.MATERIALS["tape"][0])], "plastic"),
    "label": ([list(CF.MATERIALS["label"][0])], "paper"),
    "hole": ([list(CF.MATERIALS["hole"][0])], "paper"),
    # THE CLUB BAR TOP (0.92.0). Spirit bottles are darker and clearer
    # than the beer bottles above, and the tumblers are glass rather than
    # the pint's beer.
    "liquor_amber": ([[0.19, 0.08, 0.02], [0.66, 0.50, 0.16]], "plastic"),
    "liquor_clear": ([[0.72, 0.76, 0.74], [0.10, 0.11, 0.12]], "plastic"),
    "liquor_green": ([[0.04, 0.16, 0.06], [0.58, 0.72, 0.60]], "plastic"),
    "tumbler": ([[0.70, 0.74, 0.72], [0.12, 0.13, 0.14]], "plastic"),
    "spout": ([[0.62, 0.63, 0.65]], "metal_bare"),
    "drink": ([[0.72, 0.36, 0.06], [0.24, 0.06, 0.10]], "plastic"),
}
#: A LABEL PER BRAND, generated from `core.liquor_brands` so the bottle on
#: a counter carries the same ground colour as the one on the back bar's
#: shelf. The words are not painted here -- `prim_mesh.build_stock` has no
#: textured path, and a 60 mm label read from three metres across a bar is
#: a colour. The back bar's own labels are painted (`back_bar_art`).
for _b in LB.BRANDS:
    FINISHES["lbl_" + _b["id"]] = (
        [[round(srgb_to_linear(c), 4) for c in _b["ground"]],
         [round(srgb_to_linear(c), 4) for c in _b["ink"]]], "paper")
del _b

#: Finishes that sit on their own item rather than on the host's top -- a
#: screen in a monitor, foam on a pint, tape on a carton -- and are judged
#: against that item, not the host. Every other finish is an item's body and
#: must contrast with the top it stands on.
DETAIL_FINISHES = ("key_plastic", "screen", "led", "pencil", "foam", "ash",
                   "butt", "straw", "tape", "label", "hole", "bottle_cap",
                   "cap_white", "lid", "band", "pages", "napkin",
                   "spout", "drink") + tuple("lbl_" + b["id"] for b in LB.BRANDS)

#: square metres of top per cluster, and the most clusters on one call
AREA_PER_CLUSTER = {"office": 0.33, "bar": 0.22, "kitchen": 0.25,
                    "vault": 0.22, "storage": 0.45, "bar_dense": 0.22,
                    # a playmat is 0.6 x 0.35, so one player's worth of the
                    # table is about a fifth of a square metre
                    "cards": 0.30}
MAX_CLUSTERS = 5

# --- the club bar top (bar_dense) ------------------------------------------
#: Along a lane, centre to centre. The back bar's own row is 0.095 for a
#: 0.075 m bottle; a counter is read from further away and carries the same
#: bottle, so it keeps the same pitch.
LIQUOR_PITCH = 0.095
SPOUT_PITCH = 0.085
GLASS_PITCH = 0.150
#: A lane's half depth (the widest item on it) and the gap between lanes.
LANE_GAP = 0.02
#: The lanes from the SERVICE edge (+Y) inward: the speed rail against the
#: service run, the liquor row behind the customers' reach, and the glass
#: lane nearest the customer. A top too shallow for all three keeps the
#: ones that fit, in this order.
LANES = ("rail", "liquor", "glass")
#: ITEMS ON ONE REGION, and therefore the pitch once a run is long enough
#: to blow it. Measured before the cap: a 4.0 m counter bay drew 96 items
#: and 8,176 triangles, six times what the flavour above puts on the same
#: top. Every pitch is multiplied by whatever it takes to hold this count,
#: so a bar top's cost stops growing with its length -- measured after,
#: 72 items and 5,132 triangles at 4.0 m, 78 and 6,124 at 8.0 m.
DENSE_MAX_ITEMS = 80


def luminance(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def resolve_finish(finish, host_rgb):
    """``(index, rgb)``: the object's own colour when it contrasts with the
    host, else the candidate that contrasts most."""
    cands, _kind = FINISHES[finish]
    if host_rgb is None or contrast(cands[0], host_rgb) >= 1.4:
        return 0, cands[0]
    best = max(range(len(cands)), key=lambda i: contrast(cands[i], host_rgb))
    return best, cands[best]


# --- items: each builds at its own origin, base z = 0, front toward -Y ------


def _turn(rng):
    return math.radians(rng.uniform(MIN_TURN_DEG, 3.0)) * rng.choice((-1.0, 1.0))


def _monitor(rng):
    out = [P.box("Stock_Monitor", "beige_plastic", (-0.11, -0.11, 0.0), (0.11, 0.11, 0.025)),
           P.box("Stock_Monitor", "beige_plastic", (-0.06, -0.06, 0.02), (0.06, 0.06, 0.05)),
           P.box("Stock_Monitor", "beige_plastic", (-0.175, -0.19, 0.045), (0.175, 0.0, 0.37)),
           P.box("Stock_Monitor", "beige_plastic", (-0.13, -0.01, 0.08), (0.13, 0.19, 0.32)),
           P.box("Stock_Screen", "screen", (-0.135, -0.19 - DETAIL, 0.10),
                 (0.135, -0.19 + DETAIL, 0.31)),
           P.box("Stock_Screen", "led", (0.145, -0.19 - DETAIL, 0.06),
                 (0.16, -0.19 + DETAIL, 0.075))]
    return out


def _keyboard(rng):
    return [P.box("Stock_Keyboard", "beige_plastic", (-0.23, -0.085, 0.0), (0.23, 0.085, 0.022)),
            P.box("Stock_Keyboard", "key_plastic", (-0.21, -0.07, 0.012),
                  (0.21, 0.06, 0.022 + DETAIL))]


def _pad(rng):
    t = rng.uniform(0.011, 0.028)   # its top sheet's bottom, t - SINK, >= 7 mm
    out = [P.box("Stock_Paper", "paper", (-0.108, -0.14, 0.0), (0.108, 0.14, t))]
    if rng.random() < 0.6:
        top = P.box("Stock_Paper", "paper", (-0.1, -0.13, t - SINK), (0.1, 0.13, t - SINK + 0.007))
        out.append(P.rotate_z(top, _turn(rng) * 2.0))
    return out


def _folders(rng):
    """Two to four manila folders stacked, each turned off the one below,
    forms on the top one."""
    out = []
    z = 0.0
    yaw = 0.0
    n = rng.randint(2, 4)
    for k in range(n):
        t = rng.uniform(0.01, 0.018)
        f = P.box("Stock_Folder", "manila", (-0.15, -0.117, z - (SINK if k else 0.0)),
                  (0.15, 0.117, z - (SINK if k else 0.0) + t))
        if k:
            yaw += _turn(rng)
        out.append(P.rotate_z(f, yaw) if yaw else f)
        z = z - (SINK if k else 0.0) + t
    sheet = P.box("Stock_Paper", "paper", (-0.105, -0.135, z - SINK), (0.105, 0.135, z - SINK + 0.007))
    out.append(P.rotate_z(sheet, yaw + _turn(rng) * 2.0))
    return out


def _mug(rng):
    return [P.cyl("Stock_Mug", "mug", (0.0, 0.0), 0.041, 0.0, 0.095, segments=8),
            P.box("Stock_Mug", "mug", (0.034, -0.006, 0.02), (0.062, 0.006, 0.075))]


def _phone(rng):
    return [P.box("Stock_Phone", "beige_plastic", (-0.095, -0.105, 0.0), (0.095, 0.105, 0.045)),
            P.box("Stock_Phone", "beige_plastic", (-0.09, 0.02, 0.04), (0.09, 0.105 - 0.004, 0.075)),
            P.box("Stock_Handset", "beige_plastic", (-0.105, 0.035, 0.07), (0.105, 0.09, 0.10)),
            P.box("Stock_Keypad", "key_plastic", (-0.05, -0.09, 0.04), (0.05, -0.01, 0.045 + DETAIL))]


def _pencil_cup(rng):
    out = [P.cyl("Stock_PencilCup", "mug", (0.0, 0.0), 0.034, 0.0, 0.10, segments=8)]
    for k in range(rng.randint(2, 4)):
        a = 2 * math.pi * k / 4 + rng.uniform(-0.3, 0.3)
        px, py = 0.015 * math.cos(a), 0.015 * math.sin(a)
        pen = P.box("Stock_Pencil", "pencil", (px - 0.0035, py - 0.0035, 0.02),
                    (px + 0.0035, py + 0.0035, 0.18 + 0.01 * k))
        out.append(P.rotate_y(P.rotate_x(pen, rng.uniform(-0.2, 0.2), (py, 0.02)),
                              rng.uniform(-0.2, 0.2), (px, 0.02)))
    return out


def _bottle(rng):
    glass = rng.choice(("glass_brown", "glass_brown", "glass_green"))
    return [P.cyl("Stock_Bottle", glass, (0.0, 0.0), 0.031, 0.0, 0.15, segments=8),
            P.cyl("Stock_Bottle", glass, (0.0, 0.0), 0.031, 0.147, 0.20, segments=8, r_top=0.013),
            P.cyl("Stock_Bottle", glass, (0.0, 0.0), 0.013, 0.197, 0.25, segments=8),
            P.cyl("Stock_BottleCap", "bottle_cap", (0.0, 0.0), 0.017, 0.245, 0.258, segments=8)]


def _pint(rng):
    # a 10 mm coaster: at 6 mm the glass's foot, SINK into it, lay in the
    # host's top
    return [P.cyl("Stock_Coaster", "coaster", (0.0, 0.0), 0.047, 0.0, 0.010, segments=8,
                  phase=math.pi / 8),
            P.cyl("Stock_Pint", "beer", (0.0, 0.0), 0.030, 0.010 - SINK, 0.152, segments=8,
                  r_top=0.041),
            P.cyl("Stock_Pint", "foam", (0.0, 0.0), 0.0385, 0.141, 0.165, segments=8)]


def _ashtray(rng):
    out = [P.cyl("Stock_Ashtray", "ashtray", (0.0, 0.0), 0.055, 0.0, 0.022, segments=8),
           P.cyl("Stock_Ashtray", "ash", (0.0, 0.0), 0.038, 0.012, 0.025, segments=8,
                 phase=math.pi / 8)]
    a0 = rng.uniform(0, 2 * math.pi)
    for k in range(rng.randint(1, 3)):
        # a third of a turn apart, so no two butts overlap
        a = a0 + k * 2 * math.pi / 3 + rng.uniform(-0.35, 0.35)
        butt = P.box("Stock_Butt", "butt", (0.012, -0.004, 0.018), (0.046, 0.004, 0.03))
        out.append(P.rotate_z(butt, a))
    return out


def _napkins(rng):
    return [P.box("Stock_Napkins", "steel", (-0.065, -0.04, 0.0), (0.065, 0.04, 0.012)),
            P.box("Stock_Napkins", "steel", (-0.06, -0.036, 0.009), (0.06, -0.03, 0.11)),
            P.box("Stock_Napkins", "steel", (-0.06, 0.03, 0.009), (0.06, 0.036, 0.11)),
            P.box("Stock_Napkin", "napkin", (-0.054, -0.024, 0.009), (0.054, 0.024, 0.10))]


def _squeeze(rng, colour):
    return [P.cyl("Stock_Condiment", colour, (0.0, 0.0), 0.028, 0.0, 0.15, segments=8),
            P.cyl("Stock_Condiment", "cap_white", (0.0, 0.0), 0.024, 0.147, 0.19, segments=8,
                  r_top=0.007)]


def _shaker(rng):
    return [P.cyl("Stock_Shaker", "shaker", (0.0, 0.0), 0.017, 0.0, 0.065, segments=8),
            P.cyl("Stock_Shaker", "steel", (0.0, 0.0), 0.021, 0.062, 0.085, segments=8,
                  r_top=0.014)]


def _cup(rng, z0=0.0):
    return [P.cyl("Stock_Cup", "cup", (0.0, 0.0), 0.033, z0, z0 + 0.14, segments=8, r_top=0.045),
            P.cyl("Stock_Cup", "lid", (0.0, 0.0), 0.049, z0 + 0.137, z0 + 0.147, segments=8),
            P.cyl("Stock_Straw", "straw", (0.012, 0.0), 0.0035, z0 + 0.13, z0 + 0.23, segments=4)]


def _tray(rng):
    # the end rims stop 4 mm short of the long rims: reaching into them, their
    # bottoms and the long rims' shared a plane wherever the two crossed
    out = [P.box("Stock_Tray", "tray", (-0.170, -0.134, 0.0), (0.170, 0.134, 0.012)),
           P.box("Stock_Tray", "tray", (-0.178, -0.138, 0.007), (0.178, -0.130, 0.03)),
           P.box("Stock_Tray", "tray", (-0.178, 0.130, 0.007), (0.178, 0.138, 0.03)),
           P.box("Stock_Tray", "tray", (-0.175, -0.126, 0.007), (-0.167, 0.126, 0.027)),
           P.box("Stock_Tray", "tray", (0.167, -0.126, 0.007), (0.175, 0.126, 0.027))]
    for k in range(rng.randint(1, 2)):
        cx = (-0.07 if k == 0 else 0.075) + rng.uniform(-0.01, 0.01)
        cy = rng.uniform(-0.05, 0.05)
        cup = _cup(rng, 0.012 - SINK)
        out += [P.translate(P.rotate_z(p, rng.uniform(0, 2 * math.pi)), (cx, cy, 0.0))
                for p in cup]
    return out


def _cash(rng):
    """One to three columns of strapped bundles, side by side along y."""
    out = []
    cols = rng.randint(1, 3)
    for c in range(cols):
        cy = (c - (cols - 1) / 2.0) * 0.09
        z = 0.0
        base_yaw = rng.uniform(-0.02, 0.02)
        yaw = base_yaw
        turn = abs(_turn(rng))
        for k in range(rng.randint(1, 5)):
            t = rng.uniform(0.014, 0.024)
            z0 = z - (SINK if k else 0.0)
            z1 = z0 + t
            bx = rng.uniform(-0.03, 0.03)
            bundle = [P.box("Stock_Cash", "cash", (-0.078, cy - 0.033, z0), (0.078, cy + 0.033, z1)),
                      P.box("Stock_CashBand", "band", (bx - 0.016, cy - 0.033 - DETAIL, z0 + 0.009),
                            (bx + 0.016, cy + 0.033 + DETAIL, z1 + DETAIL))]
            # alternate either side of the column's line, so neighbours
            # differ by 2 x turn and a tall column does not walk into the next
            yaw = base_yaw + (turn if k % 2 else -turn) * (1 if k else 0)
            out += [P.rotate_z(p, yaw, (0.0, cy)) for p in bundle]
            z = z1
    return out


def _bag(rng):
    return [P.pillow("Stock_Bag", "bag", (-0.14, -0.09, 0.0), (0.14, 0.09, 0.04),
                     rng.uniform(0.012, 0.024)),
            P.box("Stock_BagTab", "steel", (0.09, -0.095, 0.012), (0.12, -0.085, 0.036))]


LEDGER_T = 0.04
LEDGER_BOARD = 0.010


def _ledger(rng, z0=0.0):
    """A cloth-bound ledger: two boards, the page block between them 3 mm
    into each, and a spine proud of the boards' back edges.

    Every horizontal face keeps 3 mm or more from every other, for a ledger
    on the top AND for one stacked on another (base = the one below's top
    less SINK). REFUTED FIRST: 4 mm boards and a spine standing proud above
    and below them -- a board's top then lay 1 mm over the host's top, and
    a stacked ledger's bottom board 1 mm over the lower one's top board."""
    t, b = LEDGER_T, LEDGER_BOARD
    return [P.box("Stock_Ledger", "ledger_cloth", (-0.147, -0.115, z0), (0.15, 0.115, z0 + b)),
            P.box("Stock_Ledger", "ledger_cloth", (-0.147, -0.115, z0 + t - b), (0.15, 0.115, z0 + t)),
            P.box("Stock_Ledger", "ledger_cloth", (-0.153, -0.118, z0 + 0.006),
                  (-0.144, 0.118, z0 + t - 0.006)),
            P.box("Stock_LedgerPages", "pages", (-0.141, -0.111, z0 + b - 0.003),
                  (0.146, 0.111, z0 + t - b + 0.003))]


def _ledgers(rng):
    out = []
    yaw = 0.0
    z = 0.0
    for k in range(rng.randint(1, 3)):
        base = z - (SINK if k else 0.0)
        book = _ledger(rng, base)
        if k:
            yaw += _turn(rng) * 2.0
        out += [P.rotate_z(p, yaw) for p in book] if yaw else book
        z = base + LEDGER_T
    return out


def _carton(rng):
    sx, sy = rng.uniform(0.28, 0.42), rng.uniform(0.22, 0.32)
    out = []
    CF._carton(out, 0.0, 0.0, sx, sy, 0.0, rng.uniform(0.16, 0.28), 0.0,
               (rng.uniform(-1, 1), 0.5) if rng.random() < 0.5 else None)
    return [P.recolour(p, part="Stock_" + p["part"]) for p in out]


def _banker_box(rng):
    out = []
    CF._banker(out, 0.0, 0.0, 0.40, 0.32, 0.0, 0.27, 0.0)
    return [P.recolour(p, part="Stock_" + p["part"]) for p in out]


def _clipboard(rng):
    # REFUTED FIRST at a 7 mm board: the forms' bottom then sat 1 mm over
    # the host's top and the clip's 1 mm under the forms' -- every part's
    # bottom is 0 or at least SINK + 4 mm, and 2.5 mm from any other
    return [P.box("Stock_Clipboard", "masonite", (-0.115, -0.16, 0.0), (0.115, 0.16, 0.012)),
            P.box("Stock_Paper", "paper", (-0.1075, -0.1395, 0.007), (0.1075, 0.1395, 0.015)),
            P.box("Stock_Clip", "steel", (-0.04, 0.13, 0.0095), (0.04, 0.155, 0.026))]


# --- the club bar top: bottles, spouts, towers, cocktails ---------------------
#
# Every one of these is drawn so that no two of its own faces share a plane
# (`prims.coincident_pairs`, the rule the whole module keeps): a stacked
# section overlaps the one below by 4 mm so their caps differ, and a label
# ring stands 4 mm PROUD of the glass rather than flush with it -- flush,
# its side facets lay in the bottle's, 0 mm apart, over the whole ring.

LIQUOR_GLASS = {"amber": "liquor_amber", "clear": "liquor_clear",
                "green": "liquor_green"}
_JOIN = 0.004
LABEL_PROUD = 0.004


def _liquor_bottle(rng, brand, r=0.034, hgt=0.30, spout=False):
    """A spirit bottle, its label ring in the brand's own ground colour and
    (on the speed rail) a steel pour spout in its neck."""
    glass = LIQUOR_GLASS[brand["glass"]]
    body = hgt * 0.64
    neck_r = r * 0.34
    ph = math.pi / 6.0
    # FOUR PRIMITIVES, not five: the shoulder runs straight into the neck
    # in one frustum. The separate neck is 20 triangles a bottle and a bar
    # top carries eighty of them -- it reads at the back bar's arm's
    # length and not across a counter.
    out = [P.cyl("Stock_Liquor", glass, (0.0, 0.0), r, 0.0, body, segments=6,
                 phase=ph),
           P.cyl("Stock_Liquor", glass, (0.0, 0.0), r, body - _JOIN, hgt,
                 segments=6, phase=ph, r_top=neck_r),
           P.cyl("Stock_Label", "lbl_" + brand["id"], (0.0, 0.0),
                 r + LABEL_PROUD, body * 0.28, body * 0.68, segments=6, phase=ph)]
    if spout:
        out.append(P.rod("Stock_Spout", "spout", (0.0, 0.0, hgt - 0.006),
                         (0.0, -0.035, hgt + 0.045), neck_r * 0.55,
                         neck_r * 0.30, segments=5))
    else:
        out.append(P.cyl("Stock_Liquor", "bottle_cap", (0.0, 0.0), neck_r * 1.15,
                         hgt - 0.012, hgt + 0.004, segments=5, phase=ph))
    return out


def _magnum(rng):
    return _liquor_bottle(rng, LB.BY_ID[LB.IDS[rng.randrange(len(LB.IDS))]],
                          r=0.049, hgt=0.42)


def _rocks_tower(rng, n=None):
    """A tower of rocks glasses: one tapered body with a lip ring where each
    glass sits in the one below (the back bar's own tower, same reason --
    nested cylinders of one taper are coplanar with each other)."""
    n = n or rng.randint(3, 5)
    r, t = 0.039, 0.088
    step = t * 0.66
    out = [P.cyl("Stock_Tumbler", "tumbler", (0.0, 0.0), r, 0.0,
                 step * (n - 1) + t, segments=6, r_top=r * 1.12)]
    for k in range(1, n):
        out.append(P.cyl("Stock_Tumbler", "tumbler", (0.0, 0.0), r * 1.10,
                         step * k, step * k + 0.005, segments=6))
    return out


def _cocktail(rng):
    """A cocktail glass with a drink in it."""
    hgt = 0.155
    r = hgt * 0.30
    return [P.cyl("Stock_Cocktail", "tumbler", (0.0, 0.0), r * 0.62, 0.0,
                  hgt * 0.42, segments=5, r_top=r * 0.10),
            P.cyl("Stock_Cocktail", "tumbler", (0.0, 0.0), r * 0.12,
                  hgt * 0.42 - _JOIN, hgt, segments=6, r_top=r),
            # 5 mm of drink, not 2: at 2 mm its own two caps are 2.0 mm
            # apart, which is inside the coincidence probe's window
            P.cyl("Stock_Drink", "drink", (0.0, 0.0), r * 0.72, hgt * 0.80,
                  hgt * 0.80 + 0.005, segments=6)]


#: lane -> (builder, pitch, half depth). The half depth is the widest the
#: lane's items get, and it is what decides whether a top is deep enough.
_LANE = {
    "rail": (lambda rng, brand: _liquor_bottle(rng, brand, r=0.030, hgt=0.265,
                                               spout=True), SPOUT_PITCH, 0.042),
    "liquor": (lambda rng, brand: _liquor_bottle(rng, brand), LIQUOR_PITCH, 0.040),
    "glass": (None, GLASS_PITCH, 0.055),
}


def _blocked(poly, placed, keep_out):
    if any(not P.poly_separated(poly, q, MIN_GAP) for q in placed):
        return True
    return any(not P.poly_separated(poly, P.rect_poly(kx, ky, 2 * kr, 2 * kr, 0.0), 0.0)
               for kx, ky, kr in keep_out)


def plan_bar_dense(rng, x0, x1, y0, y1, z0, host_rgb=None, clear=0.6,
                   keep_out=()):
    """The club bar's top: LANES along the run, not clusters.

    The service side is +Y (a counter's top overhangs the customer side,
    `recipes/counter.py`), so the speed rail takes the +Y lane. Returns the
    same shape `plan_surface` does.

    A REAL SPEED RAIL HANGS UNDER THE COUNTER'S SERVICE LIP. This planner
    owns the TOP and nothing else, so the rail stands on the service edge
    of it instead -- the bottles, the spouts and the reach are the photo's;
    the shelf they sit on is not. Say so rather than calling it a rail.
    """
    out = {"prims": [], "materials": {}, "items": []}
    rx0, rx1, ry0, ry1 = x0 + EDGE, x1 - EDGE, y0 + EDGE, y1 - EDGE
    if rx1 - rx0 < 0.12 or ry1 - ry0 < 0.12 or clear - HEADROOM < 0.03:
        return out
    order = [LB.BY_ID[b] for b in LB.order("%08x" % (rng.getrandbits(32)))]
    placed = []
    cursor = ry1
    pick = 0
    # the pitch multiplier that holds `DENSE_MAX_ITEMS` over the lanes this
    # top is deep enough for (see the constant)
    run = rx1 - rx0
    fit, y = [], ry1
    for lane in LANES:
        half = _LANE[lane][2]
        if y - 2 * half >= ry0:
            fit.append(lane)
            y -= 2 * half + LANE_GAP
    dense = sum(run / _LANE[ln][1] for ln in fit) if fit else 0.0
    k = max(1.0, dense / DENSE_MAX_ITEMS) if DENSE_MAX_ITEMS else 1.0
    for lane in LANES:
        builder, pitch, half = _LANE[lane]
        pitch *= k
        if cursor - 2 * half < ry0:
            continue
        ly = cursor - half
        cursor -= 2 * half + LANE_GAP
        n = int((rx1 - rx0 - 2 * half) / pitch) + 1
        if n < 1:
            continue
        start = (rx0 + rx1) / 2.0 - (n - 1) * pitch / 2.0
        for i in range(n):
            lx = start + i * pitch
            ly_i = ly + rng.uniform(-0.006, 0.006)
            if lane == "glass":
                prims = (_rocks_tower(rng) if (i + pick) % 2 == 0
                         else _cocktail(rng))
            else:
                brand = order[pick % len(order)]
                prims = builder(rng, brand)
            pick += 1
            cx, cy, sx, sy, top = _local_rect(prims)
            if top > clear - HEADROOM:
                continue
            yaw = rng.uniform(-0.25, 0.25) if lane != "rail" else 0.0
            pcx = lx + math.cos(yaw) * cx - math.sin(yaw) * cy
            pcy = ly_i + math.sin(yaw) * cx + math.cos(yaw) * cy
            poly = P.rect_poly(pcx, pcy, sx + 2 * DETAIL, sy + 2 * DETAIL, yaw)
            if not P.poly_inside_rect(poly, rx0, rx1, ry0, ry1):
                continue
            if _blocked(poly, placed, keep_out):
                continue
            placed.append(poly)
            out["items"].append({"group": lane, "poly": poly,
                                 "top": z0 - SINK + top})
            for p in prims:
                q = P.translate(P.rotate_z(p, yaw), (lx, ly_i, z0 - SINK))
                idx, rgb = resolve_finish(q["mat"], host_rgb)
                key = f"{q['mat']}_{idx}"
                out["materials"][key] = (rgb, FINISHES[q["mat"]][1])
                out["prims"].append(P.recolour(q, mat=key))
    # THE MAGNUM IN FRONT, where the photo has it: one bottle standing
    # forward of the rows, on the customer half, where there is room.
    tall = _magnum(rng)
    _cx, _cy, sx, sy, top = _local_rect(tall)
    if out["items"] and top <= clear - HEADROOM:
        for _try in range(12):
            mx = rng.uniform(rx0 + sx, rx1 - sx)
            my = rng.uniform(ry0 + sy / 2.0, min(cursor, ry1) - sy / 2.0) \
                if cursor - sy / 2.0 > ry0 + sy / 2.0 else None
            if my is None:
                break
            poly = P.rect_poly(mx, my, sx + 2 * DETAIL, sy + 2 * DETAIL, 0.0)
            if not P.poly_inside_rect(poly, rx0, rx1, ry0, ry1):
                continue
            if _blocked(poly, placed, keep_out):
                continue
            placed.append(poly)
            out["items"].append({"group": "magnum", "poly": poly,
                                 "top": z0 - SINK + top})
            for p in tall:
                q = P.translate(p, (mx, my, z0 - SINK))
                idx, rgb = resolve_finish(q["mat"], host_rgb)
                key = f"{q['mat']}_{idx}"
                out["materials"][key] = (rgb, FINISHES[q["mat"]][1])
                out["prims"].append(P.recolour(q, mat=key))
            break
    return out


# --- groups: an anchor and the items about it ---------------------------------
#
# A group is ``[(builder, dx, dy, yaw), ...]`` in the cluster's frame, the
# cluster's front toward -Y. ``yaw`` is the item's own turn in that frame
# before the off-kilter jitter.


def _g_workstation(rng):
    g = [(_monitor, 0.0, 0.07, 0.0), (_keyboard, rng.uniform(-0.03, 0.03), -0.25, 0.0)]
    if rng.random() < 0.5:
        g.append((_mug, rng.choice((-1, 1)) * 0.3, -0.2, rng.uniform(0, 6.28)))
    return g


def _g_paperwork(rng):
    g = [(_folders, 0.0, 0.0, rng.uniform(-0.3, 0.3))]
    if rng.random() < 0.6:
        g.append((_pad, rng.choice((-1, 1)) * 0.29, rng.uniform(-0.05, 0.05), rng.uniform(-0.4, 0.4)))
    if rng.random() < 0.4:
        g.append((_pencil_cup, rng.choice((-1, 1)) * 0.22, 0.17, 0.0))
    return g


def _g_phone(rng):
    g = [(_phone, 0.0, 0.0, rng.uniform(-0.4, 0.4))]
    if rng.random() < 0.6:
        g.append((_mug, 0.2, rng.uniform(-0.06, 0.06), rng.uniform(0, 6.28)))
    return g


def _g_bottles(rng):
    n = rng.randint(2, 5)
    return [(_bottle, rng.uniform(-0.09, 0.09), rng.uniform(-0.09, 0.09), 0.0)
            for _ in range(n)]


def _g_pints(rng):
    return [(_pint, k * 0.11, rng.uniform(-0.03, 0.03), rng.uniform(0, 6.28))
            for k in range(rng.randint(1, 3))]


def _g_ashtray(rng):
    g = [(_ashtray, 0.0, 0.0, rng.uniform(0, 6.28))]
    if rng.random() < 0.5:
        g.append((_bottle, 0.12, 0.05, 0.0))
    return g


def _g_napkins(rng):
    return [(_napkins, 0.0, 0.0, rng.uniform(-0.5, 0.5))]


def _g_condiments(rng):
    g = [(lambda r: _squeeze(r, "ketchup"), 0.0, 0.0, 0.0),
         (lambda r: _squeeze(r, "mustard"), 0.075, 0.02, 0.0)]
    if rng.random() < 0.7:
        g += [(_shaker, -0.07, 0.03, 0.0), (_shaker, -0.07, -0.035, 0.0)]
    return g


def _g_tray(rng):
    return [(_tray, 0.0, 0.0, rng.uniform(-0.3, 0.3))]


def _g_cups(rng):
    return [(_cup, k * 0.1, rng.uniform(-0.02, 0.02), rng.uniform(0, 6.28))
            for k in range(rng.randint(1, 2))]


def _g_cash(rng):
    return [(_cash, 0.0, 0.0, rng.uniform(-0.3, 0.3))]


def _g_bags(rng):
    return [(_bag, k * 0.3, rng.uniform(-0.03, 0.03), rng.uniform(-0.4, 0.4))
            for k in range(rng.randint(1, 2))]


def _g_ledgers(rng):
    g = [(_ledgers, 0.0, 0.0, rng.uniform(-0.3, 0.3))]
    if rng.random() < 0.5:
        g.append((_cash, 0.27, 0.0, rng.uniform(-0.3, 0.3)))
    return g


def _g_carton(rng):
    return [(_carton, 0.0, 0.0, rng.uniform(-0.15, 0.15))]


def _g_banker(rng):
    return [(_banker_box, 0.0, 0.0, rng.uniform(-0.1, 0.1))]


def _g_clipboard(rng):
    g = [(_clipboard, 0.0, 0.0, rng.uniform(-0.5, 0.5))]
    if rng.random() < 0.5:
        g.append((_pad, 0.27, 0.0, rng.uniform(-0.4, 0.4)))
    return g


# --- the card table (cards) --------------------------------------------------
#
# Every one of these keeps the module's own rule: nothing shares a plane with
# anything, so a printed border is a SEPARATE slab 2.5 mm proud of the mat
# rather than a face lying in it, and a card stack sits SINK into whatever it
# stands on. A playmat is 0.60 x 0.35 (the size every one of them is).

#: A HALF-SIZE PLAYMAT, and it had to be. A full one is 0.61 x 0.356, two of
#: them face to face need 0.71 m, and a folding table is 0.76 deep -- after
#: this module's `EDGE` (20 mm a side) and the host's own region inset the
#: half a player gets is 0.318 m, so a full mat NEVER fit and `_place_group`
#: gave way to card piles every time: measured on a 1.8 x 0.76 table, 0 mats
#: in the frame. 0.56 x 0.27 is the small mat that is also a real product,
#: and it has to be 0.27 rather than 0.28 because the module turns every item
#: off square by up to `min(MAX_JITTER_DEG, JITTER_K / size)` -- 3.57 degrees
#: for a 0.56 m mat, which is 35 mm of extra depth and was what still missed.
#:
#: A playmat is 2 mm of rubber, and this one is 9. `SINK` is 3 and this
#: module's own rule is that no face of an item lands between the host's
#: top and SINK + 4 mm above it -- at a true thickness the mat's top face
#: sat 1.0 mm over the host top, on every seed and every table. The rule
#: is what keeps stock out of the z-fighting band, so the mat moves.
MAT_W, MAT_D, MAT_T = 0.56, 0.27, 0.009
EDGE_W = 0.022
DECK_W, DECK_D = 0.066, 0.094      # a deck of cards on its back
#: How far the printed face floats over the mat's own top. Above `SINK` + 4
#: mm (this module's own band, which nothing may have a face in) and above
#: the 2.2 mm coincident window with room for the float.
PRINT_PROUD = 0.003


def _playmat(rng):
    """The mat, PRINTED (0.98.0). Was two flat slabs standing for a border.

    THE TEXTURED PATH, WHICH IS FINDING 5 OF THE CARD-SHOP REFERENCE. The
    0.95.0 entry records the gap in this module's own docstring -- "NOT
    TEXTURED, and that is a limit rather than a choice: `prim_mesh`'s
    `build_stock` has no textured path, so a mat is a colour with a border
    and not art" -- and the walker's close-up reference is exactly this
    surface: a neon playmat with a pack held over it. So the mat now carries
    ONE art quad naming a tile in `core.flat_art`, and the printed border
    the two `Stock_MatEdge` slabs used to stand for is IN the print, where
    a real one is. That is 24 triangles back per mat and one tile out.

    The quad is a separate prim `PRINT_PROUD` over the mat's top face rather
    than a face lying in it, which is this module's rule and not a
    preference: `tests/test_surface_stock.py` runs the coincident-face
    measurement over every flavour and every seed.
    """
    from ..core import card_brands as CB
    out = [P.box("Stock_Playmat", "playmat",
                 (-MAT_W / 2, -MAT_D / 2, 0.0), (MAT_W / 2, MAT_D / 2, MAT_T))]
    gid = CB.IDS[rng.randrange(len(CB.IDS))]
    e = EDGE_W * 0.5
    x, y = MAT_W / 2 - e, MAT_D / 2 - e
    z = MAT_T + PRINT_PROUD
    q = P.mesh("Stock_MatPrint", "playmat",
               [(-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)], [(0, 1, 2, 3)])
    # ONE TILE PER GAME, not per mat: two mats of the same game on two
    # tables share one rect in the atlas, which is the whole reason the
    # planners name tiles instead of images (`_card_atlas`).
    q["tile"] = f"playmat_{gid}"
    q["uvs"] = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))]
    q["tile_spec"] = {"kind": "playmat", "game": gid,
                      "w_m": round(2 * x, 4), "h_m": round(2 * y, 4),
                      "key": gid}
    out.append(q)
    return out


def _card_stack(rng):
    """A stack of cards: the white edge of the block with a coloured back
    slab on top, overlapping by 4 mm so no two caps share a plane."""
    hgt = rng.uniform(0.012, 0.040)
    out = [P.box("Stock_CardStack", "card_edge",
                 (-DECK_W / 2, -DECK_D / 2, 0.0), (DECK_W / 2, DECK_D / 2, hgt))]
    out.append(P.box("Stock_CardBack", "card_back",
                     (-DECK_W / 2 + 0.003, -DECK_D / 2 + 0.003, hgt - 0.004),
                     (DECK_W / 2 - 0.003, DECK_D / 2 - 0.003, hgt + 0.0025)))
    return out


def _deck_box(rng):
    w = rng.uniform(0.072, 0.082)
    dd = rng.uniform(0.098, 0.108)
    hgt = rng.uniform(0.075, 0.095)
    return [P.box("Stock_DeckBox", "deck_box",
                  (-w / 2, -dd / 2, 0.0), (w / 2, dd / 2, hgt)),
            P.box("Stock_DeckLid", "deck_box",
                  (-w / 2 + 0.004, -dd / 2 + 0.004, hgt - 0.006),
                  (w / 2 - 0.004, dd / 2 - 0.004, hgt + 0.010))]


def _dice(rng):
    out = []
    for k in range(rng.randint(2, 4)):
        s = rng.uniform(0.013, 0.017)
        x = -0.03 + k * 0.026 + rng.uniform(-0.004, 0.004)
        y = rng.uniform(-0.016, 0.016)
        out.append(P.box(f"Stock_Die{k}", "die",
                         (x - s / 2, y - s / 2, 0.0), (x + s / 2, y + s / 2, s)))
    return out


def _g_playmat(rng):
    """A mat with a deck on one corner of it -- a player's side of a game,
    not a mat here and a deck somewhere."""
    g = [(_playmat, 0.0, 0.0, rng.uniform(-0.03, 0.03))]
    g.append((_card_stack, MAT_W * 0.30, -MAT_D * 0.22, rng.uniform(-0.3, 0.3)))
    if rng.random() < 0.55:
        g.append((_deck_box, -MAT_W * 0.36, MAT_D * 0.20, rng.uniform(-0.4, 0.4)))
    return g


def _g_card_piles(rng):
    g = [(_card_stack, 0.0, 0.0, rng.uniform(-0.5, 0.5)),
         (_card_stack, 0.085, 0.02, rng.uniform(-0.5, 0.5))]
    if rng.random() < 0.5:
        g.append((_card_stack, 0.042, 0.11, rng.uniform(-0.5, 0.5)))
    return g


def _g_deck_kit(rng):
    g = [(_deck_box, 0.0, 0.0, rng.uniform(-0.4, 0.4))]
    if rng.random() < 0.7:
        g.append((_dice, 0.095, -0.02, rng.uniform(-0.6, 0.6)))
    return g


#: flavour -> ((group, weight, most per call), ...)
GROUPS = {
    "office": ((_g_workstation, 3.0, 1), (_g_paperwork, 3.0, 2), (_g_phone, 1.5, 1)),
    "bar": ((_g_bottles, 3.0, 2), (_g_pints, 2.5, 2), (_g_ashtray, 2.0, 2),
            (_g_napkins, 1.0, 1)),
    "kitchen": ((_g_condiments, 3.0, 2), (_g_tray, 2.0, 1), (_g_cups, 2.0, 2),
                (_g_napkins, 1.0, 1)),
    "vault": ((_g_cash, 3.0, 3), (_g_bags, 2.0, 2), (_g_ledgers, 2.0, 1)),
    "storage": ((_g_carton, 3.0, 2), (_g_banker, 1.5, 1), (_g_clipboard, 2.0, 1)),
    "cards": ((_g_playmat, 3.0, 2), (_g_card_piles, 2.0, 2),
              (_g_deck_kit, 1.5, 2)),
}


def _local_rect(prims):
    lo, hi = P.bounds(prims)
    return ((lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0,
            hi[0] - lo[0], hi[1] - lo[1], hi[2])


def _place_group(rng, g, placed, rx0, rx1, ry0, ry1, facing, clear, keep_out):
    """``(polys, poses)`` for group ``g`` placed on the region clear of
    ``placed``, or None after 48 tries."""
    members = g(rng)
    built = []
    for builder, dx, dy, iyaw in members:
        prims = builder(rng)
        cx, cy, sx, sy, top = _local_rect(prims)
        size = max(sx, sy)
        jitter = math.radians(min(MAX_JITTER_DEG, JITTER_K / max(size, 0.05)))
        built.append((prims, cx, cy, sx, sy, top, dx, dy,
                      iyaw + rng.uniform(-jitter, jitter)))
    built = [b for b in built if b[5] <= clear - HEADROOM]
    if not built:
        return None
    base_yaw = facing if facing is not None else rng.choice((0.0, 0.5, 1.0, 1.5)) * math.pi
    cyaw = base_yaw + math.radians(rng.uniform(-4.0, 4.0))
    c, s = math.cos(cyaw), math.sin(cyaw)

    def reach(members):
        """The group's footprint bounds about its anchor, turned."""
        xs, ys = [], []
        for _p, cx, cy, sx, sy, _t, dx, dy, iyaw in members:
            yaw = cyaw + iyaw
            pcx = c * dx - s * dy + math.cos(yaw) * cx - math.sin(yaw) * cy
            pcy = s * dx + c * dy + math.sin(yaw) * cx + math.cos(yaw) * cy
            for x, y in P.rect_poly(pcx, pcy, sx + 2 * DETAIL, sy + 2 * DETAIL, yaw):
                xs.append(x)
                ys.append(y)
        return min(xs), max(xs), min(ys), max(ys)

    for attempt in range(48):
        # every 12 failed tries the group gives up its last member, so a
        # workstation loses its mug before its keyboard
        members_now = built[:max(1, len(built) - attempt // 12)]
        # the anchor is drawn where the whole group can fit: drawn over the
        # whole top, a workstation (monitor, keyboard 0.32 m in front of it)
        # fitted a 0.8 m desk so rarely that the first renders showed
        # monitors with no keyboard
        mnx, mxx, mny, mxy = reach(members_now)
        lo_x, hi_x = rx0 - mnx, rx1 - mxx
        lo_y, hi_y = ry0 - mny, ry1 - mxy
        if lo_x > hi_x or lo_y > hi_y:
            continue
        ax = rng.uniform(lo_x, hi_x)
        ay = rng.uniform(lo_y, hi_y)
        polys, poses = [], []
        ok = True
        for prims, cx, cy, sx, sy, top, dx, dy, iyaw in members_now:
            wx = ax + c * dx - s * dy
            wy = ay + s * dx + c * dy
            yaw = cyaw + iyaw
            # the item's local bounds centre, turned with it
            pcx = wx + math.cos(yaw) * cx - math.sin(yaw) * cy
            pcy = wy + math.sin(yaw) * cx + math.cos(yaw) * cy
            poly = P.rect_poly(pcx, pcy, sx + 2 * DETAIL, sy + 2 * DETAIL, yaw)
            if not P.poly_inside_rect(poly, rx0, rx1, ry0, ry1):
                ok = False
            elif any(not P.poly_separated(poly, q, MIN_GAP) for q in placed + polys):
                ok = False
            elif any(not P.poly_separated(poly, P.rect_poly(kx, ky, 2 * kr, 2 * kr, 0.0), 0.0)
                     for kx, ky, kr in keep_out):
                ok = False
            if not ok:
                break
            polys.append(poly)
            poses.append((prims, wx, wy, yaw, top))
        if ok:
            return polys, poses
    return None


def plan_surface(rng, flavour, x0, x1, y0, y1, z0, host_rgb=None, facing=None,
                 clear=0.6, keep_out=()):
    """Stock for one top: the rectangle ``x0..x1`` by ``y0..y1`` at height
    ``z0``, ``clear`` metres of room above it.

    ``facing`` is the yaw that turns an item's front toward the person at
    this top (0.0: they stand at -Y); None lets each cluster face any of
    the four ways, which is a table. ``keep_out`` is ``[(x, y, radius)]``
    left empty -- a counter's register stations. Returns
    ``{"prims": [...], "materials": {key: (rgb, kind)}, "items": [...],
    "tiles": {key: spec}}``, items being ``{"group", "poly", "top"}`` per
    placed item.

    ``tiles`` (0.98.0) is the ART a flavour asks for -- today only the card
    table's printed playmat. It is EMPTY for every other flavour and every
    host, so a desk with office stock plans exactly what it planned before.
    `prim_mesh.build_stock` is what turns it into one atlas.
    """
    out = {"prims": [], "materials": {}, "items": [], "tiles": {}}
    if flavour == "bar_dense":
        return plan_bar_dense(rng, x0, x1, y0, y1, z0, host_rgb=host_rgb,
                              clear=clear, keep_out=keep_out)
    if flavour not in GROUPS:
        return out
    rx0, rx1, ry0, ry1 = x0 + EDGE, x1 - EDGE, y0 + EDGE, y1 - EDGE
    if rx1 - rx0 < 0.12 or ry1 - ry0 < 0.12 or clear - HEADROOM < 0.03:
        return out
    area = (rx1 - rx0) * (ry1 - ry0)
    n = max(1, min(MAX_CLUSTERS, int(round(area / AREA_PER_CLUSTER[flavour]))))
    used = {}
    placed = []          # footprint polygons already on the top
    for _c in range(n):
        # A GROUP THAT DOES NOT FIT GIVES WAY TO ONE THAT DOES. With one
        # cluster's worth of area, a 0.9 x 0.5 file cabinet top drew the
        # office workstation (a 0.39 m-deep monitor with a keyboard in front
        # of it), failed to place it, and stayed bare -- measured as zero
        # Stock_ objects on the first build.
        failed = set()
        accepted = g = None
        for _pick in range(3):
            choices = [(gg, wt) for gg, wt, most in GROUPS[flavour]
                       if used.get(gg, 0) < most and gg not in failed]
            if not choices:
                break
            pick = rng.uniform(0.0, sum(wt for _g, wt in choices))
            for g, wt in choices:
                pick -= wt
                if pick <= 0.0:
                    break
            accepted = _place_group(rng, g, placed, rx0, rx1, ry0, ry1, facing,
                                    clear, keep_out)
            if accepted is not None:
                break
            failed.add(g)
        if accepted is None:
            continue
        used[g] = used.get(g, 0) + 1
        for poly, (prims, wx, wy, yaw, top) in zip(*accepted):
            placed.append(poly)
            out["items"].append({"group": g.__name__[3:], "poly": poly,
                                 "top": z0 - SINK + top})
            for p in prims:
                q = P.translate(P.rotate_z(p, yaw), (wx, wy, z0 - SINK))
                idx, rgb = resolve_finish(q["mat"], host_rgb)
                key = f"{q['mat']}_{idx}"
                out["materials"][key] = (rgb, FINISHES[q["mat"]][1])
                # AN ART PRIM CARRIES ITS OWN SPEC UP, because the builder
                # that paints it is not the one that placed it: the item
                # knows which game its mat is printed with and `plan_surface`
                # is the only thing that sees all of them. Two mats of one
                # game land on the same key and share one rect.
                if q.get("tile") and q.get("tile_spec"):
                    out["tiles"][q["tile"]] = q["tile_spec"]
                out["prims"].append(P.recolour(q, mat=key))
    return out
