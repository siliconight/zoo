"""What a rowhouse stoop's iron railing is, in numbers: ONE place, no bpy.

Factory roadmap 240. The walker's comps of a Philadelphia rowhouse street (the factory's
`docs/reference/PHILLY_STREET_COMPS.md`): "three or four steps up to each door, with iron railings";
the walker's calls of 2026-10-13: three risers, concrete, "railings both sides -- build the
railings". Deli Counter stands each railing of a rowhome Empty's stoop as two slots of this species,
a LEVEL section along the landing and a FLIGHT section down the steps, and this module draws either
from its slot's box alone -- so a stoop of any rise or run is drawn without the module knowing it.

REFERENCE, the residential code where it speaks (IRC R311.7.8 and R312, as adopting jurisdictions
reproduce them; the sources are in the factory's `docs/proposals/ROWHOUSE_STOOP.md`):
  * a handrail 34 to 38 in above the nosings: `RAIL_H` is 36 in, the middle of that;
  * a rail that runs from above the top riser to above the bottom riser and ends in a newel post;
  * a guard's openings pass no 4 in sphere: `PICKET_CLEAR`, the look of a railing built to it;
  * the triangle under a stair's bottom rail passes no 6 in sphere: `BOTTOM_Z` keeps the bottom
    rail's underside 9 cm over its walking line.
A three-riser stoop needs neither a handrail nor a guard by that code (handrails from four risers,
guards over a 30 in drop): the railing drawn is the comps', and the code gives its numbers.

THE IRON is the common ornamental sizes, not a standard's: a 1-1/4 in square post, a 1-1/2 in flat
bar 3/4 in deep for the top rail, a 1 in bar for the bottom rail, and 5/8 in square pickets -- 1/2 in
is the usual picket; at 5/8 one holds a pixel a few metres further out, as the fence's tension wire is
drawn at twice its size.

THE FRAME is the module's own: X along the run, its HIGH end at +X (where a flight meets the landing,
toward the house); Y across, the slot's depth the top rail's width; Z up. Centre pivot, and the extents
are exactly the slot's (w, d, h).

THE FORMS
  level   along a landing. A post at each end, its top the box's top; the top rail between the posts,
          `POST_PROUD` under their tops; the bottom rail `BOTTOM_Z` over the box's bottom (the landing);
          pickets between.
  flight  down the steps. A post at the low end (-X), standing on the bottom tread -- the box's
          bottom; the top rail from `RAIL_H` over the post's foot there to the box's top at +X, where the
          flight meets the level section's post (that module draws it); the bottom rail parallel to it,
          `BOTTOM_Z` over the post's foot at the post; pickets between, SHEARED to the rails' pitch so
          their ends stay inside the rails at any pitch.

NO FACE OF ONE PART LIES ON ANOTHER'S, so `prims.coincident_pairs` reads none on either form before
Blender does. A rail's end stops `SINK` inside its post, a picket's ends lie on the rails' centre
lines, and a post stands `POST_PROUD` over the top rail. Across the module, each member is `NEST` (3
mm a side) narrower than the one it runs into: post inside top rail, bottom rail inside post, picket
inside bottom rail.

COLLISION: none here (the genome's `collision: false`). Deli Counter writes the railing's colliders
itself, in the greybox the graders walk, as it does the stoop's.
"""
from __future__ import annotations

import math

from . import prims

IN = 0.0254
#: the handrail's height over the walking line: IRC R311.7.8.1's 34-38 in, at 36 in
RAIL_H = round(36 * IN, 4)            # 0.9144 m
POST = round(1.25 * IN, 4)            # 0.0318 m, a square post
BOTTOM_W = round(1.0 * IN, 4)         # 0.0254 m, the bottom rail across
PICKET = round(0.625 * IN, 4)         # 0.0159 m, a square picket
RAIL_T = round(0.75 * IN, 4)          # 0.0191 m, either rail's depth (Z)
#: the clear between pickets, and between a picket and a post: IRC R312.1.3's 4 in sphere
PICKET_CLEAR = round(4 * IN, 4)       # 0.1016 m
#: the bottom rail's centre over its walking line (its underside 9 cm up, inside the 6 in rule)
BOTTOM_Z = 0.10
#: a post's top over the top rail's, so the two tops are never one plane
POST_PROUD = 0.006
#: a rail's end inside its post (Zoo's JOIN)
SINK = 0.004
#: how much narrower, each side, a member is than the one it runs into
NEST = 0.003
FORMS = ("level", "flight")
MAT = "iron"
PART = "StoopRailing_Iron"


def form_of(form):
    """The form drawn for a slot's ``form``: none or "auto" is ``level``."""
    f = (str(form) if form not in (None, "") else "auto").lower()
    if f == "auto":
        return "level"
    if f not in FORMS:
        raise ValueError("stoop_railing has no form %r (it draws %s)" % (form, ", ".join(FORMS)))
    return f


def members(d):
    """``(top_w, post, bottom_w, picket)`` across Y for a slot ``d`` deep: the top rail is the slot's
    depth and each member is `NEST` a side narrower than the one it runs into, at most its iron size."""
    top_w = float(d)
    post = min(POST, top_w - 2 * NEST)
    bottom_w = min(BOTTOM_W, post - 2 * NEST)
    picket = min(PICKET, bottom_w - 2 * NEST)
    if picket <= 0.0:
        raise ValueError("a stoop railing %.4f m deep cannot nest its members" % top_w)
    return top_w, post, bottom_w, picket


def pickets(x0, x1, width=PICKET):
    """Picket centres between ``x0`` and ``x1``: as few as keep every clear gap -- either end and
    between -- at most `PICKET_CLEAR`, the gaps equal."""
    span = x1 - x0
    n = max(0, math.ceil((span - PICKET_CLEAR) / (width + PICKET_CLEAR) - 1e-9))
    if n == 0:
        return []
    gap = (span - n * width) / (n + 1)
    return [x0 + gap * (i + 1) + width * (i + 0.5) for i in range(n)]


def sheared(part, mat, x0, x1, y0, y1, zb0, zb1, zt0, zt1, bevel=False):
    """A bar with vertical ends at ``x0`` and ``x1`` whose bottom runs ``zb0`` -> ``zb1`` and top
    ``zt0`` -> ``zt1``: `prims.box`'s corners and faces, each end at its own heights -- a shear of a
    box, so its faces keep their winding."""
    v = [(x0, y0, zb0), (x1, y0, zb1), (x1, y1, zb1), (x0, y1, zb0),
         (x0, y0, zt0), (x1, y0, zt1), (x1, y1, zt1), (x0, y1, zt0)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5),
         (2, 3, 7, 6), (3, 0, 4, 7)]
    return prims.mesh(part, mat, v, f, bevel)


def _level(w, d, h):
    top_w, post, bottom_w, picket = members(d)
    x0, x1, z0, z1 = -w / 2.0, w / 2.0, -h / 2.0, h / 2.0
    out = [prims.box(PART, MAT, (x0, -post / 2, z0), (x0 + post, post / 2, z1)),
           prims.box(PART, MAT, (x1 - post, -post / 2, z0), (x1, post / 2, z1))]
    rx0, rx1 = x0 + post - SINK, x1 - post + SINK
    top = z1 - POST_PROUD
    out.append(prims.box(PART, MAT, (rx0, -top_w / 2, top - RAIL_T), (rx1, top_w / 2, top)))
    bc = min(z0 + BOTTOM_Z, top - RAIL_T - RAIL_T)
    out.append(prims.box(PART, MAT, (rx0, -bottom_w / 2, bc - RAIL_T / 2),
                         (rx1, bottom_w / 2, bc + RAIL_T / 2)))
    tc = top - RAIL_T / 2
    for xc in pickets(x0 + post, x1 - post, picket):
        out.append(prims.box(PART, MAT, (xc - picket / 2, -picket / 2, bc),
                             (xc + picket / 2, picket / 2, tc)))
    return out, {"rail_top": [round(top, 6), round(top, 6)], "posts": 2}


def _flight(w, d, h):
    top_w, post, bottom_w, picket = members(d)
    x0, x1, z0, z1 = -w / 2.0, w / 2.0, -h / 2.0, h / 2.0
    xp = x0 + post / 2.0                         # the bottom post's centre
    lo = z0 + min(RAIL_H, h - POST_PROUD)        # the top rail's top over the post's foot

    def top_at(x):
        return lo + (z1 - lo) * (x - xp) / (x1 - xp)

    out = [prims.box(PART, MAT, (x0, -post / 2, z0),
                     (x0 + post, post / 2, min(z1, lo + POST_PROUD)))]
    # the top rail, from inside the post to the box's end
    out.append(sheared(PART, MAT, xp, x1, -top_w / 2, top_w / 2,
                       top_at(xp) - RAIL_T, top_at(x1) - RAIL_T, top_at(xp), top_at(x1)))
    # the bottom rail, parallel, BOTTOM_Z over the post's foot at the post
    drop = (lo - RAIL_T / 2) - min(z0 + BOTTOM_Z, lo - 2 * RAIL_T)

    def bottom_c(x):
        return top_at(x) - RAIL_T / 2 - drop

    out.append(sheared(PART, MAT, xp, x1, -bottom_w / 2, bottom_w / 2,
                       bottom_c(xp) - RAIL_T / 2, bottom_c(x1) - RAIL_T / 2,
                       bottom_c(xp) + RAIL_T / 2, bottom_c(x1) + RAIL_T / 2))
    for xc in pickets(x0 + post, x1, picket):
        a, b = xc - picket / 2, xc + picket / 2
        out.append(sheared(PART, MAT, a, b, -picket / 2, picket / 2,
                           bottom_c(a), bottom_c(b),
                           top_at(a) - RAIL_T / 2, top_at(b) - RAIL_T / 2))
    pitch = math.degrees(math.atan2(z1 - lo, x1 - xp))
    return out, {"rail_top": [round(lo, 6), round(z1, 6)], "posts": 1, "pitch_deg": round(pitch, 3)}


def plan(w, d, h, form=None):
    """The railing for a slot of ``w`` x ``d`` x ``h`` (X the run, its high end +X): ``{prims,
    collision, form, facts, overshoot_m}``. ``collision`` is empty: Deli Counter writes it."""
    f = form_of(form)
    w, d, h = float(w), float(d), float(h)
    out, facts = (_level if f == "level" else _flight)(w, d, h)
    out, _boxes = prims.fit_exact(out, (-w / 2, -d / 2, -h / 2), (w / 2, d / 2, h / 2))
    facts["tris"] = prims.tri_count(out)
    facts["pickets"] = len(out) - facts["posts"] - 2
    return {"prims": out, "collision": [], "form": f, "facts": facts, "overshoot_m": 0.0}
