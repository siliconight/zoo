"""What a run of retractable-belt queue stanchions is, in numbers: ONE place, no bpy.

Factory roadmap 267. The walker, 2026-10-20, on what lines a queue indoors: "stanchion or stanchions are likley more
common for banks and indoor common areas", "metal barriers are for outdoor concerts or riot protection from police",
and a photo of the thing itself -- black posts on round weighted bases, a flat black belt pulled taut between each
pair at waist height, lanes switching back in front of a registration desk. Deli Counter lays a box office's queue as
runs of this species, one straight run a slot: posts along the slot's width, a belt between each neighbouring pair.

REFERENCE, the common retractable-belt stanchion as suppliers list it (no code governs one): a post about 38 in tall,
2-1/2 in across, on a 14 in weighted base about 2 in high, the belt 2 in wide, pulled from a cassette in the post's head
to the next post, 7-1/2 ft of belt the usual reach.
  * `POST_R`, `HEAD_R`, `HEAD_H`: the post's tube and the cassette head the belt runs out of;
  * `BASE_H`: the domed base's height. It is also the rule the crowd barrier learned in Zoo 1.118.1: Deli Counter
    lays a room's floor finish as a 2 cm skin over the slab and stands props on the slab under it, so a base under
    2 cm is buried -- this one stands 3 cm proud of that skin;
  * `BELT_MAX`: the most belt between two posts, 7-1/2 ft; a run is as few posts as keep every span within it, the
    spans equal; `MIN_BELT`, the least that shows between two bases' rims, so the shortest run is two bases and
    some belt, never two bases touching;
  * `BELT_W`, `BELT_T`: the belt, 2 in high and drawn 6 mm thick (it is about 1), so it holds a pixel across a room.

THE FRAME is the module's own: X along the run, Y across (the base's diameter), Z up. Centre pivot, and the extents are
exactly the slot's (w, d, h): the end bases' rims are the run's ends, a base's diameter its depth, the heads' tops its
top. ONE MATERIAL, one part, one submission: black powder coat, the belt in the same black.

NO FACE OF ONE PART LIES ON ANOTHER'S, and no open end shows: a post is open at both ends, its foot inside its base and
its top inside its head; a base is open only at the floor, its top capped where the post rises through it; the belt
is one band from the first post's axis to the last's, its ends inside the end heads and its 6 mm inside a head's
flats -- a belt a span put two end faces on one plane inside every middle head. The bases' rings are twelve-sided,
since at 14 in across eight would read as an octagon; the posts' and heads' are eight, as every tube's in Zoo.

COLLISION: each post, base to head, and the belt line -- a thin band at the belt's height from end post to end post --
so a body cannot walk through a run, and a shot above or below the belt passes, as it would. Deli Counter writes no
box over a run (its `prop_species.SPECIES_OWNS_COLLISION`): a solid box would be cover the belt is not.
"""
from __future__ import annotations

import math

from . import prims

IN = 0.0254
POST_R = round(1.25 * IN, 5)          # a 2-1/2 in post
HEAD_R = round(1.5 * IN, 5)           # the cassette head, 3 in across
HEAD_H = round(4 * IN, 4)             # the head's height
BASE_H = round(2 * IN, 4)             # the domed base: 2 in, 3 cm proud of a 2 cm floor skin
BASE_TOP_R = round(1.75 * IN, 5)      # where the dome meets the post
BELT_MAX = round(90 * IN, 4)          # 7-1/2 ft of belt
BELT_W = round(2 * IN, 4)             # the belt's height
BELT_T = 0.006                        # its thickness, drawn heavier than the real 1 mm
#: the belt's centre under the head's top
BELT_DROP = round(2 * IN, 4)
#: the post's foot inside its base, under the base's top
SINK = 0.01
#: the least belt that shows between two bases' rims: closer, and a run is two bases touching
MIN_BELT = 0.2
SIDES = 8
BASE_SIDES = 12
MAT = "steel"
PART = "StanchionRun_Steel"
FLAT = math.cos(math.pi / SIDES)


def _open(p, keep=()):
    """``p`` with its two end caps (faces 0 and 1 of `prims.cyl`) dropped, but those in ``keep``."""
    q = dict(p)
    q["faces"] = [f for i, f in enumerate(p["faces"]) if i >= 2 or i in keep]
    return q


def post_xs(w, base_r):
    """The posts' centres along a run ``w`` long: the end bases' rims at its ends, as few posts as keep every belt
    within `BELT_MAX`, the spans equal."""
    x0, x1 = -w / 2.0 + base_r, w / 2.0 - base_r
    spans = max(1, math.ceil((x1 - x0) / BELT_MAX - 1e-9))
    return [x0 + (x1 - x0) * i / spans for i in range(spans + 1)]


def plan(w, d, h):
    """The run for a slot of ``w`` x ``d`` x ``h`` (X along it): ``{prims, collision, facts}``."""
    w, d, h = float(w), float(d), float(h)
    base_r = d / 2.0
    if w - 4 * base_r < MIN_BELT:
        raise ValueError("a stanchion run %.3f m long cannot stand two posts on %.3f m bases with %.2f m of belt "
                         "between them" % (w, d, MIN_BELT))
    if h < BASE_H + HEAD_H + 0.3:
        raise ValueError("a stanchion %.3f m tall cannot hold its head over its base" % h)
    z0, z1 = -h / 2.0, h / 2.0
    xs = post_xs(w, base_r)
    head0 = z1 - HEAD_H
    belt_z = z1 - BELT_DROP
    out = []
    for x in xs:
        # the domed base, open at the floor, its top capped: the post rises through it
        out.append(_open(prims.cyl(PART, MAT, (x, 0.0), base_r, z0, z0 + BASE_H, segments=BASE_SIDES,
                                   r_top=BASE_TOP_R), keep=(1,)))
        # the post, from inside the base to inside the head
        out.append(_open(prims.cyl(PART, MAT, (x, 0.0), POST_R, z0 + BASE_H - SINK, head0 + SINK, segments=SIDES)))
        # the head, capped both ends: the post rises into its underside
        out.append(prims.cyl(PART, MAT, (x, 0.0), HEAD_R, head0, z1, segments=SIDES))
    # the belt: ONE band from the first post's axis to the last's, through every head between. A belt a span, end
    # to end, put two belts' end faces on one plane inside each middle head (the census's pair); the heads hide the
    # joins either way
    out.append(prims.box(PART, MAT, (xs[0], -BELT_T / 2, belt_z - BELT_W / 2),
                         (xs[-1], BELT_T / 2, belt_z + BELT_W / 2)))
    boxes = [((x - POST_R, -POST_R, z0), (x + POST_R, POST_R, z1)) for x in xs]
    boxes.append(((xs[0], -BELT_T / 2, belt_z - BELT_W / 2), (xs[-1], BELT_T / 2, belt_z + BELT_W / 2)))
    out, boxes = prims.fit_exact(out, (-w / 2, -d / 2, z0), (w / 2, d / 2, z1), boxes)
    facts = {"tris": prims.tri_count(out), "posts": len(xs),
             "span": round((xs[-1] - xs[0]) / max(1, len(xs) - 1), 4), "belt_z": round(belt_z, 4)}
    return {"prims": out, "collision": boxes, "facts": facts}
