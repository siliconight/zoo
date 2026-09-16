"""The flat art: posters, banners, ceiling hangers, aisle signs, playmats.

Zoo 0.98.0, and the cheap half of "the card shop is not dense enough"
(`docs/SET_DRESSING_REFERENCES.md`, "The card shop is not dense enough, and
what dense means"). `card_art` paints the PRODUCT -- a box front, a card, a
bay header -- and this paints the things that hang on and over it. Same
machinery throughout: a `Canvas` with row 0 at the top, integer arithmetic,
`zlib.crc32` for every draw, so the same inputs give the same bytes in host
Python and inside Blender. `card_art.paint` is still the one dispatcher and
routes the five kinds below here; `recipes/_card_atlas.py` is still the one
thing that turns tiles into geometry.

THE COMPOSITION TRAVELS AND THE CONTENT DOES NOT. The walker, sending the
fourth poster reference: "obviously we can't copy this intellectual property,
but it is comps of what it could look like." So what this module takes from
the references is the LAYOUT and nothing else -- no character, name, logo or
set from any of them is drawn, every string comes from `card_brands.py`, and
`tests/test_card_brands.py`'s denylist holds every one of them.

THE POSTER'S LAYOUT, WHICH THE FOURTH REFERENCE CORRECTED. The earlier three
read as a title block along the BOTTOM and that is what the first draft of
this module built. The framed magazine cover the walker sent afterwards
settles it the other way:

  * the TITLE IS AT THE TOP, over the art, in a serif;
  * the only thing at the bottom is a small publisher mark in one corner;
  * one creature CENTRED, filling the frame and looking out of it;
  * one strong warm ground, with architecture behind;
  * and a framed poster is THREE RECTANGLES -- frame, mat, plate -- not one
    quad with a border painted into it. That last one is geometry and lives
    in `flat_forms.py`; the mat is a slab, not a texture.

THE SERIF IS DRAWN, NOT MINTED, and this is a look that was narrowed on
purpose. The factory has exactly one typeface -- Pixel Operator, through
`pixel_type` -- and it is a sans. `_serif` post-processes the glyph mask:
it widens the top and bottom row of every stem by one pixel and lays a
one-pixel shadow under the whole line, which at the sizes a poster title
ships (scale 1 to 3, so 11 to 33 rows of ink) is what separates a title from
a price sign at three metres. What an ornate fantasy serif would have bought
is the register itself -- the reference's title is the most expensive thing
in its frame -- and what it would cost is a second face minted into
`pixel_type_glyphs.py`, which is a Pixelcoat job (roadmap: the poster art is
listed under Pixelcoat in the references file) and not a Zoo one.

RESOLUTION: `card_art.TEXEL`, 256 px/m, and THAT IS THE CHEAP VERSION. The
brief asked for art that reads at 3 m and a coloured rectangle at 10 m; the
arithmetic for both is in `reads_at()` below, and at 256 px/m a poster is
magnified about two to one at three metres. See `POSTER_TEXEL_NOTE`.

FRAME AND UNITS: pixels, row 0 at the TOP. Colours are sRGB.
"""
from __future__ import annotations

import zlib

from . import card_brands as CB
from . import pixel_type as pt
from .card_art import (Canvas, MARKER, NAME_BAND as CA_NAME_BAND, Roll, TEXEL,
                       _dashes, _ellipse, _frame, _lum, _mix, _readable,
                       _stamp)

#: How rough each printed surface is. A poster is coated paper and a banner
#: is printed vinyl; a playmat is rubber-backed cloth and is the roughest
#: thing here, which is why it does not take `card_art.CARD_ROUGHNESS`.
POSTER_ROUGHNESS = 0.46
BANNER_ROUGHNESS = 0.62
HANGER_ROUGHNESS = 0.52
MAT_ROUGHNESS = 0.88

#: The kinds this module paints, which `card_art.paint` routes here.
KINDS = ("poster", "banner", "hanger", "aisle", "playmat")

#: WHAT A BIGGER TEXEL WOULD BUY, measured rather than asserted, so the
#: walker can choose it later (the standing rule: ship the cheap version and
#: say what the expensive one would have bought).
#:
#: A length L metres at distance z metres subtends 2*atan(L/2z); on a 1920 px
#: display across a 70 degree horizontal FOV that is 1920/70 = 27.43 px per
#: degree. So one metre at 3 m is 519 screen px and at 10 m is 157. A poster
#: is 1:1 with the screen at three metres at 519 px/m; at `TEXEL` it is 256,
#: so every texel covers about two screen pixels and the art is BLOCKY at
#: three metres rather than soft -- which is the house look (every Pixelcoat
#: pack asks for nearest-neighbour and `card_art` is deliberately a 4 mm
#: pixel), not a defect. At ten metres 256 px/m is already minified 3.3 to 1
#: and the poster is a coloured rectangle, which is the other half of what
#: was asked for and comes free.
#:
#: The figures are in the release note. 512 px/m quadruples every poster
#: tile; nothing else in the shop moves, because `TEXEL` stays what it is.
POSTER_TEXEL_NOTE = "ships at card_art.TEXEL; see reads_at() and the 0.98.0 entry"
#: px per degree on the target display, and the FOV it assumes. Written down
#: because a different display moves every number derived from it.
SCREEN_PX, SCREEN_FOV_DEG = 1920.0, 70.0


def reads_at(length_m, distance_m, texel=TEXEL):
    """``(screen_px, texels, ratio)`` for a length seen at a distance.

    ``ratio`` above 1 is magnified (one texel covers that many screen
    pixels); below 1 is minified. A probe: it prints the arithmetic and
    names no verdict.
    """
    import math
    ang = 2.0 * math.degrees(math.atan(float(length_m) / (2.0 * float(distance_m))))
    screen = ang * SCREEN_PX / SCREEN_FOV_DEG
    texels = float(length_m) * float(texel)
    return (screen, texels, screen / texels if texels else 0.0)


# --- the ink -----------------------------------------------------------------


def _warm(rgb, k=3):
    """A colour pushed toward the reference's burning sky, keeping its own
    identity. ``k`` of 4 parts stay; the rest goes to a hot orange."""
    return _mix(rgb, (232, 96, 26), 4 - k, 4)


def _serif(mask):
    """Slab serifs on a sans mask: the top and bottom row of every stem
    widened by one pixel, which is all a serif IS at eleven rows of ink.

    Returns a NEW mask one pixel wider each side, so the caller's centring
    arithmetic sees the real width. An empty mask comes back unchanged.
    """
    if not mask or not any(any(r) for r in mask):
        return mask
    w, hgt = len(mask[0]), len(mask)
    out = [bytearray(w + 2) for _ in mask]
    for y, row in enumerate(mask):
        for x, v in enumerate(row):
            if v:
                out[y][x + 1] = 1
    # A SERIF IS A FOOT ON A STEM, and only a stem gets one. The first draft
    # widened every inked column of the top and bottom row, so a FULL STOP
    # -- whose ink is three rows at the baseline, and therefore both its own
    # top row and its own bottom row -- came out three pixels wide and read
    # as a dash: "YOUSE VS. THEM" rendered as "YOUSE VS_ THEM" in the first
    # frame. Caught by looking at it, not by a test. A column only counts as
    # a stem when its ink spans at least half the line's height.
    tall = []
    for x in range(w):
        ys = [y for y in range(hgt) if mask[y][x]]
        tall.append(bool(ys) and (ys[-1] - ys[0] + 1) * 2 >= hgt)
    for y in (0, hgt - 1):
        for x, v in enumerate(mask[y]):
            if v and tall[x]:
                out[y][x] = 1
                out[y][x + 2] = 1
    return out


def _serif_stamp(c, text, x0, y0, x1, y1, rgb, shadow=None, cap=6):
    """`card_art._stamp` in a drawn serif, with a one-pixel shadow under it.

    Measured the way `_stamp` is: the largest whole scale whose INK fits,
    and 0 -- nothing painted -- when not even scale 1 does. The shadow is
    offset down and right by ``max(1, scale // 2)``, so it grows with the
    face instead of vanishing at scale 3.
    """
    box_w, box_h = int(x1 - x0), int(y1 - y0)
    if box_w <= 2 or box_h <= 0:
        return 0
    s = pt.fit_scale(text, max(0, box_w - 2), cap=cap)
    while s:
        m = _serif(pt.trim(pt.render(text, s)))
        if len(m) <= box_h and len(m[0]) <= box_w:
            ox = int(x0) + (box_w - len(m[0])) // 2
            oy = int(y0) + (box_h - len(m)) // 2
            if shadow is not None:
                d = max(1, s // 2)
                c.mask(m, ox + d, oy + d, shadow)
            c.mask(m, ox, oy, rgb)
            return s
        s -= 1
    return 0


def _sky(c, x0, y0, x1, y1, top, bottom):
    """A vertical gradient: the reference's burning sky, in whole rows."""
    span = max(1, int(y1) - int(y0))
    for y in range(int(y0), int(y1)):
        c.rect(x0, y, x1, y + 1, _mix(top, bottom, y - int(y0), span))


def _skyline(c, x0, x1, base_y, top_y, rgb, roll):
    """The architecture behind the creature: towers and battlements along
    the horizon, drawn as a run of rectangles of varying height. Deliberately
    a silhouette -- at a poster's size a castle IS a silhouette, and the
    alternative is detail nobody resolves for the same pixels."""
    span = max(1, int(base_y) - int(top_y))
    x = int(x0)
    while x < int(x1):
        w = roll.between(max(2, (int(x1) - int(x0)) // 14),
                         max(3, (int(x1) - int(x0)) // 7))
        hgt = roll.between(span // 4, span)
        c.rect(x, int(base_y) - hgt, min(int(x1), x + w), int(base_y), rgb)
        if hgt > span // 2 and w >= 5:            # a battlemented top
            for k in range(0, w, 3):
                c.rect(x + k, int(base_y) - hgt - 2, min(int(x1), x + k + 2),
                       int(base_y) - hgt, rgb)
        x += w + roll.below(3)


def _held_figure(c, cx, cy, w, h, ink, accent):
    """The small armoured figure the creature holds against its chest -- the
    fourth reference's own composition, and the thing that gives the creature
    its scale. A body, a helm, a bright visor slit."""
    if w < 4 or h < 6:
        return
    c.rect(cx - w // 2, cy - h // 2 + h // 4, cx + w // 2, cy + h // 2, ink)
    c.rect(cx - w // 3, cy - h // 2, cx + w // 3, cy - h // 2 + h // 3, ink)
    c.rect(cx - w // 4, cy - h // 2 + h // 6, cx + w // 4,
           cy - h // 2 + h // 6 + max(1, h // 12), accent)


def _creature(c, x0, y0, x1, y1, kind, ink, accent, eye):
    """ONE CREATURE, CENTRED, FILLING THE FRAME, LOOKING OUT. The fourth
    reference's composition, drawn per `card_brands.KINDS` so twelve games do
    not make one poster.

    This is NOT `card_art._figure` at a larger size, and the difference is
    the whole point of the reference: a card face's figure is a blob in a
    panel seen at two metres, and a poster's is a portrait seen at three. It
    is built from the shoulders up -- head high and wide, eyes as bright
    pips aimed at the viewer, arms brought in around a held figure.
    """
    w, h = int(x1 - x0), int(y1 - y0)
    cx = (int(x0) + int(x1)) // 2
    if w < 12 or h < 16:
        _ellipse(c, cx, (int(y0) + int(y1)) // 2, w * 0.4, h * 0.4, ink)
        return
    # THE HEAD SITS ON THE SHOULDERS, AND THE FIRST DRAFT'S DID NOT. With the
    # head centred at 0.30 of the sub-frame and the torso starting at 0.46,
    # a 154 x 230 plate left ten pixels of sky between the two and the
    # creature read as a head floating over a mound. The frame showed it; no
    # test did, which is the 0.96.0 lesson repeating. The shoulder line is
    # now DERIVED from the head -- it starts three quarters of a head-radius
    # below the head's centre, so the two always overlap whatever the plate's
    # aspect is -- rather than being a second free fraction.
    head_r = w * 0.19
    head_y = int(y0 + h * 0.27)
    shoulder_y = head_y + int(head_r * 0.75)
    # the torso: a trapezoid widening to the bottom of the frame
    for y in range(shoulder_y, int(y1)):
        t = (y - shoulder_y) / max(1.0, float(int(y1) - shoulder_y))
        half = int(w * (0.24 + 0.22 * t))
        c.rect(cx - half, y, cx + half, y + 1, ink)
    if kind == "wizard":                       # a hood, not a skull
        for y in range(int(y0 + h * 0.10), shoulder_y):
            t = (y - (y0 + h * 0.10)) / max(1.0, h * 0.36)
            half = max(1, int(w * (0.04 + 0.26 * t)))
            c.rect(cx - half, y, cx + half, y + 1, ink)
        shade = _mix(ink, (0, 0, 0), 2, 3)     # the face in shadow
        _ellipse(c, cx, head_y + int(h * 0.04), head_r * 0.62, head_r * 0.72, shade)
    elif kind == "scifi":                      # a helm with a visor band
        c.rect(cx - int(head_r), head_y - int(head_r), cx + int(head_r),
               head_y + int(head_r * 0.9), ink)
        c.rect(cx - int(head_r * 0.8), head_y - int(head_r * 0.1),
               cx + int(head_r * 0.8), head_y + int(head_r * 0.3), accent)
    else:                                      # monster and sport: a skull
        _ellipse(c, cx, head_y, head_r, head_r * 0.92, ink)
        if kind == "monster":                  # ...and horns, swept out
            # A HORN GROWS OUT OF THE SKULL. The first draft placed three
            # blocks per side at 0.70, 1.02 and 1.34 head-radii out and
            # 0.85 up, and the skull's ellipse is only 0.38 radii wide at
            # that height -- so every one of the six floated clear of the
            # head and read as antennae. Seen in the frame, not in a test.
            # The sweep now STARTS inside the ellipse and each step
            # overlaps the one below it: the row step is 0.17 of a radius
            # against a block 0.25 tall, so the run cannot come apart at
            # any plate size.
            steps = 5
            for side in (-1, 1):
                for k in range(steps):
                    frac = k / float(steps - 1)
                    hx = cx + int(side * head_r * (0.40 + 0.85 * frac))
                    hy = head_y - int(head_r * (0.45 + 0.85 * frac))
                    t = max(1, int(head_r * 0.12))
                    c.rect(hx - t, hy, hx + t,
                           hy + max(2, int(head_r * 0.25)), ink)
    if kind != "wizard":                       # THE EYES LOOK OUT
        e = max(1, int(head_r * 0.22))
        for side in (-1, 1):
            _ellipse(c, cx + int(side * head_r * 0.42), head_y - int(head_r * 0.10),
                     e, e, eye)
    else:
        e = max(1, int(head_r * 0.16))
        for side in (-1, 1):
            _ellipse(c, cx + int(side * head_r * 0.26), head_y + int(h * 0.03),
                     e, e, eye)
    # the arms brought in around whatever it is holding
    arm_y = int(y0 + h * 0.62)
    arm_t = max(2, int(h * 0.07))
    for side in (-1, 1):
        ax = cx + int(side * w * 0.40)
        c.rect(min(ax, cx), arm_y, max(ax, cx), arm_y + arm_t, ink)
    _held_figure(c, cx, int(y0 + h * 0.72), max(4, int(w * 0.17)),
                 max(6, int(h * 0.22)), _mix(ink, (255, 255, 255), 1, 2), accent)


# --- the tiles ---------------------------------------------------------------


def poster_plate(game, w_px, h_px, key, maker=None):
    """The painted plate INSIDE a frame and mat, or the whole of a bare
    poster: warm sky, architecture, one creature looking out, the title
    across the top in a serif, the maker's mark in the bottom right."""
    roll = Roll(f"poster|{game['id']}|{key}")
    ground = CB.hex_rgb(game["ground"])
    ink = CB.hex_rgb(game["ink"])
    accent = CB.hex_rgb(game["accent"])
    hot = _warm(accent, 2)
    c = Canvas(w_px, h_px, ground)
    horizon = int(h_px * 0.72)
    _sky(c, 0, 0, w_px, horizon, _mix(_warm(ground, 3), (0, 0, 0), 1, 2), hot)
    c.rect(0, horizon, w_px, h_px, _mix(ground, (0, 0, 0), 2, 3))
    _skyline(c, 0, w_px, horizon, int(h_px * 0.34),
             _mix(hot, (0, 0, 0), 3, 4), roll)
    body = _mix(ink, (0, 0, 0), 1, 3) if _lum(ink) > 120 else ink
    _creature(c, int(w_px * 0.10), int(h_px * 0.16), int(w_px * 0.90), h_px,
              game["kind"], body, accent,
              _readable(body, hot, (248, 240, 200)))
    # THE TITLE, AT THE TOP, OVER THE ART -- the fourth reference's one
    # correction to the other three. A long name wraps rather than shrinking
    # to a size nobody reads, the way a bay header does.
    title = _readable(_mix(_warm(ground, 3), (0, 0, 0), 1, 2),
                      (248, 240, 208), _mix(accent, (255, 255, 255), 1, 3))
    shade = (16, 12, 10)
    band = max(pt.LINE // 2, int(h_px * 0.17))
    if not _serif_stamp(c, game["name"], 3, 2, w_px - 3, 2 + band, title,
                        shadow=shade, cap=4):
        lines = pt.wrap(game["name"], w_px - 8, 1) or []
        half = band // max(1, len(lines) or 1)
        for i, line in enumerate(lines):
            _serif_stamp(c, line, 3, 2 + i * half, w_px - 3,
                         2 + (i + 1) * half, title, shadow=shade, cap=2)
    mk = maker or CB.maker_for(key)
    # THE BAND IS THE FACE'S OWN INK HEIGHT, NOT HALF A LINE, and the first
    # draft used `pt.LINE // 2` -- 8 rows for a face whose capitals trim to
    # `NAME_BAND` = 11. `_stamp` measures the ink against the box and paints
    # NOTHING rather than a smear when it does not fit, so every poster
    # shipped with no maker's mark at all and nothing said so. Caught by
    # `test_the_posters_title_is_at_the_top_and_the_makers_mark_at_the_bottom`,
    # which asks where the pixels moved rather than whether `_stamp` was
    # called -- the same shape of mistake `card_art._stamp`'s own docstring
    # records for the booster-box fronts ("0 of 12 lettered, then 12").
    mark_h = CA_NAME_BAND + 1
    if h_px > mark_h * 3 and w_px > 24:
        _stamp(c, mk["short"], w_px - 2 - int(w_px * 0.42), h_px - 2 - mark_h,
               w_px - 2, h_px - 2, _mix(CB.hex_rgb(mk["ink"]),
                                        (255, 255, 255), 1, 2), cap=1)
    return c


def banner_face(game, w_px, h_px, key):
    """A printed cloth banner hung above shelving or behind the play area.
    Read across a room and never nearer than the aisle, so it is the game's
    name on its own ground with a rule under it and one small figure -- the
    poster's composition would be illegible at a banner's aspect."""
    ground = _mix(CB.hex_rgb(game["ground"]), (0, 0, 0), 1, 3)
    accent = CB.hex_rgb(game["accent"])
    c = Canvas(w_px, h_px, ground)
    _sky(c, 0, 0, w_px, h_px, _mix(ground, (0, 0, 0), 1, 2), _warm(ground, 3))
    _frame(c, 0, 0, w_px, h_px, max(1, h_px // 14), accent)
    pad = max(2, h_px // 7)
    ink = _readable(ground, (244, 238, 216), accent,
                    CB.hex_rgb(game["ink"]))
    _serif_stamp(c, game["name"], pad + h_px, pad, w_px - pad,
                 h_px - pad - max(1, h_px // 7), ink, shadow=(14, 12, 12), cap=6)
    c.rect(pad + h_px, h_px - pad - max(1, h_px // 8), w_px - pad,
           h_px - pad, accent)
    # one figure at the hoist end, so the banner is not a word on a field
    if w_px > h_px + 12 and h_px >= 16:
        _creature(c, pad, pad, pad + h_px - pad, h_px - pad, game["kind"],
                  _mix(CB.hex_rgb(game["ink"]), (0, 0, 0), 1, 3), accent,
                  (248, 240, 200))
    return c


def hanger_face(game, w_px, h_px, key):
    """The painted model on a drop chain: a die-cut creature on a plate, the
    side a shopper sees from the aisle. Both faces of the hanger carry this
    ONE tile -- a hanging sign is printed both sides and painting two is two
    tiles of atlas for a difference nobody can see from either side."""
    ground = _warm(CB.hex_rgb(game["ground"]), 2)
    accent = CB.hex_rgb(game["accent"])
    c = Canvas(w_px, h_px, ground)
    _sky(c, 0, 0, w_px, h_px, _mix(ground, (255, 255, 255), 1, 4),
         _mix(ground, (0, 0, 0), 1, 3))
    _frame(c, 0, 0, w_px, h_px, max(1, min(w_px, h_px) // 12), accent)
    inset = max(2, min(w_px, h_px) // 10)
    _creature(c, inset, inset, w_px - inset, h_px - inset, game["kind"],
              _mix(CB.hex_rgb(game["ink"]), (0, 0, 0), 1, 4), accent,
              (250, 244, 210))
    return c


def aisle_letters(says, w_px, h_px, key):
    """The hand-lettered sign hung over an aisle naming what is under it.
    Board, a marker rule, and the word -- and the word is the ONE thing on
    this tile that has to be legible, because a sign nobody can read over an
    aisle is a coloured rectangle with a chain on it."""
    roll = Roll(f"aisle|{says}|{key}")
    c = Canvas(w_px, h_px, (236, 230, 214))
    _frame(c, 0, 0, w_px, h_px, max(1, h_px // 16), (58, 52, 44))
    pad = max(2, h_px // 8)
    if not _stamp(c, says, pad, pad, w_px - pad, h_px - pad, MARKER, cap=8):
        lines = pt.wrap(says, w_px - 2 * pad, 1) or []
        room = h_px - 2 * pad
        if lines and len(lines) * (pt.LINE // 2 + 1) <= room:
            step = room // len(lines)
            for i, line in enumerate(lines):
                _stamp(c, line, pad, pad + i * step, w_px - pad,
                       pad + (i + 1) * step, MARKER, cap=3)
        else:
            _dashes(c, pad, pad, w_px - pad, h_px - pad, roll, MARKER)
    return c


def playmat_face(game, w_px, h_px, key):
    """A printed playmat: a full-bleed painted scene under the cards.

    The one tile in this module seen from ABOVE and from under a metre, and
    the only one whose composition is not the poster's -- a mat is looked
    down on with cards on it, so the middle is where the cards go and the
    art is a ground, a border and one emblem off to the hoist side. The
    walker's close-up reference is exactly this: a neon mat with a pack held
    over it and the printing readable around the edge.
    """
    ground = _mix(CB.hex_rgb(game["ground"]), (0, 0, 0), 1, 2)
    accent = CB.hex_rgb(game["accent"])
    ink = CB.hex_rgb(game["ink"])
    c = Canvas(w_px, h_px, ground)
    _sky(c, 0, 0, w_px, h_px, _mix(ground, (0, 0, 0), 1, 3), _warm(ground, 3))
    # the play zones a real mat prints: a deck box, a discard box, a row
    band = max(2, h_px // 14)
    _frame(c, 0, 0, w_px, h_px, band, _mix(accent, (0, 0, 0), 2, 3))
    _frame(c, band + 1, band + 1, w_px - band - 1, h_px - band - 1, 1, accent)
    if w_px >= 40 and h_px >= 24:
        zx, zw = int(w_px * 0.62), int(w_px * 0.14)
        for k in range(3):
            x = zx + k * (zw + max(1, w_px // 40))
            _frame(c, x, int(h_px * 0.30), min(w_px - band - 2, x + zw),
                   int(h_px * 0.74), 1, _mix(accent, ground, 1, 2))
        _creature(c, int(w_px * 0.06), int(h_px * 0.14), int(w_px * 0.42),
                  int(h_px * 0.88), game["kind"],
                  _mix(ink, (0, 0, 0), 1, 4), accent, (250, 240, 200))
    line = max(1, h_px // 12)
    _stamp(c, game["short"], band + 2, h_px - band - line - 2,
           band + 2 + int(w_px * 0.18), h_px - band - 2,
           _mix(accent, (255, 255, 255), 1, 3), cap=2)
    return c


# --- the dispatcher's half ---------------------------------------------------


def paint(spec, w, h):
    """One tile, from a planner's spec already converted to pixels.

    `card_art.paint` owns the metres-to-pixels conversion and the kind
    lookup; this is the half that knows these five kinds. Called only from
    there, so a planner never chooses between two painters.
    """
    kind = spec["kind"]
    key = spec.get("key", "")
    maker = next((m for m in CB.MAKERS if m["id"] == spec.get("maker")), None)
    if kind == "aisle":
        return aisle_letters(spec.get("says", ""), w, h, key)
    game = CB.BY_ID[spec["game"]]
    if kind == "poster":
        return poster_plate(game, w, h, key, maker)
    if kind == "banner":
        return banner_face(game, w, h, key)
    if kind == "hanger":
        return hanger_face(game, w, h, key)
    if kind == "playmat":
        return playmat_face(game, w, h, key)
    raise ValueError(f"flat_art.paint: unknown tile kind {kind!r}")


def atlas_bytes(atlas):
    """``(png_bytes, raw_rgb_bytes)`` for a built atlas -- the two numbers a
    texture budget is argued in. The PNG is what ships in the GLB; the raw
    figure is what the card costs once it is decoded, which is the one that
    is spent on every client. A probe: it returns numbers and names nothing.
    """
    png = atlas["canvas"].png()
    w, h = atlas["size"]
    return (len(png), w * h * 3)


def _key(*parts):
    """A short stable tile key, so an atlas's rects do not carry a sentence."""
    return "%08x" % (zlib.crc32("|".join(str(p) for p in parts).encode("utf-8"))
                     & 0xFFFFFFFF)
