"""A 1997 tavern video-poker cabinet, "for amusement only": two atlases, two draws.

Zoo 1.39.0, species `video_poker`. The walker, 2026-09-30: "actually put in
'PA Skill Games' ... into the level. We would see them in convenient stores,
bars, and strip clubs. High stool to play" -- and then, agreeing to the
period push-back, the 1997 version rather than the 2010s curved-LCD skill
game: a boxy upright with a CRT, the "for amusement only" sticker every one of
them carried, and a high stool in front.

WHAT IS BUILT (metres, Z up, origin at the floor's centre, the player at -Y),
from the bottom:

  plinth    a dark kick base, the slot's full footprint;
  cabinet   the lower body, its front the BELLY GLASS: the pay table, the coin
            door and the bill acceptor;
  deck      the button deck, sloped toward the player: five HOLD buttons, BET
            ONE, MAX BET and DEAL / DRAW;
  head      the screen housing, set back, a bezel round a recessed CRT showing
            a dealt hand, JACKS OR BETTER and the credits;
  marquee   the lit sign across the top: the brand, and FOR AMUSEMENT ONLY.

TWO ATLASES, TWO MATERIALS, TWO DRAWS, as the ATM's (`atm_forms`): PAINT --
the cabinet, the trim, the belly glass and the deck -- is lit by the room;
GLOW -- the CRT and the marquee -- is its own light
(`materials.make_backlit_material`), named `_Face` so Lux's power cut takes
it. The buttons are painted lit, as the price wheels' 9/10 are: part of the
paint, no light of their own.

EVERY NAME ON IT IS INVENTED: Delco slang, PG-13, held against the factory's
denylists and the real makers and the real Pennsylvania mark
(`tests/test_video_poker.py`). The walker's rule: never "Pennsylvania Skill".
"""
from __future__ import annotations

from . import prims as P
from . import shutters as SH
from .vending_forms import Canvas

#: The brands, by variant: marquee line, its colours (field, ink). No brand
#: says POKER: the card-brand denylist holds POKE as a substring (a real
#: card mark), and the first draft's JAWN POKER and PIKE POKER tripped it.
BRANDS = (
    ("JAWN JACKPOT", (150, 24, 30), (255, 214, 60)),
    ("PIKE DRAW", (24, 60, 150), (255, 244, 170)),
    ("LUCKY HOAGIE", (20, 110, 60), (255, 236, 120)),
    ("DOWN THE SHORE DRAW", (40, 30, 70), (120, 230, 255)),
)
STICKER = "FOR AMUSEMENT ONLY"
GAME = "JACKS OR BETTER"
#: The hand on the screen, by variant: five cards, rank and suit letter.
HANDS = (("A", "S"), ("A", "H"), ("7", "C"), ("7", "D"), ("K", "S")), \
        (("Q", "H"), ("Q", "S"), ("J", "D"), ("4", "C"), ("4", "H")), \
        (("10", "S"), ("J", "S"), ("Q", "S"), ("K", "S"), ("2", "D")), \
        (("9", "C"), ("9", "D"), ("9", "H"), ("5", "S"), ("3", "C"))
CREDITS = ("CREDIT 40", "CREDIT 125", "CREDIT 5", "CREDIT 80")
PAYS = (("ROYAL FLUSH", "250"), ("STRAIGHT FLUSH", "50"), ("4 OF A KIND", "25"),
        ("FULL HOUSE", "9"), ("FLUSH", "6"), ("STRAIGHT", "4"), ("3 OF A KIND", "3"),
        ("TWO PAIR", "2"), ("JACKS OR BETTER", "1"))
BODY = (24, 22, 26)              # a black cabinet
TRIM = (90, 92, 98)              # its chrome-grey edges
CRT_BG = (8, 20, 90)             # the video-poker blue
GLOW_EMISSION = 1.0
GLOW_ALBEDO = 0.6
#: Heights as fractions of the slot's, from a 1.75 m upright.
PLINTH = 0.05
DECK_LO, DECK_HI = 0.50, 0.56
HEAD_TOP = 0.86
SET_BACK = 0.30
SCREEN_INSET = 0.015
TEXEL = 256
#: THE DEAL (1.45.0). The screen's five cards come up one after another,
#: the hand holds, and all five go for the next deal: a shutter a card,
#: open from `DEAL_FIRST + i * DEAL_STEP` to `DEAL_HOLD` of a period.
DEAL_PERIOD_S = 8.0
DEAL_FIRST = 0.08
DEAL_STEP = 0.05
DEAL_HOLD = 0.92
#: A closed shutter's colour: the tube's blue, between its two scanline rows.
SHUTTER_RGB = (7, 17, 80)


def _quad(part, mat, tile, verts, uv=(0.0, 1.0, 0.0, 1.0)):
    p = P.mesh(part, mat, verts, [(0, 1, 2, 3)])
    u0, u1, v0, v1 = uv
    p["tile"] = tile
    p["uvs"] = [((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
    return p


def _box(part, mat, tile, lo, hi, skip=()):
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


def plan(w, d, h, variant=0):
    """``{"prims", "tiles", "collision", "facts"}``, the ATM's shape: prims
    carry ``mat`` "paint" or "glow" and a ``tile``."""
    v = int(variant) % len(BRANDS)
    brand = BRANDS[v][0]
    y0, y1 = -d / 2.0, d / 2.0
    x0, x1 = -w / 2.0, w / 2.0
    zp, zd0, zd1, zh = h * PLINTH, h * DECK_LO, h * DECK_HI, h * HEAD_TOP
    yh = y0 + d * SET_BACK
    prims = []
    prims += _box("VP_Plinth", "paint", "trim", (x0, y0, 0.0), (x1, y1, zp), skip=("bottom",))
    prims += _box("VP_Cabinet", "paint", "body", (x0, y0, zp), (x1, y1, zd0),
                  skip=("front", "bottom", "top"))
    prims.append(_quad("VP_Belly", "paint", "belly",
                       [(x0, y0, zp), (x1, y0, zp), (x1, y0, zd0), (x0, y0, zd0)]))
    prims.append(_quad("VP_Deck", "paint", "deck",
                       [(x0, y0, zd0), (x1, y0, zd0), (x1, yh, zd1), (x0, yh, zd1)]))
    for x, side in ((x0, "L"), (x1, "R")):
        tri = [(x, y0, zd0), (x, yh, zd0), (x, yh, zd1)]
        if side == "L":
            tri = [tri[1], tri[0], tri[2]]
        t = P.mesh(f"VP_DeckSide{side}", "paint", tri, [(0, 1, 2)])
        t["tile"] = "body"
        t["uvs"] = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0))]
        prims.append(t)
    prims.append(_quad("VP_CabinetTop", "paint", "body",
                       [(x0, yh, zd0), (x1, yh, zd0), (x1, y1, zd0), (x0, y1, zd0)]))
    prims += _box("VP_Head", "paint", "body", (x0, yh, zd0), (x1, y1, zh),
                  skip=("front", "bottom", "top"))
    sw, sh = w * 0.78, (zh - zd1) * 0.70
    sx0, sx1 = -sw / 2.0, sw / 2.0
    sz0 = zd1 + (zh - zd1) * 0.15
    sz1 = sz0 + sh
    prims += [
        _quad("VP_Bezel_B", "paint", "trim", [(x0, yh, zd0), (x1, yh, zd0), (x1, yh, sz0), (x0, yh, sz0)]),
        _quad("VP_Bezel_T", "paint", "trim", [(x0, yh, sz1), (x1, yh, sz1), (x1, yh, zh), (x0, yh, zh)]),
        _quad("VP_Bezel_L", "paint", "trim", [(x0, yh, sz0), (sx0, yh, sz0), (sx0, yh, sz1), (x0, yh, sz1)]),
        _quad("VP_Bezel_R", "paint", "trim", [(sx1, yh, sz0), (x1, yh, sz0), (x1, yh, sz1), (sx1, yh, sz1)]),
    ]
    yi = yh + SCREEN_INSET
    prims += [
        _quad("VP_Well_B", "paint", "trim", [(sx0, yh, sz0), (sx1, yh, sz0), (sx1, yi, sz0), (sx0, yi, sz0)]),
        _quad("VP_Well_T", "paint", "trim", [(sx0, yi, sz1), (sx1, yi, sz1), (sx1, yh, sz1), (sx0, yh, sz1)]),
        _quad("VP_Well_L", "paint", "trim", [(sx0, yh, sz0), (sx0, yi, sz0), (sx0, yi, sz1), (sx0, yh, sz1)]),
        _quad("VP_Well_R", "paint", "trim", [(sx1, yi, sz0), (sx1, yh, sz0), (sx1, yh, sz1), (sx1, yi, sz1)]),
        _quad("VP_Screen", "glow", "screen", [(sx0, yi, sz0), (sx1, yi, sz0), (sx1, yi, sz1), (sx0, yi, sz1)]),
    ]
    # THE DEAL: a shutter over each card on the screen, a pixel wider all
    # round than the card it hides
    screen = [(sx0, yi, sz0), (sx1, yi, sz0), (sx1, yi, sz1), (sx0, yi, sz1)]
    wpx, hpx = _px(sw), _px(sh)
    for i, (bx0, by0, bx1, by1) in enumerate(card_boxes(wpx, hpx)):
        rect = (max(0.0, (bx0 - 1) / wpx), max(0.0, 1.0 - (by1 + 1) / hpx),
                min(1.0, (bx1 + 1) / wpx), min(1.0, 1.0 - (by0 - 1) / hpx))
        prims.append(SH.over("VP_ScreenShutter", screen, rect,
                             (DEAL_FIRST + i * DEAL_STEP, DEAL_HOLD, DEAL_PERIOD_S, 0.0)))
    prims += _box("VP_Marquee", "paint", "trim", (x0, yh, zh), (x1, y1, h), skip=("front", "bottom"))
    prims.append(_quad("VP_Sign", "glow", "marquee", [(x0, yh, zh), (x1, yh, zh), (x1, yh, h), (x0, yh, h)]))
    tiles = {
        "body": ("paint", {"kind": "vp_flat", "rgb": BODY, "w_m": 0.08, "h_m": 0.08}),
        "trim": ("paint", {"kind": "vp_flat", "rgb": TRIM, "w_m": 0.08, "h_m": 0.08}),
        "belly": ("paint", {"kind": "vp_belly", "w_m": w, "h_m": zd0 - zp, "variant": v}),
        "deck": ("paint", {"kind": "vp_deck", "w_m": w,
                           "h_m": ((zd1 - zd0) ** 2 + (yh - y0) ** 2) ** 0.5, "variant": v}),
        "screen": ("glow", {"kind": "vp_crt", "w_m": sw, "h_m": sh, "variant": v}),
        "marquee": ("glow", {"kind": "vp_marquee", "w_m": w, "h_m": h - zh, "variant": v}),
    }
    return {"prims": prims, "tiles": tiles,
            "collision": ((x0, y0, 0.0), (x1, y1, h)),
            "facts": {"brand": brand, "variant": v, "tris": P.tri_count(prims), "materials": 3}}


# --- the art -----------------------------------------------------------------------------


def _px(m):
    return max(4, int(round(m * TEXEL)))


SUIT_RGB = {"S": (20, 20, 24), "C": (20, 20, 24), "H": (200, 20, 30), "D": (200, 20, 30)}


def card_boxes(w, h):
    """The five cards' pixel boxes on a ``w`` x ``h`` screen, row 0 at the
    top: ONE derivation for the painter and for the shutters that hide them
    (1.45.0), so a shutter cannot drift off its card."""
    n = 5
    gap = max(2, w // 60)
    cw = (w - 8 - gap * (n - 1)) // n
    cy0, cy1 = int(h * 0.26), int(h * 0.74)
    return [(4 + i * (cw + gap), cy0, 4 + i * (cw + gap) + cw, cy1) for i in range(n)]


def paint(spec):
    """One tile as a Canvas; ``c.unset`` lists every line that did not set."""
    from .poster_art import fit_text
    w, h = _px(spec["w_m"]), _px(spec["h_m"])
    kind = spec["kind"]
    v = int(spec.get("variant", 0)) % len(BRANDS)
    if kind == "vp_flat":
        return Canvas(w, h, spec["rgb"])
    unset = []

    def say(text, box, rgb, face="m5x7", cap=2):
        if fit_text(c, text, box, rgb, face=face, cap=cap) is None:
            unset.append(text)

    if kind == "vp_marquee":
        _name, field, ink = BRANDS[v]
        c = Canvas(w, h, field)
        c.rect(0, 0, w, 3, ink)
        c.rect(0, h - 3, w, h, ink)
        say(BRANDS[v][0], (4, 4, w - 4, int(h * 0.70)), ink, face="monogram", cap=4)
        say(STICKER, (4, int(h * 0.70), w - 4, h - 4), (250, 250, 244), cap=1)
        c.unset = unset
        return c
    if kind == "vp_crt":
        c = Canvas(w, h, CRT_BG)
        for y in range(0, h, 2):
            c.rect(0, y, w, y + 1, (6, 14, 70))
        say(GAME, (4, 3, w - 4, int(h * 0.22)), (255, 220, 60), cap=2)
        # five cards across the middle, white faces, rank and suit letter
        for (x, cy0, x1, cy1), (rank, suit) in zip(card_boxes(w, h), HANDS[v]):
            cw = x1 - x
            c.rect(x, cy0, x + cw, cy1, (248, 248, 240))
            # the rank in its suit's colour: "10S" does not set on the
            # narrowest unit's 18 px card, and red / black is what reads
            say(rank, (x + 1, cy0 + 2, x + cw - 1, cy1 - 2), SUIT_RGB[suit], cap=3)
        say(CREDITS[v], (4, int(h * 0.78), w - 4, h - 3), (255, 255, 255), cap=2)
        c.unset = unset
        return c
    if kind == "vp_deck":
        c = Canvas(w, h, (40, 40, 46))
        n = 5
        bw = (w - 12) // n
        for i in range(n):
            x = 6 + i * bw
            # a plain lit cap: the period's HOLD buttons were labelled in
            # print too small to set at this density (20 px a cap on the
            # narrowest unit), and HELD shows on the screen instead
            c.rect(x + 1, int(h * 0.30), x + bw - 2, int(h * 0.62), (240, 230, 90))
            c.rect(x + 1, int(h * 0.56), x + bw - 2, int(h * 0.62), (190, 170, 50))
        c.rect(6, int(h * 0.70), int(w * 0.30), int(h * 0.92), (40, 160, 230))
        say("BET", (7, int(h * 0.71), int(w * 0.30) - 1, int(h * 0.91)), (255, 255, 255), cap=1)
        c.rect(int(w * 0.62), int(h * 0.70), w - 6, int(h * 0.92), (220, 40, 40))
        say("DEAL", (int(w * 0.62) + 1, int(h * 0.71), w - 7, int(h * 0.91)), (255, 255, 255), cap=1)
        c.unset = unset
        return c
    if kind == "vp_belly":
        c = Canvas(w, h, BODY)
        # the pay table on a dark glass, the coin door and the bill slot below
        top = int(h * 0.05)
        row = int(h * 0.58) // len(PAYS)
        for i, (hand, pay) in enumerate(PAYS):
            y = top + i * row
            say(hand, (6, y, int(w * 0.74), y + row - 1), (255, 214, 60), cap=1)
            say(pay, (int(w * 0.76), y, w - 6, y + row - 1), (255, 255, 255), cap=1)
        dy = int(h * 0.68)
        c.rect(int(w * 0.10), dy, int(w * 0.55), int(h * 0.94), (60, 60, 66))     # coin door
        c.rect(int(w * 0.64), dy + 4, int(w * 0.90), dy + 12, (10, 10, 12))       # bill slot
        c.rect(int(w * 0.20), dy + 6, int(w * 0.24), dy + 20, (200, 180, 60))     # coin slot
        c.unset = unset
        return c
    raise ValueError(f"video_poker: no tile kind {kind!r}")


def all_strings():
    out = [b[0] for b in BRANDS] + [STICKER, GAME, "BET", "DEAL"]
    out += [p for p, _ in PAYS] + list(CREDITS)
    return out
