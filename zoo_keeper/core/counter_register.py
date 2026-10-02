"""A register standing on a counter, with its green display lit.

Zoo 1.16.0. The walker, 2026-09-28, with three photographs of 1990s
registers (a beige Fujitsu, a black Sharp XE-A207 with a pole display, a
TEC MA-1595 with one): "I also want the cash registers in these buildings
(where we have cash registers) to have that glowing green/black screen" --
and "I've mentioned this before": 1.0.0's `cash_register` species carries
it ("Cash registers in the 90s had this green font on a black screen"), but
the registers the stores and bars actually stand -- on the service
counter's stations (1.7.0) and the club bar's (0.92.0) -- were three beige
boxes with no screen at all, the bar's own comment promising "a display on
a stalk" that was never built.

ONE REGISTER, BOTH COUNTERS. `back_bar_forms.counter_fitout` and
`service_counter_forms.fitout` each spelled the same three boxes; both now
call `station`, so the next change to a register is made once.

WHAT IS BUILT at a station, in the counter recipe's frame (-Y the customer,
+Y the staff side):

  * the beige BODY on the top, as before;
  * the KEYPAD at the STAFF end and the display HUMP at the CUSTOMER end.
    Until 1.16.0 it was the other way round -- keys toward the customer,
    the hump's blank back to the clerk -- which is not how any of the
    walker's photographs stands: the operator faces the keys and reads the
    hump across them, and the customer reads its back;
  * the OPERATOR display on the hump's staff face, green type on black
    (the hump's customer face carried a second display until 1.54.0; the
    walker asked for one price facing the customer, and that is the pole's);
  * the POLE DISPLAY: a stalk from the hump's top and a dark box on it, its
    window facing the customer, as the Sharp's and the TEC's stand.

GLOWING WITHOUT A LIGHT. The three windows are one backlit image,
`M_Counter_VFD_<art>_Face` in the recipe (the `_Face` suffix is what Lux's
power cut takes), at `register_forms.SCREEN_EMISSION` -- the strength 1.0.0
chose for this exact screen by measured saturation. The type and the
colours are `register_forms`' own (`paint_screen`, `VFD_INK`), so a till
in the card shop and a till on a store counter read as one make.

COST: the windows of every station on a counter are one object on one
image, whatever its register count.

THE REAL LOOK (1.46.0). The walker, 2026-10-02: "this looks like it is made
with a 90s GPU ... replace the retro look", then "do the ATM and register the
same way". The body was three flat-coloured boxes and the keys one dark box.
Every face of the register is now a quad naming a tile in ONE painted image
(`paint_art`): a chamfered body, a deck with the shadows of what stands on
it, a block of bevelled keys carrying their digits, a dark pole head. The
windows are single quads on the display image, which now paints its own
bezel shadow, a dot-segment face and its bloom (`register_forms.paint_screen`).

WHAT THAT COSTS, said rather than implied: the painted register is one more
object on a counter module -- ``Counter_RegisterArt``, one draw for every
station on it. On the `bar` form it replaces two flat materials
(``M_Counter_register``, ``M_Counter_registerkeys``); on the `service` form
the register's boxes used to ride in the counter's shared plastic, so there
it is one draw more than before.
"""
from __future__ import annotations

from . import card_art as CA
from . import counter_lottery as CL
from . import machine_parts as MP
from . import paint as PT
from . import register_forms as RF

#: The register: a beige box with a keyboard deck and a display hump, 1997
#: and not a touch terminal (moved here from `back_bar_forms`, which
#: re-exports them).
REG_W = 0.30
REG_D = 0.34
REG_H = 0.12
REG_SCREEN_H = 0.13
HUMP_IN_X = 0.03
#: The hump's depth from the register's CUSTOMER edge, and the keypad's
#: span: from this far past the customer edge to this far short of the
#: staff edge. The same 0.07 m hump and 0.18 m keypad as before, mirrored.
HUMP_Y = (0.02, 0.09)
KEYS_Y = (0.13, 0.03)
KEYS_IN_X = 0.035
#: The key block stands this far off the deck.
KEYS_UP = 0.008
#: A window: inset in x inside the hump, its bottom this far over the body
#: and its top this far under the hump's; proud of the face it is on.
WIN_IN_X = 0.02
WIN_Z = (0.035, 0.025)
PROUD = 0.003
#: The pole display: a stalk from the hump's top and a box on it.
STALK_W, STALK_D = 0.024, 0.020
POLE_UP = 0.13
POLE_W, POLE_D, POLE_H = 0.17, 0.045, 0.06
POLE_WIN_IN = (0.012, 0.010)          # x, z
#: Broken vertical corners: the body's, the hump's, the pole head's.
BODY_C, HUMP_C, HEAD_C = 0.012, 0.008, 0.005
TEXEL = RF.TEXEL
PAINT_TEXEL = RF.PAINT_TEXEL
#: 1.54.0: the hump's customer window is gone. The walker, 2026-10-02, on
#: run 9137's frame: "i think we only need 1 set of numbers/face of the
#: price per register facing the customer" -- the pole reads to the
#: customer, the hump's back to the clerk, and the hump's front is plastic.
REGIONS = ("operator", "pole")
#: The two material keys a station's prims carry: the painted image and the
#: lit one.
PAINT, VFD = "regpaint", "vfd"
#: Putty plastic and the pole head's dark, 8-bit sRGB. MATCHED TO A FRAME,
#: not converted: the boxes were built in 0.60 / 0.57 / 0.48 linear, which is
#: 203 / 199 / 184 through the sRGB curve -- and painted that, the till came
#: out near white beside the same till in its flat plastic under the same
#: lamp (the flat material is skinned and grimed on the way in; a painted
#: one is not). This is the putty the flat till showed.
BEIGE = (170, 162, 140)
DARK = (40, 40, 44)
#: The keys as the clerk reads them, row by row: a digit, or a colour.
KEY_ROWS = (("", "", "7", "8", "9", "y"),
            ("", "", "4", "5", "6", ""),
            ("", "", "1", "2", "3", ""),
            ("r", "", "0", "00", ".", "g"))
KEY_TINTS = {"y": (214, 178, 48), "r": (190, 60, 52), "g": (60, 150, 84)}
KEY_FACE = (226, 222, 208)


def window(part, x0, x1, y, z0, z1, region, toward_plus_y=False):
    """A lit window: one quad facing -Y (or +Y), every corner
    ``(region, u, v)`` into the display image.

    SEEN FROM +Y, +X IS ON THE VIEWER'S LEFT, so a +Y window is wound from
    x1 to x0; wound like a -Y face its digits read mirrored."""
    xa, xb = (x1, x0) if toward_plus_y else (x0, x1)
    p = MP.quad(part, VFD, region, [(xa, y, z0), (xb, y, z0), (xb, y, z1), (xa, y, z1)])
    p["uvs"] = [tuple((region, u, v) for u, v in p["uvs"][0])]
    del p["tile"]
    return p


def hump(ax, ry, h):
    """``(x0, y0, z0, x1, y1, z1)`` of the display hump at a station."""
    y0 = ry - REG_D / 2.0
    return (ax - REG_W / 2.0 + HUMP_IN_X, y0 + HUMP_Y[0], h + REG_H - 0.004,
            ax + REG_W / 2.0 - HUMP_IN_X, y0 + HUMP_Y[1], h + REG_H + REG_SCREEN_H)


def _clerk(p, face=None):
    """Turn a face-up tile round so the clerk at +Y reads it
    (`register_forms._clerk`): ``face`` alone, or every face."""
    q = dict(p)
    q["uvs"] = [tuple((1.0 - u, 1.0 - v) for u, v in f) if face in (None, k) else f
                for k, f in enumerate(p["uvs"])]
    return q


def station(ax, ry, h):
    """``(painted, lit)``: one register at station x ``ax``, its depth centred
    on ``ry``, standing on a top at ``h``. ``painted`` prims are ``mat``
    `PAINT`, each face naming a ``tile`` of `paint_art`; ``lit`` are `window`
    quads, ``mat`` `VFD`."""
    x0, x1 = ax - REG_W / 2.0, ax + REG_W / 2.0
    y0, y1 = ry - REG_D / 2.0, ry + REG_D / 2.0
    zt = h + REG_H
    body = MP.cbody("Counter_Register", x0, x1, y0, y1, h - 0.004, zt, BODY_C,
                    side="reg_side", edge="reg_edge", top="reg_deck", mat=PAINT)
    body[-1] = _clerk(body[-1])
    hx0, hy0, hz0, hx1, hy1, hz1 = hump(ax, ry, h)
    painted = body + MP.cbody("Counter_RegisterHump", hx0, hx1, hy0, hy1, hz0, hz1, HUMP_C,
                              side="reg_side", edge="reg_edge", top="reg_top", mat=PAINT)
    # the key block, standing off the deck at the clerk's end
    ky0, ky1 = y0 + KEYS_Y[0], y1 - KEYS_Y[1]
    keys = MP.cap("Counter_RegisterKeys", "reg_keys", ax, ((ky0 + ky1) / 2.0 - y0) / REG_D,
                  (y0, zt, y1, zt), (REG_W - 2.0 * KEYS_IN_X, ky1 - ky0, KEYS_UP), mat=PAINT)
    painted.append(_clerk(keys, 0))
    wx0, wx1 = hx0 + WIN_IN_X, hx1 - WIN_IN_X
    wz0, wz1 = zt + WIN_Z[0], hz1 - WIN_Z[1]
    lit = [window("Counter_RegisterScreen", wx0, wx1, hy1 + PROUD, wz0, wz1, "operator", True)]
    # the pole: the stalk up from the hump's centre into the head's floor
    sy = (hy0 + hy1) / 2.0
    pz0 = hz1 + POLE_UP
    sx0, sx1, sy0, sy1 = ax - STALK_W / 2.0, ax + STALK_W / 2.0, sy - STALK_D / 2.0, sy + STALK_D / 2.0
    for name, a, b in (("front", (sx0, sy0), (sx1, sy0)), ("right", (sx1, sy0), (sx1, sy1)),
                       ("back", (sx1, sy1), (sx0, sy1)), ("left", (sx0, sy1), (sx0, sy0))):
        painted.append(MP.quad(f"Counter_RegisterPole_{name}", PAINT, "reg_side",
                               [(a[0], a[1], hz1 - 0.004), (b[0], b[1], hz1 - 0.004),
                                (b[0], b[1], pz0 + 0.004), (a[0], a[1], pz0 + 0.004)]))
    px0, px1 = ax - POLE_W / 2.0, ax + POLE_W / 2.0
    py0, py1 = sy - POLE_D / 2.0, sy + POLE_D / 2.0
    head = MP.cbody("Counter_RegisterHead", px0, px1, py0, py1, pz0, pz0 + POLE_H, HEAD_C,
                    side="head_side", edge="head_edge", top="head_top", mat=PAINT)
    painted += head
    painted.append(MP.poly("Counter_RegisterHead_under", PAINT, "head_side",
                           [(x, y, pz0) for x, y, _z in reversed(head[-1]["verts"])]))
    lit.append(window("Counter_RegisterScreen", px0 + POLE_WIN_IN[0], px1 - POLE_WIN_IN[0],
                      py0 - PROUD, pz0 + POLE_WIN_IN[1], pz0 + POLE_H - POLE_WIN_IN[1], "pole"))
    return painted, lit


def window_px():
    """``{region: (w_px, h_px)}``: every window at `TEXEL`, from the same
    numbers `station` builds with."""
    ww = REG_W - 2.0 * HUMP_IN_X - 2.0 * WIN_IN_X
    wh = (REG_SCREEN_H + REG_H) - (REG_H + WIN_Z[0]) - WIN_Z[1]
    pw = POLE_W - 2.0 * POLE_WIN_IN[0]
    ph = POLE_H - 2.0 * POLE_WIN_IN[1]
    px = lambda m: max(8, int(round(m * TEXEL)))  # noqa: E731
    return {"operator": (px(ww), px(wh)), "pole": (px(pw), px(ph))}


def art(price):
    """ONE image for every window on a counter: the three displays and a
    dark block, packed with a gutter each bleeds into (the image is sampled
    with filtering). ``{canvas, size, rects, name, said}``; ``said`` is each
    window's ``(text, cap_px)``. The operator reads the item count before
    the amount, as the Fujitsu's does."""
    sizes = window_px()
    tiles, said = [], {}
    for region in REGIONS:
        w, h = sizes[region]
        forms = RF._price_forms(price)
        if region == "operator":
            forms = ["1  " + price] + forms
        text, cap = RF.digits_fit(forms, w, h)
        tiles.append((region, RF.paint_screen(text, cap, w, h)))
        said[region] = (text, cap)
    tiles.append(("bezel", PT.Img(8, 8, RF.VFD_GROUND).to_canvas()))
    A = CA.atlas(tiles, f"vfd_{price.replace('.', '_')}", gutter=CA.SMOOTH_GUTTER, bleed=True)
    A["said"] = said
    return A


# --- the painted register --------------------------------------------------------


def _ppx(m):
    return max(8, int(round(m * PAINT_TEXEL)))


def paint_deck():
    """The body's top as the clerk sees it -- the image's top edge is the
    customer's: putty plastic, the shadow of the hump and of the key block
    where each stands, the printer's lid between them with its paper mouth."""
    W, H = _ppx(REG_W), _ppx(REG_D)
    im = RF._plastic(W, H, BEIGE, 31, 8, -10, 0.16)
    sx, sy = W / REG_W, H / REG_D

    def shadow(xa, ya, xb, yb, grow):
        im.rrect((xa * sx - grow, ya * sy - grow, xb * sx + grow, yb * sy + grow * 2.2),
                 grow, (0, 0, 0), 0.5)

    shadow(HUMP_IN_X, HUMP_Y[0], REG_W - HUMP_IN_X, HUMP_Y[1], 4)
    shadow(KEYS_IN_X, KEYS_Y[0], REG_W - KEYS_IN_X, REG_D - KEYS_Y[1], 4)
    im.blur((0, 0, W, H), 3)
    # the printer's lid: a seam across the deck between hump and keys, and
    # the mouth a receipt leaves by, on the clerk's left (the image's left)
    ya = (HUMP_Y[1] + 0.010) * sy
    im.rect((W * 0.05, ya, W * 0.95, ya + 1.5), RF._lift(BEIGE, -46))
    im.rect((W * 0.05, ya + 1.5, W * 0.95, ya + 2.5), RF._lift(BEIGE, 24), 0.5)
    mouth = (W * 0.10, ya + 6, W * 0.44, ya + 11)
    im.rrect(mouth, 2, (10, 10, 12))
    im.bevel(mouth, 2, 20.0, 34.0, raised=False)
    return im.to_canvas()


def paint_keys():
    """The key block's top as the clerk reads it: `KEY_ROWS` of bevelled
    keys on a dark plate, digits on the number block, three coloured."""
    W, H = _ppx(REG_W - 2.0 * KEYS_IN_X), _ppx(REG_D - KEYS_Y[0] - KEYS_Y[1])
    im = PT.Img(W, H, (38, 38, 42))
    rows, cols = len(KEY_ROWS), len(KEY_ROWS[0])
    mx, my = W * 0.04, H * 0.05
    px, py = (W - 2 * mx) / cols, (H - 2 * my) / rows
    gap = max(1.5, min(px, py) * 0.09)
    for r, row in enumerate(KEY_ROWS):
        for c, what in enumerate(row):
            box = (mx + c * px + gap, my + r * py + gap, mx + (c + 1) * px - gap, my + (r + 1) * py - gap)
            bh = box[3] - box[1]
            rgb = KEY_TINTS.get(what, KEY_FACE)
            rad = min(box[2] - box[0], bh) * 0.16
            im.rrect((box[0] + 1, box[1] + 2, box[2] + 1, box[3] + 2.5), rad, (0, 0, 0), 0.55)
            im.rrect(box, rad, rgb)
            im.vgrad((box[0] + 2, box[1] + 2, box[2] - 2, box[3] - 2), RF._lift(rgb, 14), RF._lift(rgb, -18))
            im.bevel(box, 2, 20.0, 44.0)
            if what and what not in KEY_TINTS:
                im.text(what, (box[0] + 2, box[1] + bh * 0.22, box[2] - 2, box[3] - bh * 0.22),
                        (30, 30, 34), RF.LEGEND_FACE)
    im.edge_dark((0, 0, W, H), min(W, H) * 0.06, 0.3)
    return im.to_canvas()


_PAINT = []


def paint_art():
    """The painted register's ONE image, the same for every station on
    every counter -- so it is painted once and every counter shares it:
    ``{canvas, size, rects, name, unset}``. It also holds what else stands
    painted on a counter's top beside a till: `counter_lottery`'s tickets
    and case (1.47.0), which ride in the till's draw."""
    if not _PAINT:
        tiles = [
            ("reg_deck", paint_deck()),
            ("reg_keys", paint_keys()),
            ("reg_side", RF._plastic(64, 64, BEIGE, 32, 14, -30, 0.14).to_canvas()),
            ("reg_edge", RF._plastic(16, 64, RF._lift(BEIGE, 14), 33, 14, -26, 0.0).to_canvas()),
            ("reg_top", RF._plastic(48, 32, RF._lift(BEIGE, 8), 34, 4, -4, 0.2).to_canvas()),
            ("head_side", RF._plastic(48, 32, DARK, 35, 14, -16, 0.16).to_canvas()),
            ("head_edge", RF._plastic(16, 32, RF._lift(DARK, 18), 36, 14, -16, 0.0).to_canvas()),
            ("head_top", RF._plastic(48, 32, RF._lift(DARK, 10), 37, 4, -4, 0.2).to_canvas()),
        ] + CL.tiles()
        A = CA.atlas(tiles, "counter_register", gutter=CA.SMOOTH_GUTTER, bleed=True)
        A["unset"] = [s for _k, c in tiles for s in getattr(c, "unset", [])]
        _PAINT.append(A)
    return _PAINT[0]
