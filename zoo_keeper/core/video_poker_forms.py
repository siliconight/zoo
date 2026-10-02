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

from . import machine_parts as MP
from . import paint as PT
from . import prims as P
from . import shutters as SH

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
SCREEN_INSET = 0.022
#: THE REAL LOOK (1.46.0). The walker, 2026-10-02: "this looks like it is
#: made with a 90s GPU ... replace the retro look". Three things, none of
#: which costs a frame a draw:
#:   * the art is painted at three times the density, in a smooth face, and
#:     sampled with filtering (`PAINT_TEXEL`, `GLOW_TEXEL`; they were 256);
#:   * shading is PAINTED IN: graded panels, darkening where faces meet, a
#:     lit rim on a raised part, a streak of the room across glass;
#:   * the shape is a made thing's: chamfered corners, a toe kick set in, a
#:     marquee that overhangs, a tube that bulges behind a sloped bezel,
#:     buttons that stand off the deck.
PAINT_TEXEL = 768
GLOW_TEXEL = 640
TEXEL = 256                      # the small plain tiles
CHAMFER = 0.02                   # the cabinet's corners
KICK_IN = (0.02, 0.03)           # the toe kick, set in at the sides and the front
MARQUEE_PROUD = 0.03             # the marquee overhangs the head
BEZEL_M = 0.014                  # the sloped surround of the tube
BULGE = 0.008                    # the tube's face, proud at its middle
SCREEN_GRID = (6, 4)
BUTTON = (0.062, 0.040, 0.012)   # a cap: across, along the deck, standing off it
#: THE DEAL (1.45.0). The screen's five cards come up one after another,
#: the hand holds, and all five go for the next deal: a shutter a card,
#: open from `DEAL_FIRST + i * DEAL_STEP` to `DEAL_HOLD` of a period.
DEAL_PERIOD_S = 8.0
DEAL_FIRST = 0.08
DEAL_STEP = 0.05
DEAL_HOLD = 0.92
#: A closed shutter's colour: the tube's blue where the cards stand.
SHUTTER_RGB = (9, 24, 104)


def button_places(w):
    """``[(tile, x, t)]``: the five HOLD caps in a row up the deck, BET and
    DEAL nearer the player. ONE derivation for the caps and for the deck's
    printed legends and contact shadows."""
    out = [("btn_hold", (i - 2) * w * 0.17, 0.66) for i in range(5)]
    out += [("btn_bet", -w * 0.30, 0.27), ("btn_deal", w * 0.30, 0.27)]
    return out


def plan(w, d, h, variant=0):
    """``{"prims", "tiles", "collision", "facts"}``: prims carry ``mat``
    "paint", "glow" or "shutter", and the first two a ``tile``."""
    v = int(variant) % len(BRANDS)
    brand = BRANDS[v][0]
    y0, y1 = -d / 2.0, d / 2.0
    x0, x1 = -w / 2.0, w / 2.0
    zp, zd0, zd1, zh = h * PLINTH, h * DECK_LO, h * DECK_HI, h * HEAD_TOP
    yh = y0 + d * SET_BACK
    c = min(CHAMFER, w * 0.04)
    prims = []
    # the toe kick, set in: the cabinet stands over it
    prims += MP.kick("VP", x0, x1, y0, y1, zp, KICK_IN)
    # the lower cabinet, its front the belly glass between the chamfers
    prims += MP.cbody("VP_Cabinet", x0, x1, y0, y1, zp, zd0, c, skip=("front", "top"))
    prims.append(MP.quad("VP_Belly", "paint", "belly",
                         [(x0 + c, y0, zp), (x1 - c, y0, zp), (x1 - c, y0, zd0), (x0 + c, y0, zd0)]))
    # the deck, sloped to the player, and the wedges under its ends
    prims.append(MP.quad("VP_Deck", "paint", "deck",
                         [(x0, y0, zd0), (x1, y0, zd0), (x1, yh, zd1), (x0, yh, zd1)]))
    prims.append(MP.wedge("VP_DeckSideL", "paint", "side", x0, y0, yh, zd0, zd1, True))
    prims.append(MP.wedge("VP_DeckSideR", "paint", "side", x1, y0, yh, zd0, zd1, False))
    for i, (tile, bx, bt) in enumerate(button_places(w)):
        prims.append(MP.cap(f"VP_Button{i}", tile, bx, bt, (y0, zd0, yh, zd1), BUTTON))
    # the head, set back; its front the bezel round the tube
    prims += MP.cbody("VP_Head", x0, x1, yh, y1, zd0, zh, c, skip=("front", "top"))
    sw, sh = w * 0.74, (zh - zd1) * 0.66
    sx0, sx1 = -sw / 2.0, sw / 2.0
    sz0 = zd1 + (zh - zd1) * 0.17
    sz1 = sz0 + sh
    m = BEZEL_M
    hole, screen = (sx0 - m, sx1 + m, sz0 - m, sz1 + m), (sx0, sx1, sz0, sz1)
    yi = yh + SCREEN_INSET
    prims += MP.bezel("VP", x0 + c, x1 - c, zd0, zh, hole, yh)
    prims += MP.wells("VP", hole, screen, yh, yi)
    prims.append(MP.curved_screen("VP_Screen", screen, yi, BULGE, SCREEN_GRID))
    # THE DEAL: a shutter over each card, a pixel wider all round than the
    # card it hides, standing clear of the tube's bulge
    flat = [(sx0, yi, sz0), (sx1, yi, sz0), (sx1, yi, sz1), (sx0, yi, sz1)]
    wpx, hpx = _gpx(sw), _gpx(sh)
    for i, (cx0, cy0, cx1, cy1) in enumerate(card_boxes(wpx, hpx)):
        rect = (max(0.0, (cx0 - 1) / wpx), max(0.0, 1.0 - (cy1 + 1) / hpx),
                min(1.0, (cx1 + 1) / wpx), min(1.0, 1.0 - (cy0 - 1) / hpx))
        prims.append(SH.over("VP_ScreenShutter", flat, rect,
                             (DEAL_FIRST + i * DEAL_STEP, DEAL_HOLD, DEAL_PERIOD_S, 0.0),
                             proud=BULGE + SH.PROUD))
    # the marquee, overhanging the head: its front lit, its underside in shade
    ym = yh - MARQUEE_PROUD
    prims += MP.cbody("VP_Marquee", x0, x1, ym, y1, zh, h, c, skip=("front",))
    prims.append(MP.quad("VP_Sign", "glow", "marquee",
                         [(x0 + c, ym, zh), (x1 - c, ym, zh), (x1 - c, ym, h), (x0 + c, ym, h)]))
    prims.append(MP.quad("VP_MarqueeUnder", "paint", "kick",
                         [(x0, yh, zh), (x1, yh, zh), (x1, ym, zh), (x0, ym, zh)]))
    tiles = {
        "side": ("paint", {"kind": "vp_side", "w_m": 0.5, "h_m": 1.0, "variant": v}),
        "edge": ("paint", {"kind": "vp_edge", "w_m": 0.06, "h_m": 0.5, "variant": v}),
        "top": ("paint", {"kind": "vp_top", "w_m": 0.25, "h_m": 0.25, "variant": v}),
        "kick": ("paint", {"kind": "vp_kick", "w_m": 0.25, "h_m": 0.12, "variant": v}),
        "bezel": ("paint", {"kind": "vp_bezel", "w_m": 0.25, "h_m": 0.25, "variant": v}),
        "well": ("paint", {"kind": "vp_well", "w_m": 0.12, "h_m": 0.12, "variant": v}),
        "belly": ("paint", {"kind": "vp_belly", "w_m": w - 2 * c, "h_m": zd0 - zp, "variant": v}),
        "deck": ("paint", {"kind": "vp_deck", "w_m": w,
                           "h_m": ((zd1 - zd0) ** 2 + (yh - y0) ** 2) ** 0.5, "variant": v}),
        "screen": ("glow", {"kind": "vp_crt", "w_m": sw, "h_m": sh, "variant": v}),
        "marquee": ("glow", {"kind": "vp_marquee", "w_m": w - 2 * c, "h_m": h - zh, "variant": v}),
        "btn_hold": ("glow", {"kind": "vp_button", "w_m": BUTTON[0], "h_m": BUTTON[1], "rgb": (250, 226, 70)}),
        "btn_bet": ("glow", {"kind": "vp_button", "w_m": BUTTON[0], "h_m": BUTTON[1], "rgb": (60, 170, 250)}),
        "btn_deal": ("glow", {"kind": "vp_button", "w_m": BUTTON[0], "h_m": BUTTON[1], "rgb": (240, 60, 50)}),
    }
    return {"prims": prims, "tiles": tiles,
            "collision": ((x0, y0, 0.0), (x1, y1, h)),
            "facts": {"brand": brand, "variant": v, "tris": P.tri_count(prims), "materials": 3,
                      "smooth": True}}


# --- the art -----------------------------------------------------------------------------


def _px(m):
    return max(4, int(round(m * TEXEL)))


def _ppx(m):
    return max(8, int(round(m * PAINT_TEXEL)))


def _gpx(m):
    return max(8, int(round(m * GLOW_TEXEL)))


SUIT_RGB = {"S": (20, 20, 24), "C": (20, 20, 24), "H": (200, 20, 30), "D": (200, 20, 30)}


def card_boxes(w, h):
    """The five cards' pixel boxes on a ``w`` x ``h`` screen, row 0 at the
    top: ONE derivation for the painter and for the shutters that hide them
    (1.45.0), so a shutter cannot drift off its card."""
    n = 5
    pad = max(4, w // 28)
    gap = max(2, w // 60)
    cw = (w - 2 * pad - gap * (n - 1)) // n
    cy0, cy1 = int(h * 0.27), int(h * 0.74)
    return [(pad + i * (cw + gap), cy0, pad + i * (cw + gap) + cw, cy1) for i in range(n)]


def _lift(rgb, by):
    return tuple(max(0.0, min(255.0, c + by)) for c in rgb)


def _pip(im, suit, cx, cy, s, rgb):
    """A suit's pip, drawn: a diamond, a heart, a spade, a club."""
    if suit == "D":
        for k in range(-s, s + 1):
            half = (s - abs(k)) * 0.72
            im.rect((cx - half, cy + k, cx + half + 1, cy + k + 1), rgb)
    elif suit == "H":
        im.disc(cx - s * 0.48, cy - s * 0.25, s * 0.56, rgb)
        im.disc(cx + s * 0.48, cy - s * 0.25, s * 0.56, rgb)
        for k in range(0, s + 1):
            half = (s - k) * 1.0
            im.rect((cx - half, cy + k - s * 0.1, cx + half + 1, cy + k - s * 0.1 + 1), rgb)
    elif suit == "S":
        im.disc(cx - s * 0.48, cy + s * 0.2, s * 0.56, rgb)
        im.disc(cx + s * 0.48, cy + s * 0.2, s * 0.56, rgb)
        for k in range(0, s + 1):
            half = k * 1.0
            im.rect((cx - half, cy - s + k, cx + half + 1, cy - s + k + 1), rgb)
        im.rect((cx - s * 0.18, cy + s * 0.4, cx + s * 0.18 + 1, cy + s * 1.1), rgb)
    else:
        im.disc(cx, cy - s * 0.5, s * 0.5, rgb)
        im.disc(cx - s * 0.55, cy + s * 0.2, s * 0.5, rgb)
        im.disc(cx + s * 0.55, cy + s * 0.2, s * 0.5, rgb)
        im.rect((cx - s * 0.18, cy + s * 0.2, cx + s * 0.18 + 1, cy + s * 1.1), rgb)


def paint(spec):
    """One tile as a Canvas; ``c.unset`` lists every line that did not set."""
    kind = spec["kind"]
    v = int(spec.get("variant", 0)) % len(BRANDS)
    if kind == "vp_side":
        # a painted steel panel: graded under the ceiling's light, darker
        # toward its foot and its edges, with the grain of a sprayed finish
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, BODY)
        im.vgrad((0, 0, w, h), _lift(BODY, 26), _lift(BODY, -6))
        im.edge_dark((0, 0, w, h), w * 0.22, 0.30)
        im.grain((0, 0, w, h), 2.2, 11)
        return im.to_canvas()
    if kind == "vp_edge":
        # the chamfer: paint worn thin where hands and stools reach
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, BODY)
        im.vgrad((0, 0, w, h), _lift(BODY, 70), _lift(BODY, 34))
        im.rect((w * 0.35, 0, w * 0.65, h), _lift(BODY, 96), 0.55)
        im.grain((0, 0, w, h), 4.0, 12)
        return im.to_canvas()
    if kind == "vp_top":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, _lift(BODY, 22))
        im.edge_dark((0, 0, w, h), w * 0.2, 0.25)
        im.grain((0, 0, w, h), 3.0, 13)                 # dust
        return im.to_canvas()
    if kind == "vp_kick":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, (9, 9, 10))
        im.vgrad((0, 0, w, h), (6, 6, 7), (20, 19, 20))
        im.grain((0, 0, w, h), 3.0, 14)                 # scuffs
        return im.to_canvas()
    if kind == "vp_bezel":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, (30, 30, 34))
        im.vgrad((0, 0, w, h), (46, 46, 52), (26, 26, 30))
        im.grain((0, 0, w, h), 1.6, 15)
        return im.to_canvas()
    if kind == "vp_well":
        # the surround sloping in to the tube: row 0 is the glass's edge,
        # in the tube's own shade
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, (20, 20, 22))
        im.vgrad((0, 0, w, h), (4, 4, 6), (40, 40, 46))
        return im.to_canvas()
    if kind == "vp_button":
        w, h = _gpx(spec["w_m"]), _gpx(spec["h_m"])
        rgb = spec["rgb"]
        im = PT.Img(w, h, _lift(rgb, -80))
        im.rrect((1, 1, w - 1, h - 1), h * 0.28, rgb)
        im.vgrad((3, 3, w - 3, h * 0.45), _lift(rgb, 60), rgb)       # the cap's lit crown
        im.edge_dark((0, 0, w, h), h * 0.3, 0.45, h * 0.28)
        return im.to_canvas()
    if kind == "vp_marquee":
        w, h = _gpx(spec["w_m"]), _gpx(spec["h_m"])
        _name, field, ink = BRANDS[v]
        im = PT.Img(w, h, field)
        im.vgrad((0, 0, w, h), _lift(field, 34), _lift(field, -18))
        b = max(3, h // 22)
        im.rrect((b, b, w - b, h - b), h * 0.10, ink)
        im.rrect((2 * b, 2 * b, w - 2 * b, h - 2 * b), h * 0.08, field)
        im.vgrad((2 * b + 2, 2 * b + 2, w - 2 * b - 2, h - 2 * b - 2), _lift(field, 30), _lift(field, -10))
        im.text(BRANDS[v][0], (4 * b, 3 * b, w - 4 * b, int(h * 0.66)), ink, "highway_bold",
                shadow=_lift(field, -70))
        im.text(STICKER, (4 * b, int(h * 0.70), w - 4 * b, h - 3 * b), (250, 250, 244), "highway_cond",
                cap=int(h * 0.13), tracking=0.04)
        # a backlit panel is brightest at its tubes and falls off to its frame
        im.vignette((0, 0, w, h), 0.38)
        im.glow((0, 0, w, h), max(2, h // 40), 0.22)
        return im.to_canvas()
    if kind == "vp_crt":
        w, h = _gpx(spec["w_m"]), _gpx(spec["h_m"])
        im = PT.Img(w, h, CRT_BG)
        im.vgrad((0, 0, w, h), (10, 28, 120), (6, 16, 76))
        im.text(GAME, (int(w * 0.06), int(h * 0.05), int(w * 0.94), int(h * 0.22)), (255, 224, 70),
                "highway_bold")
        for (x, cy0, x1, cy1), (rank, suit) in zip(card_boxes(w, h), HANDS[v]):
            cw, ch = x1 - x, cy1 - cy0
            im.rrect((x, cy0, x1, cy1), cw * 0.10, (250, 250, 244))
            im.vgrad((x + 2, cy0 + 2, x1 - 2, cy1 - 2), (255, 255, 250), (226, 226, 220))
            # the rank over its suit's pip, both in the suit's colour
            im.text(rank, (x + 2, cy0 + ch * 0.08, x1 - 2, cy0 + ch * 0.54), SUIT_RGB[suit],
                    "highway_bold")
            _pip(im, suit, x + cw / 2.0, cy0 + ch * 0.76, max(3, int(min(cw, ch) * 0.16)), SUIT_RGB[suit])
        im.text(CREDITS[v], (int(w * 0.06), int(h * 0.79), int(w * 0.94), int(h * 0.95)), (255, 255, 255),
                "highway_bold")
        # the tube: its phosphor spills, its lines show, its corners fall off
        im.glow((0, 0, w, h), max(2, h // 60), 0.30)
        im.scanlines((0, 0, w, h), 3, 0.16)
        im.vignette((0, 0, w, h), 0.42)
        return im.to_canvas()
    if kind == "vp_deck":
        w, h = _ppx(spec["w_m"]), _ppx(spec["h_m"])
        im = PT.Img(w, h, (40, 40, 46))
        im.vgrad((0, 0, w, h), (58, 58, 66), (34, 34, 40))
        im.grain((0, 0, w, h), 2.0, 21)
        cw_px = BUTTON[0] / spec["w_m"] * w
        cl_px = BUTTON[1] / spec["h_m"] * h
        legends = ("HOLD",) * 5 + ("BET ONE", "DEAL / DRAW")
        for (tile, bx, bt), legend in zip(button_places(spec["w_m"]), legends):
            cx = w / 2.0 + bx / spec["w_m"] * w
            cy = h * (1.0 - bt)
            # the cap's contact shadow, soft, a little toward the player
            im.rrect((cx - cw_px * 0.62, cy - cl_px * 0.55, cx + cw_px * 0.62, cy + cl_px * 0.85),
                     cl_px * 0.3, (8, 8, 10), 0.75)
        # the shadows are soft; the legends, printed after, are not (the
        # first cut blurred the deck with its lettering on it)
        im.blur((0, 0, w, h), 2)
        for (tile, bx, bt), legend in zip(button_places(spec["w_m"]), legends):
            cx = w / 2.0 + bx / spec["w_m"] * w
            cy = h * (1.0 - bt)
            # a HOLD's legend is beyond its cap; BET's and DEAL's are on the
            # player's side of theirs, clear of the row above
            box = ((cx - cw_px * 0.95, cy - cl_px * 1.5, cx + cw_px * 0.95, cy - cl_px * 0.72)
                   if tile == "btn_hold" else
                   (cx - cw_px * 1.1, cy + cl_px * 0.9, cx + cw_px * 1.1, cy + cl_px * 1.55))
            im.text(legend, box, (232, 232, 224), "highway_cond", cap=int(cl_px * 0.5))
        im.edge_dark((0, 0, w, h), h * 0.25, 0.30)
        return im.to_canvas()
    if kind == "vp_belly":
        w, h = _ppx(spec["w_m"]), _ppx(spec["h_m"])
        im = PT.Img(w, h, BODY)
        im.vgrad((0, 0, w, h), _lift(BODY, 22), _lift(BODY, -4))
        # THE PAY TABLE, on a dark glass set in a frame
        g = (int(w * 0.06), int(h * 0.04), int(w * 0.94), int(h * 0.62))
        im.rrect(g, w * 0.02, (70, 70, 78))
        gi = (g[0] + 4, g[1] + 4, g[2] - 4, g[3] - 4)
        im.rrect(gi, w * 0.015, (10, 12, 22))
        im.vgrad((gi[0] + 3, gi[1] + 3, gi[2] - 3, gi[3] - 3), (18, 22, 44), (8, 9, 18))
        row = (gi[3] - gi[1] - 12) / float(len(PAYS))
        for i, (hand, pay) in enumerate(PAYS):
            y = gi[1] + 6 + i * row
            if i % 2 == 0:
                im.rect((gi[0] + 6, y, gi[2] - 6, y + row), (255, 255, 255), 0.045)
            cap = int(row * 0.56)
            im.text(hand, (gi[0] + 14, y, gi[0] + (gi[2] - gi[0]) * 0.74, y + row), (255, 214, 60),
                    "highway_cond", cap=cap, align="left")
            im.text(pay, (gi[0] + (gi[2] - gi[0]) * 0.76, y, gi[2] - 14, y + row), (255, 255, 255),
                    "highway_bold", cap=cap, align="right")
        im.gloss(gi, 0.10)
        im.bevel(g, 3, 30.0, 40.0, raised=False)
        # THE COIN DOOR: a brushed steel plate, its slot, its lock; the bill
        # acceptor beside it
        dz = (int(w * 0.08), int(h * 0.68), int(w * 0.54), int(h * 0.95))
        im.rrect(dz, w * 0.012, (120, 122, 128))
        im.vgrad((dz[0] + 2, dz[1] + 2, dz[2] - 2, dz[3] - 2), (150, 152, 158), (96, 98, 104))
        for y in range(dz[1] + 3, dz[3] - 3, 2):                 # the brushing
            im.rect((dz[0] + 3, y, dz[2] - 3, y + 1), (255, 255, 255), 0.05)
        im.bevel(dz, 3, 46.0, 50.0)
        dw, dh = dz[2] - dz[0], dz[3] - dz[1]
        slot = (dz[0] + dw * 0.20, dz[1] + dh * 0.16, dz[0] + dw * 0.30, dz[1] + dh * 0.50)
        im.rrect(slot, dw * 0.02, (16, 16, 18))
        im.bevel(slot, 2, 30.0, 30.0, raised=False)
        im.disc(dz[0] + dw * 0.70, dz[1] + dh * 0.34, dw * 0.09, (196, 180, 96))       # the lock
        im.disc(dz[0] + dw * 0.70, dz[1] + dh * 0.34, dw * 0.035, (40, 36, 24))
        im.rrect((dz[0] + dw * 0.14, dz[1] + dh * 0.66, dz[0] + dw * 0.86, dz[1] + dh * 0.86), dw * 0.02,
                 (30, 30, 34))                                                        # the coin return
        ba = (int(w * 0.62), int(h * 0.70), int(w * 0.92), int(h * 0.82))
        im.rrect(ba, w * 0.012, (26, 26, 30))
        im.rrect((ba[0] + 6, ba[1] + (ba[3] - ba[1]) * 0.36, ba[2] - 6, ba[1] + (ba[3] - ba[1]) * 0.64),
                 3, (4, 4, 5))
        im.bevel(ba, 2, 36.0, 40.0)
        im.text("$1  $5", (ba[0], ba[3] + 4, ba[2], ba[3] + int(h * 0.05)), (200, 200, 190), "highway_cond")
        im.edge_dark((0, 0, w, h), w * 0.10, 0.35)
        im.grain((0, 0, w, h), 1.8, 31)
        return im.to_canvas()
    raise ValueError(f"video_poker: no tile kind {kind!r}")


def all_strings():
    out = [b[0] for b in BRANDS] + [STICKER, GAME, "BET ONE", "DEAL / DRAW", "HOLD", "$1  $5"]
    out += [p for p, _ in PAYS] + list(CREDITS)
    return out
