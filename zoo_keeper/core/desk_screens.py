"""What a desk's computer is showing, decided and painted in pure Python (Zoo 1.115.0; the factory's roadmap 148).

The walker's look review, 2026-10-19, on the factory's interiors: "Too sparse" -- "computer screens hsould be
on...bring life to this dead world". Every desk monitor `_surface_stock._monitor` built showed a dark plastic face
(the ``screen`` finish, linear 0.02-0.03): a machine that is off, in every office of every level. This paints what a
1997 office's machines were showing, so the screen can be lit (`prim_mesh.build_stock` builds it on a backlit
``_Face`` material, which Lux's power cut turns off with the lights).

THE APPS, one 4:3 raster each -- invented software with Delco-flavoured names, never a real product, publisher or
logo (`tests/test_desk_screens.py` holds a denylist over every string painted):

  * ``word``  -- a word processor, full screen: blue ground, white lines of text, a status row at the foot.
  * ``sheet`` -- a spreadsheet: a pale grid with column letters and row numbers, figures in the cells, one cell
    highlighted, a status row.
  * ``desk``  -- a desktop: a teal ground, a grey program window with a title bar and a grid of icons, a second
    window behind it.
  * ``term``  -- a terminal: black, green lines of text and a block cursor.
  * ``amber`` -- a bulletin board on an amber phosphor: a header, a menu, a prompt.
  * ``stars`` -- a screensaver: black with stars, some brighter than others.

The text is never legible at a desk's distance and is not meant to be: lines are bars of ink in the app's colours,
the one or two words in the face (`pixel_type`'s 8 px ``small`` face) are its title and its prompt. A screen is
painted crisp, blurred once, then given the bar TV's tube: every other row dimmed, the corners darkened, a phosphor's
cast (`crt_screens._tube`). Integer and float arithmetic only, rounded once: the same bytes on every build.

WHICH APP a monitor shows is `pick_app`'s: a hash of where the monitor stands on its top, so the stock's random
stream -- which places every other item on the top -- is not drawn from. Desks of different builds show a mix;
the copies of one module (one stem, `kit.module_stem`) show its one app. Cold run 9349's office stood 9 desks on
7 modules.
"""
from __future__ import annotations

import zlib

from . import crt_screens as CS
from . import pixel_type as pt

APPS = ("word", "sheet", "desk", "term", "amber", "stars")
#: The raster's width; its height follows the screen's own aspect (`paint`).
W = 128
FACE = "small"

#: Every string a screen paints, by app. Invented; the denylist test reads this.
STRINGS = {
    "word": ("JAWN.DOC  PG 1 LN 4",),
    "sheet": ("WOODERCALC", "READY", "ABCDEF"),
    "desk": ("HOAGIE SHELL",),
    "term": ("C:\\YO>",),
    "amber": ("SCRAPPLE BBS", "MAIN MENU"),
    "stars": (),
}

BLUE = (24, 40, 150)
WHITE = (226, 228, 232)
GREY = (172, 174, 178)
DARK_GREY = (96, 98, 104)
TEAL = (24, 128, 128)
GREEN = (60, 220, 90)
AMBER = (240, 168, 40)
BLACK = (6, 8, 10)
NAVY = (16, 24, 96)
PAPER = (232, 232, 224)
GRID = (150, 154, 166)
HILITE = (40, 60, 170)


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def pick_app(x, y, salt=""):
    """The app the monitor standing at ``(x, y)`` (metres, its host's frame) shows: a hash of where it stands,
    rounded to the millimetre, so the same desk always shows the same thing and the stock stream is untouched."""
    return APPS[_h("desk_screen", salt, int(round(float(x) * 1000)), int(round(float(y) * 1000))) % len(APPS)]


def _text(img, s, x, y, rgb):
    img.mask(pt.render(s, 1, FACE), x, y, rgb)


def _bars(img, x0, y0, x1, rows, pitch, rgb, key, min_frac=0.35):
    """`rows` lines of text as bars of ink: each a run of words, each word a bar."""
    for r in range(rows):
        y = y0 + r * pitch
        span = int((x1 - x0) * (min_frac + (1.0 - min_frac) * ((_h(key, "row", r) % 1000) / 1000.0)))
        x = x0
        w = 0
        while x < x0 + span:
            w = 3 + _h(key, r, x) % 9
            img.rect(x, y, min(x + w, x0 + span), y + 2, rgb)
            x += w + 2


def _word(img, key):
    img.rect(0, 0, img.w, img.h, BLUE)
    _bars(img, 4, 5, img.w - 6, (img.h - 16) // 4, 4, WHITE, key)
    img.rect(0, img.h - 9, img.w, img.h, NAVY)
    _text(img, STRINGS["word"][0], 2, img.h - 9, GREY)


def _sheet(img, key):
    img.rect(0, 0, img.w, img.h, PAPER)
    img.rect(0, 0, img.w, 9, HILITE)
    _text(img, STRINGS["sheet"][0], 2, 0, WHITE)
    cols, cw, rh, top, left = 6, (img.w - 10) // 6, 7, 18, 10
    for c in range(cols):
        _text(img, STRINGS["sheet"][2][c], left + c * cw + cw // 2 - 2, 9, DARK_GREY)
    rows = (img.h - top - 10) // rh
    for r in range(rows + 1):
        img.rect(left, top + r * rh, img.w, top + r * rh + 1, GRID)
    for c in range(cols + 1):
        img.rect(left + c * cw, top, left + c * cw + 1, top + rows * rh, GRID)
    for r in range(rows):
        img.rect(1, top + r * rh + 2, 7, top + r * rh + 4, DARK_GREY)
        for c in range(cols):
            if _h(key, "cell", r, c) % 3:
                w = 4 + _h(key, "w", r, c) % (cw - 6)
                img.rect(left + (c + 1) * cw - 2 - w, top + r * rh + 3, left + (c + 1) * cw - 2,
                         top + r * rh + 5, BLACK)
    hr, hc = _h(key, "hr") % rows, _h(key, "hc") % cols
    img.rect(left + hc * cw + 1, top + hr * rh + 1, left + (hc + 1) * cw, top + (hr + 1) * rh, HILITE)
    img.rect(0, img.h - 9, img.w, img.h, GREY)
    _text(img, STRINGS["sheet"][1], 2, img.h - 9, BLACK)


def _window(img, x0, y0, x1, y1, title, key):
    img.rect(x0, y0, x1, y1, GREY)
    img.rect(x0, y0, x1, y0 + 9, NAVY)
    if title:
        _text(img, title, x0 + 3, y0, WHITE)
    img.rect(x0 + 2, y0 + 11, x1 - 2, y1 - 2, WHITE)
    for r in range(2):
        for c in range(4):
            ix, iy = x0 + 8 + c * ((x1 - x0 - 12) // 4), y0 + 15 + r * 18
            if iy + 10 < y1 - 2:
                img.rect(ix, iy, ix + 8, iy + 8, (40 + _h(key, r, c) % 160, 60, 120 + _h(key, c) % 120))
                img.rect(ix - 1, iy + 10, ix + 9, iy + 12, DARK_GREY)


def _desk(img, key):
    img.rect(0, 0, img.w, img.h, TEAL)
    _window(img, img.w // 2, 6, img.w - 6, img.h // 2 + 6, "", key + "b")
    _window(img, 6, img.h // 4, img.w - 22, img.h - 8, STRINGS["desk"][0], key)


def _term(img, key):
    img.rect(0, 0, img.w, img.h, BLACK)
    rows = (img.h - 14) // 5
    _bars(img, 3, 3, img.w - 20, rows, 5, GREEN, key, min_frac=0.15)
    _text(img, STRINGS["term"][0], 3, img.h - 11, GREEN)
    img.rect(3 + pt.width(STRINGS["term"][0], 1, FACE) + 1, img.h - 9, 3 + pt.width(STRINGS["term"][0], 1, FACE) + 6,
             img.h - 3, GREEN)


def _amber(img, key):
    img.rect(0, 0, img.w, img.h, BLACK)
    _text(img, STRINGS["amber"][0], 4, 2, AMBER)
    img.rect(4, 12, img.w - 4, 13, AMBER)
    _text(img, STRINGS["amber"][1], 4, 16, AMBER)
    _bars(img, 10, 28, img.w - 30, (img.h - 40) // 6, 6, AMBER, key, min_frac=0.3)
    img.rect(4, img.h - 8, 10, img.h - 3, AMBER)


def _stars(img, key):
    img.rect(0, 0, img.w, img.h, BLACK)
    n = img.w * img.h // 60
    for k in range(n):
        x, y = _h(key, "x", k) % img.w, _h(key, "y", k) % img.h
        v = 90 + _h(key, "v", k) % 166
        # one pixel in three of the brightest is a 2 x 2 star: the blur takes a lone pixel down to a third
        if v > 200:
            img.rect(x, y, x + 2, y + 2, (v, v, v))
        else:
            img.set(x, y, (v, v, v))


PAINTERS = {"word": _word, "sheet": _sheet, "desk": _desk, "term": _term, "amber": _amber, "stars": _stars}


def paint(spec):
    """One app's screen from a planner's tile spec: ``{"kind": "desk_screen", "app", "w_m", "h_m"}``. Returns the
    `vending_forms.Canvas` the card atlas packs. An unknown app raises, naming the apps there are."""
    app = spec.get("app")
    if app not in PAINTERS:
        raise ValueError(f"desk_screens.paint: no app {app!r}; the apps are {', '.join(APPS)}")
    w = W
    h = max(24, int(round(W * float(spec["h_m"]) / float(spec["w_m"]))))
    img = CS._Img(w, h, BLACK)
    PAINTERS[app](img, f"{app}:{w}x{h}")
    img.blur(1)
    CS._tube(img)
    return img.to_canvas()


def painted_strings():
    """Every string any app paints, for the denylist test."""
    return [s for app in APPS for s in STRINGS[app]]
