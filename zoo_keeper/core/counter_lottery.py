"""The instant-ticket dispensers on a store counter.

Zoo 1.47.0. Until now these were three flat red boxes beside each till
(1.7.0's "lottery dispensers"), and cold run 9135's frames put them next to
a till that had just been given a made body and lettered keys: the walker's
store had two looks in one room. This is the dispensers taken to the same
standard -- and the first prop built to the walker's authorship guide
(`docs/reference/HUMAN_AUTHORSHIP_GUIDE.md` in the root repo), which asks
for a brief before a surface is painted.

THE BRIEF. What it is: a countertop dispenser for scratch-off tickets, one
game a unit, three in a row at the customer's edge of the counter beside the
till. What it is made of: a clear acrylic case on a black plastic foot, a
roll of printed tickets inside. Who touches it: the clerk, who tears a ticket
off from behind; the customer only looks, so its face leans back toward a
standing customer's eyes. What it is for, to the room: it is the loudest
small thing on the counter, on purpose -- a ticket is printed to be seen
from the door.

WHAT FOLLOWS FROM THE BRIEF, and what is left out because of it:

  * THE TICKET IS LOUD AND THE CASE IS QUIET. Saturated ink, a price in a
    burst, three scratch panels; the acrylic is a pale side, a streak of the
    room across the face and a lit edge. No grain, no grime: acrylic by a
    till is wiped daily and a ticket is new by definition.
  * THREE DIFFERENT GAMES IN A ROW, the same three on every counter. A row of
    one game would be a stock shelf; a state's games are the same in every
    store, so the repetition across stores is the true thing here and not a
    kit repeating.
  * IDENTICAL CASES AT IDENTICAL HEIGHTS. They are one manufactured unit
    bought three times. (1.7.0 stepped each one a centimetre shorter than
    the last; nothing made them differ.)
  * NO TRANSPARENCY. Clear acrylic is painted as what is seen through it. A
    blended material is a sorting cost and a shadow-pass exception on every
    client, for a case 11 cm wide.

COST: nothing. Every face names a tile in the till's painted image
(`counter_register.paint_art`) and is built into the till's object, so the
dispensers ride in a draw the counter already makes. The red boxes rode in
the counter's shared plastic; that draw is unchanged too.

Frame: the counter recipe's -- metres, Z up, -Y the customer, +Y the clerk.
Pure Python: no bpy.
"""
from __future__ import annotations

from . import machine_parts as MP
from . import paint as PT

#: One unit: its foot's footprint and its whole height (1.7.0's box).
W = 0.11
D = 0.09
H = 0.28
#: The black foot, and its broken corners.
FOOT_H = 0.030
FOOT_C = 0.006
#: The case stands this far inside the foot's edge, and its foot is this far
#: into the foot's top, so the two share no plane.
CASE_IN = 0.006
BURY = 0.004
#: The face leans back by this much over its height: about 5 degrees, toward
#: the eyes of somebody standing at the counter.
LEAN = 0.022
#: Pixels per metre, the painted density the tills use.
TEXEL = 768

#: The games: two lines of name, a price in dollars, the ticket's field and
#: its second ink. INVENTED, Delco slang, PG-13; none is a state's mark and
#: the word LOTTERY is on `poster_copy`'s denylist and is not used.
GAMES = (
    ("WOODER", "WINS", 1, (22, 132, 86), (250, 222, 60)),
    ("HOAGIE", "MONEY", 2, (214, 96, 28), (255, 240, 200)),
    ("FAT", "STACKS", 5, (104, 52, 150), (120, 232, 160)),
)
ACRYLIC = (164, 176, 180)


def dispenser(lx, ly0, h, i, mat):
    """One unit, its foot's customer edge at ``ly0``, centred on ``lx``,
    standing on a top at ``h``; ``i`` picks its game. Every prim is ``mat``
    and names a tile of `tiles` (the foot wears the till's dark plastic)."""
    x0, x1 = lx - W / 2.0, lx + W / 2.0
    y1 = ly0 + D
    zf = h + FOOT_H
    out = MP.cbody("Counter_Lottery_Foot", x0, x1, ly0, y1, h - 0.004, zf, FOOT_C,
                   side="head_side", edge="head_edge", top="head_top", mat=mat)
    bx0, bx1 = x0 + CASE_IN, x1 - CASE_IN
    yf0, yf1, yb = ly0 + CASE_IN, ly0 + CASE_IN + LEAN, y1 - CASE_IN
    zb, zt = zf - BURY, h + H
    game = "lot_ticket_%d" % (i % len(GAMES))
    out += [
        MP.quad("Counter_Lottery_Ticket", mat, game,
                [(bx0, yf0, zb), (bx1, yf0, zb), (bx1, yf1, zt), (bx0, yf1, zt)]),
        MP.quad("Counter_Lottery_CaseSideR", mat, "lot_side",
                [(bx1, yf0, zb), (bx1, yb, zb), (bx1, yb, zt), (bx1, yf1, zt)]),
        MP.quad("Counter_Lottery_CaseSideL", mat, "lot_side",
                [(bx0, yb, zb), (bx0, yf0, zb), (bx0, yf1, zt), (bx0, yb, zt)]),
        MP.quad("Counter_Lottery_Case_back", mat, "lot_back",
                [(bx1, yb, zb), (bx0, yb, zb), (bx0, yb, zt), (bx1, yb, zt)]),
        MP.quad("Counter_Lottery_Case_top", mat, "lot_top",
                [(bx0, yf1, zt), (bx1, yf1, zt), (bx1, yb, zt), (bx0, yb, zt)]),
    ]
    return out


def _px(m):
    return max(8, int(round(m * TEXEL)))


def _lift(rgb, by):
    return tuple(max(0.0, min(255.0, c + by)) for c in rgb)


def paint_ticket(i):
    """A unit's face: the ticket on the roll behind the acrylic -- its price
    in a burst, its name, three panels to scratch, the tear line and the top
    of the next ticket under it -- and the room's light across the case."""
    top, foot, price, field, ink = GAMES[i % len(GAMES)]
    w = _px(W - 2.0 * CASE_IN)
    h = _px(((H - FOOT_H + BURY) ** 2 + LEAN ** 2) ** 0.5)
    im = PT.Img(w, h, field)
    im.vgrad((0, 0, w, h), _lift(field, 26), _lift(field, -22))
    tear = h * 0.74                                          # one ticket's foot
    # the price, in a burst at the ticket's head
    r = w * 0.27
    cx, cy = w * 0.5, h * 0.17
    im.disc(cx + 1.5, cy + 2.0, r, (0, 0, 0), 0.35)
    im.disc(cx, cy, r, ink)
    im.disc(cx, cy, r * 0.84, _lift(ink, 14))
    im.text("$%d" % price, (cx - r * 0.78, cy - r * 0.56, cx + r * 0.78, cy + r * 0.56),
            _lift(field, -40), "highway_bold")
    # the name, two lines
    im.text(top, (w * 0.07, h * 0.325, w * 0.93, h * 0.405), (255, 255, 255), "highway_bold",
            shadow=_lift(field, -80))
    im.text(foot, (w * 0.07, h * 0.415, w * 0.93, h * 0.495), ink, "highway_bold",
            shadow=_lift(field, -80))
    # three panels to scratch: foil, each with its own light
    pw, gap = w * 0.24, w * 0.05
    px0 = (w - 3 * pw - 2 * gap) / 2.0
    for k in range(3):
        box = (px0 + k * (pw + gap), h * 0.55, px0 + k * (pw + gap) + pw, h * 0.55 + pw * 1.05)
        im.rrect(box, 3, (176, 180, 186))
        im.vgrad((box[0] + 1.5, box[1] + 1.5, box[2] - 1.5, box[3] - 1.5), (214, 218, 224), (150, 154, 160))
        im.bevel(box, 1, 26.0, 30.0)
    # the tear line, and the next ticket on the roll
    for x in range(3, w - 3, 6):
        im.rect((x, tear, x + 3, tear + 1.5), _lift(field, -70))
    im.shade((0, tear + 1.5, w, h), 0.86)
    im.disc(cx, tear + (cy + r) * 0.62, r * 0.9, ink, 0.9)
    # the acrylic over it: a streak of the room, and a lit edge each side
    im.gloss((0, 0, w, h), 0.10, 0.35, 0.22, 0.16)
    im.rect((0, 0, 1.5, h), (255, 255, 255), 0.45)
    im.rect((w - 1.5, 0, w, h), (255, 255, 255), 0.25)
    im.edge_dark((0, 0, w, h), w * 0.06, 0.18)
    return im.to_canvas()


def paint_side():
    """The case from the side: clear acrylic, the roll's edge seen through it."""
    w, h = _px(D - 2.0 * CASE_IN), 96
    im = PT.Img(w, h, ACRYLIC)
    im.vgrad((0, 0, w, h), _lift(ACRYLIC, 14), _lift(ACRYLIC, -30))
    im.rect((w * 0.16, 0, w * 0.26, h), (244, 244, 238), 0.8)   # the strip of tickets, edge on
    im.gloss((0, 0, w, h), 0.08, 0.3, 0.3, 0.2)
    im.rect((0, 0, 1.5, h), (255, 255, 255), 0.4)
    return im.to_canvas()


def paint_back():
    """The clerk's side: the roll the tickets feed from, low in the case."""
    w, h = _px(W - 2.0 * CASE_IN), 144
    im = PT.Img(w, h, ACRYLIC)
    im.vgrad((0, 0, w, h), _lift(ACRYLIC, 10), _lift(ACRYLIC, -34))
    im.rect((w * 0.2, 0, w * 0.8, h * 0.62), (238, 238, 232), 0.85)       # the strip, its plain back
    r = w * 0.36
    im.disc(w * 0.5, h * 0.74, r, (232, 232, 226))
    im.disc(w * 0.5, h * 0.74, r * 0.34, (120, 120, 124))
    im.gloss((0, 0, w, h), 0.06, 0.35, 0.25, 0.18)
    return im.to_canvas()


def paint_top():
    im = PT.Img(48, 32, _lift(ACRYLIC, 16))
    im.edge_dark((0, 0, 48, 32), 5, 0.2)
    return im.to_canvas()


def tiles():
    """``[(tile, canvas)]``: what `counter_register.paint_art` adds to the
    till's one image for these."""
    out = [("lot_ticket_%d" % i, paint_ticket(i)) for i in range(len(GAMES))]
    return out + [("lot_side", paint_side()), ("lot_back", paint_back()), ("lot_top", paint_top())]


def painted_strings():
    """Every string a dispenser paints, for the denylist test."""
    out = []
    for top, foot, price, _f, _i in GAMES:
        out += [top, foot, "$%d" % price, "%s %s" % (top, foot)]
    return out
