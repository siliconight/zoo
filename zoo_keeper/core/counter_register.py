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
  * the OPERATOR display on the hump's staff face and the CUSTOMER display
    on its customer face, both green type on black;
  * the POLE DISPLAY: a stalk from the hump's top and a dark box on it, its
    window facing the customer, as the Sharp's and the TEC's stand.

GLOWING WITHOUT A LIGHT. The three windows are one backlit image,
`M_Counter_VFD_<art>_Face` in the recipe (the `_Face` suffix is what Lux's
power cut takes), at `register_forms.SCREEN_EMISSION` -- the strength 1.0.0
chose for this exact screen by measured saturation. The type and the
colours are `register_forms`' own (`paint_screen`, `VFD_INK`), so a till
in the card shop and a till on a store counter read as one make.

COST: one submission a counter module, whatever its register count -- the
windows of every station on it are one object on one image. The pole and
stalk go into the counter's existing plastic.
"""
from __future__ import annotations

import zlib

from . import prims as P
from . import register_forms as RF
from .vending_forms import Canvas

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
#: A window: inset in x inside the hump, its bottom this far over the body
#: and its top this far under the hump's; proud of the face, and sunk.
WIN_IN_X = 0.02
WIN_Z = (0.035, 0.025)
PROUD = 0.003
SINK = 0.004
#: The pole display: a stalk from the hump's top and a box on it.
STALK_W, STALK_D = 0.024, 0.020
POLE_UP = 0.13
POLE_W, POLE_D, POLE_H = 0.17, 0.045, 0.06
POLE_WIN_IN = (0.012, 0.010)          # x, z
TEXEL = RF.TEXEL
REGIONS = ("customer", "operator", "pole")


def screen_box(part, lo, hi, region, face):
    """A window: face ``face`` (P.box order: 2 is -Y, 4 is +Y) maps onto
    ``region`` of the display image, the rest take the bezel.

    SEEN FROM +Y, +X IS ON THE VIEWER'S LEFT, so a +Y window runs u from
    x1 to x0; mapped like a -Y face its digits read mirrored."""
    p = P.box(part, "vfd", lo, hi)
    x0, _y0, z0 = lo
    x1, _y1, z1 = hi

    def uv(i):
        x, _y, z = p["verts"][i]
        u = (x - x0) / (x1 - x0)
        return (region, 1.0 - u if face == 4 else u, (z - z0) / (z1 - z0))
    p["uvs"] = [tuple(uv(i) for i in f) if k == face else tuple(("bezel",) for _ in f)
                for k, f in enumerate(p["faces"])]
    return p


def hump(ax, ry, h):
    """``(x0, y0, z0, x1, y1, z1)`` of the display hump at a station."""
    y0 = ry - REG_D / 2.0
    return (ax - REG_W / 2.0 + HUMP_IN_X, y0 + HUMP_Y[0], h + REG_H - 0.004,
            ax + REG_W / 2.0 - HUMP_IN_X, y0 + HUMP_Y[1], h + REG_H + REG_SCREEN_H)


def station(ax, ry, h):
    """``(solid, lit)``: one register at station x ``ax``, its depth centred
    on ``ry``, standing on a top at ``h``. ``solid`` keys are ``beige`` and
    ``key_dark``, the ones both counters already build; ``lit`` are
    `screen_box` windows, ``mat`` ``vfd``."""
    y0, y1 = ry - REG_D / 2.0, ry + REG_D / 2.0
    solid = [P.box("Counter_Register", "beige", (ax - REG_W / 2.0, y0, h - 0.004),
                   (ax + REG_W / 2.0, y1, h + REG_H))]
    hx0, hy0, hz0, hx1, hy1, hz1 = hump(ax, ry, h)
    solid.append(P.box("Counter_Register", "beige", (hx0, hy0, hz0), (hx1, hy1, hz1)))
    solid.append(P.box("Counter_RegisterKeys", "key_dark",
                       (ax - REG_W / 2.0 + 0.035, y0 + KEYS_Y[0], h + REG_H - 0.006),
                       (ax + REG_W / 2.0 - 0.035, y1 - KEYS_Y[1], h + REG_H + 0.004)))
    wx0, wx1 = hx0 + WIN_IN_X, hx1 - WIN_IN_X
    wz0, wz1 = h + REG_H + WIN_Z[0], hz1 - WIN_Z[1]
    lit = [screen_box("Counter_RegisterScreen", (wx0, hy0 - PROUD, wz0), (wx1, hy0 + SINK, wz1), "customer", 2),
           screen_box("Counter_RegisterScreen", (wx0, hy1 - SINK, wz0), (wx1, hy1 + PROUD, wz1), "operator", 4)]
    # the pole: the stalk up from the hump's centre into the box's floor
    sy = (hy0 + hy1) / 2.0
    pz0 = hz1 + POLE_UP
    solid.append(P.box("Counter_RegisterPole", "beige", (ax - STALK_W / 2.0, sy - STALK_D / 2.0, hz1 - 0.004),
                       (ax + STALK_W / 2.0, sy + STALK_D / 2.0, pz0 + 0.004)))
    # its own part: a part built from two keys comes back from Blender as
    # `Counter_RegisterPole.001` when a recipe builds key by key
    solid.append(P.box("Counter_RegisterHead", "key_dark", (ax - POLE_W / 2.0, sy - POLE_D / 2.0, pz0),
                       (ax + POLE_W / 2.0, sy + POLE_D / 2.0, pz0 + POLE_H)))
    lit.append(screen_box("Counter_RegisterScreen",
                          (ax - POLE_W / 2.0 + POLE_WIN_IN[0], sy - POLE_D / 2.0 - PROUD, pz0 + POLE_WIN_IN[1]),
                          (ax + POLE_W / 2.0 - POLE_WIN_IN[0], sy - POLE_D / 2.0 + SINK, pz0 + POLE_H - POLE_WIN_IN[1]),
                          "pole", 2))
    return solid, lit


def window_px():
    """``{region: (w_px, h_px)}``: every window at `TEXEL`, from the same
    numbers `station` builds with."""
    ww = REG_W - 2.0 * HUMP_IN_X - 2.0 * WIN_IN_X
    wh = (REG_SCREEN_H + REG_H) - (REG_H + WIN_Z[0]) - WIN_Z[1]
    pw = POLE_W - 2.0 * POLE_WIN_IN[0]
    ph = POLE_H - 2.0 * POLE_WIN_IN[1]
    px = lambda m: max(8, int(round(m * TEXEL)))  # noqa: E731
    return {"customer": (px(ww), px(wh)), "operator": (px(ww), px(wh)), "pole": (px(pw), px(ph))}


def art(price):
    """ONE image for every window on a counter: the three displays stacked,
    then a bezel block. ``{canvas, size, rects, name, said}``. The operator
    reads the item count before the amount, as the Fujitsu's does."""
    sizes = window_px()
    W = max(w for w, _h in sizes.values())
    H = sum(h for _w, h in sizes.values()) + 6
    c = Canvas(W, H, RF.VFD_GROUND)
    rects, said = {}, {}
    y = 0
    for region in REGIONS:
        w, h = sizes[region]
        forms = RF._price_forms(price)
        if region == "operator":
            forms = ["1  " + price] + forms
        text, scale = RF.digits_layout(forms, w, h)
        c.paste(RF.paint_screen(text, scale, w, h), 0, y)
        rects[region] = (0, y, w, y + h)
        said[region] = (text, scale)
        y += h
    rects["bezel"] = (0, y + 1, 4, y + 5)
    c.rect(*rects["bezel"], RF.VFD_GROUND)
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H), "rects": rects, "said": said,
            "name": f"vfd_{price.replace('.', '_')}_{W}x{H}_{digest:08x}"}
