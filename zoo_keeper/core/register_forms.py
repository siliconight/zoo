"""The 1990s cash register, decided in pure Python: layout, price, artwork.

Zoo 1.0.0. `recipes/cash_register.py` only executes what this returns, so
every size, every digit and every pixel of the display is testable without
Blender -- the shape `vending_forms` and `crt_forms` set.

WHAT STOOD THERE BEFORE, measured before anything moved. The card shop's
counter is Zoo's `display_case`, and its register is four boxes drawn by
`display_case_forms._register`: a 0.34 x 0.36 x 0.15 body in the case's own
BODY material (the slot's wood, so brown in a panelled shop), a 0.26 x 0.12
key plate in STOCK (0.55, 0.52, 0.47 paper), a 0.035 square METAL stem (mill
aluminium, so a white post) and a 0.16 x 0.05 x 0.08 head in BODY again.
48 triangles, no artwork, nothing lit. The walker's frame from cold run
9062: "a brown box with a white post and a smaller box on top -- it reads as
a mistake, not a register."

THE REFERENCE, as the walker described the photograph:

  * a squat black moulded-plastic body, wider than deep, with a separate
    raised CUSTOMER display on a short post: a black bezel with bright green
    segment digits on a black screen, reading a price. "Cash registers in
    the 90s had this green font on a black screen";
  * a second, OPERATOR display angled toward the clerk -- a small green LCD
    panel, dark text on a green-grey ground, set in the body's top;
  * a receipt PRINTER slot on the left of the top face with a curl of white
    paper coming out of it;
  * a KEYPAD on the right of the top face: three or four columns of small
    square keys, mostly grey/white with a few coloured ones at the edges;
  * below the body, a deeper DRAWER with a full-width horizontal pull and a
    small round keyhole.

FRAME AND UNITS: metres, Z up, CENTRE pivot, -Y is the CUSTOMER side. The
operator stands at +Y, so the operator's right hand points toward -X: the
keypad is on the -X half of the top and the printer on the +X half, which is
the reference photograph's "right" and "left" read from where it was taken.

THE SLOT IS EXACT on every axis and at every genome corner, with no scaling:
the drawer is the full width and reaches the back plane, the pull bar's face
IS the front plane, the drawer's underside IS the bottom and the pole bezel's
top IS the top. `extents` is that arithmetic and `tests/test_cash_register.py`
measures it on the built module.

NO TWO FACES SHARE A PLANE. Every part that stands on another is buried
`BURY` into it, and `BURY` is three times the 2 mm window
`tools/coplanar_probe.py` and `prims.coincident_pairs` measure at.

THE TRIANGLE BUDGET IS `TRI_BUDGET`, and it was set before the layout was
drawn rather than read off it. For scale, in the same package: `crt_tv`
bracket form 168, `poster` framed 78, `vending_machine` 464. A register is a
counter-top prop and belongs in that company. The keypad is the line item
that decides it: twenty modelled keys are 240 triangles on their own, more
than the whole rest of the register, so the keys are PAINTED into the atlas
on one quad and the well around them is real geometry. That is `card_art`'s
own call one shelf along -- "a figure is a blob and a rules box is a run of
dashes, because at this size that is what a figure and a rules box ARE".
What the modelled version would buy is a key's own shadow at arm's length,
which is nearer than any player stands to a shop counter.

GLOW, AND ONLY ON THE CUSTOMER DISPLAY. The pole screen is glTF-emissive,
named `M_*_Face` for Lux's emissive binder so a power cut kills it with the
building's fixtures. IT IS NOT A LIGHT: Compatibility's
`max_lights_per_object` is 8 and the package this ships into already carries
84, so nothing here spawns an OmniLight and the screen lights nothing but
itself. The OPERATOR panel is a reflective LCD and is PAINTED, not lit --
that is what the reference describes (dark text on a green-grey ground) and
it is the cheaper of the two readings as well.

THE REAL LOOK (1.46.0). The walker, 2026-10-02: "this looks like it is made
with a 90s GPU ... replace the retro look", and then "do the ATM and register
the same way". Three changes, the ones `machine_parts` and `paint` made to
the video-poker cabinet:

  * EVERY FACE IS PAINTED. The solids were boxes in four flat materials and
    the module was SIX draws (case, trim, lock, paper, panel, screen). Every
    face is now a quad naming a tile in the register's one image, so it is
    TWO: the painted object and the lit screen. The lock is painted on the
    drawer's face, with the shadow the pull bar throws;
  * THE SHAPE OF A MADE THING: the drawer, the body, the islands on the top
    and the pole's head have their vertical corners broken, and the glass
    sits BEHIND the head's face in a surround that slopes in to it;
  * SMOOTH TYPE AT THREE TIMES THE DENSITY, sampled with filtering: the
    display is a dot-segment face with its own bloom, the keys are bevelled
    and carry their digits.

What it costs is texture: the atlas decodes at several hundred KiB where
1.0.0's was 65 (`tests/test_cash_register.py` holds the figure).
"""
from __future__ import annotations

import math
import zlib

from . import card_art as CA
from . import machine_parts as MP
from . import paint as PT
from . import prims as P
from . import smooth_type as ST
from .vending_forms import uv_rect

# --- the budget ----------------------------------------------------------------

#: Triangles, whole module, at every genome corner. Set BEFORE the layout was
#: drawn (see the module docstring for the company it is in). The count does
#: not move with the slot -- every part is a fixed set of faces -- so one
#: number holds at all 27 corners and `triangles` proves it. 1.46.0's broken
#: corners and sloped surround took it from 134 to 182, inside the same 200.
TRI_BUDGET = 200

# --- the frame -----------------------------------------------------------------

#: Burial past a contact plane: 3 x the coplanar probe's 2 mm window.
BURY = 0.006
#: Broken vertical corners (1.46.0): the drawer's, the body's, and those of
#: the small parts standing on it.
DRAWER_C = 0.008
BODY_C = 0.010
PART_C = 0.004
#: The pole's glass sits this far behind its head's face, inside a surround
#: this wide sloping in to it.
SCREEN_RECESS = 0.005
WELL_M = 0.004

#: The three bands of the silhouette, as fractions of the slot's height: the
#: drawer, the body, and the pole above it. A register is read by these
#: proportions before anything else, so they are the one place the shape is
#: authored; everything below is derived from the band it lives in.
DRAWER_F = 0.30
BODY_F = 0.30
POLE_F = 1.0 - DRAWER_F - BODY_F

#: The body stands inside the drawer's footprint -- the reference's "below
#: the body, a DEEPER drawer".
BODY_IN_X = 0.020
BODY_IN_FRONT = 0.030
BODY_IN_BACK = 0.030

#: The drawer's face is recessed behind the pull bar, which is what makes the
#: pull read as a full-width slot rather than a stripe. The bar's front IS the
#: slot's front plane.
PULL_T = 0.014
PULL_END = 0.028          # bar stops this far short of each end
PULL_H = 0.020
#: The drawer lock: a small round barrel, the one bright accent on the front.
#: Painted on the drawer's face since 1.46.0 (`paint_drawer`).
LOCK_R = 0.008

#: THE TOP FACE IS THREE LANES, and the first one is why. The pole stem
#: stands on the body's top at the customer edge; the first layout let the
#: keypad island run the full depth under it and `prims.coincident_pairs`
#: read the two sharing their base plane at 5.7 cm2 -- not a near miss, an
#: overlap. `POLE_LANE` is the strip the stem owns, derived from the stem's
#: own section, and nothing else is laid in it:
#:
#:   -Y  [ pole lane ][  keypad (operator's right)  |  printer / panel  ]  +Y
#:
#: The two columns are `COL_GAP` apart and the panel is inset inside its
#: column, so no two parts on this face share a side plane either.
POLE_LANE_PAD = 0.020
COL_SPLIT = 0.55          # x fraction of the body's width, keypad side
COL_GAP = 0.016
KEY_D_F = 0.86            # x the working strip's depth
KEY_PLATE_H = 0.012
PRN_D_F = 0.40            # x the working strip's depth
PRN_H = 0.024
LANE_PAD = 0.008
#: The receipt: 80 mm paper, the till roll of the decade, leaning out of the
#: printer's mouth toward the clerk.
#:
#: 4 mm THICK, AND THAT IS THE PROBE'S NUMBER RATHER THAN A STATIONER'S. At
#: the 1.6 mm a receipt actually is, the slab's own two faces are 1.6 mm
#: apart and `coincident_pairs` reads every register in the library as
#: carrying a coplanar pair -- a paper is a solid here, and a solid thinner
#: than the 2 mm window cannot exist. 4 mm is 2 x the window, the same margin
#: `ART_PROUD` keeps.
PAPER_W = 0.076
PAPER_T = 0.004
PAPER_H_F = 3.2           # x the printer housing's height
#: 15 degrees off upright, not 24: at 24 the slab foreshortens into a flat
#: white card in the clerk's own frame -- measured in
#: `_preview_register/operator.png` before the change.
PAPER_LEAN_DEG = 15.0

#: The operator panel, set in the body's top and tipped toward the clerk.
OP_D_F = 0.34             # x the working strip's depth
OP_IN_X = 0.012           # inset inside its column, so no shared side plane
OP_T = 0.014
OP_TILT_DEG = 22.0

#: The pole: the stem's section, and how the band above the body is split
#: between stem and bezel.
STEM_W = 0.038
STEM_D = 0.030
POLE_BEZEL_F = 0.55
POLE_W_F = 0.52           # x the body's width
POLE_BEZEL_D = 0.040
#: The lit window inside the bezel, as fractions of it.
#:
#: THESE TWO AND `POLE_BEZEL_F` WERE SET BY MEASUREMENT, because they decide
#: whether the digits set at scale 2 or at scale 1 -- which is the difference
#: between 35 mm and 18 mm of green on the display, and the walker's whole
#: question about this species. At 0.46 / 0.78 the SHORTEST slot in the genome
#: (h = 0.38) gave a 28 px window against the 26 px a scale-2 line needs plus
#: 2 px of margin each side: one pixel short, and `digits_layout` halved the
#: digits for it. 0.55 gives 33 px, 3 px of slack over the requirement, at
#: every width. `test_cash_register` holds scale 2 at all 27 corners so the
#: slack cannot be spent silently.
#:
#: 1.46.0: the digits are a smooth face and no longer step by whole scales;
#: the rule is `DIGIT_MIN_M` and the same test holds it at the same corners.
WINDOW_W_F = 0.88
WINDOW_H_F = 0.78

# --- the art -------------------------------------------------------------------

#: Artwork density, pixels per metre (1.46.0, the real look). The two
#: SCREENS are set at `TEXEL` and everything painted -- the keys, the drawer's
#: face, the printer's lid -- at `PAINT_TEXEL`, the density `atm_forms` and
#: `video_poker_forms` paint at. Until 1.46.0 these were 512 and 256 and the
#: art was sampled Closest: `pixel_type`'s 13 px line at a whole scale. A
#: smooth face sets at any height, so the display's digits are now as tall as
#: the window holds (`digits_fit`) and no longer step between 18 and 35 mm.
TEXEL = 1024
PAINT_TEXEL = 768

#: The display's face: Minisystem (CC0, vendored by Pixelcoat 0.54.0 and
#: minted into `smooth_faces/`), a dot-segment face -- the "slanted,
#: broken-stroke silhouette of a real VFD" this module said in 1.0.0 a
#: seven-segment table would have bought and did not mint. Legends on keys
#: are Blue Highway Bold.
FACE = "minisystem"
LEGEND_FACE = "highway_bold"
#: THE RULE THE WALKER ASKED FOR IN 1.0.0, restated in metres: the green
#: digits are at least this tall at every genome corner, and a price that
#: cannot set that tall drops its leading digit before it shrinks.
DIGIT_MIN_M = 0.030
#: The digits' capitals take at most this much of the window's height.
DIGIT_FILL = 0.62
#: Margin inside the customer display, pixels.
PAD = 2

VFD_INK = (56, 240, 104)
VFD_GROUND = (4, 6, 5)
LCD_GROUND = (150, 168, 130)
LCD_INK = (28, 38, 26)
LCD_EDGE = (96, 112, 84)
KEY_GROUND = (30, 30, 32)
KEY_FACE = (176, 174, 166)
KEY_ACCENT_A = (214, 178, 48)
KEY_ACCENT_B = (58, 96, 168)
KEY_COLS = 4
KEY_ROWS = 5
#: What a key says, by (row, column) as the clerk reads them. DIGITS ONLY.
#: Until 1.46.0 the keys carried nothing, by `card_art`'s rule: a key face
#: was 7 px across and a legend at that size is noise. At `PAINT_TEXEL` a key
#: is about 30 px and a digit on it is 14 mm tall, which a player at the
#: counter reads -- so the rule's own test now comes out the other way.
KEY_LEGENDS = {(1, 0): "7", (1, 1): "8", (1, 2): "9",
               (2, 0): "4", (2, 1): "5", (2, 2): "6",
               (3, 0): "1", (3, 1): "2", (3, 2): "3",
               (4, 0): "0", (4, 1): "00", (4, 2): "."}

#: The glow, A/B-ed rather than borrowed -- four builds of the same register,
#: `tools/preview_specimen.py` at 1.6 m straight on, style 4 delco_1997,
#: Cycles CPU 40 samples, world 0.55, the harness's sun. Screen pixels are
#: those that are green-dominant; "pinned" is any channel >= 250, "white" all
#: >= 235; 8-bit sRGB after tonemap, Rec.709 luma, saturation (max-min)/max.
#:
#:   strength        0.6     1.0     1.5     2.5
#:   luma          145.1   159.3   172.8   180.8
#:   saturation    0.479   0.411   0.357   0.311
#:   pinned %          0       0       0       0
#:   white %           0       0       0       0
#:
#: NOTHING PINS AT ANY OF THEM, so the rule `vending_forms` and `crt_forms`
#: chose by -- "the highest strength with no pinned and no white pixel in
#: either preset" -- does not decide this one, and taking it literally here
#: would pick 2.5. What moves instead is SATURATION: the artwork's own is
#: 0.77 and the screen has lost a third of it by 1.5. The walker's words were
#: "bright green"; 1.0 keeps 0.41 at 159 luma, and the extra 8 % of luma at
#: 1.5 costs 13 % of the green. 1.0 is also `vending_forms.PANEL_EMISSION`,
#: which WAS measured in a Godot walk under the two presets that matter.
#:
#: WHAT IS NOT MEASURED, said rather than implied: this A/B is Cycles under a
#: sun, not `gl_compatibility` under Heavy Rain and delco_summer_afternoon
#: with Lux post, which is what the other two lit species carry and the only
#: measurement that describes a client. Re-run it there before moving this
#: number: a preview render can show a wash and cannot price one. It was
#: also made on 1.0.0's pixel digits; the 1.46.0 screen paints its own bloom
#: round the digits and has not been A/B-ed again.
SCREEN_EMISSION = 1.0
SCREEN_ALBEDO = 0.35

#: The one material key: every face of the register is a quad naming a tile
#: in the register's ONE image (1.46.0). Until then the solids were four flat
#: materials -- case, trim, lock, paper -- and the module was six draws.
ART = "art"

#: The body's colour when nobody says: the genome's default, 0.055 linear.
CASE_LINEAR = (0.055, 0.055, 0.06)
#: The trim -- the pull, the keypad island, the printer, the pole -- is the
#: body lifted by this much (8-bit sRGB), NOT a second colour: the smallest
#: lift that separates the parts of a black register under a shop's tubes.
TRIM_LIFT = 22

#: The prices a display can read. Four and five characters both, because the
#: narrow corner of the genome cannot set five at `DIGIT_MIN_M` and a display
#: that shrinks its digits to keep a leading digit is the wrong trade.
#: Invented numbers on a prop; nothing here is a mark.
PRICES = ("4.95", "9.95", "2.50", "14.95", "24.99", "7.25", "34.95", "1.75")
#: What the operator panel says over the price.
LCD_HEAD = "TOTAL"
#: A panel's glass shorter than this, in pixels, carries the price alone.
LCD_TWO_LINES_PX = 44


def _bands(h):
    """(drawer height, body height, pole span) for a slot ``h`` metres tall.

    ONE division, asked once. The three are a partition of ``h`` and the pole
    takes the remainder rather than its own fraction, so the stack lands on
    ``h`` exactly whatever the floats do -- the `_wall_span` lesson: a
    quantity derived twice is two different numbers at the fifth decimal, and
    here the second spelling would be the module's own height.
    """
    dr = DRAWER_F * h
    bo = BODY_F * h
    return dr, bo, h - dr - bo


def layout(w, d, h):
    """Every part of a register at slot (w, d, h).

    Returns a dict of boxes ``(x0, x1, y0, y1, z0, z1)`` in the module frame
    plus the derived planes the prims and the art both need. Raises when the
    slot cannot carry the shape, rather than building a register with a
    negative pole.
    """
    dr_h, bo_h, pole = _bands(h)
    z0, z1 = -h / 2.0, h / 2.0
    yf, yb = -d / 2.0, d / 2.0
    zdt = z0 + dr_h                 # drawer top / body base
    zbt = zdt + bo_h                # body top
    bx0, bx1 = -w / 2.0 + BODY_IN_X, w / 2.0 - BODY_IN_X
    by0, by1 = yf + BODY_IN_FRONT, yb - BODY_IN_BACK
    bw, bd = bx1 - bx0, by1 - by0
    if bw <= 0.10 or bd <= 0.12:
        raise ValueError(f"slot {w} x {d} x {h} leaves a {bw:.3f} x {bd:.3f} body")
    if pole <= 0.05:
        raise ValueError(f"slot height {h} leaves a {pole:.3f} m pole")

    L = {"w": w, "d": d, "h": h, "z0": z0, "z1": z1, "yf": yf, "yb": yb,
         "zdt": zdt, "zbt": zbt, "bands": (dr_h, bo_h, pole),
         "body_top": (bx0, bx1, by0, by1)}

    # --- the drawer, its pull and its lock --------------------------------------
    L["drawer"] = (-w / 2.0, w / 2.0, yf + PULL_T, yb, z0, zdt)
    pull_z = z0 + dr_h * 0.56
    L["pull"] = (-w / 2.0 + PULL_END, w / 2.0 - PULL_END, yf, yf + PULL_T + BURY,
                 pull_z - PULL_H / 2.0, pull_z + PULL_H / 2.0)
    # the lock is PAINTED on the drawer's face since 1.46.0; these are where
    L["lock"] = {"x": w / 2.0 - 0.055, "z": z0 + dr_h * 0.24, "r": LOCK_R}

    # --- the body ----------------------------------------------------------------
    L["body"] = (bx0, bx1, by0, by1, zdt - BURY, zbt)

    # --- the top, in its three lanes ---------------------------------------------
    sy = by0 + LANE_PAD + STEM_D / 2.0                 # the pole stem's centre
    ty0 = by0 + POLE_LANE_PAD + STEM_D                 # the working strip starts
    td = by1 - ty0
    if td < 0.10:
        raise ValueError(f"slot depth {d} leaves a {td:.3f} m working strip")
    xm = bx0 + bw * COL_SPLIT
    L["strip"] = (ty0, by1, xm, td)

    kx0, kx1 = bx0 + LANE_PAD, xm - COL_GAP / 2.0
    kd = td * KEY_D_F
    kyc = (ty0 + by1) / 2.0
    L["keypad"] = (kx0, kx1, kyc - kd / 2.0, kyc + kd / 2.0,
                   zbt - BURY, zbt + KEY_PLATE_H)
    # the keys are the island's own top face (1.46.0), not a quad over it
    L["keypad_art"] = {"centre": ((kx0 + kx1) / 2.0, kyc), "z": zbt + KEY_PLATE_H,
                       "size_m": (kx1 - kx0, kd)}

    cx0, cx1 = xm + COL_GAP / 2.0, bx1 - LANE_PAD
    # the PRINTER sits at the clerk's own edge, where a hand tears a receipt;
    # the PANEL in front of it, tipped up toward the same pair of eyes
    pd_ = td * PRN_D_F
    py1 = by1 - LANE_PAD
    L["printer"] = (cx0, cx1, py1 - pd_, py1, zbt - BURY, zbt + PRN_H)
    paper_h = PRN_H * PAPER_H_F
    L["paper"] = {"w": min(PAPER_W, (cx1 - cx0) * 0.82), "t": PAPER_T,
                  "h": paper_h, "x": (cx0 + cx1) / 2.0,
                  "hinge": (py1 - 0.012, zbt + PRN_H - BURY),
                  "lean": math.radians(PAPER_LEAN_DEG)}

    od = td * OP_D_F
    oy1 = py1 - pd_ - COL_GAP
    L["op_panel"] = {"x": (cx0 + OP_IN_X, cx1 - OP_IN_X),
                     "y": (oy1 - od, oy1),
                     "t": OP_T, "hinge": (oy1 - od / 2.0, zbt),
                     "tilt": math.radians(OP_TILT_DEG),
                     "size_m": (cx1 - cx0 - 2 * OP_IN_X, od)}
    if L["op_panel"]["y"][0] <= ty0:
        raise ValueError(f"slot depth {d} leaves no room for the operator panel")

    # --- the pole ----------------------------------------------------------------
    bez_h = pole * POLE_BEZEL_F
    bez_w = bw * POLE_W_F
    L["stem"] = (-STEM_W / 2.0, STEM_W / 2.0, sy - STEM_D / 2.0, sy + STEM_D / 2.0,
                 zbt - BURY, z1 - bez_h + BURY)
    L["bezel"] = (-bez_w / 2.0, bez_w / 2.0, sy - POLE_BEZEL_D / 2.0,
                  sy + POLE_BEZEL_D / 2.0, z1 - bez_h, z1)
    # THE OPENING in the bezel's face, and THE GLASS behind it: the surround
    # slopes in from one to the other (`machine_parts.wells`). Until 1.46.0
    # the glass was a quad standing 4 mm PROUD of a flat bezel.
    win_w, win_h = bez_w * WINDOW_W_F, bez_h * WINDOW_H_F
    yh = sy - POLE_BEZEL_D / 2.0
    zc = z1 - bez_h / 2.0
    L["window"] = {"x": (-win_w / 2.0, win_w / 2.0),
                   "z": (zc - win_h / 2.0, zc + win_h / 2.0), "y": yh}
    sw, sh = win_w - 2.0 * WELL_M, win_h - 2.0 * WELL_M
    L["screen"] = {"x": (-sw / 2.0, sw / 2.0), "z": (zc - sh / 2.0, zc + sh / 2.0),
                   "y": yh + SCREEN_RECESS, "size_m": (sw, sh)}
    if yh <= yf:
        raise ValueError(f"slot depth {d} puts the pole display through the front plane")
    return L


# --- the type ---------------------------------------------------------------------


def digits_fit(candidates, w_px, h_px, pad=PAD, floor_px=None):
    """``(text, cap_px)``: the first candidate -- they come longest first --
    whose capitals set at least ``floor_px`` tall inside ``w_px`` x ``h_px``,
    as tall as the window holds. When none reaches the floor, the candidate
    that sets tallest, so a caller always gets digits.

    ONE fit, asked once per candidate: across and down are both answered by
    `smooth_type.fit_cap` at a height capped by the window's.
    """
    floor_px = int(math.ceil(DIGIT_MIN_M * TEXEL)) if floor_px is None else int(floor_px)
    most = max(5, int(h_px * DIGIT_FILL))
    best = None
    for text in candidates:
        # the stroke is fattened by `stroke(cap)` pixels (`paint_screen`)
        cap = ST.fit_cap(text, w_px - 2 * pad - stroke(most), most, FACE, 5)
        if cap is None:
            continue
        if cap >= floor_px:
            return text, cap
        if best is None or cap > best[1]:
            best = (text, cap)
    if best is None:
        raise ValueError(f"no price in {list(candidates)} sets in {w_px} x {h_px} px")
    return best


def stroke(cap):
    """How many pixels a display's stroke is fattened by at ``cap``.

    MEASURED ON A FRAME, 2026-10-02: Minisystem's own hairline, set once or
    twice, came out thinner and dimmer than the pixel digits it replaced --
    the opposite of "bright green". A tube's segment is about a fourteenth
    of its digit's height wider than the face draws it."""
    return max(1, int(cap) // 14)


def _fat(cov, n):
    """``cov`` (uint8 rows x cols) grown ``n`` px right and down: the max
    over every shift, so a dot stays a dot and only gets heavier."""
    import numpy as np
    h, w = cov.shape
    out = np.zeros((h + n, w + n), dtype=np.uint8)
    for dy in range(n + 1):
        for dx in range(n + 1):
            view = out[dy:dy + h, dx:dx + w]
            np.maximum(view, cov, out=view)
    return out


def _lift(rgb, by):
    return tuple(max(0.0, min(255.0, c + by)) for c in rgb)


def srgb8(rgb):
    """A material's LINEAR colour as the 8-bit sRGB a painted tile holds."""
    out = []
    for c in list(rgb)[:3]:
        c = max(0.0, min(1.0, float(c)))
        s = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1.0 / 2.4) - 0.055
        out.append(int(round(s * 255.0)))
    return tuple(out)


CASE_RGB = srgb8(CASE_LINEAR)


def _px(m):
    return max(8, int(round(m * TEXEL)))


def _ppx(m):
    return max(8, int(round(m * PAINT_TEXEL)))


def paint_screen(text, cap, w_px, h_px):
    """The customer display: bright green dot-segment type on a black tube,
    its own bloom round it, and the tube's rim in shadow under the bezel."""
    im = PT.Img(w_px, h_px, VFD_GROUND)
    im.vgrad((0, 0, w_px, h_px), _lift(VFD_GROUND, 6), VFD_GROUND)
    cov = _fat(ST.coverage(text, cap, FACE), stroke(cap))
    ch, cw = cov.shape
    im.mask(cov, (w_px - cw) // 2, (h_px - ch) // 2, VFD_INK)
    im.glow((0, 0, w_px, h_px), max(2, cap // 8), 0.6)
    # the grid mesh over the phosphor, and the glass over that
    im.scanlines((0, 0, w_px, h_px), 3, 0.08)
    im.vignette((0, 0, w_px, h_px), 0.18)
    im.gloss((0, 0, w_px, h_px), 0.04)
    im.edge_dark((0, 0, w_px, h_px), max(3.0, h_px * 0.06), 0.4)
    return im.to_canvas()


def _plastic(w, h, rgb, seed, top=14, foot=-20, rim=0.18):
    """Moulded plastic under a ceiling's light: graded, grained, and darker
    toward the edges where it meets its neighbours."""
    im = PT.Img(w, h, rgb)
    im.vgrad((0, 0, w, h), _lift(rgb, top), _lift(rgb, foot))
    im.grain((0, 0, w, h), 1.4, seed)
    if rim:
        im.edge_dark((0, 0, w, h), min(w, h) * 0.2, rim)
    return im


def paint_lcd(text, w_px, h_px, trim=None):
    """The operator panel's top: its bezel, and in it a reflective LCD --
    dark type on a green-grey ground, each stroke's shadow on the reflector.

    Returns ``(canvas, lines)``. A glass tall enough carries `LCD_HEAD` over
    the price; a shorter one the price alone, because the number is the half
    a clerk reads.
    """
    trim = _lift(CASE_RGB, TRIM_LIFT) if trim is None else trim
    im = _plastic(w_px, h_px, trim, 17, 6, -6, 0.2)
    gx, gy = w_px * 0.08, h_px * 0.11
    glass = (gx, gy, w_px - gx, h_px - gy)
    gh = glass[3] - glass[1]
    im.rrect(glass, 3, LCD_GROUND)
    im.vgrad((gx + 2, gy + 2, w_px - gx - 2, h_px - gy - 2),
             _lift(LCD_GROUND, 8), _lift(LCD_GROUND, -12))
    im.edge_dark(glass, gh * 0.16, 0.30)
    im.bevel(glass, 2, 20.0, 40.0, raised=False)
    lines = [LCD_HEAD, text] if gh >= LCD_TWO_LINES_PX else [text]
    tx0, tx1 = gx + 6, w_px - gx - 6
    shade = _lift(LCD_GROUND, -34)
    if len(lines) == 2:
        im.text(LCD_HEAD, (tx0, gy + gh * 0.10, tx1, gy + gh * 0.36), LCD_INK,
                "highway_cond", align="left", shadow=shade)
        band = (gy + gh * 0.44, gy + gh * 0.90)
    else:
        band = (gy + gh * 0.18, gy + gh * 0.82)
    # the price: the display's face, its stroke fattened as the tube's is
    most = max(5, int(band[1] - band[0]))
    cap = ST.fit_cap(text, tx1 - tx0 - stroke(most), most, FACE, 5)
    if cap is None:
        im.unset.append(text)
    else:
        cov = _fat(ST.coverage(text, cap, FACE), stroke(cap))
        ch, cw = cov.shape
        x, y = tx1 - cw, band[0] + (band[1] - band[0] - ch) / 2.0
        im.mask(cov, x + 1, y + 1, shade, 0.7)
        im.mask(cov, x, y, LCD_INK)
    im.gloss(glass, 0.06)
    c = im.to_canvas()
    return c, lines


def paint_keys(w_px, h_px):
    """The keypad island's top: `KEY_COLS` x `KEY_ROWS` bevelled keys on a
    dark plate, grey save for one yellow and one blue at the edges -- the
    reference's "mostly grey/white with a few coloured ones" -- each with its
    shadow on the plate, and `KEY_LEGENDS` on the number block.
    """
    im = PT.Img(w_px, h_px, KEY_GROUND)
    mx, my = w_px * 0.05, h_px * 0.05
    pitch_x = (w_px - 2 * mx) / KEY_COLS
    pitch_y = (h_px - 2 * my) / KEY_ROWS
    gap = max(1.5, min(pitch_x, pitch_y) * 0.10)
    # THE SHADE IS PER KEY POSITION AND NOT PER REGISTER, and that is a
    # texture decision rather than an art one. Seeded on the module's stem,
    # two counters in one shop draw two atlases that differ in a 3 % grey
    # nobody can see, and the second one costs a client a second decoded
    # texture for it. Keyed on the grid, every register of a size and a
    # price shares one image.
    seed = zlib.crc32(f"keys:{w_px}x{h_px}".encode("utf-8"))
    for r in range(KEY_ROWS):
        for col in range(KEY_COLS):
            box = (mx + col * pitch_x + gap, my + r * pitch_y + gap,
                   mx + (col + 1) * pitch_x - gap, my + (r + 1) * pitch_y - gap)
            bw, bh = box[2] - box[0], box[3] - box[1]
            if bw < 3 or bh < 3:
                continue
            if col == KEY_COLS - 1 and r == 0:
                rgb = KEY_ACCENT_A
            elif col == KEY_COLS - 1 and r == KEY_ROWS - 1:
                rgb = KEY_ACCENT_B
            else:
                # a moulded key row is not one flat grey: a seeded 3 % shade
                # per key is what stops the grid reading as a printed table
                v = ((seed >> ((r * KEY_COLS + col) % 24)) & 0x07) - 3
                rgb = tuple(max(0, min(255, ch + v * 3)) for ch in KEY_FACE)
            rad = min(bw, bh) * 0.16
            im.rrect((box[0] + 1, box[1] + 2, box[2] + 1, box[3] + 2.5), rad, (0, 0, 0), 0.55)
            im.rrect(box, rad, rgb)
            im.vgrad((box[0] + 2, box[1] + 2, box[2] - 2, box[3] - 2),
                     _lift(rgb, 16), _lift(rgb, -14))
            im.bevel(box, 2, 22.0, 40.0)
            legend = KEY_LEGENDS.get((r, col))
            if legend:
                im.text(legend, (box[0] + 2, box[1] + bh * 0.22, box[2] - 2, box[3] - bh * 0.22),
                        (26, 26, 30), LEGEND_FACE)
    im.edge_dark((0, 0, w_px, h_px), min(w_px, h_px) * 0.06, 0.3)
    return im.to_canvas()


def paint_drawer(L, rgb):
    """The drawer's face: its moulded panel line, the shadow the pull bar
    throws down it, and the lock -- a bright barrel with its keyway."""
    x0 = -L["w"] / 2.0 + DRAWER_C
    fw, fh = L["w"] - 2.0 * DRAWER_C, L["bands"][0]
    W, H = _ppx(fw), _ppx(fh)

    def at(x, z):
        return (x - x0) / fw * W, (L["zdt"] - z) / fh * H

    im = _plastic(W, H, rgb, 11)
    px0, px1, _y0, _y1, pz0, pz1 = L["pull"]
    ax, ay = at(px0, pz1)
    bx, by = at(px1, pz0)
    im.rrect((ax - 2, ay, bx + 2, by + (by - ay) * 1.1), 3, (0, 0, 0), 0.6)
    im.blur((0, max(0, ay - 6), W, min(H, by + (by - ay) * 1.6 + 6)), 2)
    m = max(3.0, H * 0.06)
    dark, light = _lift(rgb, -34), _lift(rgb, 26)
    for box in ((m, m, W - m, m + 1.5), (m, H - m - 1.5, W - m, H - m),
                (m, m, m + 1.5, H - m), (W - m - 1.5, m, W - m, H - m)):
        im.rect(box, dark)
    im.rect((m, m + 1.5, W - m, m + 2.5), light, 0.35)
    lk = L["lock"]
    cx, cy = at(lk["x"], lk["z"])
    r = lk["r"] * PAINT_TEXEL
    im.disc(cx + 1, cy + 1.5, r + 1, (0, 0, 0), 0.45)
    im.disc(cx, cy, r, (168, 170, 176))
    im.disc(cx - r * 0.25, cy - r * 0.3, r * 0.45, (232, 234, 238), 0.7)
    im.rect((cx - 0.8, cy - r * 0.55, cx + 0.8, cy + r * 0.55), (30, 30, 34))
    return im.to_canvas()


def paint_printer(L, trim):
    """The printer's lid as the clerk sees it (the image's top is the
    customer's edge): the mouth the paper stands in, and three vent slits."""
    x0, x1, y0, y1, _z0, _z1 = L["printer"]
    W, H = _ppx(x1 - x0), _ppx(y1 - y0)
    im = _plastic(W, H, trim, 13, 6, -6, 0.22)
    pa = L["paper"]
    row = (pa["hinge"][0] - y0) / (y1 - y0) * H
    half = pa["w"] / (x1 - x0) * W / 2.0 + 3.0
    slot = (W / 2.0 - half, row - 3.5, W / 2.0 + half, row + 3.5)
    im.rrect(slot, 2, (4, 4, 5))
    im.bevel(slot, 2, 24.0, 36.0, raised=False)
    for i in range(3):
        yv = H * (0.14 + 0.10 * i)
        im.rrect((W * 0.2, yv, W * 0.8, yv + 2.2), 1, _lift(trim, -34))
    return im.to_canvas()


def paint_paper():
    """Till roll: white, a little grey down its length, and the rows a
    printer leaves -- bars, not words, because a receipt at this size is its
    rhythm and not its text."""
    W, H = 56, 88
    im = PT.Img(W, H, (236, 234, 226))
    im.vgrad((0, 0, W, H), (244, 242, 236), (220, 218, 210))
    for i, n in enumerate((34, 22, 40, 28, 36, 18, 30)):
        y = 12 + i * 10
        im.rect((7, y, 7 + n * 0.6, y + 2), (120, 120, 124), 0.55)
        im.rect((W - 16, y, W - 7, y + 2), (120, 120, 124), 0.55)
    return im.to_canvas()


def art(L, price, rgb=None, key=""):
    """The register's ONE texture: the two displays, the keys and every
    panel of the body, packed with a gutter each tile bleeds into
    (`card_art.atlas`) because the image is sampled with filtering.

    ``rgb`` is the body's colour, 8-bit sRGB. Returns the canvas, each
    tile's pixel rect (row 0 at the top), and a NAME derived from the
    pixels, so two registers reading the same price at the same size in the
    same colour share one image.
    """
    rgb = CASE_RGB if rgb is None else tuple(rgb)
    trim = _lift(rgb, TRIM_LIFT)
    sw, sh = (_px(v) for v in L["screen"]["size_m"])
    text, cap = digits_fit(_price_forms(price), sw, sh)
    ow, oh = (_ppx(v) for v in L["op_panel"]["size_m"])
    # THE TWO DISPLAYS READ THE SAME NUMBER. `digits_fit` may have dropped a
    # leading digit to keep the pole's type at `DIGIT_MIN_M`, and a pole
    # saying 4.99 over a panel saying 24.99 is a defect a player can see.
    lcd, lcd_lines = paint_lcd(text, ow, oh, trim)
    kw, kh = (_ppx(v) for v in L["keypad_art"]["size_m"])
    well = PT.Img(24, 24, trim)
    well.vgrad((0, 0, 24, 24), _lift(trim, -46), _lift(trim, 6))    # dark at the glass
    pull = _plastic(48, 16, _lift(trim, 12), 23, 30, -26, 0.0)
    tiles = [
        ("screen", paint_screen(text, cap, sw, sh)),
        ("lcd", lcd),
        ("keys", paint_keys(kw, kh)),
        ("drawer", paint_drawer(L, rgb)),
        ("printer", paint_printer(L, trim)),
        ("paper", paint_paper()),
        ("case", _plastic(64, 64, rgb, 3).to_canvas()),
        ("case_edge", _plastic(16, 64, _lift(rgb, 16), 4, 14, -20, 0.0).to_canvas()),
        ("case_top", _plastic(64, 64, _lift(rgb, 8), 5, 4, -4, 0.22).to_canvas()),
        ("trim", _plastic(48, 48, trim, 6).to_canvas()),
        ("trim_edge", _plastic(16, 48, _lift(trim, 16), 7, 14, -20, 0.0).to_canvas()),
        ("trim_top", _plastic(48, 48, _lift(trim, 8), 8, 4, -4, 0.22).to_canvas()),
        ("well", well.to_canvas()),
        ("pull", pull.to_canvas()),
    ]
    A = CA.atlas(tiles, "register", gutter=CA.SMOOTH_GUTTER, bleed=True)
    A.update({"price": price, "text": text, "cap": cap,
              # the digits' height on the real display, which is the number
              # the walker's question ("does it read?") is actually about
              "digit_h_m": round(cap / float(TEXEL), 5), "lcd_lines": lcd_lines,
              "unset": [s for _k, c in tiles for s in getattr(c, "unset", [])]})
    return A


def _price_forms(price):
    """The display's candidates, longest first: the price, and the price with
    its leading digit dropped where that leaves a sane number. The narrow
    corner of the genome sets four characters at `DIGIT_MIN_M` and five only
    smaller, and short digits to keep a leading digit is the wrong trade."""
    out = [price]
    if len(price) > 4 and price[1] != ".":
        out.append(price[1:])
    return out


def pick_price(plan, streams=None):
    """The price on the display, deterministically: an explicit
    ``params.price`` if it is in the table, else the entry at ``variant`` of an
    order drawn from the module's stem WITHOUT its variant suffix -- so the
    variants of one slot read different prices. `vending_forms.pick_brand`'s
    rule, and for the same reason."""
    asked = str((plan.get("params") or {}).get("price") or "")
    if asked in PRICES:
        return asked
    module = plan.get("module") or {}
    stem = module.get("stem")
    if stem:
        import re
        base = re.sub(r"_n\d+(?=_|$)", "", stem)
        order = sorted(PRICES,
                       key=lambda s: (zlib.crc32(f"{base}:{s}".encode("utf-8")), s))
        return order[int(module.get("variant") or 0) % len(order)]
    if streams is not None:
        return streams.stream("register_price").choice(list(PRICES))
    return PRICES[0]


# --- the primitives ----------------------------------------------------------------


def _tbox(part, b, tile, faces=("front", "right", "back", "left", "top")):
    """A plain box's named faces as quads on one tile, each wound to face
    out: ``front`` is -Y. For the parts too small to carry a chamfer."""
    x0, x1, y0, y1, z0, z1 = b
    walls = {"front": ((x0, y0), (x1, y0)), "right": ((x1, y0), (x1, y1)),
             "back": ((x1, y1), (x0, y1)), "left": ((x0, y1), (x0, y0))}
    out = []
    for name in faces:
        if name in walls:
            a, c = walls[name]
            verts = [(a[0], a[1], z0), (c[0], c[1], z0), (c[0], c[1], z1), (a[0], a[1], z1)]
        elif name == "top":
            verts = [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        else:                                               # bottom
            verts = [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)]
        out.append(MP.quad(f"{part}_{name}", ART, tile, verts))
    return out


def _clerk(p):
    """Turn a face-up tile round SO THE CLERK CAN READ IT.

    The operator stands at +Y and looks along -Y, so what is "up" in the
    image is the -Y edge and what is "right" is -X -- their right hand, the
    same frame the keypad's lanes are laid out in. `machine_parts.poly` lays
    a tile over a face's bounds for a viewer at -Y; half a turn is both axes
    reversed, so the tile's bottom-left lands on the (+X, +Y) corner.

    MEASURED, not reasoned, in 1.0.0: the first draft had it the customer's
    way up and `_preview_register/operator.png` came back with TOTAL 24.99
    upside down and mirrored. Nothing else in the module would have said so.
    """
    q = dict(p)
    q["uvs"] = [tuple((1.0 - u, 1.0 - v) for u, v in f) for f in p["uvs"]]
    return q


def _island(part, b, c, top, clerk=True):
    """A chamfered trim block standing on the body, its top a tile."""
    x0, x1, y0, y1, z0, z1 = b
    out = MP.cbody(part, x0, x1, y0, y1, z0, z1, c, side="trim", edge="trim_edge",
                   top=top, mat=ART)
    if clerk:
        out[-1] = _clerk(out[-1])
    return out


def plan(w, d, h, params=None, variant=0, price=None, key="", rgb=None):
    """The whole register: ``{"prims", "art", "collision", "attachments",
    "facts"}``. Every prim is a face naming its tile in ``art``; the customer
    screen alone carries ``lit``. ``rgb`` is the body's colour, 8-bit sRGB."""
    params = params or {}
    L = layout(w, d, h)
    price = price if price in PRICES else PRICES[int(variant) % len(PRICES)]
    A = art(L, price, rgb, key)
    prims = []

    # the drawer: its front the painted face, behind the pull bar
    dx0, dx1, dy0, dy1, dz0, dz1 = L["drawer"]
    prims += MP.cbody("Register_Drawer", dx0, dx1, dy0, dy1, dz0, dz1, DRAWER_C,
                      skip=("front",), side="case", edge="case_edge", top="case_top", mat=ART)
    prims.append(MP.quad("Register_Drawer_front", ART, "drawer",
                         [(dx0 + DRAWER_C, dy0, dz0), (dx1 - DRAWER_C, dy0, dz0),
                          (dx1 - DRAWER_C, dy0, dz1), (dx0 + DRAWER_C, dy0, dz1)]))
    prims += _tbox("Register_Pull", L["pull"], "pull",
                   faces=("front", "left", "right", "top", "bottom"))

    bx0, bx1, by0, by1, bz0, bz1 = L["body"]
    prims += MP.cbody("Register_Body", bx0, bx1, by0, by1, bz0, bz1, BODY_C,
                      side="case", edge="case_edge", top="case_top", mat=ART)
    prims += _island("Register_Keypad", L["keypad"], PART_C, "keys")
    prims += _island("Register_Printer", L["printer"], PART_C, "printer")

    pa = L["paper"]
    hy, hz = pa["hinge"]
    # the roll leans toward the clerk; the hinge is the printer's mouth, so
    # the lean pivots about the slot rather than about the paper's middle
    for q in _tbox("Register_Paper",
                   (pa["x"] - pa["w"] / 2.0, pa["x"] + pa["w"] / 2.0,
                    hy - pa["t"] / 2.0, hy + pa["t"] / 2.0, hz, hz + pa["h"]), "paper"):
        prims.append(P.rotate_x(q, -pa["lean"], about=pa["hinge"]))

    op = L["op_panel"]
    ox0, ox1 = op["x"]
    oy0, oy1 = op["y"]
    for q in _island("Register_OpBezel", (ox0, ox1, oy0, oy1, op["hinge"][1] - 0.006,
                                          op["hinge"][1] + op["t"]), PART_C, "lcd"):
        prims.append(P.rotate_x(q, -op["tilt"], about=op["hinge"]))

    prims += _tbox("Register_Stem", L["stem"], "trim", faces=("front", "right", "back", "left"))
    # the pole's head: its front a surround sloping in to the glass
    ex0, ex1, ey0, ey1, ez0, ez1 = L["bezel"]
    head = MP.cbody("Register_Bezel", ex0, ex1, ey0, ey1, ez0, ez1, PART_C, skip=("front",),
                    side="trim", edge="trim_edge", top="trim_top", mat=ART)
    prims += head
    prims.append(MP.poly("Register_Bezel_under", ART, "trim",
                         [(x, y, ez0) for x, y, _z in reversed(head[-1]["verts"])]))
    win, scr = L["window"], L["screen"]
    hole = (win["x"][0], win["x"][1], win["z"][0], win["z"][1])
    glass = (scr["x"][0], scr["x"][1], scr["z"][0], scr["z"][1])
    prims += MP.bezel("Register", ex0 + PART_C, ex1 - PART_C, ez0, ez1, hole, win["y"],
                      tile="trim", mat=ART)
    prims += MP.wells("Register", hole, glass, win["y"], scr["y"], tile="well", mat=ART)
    # THE LIT FACE LOOKS AT THE CUSTOMER (-Y), and the winding is what
    # decides that: ascending X gives a -Y normal, descending X gives +Y and
    # a display only the bezel can read. The first draft had it descending;
    # `test_the_screen_faces_the_customer` is the measurement, because a
    # backfacing quad renders as nothing and nothing else says why.
    screen = MP.quad("Register_Screen", ART, "screen",
                     [(scr["x"][0], scr["y"], scr["z"][0]), (scr["x"][1], scr["y"], scr["z"][0]),
                      (scr["x"][1], scr["y"], scr["z"][1]), (scr["x"][0], scr["y"], scr["z"][1])])
    screen["lit"] = True
    prims.append(screen)

    ka = L["keypad_art"]
    collision = [((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, h / 2.0))]
    facts = {"tris": P.tri_count(prims), "budget": TRI_BUDGET,
             "price": price, "digits": A["text"], "digit_cap_px": A["cap"],
             "digit_h_m": A["digit_h_m"], "lcd_lines": A["lcd_lines"],
             "art": A["name"], "art_px": A["size"], "unset": A["unset"],
             "screen_m": tuple(round(v, 4) for v in scr["size_m"]),
             "bands_m": tuple(round(v, 4) for v in L["bands"])}
    return {"prims": prims, "art": A, "collision": collision,
            "attachments": {
                "ATT_screen_center": (0.0, scr["y"], (scr["z"][0] + scr["z"][1]) / 2.0),
                "ATT_keypad_center": (ka["centre"][0], ka["centre"][1], ka["z"])},
            "facts": facts}


def triangles(got):
    """What the recipe emits -- and nothing here asks for a bevel: the
    corners are broken in the plan (`machine_parts.cbody`), where they are
    counted."""
    return P.tri_count(got["prims"])


def extents(got):
    """(lo, hi) over every primitive, in the module frame."""
    return P.bounds(got["prims"])


def uv(rect, size):
    """A tile's pixel rect -> (u0, v0, u1, v1), v up."""
    return uv_rect(rect, size)
