"""What a bar dartboard looks like, painted in pure Python: the bristle board
and the two chalkboards inside the cabinet doors.

Zoo 0.91.0. The walker, 2026-09-15, with two photos: "we also need dart
boards in the strip clubs. The kind where you use chalk to keep your score".
The first photo is a wall cabinet with its doors swung open -- a bristle
board on a felt backing, and inside each door a chalkboard with a painted
cricket grid and a dart rail. The second is one of those doors close up, the
grid covered in real chalk: tallies, slashes, X's, a circled number, "x2",
an erased smudge.

TWO RASTERS, one per material:

  * THE BOARD, `BOARD_PX` square: the twenty sectors in the regulation order
    from 20 at the top, clockwise; black and cream singles; the treble and
    double rings red on a black sector and green on a cream one; the green
    outer bull and the red bull; a silver spider on every boundary; the
    numbers upright in the black band outside the doubles; and the invented
    brand along the bottom of the rim. Radii are the regulation board's
    (`RADII_MM`), so the rings are where a player expects them. The sisal is
    grain noise on every pixel, and the board is worn where a bar throws --
    pocked round treble 20, the bull and the misses beside 20 -- more on a
    later variant.
  * THE CHALK, two door panels side by side: a painted frame and header
    (the brand, then HOME / AWAY or 01 / 01), a centre column of boxed
    numbers 20 to 15 and a bull, and the chalk -- a game in progress drawn
    from the variant (`CHALK_STAGES`): wiped, the first rounds, mid-game,
    and a finished game with the scores run up. Chalk is grainy and broken,
    paint is solid, and that is the whole difference between the two.

THE BRANDS ARE INVENTED (`BRANDS`) and never a real dart maker's mark;
`DENYLIST` is the guard `tests/test_dartboard.py` holds every string on
both rasters against. It is a guard and not a proof.

Integer arithmetic on bytes, `zlib.crc32` for every random draw, and one
`math.atan2` per board pixel quantised to a sector index: the same bytes in
Blender's Python and a test's. The lettering is Pixel Operator Bold
(`pixel_type`) and the PNG writer is the vending machine's
(`vending_forms.Canvas`).

Frame of the rasters: row 0 at the top, as a PNG is stored; a module maps
v = 1 at row 0 (`uv_of`).
"""
from __future__ import annotations

import math
import re
import zlib

from . import pixel_type as pt
from .vending_forms import Canvas

# --- the board -------------------------------------------------------------------

#: The board's diameter in metres (a regulation bristle board is 451 mm)...
BOARD_D = 0.451
#: ...painted at this many pixels across: a 1.13 mm pixel, so a double ring's
#: 8 mm is seven pixels and a number 16 mm tall is legible at 1.5 m.
BOARD_PX = 400
#: Regulation radii, millimetres from the centre: bull, outer bull, the
#: treble ring's inner and outer wire, the double ring's inner and outer
#: wire, and the board's edge.
RADII_MM = {"bull": 6.35, "outer_bull": 15.9, "treble_in": 99.0, "treble_out": 107.0,
            "double_in": 162.0, "double_out": 170.0, "edge": 225.5}
#: Clockwise from the top.
SECTORS = (20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5)
#: The numbers' centres, and the brand's baseline radius, in millimetres.
NUMBER_R_MM = 190.0
BRAND_R_MM = 214.0

BLACK = (24, 22, 20)
CREAM = (222, 204, 162)
RED = (178, 34, 32)
GREEN = (26, 112, 58)
WIRE = (176, 176, 170)
BAND = (16, 16, 16)
NUMBER = (232, 230, 222)

#: INVENTED dart makers: the mark round the board and on the door header.
#: Delco talk (jawn, youse, wooder, the Boulevard, the Pike), PG-13. None is,
#: or is meant to evoke, a real dart company or a bar.
BRANDS = (
    {"id": "double_delco", "mark": "DOUBLE DELCO", "tag": "BRISTLE",
     "ink": (232, 196, 80)},
    {"id": "macdade_bristle", "mark": "MACDADE BRISTLE", "tag": "CO.",
     "ink": (226, 226, 214)},
    {"id": "jawn_board", "mark": "THE JAWNBOARD", "tag": "PRO",
     "ink": (220, 64, 50)},
    {"id": "youse_throw", "mark": "YOUSE THROW", "tag": "LIKE MY NAN",
     "ink": (120, 186, 226)},
    {"id": "pike_pro", "mark": "BALTIMORE PIKE PRO", "tag": "TOURNAMENT",
     "ink": (232, 196, 80)},
    {"id": "wooder_ice", "mark": "WOODER ICE HOUSE", "tag": "LEAGUE",
     "ink": (226, 226, 214)},
)
BY_ID = {b["id"]: b for b in BRANDS}
IDS = tuple(b["id"] for b in BRANDS)

#: Real marks nothing painted here may contain (upper case, substrings):
#: dart and board makers a writer reaches for, and the local brands and
#: teams the factory's other tables already deny.
DENYLIST = (
    "HARROWS", "WINMAU", "UNICORN", "BOTTELSEN", "NODOR", "TARGET", "VIPER",
    "ARACHNID", "HALEX", "RED DRAGON", "BULL'S", "BULLS", "PUMA", "ACCUDART",
    "LASER", "DARTMASTER", "ELKADART", "COSMO", "L-STYLE", "BLADE", "DIAMOND",
    "SHOT", "MISSION", "ONE80", "GLD", "DATADART", "DMI", "PENTATHLON",
    "WAWA", "TASTYKAKE", "EAGLES", "FLYERS", "PHILLIES", "SIXERS", "YUENGLING",
    "LOU TURK",
)

# --- the chalkboards ----------------------------------------------------------------

#: Pixels per metre of a door's chalk panel: a 2 mm pixel, the numbers at
#: twice the face (18 px cap, 36 mm).
CHALK_TEXEL = 512
SLATE = (30, 33, 31)
PAINT = (214, 210, 190)
CHALK = (236, 236, 228)
#: What the cricket grid's rows say, top to bottom under the header.
ROWS = ("20", "19", "18", "17", "16", "15", "B")
#: A game at four stages, one per module variant: how many marks each
#: player column may carry per row (0 to 3, 3 closed and circled), how many
#: points are written in the margin, the erased patches, and whether a
#: "x2" is scrawled.
CHALK_STAGES = (
    {"id": "wiped", "marks": 0, "points": 0, "smudges": 3, "x2": False, "ghost": 0.10},
    {"id": "first_rounds", "marks": 1, "points": 1, "smudges": 1, "x2": False, "ghost": 0.06},
    {"id": "mid_game", "marks": 2, "points": 2, "smudges": 1, "x2": True, "ghost": 0.05},
    {"id": "late_game", "marks": 3, "points": 3, "smudges": 2, "x2": True, "ghost": 0.07},
)


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def _blend(c, x, y, rgb, a255):
    """Blend ``rgb`` over pixel (x, y) at alpha a255/255, integers only."""
    if not (0 <= x < c.w and 0 <= y < c.h) or a255 <= 0:
        return
    i = (y * c.w + x) * 3
    b = c.buf
    inv = 255 - a255
    b[i] = (b[i] * inv + rgb[0] * a255 + 127) // 255
    b[i + 1] = (b[i + 1] * inv + rgb[1] * a255 + 127) // 255
    b[i + 2] = (b[i + 2] * inv + rgb[2] * a255 + 127) // 255


# --- picking ------------------------------------------------------------------------

_VARIANT = re.compile(r"_n\d+(?=_|$)")


def brand_order(key):
    """Every brand, in the order a module keyed ``key`` walks its variants."""
    return sorted(IDS, key=lambda i: (_h(key, i), i))


def pick(plan):
    """``(brand_id, variant, key)`` for a plan: an explicit ``params.brand``
    wins; a module takes index ``variant`` of `brand_order` keyed by its
    stem WITHOUT the variant suffix, so a slot's variants are four brands;
    anything else is variant 0 of the first order."""
    params = plan.get("params") or {}
    module = plan.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    key = _VARIANT.sub("", module.get("stem") or "") or "dartboard"
    asked = params.get("brand")
    if asked in BY_ID:
        return asked, variant, key
    return brand_order(key)[variant % len(IDS)], variant, key


# --- the board ----------------------------------------------------------------------

def sector_at(dx_mm, dy_mm):
    """The sector number at an offset from the centre, x right, y UP."""
    a = math.degrees(math.atan2(dx_mm, dy_mm))       # 0 at the top, clockwise
    k = int(math.floor((a + 9.0) / 18.0)) % 20
    return SECTORS[k]


def region_at(dx_mm, dy_mm):
    """``(ring, sector)``: ring is bull, outer_bull, single, treble, double,
    band or off (past the edge)."""
    r = math.hypot(dx_mm, dy_mm)
    R = RADII_MM
    if r <= R["bull"]:
        return "bull", None
    if r <= R["outer_bull"]:
        return "outer_bull", None
    if r > R["edge"]:
        return "off", None
    s = sector_at(dx_mm, dy_mm)
    if R["treble_in"] <= r <= R["treble_out"]:
        return "treble", s
    if R["double_in"] <= r <= R["double_out"]:
        return "double", s
    if r > R["double_out"]:
        return "band", s
    return "single", s


def _dark_sector(s):
    """20 is a black sector, and they alternate round the board."""
    return SECTORS.index(s) % 2 == 0


def _base_colour(ring, s):
    if ring == "bull":
        return RED
    if ring == "outer_bull":
        return GREEN
    if ring in ("band", "off"):
        return BAND
    dark = _dark_sector(s)
    if ring == "single":
        return BLACK if dark else CREAM
    return RED if dark else GREEN


#: Where a bar's darts land, as (sector, ring, weight): the treble 20 and its
#: neighbours, the bull, and the singles either side.
_WEAR_SPOTS = ((20, "treble", 5), (20, "single", 4), (1, "single", 2), (5, "single", 2),
               (None, "outer_bull", 3), (19, "treble", 2), (19, "single", 1), (3, "double", 1))


def _spot_centre(sector, ring):
    if sector is None:
        return 0.0, 0.0
    R = RADII_MM
    r = {"treble": (R["treble_in"] + R["treble_out"]) / 2.0,
         "double": (R["double_in"] + R["double_out"]) / 2.0,
         "single": 135.0}[ring]
    a = math.radians(SECTORS.index(sector) * 18.0)
    return r * math.sin(a), r * math.cos(a)


def paint_board(brand_id, variant=0, key=""):
    """The board's raster. Returns (canvas, facts)."""
    brand = BY_ID[brand_id]
    n = BOARD_PX
    mm = BOARD_D * 1000.0 / n                       # millimetres per pixel
    c = Canvas(n, n, BAND)
    half = n / 2.0
    wear = int(variant) % 4
    grain = 10 + 3 * wear
    for py in range(n):
        dy = (half - (py + 0.5)) * mm
        for px in range(n):
            dx = ((px + 0.5) - half) * mm
            ring, s = region_at(dx, dy)
            col = _base_colour(ring, s)
            # the sisal: coarse fibres run radially, so grain is keyed on the
            # pixel's angle bucket as well as the pixel
            hh = _h(brand_id, px, py)
            g = (hh & 0xFF) * grain // 255 - grain // 2
            if ring not in ("band", "off"):
                fib = (_h("fibre", int(math.atan2(dx, dy) * 90.0), int(math.hypot(dx, dy) // 3))
                       & 0x1F) - 15
                g += fib // 3
            c.px(px, py, tuple(max(0, min(255, v + g)) for v in col))
    # the spider: every ring wire and sector wire, one silver pixel
    R = RADII_MM
    for key_r in ("outer_bull", "treble_in", "treble_out", "double_in", "double_out"):
        r = R[key_r] / mm
        steps = int(2 * math.pi * r * 2) + 8
        for k in range(steps):
            a = 2 * math.pi * k / steps
            c.px(int(half + r * math.sin(a)), int(half - r * math.cos(a)), WIRE)
    c.px(int(half), int(half), WIRE)
    for k in range(20):
        a = math.radians(k * 18.0 + 9.0)
        for j in range(int(R["outer_bull"] / mm), int(R["double_out"] / mm) + 1):
            c.px(int(half + j * math.sin(a)), int(half - j * math.cos(a)), WIRE)
    # the pocks: dark holes where the darts land, more on a later variant
    holes = 0
    for sec, ring, weight in _WEAR_SPOTS:
        cx, cy = _spot_centre(sec, ring)
        for k in range(weight * (6 + 10 * wear)):
            hh = _h(key, brand_id, "pock", sec, ring, k)
            ox = ((hh & 0x3FF) / 1023.0 - 0.5) * (8.0 if ring == "treble" else 22.0)
            oy = (((hh >> 10) & 0x3FF) / 1023.0 - 0.5) * (8.0 if ring == "treble" else 22.0)
            x = int(half + (cx + ox) / mm)
            y = int(half - (cy + oy) / mm)
            a = 120 + ((hh >> 20) & 0x3F)
            _blend(c, x, y, (6, 6, 6), a)
            if (hh >> 26) & 1:
                _blend(c, x + 1, y, (6, 6, 6), a // 2)
                _blend(c, x, y + 1, (6, 6, 6), a // 2)
            holes += 1
        if wear >= 2:
            # the sisal round a treble goes grey: a hundred nights of it,
            # thinning out from where the darts land
            rr = 16.0 if ring != "treble" else 11.0
            for k in range(60 * wear):
                hh = _h(key, "fade", sec, ring, k)
                ox = ((hh & 0xFF) / 255.0 - 0.5) * 2.0 * rr
                oy = (((hh >> 8) & 0xFF) / 255.0 - 0.5) * 2.0 * rr
                d = (ox * ox + oy * oy) / (rr * rr)
                if d > 1.0:
                    continue
                _blend(c, int(half + (cx + ox) / mm), int(half - (cy + oy) / mm),
                       (128, 122, 108), int(70 * (1.0 - d)))
    # the numbers, upright, in the band
    numbers = []
    for k, num in enumerate(SECTORS):
        a = math.radians(k * 18.0)
        m = pt.trim(pt.render(str(num), 2))
        cx = half + (NUMBER_R_MM / mm) * math.sin(a)
        cy = half - (NUMBER_R_MM / mm) * math.cos(a)
        ox, oy = int(round(cx - len(m[0]) / 2.0)), int(round(cy - len(m) / 2.0))
        c.mask(m, ox, oy, NUMBER)
        numbers.append((num, ox, oy, len(m[0]), len(m)))
    # the brand along the bottom of the rim, a glyph at a time, upright
    text = brand["mark"]
    widths = [pt.ink_width(ch, 1) if ch != " " else 4 for ch in text]
    total = sum(widths) + (len(text) - 1)
    r_px = BRAND_R_MM / mm
    arc = total / r_px                              # radians the text spans
    x_run = 0.0
    for ch, wch in zip(text, widths):
        if ch != " ":
            t = (x_run + wch / 2.0) / r_px - arc / 2.0
            ang = math.pi + (-t)                     # the bottom, left to right
            m = pt.trim(pt.render(ch, 1))
            cx = half + r_px * math.sin(ang)
            cy = half - r_px * math.cos(ang)
            c.mask(m, int(round(cx - len(m[0]) / 2.0)), int(round(cy - len(m) / 2.0)),
                   brand["ink"])
        x_run += wch + 1
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return c, {"brand": brand_id, "mark": text, "numbers": numbers, "pocks": holes,
               "arc_deg": math.degrees(arc),
               "name": f"dartboard_{brand_id}_v{wear}_{n}_{digest:08x}"}


def board_uv(dx_m, dy_m):
    """(u, v) of a point on the board's face, metres from its centre, x right
    and y up, clamped to the raster."""
    u = 0.5 + dx_m / BOARD_D
    v = 0.5 + dy_m / BOARD_D
    return (min(1.0, max(0.0, u)), min(1.0, max(0.0, v)))


#: A pixel in the black band, for every face of the board that is not its
#: front (the side and back are the band's black).
BOARD_DARK_UV = (0.5, 1.0 / BOARD_PX)


# --- the chalkboards -----------------------------------------------------------------

def _stroke(c, x0, y0, x1, y1, seed, width=2, grain=90, rgb=CHALK, alpha=220):
    """A chalk line: broken, grainy, a little wider in the middle."""
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for k in range(n + 1):
        t = k / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for oy in range(-(width // 2), width - width // 2):
            for ox in range(-(width // 2), width - width // 2):
                hh = _h(seed, int(x) + ox, int(y) + oy)
                if (hh & 0xFF) < grain:
                    continue
                _blend(c, int(x) + ox, int(y) + oy, rgb, alpha * ((hh >> 8) & 0xFF) // 255)


def _ring(c, cx, cy, r, seed, width=2):
    steps = max(16, int(2 * math.pi * r * 1.5))
    pts = []
    for k in range(steps + 2):
        a = 2 * math.pi * k / steps + 0.4
        wob = 1.0 + ((_h(seed, k // 4) & 0xFF) / 255.0 - 0.5) * 0.12
        pts.append((cx + r * wob * math.cos(a), cy + r * wob * math.sin(a)))
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        _stroke(c, xa, ya, xb, yb, seed, width=width)


def _chalk_text(c, text, x, y, seed, scale=2):
    """Handwriting, as the pixel face jittered a pixel per glyph with grain."""
    ox = x
    for i, ch in enumerate(text):
        m = pt.render(ch, scale)
        jx = (_h(seed, i, "jx") & 3) - 1
        jy = (_h(seed, i, "jy") & 3) - 1
        for yy, row in enumerate(m):
            for xx, v in enumerate(row):
                if v:
                    hh = _h(seed, i, xx, yy)
                    if (hh & 0xFF) < 70:
                        continue
                    _blend(c, ox + xx + jx, y + yy + jy, CHALK, 150 + ((hh >> 8) & 0x5F))
        ox += pt.width(ch, scale)


def _smudge(c, cx, cy, rx, ry, seed, strength):
    """An erased patch: a pale cloud with the eraser's streaks through it."""
    for yy in range(int(cy - ry), int(cy + ry) + 1):
        for xx in range(int(cx - rx), int(cx + rx) + 1):
            dx, dy = (xx - cx) / max(1.0, rx), (yy - cy) / max(1.0, ry)
            d = dx * dx + dy * dy
            if d > 1.0:
                continue
            hh = _h(seed, xx, yy)
            streak = 1.0 if (yy + (hh & 3)) % 5 < 2 else 0.6
            a = int(strength * 255 * (1.0 - d) * streak)
            _blend(c, xx, yy, (150, 152, 146), a)


def panel_layout(pw, ph):
    """The painted grid of one door panel, in pixels: the header's height,
    each row's top, the three columns' x edges."""
    frame = max(3, pw // 40)
    head = int(ph * 0.17)
    names = int(ph * 0.09)
    top = frame + head + names
    row_h = (ph - frame - top) // len(ROWS)
    col_w = (pw - 2 * frame) // 3
    xs = (frame, frame + col_w, frame + 2 * col_w, pw - frame)
    return {"frame": frame, "head": head, "names": names, "top": top, "row_h": row_h,
            "xs": xs}


def paint_panel(brand_id, pw, ph, variant, key, door):
    """One door's chalkboard. ``door`` is "L" or "R". Returns (canvas, facts)."""
    brand = BY_ID[brand_id]
    stage = CHALK_STAGES[int(variant) % len(CHALK_STAGES)]
    c = Canvas(pw, ph, SLATE)
    seed = f"{key}:{brand_id}:{variant}:{door}"
    # slate grain, and the ghosts of every game wiped before this one
    for y in range(ph):
        for x in range(pw):
            hh = _h(seed, "slate", x, y)
            g = (hh & 0xF) - 7
            if g:
                p = c.get(x, y)
                c.px(x, y, tuple(max(0, min(255, v + g)) for v in p))
    for k in range(int(stage["ghost"] * 400)):
        hh = _h(seed, "ghost", k)
        x, y = hh % pw, (hh >> 12) % ph
        _smudge(c, x, y, 4 + (hh >> 24) % 9, 2 + (hh >> 28) % 4, (seed, "g", k), 0.10)
    L = panel_layout(pw, ph)
    fr, xs = L["frame"], L["xs"]
    # the painted frame and grid
    c.rect(0, 0, pw, fr, PAINT)
    c.rect(0, ph - fr, pw, ph, PAINT)
    c.rect(0, 0, fr, ph, PAINT)
    c.rect(pw - fr, 0, pw, ph, PAINT)
    hb = fr + L["head"]
    c.rect(fr, hb - 2, pw - fr, hb, PAINT)
    c.rect(fr, L["top"] - 2, pw - fr, L["top"], PAINT)
    for x in xs[1:3]:
        c.rect(x - 1, hb, x + 1, ph - fr, PAINT)
    painted = []
    # the header: the brand, set as large as fits, and its tag under it
    words = brand["mark"]
    s = max(1, min(2, pt.fit_scale(words, pw - 2 * fr - 6)))
    lines = pt.wrap(words, pw - 2 * fr - 6, s) or [words]
    yy = fr + 3
    for line in lines[:2]:
        m = pt.trim(pt.render(line, s))
        c.mask(m, (pw - len(m[0])) // 2, yy, brand["ink"])
        painted.append(line)
        yy += len(m) + 3
    tag = brand["tag"]
    if yy + 10 <= hb - 2 and pt.ink_width(tag, 1) <= pw - 2 * fr - 4:
        m = pt.trim(pt.render(tag, 1))
        c.mask(m, (pw - len(m[0])) // 2, yy + 1, PAINT)
        painted.append(tag)
    heads = ("HOME", "AWAY") if int(variant) % 2 == 0 else ("01", "01")
    for col, text in ((0, heads[0]), (2, heads[1])):
        m = pt.trim(pt.render(text, 1))
        x0, x1 = xs[col], xs[col + 1]
        c.mask(m, (x0 + x1 - len(m[0])) // 2, hb + (L["names"] - len(m)) // 2, PAINT)
        painted.append(text)
    # the centre column: boxed numbers and a bull
    rh = L["row_h"]
    for i, label in enumerate(ROWS):
        y0 = L["top"] + i * rh
        c.rect(fr, y0 + rh - 1, pw - fr, y0 + rh, (84, 86, 80))
        bx0, bx1 = xs[1] + 3, xs[2] - 3
        by0, by1 = y0 + 3, y0 + rh - 3
        c.rect(bx0, by0, bx1, by0 + 2, PAINT)
        c.rect(bx0, by1 - 2, bx1, by1, PAINT)
        c.rect(bx0, by0, bx0 + 2, by1, PAINT)
        c.rect(bx1 - 2, by0, bx1, by1, PAINT)
        cx, cy = (bx0 + bx1) // 2, (by0 + by1) // 2
        if label == "B":
            for rr, col in ((min(bx1 - bx0, by1 - by0) // 2 - 4, PAINT),):
                for k in range(96):
                    a = 2 * math.pi * k / 96
                    for w_ in (0, 1):
                        c.px(int(cx + (rr - w_) * math.cos(a)), int(cy + (rr - w_) * math.sin(a)), col)
            c.rect(cx - 2, cy - 2, cx + 2, cy + 2, PAINT)
            painted.append("BULL")
        else:
            m = pt.trim(pt.render(label, 2))
            c.mask(m, cx - len(m[0]) // 2, cy - len(m) // 2, PAINT)
            painted.append(label)
    # the chalk: marks per row per player, stopping short of closing where
    # the stage says so
    marks = {}
    written = []
    for side, col in (("home", 0), ("away", 2)):
        x0, x1 = xs[col], xs[col + 1]
        for i, label in enumerate(ROWS):
            hh = _h(seed, "marks", side, label)
            n = 0
            if stage["marks"]:
                n = (hh % (stage["marks"] + 2))
                n = min(3, n)
                if stage["marks"] == 1:
                    n = min(n, 1 if (hh >> 8) % 3 == 0 else 0)
            marks[(side, label)] = n
            if not n:
                continue
            y0 = L["top"] + i * rh
            cx = (x0 + x1) // 2 + ((hh >> 12) & 7) - 3
            cy = y0 + rh // 2
            r = min(rh // 2 - 4, (x1 - x0) // 2 - 6)
            ms = (seed, side, label)
            _stroke(c, cx - r * 0.6, cy + r * 0.7, cx + r * 0.6, cy - r * 0.7, (ms, 1), width=3)
            if n >= 2:
                _stroke(c, cx - r * 0.6, cy - r * 0.7, cx + r * 0.6, cy + r * 0.7, (ms, 2), width=3)
            if n >= 3:
                _ring(c, cx, cy, r * 0.95, (ms, 3), width=2)
    # points run up in a column's margin, and a "x2" where the stage says
    for k in range(stage["points"]):
        hh = _h(seed, "points", k)
        side_col = 0 if (hh & 1) == 0 else 2
        x0 = xs[side_col] + 3
        y = L["top"] + ((hh >> 4) % len(ROWS)) * rh + 2
        text = str(3 * (1 + (hh >> 8) % 19) + (0 if k == 0 else 9 * k))
        _chalk_text(c, text, x0, y, (seed, "pt", k), scale=1)
        written.append(text)
    if stage["x2"]:
        hh = _h(seed, "x2")
        y = L["top"] + (1 + hh % (len(ROWS) - 2)) * rh + 1
        x = xs[2] + 2 if hh & 16 else xs[0] + 2
        _chalk_text(c, "x2", x, y, (seed, "x2"), scale=1)
        written.append("x2")
    for k in range(stage["smudges"]):
        hh = _h(seed, "smudge", k)
        _smudge(c, fr + hh % max(1, pw - 2 * fr), L["top"] + (hh >> 10) % max(1, ph - L["top"]),
                10 + (hh >> 20) % 14, 5 + (hh >> 26) % 5, (seed, "s", k), 0.55)
    return c, {"door": door, "stage": stage["id"], "marks": marks, "written": written,
               "painted": painted, "heads": heads, "layout": L}


def chalk_art(pw_m, ph_m, brand_id, variant=0, key=""):
    """Both doors' panels side by side on one raster, with a slate patch for
    the panels' edges. Returns ``{canvas, rects, size, facts, name}``: rects
    are pixel boxes (x0, y0, x1, y1), row 0 at the top."""
    pw = max(48, int(round(pw_m * CHALK_TEXEL)))
    ph = max(96, int(round(ph_m * CHALK_TEXEL)))
    W, H = 2 * pw + 2 + 4 + 2, ph
    canvas = Canvas(W, H, SLATE)
    facts = {}
    rects = {}
    for i, door in enumerate(("L", "R")):
        p, f = paint_panel(brand_id, pw, ph, variant, key, door)
        x = i * (pw + 2)
        canvas.paste(p, x, 0)
        rects[door] = (x, 0, x + pw, ph)
        facts[door] = f
    rects["edge"] = (2 * pw + 4, 0, 2 * pw + 8, 4)
    digest = zlib.crc32(bytes(canvas.buf)) & 0xFFFFFFFF
    return {"canvas": canvas, "rects": rects, "size": (W, H), "facts": facts,
            "brand": brand_id, "variant": int(variant) % len(CHALK_STAGES),
            "name": f"chalk_{brand_id}_v{int(variant) % 4}_{W}x{H}_{digest:08x}"}


def uv_of(rect, size, u, v):
    """A point (u, v) in 0..1 of a pixel rect -> the raster's (u, v), v up."""
    x0, y0, x1, y1 = rect
    W, H = size
    return ((x0 + (x1 - x0) * u) / W, 1.0 - (y0 + (y1 - y0) * (1.0 - v)) / H)


def painted_strings(brand_id):
    """Every string a module of this brand paints: for the denylist."""
    b = BY_ID[brand_id]
    return [b["mark"], b["tag"], "HOME", "AWAY", "01"] + list(ROWS)
