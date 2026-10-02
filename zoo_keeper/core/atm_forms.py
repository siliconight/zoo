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

from . import machine_parts as MP
from . import paint as PT
from . import prims as P
from . import shutters as SH

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
SCREEN_INSET = 0.020
#: THE REAL LOOK (1.46.0), the video-poker cabinet's three moves
#: (`video_poker_forms`): art at three times the density in a smooth face,
#: sampled with filtering; shading painted in; and the shape of a made
#: thing, from `machine_parts`.
PAINT_TEXEL = 768
GLOW_TEXEL = 640
TEXEL = 256                      # the small plain tiles
CHAMFER = 0.018
KICK_IN = (0.02, 0.03)
TOPPER_PROUD = 0.025
BEZEL_M = 0.012
BULGE = 0.007
SCREEN_GRID = (6, 4)
#: The raised key block and the function keys beside it: across, along the
#: ledge, standing off it; and where each sits on the ledge (x as a fraction
#: of the width, t up the slope).
KEYS = (0.130, 0.090, 0.006)
FKEYS = (0.060, 0.090, 0.006)
KEYS_AT = (-0.20, 0.50)
KEY_GAP = 0.012
#: THE SCREEN CYCLES (1.45.0): its greeting and INSERT CARD take turns, half
#: of this period each.
CYCLE_PERIOD_S = 3.0
#: A closed shutter's colour: the tube's dark green.
SHUTTER_RGB = (5, 20, 9)


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def plan(w, d, h, variant=0, sign=True):
    """``{"prims", "tiles", "collision", "facts"}``: prims carry ``mat``
    "paint", "glow" or "shutter", and the first two a ``tile``; ``tiles``
    maps each tile to its ``(atlas, spec)``."""
    v = int(variant) % len(NETWORKS)
    net, greet = NETWORKS[v]
    y0, y1 = -d / 2.0, d / 2.0
    x0, x1 = -w / 2.0, w / 2.0
    zp, zs0, zs1, zh = h * PLINTH, h * SHELF_LO, h * SHELF_HI, (h * HEAD_TOP if sign else h)
    yh = y0 + d * SET_BACK                           # the head's front
    c = min(CHAMFER, w * 0.04)
    prims = []
    prims += MP.kick("ATM", x0, x1, y0, y1, zp, KICK_IN)
    # the cabinet, its front the fascia between the chamfers
    prims += MP.cbody("ATM_Cabinet", x0, x1, y0, y1, zp, zs0, c, skip=("front", "top"))
    prims.append(MP.quad("ATM_Fascia", "paint", "fascia",
                         [(x0 + c, y0, zp), (x1 - c, y0, zp), (x1 - c, y0, zs0), (x0 + c, y0, zs0)]))
    # the keypad ledge: a slope from the fascia's top edge back to the head,
    # the key block and the function keys standing off it
    prims.append(MP.quad("ATM_Keypad", "paint", "keypad",
                         [(x0, y0, zs0), (x1, y0, zs0), (x1, yh, zs1), (x0, yh, zs1)]))
    prims.append(MP.wedge("ATM_LedgeSideL", "paint", "side", x0, y0, yh, zs0, zs1, True))
    prims.append(MP.wedge("ATM_LedgeSideR", "paint", "side", x1, y0, yh, zs0, zs1, False))
    ledge = (y0, zs0, yh, zs1)
    run = ((yh - y0) ** 2 + (zs1 - zs0) ** 2) ** 0.5
    k = key_scale(w, run)
    for part, tile, size, cx, t in key_places(w, k):
        prims.append(MP.cap(part, tile, cx, t, ledge, size, mat="paint"))
    # the head: its front a bezel sloping in to the tube
    prims += MP.cbody("ATM_Head", x0, x1, yh, y1, zs0, zh, c,
                      skip=("front", "top") if sign else ("front",))
    sw, sh = w * 0.70, (zh - zs1) * 0.60
    sx0, sx1 = -sw / 2.0, sw / 2.0
    sz0 = zs1 + (zh - zs1) * 0.21
    sz1 = sz0 + sh
    m = BEZEL_M
    hole, screen = (sx0 - m, sx1 + m, sz0 - m, sz1 + m), (sx0, sx1, sz0, sz1)
    yi = yh + SCREEN_INSET
    prims += MP.bezel("ATM", x0 + c, x1 - c, zs0, zh, hole, yh)
    prims += MP.wells("ATM", hole, screen, yh, yi)
    prims.append(MP.curved_screen("ATM_Screen", screen, yi, BULGE, SCREEN_GRID))
    # THE CYCLE: the greeting and the line under it take turns. A tube too
    # small for two lines shows its one line and has no shutter.
    wpx, hpx = _gpx(sw), _gpx(sh)
    lines, pad, band = crt_bands(hpx, greet)
    if len(lines) >= 2:
        flat = [(sx0, yi, sz0), (sx1, yi, sz0), (sx1, yi, sz1), (sx0, yi, sz1)]
        for i, (a, b) in enumerate(((0.0, 0.5), (0.5, 1.0))):
            top, foot = pad + i * band, pad + (i + 1) * band
            rect = (2.0 / wpx, max(0.0, 1.0 - foot / float(hpx)),
                    1.0 - 2.0 / wpx, min(1.0, 1.0 - top / float(hpx)))
            prims.append(SH.over("ATM_ScreenShutter", flat, rect, (a, b, CYCLE_PERIOD_S, 0.0),
                                 proud=BULGE + SH.PROUD))
    if sign:
        # the topper, overhanging the head: its front lit, its underside in shade
        yt = yh - TOPPER_PROUD
        prims += MP.cbody("ATM_Topper", x0, x1, yt, y1, zh, h, c, skip=("front",))
        prims.append(MP.quad("ATM_Sign", "glow", "topper",
                             [(x0 + c, yt, zh), (x1 - c, yt, zh), (x1 - c, yt, h), (x0 + c, yt, h)]))
        prims.append(MP.quad("ATM_TopperUnder", "paint", "kick",
                             [(x0, yh, zh), (x1, yh, zh), (x1, yt, zh), (x0, yt, zh)]))
    tiles = {
        "side": ("paint", {"kind": "atm_side", "w_m": 0.5, "h_m": 1.0, "variant": v}),
        "edge": ("paint", {"kind": "atm_edge", "w_m": 0.06, "h_m": 0.5, "variant": v}),
        "top": ("paint", {"kind": "atm_top", "w_m": 0.25, "h_m": 0.25, "variant": v}),
        "kick": ("paint", {"kind": "atm_kick", "w_m": 0.25, "h_m": 0.12, "variant": v}),
        "bezel": ("paint", {"kind": "atm_bezel", "w_m": 0.25, "h_m": 0.25, "variant": v}),
        "well": ("paint", {"kind": "atm_well", "w_m": 0.12, "h_m": 0.12, "variant": v}),
        "fascia": ("paint", {"kind": "atm_fascia", "w_m": w - 2 * c, "h_m": zs0 - zp, "variant": v}),
        "keypad": ("paint", {"kind": "atm_keypad", "w_m": w, "h_m": run, "variant": v, "k": k}),
        "keys": ("paint", {"kind": "atm_keys", "w_m": KEYS[0] * k, "h_m": KEYS[1] * k, "variant": v}),
        "fkeys": ("paint", {"kind": "atm_fkeys", "w_m": FKEYS[0] * k, "h_m": FKEYS[1] * k, "variant": v}),
        "screen": ("glow", {"kind": "atm_crt", "w_m": sw, "h_m": sh, "greet": greet, "variant": v}),
    }
    if sign:
        tiles["topper"] = ("glow", {"kind": "atm_topper", "w_m": w - 2 * c, "h_m": h - zh, "net": net,
                                    "variant": v})
    return {"prims": prims, "tiles": tiles,
            "collision": ((x0, y0, 0.0), (x1, y1, h)),
            "facts": {"network": net, "variant": v, "sign": bool(sign),
                      "tris": P.tri_count(prims), "materials": 3}}


# --- the art -----------------------------------------------------------------------------


def key_scale(w, run):
    """A narrow or shallow unit's keys are smaller than a full one's."""
    return min(1.0, w / 0.6, run / 0.14)


def key_places(w, k):
    """``[(part, tile, size, x, t)]``: the key block and the function keys
    beside it on the ledge. ONE derivation for the blocks and for the
    shadows the ledge's own tile paints under them."""
    kx = w * KEYS_AT[0]
    fx = kx + (KEYS[0] / 2.0 + KEY_GAP + FKEYS[0] / 2.0) * k
    return [("ATM_Keys", "keys", (KEYS[0] * k, KEYS[1] * k, KEYS[2]), kx, KEYS_AT[1]),
            ("ATM_FKeys", "fkeys", (FKEYS[0] * k, FKEYS[1] * k, FKEYS[2]), fx, KEYS_AT[1])]


def _px(m):
    return max(4, int(round(m * TEXEL)))


def _ppx(m):
    return max(8, int(round(m * PAINT_TEXEL)))


def _gpx(m):
    return max(8, int(round(m * GLOW_TEXEL)))


def crt_bands(h, greet):
    """``(lines, pad, band)`` for a tube ``h`` px tall: as many lines as it
    holds at a legible height, the greeting first; the margin above the
    first; and each line's band. ONE derivation for the painter and for the
    shutters (1.45.0)."""
    pad = max(4, h // 12)
    n = max(1, min(1 + len(SCREEN_LINES), (h - 2 * pad) // 22))
    lines = ((greet,) + SCREEN_LINES)[:n]
    return lines, pad, (h - 2 * pad) // len(lines)


def _lift(rgb, by):
    return tuple(max(0.0, min(255.0, c + by)) for c in rgb)


def _brushed(im, box, seed, strength=0.05):
    """Brushed steel: fine horizontal strokes, lighter and darker."""
    x0, y0, x1, y1 = [int(v) for v in box]
    for y in range(y0, y1):
        k = (_h("brush", seed, y) % 1000) / 1000.0 - 0.5
        im.shade((x0, y, x1, y + 1), 1.0 + k * 2.0 * strength)


def paint(spec):
    """One tile as a Canvas; ``c.unset`` lists every line that did not set."""
    kind = spec["kind"]
    v = int(spec.get("variant", 0)) % len(NETWORKS)
    if kind == "atm_side":
        # a brushed steel panel under a ceiling's light
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, BODY)
        im.vgrad((0, 0, w, h), _lift(BODY, 22), _lift(BODY, -34))
        _brushed(im, (0, 0, w, h), 1)
        im.edge_dark((0, 0, w, h), w * 0.18, 0.22)
        return im.to_canvas()
    if kind == "atm_edge":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, BODY)
        im.vgrad((0, 0, w, h), _lift(BODY, 60), _lift(BODY, 10))
        im.rect((w * 0.35, 0, w * 0.65, h), (255, 255, 255), 0.35)
        return im.to_canvas()
    if kind == "atm_top":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, _lift(BODY, -10))
        _brushed(im, (0, 0, w, h), 2)
        im.edge_dark((0, 0, w, h), w * 0.2, 0.2)
        return im.to_canvas()
    if kind == "atm_kick":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, (16, 16, 18))
        im.vgrad((0, 0, w, h), (10, 10, 12), (30, 30, 32))
        im.grain((0, 0, w, h), 3.0, 3)
        return im.to_canvas()
    if kind == "atm_bezel":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, TRIM)
        im.vgrad((0, 0, w, h), _lift(TRIM, 18), _lift(TRIM, -8))
        im.grain((0, 0, w, h), 1.6, 4)
        return im.to_canvas()
    if kind == "atm_well":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, (20, 20, 22))
        im.vgrad((0, 0, w, h), (3, 5, 4), (44, 44, 50))
        return im.to_canvas()
    if kind == "atm_keys":
        # the key block: a dark plate, four rows of three bevelled keys
        w, h = _ppx(spec["w_m"]), _ppx(spec["h_m"])
        im = PT.Img(w, h, (34, 34, 38))
        gx, gy = w * 0.06, h * 0.07
        kw, kh = (w - 4 * gx) / 3.0, (h - 5 * gy) / 4.0
        legends = "123456789*0#"
        for r in range(4):
            for col in range(3):
                x, y = gx + col * (kw + gx), gy + r * (kh + gy)
                box = (x, y, x + kw, y + kh)
                im.rrect(box, kh * 0.18, (206, 208, 212))
                im.vgrad((x + 2, y + 2, x + kw - 2, y + kh - 2), (232, 233, 236), (184, 186, 190))
                im.bevel(box, 2, 26.0, 46.0)
                im.text(legends[r * 3 + col], (x, y + kh * 0.16, x + kw, y + kh * 0.84), (30, 30, 34),
                        "highway_bold")
        im.edge_dark((0, 0, w, h), min(w, h) * 0.08, 0.3)
        return im.to_canvas()
    if kind == "atm_fkeys":
        # CANCEL, CLEAR, ENTER: red, yellow, green, with a blank under them
        w, h = _ppx(spec["w_m"]), _ppx(spec["h_m"])
        im = PT.Img(w, h, (34, 34, 38))
        gy = h * 0.07
        kh = (h - 5 * gy) / 4.0
        for r, rgb in enumerate(((204, 44, 44), (232, 200, 44), (44, 164, 74), (206, 208, 212))):
            y = gy + r * (kh + gy)
            box = (w * 0.10, y, w * 0.90, y + kh)
            im.rrect(box, kh * 0.18, rgb)
            im.vgrad((box[0] + 2, y + 2, box[2] - 2, y + kh - 2), _lift(rgb, 26), _lift(rgb, -22))
            im.bevel(box, 2, 26.0, 46.0)
        im.edge_dark((0, 0, w, h), min(w, h) * 0.08, 0.3)
        return im.to_canvas()
    if kind == "atm_keypad":
        # the ledge: dark plastic, the card reader with its green lamp, and
        # the shadow the key blocks stand in
        w, h = _ppx(spec["w_m"]), _ppx(spec["h_m"])
        k = float(spec.get("k", 1.0))
        im = PT.Img(w, h, (60, 62, 66))
        im.vgrad((0, 0, w, h), (78, 80, 86), (50, 52, 56))
        im.grain((0, 0, w, h), 1.6, 5)
        for _part, _tile, size, kx, kt in key_places(spec["w_m"], k):
            cx = w / 2.0 + kx / spec["w_m"] * w
            cy = h * (1.0 - kt)
            bw, bl = size[0] / spec["w_m"] * w, size[1] / spec["h_m"] * h
            im.rrect((cx - bw * 0.56, cy - bl * 0.52, cx + bw * 0.56, cy + bl * 0.62), bl * 0.08,
                     (6, 6, 8), 0.8)
        im.blur((0, 0, w, h), 2)
        # the card reader, right of the keys: a dark throat in a raised bezel
        rd = (w * 0.66, h * 0.30, w * 0.94, h * 0.62)
        im.rrect(rd, h * 0.05, (28, 28, 32))
        im.bevel(rd, 3, 40.0, 40.0)
        im.rrect((rd[0] + (rd[2] - rd[0]) * 0.10, rd[1] + (rd[3] - rd[1]) * 0.42,
                  rd[2] - (rd[2] - rd[0]) * 0.10, rd[1] + (rd[3] - rd[1]) * 0.60), 2, (2, 2, 3))
        im.disc(rd[0] + (rd[2] - rd[0]) * 0.86, rd[1] + (rd[3] - rd[1]) * 0.20, h * 0.022, (70, 250, 110))
        im.text("CARD", (rd[0], rd[3] + h * 0.03, rd[2], rd[3] + h * 0.20), (214, 214, 206), "highway_cond")
        im.edge_dark((0, 0, w, h), h * 0.22, 0.28)
        return im.to_canvas()
    if kind == "atm_fascia":
        w, h = _ppx(spec["w_m"]), _ppx(spec["h_m"])
        im = PT.Img(w, h, BODY)
        im.vgrad((0, 0, w, h), _lift(BODY, 18), _lift(BODY, -30))
        _brushed(im, (0, 0, w, h), 6)
        # THE CASH DISPENSER: a dark mouth behind a steel flap, its legend over it
        im.text(FASCIA_WORDS[0], (w * 0.18, h * 0.06, w * 0.82, h * 0.15), TRIM, "highway_bold")
        cash = (w * 0.14, h * 0.17, w * 0.86, h * 0.29)
        im.rrect(cash, h * 0.012, (52, 54, 58))
        im.bevel(cash, 3, 30.0, 50.0, raised=False)
        im.rrect((cash[0] + 8, cash[1] + (cash[3] - cash[1]) * 0.30, cash[2] - 8,
                  cash[1] + (cash[3] - cash[1]) * 0.70), 3, (8, 8, 10))
        # THE RECEIPT SLOT, smaller, to the right
        im.text(FASCIA_WORDS[1], (w * 0.54, h * 0.34, w * 0.90, h * 0.40), TRIM, "highway_cond")
        rc = (w * 0.56, h * 0.41, w * 0.88, h * 0.46)
        im.rrect(rc, 3, (40, 42, 46))
        im.bevel(rc, 2, 30.0, 46.0, raised=False)
        im.rrect((rc[0] + 6, rc[1] + (rc[3] - rc[1]) * 0.36, rc[2] - 6, rc[1] + (rc[3] - rc[1]) * 0.64),
                 2, (6, 6, 8))
        # THE SURCHARGE STICKER: yellow vinyl, a little crooked light on it
        st = (w * 0.10, h * 0.55, w * 0.60, h * 0.75)
        im.rrect((st[0] + 3, st[1] + 4, st[2] + 3, st[3] + 4), 4, (40, 40, 40), 0.35)      # its shadow
        im.rrect(st, 4, (250, 220, 40))
        im.vgrad((st[0] + 2, st[1] + 2, st[2] - 2, st[3] - 2), (255, 232, 70), (236, 200, 30))
        words = FASCIA_WORDS[2].split(" ")
        half = (len(words) + 1) // 2
        sh_ = st[3] - st[1]
        im.text(" ".join(words[:half]), (st[0] + 8, st[1] + sh_ * 0.10, st[2] - 8, st[1] + sh_ * 0.50),
                (30, 20, 10), "highway_bold")
        im.text(" ".join(words[half:]), (st[0] + 8, st[1] + sh_ * 0.52, st[2] - 8, st[1] + sh_ * 0.92),
                (30, 20, 10), "highway_bold")
        # the service door's seam and its lock, low on the cabinet
        im.rect((w * 0.06, h * 0.82, w * 0.94, h * 0.82 + 2), (90, 92, 96))
        im.rect((w * 0.06, h * 0.82 + 2, w * 0.94, h * 0.82 + 3), (224, 226, 230), 0.6)
        im.disc(w * 0.84, h * 0.90, w * 0.022, (150, 150, 156))
        im.disc(w * 0.84, h * 0.90, w * 0.008, (40, 40, 44))
        im.edge_dark((0, 0, w, h), w * 0.10, 0.25)
        return im.to_canvas()
    if kind == "atm_topper":
        w, h = _gpx(spec["w_m"]), _gpx(spec["h_m"])
        field, ink = TOPPER_INKS[v % len(TOPPER_INKS)]
        im = PT.Img(w, h, field)
        im.vgrad((0, 0, w, h), _lift(field, 32), _lift(field, -16))
        b = max(3, h // 16)
        im.rect((0, 0, w, b), ink)
        im.rect((0, h - b, w, h), ink)
        im.text("ATM", (w * 0.04, b * 2, w * 0.36, h - b * 2), ink, "highway_bold",
                shadow=_lift(field, -70))
        im.text(spec["net"], (w * 0.40, h * 0.22, w * 0.96, h * 0.78), ink, "highway_bold",
                shadow=_lift(field, -70))
        im.vignette((0, 0, w, h), 0.34)
        im.glow((0, 0, w, h), max(2, h // 30), 0.22)
        return im.to_canvas()
    if kind == "atm_crt":
        w, h = _gpx(spec["w_m"]), _gpx(spec["h_m"])
        im = PT.Img(w, h, CRT_BG)
        im.vgrad((0, 0, w, h), (8, 26, 12), (4, 14, 6))
        lines, pad, band = crt_bands(h, spec["greet"])
        for i, line in enumerate(lines):
            im.text(line, (w * 0.05, pad + i * band + band * 0.14, w * 0.95, pad + (i + 1) * band - band * 0.14),
                    CRT_INK, "highway_bold")
        # the tube: its phosphor spills, its lines show, its corners fall off
        im.glow((0, 0, w, h), max(2, h // 50), 0.36)
        im.scanlines((0, 0, w, h), 3, 0.18)
        im.vignette((0, 0, w, h), 0.40)
        return im.to_canvas()
    raise ValueError(f"atm: no tile kind {kind!r}")


def all_strings():
    out = ["ATM", "CARD"]
    for net, greet in NETWORKS:
        out += [net, greet]
    return out + list(SCREEN_LINES) + list(FASCIA_WORDS)
