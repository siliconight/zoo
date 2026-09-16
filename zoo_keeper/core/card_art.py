"""Card, box and sign artwork for the card shop, painted in pure Python.

Zoo 0.95.0. The same pattern as `vending_forms`' panel, `crt_screens`'
picture and `dartboard_art`'s board: a `Canvas` (row 0 at the top), integer
arithmetic and `zlib.crc32` for every draw, so the same inputs give the same
bytes in host Python and inside Blender, and the image's NAME is derived
from its own pixels -- one image per distinct atlas, reused across builds.

DELIBERATELY LOW RESOLUTION, and that is the design rather than a saving.
`TEXEL` is 256 px/m -- a 4 mm pixel -- so a 0.27 m booster-box front is 69 px
across and a 0.063 m card is 16. The walker's own framing, "Nobody reads a
card face at play distance", is the whole reason the art can be ONE small
atlas per specimen instead of a texture per product: what the eye takes from
a card shop at two metres is COLOUR AND FRAME, which is exactly what the
reference describes ("a monster game's yellow border, a wizard game's black
border and brown back, a sci-fi game's grey frame, a sports card's white
border"). A figure is a blob and a rules box is a run of dashes, because at
this size that is what a figure and a rules box ARE. Nothing here is a real
mark; see `card_brands.py`.

WHAT IS LETTERED AND WHAT IS NOT:

  * A HEADER SIGN over a pack-wall bay is read across a room, and is set in
    the factory's pixel face (`pixel_type`, Pixelcoat's Pixel Operator) at
    the largest whole scale that fits -- two lines if one will not.
  * A BOX FRONT carries the game's short name where the box has `NAME_BAND`
    rows to spare over its figure panel and its maker band. All twelve games
    do at the size a pack wall faces them out at; at 160 px/m none did,
    which is the measurement that set `TEXEL`.
  * A CARD FACE carries no type at any size, and a test asserts `card_face`
    never grows any. 16 px of lettering is noise that costs the same pixels
    as lettering somebody can read.
  * A PENNANT carries none either, and that is `pennant_forms`' decision:
    it is not painted at all, because a colour and a band is what a pennant
    at ceiling height IS.

FRAME AND UNITS: pixels. A tile's own rect inside the atlas is pixels with
row 0 at the TOP; `uv_rect` flips to glTF's bottom-up V.
"""
from __future__ import annotations

import zlib

from . import card_brands as CB
from . import pixel_type as pt
from .vending_forms import Canvas

#: Artwork density, pixels per metre -- ONE constant for every tile. A 4 mm
#: pixel, the vending panel's (`vending_forms.TEXEL`), crisp under the
#: nearest-neighbour filter every Pixelcoat pack asks for.
#:
#: REFUTED, kept: 160 px/m first, on the argument that nothing here is read
#: closely. It is not the reading distance that sets this, it is the pixel
#: face -- `pixel_type`'s glyphs trim to 11 rows at scale 1, so at 160 px/m
#: a 0.18 m booster-box front had 29 rows to spend and could not carry its
#: game's name over its figure at all (measured on the contact sheet: 0 of
#: 12 lettered). At 256 the same box is 46 rows and all twelve carry it.
#: The atlas a whole pack wall needs is still one 256 x 300 PNG.
TEXEL = 256
#: The height of a line of capitals in the factory's face at scale 1, and
#: therefore the shortest band that can carry a name. Derived from the face
#: rather than pinned, because a re-mint of the glyphs would move it.
NAME_BAND = len(pt.trim(pt.render("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 1)))
#: Gutter between atlas tiles, and the atlas's target width in pixels. The
#: width is a target and not a cap: one tile wider than it gets its own row.
GUTTER = 2
ATLAS_W = 256
#: How rough a painted card face is. `dartboard_art` paints sisal at 0.85;
#: a card is coated stock and a cardboard box is not, so they split.
CARD_ROUGHNESS = 0.42
BOX_ROUGHNESS = 0.78
#: The ink of a shop's hand lettering, and the kraft of an unlabelled box.
MARKER = (26, 26, 30)
KRAFT = (168, 132, 84)
#: The tile kinds `flat_art` paints, named HERE because `paint` below is the
#: one dispatcher and a kind it does not recognise must fail rather than
#: fall through. Kept as a literal tuple rather than imported from that
#: module, because importing it at module scope is the cycle.
#: `tests/test_flat_art.py` holds the two tuples equal.
FLAT_KINDS = ("poster", "banner", "hanger", "aisle", "playmat")


class Roll:
    """A 32-bit LCG seeded from a string, so every draw is reproducible and
    no draw touches the build's own RNG streams. (`random.Random` would do
    as well; this matches `back_bar_art`'s integer-only house style and can
    be read in a test without constructing a stream.)"""

    def __init__(self, key):
        self.s = (zlib.crc32(str(key).encode("utf-8")) & 0xFFFFFFFF) or 1

    def next(self):
        self.s = (1664525 * self.s + 1013904223) & 0xFFFFFFFF
        return self.s

    def below(self, n):
        return self.next() % max(1, int(n))

    def between(self, a, b):
        return int(a) + self.below(int(b) - int(a) + 1)

    def pick(self, seq):
        return seq[self.below(len(seq))]


def _mix(a, b, num, den):
    return tuple(int(a[k] + (b[k] - a[k]) * num / den) for k in range(3))


def _ellipse(c, cx, cy, rx, ry, rgb):
    rx, ry = max(1, int(rx)), max(1, int(ry))
    for y in range(int(cy) - ry, int(cy) + ry + 1):
        dy = (y - cy) / float(ry)
        if abs(dy) > 1.0:
            continue
        half = rx * (1.0 - dy * dy) ** 0.5
        c.rect(int(cx - half), y, int(cx + half) + 1, y + 1, rgb)


def _frame(c, x0, y0, x1, y1, t, rgb):
    """A rectangular border ``t`` pixels thick, drawn INSIDE the rect."""
    t = max(1, int(t))
    c.rect(x0, y0, x1, y0 + t, rgb)
    c.rect(x0, y1 - t, x1, y1, rgb)
    c.rect(x0, y0, x0 + t, y1, rgb)
    c.rect(x1 - t, y0, x1, y1, rgb)


def _dashes(c, x0, y0, x1, y1, roll, rgb):
    """The unreadable text block: rows of broken runs, one pixel tall, with
    a blank row between. This IS what a rules box looks like at 40 px, and
    the alternative -- real words at a size nobody resolves -- reads as
    noise for the same pixels and invites somebody to make them legible."""
    y = int(y0)
    while y + 1 <= y1:
        x = int(x0) + roll.below(3)
        while x < x1 - 1:
            run = roll.between(3, 9)
            c.rect(x, y, min(int(x1), x + run), y + 1, rgb)
            x += run + roll.between(1, 3)
        y += 2


def _figure(c, x0, y0, x1, y1, kind, ink, accent, roll):
    """The blobby central figure. Four shapes, one per `card_brands.KINDS`,
    and none of them is anybody's creature: a lump with limbs, a hooded
    wedge, an angular hull, a player in team colours."""
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if w < 6 or h < 6:
        c.rect(x0, y0, x1, y1, ink)
        return
    # FOUR SILHOUETTE FAMILIES, and they had to be made to differ. The first
    # pass drew the wizard's robe and the sci-fi hull as vertical tapers on a
    # panel about as wide as it is tall, and on the contact sheet all three
    # of monster, wizard and sci-fi read as the same MOUND -- the frame
    # colour was carrying the whole difference. A blob is allowed to be a
    # blob; it is not allowed to be the same blob.
    if kind == "monster":                       # a lump, wider than tall
        by = cy + h // 8
        _ellipse(c, cx, by, w * 0.32, h * 0.26, ink)
        _ellipse(c, cx, by - h * 0.26, w * 0.19, h * 0.17, ink)   # head
        for k in range(roll.between(2, 4)):                       # limbs
            side = -1 if k % 2 == 0 else 1
            lx = cx + int(side * w * 0.26)
            ly = by + int((roll.below(3) - 1) * h * 0.12)
            c.rect(min(lx, cx), ly, max(lx, cx), ly + max(1, h // 12), ink)
        for side in (-1, 1):                                      # horns
            hx = cx + int(side * w * 0.13)
            c.rect(hx, int(by - h * 0.46), hx + max(1, w // 22),
                   int(by - h * 0.30), ink)
        e = max(1, w // 16)
        _ellipse(c, cx - w // 10, int(by - h * 0.28), e, e, accent)
        _ellipse(c, cx + w // 10, int(by - h * 0.28), e, e, accent)
    elif kind == "wizard":                      # a narrow robe under a point
        hem = int(y1 - h * 0.05)
        shoulder = int(y0 + h * 0.42)
        for y in range(shoulder, hem):
            t = (y - shoulder) / max(1.0, float(hem - shoulder))
            half = max(1, int(w * (0.05 + 0.17 * t)))
            c.rect(cx - half, y, cx + half + 1, y + 1, ink)
        brim = int(y0 + h * 0.34)               # the hat: a tall cone
        for y in range(int(y0 + h * 0.04), brim):
            t = (y - (y0 + h * 0.04)) / max(1.0, h * 0.30)
            half = max(1, int(w * 0.16 * t))
            c.rect(cx - half, y, cx + half + 1, y + 1, accent)
        c.rect(cx - int(w * 0.18), brim, cx + int(w * 0.18) + 1,
               brim + max(1, h // 16), accent)
        sx = cx + int(w * 0.30)                 # the staff
        c.rect(sx, int(y0 + h * 0.20), sx + max(1, w // 24), hem, accent)
    elif kind == "scifi":                       # a hull ACROSS the frame
        left, right = int(x0 + w * 0.06), int(x1 - w * 0.06)
        span = max(1.0, float(right - left))
        for x in range(left, right):
            t = (x - left) / span
            half = max(1, int(h * (0.05 + 0.24 * (1.0 - abs(2.0 * t - 1.0)))))
            c.rect(x, cy - half, x + 1, cy + half + 1, ink)
        c.rect(left, cy - int(h * 0.30), left + max(1, w // 10),
               cy + int(h * 0.30) + 1, ink)     # tail fin
        _ellipse(c, int(x0 + w * 0.72), cy, w * 0.05, h * 0.09, accent)
    else:                                                      # sport
        by = cy + h // 10
        _ellipse(c, cx, by - int(h * 0.26), w * 0.13, h * 0.11, ink)
        c.rect(cx - int(w * 0.16), by - int(h * 0.14),
               cx + int(w * 0.16), by + int(h * 0.14), accent)
        c.rect(cx - int(w * 0.16), by + int(h * 0.14),
               cx - int(w * 0.03), int(y1 - h * 0.06), ink)
        c.rect(cx + int(w * 0.03), by + int(h * 0.14),
               cx + int(w * 0.16), int(y1 - h * 0.06), ink)


def _lum(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def _readable(on, *candidates):
    """Whichever candidate is furthest in luminance from the ground it is
    printed on. A name band takes the game's OWN colours -- this only
    decides which of them, so a grey-framed sci-fi game does not print grey
    type on a grey band the way the first contact sheet did."""
    return max(candidates, key=lambda c: abs(_lum(c) - _lum(on)))


def _stamp(c, text, x0, y0, x1, y1, rgb, cap=6):
    """The largest whole scale of the pixel face whose INK fits the box,
    centred on the ink. Returns the scale used, or 0 when not even scale 1
    fits -- the caller then paints nothing rather than a smear.

    THE INK, NOT THE LINE, and the difference decides whether a box front
    is lettered at all. `pt.LINE` is 16 rows at scale 1 (ascent plus
    descent), while a line of capitals trims to 11; a booster box front at
    `TEXEL` is 29 px tall with about 12 to spare over its figure panel, so
    measuring the line box refused every one of them and measuring the ink
    sets all twelve at scale 1. Measured on the contact sheet before and
    after: 0 of 12 box fronts lettered, then 12.
    """
    box_w, box_h = int(x1 - x0), int(y1 - y0)
    s = pt.fit_scale(text, max(0, box_w), cap=cap)
    while s:
        m = pt.trim(pt.render(text, s))
        if len(m) <= box_h and len(m[0]) <= box_w:
            c.mask(m, int(x0) + (box_w - len(m[0])) // 2,
                   int(y0) + (box_h - len(m)) // 2, rgb)
            return s
        s -= 1
    return 0


# --- the tiles ---------------------------------------------------------------


def card_face(game, w_px, h_px, key):
    """One card, front. Border, ground, figure, a dash block for the rules
    and -- on a sport card -- a colour chip. No lettering at any size."""
    roll = Roll(f"{game['id']}|{key}")
    border = CB.hex_rgb(game["border"])
    ground = CB.hex_rgb(game["ground"])
    ink = CB.hex_rgb(game["ink"])
    accent = CB.hex_rgb(game["accent"])
    c = Canvas(w_px, h_px, border)
    b = max(1, min(w_px, h_px) // 10)
    art_h = int((h_px - 2 * b) * (0.58 if h_px > 24 else 0.72))
    c.rect(b, b, w_px - b, b + art_h, ground)
    _figure(c, b + 1, b + 1, w_px - b - 1, b + art_h - 1,
            game["kind"], ink, accent, roll)
    if h_px - (b + art_h) - b > 3:
        panel = _mix(ground, (255, 255, 255), 1, 2) if game["kind"] != "wizard" \
            else _mix(ground, (0, 0, 0), 1, 3)
        c.rect(b, b + art_h + 1, w_px - b, h_px - b, panel)
        _dashes(c, b + 2, b + art_h + 3, w_px - b - 2, h_px - b - 2, roll, ink)
    if game["kind"] == "sport":
        team = CB.team_order(key)[0]
        chip = max(2, w_px // 5)
        c.rect(w_px - b - chip, b, w_px - b, b + chip, CB.hex_rgb(team[1]))
        c.rect(w_px - b - chip, b + chip, w_px - b, b + chip + max(1, chip // 3),
               CB.hex_rgb(team[2]))
    return c


def box_face(game, w_px, h_px, key, maker=None):
    """A sealed booster box front: the game's border, a big figure panel, the
    short name where the box is wide enough to carry ink at scale 1, and a
    maker band along the bottom."""
    roll = Roll(f"box|{game['id']}|{key}")
    border = CB.hex_rgb(game["border"])
    ground = CB.hex_rgb(game["ground"])
    ink = CB.hex_rgb(game["ink"])
    accent = CB.hex_rgb(game["accent"])
    c = Canvas(w_px, h_px, border)
    b = max(1, min(w_px, h_px) // 12)
    band = max(2, h_px // 9)
    # A NAME BAND ONLY WHERE THE FIGURE STILL HAS A PANEL. `NAME_BAND` rows
    # of ink plus the maker band plus the borders, and at least as much
    # again left over, or the box carries no type at all.
    name_h = NAME_BAND + 1 if (w_px >= 36 and
                               h_px - 2 * b - band - NAME_BAND - 1 >= NAME_BAND) else 0
    top = b + name_h
    c.rect(b, top, w_px - b, h_px - b - band, ground)
    _figure(c, b + 1, top + 1, w_px - b - 1, h_px - b - band - 1,
            game["kind"], ink, accent, roll)
    if name_h:
        _stamp(c, game["short"], b, b, w_px - b, b + name_h,
               _readable(border, _mix(ground, (255, 255, 255), 2, 3),
                         _mix(ink, (0, 0, 0), 1, 3), accent), cap=3)
    mk = maker or CB.maker_for(key)
    c.rect(b, h_px - b - band, w_px - b, h_px - b, CB.hex_rgb(mk["ink"]))
    if band >= pt.LINE:
        _stamp(c, mk["short"], b + 1, h_px - b - band, w_px - b - 1, h_px - b,
               (240, 240, 232), cap=2)
    else:
        _dashes(c, b + 2, h_px - b - band + 1, w_px - b - 2, h_px - b - 1,
                roll, (240, 240, 232))
    _frame(c, 0, 0, w_px, h_px, max(1, b // 2), accent)
    return c


def header_sign(game, w_px, h_px):
    """The coloured header over a gondola bay: the game's border colour as
    the ground, its name in the pixel face, a rule under it. Read across a
    room, so this is the one tile that is lettered at every size it ships."""
    ground = CB.hex_rgb(game["border"])
    ink = CB.hex_rgb(game["ink"])
    if sum(ground) > 560:                     # a white-bordered sports game
        ink = CB.hex_rgb(game["accent"])
    c = Canvas(w_px, h_px, ground)
    _frame(c, 0, 0, w_px, h_px, max(1, h_px // 12), CB.hex_rgb(game["accent"]))
    pad = max(2, h_px // 8)
    text = game["name"]
    s = _stamp(c, text, pad, pad, w_px - pad, h_px - pad - max(1, h_px // 6),
               ink, cap=8)
    if not s and " " in text:                 # a long name goes on two lines
        a, b = text.split(" ", 1)
        half = (h_px - 2 * pad) // 2
        _stamp(c, a, pad, pad, w_px - pad, pad + half, ink, cap=8)
        _stamp(c, b, pad, pad + half, w_px - pad, h_px - pad, ink, cap=8)
    c.rect(pad, h_px - pad - max(1, h_px // 8), w_px - pad,
           h_px - pad, CB.hex_rgb(game["accent"]))
    return c


def storage_label(maker, w_px, h_px, says, key):
    """The end of a white card-storage box: the reference's shops have towers
    of them on the counter, hand-lettered. Kraft-white board, a marker rule,
    the shop's own words in the pixel face when they fit."""
    roll = Roll(f"label|{key}")
    c = Canvas(w_px, h_px, (232, 228, 214))
    _frame(c, 0, 0, w_px, h_px, 1, (198, 190, 172))
    bar = max(2, h_px // 5)
    c.rect(2, 2, w_px - 2, 2 + bar, CB.hex_rgb(maker["ink"]))
    _stamp(c, maker["short"], 3, 2, w_px - 3, 2 + bar, (244, 242, 236), cap=2)
    # THE WORDS WRAP, and that is what makes this tile lettered at all.
    # "NO TRADES WITHOUT A GROWN-UP" is 210 px of ink at scale 1 and a
    # 0.33 m box end is 84: on one line every sign in `SHOP_SAYS` fell
    # through to dashes. Two or three lines fit five of the six.
    lines = pt.wrap(says, w_px - 6, 1) or []
    room = h_px - bar - 6
    if lines and len(lines) * (NAME_BAND + 1) <= room:
        y = 3 + bar + (room - len(lines) * (NAME_BAND + 1)) // 2
        for line in lines:
            _stamp(c, line, 3, y, w_px - 3, y + NAME_BAND + 1, MARKER, cap=1)
            y += NAME_BAND + 1
        return c
    _dashes(c, 3, 4 + bar, w_px - 3, h_px - 3, roll, MARKER)
    return c


def tin_lid(game, w_px, h_px, key):
    """A collector tin's lid: the game's accent as the metal, an embossed
    ring and the figure. Tins sit inside a case behind glass and are never
    nearer than the counter, so nothing on one is lettered."""
    roll = Roll(f"tin|{game['id']}|{key}")
    c = Canvas(w_px, h_px, CB.hex_rgb(game["accent"]))
    _frame(c, 0, 0, w_px, h_px, max(1, min(w_px, h_px) // 10),
           CB.hex_rgb(game["border"]))
    inset = max(2, min(w_px, h_px) // 6)
    c.rect(inset, inset, w_px - inset, h_px - inset, CB.hex_rgb(game["ground"]))
    _figure(c, inset + 1, inset + 1, w_px - inset - 1, h_px - inset - 1,
            game["kind"], CB.hex_rgb(game["ink"]),
            CB.hex_rgb(game["border"]), roll)
    return c


def slab_face(game, w_px, h_px, key):
    """A graded card in its slab, seen from above on the case's top shelf: a
    clear holder, the grader's label strip across the top (dashes -- every
    real grader is a real mark and its label is its trade dress) and the
    card inside it."""
    roll = Roll(f"slab|{game['id']}|{key}")
    c = Canvas(w_px, h_px, (214, 218, 222))
    strip = max(3, h_px // 5)
    c.rect(1, 1, w_px - 1, strip, (242, 242, 238))
    _dashes(c, 3, 2, w_px - 3, strip - 1, roll, (60, 62, 70))
    m = max(1, w_px // 12)
    inner = card_face(game, max(4, w_px - 2 * m), max(4, h_px - strip - 2 * m), key)
    c.paste(inner, m, strip + m)
    _frame(c, 0, 0, w_px, h_px, 1, (170, 176, 182))
    return c


# --- the atlas ---------------------------------------------------------------


def uv_rect(rect, size):
    """glTF UVs for a pixel rect in an atlas whose row 0 is the top."""
    x0, y0, x1, y1 = rect
    W, H = size
    return (x0 / W, 1.0 - y1 / H, x1 / W, 1.0 - y0 / H)


def atlas(tiles, name_prefix="cardshop"):
    """Shelf-pack ``[(key, Canvas), ...]`` into one raster.

    Returns ``{"canvas", "size", "rects", "name"}``; ``rects`` maps each key
    to its pixel box. The pack order is the list's, so the same tiles in the
    same order give the same atlas -- and the NAME is a digest of the
    finished pixels, so two specimens whose art happens to be identical
    share one image in the .blend and one in the GLB.
    """
    if not tiles:
        return None
    width = max(ATLAS_W, max(t.w for _k, t in tiles) + 2 * GUTTER)
    rows, cur, x, row_h = [], [], GUTTER, 0
    for key, tile in tiles:
        if x + tile.w + GUTTER > width and cur:
            rows.append((cur, row_h))
            cur, x, row_h = [], GUTTER, 0
        cur.append((key, tile, x))
        x += tile.w + GUTTER
        row_h = max(row_h, tile.h)
    if cur:
        rows.append((cur, row_h))
    height = GUTTER + sum(h + GUTTER for _r, h in rows)
    c = Canvas(width, height, (16, 16, 18))
    rects, y = {}, GUTTER
    for row, h in rows:
        for key, tile, x in row:
            c.paste(tile, x, y)
            rects[key] = (x, y, x + tile.w, y + tile.h)
        y += h + GUTTER
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (width, height), "rects": rects,
            "name": f"{name_prefix}_{width}x{height}_{digest:08x}"}


def paint(spec):
    """One tile from a planner's spec dict. The planners describe tiles in
    METRES and this is the only place that turns them into pixels, so a
    change to `TEXEL` moves every tile at once and no planner carries a
    pixel size."""
    w = max(4, int(round(float(spec["w_m"]) * TEXEL)))
    hgt = max(4, int(round(float(spec["h_m"]) * TEXEL)))
    kind = spec["kind"]
    key = spec.get("key", "")
    maker = next((m for m in CB.MAKERS if m["id"] == spec.get("maker")), None)
    # THE FLAT ART (0.98.0) -- posters, banners, ceiling hangers, aisle signs
    # and playmats -- is painted in `flat_art`, which imports THIS module for
    # its Canvas, its rolls and its ink helpers. The import is local because
    # of that cycle and for no other reason: `paint` stays the one dispatcher
    # a planner calls, so a planner never chooses between two painters and
    # `recipes/_card_atlas.py` needs no second door.
    if kind in FLAT_KINDS:
        from . import flat_art as FA
        return FA.paint(spec, w, hgt)
    if kind == "label":
        return storage_label(maker or CB.MAKERS[0], w, hgt,
                             spec.get("says", ""), key)
    # AN UNKNOWN KIND FAILS HERE AND NOT FIVE LINES LOWER. The line below
    # reads `spec["game"]`, so before 0.98.0 an unrecognised kind raised
    # KeyError('game') -- which is a failure, but one that names the wrong
    # thing and sends the reader after a missing field instead of a typo in
    # the kind. The ValueError at the bottom could never fire for a spec
    # that had no game.
    if kind not in ("box", "header", "tin", "slab", "card"):
        raise ValueError(f"card_art.paint: unknown tile kind {kind!r}")
    game = CB.BY_ID[spec["game"]]
    if kind == "box":
        return box_face(game, w, hgt, key, maker)
    if kind == "header":
        return header_sign(game, w, hgt)
    if kind == "tin":
        return tin_lid(game, w, hgt, key)
    if kind == "slab":
        return slab_face(game, w, hgt, key)
    if kind == "card":
        return card_face(game, w, hgt, key)
    raise ValueError(f"card_art.paint: unknown tile kind {kind!r}")


def build_atlas(tiles, name_prefix="cardshop"):
    """Paint a planner's ``tiles`` mapping into one atlas.

    The tiles are packed in SORTED key order rather than dict order, so the
    atlas's bytes -- and therefore its name -- depend on what is in it and
    not on the order the planner happened to discover it in. Two specimens
    that stock the same products share one image.
    """
    return atlas([(k, paint(tiles[k])) for k in sorted(tiles)], name_prefix)


def painted_strings(games=None, makers=None, teams=None, says=None,
                    aisle=None):
    """Every string this module can paint, for the denylist test. It is
    deliberately built from the ART's inputs and not from `card_brands`'
    tables: the two are the same set today and stop being the same set the
    moment somebody letters something new.

    0.98.0: `aisle` is `card_brands.AISLE_SAYS`, which `flat_art` letters on
    an aisle sign. It is here and not in a second function because the whole
    point of this one is that ONE list is what the denylist test walks --
    the flat art paints through `paint` and must be held by the same guard.
    """
    out = []
    for g in (games if games is not None else CB.GAMES):
        out += [g["name"], g["short"], g["slogan"]]
    for m in (makers if makers is not None else CB.MAKERS):
        out += [m["name"], m["short"]]
    for t in (teams if teams is not None else CB.TEAMS):
        out.append(t[0])
    out += list(says if says is not None else CB.SHOP_SAYS)
    out += list(aisle if aisle is not None else CB.AISLE_SAYS)
    return tuple(out)
