"""cash_cart recipe: a bank's money cart -- a steel cage on casters, a deck, corner posts and rails, bars on three sides,
an open end with a push handle, sealed deposit bags and strapped bundles stacked on the deck.

Zoo 1.135.0, from the walker's bank comps (the factory's docs/reference/BANK_INTERIOR_COMPS.md, 2026-10-27): the money
room's "canvas hampers on wheels, a steel cage cart" (comp 10) and the cash-in-transit depot's "carts and tubs" (comp
11). Minted by `tools/new_species.py`; shaped here.

REFERENCE: the steel security cage cart a vault or a cash depot moves money in -- a flat steel deck on four swivel
casters, a frame of corner posts and top and middle rails, vertical bars about a hand apart on both long sides and
the far end, the near end open behind a push handle. On the deck, what it carries: clear and grey deposit bags,
sealed, and strapped bundles, in a stack whose top stays under the rails.

TWO MATERIALS: the steel (the plan's material: metal by default), the casters' black rubber as COLOUR ONLY in the
`Wear` vertex colour (`geometry.tint_wear`); and the load, every bag's and bundle's colour in the same vertex colour,
in a second. Two submissions whatever its size. The load is the VARIANT: which bags and how they stack follows
`variant`, so two carts in one vault differ.

Recipe frame: centre pivot, the handle end at -x. The module is exactly (w, d, h): the deck and frame are the
footprint, the casters stand on the floor, the top rail is the slot's top.
"""
from __future__ import annotations

import random

from ..bpylayer import geometry, materials

CASTER_H = 0.12          # floor to the deck's underside
CASTER_W = 0.07
DECK_T = 0.035
POST = 0.035             # a corner post's square section
RAIL = 0.025             # a rail's square section
BAR = 0.012              # a bar's square section
BAR_PITCH = 0.10         # bars this far apart, centre to centre
INSET = 0.004            # a rail and a bar stand this far inside a post's outer faces: never on their plane
BURY = 0.008
STACK_IN = 0.01          # a bag stacked on another stands this far inside it, every side
LONG_END = 0.012         # a long rail's end, this far inside the post's outer face
SHORT_END = POST - (POST - RAIL - INSET) / 2.0     # a short rail's end: between the long rail's and the post's inner faces

RUBBER = (0.05, 0.05, 0.05)
#: the load's colours: grey and clear-blue bags, strapped bundles in green and tan
LOAD = ((0.55, 0.56, 0.58), (0.62, 0.70, 0.78), (0.30, 0.42, 0.28), (0.66, 0.58, 0.42), (0.80, 0.80, 0.82))


def layout(w, d, h, variant=0):
    """``[(part, kind, [(centre, size), ...], rgb)]``, kind ``"steel"`` or ``"load"``. Pure: the tests read it."""
    z0, z1 = -h / 2.0, h / 2.0
    deck_z0 = z0 + CASTER_H
    deck_z1 = deck_z0 + DECK_T
    x0, x1, y0, y1 = -w / 2.0, w / 2.0, -d / 2.0, d / 2.0
    parts = []
    # the deck, inside the posts' outer faces
    parts.append(("CashCart_Deck", "steel",
                  [((0.0, 0.0, (deck_z0 + deck_z1) / 2.0), (w - 2.0 * INSET, d - 2.0 * INSET, DECK_T))], (1, 1, 1)))
    # four casters under the deck's corners, into it
    # into the deck by half a bury: a whole one is the posts' foot, and the two would share its plane
    cz0, cz1 = z0, deck_z0 + BURY / 2.0
    casters = [((sx * (w / 2.0 - POST), sy * (d / 2.0 - POST), (cz0 + cz1) / 2.0), (CASTER_W, CASTER_W, cz1 - cz0))
               for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]
    parts.append(("CashCart_Casters", "steel", casters, RUBBER))
    # the corner posts, from inside the deck to the slot's top
    pz0 = deck_z0 + BURY
    posts = [((sx * (w / 2.0 - POST / 2.0), sy * (d / 2.0 - POST / 2.0), (pz0 + z1) / 2.0), (POST, POST, z1 - pz0))
             for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]
    parts.append(("CashCart_Posts", "steel", posts, (1, 1, 1)))
    # rails: top and middle, round all four sides, inside the posts' outer faces and below the top by INSET. At a
    # corner the long rail runs to LONG_END inside the post's outer face and the short rail stops SHORT_END inside it,
    # half way between the long rail's inner face and the post's: each end face stands 3 mm or more off every plane
    # it meets (the first cut ran both to a bury past the post and put a short rail's end 2 mm from a long rail).
    rails = []
    for rz in (z1 - RAIL / 2.0 - INSET, (deck_z1 + z1) / 2.0):
        for sy in (-1.0, 1.0):
            rails.append(((0.0, sy * (d / 2.0 - RAIL / 2.0 - INSET), rz), (w - 2.0 * LONG_END, RAIL, RAIL)))
        for sx in (-1.0, 1.0):
            rails.append(((sx * (w / 2.0 - RAIL / 2.0 - INSET), 0.0, rz), (RAIL, d - 2.0 * SHORT_END, RAIL)))
    parts.append(("CashCart_Rails", "steel", rails, (1, 1, 1)))
    # bars: both long sides and the far (+x) end, from inside the deck to inside the top rail
    bz0, bz1 = deck_z1 - BURY, z1 - RAIL / 2.0 - INSET
    bars = []
    n = max(1, int((w - 2.0 * POST) // BAR_PITCH))
    for i in range(1, n):
        bx = x0 + POST + i * (w - 2.0 * POST) / n
        for sy in (-1.0, 1.0):
            bars.append(((bx, sy * (d / 2.0 - RAIL / 2.0 - INSET), (bz0 + bz1) / 2.0), (BAR, BAR, bz1 - bz0)))
    m = max(1, int((d - 2.0 * POST) // BAR_PITCH))
    for j in range(1, m):
        by = y0 + POST + j * (d - 2.0 * POST) / m
        bars.append(((x1 - RAIL / 2.0 - INSET, by, (bz0 + bz1) / 2.0), (BAR, BAR, bz1 - bz0)))
    parts.append(("CashCart_Bars", "steel", bars, (1, 1, 1)))
    # the push handle: a grip bar across the open end, between the posts, a hand below the top rail
    hz = z1 - RAIL - INSET - 0.10
    parts.append(("CashCart_Handle", "steel",
                  [((x0 + RAIL / 2.0 + INSET, 0.0, hz), (RAIL, d - 2.0 * POST + 2.0 * BURY, RAIL))], RUBBER))
    # the load: bags and bundles on the deck, in two layers, the variant's
    rng = random.Random("cash_cart:%d" % int(variant))
    load = []
    lx0, lx1 = x0 + POST + 0.03, x1 - POST - 0.03
    ly0, ly1 = y0 + POST + 0.03, y1 - POST - 0.03
    top_room = bz1 - deck_z1 - 0.06
    cols = max(1, int((lx1 - lx0) // 0.32))
    rows = max(1, int((ly1 - ly0) // 0.26))
    cw, rw = (lx1 - lx0) / cols, (ly1 - ly0) / rows
    for i in range(cols):
        for j in range(rows):
            stack = deck_z1 - BURY
            sx, sy = cw * (0.70 + 0.18 * rng.random()), rw * (0.70 + 0.18 * rng.random())
            cx = lx0 + (i + 0.5) * cw + (rng.random() - 0.5) * (cw - sx) * 0.8
            cy = ly0 + (j + 0.5) * rw + (rng.random() - 0.5) * (rw - sy) * 0.8
            for layer in range(2 if rng.random() < 0.6 else 1):
                if layer:
                    # A BAG ON A BAG IS SMALLER, and stands STACK_IN or more inside the one under it on every side:
                    # drawn independently, two stacked bags' sides landed 1-2 mm apart (the census, 2.4 m corner)
                    px, py = sx, sy
                    sx, sy = px * (0.60 + 0.25 * rng.random()), py * (0.60 + 0.25 * rng.random())
                    cx += (rng.random() - 0.5) * (px - sx - 2.0 * STACK_IN)
                    cy += (rng.random() - 0.5) * (py - sy - 2.0 * STACK_IN)
                bh = min(top_room / 2.0, 0.12 + 0.10 * rng.random())
                load.append(((cx, cy, stack + bh / 2.0), (sx, sy, bh), LOAD[rng.randrange(len(LOAD))]))
                stack += bh - BURY
    return parts, load


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    variant = int(plan.get("variant") or (plan.get("params") or {}).get("variant") or 0)
    rng = streams.stream("wear")
    steel_objs, load_objs = [], []
    parts, load = layout(w, d, h, variant)
    for name, _kind, boxes, rgb in parts:
        bm = geometry.new_bm()
        for centre, size in boxes:
            geometry.add_box(bm, centre, size)
        o = geometry.bm_to_object(bm, name, collection, bevel=bevel, texel=1.2, rng=rng, wear=wear)
        geometry.tint_wear(o, rgb)
        steel_objs.append(o)
    for k, (centre, size, rgb) in enumerate(load):
        bm = geometry.new_bm()
        geometry.add_box(bm, centre, size)
        o = geometry.bm_to_object(bm, "CashCart_Load_%d" % k, collection, bevel=0.0, texel=1.2, rng=rng, wear=wear)
        geometry.tint_wear(o, rgb)
        load_objs.append(o)
    steel = materials.make_material(f"M_CashCart_{plan['material']}", plan["color"], plan["material"])
    bags = materials.make_material("M_CashCart_load", (1.0, 1.0, 1.0), "plastic")
    materials.assign(steel_objs, steel)
    materials.assign(load_objs, bags)
    return {"objects": steel_objs + load_objs,
            "collision_boxes": [((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, h / 2.0))],
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
