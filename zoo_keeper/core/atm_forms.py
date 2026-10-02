"""A 1990s freestanding surcharge ATM: two atlases, two draws.

Zoo 1.35.0, species `atm`. The walker, 2026-09-29: "Convenient stores should
also have ATMs", with photographs of late-'90s units; the queue note kept from
them: free-standing, a lit ATM topper, a green-on-black CRT, a keypad. Until
this the species was a grey box with a dark glass panel and a pale slab on
top, four materials and six coincident face pairs (`test_coincident_faces`).

WHAT IS BUILT (metres, Z up, origin at the floor's centre, the customer at
-Y), from the bottom:

  plinth   a dark kick base, the slot's full footprint;
  cabinet  the lower body, its front the FASCIA: the cash dispenser and the
           receipt slot, the network stickers, a surcharge notice;
  shelf    the keypad ledge, sloped toward the customer, the keypad and the
           card slot painted on it;
  head     the screen housing, set back, its front a bezel round a recessed
           CRT;
  topper   the lit sign across the top: ATM, and the network's name.

TWO ATLASES, TWO MATERIALS, TWO DRAWS (CLAUDE.md: variation belongs in a
texture, never in another material). PAINT -- the cabinet's colour, the dark
trim, the fascia and the keypad -- is paper-like painted art lit by the room.
GLOW -- the CRT and the topper -- is its own light
(`materials.make_backlit_material`), named `_Face` so Lux's power cut takes
it with the lights.

EVERY NAME ON IT IS INVENTED: Delco slang, PG-13, held against the factory's
denylists (`tests/test_atm.py`). The walker's rule: invented brands on every
branded surface, no real marks -- and the Philadelphia area's own 1990s ATM
network is exactly the kind of real name this must not echo.
"""
from __future__ import annotations

import zlib

from . import prims as P
from . import shutters as SH
from .vending_forms import Canvas

#: The networks, by variant: topper line, screen greeting.
#: The greeting has to fit the CRT at one line of m5x7: the first cut's
#: "WELCOME TO CASH JAWN" did not, and `fit_text` drops a line it cannot set,
#: so three screens of four lost their first line (`tests/test_atm.py` now
#: asks every line of every tile to set).
NETWORKS = (
    ("CASH JAWN", "HEY. CASH JAWN."),
    ("YO MONEY", "YO. CARD IN."),
    ("QUIK KWIK CASH", "QUIK KWIK CASH"),
    ("MONEY BUCKET", "MONEY BUCKET"),
)
#: What the screen says under the greeting, in the CRT's green.
SCREEN_LINES = ("INSERT CARD", "SURCHARGE $1.50", "FEE IS FINAL")
#: The fascia's small print.
FASCIA_WORDS = ("TAKE CASH", "RECEIPT", "NO FEE ATM THIS AINT")
#: Topper fields, by variant: (field, ink).
TOPPER_INKS = (((24, 70, 150), (255, 244, 170)), ((150, 24, 30), (255, 250, 236)),
               ((20, 110, 60), (250, 250, 240)), ((40, 40, 46), (255, 210, 60)))
BODY = (182, 186, 190)          # brushed-grey cabinet
TRIM = (38, 38, 42)
CRT_BG, CRT_INK = (6, 18, 8), (90, 255, 120)
#: The backlit glow: emission and the diffuse copy, as the cooler's signs.
GLOW_EMISSION = 1.0
GLOW_ALBEDO = 0.6
#: Heights as fractions of the slot's, from a 1.45 m unit.
PLINTH = 0.06
SHELF_LO, SHELF_HI = 0.60, 0.67      # the keypad ledge
HEAD_TOP = 0.86                      # the housing; the topper above it
SET_BACK = 0.22                      # the head's front, of the depth
SCREEN_INSET = 0.012
TEXEL = 256
#: THE SCREEN CYCLES (1.45.0): its greeting and INSERT CARD take turns, half
#: of this period each.
CYCLE_PERIOD_S = 3.0
#: A closed shutter's colour: the tube's dark green, between its scanline rows.
SHUTTER_RGB = (4, 14, 6)


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def _quad(part, mat, tile, verts, uv=(0.0, 1.0, 0.0, 1.0)):
    """One textured quad: corners bottom-left, bottom-right, top-right,
    top-left as the viewer sees it; ``uv`` the part of its tile it shows."""
    p = P.mesh(part, mat, verts, [(0, 1, 2, 3)])
    u0, u1, v0, v1 = uv
    p["tile"] = tile
    p["uvs"] = [((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
    return p


def _box(part, mat, tile, lo, hi, skip=()):
    """A box whose faces all show ``tile`` whole; ``skip`` names faces that
    another quad covers ("front", "top", ...), so none is doubled."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    faces = {
        "front": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
        "back": [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
        "left": [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
        "right": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
        "top": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        "bottom": [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)],
    }
    return [_quad(f"{part}_{k}", mat, tile, v) for k, v in faces.items() if k not in skip]


def plan(w, d, h, variant=0, sign=True):
    """``{"prims", "tiles", "collision", "facts"}``: prims carry ``mat``
    "paint" or "glow" and a ``tile``; ``tiles`` maps each tile to its
    ``(atlas, spec)``."""
    v = int(variant) % len(NETWORKS)
    net, greet = NETWORKS[v]
    y0, y1 = -d / 2.0, d / 2.0
    x0, x1 = -w / 2.0, w / 2.0
    zp, zs0, zs1, zh = h * PLINTH, h * SHELF_LO, h * SHELF_HI, (h * HEAD_TOP if sign else h)
    yh = y0 + d * SET_BACK                           # the head's front
    prims = []
    # the plinth: trim, the full footprint
    prims += _box("ATM_Plinth", "paint", "trim", (x0, y0, 0.0), (x1, y1, zp), skip=("bottom",))
    # the cabinet: body colour; its front is the fascia
    prims += _box("ATM_Cabinet", "paint", "body", (x0, y0, zp), (x1, y1, zs0),
                  skip=("front", "bottom", "top"))
    prims.append(_quad("ATM_Fascia", "paint", "fascia",
                       [(x0, y0, zp), (x1, y0, zp), (x1, y0, zs0), (x0, y0, zs0)]))
    # the keypad ledge: a slope from the fascia's top edge back to the head
    prims.append(_quad("ATM_Keypad", "paint", "keypad",
                       [(x0, y0, zs0), (x1, y0, zs0), (x1, yh, zs1), (x0, yh, zs1)]))
    # the ledge's sides, closing the slope
    for x, side in ((x0, "L"), (x1, "R")):
        tri = [(x, y0, zs0), (x, yh, zs0), (x, yh, zs1)]
        if side == "L":                 # wound to face out: -X on the left, +X on the right
            tri = [tri[1], tri[0], tri[2]]
        t = P.mesh(f"ATM_LedgeSide{side}", "paint", tri, [(0, 1, 2)])
        t["tile"] = "body"
        t["uvs"] = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0))]
        prims.append(t)
    # under the ledge's back edge, the cabinet top from the head's front to the back
    prims.append(_quad("ATM_CabinetTop", "paint", "body",
                       [(x0, yh, zs0), (x1, yh, zs0), (x1, y1, zs0), (x0, y1, zs0)]))
    # the head: body, its front a bezel with the screen recessed in it
    prims += _box("ATM_Head", "paint", "body", (x0, yh, zs0), (x1, y1, zh),
                  skip=("front", "bottom", "top" if sign else ""))
    sw, sh = w * 0.72, (zh - zs1) * 0.62
    sx0, sx1 = -sw / 2.0, sw / 2.0
    sz0 = zs1 + (zh - zs1) * 0.20
    sz1 = sz0 + sh
    # the bezel: four strips round the screen's hole, and the hole's walls
    prims += [
        _quad("ATM_Bezel_B", "paint", "trim", [(x0, yh, zs0), (x1, yh, zs0), (x1, yh, sz0), (x0, yh, sz0)]),
        _quad("ATM_Bezel_T", "paint", "trim", [(x0, yh, sz1), (x1, yh, sz1), (x1, yh, zh), (x0, yh, zh)]),
        _quad("ATM_Bezel_L", "paint", "trim", [(x0, yh, sz0), (sx0, yh, sz0), (sx0, yh, sz1), (x0, yh, sz1)]),
        _quad("ATM_Bezel_R", "paint", "trim", [(sx1, yh, sz0), (x1, yh, sz0), (x1, yh, sz1), (sx1, yh, sz1)]),
    ]
    yi = yh + SCREEN_INSET
    # the recess's walls face INTO the hole (a first cut wound all four out:
    # the floor faced down, the sides away -- caught by a normal check)
    prims += [
        _quad("ATM_Well_B", "paint", "trim", [(sx0, yh, sz0), (sx1, yh, sz0), (sx1, yi, sz0), (sx0, yi, sz0)]),
        _quad("ATM_Well_T", "paint", "trim", [(sx0, yi, sz1), (sx1, yi, sz1), (sx1, yh, sz1), (sx0, yh, sz1)]),
        _quad("ATM_Well_L", "paint", "trim", [(sx0, yh, sz0), (sx0, yi, sz0), (sx0, yi, sz1), (sx0, yh, sz1)]),
        _quad("ATM_Well_R", "paint", "trim", [(sx1, yi, sz0), (sx1, yh, sz0), (sx1, yh, sz1), (sx1, yi, sz1)]),
        _quad("ATM_Screen", "glow", "screen", [(sx0, yi, sz0), (sx1, yi, sz0), (sx1, yi, sz1), (sx0, yi, sz1)]),
    ]
    # THE CYCLE: the greeting and the line under it take turns. A tube too
    # small for two lines shows its one line and has no shutter.
    wpx, hpx = _px(sw), _px(sh)
    lines, band = crt_bands(hpx, greet)
    if len(lines) >= 2:
        screen = [(sx0, yi, sz0), (sx1, yi, sz0), (sx1, yi, sz1), (sx0, yi, sz1)]
        for i, (a, b) in enumerate(((0.0, 0.5), (0.5, 1.0))):
            top, foot = 4 + i * band - 1, 4 + (i + 1) * band - 1
            rect = (2.0 / wpx, max(0.0, 1.0 - foot / float(hpx)),
                    1.0 - 2.0 / wpx, min(1.0, 1.0 - top / float(hpx)))
            prims.append(SH.over("ATM_ScreenShutter", screen, rect, (a, b, CYCLE_PERIOD_S, 0.0)))
    if sign:
        # the topper: the head's footprint, its front lit, its other sides body
        prims += _box("ATM_Topper", "paint", "trim", (x0, yh, zh), (x1, y1, h),
                      skip=("front", "bottom"))
        prims.append(_quad("ATM_Sign", "glow", "topper", [(x0, yh, zh), (x1, yh, zh), (x1, yh, h), (x0, yh, h)]))
    tiles = {
        "body": ("paint", {"kind": "atm_flat", "rgb": BODY, "w_m": 0.08, "h_m": 0.08}),
        "trim": ("paint", {"kind": "atm_flat", "rgb": TRIM, "w_m": 0.08, "h_m": 0.08}),
        "fascia": ("paint", {"kind": "atm_fascia", "w_m": w, "h_m": zs0 - zp, "variant": v}),
        "keypad": ("paint", {"kind": "atm_keypad", "w_m": w, "h_m": ((zs1 - zs0) ** 2 + (yh - y0) ** 2) ** 0.5,
                             "variant": v}),
        "screen": ("glow", {"kind": "atm_crt", "w_m": sw, "h_m": sh, "greet": greet, "variant": v}),
    }
    if sign:
        tiles["topper"] = ("glow", {"kind": "atm_topper", "w_m": w, "h_m": h - zh, "net": net, "variant": v})
    return {"prims": prims, "tiles": tiles,
            "collision": ((x0, y0, 0.0), (x1, y1, h)),
            "facts": {"network": net, "variant": v, "sign": bool(sign),
                      "tris": P.tri_count(prims), "materials": 2}}


# --- the art -----------------------------------------------------------------------------


def _px(m):
    return max(4, int(round(m * TEXEL)))


def crt_bands(h, greet):
    """``(lines, band)`` for a tube ``h`` px tall: as many lines as it holds
    at 9 px a line, the greeting first, and each line's band height. ONE
    derivation for the painter and for the shutters (1.45.0)."""
    lines = ((greet,) + SCREEN_LINES)[:max(1, (h - 8) // 9)]
    return lines, (h - 8) // len(lines)


def paint(spec):
    """One tile as a Canvas."""
    from .poster_art import fit_text
    w, h = _px(spec["w_m"]), _px(spec["h_m"])
    kind = spec["kind"]
    v = int(spec.get("variant", 0))
    if kind == "atm_flat":
        return Canvas(w, h, spec["rgb"])
    if kind == "atm_crt":
        c = Canvas(w, h, CRT_BG)
        # scanlines: every other row a step darker, the tube's own texture
        for y in range(0, h, 2):
            c.rect(0, y, w, y + 1, (3, 10, 4))
        # as many lines as the tube holds at 9 px a line, the greeting first:
        # at the genome's smallest unit the screen is 36 px tall, and four
        # lines set none (`fit_text` drops what it cannot fit)
        lines, band = crt_bands(h, spec["greet"])
        c.unset = [line for i, line in enumerate(lines)
                   if fit_text(c, line, (4, 4 + i * band, w - 4, 4 + (i + 1) * band - 2), CRT_INK,
                               face="m5x7", cap=2) is None]
        return c
    if kind == "atm_topper":
        field, ink = TOPPER_INKS[v % len(TOPPER_INKS)]
        c = Canvas(w, h, field)
        c.rect(0, 0, w, 3, ink)
        c.rect(0, h - 3, w, h, ink)
        c.unset = [t for t, box, face, cap in (("ATM", (4, 3, w * 0.42, h - 3), "bold", 4),
                                               (spec["net"], (w * 0.44, 5, w - 4, h - 5), "m5x7", 2))
                   if fit_text(c, t, box, ink, face=face, cap=cap) is None]
        return c
    if kind == "atm_keypad":
        c = Canvas(w, h, (60, 62, 66))
        # a 4 x 3 key block, the function keys beside it, the card slot
        kx0, ky0 = int(w * 0.12), int(h * 0.18)
        kw, kh = int(w * 0.10), int(h * 0.16)
        for r in range(4):
            for col in range(3):
                x, y = kx0 + col * (kw + 3), ky0 + r * (kh + 2)
                c.rect(x, y, x + kw, y + kh, (200, 202, 206))
        for r, rgb in enumerate(((200, 40, 40), (230, 200, 40), (40, 160, 70))):
            x, y = kx0 + 3 * (kw + 3) + 6, ky0 + r * (kh + 2)
            c.rect(x, y, x + int(kw * 1.6), y + kh, rgb)
        c.rect(int(w * 0.70), int(h * 0.30), int(w * 0.92), int(h * 0.30) + 4, TRIM)
        return c
    if kind == "atm_fascia":
        c = Canvas(w, h, BODY)
        c.rect(int(w * 0.18), int(h * 0.20), int(w * 0.82), int(h * 0.20) + 6, TRIM)   # cash
        c.rect(int(w * 0.62), int(h * 0.42), int(w * 0.84), int(h * 0.42) + 3, TRIM)   # receipt
        # the surcharge sticker, yellow
        sx, sy = int(w * 0.10), int(h * 0.55)
        c.rect(sx, sy, sx + int(w * 0.48), sy + int(h * 0.20), (250, 220, 40))
        c.unset = [t for t, box, rgb in (
            (FASCIA_WORDS[0], (int(w * 0.18), int(h * 0.08), int(w * 0.82), int(h * 0.19)), TRIM),
            (FASCIA_WORDS[1], (int(w * 0.50), int(h * 0.33), int(w * 0.96), int(h * 0.41)), TRIM),
            (FASCIA_WORDS[2], (sx + 2, sy + 2, sx + int(w * 0.48) - 2, sy + int(h * 0.20) - 2),
             (30, 20, 10)))
                   if fit_text(c, t, box, rgb, face="m5x7", cap=1) is None]
        return c
    raise ValueError(f"atm: no tile kind {kind!r}")


def all_strings():
    out = []
    for net, greet in NETWORKS:
        out += [net, greet]
    return out + list(SCREEN_LINES) + list(FASCIA_WORDS)
