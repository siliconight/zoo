"""What a fire escape is, in numbers: ONE place, no bpy (1.110.0, factory roadmaps 156 and 241).

The walker, 2026-09-13, with a photo of a brick walk-up: "this is something i'd like to see in our toolset,
fireescape stairs brick" (roadmap 156; the factory's `docs/SET_DRESSING_REFERENCES.md`). A steel fire escape: one
landing a floor, a slatted deck with guards on its three open sides, a flight between landings that switches back,
a drop ladder under the lowest (the factory's `docs/proposals/FIRE_ESCAPE.md`). Deli Counter stands each storey of
it as a slot of this species, and this module draws that storey from the slot's box alone -- so a fire escape of
any width, projection or storey height is drawn without the module knowing the building.

THE NUMBERS, where a source speaks:
  * the flight 22 in wide and its risers at most 8 in: the IEBC's minimum width and maximum riser for an existing
    building's fire escape stair (2012 IEBC 405.4, as a building-code forum quotes it; the ICC's own text refused
    the fetch, so it was not read there);
  * the guards 36 in over the deck: NFPA 101 lets an existing guard stand 30 in and one in a dwelling 36 (as state
    fire-code sheets reproduce its table) -- the common look, and the stoop's rail height;
  * the pickets' clear 4 in, the stoop's (`stoop_railing_forms.pickets`).
CHOSEN, not read: the steel's sizes (a 2 in angle frame, 1-1/2 in flat-bar slats 1 in apart, 1-1/2 in posts, 8 in
stringers), the hatch's 0.75 m, and the flight's pitch -- the storey's rise over what the landing leaves of its
width, steep, as the old ones are.

THE FRAME is Zoo's: X along the facade, the WALL at +Y and the street at -Y, as every module faces -Y; Z up. Centre
pivot, and the extents are exactly the slot's (w, d, h).

THE FORMS
  flight_a, flight_b   one storey's bay. At the box's bottom the landing: a deck frame, slats along X, a hatch at one
                       end of the stair band -- where the flight from the storey below comes up -- and guards on its
                       three open sides. In the stair band, behind the front guard, the flight rises from the hatch's
                       inner edge to the box's top at the far end, its handrail rising from the front guard. `a`'s hatch is
                       at -X and its flight rises toward +X; `b` is the same, reflected. A stack alternates a, b, a,
                       and each flight comes up through the next landing's hatch.
  top_a, top_b         the top landing alone, its hatch where the last flight comes up. Its posts reach the box's
                       top, so its guard is the box's height less the deck.
  drop                 the drop ladder: two rails and rungs, hung under the lowest landing's hatch.
A plan that names no form gets the one its box can be (`form_for`): the drop where the box is a ladder's width, a
flight where a storey fits, the top landing otherwise. The genome lists `auto` first, because a list's first option
is the plan's default (`dna._resolve_params`): the coplanar census names no form, and its min corner is a ladder's
size. Deli Counter names one always.

NO FACE OF ONE PART LIES ON ANOTHER'S, so `prims.coincident_pairs` reads none before Blender does. The deck nests in
levels: the front and back bars run the width; the side bars run between them, their ends `SINK` inside and their
section `NEST` inside; then the band bar, the hatch's trimmer and the slats, each a level further in. A post stands
inside the frame's outer faces and sinks into it. A rail's ends sink `RAIL_SINK` into its posts, deeper than its
section nests, so where a front rail and an end rail meet inside a corner post their faces stay `NEST` and more
apart; and the end guards' rails stand `NEST` under the front guard's. A picket's ends lie on its rails' centre
lines. The flight's treads sink into its stringers and stop a step short of their end, and its stringers start where
they clear the deck. Its
handrail starts inside the front guard's top rail -- its section at the foot the rail's, a `NEST` inside its sides --
and has no post at the foot: one stood in the treads' way, its face a millimetre or two off the first tread's at
some storeys (the module's own test, over 60 sizes).

COLLISION: none (the genome's `collision: false`). The lowest landing stands a storey up, so nobody walks it from
the street, and Level Factory reads an Empty's street edge off its colliders. A walkable fire escape is later work.
"""
from __future__ import annotations

import math

from . import prims
from .stoop_railing_forms import pickets, sheared

IN = 0.0254
#: the flight's width: 2012 IEBC 405.4's 22 in for an existing fire escape stair
FLIGHT_W = round(22 * IN, 4)          # 0.5588 m
#: the riser it may not exceed: 405.4's 8 in
RISER = round(8 * IN, 4)              # 0.2032 m
#: the guards' rail top over the deck: 36 in
GUARD_H = round(36 * IN, 4)           # 0.9144 m
#: the bottom rail's centre over the deck
BOTTOM_Z = 0.10
FRAME = round(2 * IN, 4)              # 0.0508 m, the deck frame's angle, square in section
POST = round(1.5 * IN, 4)             # 0.0381 m, a square post
RAIL_T = round(0.75 * IN, 4)          # 0.0191 m, a rail's depth in Z
PICKET = round(0.625 * IN, 4)         # 0.0159 m, a square picket
SLAT = round(1.5 * IN, 4)             # 0.0381 m, a slat across Y
SLAT_T = round(0.25 * IN, 4)          # 0.0064 m, a slat's thickness
SLAT_GAP = round(1 * IN, 4)           # 0.0254 m, the clear between slats
STRINGER_T = round(0.5 * IN, 4)       # 0.0127 m, a stringer across Y
STRINGER_H = round(8 * IN, 4)         # 0.2032 m, a stringer's depth: an 8 in channel, so a
                                      # 4 in tread fits inside it at a 56 degree pitch
TREAD_D = round(4 * IN, 4)            # 0.1016 m, a tread along the run
TREAD_T = round(0.375 * IN, 4)        # 0.0095 m
#: the stringer's top over the nosing line
LIFT = 0.03
#: the hatch's length along X, in the stair band
HATCH = 0.75
LADDER_RAIL_T = round(0.375 * IN, 4)  # 0.0095 m, a drop ladder rail's thickness across X
RUNG = round(0.75 * IN, 4)            # 0.0191 m, a square rung
RUNG_PITCH = round(12 * IN, 4)        # 0.3048 m
#: a post's top over its top rail's
POST_PROUD = 0.006
#: a member's end inside the one it runs into (Zoo's JOIN)
SINK = 0.004
#: a rail's end inside its post: deeper than a rail's section nests, so two rails meeting in one post stay apart
RAIL_SINK = 0.010
#: how much narrower, each side, a member is than the one it runs into
NEST = 0.003
FORMS = ("flight_a", "flight_b", "top_a", "top_b", "drop")
MAT = "steel"
PART = "FireEscape_Steel"
#: the box a ladder may be at most this wide; a flight needs a storey at least this tall
LADDER_MAX_W = 0.8
FLIGHT_MIN_H = 2.0


def form_for(w, d, h):
    """The form a box of ``w`` x ``d`` x ``h`` can be, for a slot that names none."""
    if float(w) <= LADDER_MAX_W:
        return "drop"
    return "flight_a" if float(h) >= FLIGHT_MIN_H else "top_a"


def form_of(form, w, d, h):
    """The form drawn for a slot's ``form``: none or "auto" is `form_for` the box."""
    f = (str(form) if form not in (None, "") else "auto").lower()
    if f == "auto":
        return form_for(w, d, h)
    if f not in FORMS:
        raise ValueError("fire_escape has no form %r (it draws %s)" % (form, ", ".join(FORMS)))
    return f


def _box(x0, x1, y0, y1, z0, z1):
    return prims.box(PART, MAT, (min(x0, x1), min(y0, y1), min(z0, z1)),
                     (max(x0, x1), max(y0, y1), max(z0, z1)))


def _sloped(xa, xb, y0, y1, za_bot, zb_bot, za_top, zb_top):
    """A sheared bar from ``xa`` to ``xb``, whichever comes first, each end at its own heights."""
    if xa > xb:
        xa, xb, za_bot, zb_bot, za_top, zb_top = xb, xa, zb_bot, za_bot, zb_top, za_top
    return sheared(PART, MAT, xa, xb, min(y0, y1), max(y0, y1), za_bot, zb_bot, za_top, zb_top)


def _slat_rows(y0, y1):
    """Slat centres across ``y0`` .. ``y1``: `SLAT` wide, as few as keep the clear between them, and at either
    end, at most `SLAT_GAP`."""
    n = max(1, math.ceil((y1 - y0 - SLAT_GAP) / (SLAT + SLAT_GAP) - 1e-9))
    gap = (y1 - y0 - n * SLAT) / (n + 1)
    return [y0 + gap * (i + 1) + SLAT * (i + 0.5) for i in range(n)]


def _band(d):
    """``(yb0, yb1)``: the stair band, from inside the front bar `FLIGHT_W` back."""
    yb0 = -d / 2.0 + FRAME
    return yb0, yb0 + FLIGHT_W


def _landing(w, d, z0, hatch):
    """The deck at ``z0``, its top at ``z0 + FRAME``. ``hatch`` is -1 or +1: the end of the stair band left open."""
    x0, x1, y0, y1 = -w / 2.0, w / 2.0, -d / 2.0, d / 2.0
    zt = z0 + FRAME
    yb0, yb1 = _band(d)
    out = [_box(x0, x1, y0, y0 + FRAME, z0, zt),      # the front bar
           _box(x0, x1, y1 - FRAME, y1, z0, zt)]      # the back bar, against the wall
    # level 1: the side bars, between the front and back bars
    for side in (-1, 1):
        out.append(_box(side * (w / 2.0 - NEST), side * (w / 2.0 - FRAME + NEST),
                        y0 + FRAME - SINK, y1 - FRAME + SINK, z0 + NEST, zt - NEST))
    # level 2: the band bar, along the stair band's inner edge, between the side bars
    side_in = w / 2.0 - FRAME + NEST                  # a side bar's inner face, |x|
    out.append(_box(-(side_in + SINK), side_in + SINK, yb1, yb1 + FRAME - 2 * NEST,
                    z0 + 2 * NEST, zt - 2 * NEST))
    # level 3: the hatch's trimmer, across the band at the hatch's inner edge, front bar to band bar
    xh = hatch * (w / 2.0 - HATCH)
    th = FRAME - 4 * NEST
    tx0, tx1 = (xh - th, xh) if hatch < 0 else (xh, xh + th)
    out.append(_box(tx0, tx1, y0 + FRAME - SINK, yb1 + SINK, z0 + 3 * NEST, zt - 3 * NEST))
    # level 4: the slats, their tops 4 NEST under the deck's top
    st1 = zt - 4 * NEST
    st0 = st1 - SLAT_T
    end_in = side_in + SINK                           # a slat's end, SINK inside a side bar
    a, b = ((tx1 - SINK, end_in) if hatch < 0 else (-end_in, tx0 + SINK))
    for yc in _slat_rows(yb0, yb1):                   # the band: trimmer to the far side bar
        out.append(_box(a, b, yc - SLAT / 2, yc + SLAT / 2, st0, st1))
    for yc in _slat_rows(yb1 + FRAME - 2 * NEST, y1 - FRAME):    # behind the band: full width
        out.append(_box(-end_in, end_in, yc - SLAT / 2, yc + SLAT / 2, st0, st1))
    return out, zt


def _guards(w, d, zt, top):
    """The guards on a deck's three open sides: corner posts from inside the deck to ``top``, the front guard's
    rails `POST_PROUD` under it, the end guards' `NEST` under those."""
    x0, x1, y0, y1 = -w / 2.0, w / 2.0, -d / 2.0, d / 2.0
    post = {}
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            px = (x0 + 2 * NEST, x0 + 2 * NEST + POST) if sx < 0 else (x1 - 2 * NEST - POST, x1 - 2 * NEST)
            py = (y0 + 2 * NEST, y0 + 2 * NEST + POST) if sy < 0 else (y1 - 2 * NEST - POST, y1 - 2 * NEST)
            out.append(_box(px[0], px[1], py[0], py[1], zt - SINK, top))
            post[(sx, sy)] = (px, py)
    rail_top = top - POST_PROUD
    bc = zt + BOTTOM_Z
    # the front guard, between the two front posts
    (lx, ly), (rx, _ry) = post[(-1, -1)], post[(1, -1)]
    a, b = lx[1] - RAIL_SINK, rx[0] + RAIL_SINK
    out.append(_box(a, b, ly[0] + NEST, ly[1] - NEST, rail_top - RAIL_T, rail_top))
    out.append(_box(a, b, ly[0] + 2 * NEST, ly[1] - 2 * NEST, bc - RAIL_T / 2, bc + RAIL_T / 2))
    yc = (ly[0] + ly[1]) / 2.0
    for xc in pickets(lx[1], rx[0], PICKET):
        out.append(_box(xc - PICKET / 2, xc + PICKET / 2, yc - PICKET / 2, yc + PICKET / 2,
                        bc, rail_top - RAIL_T / 2))
    # the end guards, front post to back post, a NEST lower
    et, eb = rail_top - NEST, bc - NEST
    for sx in (-1, 1):
        (px, fy), (_px, by) = post[(sx, -1)], post[(sx, 1)]
        a, b = fy[1] - RAIL_SINK, by[0] + RAIL_SINK
        out.append(_box(px[0] + NEST, px[1] - NEST, a, b, et - RAIL_T, et))
        out.append(_box(px[0] + 2 * NEST, px[1] - 2 * NEST, a, b, eb - RAIL_T / 2, eb + RAIL_T / 2))
        xc = (px[0] + px[1]) / 2.0
        for yc in pickets(fy[1], by[0], PICKET):
            out.append(_box(xc - PICKET / 2, xc + PICKET / 2, yc - PICKET / 2, yc + PICKET / 2,
                            eb, et - RAIL_T / 2))
    return out


def _flight(w, d, zt, z1, hatch):
    """The flight in the stair band: from the hatch's inner edge on the deck whose top is ``zt`` to the box's top
    ``z1`` at the far end, rising toward ``-hatch``."""
    yb0, yb1 = _band(d)
    up = -hatch
    xf = hatch * (w / 2.0 - HATCH)                    # the foot: the hatch's inner edge
    xt = up * (w / 2.0 - 2 * NEST)                    # the top: the far end
    run = abs(xt - xf)
    n1 = z1 - LIFT                                    # the nosing line's top, under the stringers' top
    rise = n1 - zt
    if run <= 4 * TREAD_D or rise <= 2 * RISER:
        raise ValueError("a flight %.3f m long rising %.3f m is too short to draw" % (run, rise))
    slope = rise / run

    def nose(x):
        return zt + slope * abs(x - xf)

    out = []
    # the stringers: top LIFT over the nosing line, STRINGER_H deep, from where their bottom has risen to the deck's
    # top less SINK
    xs = xf + up * max(0.0, (STRINGER_H - LIFT - SINK) / slope)
    for ya, yb in ((yb0 + NEST, yb0 + NEST + STRINGER_T), (yb1 - NEST - STRINGER_T, yb1 - NEST)):
        out.append(_sloped(xs, xt, ya, yb, nose(xs) + LIFT - STRINGER_H, nose(xt) + LIFT - STRINGER_H,
                           nose(xs) + LIFT, nose(xt) + LIFT))
    # the treads: n risers make n - 1 treads, the last riser landing on the next deck. A tread's nosing lies on the
    # nosing line and it runs up-slope from there, its ends SINK inside the stringers; it is as deep as leaves a NEST
    # and more to the next and keeps inside the stringers' depth, so a steep flight's treads are narrow, as the old
    # ones are, and the top one stops a step short of the stringers' end
    n = max(2, math.ceil(rise / RISER - 1e-9))
    step = run / n
    td = min(TREAD_D, step - 3 * NEST, (STRINGER_H - LIFT - TREAD_T - 2 * NEST) / slope)
    ty0, ty1 = yb0 + NEST + STRINGER_T - SINK, yb1 - NEST - STRINGER_T + SINK
    for k in range(1, n):
        xk = xf + up * k * step
        out.append(_box(xk, xk + up * td, ty0, ty1, nose(xk) - TREAD_T, nose(xk)))
    # the handrail, GUARD_H over the nosing line, along the landing's front line. At the foot its section is the
    # front guard's top rail's -- the same top and bottom, a NEST inside its sides -- so its end lies inside that
    # rail, which has no face there; it rises to where its top reaches the box's top. No post of its own: one at the
    # foot stood where a tread's end could meet it.
    hy0 = -d / 2.0 + 2 * NEST + 2 * NEST
    hy1 = -d / 2.0 + 2 * NEST + POST - 2 * NEST
    xe = xf + up * min(run, (z1 - zt - GUARD_H) / slope)
    out.append(_sloped(xf, xe, hy0, hy1, nose(xf) + GUARD_H - RAIL_T, nose(xe) + GUARD_H - RAIL_T,
                       nose(xf) + GUARD_H, nose(xe) + GUARD_H))
    return out, {"treads": n - 1, "pitch_deg": round(math.degrees(math.atan2(rise, run)), 3),
                 "riser_m": round(rise / n, 4), "tread_m": round(td, 4)}


def _drop(w, d, h):
    """The drop ladder: two rails the box's height, rungs `RUNG_PITCH` apart from the top, their ends inside the
    rails."""
    x0, x1, z0, z1 = -w / 2.0, w / 2.0, -h / 2.0, h / 2.0
    if d < RUNG + 2 * NEST or w < 2 * LADDER_RAIL_T + 4 * RUNG:
        raise ValueError("a drop ladder %.3f x %.3f m cannot nest its rungs" % (w, d))
    out = [_box(x0, x0 + LADDER_RAIL_T, -d / 2, d / 2, z0, z1),
           _box(x1 - LADDER_RAIL_T, x1, -d / 2, d / 2, z0, z1)]
    ra, rb = x0 + LADDER_RAIL_T - SINK, x1 - LADDER_RAIL_T + SINK
    zc = z1 - RUNG_PITCH / 2
    n = 0
    while zc - RUNG / 2 >= z0 + RUNG:
        out.append(_box(ra, rb, -RUNG / 2, RUNG / 2, zc - RUNG / 2, zc + RUNG / 2))
        zc -= RUNG_PITCH
        n += 1
    return out, {"rungs": n}


def plan(w, d, h, form=None):
    """The fire escape's storey for a slot of ``w`` x ``d`` x ``h`` (X along the facade, the wall at +Y): ``{prims,
    collision, form, facts}``. ``collision`` is empty."""
    w, d, h = float(w), float(d), float(h)
    f = form_of(form, w, d, h)
    z0, z1 = -h / 2.0, h / 2.0
    if f == "drop":
        out, facts = _drop(w, d, h)
    else:
        hatch = -1 if f.endswith("_a") else 1
        yb0, yb1 = _band(d)
        if yb1 + FRAME - 2 * NEST + SLAT + 2 * SLAT_GAP > d / 2.0 - FRAME:
            raise ValueError("a landing %.3f m deep leaves no deck behind its %.3f m stair band" % (d, FLIGHT_W))
        if w < 2 * HATCH:
            raise ValueError("a landing %.3f m wide cannot hold a %.2f m hatch and a flight" % (w, HATCH))
        out, zt = _landing(w, d, z0, hatch)
        if f.startswith("flight"):
            top = zt + GUARD_H + POST_PROUD
            out += _guards(w, d, zt, top)
            fl, facts = _flight(w, d, zt, z1, hatch)
            out += fl
            facts["guard_m"] = GUARD_H
        else:
            if z1 - POST_PROUD - zt < BOTTOM_Z + 2 * RAIL_T:
                raise ValueError("a top landing %.3f m tall has no room for its guard" % h)
            out += _guards(w, d, zt, z1)
            facts = {"guard_m": round(z1 - POST_PROUD - zt, 4)}
    out, _boxes = prims.fit_exact(out, (-w / 2, -d / 2, -h / 2), (w / 2, d / 2, h / 2))
    facts["tris"] = prims.tri_count(out)
    return {"prims": out, "collision": [], "form": f, "facts": facts}
