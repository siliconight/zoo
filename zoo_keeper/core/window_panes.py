"""An Empty's window, painted: one atlas of 1990s window states (1.64.0).

The walker, 2026-10-04, with a Vampire: The Masquerade -- Bloodlines street
as the comp: "I think its actually ok to have lights on in the windows at
night to show life". Read off in the factory root's
`docs/reference/EMPTIES_COMPS.md` ("LIT WINDOWS AT NIGHT"): windows mixed per
building -- some lit warm, many of those behind bars, most dark; curtains and
blinds; none of them a real light. Before this an Empty's pane was one
opaque `glass_facade` surface, and at night the row read as a black mass
outside the streetlight pools (cold run 9150).

COLOUR VARIATION IS KEY (1.65.0, the walker, sending window photographs: a
night facade of rowhouse and tenement windows, three street rows by day).
The first atlas had one lit colour, and the night photographs have five at
least -- tungsten yellow, the deep orange of a curtained room, a pale cool
fluorescent, a pink lampshade glow -- and as many coverings: blinds, a
roller shade pulled half down with the light below it, curtains. The day
rows add the green roller shade, closed blinds, and a box fan in the lower
sash. Sixteen states now; the AIR CONDITIONER every photograph shows is
geometry standing out of the window, and is not painted here.

ONE ATLAS, ONE MATERIAL, NO LIGHT. Every state is a cell of one image, and a
pane's UVs pick its cell, so a whole street of windows is one material and
the variety costs no submission (`CLAUDE.md`, "never express colour-only
variation as a new material"). The lit cells glow through a SEPARATE emission
image -- black wherever the room light does not show -- because driving
emission from the albedo would light boarded plywood and curtain fabric too.
The material is named `_Face`, so Lux's emissive binder darkens every lit
window in the power cut.

THE WINDOW IS A ROWHOUSE'S: a painted-wood frame, a double-hung sash with a
meeting rail, six-over-six muntins -- the comp's sash -- and on the vacant
house plywood. Deli Counter (>= 0.180.0) chooses the state per window, so
which windows glow is decided where the building is known; this paints.

Same machinery as `vending_forms` and `flat_art`: a `Canvas`, row 0 at the
top, integer arithmetic only, so host Python and Blender write the same
bytes.
"""
from __future__ import annotations

from .vending_forms import Canvas

#: The states, in atlas order: row-major, ``COLS`` to a row. Lit first, then
#: dark, then the odd ones -- the order is the cell, so append, never insert.
STATES = ("lit", "lit_amber", "lit_cool", "lit_pink",
          "lit_blind", "lit_blind_cool", "lit_curtain", "lit_shade",
          "lit_bars", "dark", "dark_blind", "dark_shade",
          "dark_curtain", "dark_bars", "dark_fan", "boarded")
COLS = 4
ROWS = 4
#: One cell, in pixels: a window is about 0.95 x 1.6 m, so taller than wide.
CELL_W = 48
CELL_H = 80
#: The frame, the meeting rail and a muntin, in pixels.
FRAME = 3
RAIL = 2
MUNTIN = 1

#: Painted wood frame, as a 1990s rowhouse sash is painted.
FRAME_RGB = (198, 192, 178)
MUNTIN_RGB = (150, 144, 132)

#: THE ROOM LIGHTS (1.65.0), each (ceiling, middle, low): the colours the
#: night photographs show, not one warm. A sofa back sits low in every room.
TUNGSTEN = ((150, 92, 44), (240, 186, 96), (226, 160, 78))
AMBER = ((140, 62, 26), (236, 138, 58), (214, 112, 44))
COOL = ((128, 140, 122), (214, 228, 200), (196, 210, 182))
PINK = ((146, 76, 70), (238, 166, 150), (220, 140, 124))
ROOMS = {"lit": TUNGSTEN, "lit_amber": AMBER, "lit_cool": COOL, "lit_pink": PINK,
         "lit_blind": TUNGSTEN, "lit_blind_cool": COOL, "lit_curtain": AMBER,
         "lit_shade": TUNGSTEN, "lit_bars": TUNGSTEN}
SOFA = (96, 52, 30)

#: Dark glass: night sky reflected, a shade lighter at the bottom.
DARK_TOP = (16, 22, 34)
DARK_LOW = (30, 40, 56)
STREAK = (52, 66, 88)
SLAT = (226, 208, 158)
SLAT_COOL = (222, 226, 214)
SLAT_SHUT = (128, 126, 116)
SHADE = (220, 206, 168)
SHADE_GREEN = (58, 88, 66)
CURTAIN = (176, 70, 34)
CURTAIN_FOLD = (132, 50, 24)
NET = (92, 90, 84)
FAN = (118, 116, 110)
FAN_GRILLE = (72, 70, 66)
PLY = (139, 109, 71)
PLY_GRAIN = (116, 88, 56)
NAIL = (70, 66, 60)

#: How much of the room light a covering lets through, out of 255 -- the rest
#: of the glow belongs to the gaps.
SLAT_GLOW = 150
CURTAIN_GLOW = 90
SHADE_GLOW = 70

#: Emission strength the material is built at. Lux scales it by energy and
#: zeroes it in the power cut; the albedo is dimmed so a lit window is its
#: glow and not a bright print under the streetlights.
EMISSION = 1.6
ALBEDO = 0.55


def _lerp(a, b, t_num, t_den):
    return tuple(a[i] + (b[i] - a[i]) * t_num // max(1, t_den) for i in range(3))


def _scale(rgb, num):
    return tuple(v * num // 255 for v in rgb)


def cell_rect(state):
    """``(x0, y0, x1, y1)`` of a state's cell in pixels, row 0 at the top."""
    i = STATES.index(state)
    cx, cy = i % COLS, i // COLS
    return (cx * CELL_W, cy * CELL_H, (cx + 1) * CELL_W, (cy + 1) * CELL_H)


def uv_rect(state):
    """``(u0, v0, u1, v1)`` of a state's GLASS, inset by the frame, in UV
    space (v up, as Blender's UVs are): a pane's outer face maps to it."""
    x0, y0, x1, y1 = cell_rect(state)
    w, h = COLS * CELL_W, ROWS * CELL_H
    return ((x0 + FRAME) / w, 1.0 - (y1 - FRAME) / h,
            (x1 - FRAME) / w, 1.0 - (y0 + FRAME) / h)


def frame_uv():
    """A UV point inside frame paint: the faces of a pane nobody looks at
    straight on (its thin edges) take the frame colour from here."""
    f = uv_rect(STATES[0])[0] * 0.25
    return (f, f)


def face_uv(state, normal_y, x, z, cx, cz, hx, hz):
    """The UV of one corner of a pane's face (1.66.0).

    ``normal_y`` is the face normal's Y in the module's own frame; ``x``, ``z``
    the corner; ``cx``, ``cz``, ``hx``, ``hz`` the pane's centre and half size.

    BOTH BIG FACES CARRY THE CELL. 1.64.0 painted only the +Y face, on the
    assumption that +Y is outdoors, and cold run 9151 measured the painted
    face pointing INTO the houses: the street saw frame paint. Painting both
    faces makes the answer independent of how a module is turned.

    EACH READS UNMIRRORED FROM ITS OWN SIDE. Looking along the view direction
    ``d`` with up +Z, the viewer's right is ``d x up``: -X for a viewer on
    the +Y side, +X on the -Y side. ``u`` runs toward that right on both.
    The thin faces take `frame_uv`.
    """
    if abs(normal_y) < 0.9:
        return frame_uv()
    u0, v0, u1, v1 = uv_rect(state)
    t = ((cx + hx) - x) / (2 * hx) if normal_y > 0 else (x - (cx - hx)) / (2 * hx)
    return (u0 + (u1 - u0) * t, v0 + (v1 - v0) * (z - (cz - hz)) / (2 * hz))


def _room(c, e, x0, y0, x1, y1, light):
    """A lit room behind the glass, into albedo ``c`` and emission ``e``."""
    top, mid, low = light
    h = y1 - y0
    for y in range(y0, y1):
        k = y - y0
        rgb = (_lerp(top, mid, k, h * 2 // 5) if k < h * 2 // 5
               else _lerp(mid, low, k - h * 2 // 5, h - h * 2 // 5))
        c.rect(x0, y, x1, y + 1, rgb)
        e.rect(x0, y, x1, y + 1, rgb)
    sofa = y1 - h // 6
    c.rect(x0, sofa, x1, y1, SOFA)
    e.rect(x0, sofa, x1, y1, tuple(v // 3 for v in SOFA))


def _dark(c, x0, y0, x1, y1):
    h = y1 - y0
    for y in range(y0, y1):
        c.rect(x0, y, x1, y + 1, _lerp(DARK_TOP, DARK_LOW, y - y0, h))
    # a reflected streak, corner to corner, two pixels wide
    for k in range(min(x1 - x0 - 1, h)):     # x + 1 stays inside the glass
        x = x0 + k
        y = y0 + h // 3 + k * 2 // 3
        if y < y1:
            c.px(x, y, STREAK)
            c.px(x + 1, y, STREAK)


def _slats(c, e, x0, y0, x1, y1, rgb, glow):
    for y in range(y0, y1):
        if (y - y0) % 4 < 3:
            c.rect(x0, y, x1, y + 1, rgb)
            e.rect(x0, y, x1, y + 1, _scale(rgb, glow))


def _sash(c, e, x0, y0, x1, y1):
    """Meeting rail and six-over-six muntins over the glass, in frame paint
    (and black in the emission: wood does not glow)."""
    mid = (y0 + y1) // 2
    c.rect(x0, mid - RAIL // 2, x1, mid + RAIL // 2 + RAIL % 2, FRAME_RGB)
    e.rect(x0, mid - RAIL // 2, x1, mid + RAIL // 2 + RAIL % 2, (0, 0, 0))
    for top, bot in ((y0, mid - RAIL // 2), (mid + RAIL // 2 + RAIL % 2, y1)):
        for j in (1, 2):
            x = x0 + (x1 - x0) * j // 3
            c.rect(x, top, x + MUNTIN, bot, MUNTIN_RGB)
            e.rect(x, top, x + MUNTIN, bot, (0, 0, 0))
        y = (top + bot) // 2
        c.rect(x0, y, x1, y + MUNTIN, MUNTIN_RGB)
        e.rect(x0, y, x1, y + MUNTIN, (0, 0, 0))


def _fan(c, x0, y0, x1, y1):
    """A box fan standing in the lower sash: a grey square, a round grille."""
    mid = (y0 + y1) // 2
    side = min(x1 - x0 - 6, y1 - mid - 4)
    fx0 = (x0 + x1 - side) // 2
    fy0 = mid + 2
    c.rect(fx0, fy0, fx0 + side, fy0 + side, FAN)
    r = side // 2 - 2
    cx, cy = fx0 + side // 2, fy0 + side // 2
    for y in range(fy0, fy0 + side):
        for x in range(fx0, fx0 + side):
            d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if d <= r * r and (d % 9 < 4 or abs(x - cx) < 1 or abs(y - cy) < 1):
                c.px(x, y, FAN_GRILLE)


def _paint(state, c, e):
    x0, y0, x1, y1 = cell_rect(state)
    c.rect(x0, y0, x1, y1, FRAME_RGB)
    gx0, gy0, gx1, gy1 = x0 + FRAME, y0 + FRAME, x1 - FRAME, y1 - FRAME
    if state == "boarded":
        for y in range(gy0, gy1):
            grain = PLY_GRAIN if (y * 7 + (y // 9) * 3) % 11 == 0 else PLY
            c.rect(gx0, y, gx1, y + 1, grain)
        seam = (gy0 + gy1) // 2
        c.rect(gx0, seam, gx1, seam + 1, PLY_GRAIN)
        for nx in (gx0 + 3, gx1 - 4):
            for ny in (gy0 + 3, seam - 3, seam + 4, gy1 - 4):
                c.px(nx, ny, NAIL)
        return
    if state.startswith("lit"):
        _room(c, e, gx0, gy0, gx1, gy1, ROOMS[state])
    else:
        _dark(c, gx0, gy0, gx1, gy1)
    if state == "lit_blind":
        _slats(c, e, gx0, gy0, gx1, gy1, SLAT, SLAT_GLOW)
    elif state == "lit_blind_cool":
        _slats(c, e, gx0, gy0, gx1, gy1, SLAT_COOL, SLAT_GLOW)
    elif state == "dark_blind":
        _slats(c, e, gx0, gy0, gx1, gy1, SLAT_SHUT, 0)
    elif state == "lit_curtain":
        cw = (gx1 - gx0) * 3 // 10
        for xa, xb in ((gx0, gx0 + cw), (gx1 - cw, gx1)):
            for x in range(xa, xb):
                rgb = CURTAIN_FOLD if (x - xa) % 4 == 0 else CURTAIN
                c.rect(x, gy0, x + 1, gy1, rgb)
                e.rect(x, gy0, x + 1, gy1, _scale(AMBER[1], CURTAIN_GLOW))
    elif state in ("lit_shade", "dark_shade"):
        # a roller shade pulled a little past half: the light shows below it
        lit = state == "lit_shade"
        bottom = gy0 + (gy1 - gy0) * 11 // 20
        rgb = SHADE if lit else SHADE_GREEN
        c.rect(gx0, gy0, gx1, bottom, rgb)
        e.rect(gx0, gy0, gx1, bottom, _scale(rgb, SHADE_GLOW) if lit else (0, 0, 0))
        c.rect(gx0, bottom, gx1, bottom + 1, MUNTIN_RGB)
        e.rect(gx0, bottom, gx1, bottom + 1, (0, 0, 0))
    elif state == "dark_curtain":
        for x in range(gx0, gx1):
            rgb = NET if (x - gx0) % 5 else tuple(v - 14 for v in NET)
            c.rect(x, gy0, x + 1, gy1, rgb)
    _sash(c, e, gx0, gy0, gx1, gy1)
    # NO PAINTED BARS (1.69.0). A barred window's bars are geometry now --
    # `dressing.bar_parts`, ordered by Patina (>= 0.26.0) from the slot Deli
    # Counter (>= 0.181.0) marks -- standing 3.5 cm off the wall while this
    # pane sits 13 cm behind it. Painted as well, they drew a second grid that
    # slid against the real one as the eye moved. A barred pane paints its
    # room and nothing else.
    if state == "dark_fan":
        _fan(c, gx0, gy0, gx1, gy1)


def atlas():
    """``(albedo, emission)`` canvases of every state, and the same bytes for
    the same code every build."""
    w, h = COLS * CELL_W, ROWS * CELL_H
    c, e = Canvas(w, h, FRAME_RGB), Canvas(w, h, (0, 0, 0))
    for state in STATES:
        _paint(state, c, e)
    return c, e
