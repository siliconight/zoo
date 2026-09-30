"""Wall posters in four families, painted in pure Python.

Zoo 1.30.0. The walker, 2026-09-29: posters to "appropriately fill out
certain walls" -- strip club interiors, bar interiors, exterior alley walls
and poles, store windows and walls -- with three guides in the root repo's
`docs/reference/` (`POSTER_GUIDES.md` indexes them). Measured against those
guides the card shop's posters failed five checks of seven: one composition
for every poster, identical neighbours, titles unreadable at 5 m, no print
character, one texture per poster. This module is the art half of the
answer; `poster_wall_forms` is the placement half and `poster_checks` the
three tests.

A FAMILY IS A LAYOUT RULE, NOT A PALETTE SWAP (the system guide: "Create 3-6
families first ... each should have rules a procedural system can vary
without losing its identity"). Every family fixes its hierarchy -- what is
read first, second, third -- and lets the seed choose only among approved
options:

  club   brash faux glamour: a dark airbrushed ground, a gold rule round it,
         the promise across the top, ONE glamour motif on a star burst,
         the deflating line and the club's name at the foot;
  bar    a photocopied gig bill: one black ink on copy paper, the band name
         reversed out of a black bar, a crude 1-bit image, the date;
  alley  a handbill: one black ink on day-glo paper, a hand-lettered
         headline, the pitch, tear-off tabs, tape at the corners;
  store  a day-glo sale poster: the deal in red across the top, a red
         star burst shouting SALE / NOW / HOT, the fine print below.

ONE FLAW, WITH A CAUSE (the art guide, "purposeful imperfection"; the system
guide, "a single strong fold, sun-faded band, or offset color pass often
reads better than uniform grunge"): the club's gold is printed one pixel off
its dark rule (a cheap second pass); the bar's copier leaves toner specks and
a drum streak; the handbill was folded into a pocket; the store poster's top
is sun-faded from the window. Nowhere is there noise without a reason.

THE TYPE IS CHUNKY ON PURPOSE. At `card_art.TEXEL` (256 px/m) Pixel
Operator Bold's capitals are 11 px, 4.3 cm on the wall; the narrow `m5x7`
face at scale 2 fits eight characters across a 0.45 m poster at 14 px, 5.5
cm, which is what "readable at play distance" asks of a headline.
`poster_checks` measures it rather than asserting it.

Every painter returns ``(canvas, info)``: ``info`` names the headline's and
the focal image's pixel rects and inks, which is what the checks measure.
"""
from __future__ import annotations

import math

from . import club_names as CN
from . import pixel_type as pt
from . import poster_copy as PC
from .card_art import Roll, _ellipse
from .vending_forms import Canvas

HEAD_FACE = "m5x7"
SMALL_FACE = "small"
INK = (22, 20, 22)


def _mix(a, b, t):
    return tuple(int(round(a[k] + (b[k] - a[k]) * t)) for k in range(3))


def fit_text(c, text, box, rgb, face=HEAD_FACE, cap=6, shadow=None, outline=None):
    """Set ``text`` as large as it fits ``box`` -- wrapping at word breaks
    before shrinking below the largest scale that fits -- centred. Returns
    the rect of the ink, or None when not even scale 1 fits (nothing is
    painted: a smear is worse than a gap)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    bw, bh = x1 - x0, y1 - y0
    if bw <= 0 or bh <= 0:
        return None
    for s in range(cap, 0, -1):
        lines = pt.wrap(text, bw - (2 if outline else 0), s, face)
        if not lines:
            continue
        masks = [pt.trim(pt.render(ln, s, face)) for ln in lines]
        gap = max(1, s)
        th = sum(len(m) for m in masks) + gap * (len(masks) - 1)
        if th > bh - (2 if outline else 0) or max(len(m[0]) for m in masks) > bw:
            continue
        y = y0 + (bh - th) // 2
        rx0, rx1 = x1, x0
        for m in masks:
            x = x0 + (bw - len(m[0])) // 2
            if outline:
                c.mask(m, x, y, outline, grow=1)
            if shadow:
                c.mask(m, x + 1, y + 1, shadow)
            c.mask(m, x, y, rgb)
            rx0, rx1 = min(rx0, x), max(rx1, x + len(m[0]))
            y += len(m) + gap
        return (rx0, y0 + (bh - th) // 2, rx1, y0 + (bh - th) // 2 + th)
    return None


def drawn(c, before):
    """The pixel box of everything that changed since ``before`` (a copy of
    ``c.buf``): the focal image as INKED, not the box it was asked to fill.
    The first cut measured a bar bill's guitar against its whole box, mostly
    paper, and read it as a 24-point step off the paper round it."""
    w = c.w
    xs, ys = [], []
    for i in range(0, len(c.buf), 3):
        if c.buf[i:i + 3] != before[i:i + 3]:
            j = i // 3
            xs.append(j % w)
            ys.append(j // w)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


def _burst(c, cx, cy, r_out, r_in, spikes, rgb, phase=0.0):
    """A star burst: ``spikes`` points between ``r_in`` and ``r_out``."""
    for y in range(int(cy - r_out), int(cy + r_out) + 1):
        for x in range(int(cx - r_out), int(cx + r_out) + 1):
            dx, dy = x - cx, y - cy
            r = math.hypot(dx, dy)
            if r > r_out:
                continue
            a = (math.atan2(dy, dx) + phase) * spikes / (2.0 * math.pi)
            f = abs((a - math.floor(a)) - 0.5) * 2.0       # 1 at a spike, 0 between
            if r <= r_in + (r_out - r_in) * f:
                c.px(x, y, rgb)


# --- the glamour motifs (club) -------------------------------------------------------

def _martini(c, cx, cy, s, rgb, olive):
    for k in range(int(s)):                                   # the bowl, a V
        c.rect(cx - s + k, cy - s + k, cx + s - k, cy - s + k + 1, rgb)
    c.rect(cx - 1, cy, cx + 1, cy + s, rgb)                    # the stem
    c.rect(cx - s // 2, cy + s, cx + s // 2 + 1, cy + s + 2, rgb)
    _ellipse(c, cx + s // 3, cy - s + s // 3, max(1, s // 5), max(1, s // 5), olive)


def _heel(c, cx, cy, s, rgb, _hot):
    c.rect(cx - s, cy + s // 2, cx + s // 3, cy + s // 2 + 3, rgb)       # the sole
    for k in range(s):                                                   # the arch
        c.rect(cx - s + k, cy - k // 2, cx - s + k + 1, cy + s // 2, rgb)
    c.rect(cx + s // 3 - 2, cy + s // 2, cx + s // 3, cy + s + 2, rgb)  # the heel
    c.rect(cx - s, cy - s // 2, cx - s + 3, cy + s // 2, rgb)            # the toe box


def _lips(c, cx, cy, s, rgb, dark):
    _ellipse(c, cx - s // 2, cy, s // 2 + 1, s // 3 + 1, rgb)
    _ellipse(c, cx + s // 2, cy, s // 2 + 1, s // 3 + 1, rgb)
    _ellipse(c, cx, cy + s // 4, s, s // 3 + 1, rgb)
    c.rect(cx - s + 2, cy + s // 6, cx + s - 1, cy + s // 6 + 1, dark)


def _pole(c, cx, cy, s, rgb, hot):
    c.rect(cx - 1, cy - s - s // 2, cx + 1, cy + s + s // 2, rgb)
    for dx, dy in ((-s // 2, -s // 2), (s // 2, -s // 3), (-s // 3, s // 2), (s // 2, s // 2)):
        c.rect(cx + dx - 1, cy + dy, cx + dx + 2, cy + dy + 1, hot)
        c.rect(cx + dx, cy + dy - 1, cx + dx + 1, cy + dy + 2, hot)


GLAMOUR = (_martini, _heel, _lips, _pole)

CLUB_PALETTES = (   # (ground top, ground foot, rule, headline)
    ((70, 16, 96), (10, 4, 16), (226, 184, 64), (255, 96, 180)),
    ((120, 8, 30), (14, 2, 6), (226, 184, 64), (255, 214, 90)),
    ((16, 30, 110), (4, 6, 22), (226, 184, 64), (120, 230, 255)),
)


def club(w, h, row, key):
    roll = Roll(f"club|{row}|{key}")
    top, foot, gold, hot = CLUB_PALETTES[roll.below(len(CLUB_PALETTES))]
    c = Canvas(w, h, foot)
    for y in range(h):                                  # the airbrushed ground
        c.rect(0, y, w, y + 1, _mix(top, foot, y / max(1, h - 1)))
    # THE FLAW: the gold rule printed a pixel off the dark one (a second pass)
    c.rect(1, 1, w - 1, 3, (40, 26, 8))
    c.rect(1, h - 3, w - 1, h - 1, (40, 26, 8))
    c.rect(1, 1, 3, h - 1, (40, 26, 8))
    c.rect(w - 3, 1, w - 1, h - 1, (40, 26, 8))
    for (a, b, cc, d) in ((2, 2, w - 2, 3), (2, h - 3, w - 2, h - 2), (2, 2, 3, h - 2), (w - 3, 2, w - 2, h - 2)):
        c.rect(a + 1, b + 1, cc + 1, d + 1, gold)
    head, small = PC.CLUB[row % len(PC.CLUB)]
    # NO OUTLINE, measured: a black outline round light letters made the title
    # WORSE at 5 m (3.0 -> 2.2:1, `poster_checks`) -- the thumbnail's box
    # filter mixes a thin light stroke with its dark ring into one mid tone
    # HEAVY, in its own colour: the thin face's two-pixel strokes are under one
    # screen pixel at 5 m, and NO COVER TIL 9 read 2.6:1 there; each letter is
    # drawn a pixel fatter in the headline's own ink
    title = fit_text(c, head, (5, 5, w - 5, int(h * 0.30)), hot, shadow=(0, 0, 0), outline=hot)
    fy0, fy1 = int(h * 0.32), int(h * 0.72)
    cx, cy = w // 2, (fy0 + fy1) // 2
    r = min(w, fy1 - fy0) // 2 - 1
    # the burst well above the ground: at 0.22 of the way to white the focal
    # step measured 29-41 against 42.5 and the blurred poster was one dark
    # field (`poster_checks`, 2026-09-30)
    _burst(c, cx, cy, r, int(r * 0.55), 12, _mix(top, (255, 255, 255), 0.62), phase=roll.below(100) / 16.0)
    motif = GLAMOUR[roll.below(len(GLAMOUR))]
    motif(c, cx, cy, max(6, r // 2), gold, hot)
    small_at = fit_text(c, small, (5, int(h * 0.74), w - 5, int(h * 0.88)), (236, 232, 240), face=SMALL_FACE, cap=2)
    fit_text(c, CN.name_for(roll.below(len(CN.NAMES))), (5, int(h * 0.88), w - 5, h - 4), gold,
             face=SMALL_FACE, cap=1)
    return c, {"family": "club", "headline": head, "small": small, "small_at": small_at,
               "title": title, "focal": (cx - r, cy - r, cx + r, cy + r),
               "ground": _mix(top, foot, cy / max(1, h - 1))}


# --- the crude 1-bit images (bar) -----------------------------------------------------

def _skull(c, cx, cy, s, ink, paper):
    _ellipse(c, cx, cy - s // 4, s, s - s // 4, ink)
    c.rect(cx - s // 2, cy + s // 3, cx + s // 2 + 1, cy + s, ink)
    _ellipse(c, cx - s // 2 + 1, cy - s // 5, s // 4 + 1, s // 4 + 1, paper)
    _ellipse(c, cx + s // 2 - 1, cy - s // 5, s // 4 + 1, s // 4 + 1, paper)
    for k in range(-s // 2 + 2, s // 2, 3):
        c.rect(cx + k, cy + s // 2, cx + k + 1, cy + s - 1, paper)


def _guitar(c, cx, cy, s, ink, paper):
    # chunky: a thin-necked first cut was mostly paper inside its own box and
    # barely separated from it (`poster_checks`: 38 against 42.5)
    _ellipse(c, cx - s // 3, cy + s // 3, s * 2 // 3 + 1, s * 2 // 3, ink)
    _ellipse(c, cx + s // 5, cy - s // 10, s // 2, s // 2 - 1, ink)
    _ellipse(c, cx - s // 6, cy + s // 6, s // 6 + 1, s // 6 + 1, paper)
    for k in range(s + s // 2):
        c.rect(cx + s // 5 + k // 2 - 1, cy - s // 10 - k, cx + s // 5 + k // 2 + 3, cy - s // 10 - k + 1, ink)


def _speakers(c, cx, cy, s, ink, paper):
    for dx in (-s // 2 - 1, s // 2 + 1):
        c.rect(cx + dx - s // 2, cy - s, cx + dx + s // 2, cy + s, ink)
        _ellipse(c, cx + dx, cy - s // 2, s // 4 + 1, s // 4 + 1, paper)
        _ellipse(c, cx + dx, cy + s // 3, s // 3 + 1, s // 3 + 1, paper)
        _ellipse(c, cx + dx, cy + s // 3, s // 6, s // 6, ink)


CRUDE = (_skull, _guitar, _speakers)
COPY_PAPER = ((236, 232, 220), (250, 214, 226), (252, 246, 176), (206, 228, 246))


def bar(w, h, row, key):
    roll = Roll(f"bar|{row}|{key}")
    paper = COPY_PAPER[roll.below(len(COPY_PAPER))]
    c = Canvas(w, h, paper)
    head, small = PC.BAR[row % len(PC.BAR)]
    band_h = int(h * 0.24)
    c.rect(3, 3, w - 3, 3 + band_h, INK)                  # the band name, reversed out
    title = fit_text(c, head, (5, 4, w - 5, 2 + band_h), paper)
    fy0, fy1 = 6 + band_h, int(h * 0.60)
    cx, cy = w // 2, (fy0 + fy1) // 2
    s = max(6, min(w // 3, (fy1 - fy0) // 2) - 1)
    before = bytes(c.buf)
    CRUDE[roll.below(len(CRUDE))](c, cx, cy, s, INK, paper)
    focal = drawn(c, before)
    fit_text(c, PC.DATES[roll.below(len(PC.DATES))], (4, int(h * 0.61), w - 4, int(h * 0.70)), INK, cap=2)
    # the punchline in the narrow face: at 0.30 m a sheet is 77 px, and the
    # first cut's `small` face could not set one of the twelve lines at all
    small_at = fit_text(c, small, (3, int(h * 0.71), w - 3, h - 3), INK, face="m5x7", cap=1)
    # THE FLAW: the copier -- toner specks in the margins and one drum streak,
    # below the band name (the guides: protect the focal title from the wear)
    sx = roll.between(4, w - 5)
    for y in range(band_h + 5, h - 3):
        if (y + sx) % 3:
            c.px(sx, y, _mix(paper, INK, 0.35))
    for _k in range(max(6, (w * h) // 400)):
        c.px(roll.below(w), roll.below(h), INK)
    return c, {"family": "bar", "headline": head, "small": small, "small_at": small_at,
               "title": title, "focal": focal, "ground": paper}


DAYGLO = ((255, 110, 180), (255, 240, 90), (140, 240, 110), (255, 170, 60), (244, 244, 236))


# --- the handbill's one picture (alley), chosen by what the bill is about ---------------

def _cat(c, cx, cy, s, ink, paper):
    _ellipse(c, cx, cy + s // 5, s, s - s // 4, ink)
    for sx in (-1, 1):
        for k in range(s // 2 + 1):
            c.rect(cx + sx * (s // 2) - k // 2, cy - s + k, cx + sx * (s // 2) + k // 2 + 1, cy - s + k + 1, ink)
        _ellipse(c, cx + sx * (s // 3), cy, max(1, s // 5), max(1, s // 5), paper)


def _house(c, cx, cy, s, ink, paper):
    for k in range(s):
        c.rect(cx - k, cy - s + k, cx + k + 1, cy - s + k + 1, ink)
    c.rect(cx - s + 2, cy, cx + s - 1, cy + s, ink)
    c.rect(cx - s // 4, cy + s // 3, cx + s // 4 + 1, cy + s, paper)


def _wheels(c, cx, cy, s, ink, paper):
    for dx in (-s // 2 - 1, s // 2 + 1):
        _ellipse(c, cx + dx, cy + s // 4, s // 2 + 1, s // 2 + 1, ink)
        _ellipse(c, cx + dx, cy + s // 4, s // 4, s // 4, paper)
    c.rect(cx - s // 2, cy - s // 4, cx + s // 2 + 1, cy - s // 4 + 2, ink)


def _star(c, cx, cy, s, ink, _paper):
    _burst(c, cx, cy, s, s // 2, 5, ink, phase=-0.3)


def _drop(c, cx, cy, s, ink, _paper):
    _ellipse(c, cx, cy + s // 3, s * 2 // 3 + 1, s * 2 // 3, ink)
    for k in range(s):
        c.rect(cx - k * 2 // 3, cy - s + k, cx + k * 2 // 3 + 1, cy - s + k + 1, ink)


def _key(c, cx, cy, s, ink, paper):
    _ellipse(c, cx - s // 2, cy, s // 2 + 1, s // 2 + 1, ink)
    _ellipse(c, cx - s // 2, cy, s // 5, s // 5, paper)
    c.rect(cx - s // 3, cy - 1, cx + s, cy + 2, ink)
    for k in (s // 3, 2 * s // 3):
        c.rect(cx + k, cy + 2, cx + k + 2, cy + s // 3 + 2, ink)


def _dollar(c, cx, cy, s, ink, _paper):
    fit_text(c, "$", (cx - s, cy - s, cx + s, cy + s), ink, face="bold", cap=4)


ALLEY_ICONS = {"cat": _cat, "house": _house, "guitar": _guitar, "wheels": _wheels,
               "star": _star, "drop": _drop, "key": _key, "dollar": _dollar}
#: Which picture a bill carries -- reviewed here, not drawn by a seed.
ALLEY_ICON_OF = {
    "LOST CAT": "cat", "ROOM 4 RENT": "house", "GUITAR LESSONS": "guitar",
    "WE BUY GOLD": "dollar", "SEEN MY BIKE?": "wheels", "BLOCK PARTY SAT": "star",
    "PAINTER NEEDED": "house", "BASEMENT DOJO": "star", "YARD SALE": "dollar",
    "CAR WASH SAT": "drop", "GARAGE BAND": "guitar", "FOUND: KEYS": "key",
}


def alley(w, h, row, key):
    roll = Roll(f"alley|{row}|{key}")
    paper = DAYGLO[roll.below(len(DAYGLO))]
    c = Canvas(w, h, paper)
    head, small = PC.ALLEY[row % len(PC.ALLEY)]
    # THE FLAW FIRST: it was folded into somebody's pocket after it was
    # printed, so the crease runs under the ink, not through it
    fy = h // 2
    c.rect(0, fy, w, fy + 1, _mix(paper, (255, 255, 255), 0.45))
    c.rect(0, fy + 1, w, fy + 2, _mix(paper, (0, 0, 0), 0.12))
    # ONE STRONG DARK MASS: the headline reversed out of a black band. The
    # first two cuts were black type on day-glo, and blurred they were an
    # even field (`poster_checks`: 39-79 against 85) -- the art guide's "fix
    # the composition before adding detail". The paper, the tabs and the tape
    # still tell it from a gig bill.
    band = int(h * 0.26)
    c.rect(2, 6, w - 2, 6 + band, INK)
    title = fit_text(c, head, (4, 7, w - 4, 5 + band), paper, face="bold", cap=3)
    iy0, iy1 = 8 + band, int(h * 0.49)
    icx, icy = w // 2, (iy0 + iy1) // 2
    isz = max(5, min(w - 6, iy1 - iy0) // 2 - 1)
    before = bytes(c.buf)
    ALLEY_ICONS[ALLEY_ICON_OF[head]](c, icx, icy, isz, INK, paper)
    focal = drawn(c, before)
    small_at = fit_text(c, small, (3, int(h * 0.50), w - 3, int(h * 0.73)), INK, face="m5x7", cap=1)
    # tear-off tabs across the foot, one already taken
    ty0 = int(h * 0.74)
    n = max(4, w // 8)
    tw = w / float(n)
    gone = roll.below(n)
    for k in range(n):
        x0 = int(k * tw)
        if k == gone:
            c.rect(x0 + 1, ty0 + 2, int((k + 1) * tw), h, _mix(paper, (0, 0, 0), 0.55))
            continue
        c.rect(x0, ty0, x0 + 1, h, _mix(paper, INK, 0.5))          # the cut
        for y in range(ty0 + 3, h - 2, 2):                          # the number, too small to read
            c.rect(x0 + 2, y, int((k + 1) * tw) - 2, y + 1, _mix(paper, INK, 0.7))
    c.rect(0, ty0, w, ty0 + 1, _mix(paper, INK, 0.5))
    # tape at the top corners
    for x in (2, w - 10):
        c.rect(x, 0, x + 8, 5, (226, 224, 206))
    return c, {"family": "alley", "headline": head, "small": small, "small_at": small_at,
               "title": title, "focal": focal, "ground": paper}


#: (paper, headline ink). Red on orange measured 1.6:1 at 5 m
#: (`poster_checks`, 2026-09-30): the orange sheet's deal is in navy.
STORE_PAPER = (((255, 236, 60), (214, 22, 30)), ((255, 132, 40), (20, 24, 110)),
               ((130, 250, 100), (214, 22, 30)), ((250, 250, 244), (214, 22, 30)))
SHOUT = ("SALE", "NOW", "HOT", "WOW")


def store(w, h, row, key):
    roll = Roll(f"store|{row}|{key}")
    paper, head_ink = STORE_PAPER[roll.below(len(STORE_PAPER))]
    red = (214, 22, 30)
    c = Canvas(w, h, paper)
    head, small = PC.STORE[row % len(PC.STORE)]
    # no white outline: at 5 m it averaged into the letters and a long deal
    # (SCRATCH & WIN) read 2.0:1 (`poster_checks`)
    title = fit_text(c, head, (3, 3, w - 3, int(h * 0.34)), head_ink, outline=_mix(head_ink, (0, 0, 0), 0.5))
    fy0, fy1 = int(h * 0.36), int(h * 0.78)
    cx, cy = w // 2, (fy0 + fy1) // 2
    r = min(w, fy1 - fy0) // 2 - 1
    _burst(c, cx, cy, r, int(r * 0.72), 14, (190, 16, 24), phase=roll.below(100) / 20.0)
    fit_text(c, SHOUT[roll.below(len(SHOUT))], (cx - int(r * 0.58), cy - int(r * 0.4),
                                                 cx + int(r * 0.58), cy + int(r * 0.4)), (255, 244, 120))
    # the fine print on a white strip: the orange sheet is a MID-value paper
    # (luma 151), and with only a dark burst on it the blurred poster spanned
    # 70 of the 85 a value group asks (`poster_checks`); a light mass at the
    # foot gives every sheet both ends
    c.rect(2, int(h * 0.80), w - 2, h - 2, (252, 252, 246))
    small_at = fit_text(c, small, (4, int(h * 0.80) + 1, w - 4, h - 3), INK, face=SMALL_FACE, cap=1)
    # THE FLAW: the window's sun has faded the top third
    fade = int(h * 0.30)
    for y in range(fade):
        t = 0.32 * (1.0 - y / float(fade))
        for x in range(w):
            c.px(x, y, _mix(c.get(x, y), (255, 255, 255), t))
    return c, {"family": "store", "headline": head, "small": small, "small_at": small_at,
               "title": title, "focal": (cx - r, cy - r, cx + r, cy + r), "ground": paper}


PAINTERS = {"club": club, "bar": bar, "alley": alley, "store": store}

#: Each family's sheet, width x height in metres: a club one-sheet, an
#: 11 x 17 gig bill, a letter-size handbill, a sale poster -- the system
#: guide's "ordinary wall poster" band is 0.45-0.75 m tall; a handbill is
#: smaller because a handbill is -- but not letter size: at 0.22 m a sheet
#: was 56 px wide and set its pitch on one handbill in twelve.
SIZES_M = {"club": (0.46, 0.64), "bar": (0.30, 0.44), "alley": (0.30, 0.42), "store": (0.46, 0.60)}


def paint(family, w_px, h_px, row, key=""):
    if family not in PAINTERS:
        raise ValueError(f"no poster family {family!r}; the families are {', '.join(PC.FAMILIES)}")
    return PAINTERS[family](int(w_px), int(h_px), int(row), str(key))
