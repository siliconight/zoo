"""A corner shop's window, painted: one atlas of 1990s storefront states (1.107.0, factory roadmap 241).

The urban comps (the factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`): "Corners carry the life. The corner
building has the shop at grade (lit, awning), homes above", and the second frame's "lit restaurant at street level
under an awning -- the warm light the eye goes to first". An Empty has no lights by design: its windows are paint
(`window_panes`), one atlas and one material for a whole street. A storefront is wider than a sash and shows a
different room, so it is its own atlas -- landscape cells, its own material -- on a corner shop's front and nowhere
else.

THE STOREFRONT IS ALUMINIUM: a frame, a transom bar a fifth of the way down with its glass above, mullions
splitting the glass into three lights, and a kick plate at the foot -- the 1990s shopfront of the comps' corner,
painted, as `window_panes` paints a sash. Behind it, per state:

  shop_deli      warm tungsten, shelves of goods on the back wall and a lit deli case low
  shop_grocery   cool fluorescent, aisles of shelving to the back and light strips overhead
  shop_bar       a dim amber room, bottles on the back bar and a neon line low
  shop_laundry   cool, a row of washers -- white boxes, round dark doors
  shop_gate      shut: a roll-down security gate over the glass, unlit
  shop_dark      shut: dark glass, the street's reflection

ONE ATLAS, ONE MATERIAL, NO LIGHT, as `window_panes`. Every state is a cell, a pane's UVs pick its cell, and the
lit cells glow through a separate emission image, black wherever no room light shows. The material is named
`_Face`, so Lux's emissive binder darkens every lit shop in the power cut. A shop glows brighter than a home's
window (`EMISSION`): it is the light the eye goes to first.

Same machinery as `window_panes`: a `Canvas`, row 0 at the top, integer arithmetic only, so host Python and
Blender write the same bytes. The states are appended, never inserted: the order is the cell.
"""
from __future__ import annotations

from .vending_forms import Canvas

#: The states, in atlas order: row-major, ``COLS`` to a row.
STATES = ("shop_deli", "shop_grocery", "shop_bar", "shop_laundry", "shop_gate", "shop_dark")
COLS = 3
ROWS = 2
#: One cell, in pixels: a storefront bay is about 2.8 m wide and 2.4 m tall.
CELL_W = 112
CELL_H = 96
#: The aluminium, in pixels: the frame round the cell, the transom bar, a mullion, the kick plate.
FRAME = 3
TRANSOM = 2
MULLION = 2
KICK = 8
#: Anodised aluminium, as a 1990s shopfront is framed.
FRAME_RGB = (170, 172, 174)
KICK_RGB = (92, 94, 98)

#: The rooms, each (ceiling, middle, low).
TUNGSTEN = ((160, 104, 52), (246, 198, 112), (230, 172, 92))
FLUORESCENT = ((186, 200, 196), (232, 242, 236), (206, 218, 210))
BAR_AMBER = ((70, 34, 16), (150, 82, 36), (110, 58, 28))
LAUNDRY = ((170, 186, 196), (222, 234, 240), (196, 210, 218))
ROOMS = {"shop_deli": TUNGSTEN, "shop_grocery": FLUORESCENT, "shop_bar": BAR_AMBER,
         "shop_laundry": LAUNDRY}
#: Goods on a shelf, in turn; a deli case's glow; a bottle; neon; a washer and its door.
GOODS = ((196, 58, 46), (232, 196, 60), (64, 128, 70), (60, 92, 168), (226, 226, 214), (214, 120, 40))
SHELF = (110, 84, 60)
CASE = (250, 248, 236)
BOTTLE = (120, 186, 120)
NEON = (255, 70, 120)
WASHER = (236, 238, 240)
WASHER_DOOR = (54, 64, 78)

#: Dark glass and the gate.
DARK_TOP = (14, 20, 30)
DARK_LOW = (28, 38, 52)
STREAK = (50, 64, 86)
GATE = (128, 130, 132)
GATE_SHADOW = (88, 90, 94)

#: Emission strength the material is built at; brighter than a home's window (`window_panes.EMISSION`, 1.6), so
#: the shop is the light the eye goes to first. Lux scales it by energy and zeroes it in the power cut.
EMISSION = 2.2
ALBEDO = 0.6


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
    """``(u0, v0, u1, v1)`` of a state's storefront, inset by the frame, in UV space (v up)."""
    x0, y0, x1, y1 = cell_rect(state)
    w, h = COLS * CELL_W, ROWS * CELL_H
    return ((x0 + FRAME) / w, 1.0 - (y1 - FRAME) / h,
            (x1 - FRAME) / w, 1.0 - (y0 + FRAME) / h)


def frame_uv():
    """A UV point inside the aluminium: the thin faces of a pane take the frame colour from here."""
    f = uv_rect(STATES[0])[0] * 0.25
    return (f, f)


def face_uv(state, normal_y, x, z, cx, cz, hx, hz):
    """The UV of one corner of a pane's face, as `window_panes.face_uv`: both big faces carry the cell, each
    unmirrored from its own side; the thin faces take `frame_uv`."""
    if abs(normal_y) < 0.9:
        return frame_uv()
    u0, v0, u1, v1 = uv_rect(state)
    t = ((cx + hx) - x) / (2 * hx) if normal_y > 0 else (x - (cx - hx)) / (2 * hx)
    return (u0 + (u1 - u0) * t, v0 + (v1 - v0) * (z - (cz - hz)) / (2 * hz))


def _room(c, e, x0, y0, x1, y1, light):
    top, mid, low = light
    h = y1 - y0
    for y in range(y0, y1):
        k = y - y0
        rgb = (_lerp(top, mid, k, h * 2 // 5) if k < h * 2 // 5
               else _lerp(mid, low, k - h * 2 // 5, h - h * 2 // 5))
        c.rect(x0, y, x1, y + 1, rgb)
        e.rect(x0, y, x1, y + 1, rgb)


def _shelves(c, e, x0, y0, x1, y1, rows, glow):
    """Rows of goods on shelves across the back wall: a shelf line, then boxes in turn along it."""
    h = y1 - y0
    for r in range(rows):
        sy = y0 + h * (r + 1) // (rows + 1)
        c.rect(x0, sy, x1, sy + 1, SHELF)
        e.rect(x0, sy, x1, sy + 1, (0, 0, 0))
        for i, x in enumerate(range(x0 + 2, x1 - 3, 4)):
            rgb = GOODS[(i + r * 2) % len(GOODS)]
            c.rect(x, sy - 4, x + 3, sy, rgb)
            e.rect(x, sy - 4, x + 3, sy, _scale(rgb, glow))


def _dark(c, x0, y0, x1, y1):
    h = y1 - y0
    for y in range(y0, y1):
        c.rect(x0, y, x1, y + 1, _lerp(DARK_TOP, DARK_LOW, y - y0, h))
    for k in range(min(x1 - x0 - 1, h)):
        x = x0 + k * 2
        y = y0 + h // 4 + k * 2 // 3
        if y < y1 and x + 1 < x1:
            c.px(x, y, STREAK)
            c.px(x + 1, y, STREAK)


def _gate(c, x0, y0, x1, y1):
    """A roll-down gate: horizontal slats, a shadow line every third, no glow."""
    for y in range(y0, y1):
        c.rect(x0, y, x1, y + 1, GATE_SHADOW if (y - y0) % 3 == 0 else GATE)


def _storefront(c, e, x0, y0, x1, y1):
    """The aluminium over the glass: the transom bar, two mullions, the kick plate -- black in the emission."""
    transom = y0 + (y1 - y0) // 5
    c.rect(x0, transom, x1, transom + TRANSOM, FRAME_RGB)
    e.rect(x0, transom, x1, transom + TRANSOM, (0, 0, 0))
    for j in (1, 2):
        x = x0 + (x1 - x0) * j // 3
        c.rect(x, transom, x + MULLION, y1, FRAME_RGB)
        e.rect(x, transom, x + MULLION, y1, (0, 0, 0))
    c.rect(x0, y1 - KICK, x1, y1, KICK_RGB)
    e.rect(x0, y1 - KICK, x1, y1, (0, 0, 0))


def _paint(state, c, e):
    x0, y0, x1, y1 = cell_rect(state)
    c.rect(x0, y0, x1, y1, FRAME_RGB)
    gx0, gy0, gx1, gy1 = x0 + FRAME, y0 + FRAME, x1 - FRAME, y1 - FRAME
    if state == "shop_gate":
        _gate(c, gx0, gy0, gx1, gy1)
        return
    if state == "shop_dark":
        _dark(c, gx0, gy0, gx1, gy1)
        _storefront(c, e, gx0, gy0, gx1, gy1)
        return
    _room(c, e, gx0, gy0, gx1, gy1, ROOMS[state])
    low = gy1 - KICK
    if state == "shop_deli":
        _shelves(c, e, gx0, gy0 + (gy1 - gy0) // 5, gx1, low - 16, 2, 150)
        c.rect(gx0 + 6, low - 14, gx1 - 6, low - 4, CASE)
        e.rect(gx0 + 6, low - 14, gx1 - 6, low - 4, CASE)
    elif state == "shop_grocery":
        for x in range(gx0 + 4, gx1 - 4, 14):
            c.rect(x, gy0 + (gy1 - gy0) // 5 + 4, x + 8, low, SHELF)
            e.rect(x, gy0 + (gy1 - gy0) // 5 + 4, x + 8, low, _scale(SHELF, 60))
        _shelves(c, e, gx0, gy0 + (gy1 - gy0) // 5, gx1, low, 3, 120)
        c.rect(gx0, gy0 + 2, gx1, gy0 + 3, (255, 255, 255))
        e.rect(gx0, gy0 + 2, gx1, gy0 + 3, (255, 255, 255))
    elif state == "shop_bar":
        bar = low - 18
        for i, x in enumerate(range(gx0 + 3, gx1 - 3, 3)):
            if i % 3 != 2:
                c.rect(x, bar - 10, x + 1, bar - 2, BOTTLE)
                e.rect(x, bar - 10, x + 1, bar - 2, _scale(BOTTLE, 160))
        c.rect(gx0 + 4, low - 6, gx1 - 4, low - 4, NEON)
        e.rect(gx0 + 4, low - 6, gx1 - 4, low - 4, NEON)
    elif state == "shop_laundry":
        side = (gy1 - gy0) // 3
        for x in range(gx0 + 3, gx1 - side, side + 3):
            c.rect(x, low - side, x + side, low, WASHER)
            e.rect(x, low - side, x + side, low, _scale(WASHER, 140))
            r = side // 3
            cx, cy = x + side // 2, low - side // 2
            for yy in range(cy - r, cy + r + 1):
                for xx in range(cx - r, cx + r + 1):
                    if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                        c.px(xx, yy, WASHER_DOOR)
                        e.px(xx, yy, (0, 0, 0))
    _storefront(c, e, gx0, gy0, gx1, gy1)


def atlas():
    """``(albedo, emission)`` canvases of every state, the same bytes for the same code every build."""
    w, h = COLS * CELL_W, ROWS * CELL_H
    c, e = Canvas(w, h, FRAME_RGB), Canvas(w, h, (0, 0, 0))
    for state in STATES:
        _paint(state, c, e)
    return c, e
