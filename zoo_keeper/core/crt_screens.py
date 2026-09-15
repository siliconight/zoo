"""What a bar TV is showing, decided and painted in pure Python: a ballgame.

Zoo 0.90.0. The walker, after walking cold run 9057's strip club: "I also
want the CRTs in the Strip club to have a light/glow from the screen as if
they are on...but we dont have to have a clear image on them...it would be a
football or baseball game tho". So the picture is a 1997 broadcast seen on a
tube over a bar -- soft, low resolution, scanlined, darker at the corners --
and never a clear image.

WHAT IS PAINTED, one 4:3 raster of `W` x `H`:

  * FOOTBALL, from the press box: grass with mowing bands, white yard lines
    converging toward a vanishing point above the frame, the stands above
    the far sideline, and two teams as blobs either side of a line of
    scrimmage. Scene ``line`` is midfield; ``goal_line`` has an end zone in
    the home team's colour.
  * BASEBALL: scene ``pitch`` is the centre-field camera -- the mound and
    the pitcher's back in the foreground, the dirt round home plate up the
    frame with a batter, catcher and umpire, the base paths running out of
    frame; ``wide`` is the high-home shot of the whole diamond with the
    fielders out on it.
  * A SCORE BUG, top left: two rows of an invented team's colour chip,
    abbreviation and score, and the period under them. The teams are
    Delco-flavoured inventions (`TEAMS`) and never a real team, league,
    network or logo; `tests/test_crt_screens.py` holds a denylist.

HOW IT IS MADE SOFT, in this order: the scene is painted crisp and blurred
twice with a separable [1 2 1] kernel, the bug is composited and the whole
frame blurred once more, every other row is dimmed (`SCANLINE`), the frame
is darkened toward its corners (`VIGNETTE`) and given a phosphor's cold
cast (`PHOSPHOR`). Integer and float arithmetic only, rounded once at the
end: the same bytes on every build, in Blender's Python and a test's.

The lettering is the factory's (`pixel_type`, Pixel Operator Bold via
Pixelcoat) and the raster and PNG writer are the vending machine's
(`vending_forms.Canvas`).
"""
from __future__ import annotations

import math
import re
import zlib

from . import pixel_type as pt
from .vending_forms import Canvas

#: The raster: 4:3, a 1.7 mm pixel on the 0.37 m screen of Deli Counter's
#: 0.6 m bracket set -- low resolution by construction, before any blur.
W, H = 224, 168

SPORTS = ("football", "baseball")
SCENES = {"football": ("line", "goal_line"), "baseball": ("pitch", "wide")}

#: Invented teams: abbreviation -> (jersey, trim), sRGB 0..255. Delco slang,
#: the vending brands' neighbourhood: youse, jawn, wooder, scrapple, hoagies,
#: wit (wiz), MacDade mud, down the shore. Jerseys are chosen to read on
#: grass -- no green jersey.
TEAMS = {
    "YOU": ((150, 28, 40), (236, 232, 222)),
    "JAWN": ((238, 238, 232), (30, 40, 110)),
    "WDR": ((120, 170, 225), (245, 245, 245)),
    "SCR": ((200, 92, 32), (40, 30, 25)),
    "HOAG": ((212, 32, 32), (250, 214, 60)),
    "WIT": ((245, 198, 40), (24, 24, 24)),
    "MUD": ((28, 28, 32), (222, 184, 120)),
    "SHOR": ((236, 236, 236), (22, 112, 162)),
}

#: The games: (id, sport, scene, away, home, away score, home score, period).
#: Four of each sport; a module's variant walks them alternating sports
#: (`pick_game`).
GAMES = (
    ("you_jawn", "football", "line", "YOU", "JAWN", 14, 10, "4TH 2:07"),
    ("hoag_wit", "football", "goal_line", "HOAG", "WIT", 21, 17, "2ND 0:48"),
    ("jawn_mud", "football", "goal_line", "JAWN", "MUD", 3, 7, "3RD 9:15"),
    ("shor_you", "football", "line", "SHOR", "YOU", 0, 6, "1ST 11:32"),
    ("wdr_scr", "baseball", "pitch", "WDR", "SCR", 3, 2, "TOP 7"),
    ("mud_shor", "baseball", "wide", "MUD", "SHOR", 5, 4, "BOT 9"),
    ("scr_hoag", "baseball", "pitch", "SCR", "HOAG", 1, 0, "TOP 3"),
    ("wit_wdr", "baseball", "wide", "WIT", "WDR", 8, 6, "BOT 5"),
)
BY_ID = {g[0]: g for g in GAMES}

#: Every other row times this: faint, a tube's line structure and not a
#: venetian blind.
SCANLINE = 0.80
#: Corner darkening: a pixel at normalised radius r (1 at a corner) is
#: multiplied by 1 - VIGNETTE * r^1.5.
VIGNETTE = 0.55
#: A tube's white is cold: per-channel gain.
PHOSPHOR = (0.94, 1.0, 1.06)

GRASS = (46, 116, 50)
GRASS_LIGHT = (60, 134, 58)
DIRT = (150, 104, 68)
CHALK = (226, 226, 216)
WALL = (22, 54, 44)
BUG_BG = (14, 16, 38)
BUG_EDGE = (170, 176, 196)
BUG_INK = (238, 238, 236)
_CROWD = ((58, 48, 54), (92, 72, 60), (40, 42, 62), (118, 100, 88),
          (72, 32, 36), (30, 30, 34), (104, 104, 112))


def _h(*k):
    """A deterministic small hash, for crowd pixels and blob jitter."""
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


# --- picking ---------------------------------------------------------------------

_VARIANT = re.compile(r"_n\d+(?=_|$)")


def game_order(key):
    """Every game, in the order a module keyed ``key`` walks them: the two
    sports alternate, the first sport and each sport's order drawn from the
    key. So variants 0 and 1 of one slot are always different sports, and
    variant 0 of two different stems usually shows two different games."""
    per = {}
    for s in SPORTS:
        per[s] = sorted((g[0] for g in GAMES if g[1] == s),
                        key=lambda i: (_h(key, i), i))
    first = SPORTS[_h(key, "sport") % 2]
    second = SPORTS[1 - SPORTS.index(first)]
    out = []
    for a, b in zip(per[first], per[second]):
        out += [a, b]
    return out


def pick_game(plan, streams=None):
    """The game id a module shows, deterministically: an explicit
    ``params.game`` from the table; for a module, index ``variant`` of
    `game_order` keyed by the stem WITHOUT its variant suffix; for a
    prompt-built specimen, a draw from its own stream."""
    params = plan.get("params") or {}
    asked = params.get("game")
    if asked and asked in BY_ID:
        return asked
    module = plan.get("module") or {}
    stem = module.get("stem")
    if stem:
        order = game_order(_VARIANT.sub("", stem))
        return order[int(module.get("variant") or 0) % len(order)]
    if streams is not None:
        return streams.stream("crt_game").choice([g[0] for g in GAMES])
    return GAMES[0][0]


def bug_lines(game_id):
    """The score bug's text, as it is painted: two team rows and the period."""
    _i, _s, _sc, away, home, a_pts, h_pts, period = BY_ID[game_id]
    return ["%s %d" % (away, a_pts), "%s %d" % (home, h_pts), period]


# --- a float raster ----------------------------------------------------------------


class _Img:
    def __init__(self, w, h, rgb=(0, 0, 0)):
        self.w, self.h = w, h
        self.px = [[float(rgb[0]), float(rgb[1]), float(rgb[2])] for _ in range(w * h)]

    def set(self, x, y, rgb):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y * self.w + x] = [float(rgb[0]), float(rgb[1]), float(rgb[2])]

    def get(self, x, y):
        return self.px[y * self.w + x]

    def ellipse(self, cx, cy, rx, ry, rgb):
        if rx <= 0 or ry <= 0:
            return
        for y in range(int(math.floor(cy - ry)), int(math.ceil(cy + ry)) + 1):
            for x in range(int(math.floor(cx - rx)), int(math.ceil(cx + rx)) + 1):
                dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                if dx * dx + dy * dy <= 1.0:
                    self.set(x, y, rgb)

    def rect(self, x0, y0, x1, y1, rgb):
        for y in range(max(0, int(y0)), min(self.h, int(y1))):
            for x in range(max(0, int(x0)), min(self.w, int(x1))):
                self.px[y * self.w + x] = [float(rgb[0]), float(rgb[1]), float(rgb[2])]

    def line(self, x0, y0, x1, y1, rgb, width=1.0):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        r = max(0.0, (width - 1.0) / 2.0)
        for k in range(n + 1):
            t = k / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if r <= 0.0:
                self.set(x, y, rgb)
            else:
                for yy in range(int(y - r), int(y + r) + 1):
                    for xx in range(int(x - r), int(x + r) + 1):
                        self.set(xx, yy, rgb)

    def mask(self, m, ox, oy, rgb):
        for y, row in enumerate(m):
            for x, v in enumerate(row):
                if v:
                    self.set(ox + x, oy + y, rgb)

    def blur(self, passes=1):
        """Separable [1 2 1] / 4, edges clamped."""
        w, h = self.w, self.h
        for _ in range(passes):
            src = self.px
            tmp = [None] * (w * h)
            for y in range(h):
                base = y * w
                for x in range(w):
                    a = src[base + max(0, x - 1)]
                    b = src[base + x]
                    c = src[base + min(w - 1, x + 1)]
                    tmp[base + x] = [(a[i] + 2.0 * b[i] + c[i]) * 0.25 for i in range(3)]
            out = [None] * (w * h)
            for y in range(h):
                ya, yc = max(0, y - 1) * w, min(h - 1, y + 1) * w
                for x in range(w):
                    a, b, c = tmp[ya + x], tmp[y * w + x], tmp[yc + x]
                    out[y * w + x] = [(a[i] + 2.0 * b[i] + c[i]) * 0.25 for i in range(3)]
            self.px = out

    def to_canvas(self):
        c = Canvas(self.w, self.h)
        buf = c.buf
        for i, p in enumerate(self.px):
            j = i * 3
            buf[j] = min(255, max(0, int(round(p[0]))))
            buf[j + 1] = min(255, max(0, int(round(p[1]))))
            buf[j + 2] = min(255, max(0, int(round(p[2]))))
        return c


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _crowd(img, y0, y1, key):
    for y in range(y0, y1):
        for x in range(img.w):
            c = _CROWD[_h(key, x // 2, y // 2) % len(_CROWD)]
            img.set(x, y, _mix(c, (10, 10, 14), 0.25 + 0.35 * (y1 - y) / max(1, y1 - y0)))


def _player(img, cx, feet_y, height, jersey, trim, back_number=False):
    """A blob: a shadow, a body in the jersey, a helmet or cap in the trim."""
    hgt = max(3.0, height)
    wid = max(2.0, hgt * 0.42)
    img.ellipse(cx + 0.6, feet_y, wid * 0.7, max(1.0, hgt * 0.10), (18, 40, 20))
    img.ellipse(cx, feet_y - hgt * 0.45, wid / 2.0, hgt * 0.45, jersey)
    img.ellipse(cx, feet_y - hgt * 0.90, wid * 0.36, hgt * 0.13, trim)
    if back_number and hgt >= 14:
        img.rect(cx - 1, feet_y - hgt * 0.62, cx + 2, feet_y - hgt * 0.40, trim)


# --- football ---------------------------------------------------------------------

def _football(img, game):
    gid, _sport, scene, away, home, _a, _h2, _p = game
    horizon = int(H * 0.20)
    _crowd(img, 0, horizon - 4, gid)
    img.rect(0, horizon - 4, W, horizon, WALL)
    vpy = -1.6 * H                       # the vanishing point, above the frame
    ppy = 7.0                            # pixels per yard at the frame's bottom
    cam = 0.0 if scene == "line" else 3.0
    x_centre = W / 2.0 + (_h(gid, "pan") % 17 - 8)

    def t_of(y):
        return (y - vpy) / (H - vpy)

    def x_of(yard, y):
        return x_centre + (yard - cam) * ppy * t_of(y)

    def yard_of(x, y):
        return cam + (x - x_centre) / (ppy * t_of(y))

    end_zone = TEAMS[home][0]
    for y in range(horizon, H):
        for x in range(W):
            yd = yard_of(x + 0.5, y + 0.5)
            if scene == "goal_line" and yd < -10.0:
                col = _mix(end_zone, (20, 20, 20), 0.35)
                if int(math.floor((yd * 0.9 + (y - horizon) * 0.25) / 1.6)) % 2 == 0:
                    col = _mix(col, TEAMS[home][1], 0.18)
            else:
                col = GRASS if int(math.floor(yd / 5.0)) % 2 == 0 else GRASS_LIGHT
            img.set(x, y, col)
    lo, hi = int(yard_of(0, H) - 5), int(yard_of(W, H) + 5)
    for yard in range(lo - lo % 5, hi + 1, 5):
        if scene == "goal_line" and yard < -10:
            continue
        width = 2.0 if yard == (-10 if scene == "goal_line" else 999) else 1.0
        for y in range(horizon, H):
            x = x_of(yard, y + 0.5)
            wpx = width * (1.0 + t_of(y))
            for xx in range(int(x - wpx / 2.0), int(x + wpx / 2.0) + 1):
                img.set(xx, y, CHALK)
    # the hash marks, two rows of ticks at every yard
    for row in (0.48, 0.70):
        y = int(horizon + (H - horizon) * row)
        for yard in range(lo, hi + 1):
            if scene == "goal_line" and yard < -10:
                continue
            x = x_of(yard, y)
            img.set(x, y, CHALK)
    # the teams: offence (away) on the camera-left of the line of scrimmage
    los = cam + (-3.0 if scene == "line" else -4.0)
    rows = 11
    for side, team, sign in (("off", away, -1.0), ("def", home, 1.0)):
        jersey, trim = TEAMS[team]
        for k in range(rows):
            depth = 0.30 + 0.60 * k / (rows - 1)
            y = horizon + (H - horizon) * depth
            j = _h(gid, side, k)
            back = 1.0 + (j % 5) * (0.9 if side == "def" else 0.5)
            if k in (4, 5, 6) and side == "off":
                back += 3.0 + (j % 3)            # the backfield
            yard = los + sign * back + ((j >> 8) % 7 - 3) * 0.15
            _player(img, x_of(yard, y), y, 10.5 * t_of(y), jersey, trim)


# --- baseball ---------------------------------------------------------------------

def _stripes(img, y0, key, diagonal):
    for y in range(y0, H):
        for x in range(W):
            band = (x + y) // 14 if diagonal else y // 10
            img.set(x, y, GRASS if band % 2 == 0 else GRASS_LIGHT)


def _inside(poly, x, y):
    n, c = len(poly), False
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def _baseball(img, game):
    gid, _sport, scene, away, home, _a, _h2, _p = game
    bat, bat_trim = TEAMS[away]
    field, field_trim = TEAMS[home]
    cx = W / 2.0
    if scene == "pitch":
        top = int(H * 0.22)
        _crowd(img, 0, top - 6, gid)
        img.rect(0, top - 6, W, top, WALL)
        _stripes(img, top, gid, diagonal=False)
        plate_y = H * 0.40
        # the base paths running out of frame, dirt with a chalk line
        for s in (-1.0, 1.0):
            img.line(cx + s * 0.06 * W, plate_y + 4, cx + s * 0.66 * W, H * 1.02, DIRT, width=7.0)
            img.line(cx + s * 0.06 * W, plate_y + 4, cx + s * 0.66 * W, H * 1.02, CHALK, width=1.0)
        img.ellipse(cx, plate_y, 0.22 * W, 0.085 * H, DIRT)
        for s in (-1.0, 1.0):                  # the batter's boxes
            bx = cx + s * 10
            img.line(bx - 4, plate_y - 5, bx + 4, plate_y - 5, CHALK)
            img.line(bx - 4, plate_y + 3, bx + 4, plate_y + 3, CHALK)
        img.rect(cx - 2, plate_y - 1, cx + 2, plate_y + 1, CHALK)
        lefty = _h(gid, "hand") % 2
        bx = cx + (12 if lefty else -12)
        _player(img, cx, plate_y + 1, 9.0, (30, 30, 34), (20, 20, 22))    # umpire
        _player(img, cx, plate_y + 2, 6.5, field, field_trim)              # catcher
        _player(img, bx, plate_y + 1, 13.0, bat, bat_trim)                 # batter
        img.line(bx + (-3 if lefty else 3), plate_y - 12, bx + (-8 if lefty else 8),
                 plate_y - 18, (170, 130, 80))
        img.ellipse(cx, H * 0.84, 0.15 * W, 0.075 * H, DIRT)
        img.rect(cx - 5, H * 0.84 - 1, cx + 5, H * 0.84 + 1, CHALK)
        _player(img, cx + 3, H * 0.86, 36.0, field, field_trim, back_number=True)
    else:
        top = int(H * 0.18)
        _crowd(img, 0, top - 5, gid)
        img.rect(0, top - 5, W, top, WALL)
        _stripes(img, top, gid, diagonal=True)
        home_p = (cx, H * 0.93)
        second = (cx, H * 0.47)
        first = (cx + 0.29 * W, H * 0.66)
        third = (cx - 0.29 * W, H * 0.66)
        mound = (cx, H * 0.67)
        # the skin: a dirt fan over the infield, clipped by the foul lines
        for y in range(top, H):
            for x in range(W):
                dx, dy = (x + 0.5 - mound[0]) / (0.40 * W), (y + 0.5 - (H * 0.60)) / (0.24 * H)
                fair = abs(x + 0.5 - home_p[0]) <= (home_p[1] - (y + 0.5)) * 1.30 + 4
                if dx * dx + dy * dy <= 1.0 and fair and y < home_p[1]:
                    img.set(x, y, DIRT)
        grass = [(home_p[0], home_p[1] - 10), (first[0] - 14, first[1]),
                 (second[0], second[1] + 10), (third[0] + 14, third[1])]
        for y in range(top, H):
            for x in range(W):
                if _inside(grass, x + 0.5, y + 0.5):
                    img.set(x, y, GRASS_LIGHT)
        img.ellipse(mound[0], mound[1], 0.05 * W, 0.03 * H, DIRT)
        img.ellipse(home_p[0], home_p[1], 0.08 * W, 0.045 * H, DIRT)
        for end in ((0.0, top + 2), (W, top + 2)):
            img.line(home_p[0], home_p[1], end[0], end[1] + (home_p[1] - top) * 0.25, CHALK)
        for b in (first, second, third):
            img.rect(b[0] - 1, b[1] - 1, b[0] + 2, b[1] + 1, CHALK)
        spots = [(mound[0], mound[1]), (first[0] - 4, first[1] - 6), (cx + 0.13 * W, H * 0.52),
                 (cx - 0.13 * W, H * 0.52), (third[0] + 4, third[1] - 6),
                 (cx - 0.33 * W, H * 0.27), (cx, H * 0.24), (cx + 0.33 * W, H * 0.27),
                 (home_p[0], home_p[1] + 4)]
        for k, (x, y) in enumerate(spots):
            depth = (y - top) / (H - top)
            _player(img, x + (_h(gid, k) % 5 - 2), y, 3.0 + 7.0 * depth, field, field_trim)
        _player(img, home_p[0] - 7, home_p[1], 10.0, bat, bat_trim)
        if _h(gid, "runner") % 2:
            _player(img, first[0] + 5, first[1] + 1, 7.5, bat, bat_trim)


# --- the bug and the tube -------------------------------------------------------------

def _bug(img, game):
    _i, _s, _sc, away, home, _a, _h2, period = game
    rows = bug_lines(game[0])
    x0, y0 = 6, 6
    chip = 5
    row_h = pt.LINE - 1
    names_w = max(pt.ink_width(r.split()[0]) for r in rows[:2])
    score_w = max(pt.ink_width(r.split()[1]) for r in rows[:2])
    box_w = 2 + chip + 3 + names_w + 5 + score_w + 3
    box_h = 2 * row_h + 3
    img.rect(x0 - 1, y0 - 1, x0 + box_w + 1, y0 + box_h + 1, BUG_EDGE)
    img.rect(x0, y0, x0 + box_w, y0 + box_h, BUG_BG)
    for k, (team, text) in enumerate(((away, rows[0]), (home, rows[1]))):
        name, score = text.split()
        ry = y0 + 1 + k * (row_h + 1)
        # the chip outlined, or a black jersey vanishes into the box
        img.rect(x0 + 1, ry, x0 + 3 + chip, ry + row_h, BUG_EDGE)
        img.rect(x0 + 2, ry + 1, x0 + 2 + chip, ry + row_h - 1, TEAMS[team][0])
        tx = x0 + 2 + chip + 3
        img.mask(pt.render(name), tx, ry - 1, BUG_INK)
        sx = x0 + box_w - 3 - pt.ink_width(score)
        img.mask(pt.render(score), sx, ry - 1, BUG_INK)
    pw = pt.ink_width(period) + 6
    py = y0 + box_h + 1
    img.rect(x0 - 1, py, x0 + pw + 1, py + row_h + 2, BUG_EDGE)
    img.rect(x0, py, x0 + pw, py + row_h + 1, (60, 16, 20))
    img.mask(pt.render(period), x0 + 3, py - 1, BUG_INK)
    return (x0 - 1, y0 - 1, x0 + max(box_w, pw) + 1, py + row_h + 2)


def _tube(img):
    for y in range(img.h):
        line = SCANLINE if y % 2 == 1 else 1.0
        ny = (y + 0.5) / img.h * 2.0 - 1.0
        for x in range(img.w):
            nx = (x + 0.5) / img.w * 2.0 - 1.0
            r = math.sqrt((nx * nx + ny * ny) / 2.0)
            f = line * (1.0 - VIGNETTE * r ** 1.5)
            p = img.px[y * img.w + x]
            img.px[y * img.w + x] = [p[i] * f * PHOSPHOR[i] for i in range(3)]


def paint(game_id):
    """The screen for one game. Returns (canvas, facts)."""
    game = BY_ID[game_id]
    img = _Img(W, H, GRASS)
    if game[1] == "football":
        _football(img, game)
    elif game[1] == "baseball":
        _baseball(img, game)
    else:
        raise ValueError(f"game {game_id}: unknown sport {game[1]!r}")
    img.blur(2)
    bug = _bug(img, game)
    img.blur(1)
    _tube(img)
    canvas = img.to_canvas()
    digest = zlib.crc32(bytes(canvas.buf)) & 0xFFFFFFFF
    return canvas, {"game": game_id, "sport": game[1], "scene": game[2],
                    "bug": bug_lines(game_id), "bug_rect": bug,
                    "name": f"crt_{game_id}_{W}x{H}_{digest:08x}"}
