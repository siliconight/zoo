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


def fit_text(c, text, box, rgb, face=HEAD_FACE, cap=6, shadow=None, outline=None, fallback=None,
             bold=False):
    """Set ``text`` as large as it fits ``box`` -- wrapping at word breaks
    before shrinking below the largest scale that fits -- centred. Returns
    the rect of the ink, or None when not even scale 1 fits (nothing is
    painted: a smear is worse than a gap). ``fallback`` is a narrower face
    tried when ``face`` fits nowhere."""
    x0, y0, x1, y1 = [int(v) for v in box]
    bw, bh = x1 - x0, y1 - y0
    if bw <= 0 or bh <= 0:
        return None
    got = _fit_face(c, text, x0, y0, x1, y1, rgb, face, cap, shadow, outline, bold)
    if got is None and fallback:
        got = _fit_face(c, text, x0, y0, x1, y1, rgb, fallback, cap, shadow, outline, bold)
    return got


def _fit_face(c, text, x0, y0, x1, y1, rgb, face, cap, shadow, outline, bold=False):
    bw, bh = x1 - x0, y1 - y0
    for s in range(cap, 0, -1):
        lines = pt.wrap(text, bw - (2 if outline else 0), s, face)
        if not lines:
            continue
        masks = [pt.trim(pt.render(ln, s, face)) for ln in lines]
        gap = max(1, s)
        th = sum(len(m) for m in masks) + gap * (len(masks) - 1)
        if th > bh - (2 if outline else 0) or max(len(m[0]) + (1 if bold else 0) for m in masks) > bw:
            continue
        y = y0 + (bh - th) // 2
        rx0, rx1 = x1, x0
        for m in masks:
            x = x0 + (bw - len(m[0])) // 2
            if outline:
                c.mask(m, x, y, outline, grow=1)
            if shadow:
                c.mask(m, x + 1, y + 1, shadow)
            if bold:                         # sideways only: the counters stay open
                c.mask(m, x + 1, y, rgb)
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


# --- the drink (club) -------------------------------------------------------------

def _martini(c, cx, cy, s, rgb, olive):
    for k in range(int(s)):                                   # the bowl, a V
        c.rect(cx - s + k, cy - s + k, cx + s - k, cy - s + k + 1, rgb)
    c.rect(cx - 1, cy, cx + 1, cy + s, rgb)                    # the stem
    c.rect(cx - s // 2, cy + s, cx + s // 2 + 1, cy + s + 2, rgb)
    _ellipse(c, cx + s // 3, cy - s + s // 3, max(1, s // 5), max(1, s // 5), olive)


#: (ground top, ground foot, rule, headline). MORE COLOUR (the walker,
#: 2026-09-30, toward Duke Nukem 3D) -- and a measured lesson: saturated
#: colour is not light value. Tops pushed to full saturation measured only
#: ~77 luma, barely moved the blur test, and cut the stepped titles' contrast.
#: The grounds are rich and moderate; the light mass is the spotlight's pool.
CLUB_PALETTES = (
    ((128, 28, 118), (14, 4, 20), (236, 192, 70), (255, 226, 110)),
    ((166, 30, 34), (18, 2, 8), (236, 192, 70), (255, 236, 150)),
    ((30, 66, 176), (4, 8, 26), (236, 192, 70), (140, 240, 255)),
)


def _spotlight(c, sx, sy, tx, ty, spread, strength=0.62, lamp=(5, 3)):
    """A light cone from (sx, sy) onto (tx, ty): the eye path from the top of
    the sheet to the performer (the feedback's "a spotlight can point to the
    performer and event title")."""
    # the lamp itself: a white glare where the beam starts
    _ellipse(c, sx, sy, lamp[0], lamp[1], (255, 244, 214))
    _ellipse(c, sx, sy, max(1, lamp[0] // 2), max(1, lamp[1] // 2), (255, 255, 255))
    ang = math.atan2(ty - sy, tx - sx)
    reach = math.hypot(tx - sx, ty - sy) * 1.12
    for y in range(c.h):
        for x in range(c.w):
            dx, dy = x - sx, y - sy
            d = math.hypot(dx, dy)
            if d == 0 or d > reach:
                continue
            a = abs((math.atan2(dy, dx) - ang + math.pi) % (2 * math.pi) - math.pi)
            if a < spread:
                c.px(x, y, _mix(c.get(x, y), (255, 236, 190), strength * (1.0 - a / spread)))


def _marquee(c, box, hot):
    """A lit marquee: a cream panel ringed with bulbs, the headline in dark
    ink on it. The poster's WHITE mass (the walker, 2026-09-30: "using whites
    and blacks for depth is essential") -- a centred club sheet with only a
    lit figure and pool on a dark ground blurred to 66-80 under
    `poster_checks`, one value group short. Returns the panel's inner box."""
    x0, y0, x1, y1 = box
    c.rect(x0, y0, x1, y1, (40, 10, 30))
    c.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, (250, 236, 200))
    for x in range(x0 + 2, x1 - 1, 4):                  # the bulbs, top and bottom
        for y in (y0 + 1, y1 - 3):
            c.rect(x, y, x + 2, y + 2, hot if (x // 4) % 2 else (255, 255, 255))
    for y in range(y0 + 5, y1 - 4, 4):                  # and down the sides
        for x in (x0 + 1, x1 - 3):
            c.rect(x, y, x + 2, y + 2, hot if (y // 4) % 2 else (255, 255, 255))
    return (x0 + 4, y0 + 4, x1 - 4, y1 - 4)


def _stage(c, cx, y, rx, ry, top_rgb, edge_rgb):
    """The stage, and the pool of light the spotlight throws on it: the
    poster's light mass has a cause (a dark club poster with only a lit
    figure blurred to one dark field under `poster_checks`)."""
    _ellipse(c, cx, y, rx, ry, edge_rgb)
    _ellipse(c, cx, y - 1, max(1, rx - 2), max(1, ry - 1), top_rgb)
    _ellipse(c, cx, y - 1, max(1, rx * 3 // 4), max(1, ry * 3 // 4), (252, 236, 196))
    _ellipse(c, cx, y - 1, max(1, rx // 2), max(1, ry // 2), (255, 252, 240))


def _stepped_width(text, step, face, scale):
    w = 0
    for ch in text:
        w += 4 * scale if ch == " " else len(pt.trim(pt.render(ch, scale, face))[0]) + scale + 2
    return w


def stepped_title(c, text, box, step, rgb, shadow, face=HEAD_FACE, scales=(2, 1)):
    """A headline set as a descending diagonal inside ``box``: each line
    indented further than the last, at the largest scale whose lines all fit.
    The first cut never checked a width and ran NO COVER TIL 9 off the sheet.
    Returns the ink's rect, or None."""
    x0, y0, x1, y1 = box
    words = text.split()
    for scale in scales:
        for n in (1, 2, 3):
            if n > len(words):
                break
            per = -(-len(words) // n)
            lines = [" ".join(words[i:i + per]) for i in range(0, len(words), per)]
            lh = pt.line(face) * scale + 2
            indent = (x1 - x0) // 5
            ok = all(x0 + k * indent + _stepped_width(ln, step, face, scale) <= x1
                     for k, ln in enumerate(lines))
            if not ok or y0 + len(lines) * lh + step * max(len(ln) for ln in lines) > y1:
                continue
            rects = [_stepped(c, ln, x0 + k * indent, y0 + k * lh, step, rgb, shadow, face, scale)
                     for k, ln in enumerate(lines)]
            return (min(r[0] for r in rects), min(r[1] for r in rects),
                    max(r[2] for r in rects), max(r[3] for r in rects))
    return None


def _stepped(c, text, x, y, step, rgb, shadow, face=HEAD_FACE, scale=2):
    """Lettering that climbs down a pixel a letter: a diagonal the grid can
    draw with no antialiasing. No fattening: a grown G read as a B."""
    x0, y0, x1, y1 = x, y, x, y
    for ch in text:
        if ch == " ":
            x += 4 * scale
            y += step
            continue
        m = pt.trim(pt.render(ch, scale, face))
        c.mask(m, x + 1, y + 1, shadow)
        # bold sideways only: a second pass a pixel right thickens every
        # stroke and leaves a counter open (grown both ways, a G shut)
        c.mask(m, x + 1, y, rgb)
        c.mask(m, x, y, rgb)
        x1, y1 = max(x1, x + len(m[0]) + 1), max(y1, y + len(m))
        x += len(m[0]) + scale + 2
        y += step
    return (x0, y0, x1, y1)


def _club_rule(c, gold):
    """The gold rule, printed a pixel off its dark one (a cheap second pass),
    with one break where the foil cracked."""
    w, h = c.w, c.h
    dark = (40, 26, 8)
    for (a, b, cc, d) in ((1, 1, w - 1, 3), (1, h - 3, w - 1, h - 1), (1, 1, 3, h - 1), (w - 3, 1, w - 1, h - 1)):
        c.rect(a, b, cc, d, dark)
        c.rect(a + 1, b + 1, cc + 1, d + 1, gold)
    c.rect(w - 3, h // 3, w, h // 3 + 7, dark)


#: What a club poster SHOWS, chosen by what it says (the feedback: "give each
#: poster a specific focal image"); the performer unless the copy is a drink.
CLUB_FOCAL = {"BUBBLY ROOM": "cocktail", "HAPPY HOUR": "cocktail"}
CLUB_LAYOUTS = ("centred", "diagonal", "offcentre")
#: Which of `pixel_figure.POSES` a headline may show, by what it says (the
#: figure guide: "Who or what is this? What are they doing?"): the pole where
#: the copy is about the dancing, hands on hips where it is swagger, the hand
#: behind the head where it is the party. Two a row where both fit, so one
#: headline does not repeat one figure down a wall.
CLUB_POSES = {
    "VIP ROOM": ("akimbo", "behind_head"),
    "AMATEUR NIGHT": ("pole", "behind_head"),
    "LIVE ON STAGE": ("pole", "akimbo"),
    "WORLD FAMOUS": ("akimbo", "pole"),
    "NO COVER TIL 9": ("behind_head", "pole"),
    "BIRTHDAY BASH": ("behind_head", "akimbo"),
    "DOLLAR DANCES": ("pole",),
    "SHOW GIRLS": ("akimbo", "pole"),
    "GRAND OPENING": ("akimbo", "behind_head"),
    "CLASSY LADIES": ("behind_head", "akimbo"),
}
#: The club's display face (the typography guide: one per family). The
#: walker's pick, 2026-09-30, from all eight: monogram italic -- it leans,
#: and at scale 2 its caps are m5x7's 14 px with the widest headline word
#: (BIRTHDAY) 94 px in a 102 px marquee. Pixel Operator Bold, the shop signs'
#: face, was the first pick: its display size is scale 2 at 18 px caps, and
#: there AMATEUR, BIRTHDAY and OPENING (110, 120, 104 px) fit no layout.
CLUB_FACE = "monogram_italic"


def club(w, h, row, key):
    """Theatrical bargain-bin glam: a performer under a spotlight -- the
    walker's comp is Duke Nukem 3D's club dancer -- in one of three layouts
    (the art-direction feedback's library: centred, diagonal, off-centre)."""
    from . import pixel_figure as PF
    roll = Roll(f"club|{row}|{key}")
    top, foot, gold, hot = CLUB_PALETTES[roll.below(len(CLUB_PALETTES))]
    c = Canvas(w, h, foot)
    # the airbrushed ground, reaching its foot at the stage and going to
    # near-black below it: the sheet's BLACK mass. Graded over the whole
    # height, a diagonal sheet's darkest twentieth blurred to 39-43 luma and
    # the lamp could not open the range to 85 alone (`poster_checks`).
    floor = _mix(foot, (0, 0, 0), 0.5)
    for y in range(h):
        t = y / max(1, int(h * 0.76))
        c.rect(0, y, w, y + 1, _mix(top, foot, t) if t <= 1.0 else floor)
    head, small = PC.CLUB[row % len(PC.CLUB)]
    layout = CLUB_LAYOUTS[roll.below(len(CLUB_LAYOUTS))]
    mirror = bool(roll.below(2))
    # A LAYOUT MUST SET ITS TITLE AT DISPLAY SIZE, or it is not this sheet's
    # layout (the typography guide, 2026-09-30: "If a word still does not fit,
    # edit the copy or choose a wider title area. Do not solve every fit
    # problem by shrinking the type."). The first cut shrank: CHAMPAGNE ROOM
    # stepped at scale 1 read smaller than its own punchline, SHOWGIRLS set in
    # no face the off-centre strip held, and a strip fitting each word on its
    # own set LIVE ON large and STAGE small. So a layout is this sheet's only
    # when its whole title sets at scale 2 in `CLUB_FACE`. A title one asymmetric layout
    # cannot hold tries the other before the marquee (the wider area): falling
    # straight to the marquee made two thirds of the set centred, and the
    # feedback asks that the rest be "visibly different". Tried on a scratch
    # sheet; the roll is not consumed.
    strip = int(w * 0.42)

    def holds(name):
        if name == "diagonal":
            return stepped_title(Canvas(w, h, foot), head, (6, 6, w - 6, int(h * 0.36)), 1,
                                 hot, (0, 0, 0), face=CLUB_FACE, scales=(2,)) is not None
        if name == "offcentre":
            return all(len(pt.trim(pt.render(wd, 2, CLUB_FACE))[0]) + 1 <= (w - 5) - (strip + 3)
                       for wd in head.split())
        return True

    if not holds(layout):
        other = {"diagonal": "offcentre", "offcentre": "diagonal"}[layout]
        layout = other if holds(other) else "centred"
    focal_kind = CLUB_FOCAL.get(head, "performer")
    poses = CLUB_POSES.get(head, ("behind_head",))
    pose = poses[roll.below(len(poses))]
    stage_top, stage_edge = _mix(hot, (60, 20, 20), 0.55), _mix(foot, (0, 0, 0), 0.3)
    if layout == "centred":
        # the marquee holds two scale-2 lines (2 x 14 + 2) inside its bulbs
        fx, feet, fh = w // 2, int(h * 0.78), int(h * 0.47)
        mh = int(h * 0.27)
        _spotlight(c, w // 2, 0, fx, feet, 0.40)          # the marquee hides the lamp
        title = fit_text(c, head, _marquee(c, (4, 4, w - 4, mh), hot), (40, 10, 60),
                         face=CLUB_FACE, bold=True)
        small_box = (5, int(h * 0.84), w - 5, int(h * 0.95))
        venue_box = (5, int(h * 0.95), w - 5, h - 3)
    elif layout == "diagonal":
        # feet high enough that the stage's pool clears the venue line
        fx, feet, fh = int(w * 0.30), int(h * 0.84), int(h * 0.56)
        if mirror:
            fx = w - fx
        # the lamp hangs below the headline, not behind it: a beam under the
        # letters cost them contrast (`poster_checks`: 2.995 against 3.0)
        # and it is the sheet's WHITE mass, so it is big: with the figure
        # lifted clear of the venue line the pool alone blurred to 77-83
        _spotlight(c, (8 if mirror else w - 8), int(h * 0.36) + 8, fx, feet, 0.48, lamp=(9, 6))
        title = stepped_title(c, head, (6, 6, w - 6, int(h * 0.36)), 1, hot, (0, 0, 0),
                              face=CLUB_FACE, scales=(2,))
        # the punchline's side box, as wide as the figure allows: at half the
        # sheet IMPORTANT fitted in no face and the line fell into the pool
        side = (int(w * 0.44), int(h * 0.50), w - 6, int(h * 0.74)) if not mirror else (6, int(h * 0.50), int(w * 0.56), int(h * 0.74))
        small_box, venue_box = side, (5, int(h * 0.94) - 2, w - 5, h - 4)
    else:                                               # off-centre: a strip of information
        fx, feet, fh = strip // 2, int(h * 0.78), int(h * 0.62)
        _spotlight(c, strip // 2, 0, strip // 2, feet, 0.30)
        c.rect(strip, 3, w - 3, int(h * 0.86), gold)
        y = 10
        rects = []
        for wd in head.split():
            r = fit_text(c, wd, (strip + 3, y, w - 5, y + 24), (40, 10, 60), face=CLUB_FACE,
                         cap=2, bold=True)
            rects.append(r)
            y = (r[3] if r else y + 20) + 4
        rs = [r for r in rects if r]
        title = (min(r[0] for r in rs), rs[0][1], max(r[2] for r in rs), rs[-1][3]) if rs else None
        # the punchline across the foot, below the strip: the "small" face sets
        # IMPORTANT at 62 px and the left panel is 52, so no narrow box held it
        small_box, venue_box = (5, int(h * 0.87), w - 5, h - 4), (strip + 2, int(h * 0.86) - 16, w - 5, int(h * 0.86) - 3)
    before = bytes(c.buf)
    _stage(c, fx, feet, max(12, fh * 2 // 5), max(4, fh // 11), stage_top, stage_edge)
    if focal_kind == "performer":
        # a pole starts under the headline, never through it
        pole_from = 4 if layout == "offcentre" else (title[3] + 3 if title else 4)
        PF.pinup(PF.Figure(), fx, feet - fh, fh, mirror=mirror, pose=pose,
                 pole_from=pole_from).paint(c)
    else:                                   # the glass stands in the pool of light
        g = max(8, fh // 4)
        _martini(c, fx, feet - g - 2, g, gold, hot)
    focal = drawn(c, before)
    ink = (236, 232, 240)
    small_at = fit_text(c, small, small_box, ink, face=SMALL_FACE, cap=2, fallback="m5x7")
    if small_at is None and layout != "offcentre":
        # too long for its side: the full-width band above the venue
        small_at = fit_text(c, small, (5, int(h * 0.80), w - 5, venue_box[1]), ink, face=SMALL_FACE, cap=1)
    fit_text(c, CN.name_for(roll.below(len(CN.NAMES))), venue_box,
             (40, 10, 60) if layout == "offcentre" else gold, face=SMALL_FACE, cap=1)
    _club_rule(c, gold)
    return c, {"family": "club", "headline": head, "small": small, "small_at": small_at,
               "title": title, "focal": focal, "layout": layout,
               "pose": pose if focal_kind == "performer" else None,
               "ground": _mix(top, foot, ((focal[1] + focal[3]) / 2 if focal else h / 2) / max(1, h - 1))}


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

#: THE STOCK (1.41.0). The walker, 2026-09-30: "if anything its just too
#: much color"; the palette guide: "a few bright flyers ... stand out more if
#: neighboring posters use cream or newsprint". A painter asked for "plain"
#: prints on white, cream or newsprint; asked for "loud", on the coloured
#: papers it always had; asked for neither (None), on any, as before. Which
#: sheets of a cluster are loud is the cluster's to say
#: (`poster_wall_forms.loud_sheets`, `pole_flyers_forms.plan`).
STOCKS = ("loud", "plain")
PLAIN_PAPER = ((244, 244, 236), (232, 224, 200), (214, 205, 180))


def _pool(stock, both, loud, plain):
    if stock is None:
        return both
    if stock not in STOCKS:
        raise ValueError(f"no poster stock {stock!r}; the stocks are {', '.join(STOCKS)}")
    return loud if stock == "loud" else plain


def bar(w, h, row, key, stock=None):
    roll = Roll(f"bar|{row}|{key}")
    pool = _pool(stock, COPY_PAPER, COPY_PAPER[1:], PLAIN_PAPER)
    paper = pool[roll.below(len(pool))]
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


def alley(w, h, row, key, stock=None):
    roll = Roll(f"alley|{row}|{key}")
    pool = _pool(stock, DAYGLO, DAYGLO[:4], PLAIN_PAPER)
    paper = pool[roll.below(len(pool))]
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
#: A plain sale poster: the deal in red on white, or in navy on cream.
STORE_PLAIN = (((250, 250, 244), (214, 22, 30)), ((238, 232, 210), (20, 24, 110)))
SHOUT = ("SALE", "NOW", "HOT", "WOW")


def store(w, h, row, key, stock=None):
    roll = Roll(f"store|{row}|{key}")
    pool = _pool(stock, STORE_PAPER, STORE_PAPER[:3], STORE_PLAIN)
    paper, head_ink = pool[roll.below(len(pool))]
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


def paint(family, w_px, h_px, row, key="", stock=None):
    """``stock`` (1.41.0) is "loud", "plain" or None; the club has one stock
    and takes none."""
    if family not in PAINTERS:
        raise ValueError(f"no poster family {family!r}; the families are {', '.join(PC.FAMILIES)}")
    if family == "club" or stock is None:
        if stock is not None and stock not in STOCKS:
            raise ValueError(f"no poster stock {stock!r}; the stocks are {', '.join(STOCKS)}")
        return PAINTERS[family](int(w_px), int(h_px), int(row), str(key))
    return PAINTERS[family](int(w_px), int(h_px), int(row), str(key), stock)
