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
"""
from __future__ import annotations

import math
import zlib

from . import pixel_type as pt
from . import prims as P
from .vending_forms import Canvas, uv_rect

# --- the budget ----------------------------------------------------------------

#: Triangles, whole module, at every genome corner. Set BEFORE the layout was
#: drawn (see the module docstring for the company it is in). The count does
#: not move with the slot -- every part is a box or a fixed-segment cylinder
#: -- so one number holds at all 27 corners and `triangles` proves it.
TRI_BUDGET = 200

# --- the frame -----------------------------------------------------------------

#: Burial past a contact plane: 3 x the coplanar probe's 2 mm window.
BURY = 0.006
#: Art stands this far off the face it prints on -- 2 x the window.
ART_PROUD = 0.004

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
LOCK_R = 0.008
LOCK_SEGMENTS = 6
LOCK_PROUD = 0.004        # how far the barrel stands out of the drawer face
LOCK_SINK = 0.010         # and how far past the pull bar's back it reaches

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
WINDOW_W_F = 0.88
WINDOW_H_F = 0.78

# --- the art -------------------------------------------------------------------

#: Artwork density, pixels per metre, for the two SCREENS:
#: `vending_forms.LABEL_TEXEL`, which is what the vending machine's lit price
#: readout is drawn at and the nearest thing in the library to this one.
TEXEL = 512
#: And for the KEYPAD: `card_art.TEXEL`, the factory's 4 mm pixel. A key face
#: is a flat rectangle and a rectangle needs no more, so the keypad tile is
#: painted at a quarter of the screens' area -- 44 x 64 px at the default
#: slot against 88 x 128, which is 24 KiB of the atlas's decoded size. The
#: screens keep 512 because a GLYPH does need it: `pixel_type`'s line is 13
#: px tall whatever the metres are, and at 256 the digits would set one whole
#: scale smaller (see `WINDOW_H_F`).
KEY_TEXEL = 256
#: Margin inside a painted window, pixels.
PAD = 2

#: The one typeface. `pixel_type` is Pixelcoat's Pixel Operator Bold at 16 px
#: -- the factory's face, the one `card_art`'s letterer (`_stamp`) sets every
#: card-shop sign in, and the one `vending_forms.paint_display` already sets a
#: LIT PRICE READOUT in. The other face in this repo, `neon_forms.FONT_5X7`,
#: is not a raster at all where it is used: `glyph_runs` turns a glyph into
#: the SKELETON of a bent glass tube and the recipe builds rods from it, which
#: is a geometry face, not a screen face. A third table of digit shapes -- a
#: true seven-segment set -- was not minted: the repo already carries three
#: glyph sources (`pixel_type`, `FONT_5X7`, `_legend`'s cell grid) and a
#: fourth is a maintenance cost paid for a look that Pixel Operator's blocky
#: digits, green on black at the size below, already deliver.
#:
#: WHAT THE SEVEN-SEGMENT VERSION WOULD HAVE BOUGHT, said rather than quietly
#: dropped: the slanted, broken-stroke silhouette of a real VFD, which reads
#: as "register" at a glance in a way a square pixel face does not quite.
#: Reopen it the day a second species wants segment digits.
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
#: number: a preview render can show a wash and cannot price one.
SCREEN_EMISSION = 1.0
SCREEN_ALBEDO = 0.35

#: Material keys.
CASE, TRIM, LOCK, PAPER, ART = "case", "trim", "lock", "paper", "art"

#: The prices a display can read. Four and five characters both, because the
#: narrow corner of the genome can only set four at scale 2 and a display
#: that halves its digits to keep a leading digit is the wrong trade. Invented
#: numbers on a prop; nothing here is a mark.
PRICES = ("4.95", "9.95", "2.50", "14.95", "24.99", "7.25", "34.95", "1.75")
#: What the operator panel says over the price.
LCD_HEAD = "TOTAL"


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
    L["lock"] = {"x": w / 2.0 - 0.055, "z": z0 + dr_h * 0.24, "r": LOCK_R,
                 "y": (yf + PULL_T - LOCK_PROUD, yf + PULL_T + LOCK_SINK)}

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
    kw = kx1 - kx0
    L["keypad_art"] = {"x": (kx0 + kw * 0.03, kx1 - kw * 0.03),
                       "y": (kyc - kd * 0.47, kyc + kd * 0.47),
                       "z": zbt + KEY_PLATE_H + ART_PROUD,
                       "size_m": (kw * 0.94, kd * 0.94)}

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
                     "size_m": ((cx1 - cx0 - 2 * OP_IN_X) * 0.86, od * 0.80)}
    if L["op_panel"]["y"][0] <= ty0:
        raise ValueError(f"slot depth {d} leaves no room for the operator panel")

    # --- the pole ----------------------------------------------------------------
    bez_h = pole * POLE_BEZEL_F
    bez_w = bw * POLE_W_F
    L["stem"] = (-STEM_W / 2.0, STEM_W / 2.0, sy - STEM_D / 2.0, sy + STEM_D / 2.0,
                 zbt - BURY, z1 - bez_h + BURY)
    L["bezel"] = (-bez_w / 2.0, bez_w / 2.0, sy - POLE_BEZEL_D / 2.0,
                  sy + POLE_BEZEL_D / 2.0, z1 - bez_h, z1)
    win_w, win_h = bez_w * WINDOW_W_F, bez_h * WINDOW_H_F
    L["window"] = {"x": (-win_w / 2.0, win_w / 2.0),
                   "z": (z1 - bez_h / 2.0 - win_h / 2.0, z1 - bez_h / 2.0 + win_h / 2.0),
                   "y": sy - POLE_BEZEL_D / 2.0 - ART_PROUD,
                   "size_m": (win_w, win_h)}
    if L["window"]["y"] <= yf:
        raise ValueError(f"slot depth {d} puts the pole screen through the front plane")
    return L


# --- the type ---------------------------------------------------------------------


def digits_layout(candidates, w_px, h_px, pad=PAD):
    """``(text, scale)``: the largest whole scale any candidate sets at inside
    ``w_px`` x ``h_px``, and the LONGEST candidate that sets at it.

    Two questions -- does it fit across, does it fit down -- asked of one
    layout rather than of two spellings of it. Falls back to the shortest
    candidate at scale 1 when nothing fits, so a caller always gets digits.
    """
    aw, ah = w_px - 2 * pad, h_px - 2 * pad
    best = 0
    for text in candidates:
        s = 0
        for k in range(1, 5):
            if pt.ink_width(text, k) <= aw and pt.LINE * k <= ah:
                s = k
            else:
                break
        best = max(best, s)
    if best == 0:
        return min(candidates, key=len), 1
    for text in sorted(candidates, key=len, reverse=True):
        s = 0
        for k in range(1, 5):
            if pt.ink_width(text, k) <= aw and pt.LINE * k <= ah:
                s = k
            else:
                break
        if s == best:
            return text, best
    raise AssertionError("a scale was found and then lost")   # pragma: no cover


def _centre(c, mask, x0, x1, y0, y1, rgb):
    """Stamp ``mask`` centred in the pixel box, clipped by `Canvas.px`."""
    c.mask(mask, x0 + ((x1 - x0) - len(mask[0])) // 2,
           y0 + ((y1 - y0) - len(mask)) // 2, rgb)


def paint_screen(text, scale, w_px, h_px):
    """The customer display: bright green type on a black screen."""
    c = Canvas(w_px, h_px, VFD_GROUND)
    _centre(c, pt.trim(pt.render(text, scale)), 0, w_px, 0, h_px, VFD_INK)
    return c


def paint_lcd(price, w_px, h_px):
    """The operator panel: dark type on a green-grey reflective ground.

    Stacks as many of (`LCD_HEAD`, the price) as fit at scale 1; a window too
    short for both carries the price alone, because the number is the half a
    clerk reads.
    """
    c = Canvas(w_px, h_px, LCD_GROUND)
    c.rect(0, 0, w_px, 1, LCD_EDGE)
    c.rect(0, h_px - 1, w_px, h_px, LCD_EDGE)
    c.rect(0, 0, 1, h_px, LCD_EDGE)
    c.rect(w_px - 1, 0, w_px, h_px, LCD_EDGE)
    masks = [pt.trim(pt.render(t, 1)) for t in (LCD_HEAD, price)]
    gap = 2
    block = sum(len(m) for m in masks) + gap * (len(masks) - 1)
    while len(masks) > 1 and block > h_px - 4:
        masks.pop(0)
        block = sum(len(m) for m in masks) + gap * (len(masks) - 1)
    y = (h_px - block) // 2
    for m in masks:
        c.mask(m, max(2, (w_px - len(m[0])) // 2), y, LCD_INK)
        y += len(m) + gap
    return c, [LCD_HEAD, price][-len(masks):]


def paint_keys(w_px, h_px):
    """The keypad: `KEY_COLS` x `KEY_ROWS` square keys in a dark well, grey
    save for one yellow and one blue at the edges -- the reference's "mostly
    grey/white with a few coloured ones".

    NO LETTERING, and that is `card_art`'s rule rather than a saving: a key
    face is 18 px across here, and a legend at that size is noise costing the
    pixels a legend somebody can read would cost.
    """
    c = Canvas(w_px, h_px, KEY_GROUND)
    pitch_x = (w_px - 2) / KEY_COLS
    pitch_y = (h_px - 2) / KEY_ROWS
    gap = max(1, int(round(min(pitch_x, pitch_y) * 0.16)))
    # THE SHADE IS PER KEY POSITION AND NOT PER REGISTER, and that is a
    # texture decision rather than an art one. Seeded on the module's stem,
    # two counters in one shop draw two atlases that differ in a 3 % grey
    # nobody can see, and the second one costs a client another 37 KiB of
    # decoded texture for it. Keyed on the grid, every register of a size
    # and a price shares one image.
    seed = zlib.crc32(f"keys:{w_px}x{h_px}".encode("utf-8"))
    for r in range(KEY_ROWS):
        for col in range(KEY_COLS):
            x0 = 1 + int(round(col * pitch_x)) + gap
            x1 = 1 + int(round((col + 1) * pitch_x)) - gap
            y0 = 1 + int(round(r * pitch_y)) + gap
            y1 = 1 + int(round((r + 1) * pitch_y)) - gap
            if x1 - x0 < 1 or y1 - y0 < 1:
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
            c.rect(x0, y0, x1, y1, rgb)
    return c


def art(L, price, key=""):
    """The register's ONE texture: the customer screen, the operator panel and
    the keypad packed side by side with a dark patch.

    Returns the canvas, each tile's pixel rect (row 0 at the top), the tiles'
    sizes and a NAME derived from the pixels, so two registers reading the
    same price at the same size share one image.
    """
    def px(size_m, texel):
        return (max(4, int(round(size_m[0] * texel))),
                max(4, int(round(size_m[1] * texel))))

    sw, sh = px(L["window"]["size_m"], TEXEL)
    text, scale = digits_layout(_price_forms(price), sw, sh)
    screen = paint_screen(text, scale, sw, sh)
    ow, oh = px(L["op_panel"]["size_m"], TEXEL)
    # THE TWO DISPLAYS READ THE SAME NUMBER. `digits_layout` may have dropped
    # a leading digit to keep the pole's type at scale 2, and a pole saying
    # 4.99 over a panel saying 24.99 is a defect a player can see.
    lcd, lcd_lines = paint_lcd(text, ow, oh)
    kw, kh = px(L["keypad_art"]["size_m"], KEY_TEXEL)
    keys = paint_keys(kw, kh)

    # STACKED, NOT SIDE BY SIDE. The screen is wide and short and the keypad
    # tall and narrow; beside each other they leave 84 x 133 px of filler and
    # the atlas decodes at 91 KiB, stacked at 37.
    gut = 2
    W = max(sw, ow, kw, 4)
    H = sh + gut + oh + gut + kh
    canvas = Canvas(W, H, (10, 10, 12))
    canvas.paste(screen, 0, 0)
    rects = {"screen": (0, 0, sw, sh)}
    y = sh + gut
    canvas.paste(lcd, 0, y)
    rects["lcd"] = (0, y, ow, y + oh)
    y += oh + gut
    canvas.paste(keys, 0, y)
    rects["keys"] = (0, y, kw, y + kh)
    rects["dark"] = (W - 4, H - 4, W, H)
    digest = zlib.crc32(bytes(canvas.buf)) & 0xFFFFFFFF
    # the digits' height on the real display, which is the number the walker's
    # question ("does it read?") is actually about
    digit_m = len(pt.trim(pt.render(text, scale))) / float(TEXEL)
    return {"canvas": canvas, "rects": rects, "size": (W, H),
            "price": price, "text": text, "scale": scale,
            "digit_h_m": round(digit_m, 5), "lcd_lines": lcd_lines,
            "name": f"register_{W}x{H}_{digest:08x}"}


def _price_forms(price):
    """The display's candidates, longest first: the price, and the price with
    its leading digit dropped where that leaves a sane number. The narrow
    corner of the genome sets four characters at scale 2 and five at scale 1,
    and half-height digits to keep a leading digit is the wrong trade."""
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

_UV = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))


def _box(part, mat, b):
    x0, x1, y0, y1, z0, z1 = b
    return P.box(part, mat, (x0, y0, z0), (x1, y1, z1))


def _top_art(cx, cy, w, d, z):
    """The four corners of a face-up art quad, wound and ordered SO THE CLERK
    CAN READ IT.

    The operator stands at +Y and looks along -Y, so what is "up" in the
    image is the -Y edge and what is "right" is -X -- their right hand, the
    same frame the keypad's lanes are laid out in. `_UV` maps vertex 0 to the
    tile's bottom-left, so vertex 0 is the (+X, +Y) corner.

    MEASURED, not reasoned: the first draft wound this from (-X, -Y) with the
    same UVs and `_preview_register/operator.png` came back with TOTAL 24.99
    set upside down and mirrored -- a 180 degree rotation, which is what
    getting BOTH axes backwards looks like. Nothing else in the module would
    have said so.
    """
    return [(cx + w / 2.0, cy + d / 2.0, z), (cx - w / 2.0, cy + d / 2.0, z),
            (cx - w / 2.0, cy - d / 2.0, z), (cx + w / 2.0, cy - d / 2.0, z)]


def _quad(part, tile, verts, lit=False):
    p = P.mesh(part, ART, verts, [(0, 1, 2, 3)])
    p["tile"] = tile
    p["uvs"] = [_UV]
    if lit:
        p["lit"] = True
    return p


def plan(w, d, h, params=None, variant=0, price=None, key=""):
    """The whole register: ``{"prims", "tiles", "collision", "attachments",
    "facts"}``. ``prims`` carries the solids and the three art quads; a quad
    names its tile in ``tiles`` and the customer screen alone carries
    ``lit``."""
    params = params or {}
    L = layout(w, d, h)
    price = price if price in PRICES else PRICES[int(variant) % len(PRICES)]
    A = art(L, price, key)
    prims = []

    prims.append(_box("Register_Drawer", CASE, L["drawer"]))
    prims.append(_box("Register_Pull", TRIM, L["pull"]))
    lk = L["lock"]
    prims.append(P.lay_along_y(
        P.cyl("Register_Lock", LOCK, (lk["x"], -lk["z"]), lk["r"],
              lk["y"][0], lk["y"][1], segments=LOCK_SEGMENTS)))
    prims.append(_box("Register_Body", CASE, L["body"]))
    prims.append(_box("Register_Keypad", TRIM, L["keypad"]))
    prims.append(_box("Register_Printer", TRIM, L["printer"]))

    pa = L["paper"]
    paper = P.box_c("Register_Paper", PAPER,
                    (pa["x"], pa["hinge"][0], pa["hinge"][1] + pa["h"] / 2.0),
                    (pa["w"], pa["t"], pa["h"]))
    # the roll leans toward the clerk; the hinge is the printer's mouth, so
    # the lean pivots about the slot rather than about the paper's middle
    prims.append(P.rotate_x(paper, -pa["lean"], about=pa["hinge"]))

    op = L["op_panel"]
    ox0, ox1 = op["x"]
    oy0, oy1 = op["y"]
    bez = P.box("Register_OpBezel", TRIM, (ox0, oy0, op["hinge"][1] - 0.006),
                (ox1, oy1, op["hinge"][1] + op["t"]))
    prims.append(P.rotate_x(bez, -op["tilt"], about=op["hinge"]))
    ow_m, od_m = op["size_m"]
    ocx, ocy = (ox0 + ox1) / 2.0, (oy0 + oy1) / 2.0
    oz = op["hinge"][1] + op["t"] + ART_PROUD
    lcd = _quad("Register_OpLcd", "lcd", _top_art(ocx, ocy, ow_m, od_m, oz))
    prims.append(P.rotate_x(lcd, -op["tilt"], about=op["hinge"]))

    ka = L["keypad_art"]
    prims.append(_quad("Register_Keys", "keys", _top_art(
        (ka["x"][0] + ka["x"][1]) / 2.0, (ka["y"][0] + ka["y"][1]) / 2.0,
        ka["x"][1] - ka["x"][0], ka["y"][1] - ka["y"][0], ka["z"])))

    prims.append(_box("Register_Stem", TRIM, L["stem"]))
    prims.append(_box("Register_Bezel", TRIM, L["bezel"]))
    win = L["window"]
    # THE LIT FACE LOOKS AT THE CUSTOMER (-Y), and the winding is what
    # decides that: ascending X gives a -Y normal, descending X gives +Y and
    # a display only the bezel can read. The first draft had it descending;
    # `test_the_screen_faces_the_customer` is the measurement, because a
    # backfacing quad renders as nothing and nothing else says why.
    prims.append(_quad("Register_Screen", "screen",
                       [(win["x"][0], win["y"], win["z"][0]),
                        (win["x"][1], win["y"], win["z"][0]),
                        (win["x"][1], win["y"], win["z"][1]),
                        (win["x"][0], win["y"], win["z"][1])], lit=True))

    collision = [((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, h / 2.0))]
    facts = {"tris": P.tri_count(prims), "budget": TRI_BUDGET,
             "price": price, "digits": A["text"], "digit_scale": A["scale"],
             "digit_h_m": A["digit_h_m"], "lcd_lines": A["lcd_lines"],
             "art": A["name"], "art_px": A["size"],
             "screen_m": tuple(round(v, 4) for v in L["window"]["size_m"]),
             "bands_m": tuple(round(v, 4) for v in L["bands"])}
    return {"prims": prims, "art": A, "collision": collision,
            "attachments": {
                "ATT_screen_center": (0.0, win["y"],
                                      (win["z"][0] + win["z"][1]) / 2.0),
                "ATT_keypad_center": ((ka["x"][0] + ka["x"][1]) / 2.0,
                                      (ka["y"][0] + ka["y"][1]) / 2.0,
                                      ka["z"])},
            "facts": facts}


def triangles(got):
    """What the recipe emits, before bevel -- and nothing here asks for one."""
    return P.tri_count(got["prims"])


def extents(got):
    """(lo, hi) over every primitive, in the module frame."""
    return P.bounds(got["prims"])


def uv(rect, size):
    """A tile's pixel rect -> (u0, v0, u1, v1), v up."""
    return uv_rect(rect, size)
