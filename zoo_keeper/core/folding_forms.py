"""The card shop's play area: a folding table and a folding chair, planned in
pure Python (no bpy).

Zoo 0.95.0. The reference (`docs/SET_DRESSING_REFERENCES.md`): "The play
area: long folding tables (white plastic or covered in a black tablecloth)
with black folding chairs, card playmats on the table, piles of cards, deck
boxes, dice. A small tournament area has several tables in rows."

FRAME AND UNITS: metres, Z up, the slot's box, -Y the near side, base at
z = 0, plan centred on x = y = 0.

WHAT IS ON THE TABLE IS STOCK, NOT PARTS, and that is the pipeline's own
answer rather than a shortcut: `_surface_stock` is how Deli Counter asks a
top to be dressed (`kit.DRESSING_FIELDS`), it already keeps the no-overhang,
no-shared-plane and contrast rules, and putting the playmats there gives
them to `table`, `desk`, `counter` and `filing_cabinet` in the same move.
The flavour is `cards`. What it costs is that `prim_mesh.build_stock` has no
TEXTURED path, so a playmat is a dark mat with a printed border in flat
colour rather than art -- the same trade `bar_dense` records for its bottle
labels. What the textured version would buy is one more atlas and about two
triangles a mat; it is not built because nothing else in `_surface_stock` is
textured and making one flavour the exception is how a rule stops being one.

THE LEGS ARE ROTATED BOXES, not tubes. `prims.rod` at 8 segments is 48
triangles a leg; a box is 12, and a folding table has eight leg members plus
braces. At the distance a play area is seen from, the silhouette is the
splay and not the section.
"""
from __future__ import annotations

import math

from . import prims as P

TABLE_FORMS = ("bare", "cloth", "auto")

JOIN = 0.004
#: The table top: a folded plastic banquet top, and how far it overhangs the
#: frame on every side (it owns all six of the slot's planes but z = 0).
TOP_T = 0.030
TOP_OVER = 0.035
#: The leg frame: section, how far in from the end each frame stands, and
#: the splay at the floor as a fraction of the table's depth.
LEG_T = 0.032
FRAME_IN = 0.22
#: The two insets a variant picks between, as multiples of `FRAME_IN`.
FRAME_INSETS = (1.0, 1.45)
SPLAY_F = 0.30
FOOT_T = 0.018
#: The cloth: how far in from the top's edge it hangs, and the hem band.
CLOTH_IN = 0.018
HEM_H = 0.060
HEM_OUT = 0.010

#: The chair.
SEAT_T = 0.026
SEAT_F = 0.62           # seat depth as a fraction of the slot's depth
BACK_T = 0.024
POST_T = 0.030
#: 22 and not 26: a leg is centred on the same x as its back post, and at
#: 26 its side planes sat 2.0 mm off the post's 30 -- the tolerance
#: exactly, on all four legs.
CHAIR_LEG_T = 0.022
BRACE_T = 0.020
#: Seat height above the floor, and the rake of the back off plumb.
SEAT_H = 0.455
RAKE_DEG = 9.0

TOP, FRAME, CLOTH, HEM, SEAT, PAN = "top", "frame", "cloth", "hem", "seat", "pan"


def pick_table_form(asked):
    asked = (asked or "auto").lower()
    return asked if asked in ("bare", "cloth") else "cloth"


# --- the table ---------------------------------------------------------------


def _leg_frame(prims, tag, cy, x0, x1, top_under, d):
    """One folding leg frame: two splayed members a side, a foot bar on the
    floor and a cross brace. Built upright and turned about X, which is the
    axis the splay is about."""
    splay = d * SPLAY_F / 2.0
    for side, sx in ((0, x0), (1, x1)):
        lean = math.atan2(splay, top_under)
        leg = P.box(f"FoldingTable_Leg{tag}{side}", FRAME,
                    (sx - LEG_T / 2.0, cy - LEG_T / 2.0, 0.0),
                    (sx + LEG_T / 2.0, cy + LEG_T / 2.0, top_under + JOIN))
        prims.append(P.rotate_x(leg, (1 if side else -1) * lean,
                                about=(cy, top_under)))
    # the foot bar reaches PAST its legs rather than flush with them: flush,
    # the bar's end planes were the legs' own (0.00039 m2 a pair, both frames)
    prims.append(P.box(f"FoldingTable_Foot{tag}", FRAME,
                       (x0 - LEG_T / 2.0 - JOIN, cy - splay - FOOT_T, 0.0),
                       (x1 + LEG_T / 2.0 + JOIN, cy - splay + FOOT_T, FOOT_T)))
    prims.append(P.box(f"FoldingTable_Brace{tag}", FRAME,
                       (x0, cy - LEG_T / 2.0 - 0.002, top_under * 0.42),
                       (x1, cy + LEG_T / 2.0 + 0.002, top_under * 0.42 + 0.018)))


def plan_table(w, d, h, params=None, variant=0):
    """``{"prims", "regions", "collision", "facts"}``; ``regions`` are
    `_surface_stock.plan_surface` rows, one per half of the top, so two
    players' worth of playmats face each other across it."""
    w, d, h = float(w), float(d), float(h)
    params = params or {}
    variant = int(variant or 0)
    form = pick_table_form(params.get("form"))
    prims = []
    x0, x1 = -w / 2.0, w / 2.0
    y0, y1 = -d / 2.0, d / 2.0
    top_under = h - TOP_T
    # THE TOP owns z = h and all four sides: a banquet top overhangs its
    # frame, which is true and is also what keeps one part per plane.
    prims.append(P.box("FoldingTable_Top", TOP, (x0, y0, top_under), (x1, y1, h)))
    # A VARIANT IS WHERE THE FRAMES STAND, and it has to be something: a
    # `module_variants` that changes nothing but wear noise is one
    # `kit.honour_dressing` refuses to carry, and an unused ``variant``
    # parameter is somebody's abandoned intent. A banquet table's leg frames
    # sit at one of two insets depending on how it folds.
    frame_in = FRAME_IN * FRAME_INSETS[variant % len(FRAME_INSETS)]
    fx0, fx1 = x0 + frame_in, x1 - frame_in
    if fx1 - fx0 > 0.2:
        for tag, cy in (("A", y0 + d * 0.28), ("B", y1 - d * 0.28)):
            _leg_frame(prims, tag, cy, fx0, fx1, top_under, d)
    if form == "cloth":
        # A CLOTH TO THE FLOOR owns z = 0 and hides the frame. Two boxes
        # rather than one: the hem stands `HEM_OUT` proud, which is what
        # makes a cloth read as cloth and not as a plinth, and the two never
        # share a plane because the hem is wider on every side.
        cx0, cy0 = x0 + CLOTH_IN, y0 + CLOTH_IN
        cx1, cy1 = x1 - CLOTH_IN, y1 - CLOTH_IN
        prims.append(P.box("FoldingTable_Cloth", CLOTH,
                           (cx0, cy0, HEM_H - JOIN), (cx1, cy1, top_under + JOIN)))
        # THE CLOTH CLEARS THE FLOOR by 4 mm, which is both what a hem does
        # and what keeps z = 0 the FEET's plane alone -- flush, the hem and
        # both foot bars shared it over 0.0285 m2.
        prims.append(P.box("FoldingTable_Hem", HEM,
                           (cx0 - HEM_OUT, cy0 - HEM_OUT, 0.004),
                           (cx1 + HEM_OUT, cy1 + HEM_OUT, HEM_H)))
        colliders = [((cx0 - HEM_OUT, cy0 - HEM_OUT, 0.0),
                      (cx1 + HEM_OUT, cy1 + HEM_OUT, h))]
    else:
        colliders = [((x0, y0, top_under - 0.02), (x1, y1, h))]
    # TWO REGIONS, one a side, each facing the player at that side.
    # 22 mm and not 35: `_surface_stock` takes its own `EDGE` (20 mm) off
    # each side of whatever region it is handed, and a folding table is only
    # 0.76 m deep, so every millimetre here is a millimetre off the playmat
    # that has to fit in half of it.
    inset = 0.022
    mid = (y0 + y1) / 2.0
    regions = [(x0 + inset, x1 - inset, y0 + inset, mid - 0.004, h, 0.0, 0.5, ()),
               (x0 + inset, x1 - inset, mid + 0.004, y1 - inset, h,
                math.pi, 0.5, ())]
    facts = {"form": form, "variant": variant, "frames": 2,
             "frame_in_m": round(frame_in, 4),
             "tris": P.tri_count(prims), "regions": len(regions)}
    return {"prims": prims, "regions": regions, "collision": colliders,
            "facts": facts}


# --- the chair ---------------------------------------------------------------


def plan_chair(w, d, h, params=None, variant=0):
    """``{"prims", "collision", "facts"}``.

    ONE PART PER PLANE: the seat pan owns -X and +X (a folding chair's seat
    is its widest member), the back's cap rail owns z = h and +Y, the front
    feet own -Y, and all four feet own z = 0 -- four boxes, disjoint in
    plan, so no two of them meet on it.
    """
    w, d, h = float(w), float(d), float(h)
    params = params or {}
    variant = int(variant or 0)
    prims = []
    x0, x1 = -w / 2.0, w / 2.0
    y0, y1 = -d / 2.0, d / 2.0
    seat_h = min(SEAT_H, h * 0.55)
    seat_d = d * SEAT_F
    sy0 = y0 + d * 0.10
    sy1 = sy0 + seat_d

    prims.append(P.box("FoldingChair_Pan", PAN,
                       (x0, sy0, seat_h - SEAT_T), (x1, sy1, seat_h)))
    prims.append(P.box("FoldingChair_Lip", FRAME,
                       (x0 + 0.010, sy0 - 0.006, seat_h - SEAT_T - 0.016),
                       (x1 - 0.010, sy0 + 0.014, seat_h - SEAT_T + JOIN)))
    # THE BACK: two raked posts, a panel between them, a cap rail on top.
    rake = math.radians(RAKE_DEG)
    px = x1 - POST_T / 2.0 - 0.020
    for side, sx in ((0, -px), (1, px)):
        post = P.box(f"FoldingChair_Post{side}", FRAME,
                     (sx - POST_T / 2.0, sy1 - POST_T - 0.004, seat_h - 0.12),
                     (sx + POST_T / 2.0, sy1 - 0.004, h - 0.030))
        prims.append(P.rotate_x(post, -rake, about=(sy1, seat_h)))
    # the back panel sits INSIDE the posts on both faces: flush at the rear
    # it shared the posts' own back plane, 0.0070 m2 a post.
    # A VARIANT IS THE BACK: one slab, or two slats with daylight between
    # them. Both are folding chairs somebody owns, and a variant that changed
    # nothing but wear noise is one `kit.honour_dressing` refuses to carry.
    slatted = bool(variant % 2)
    bz0, bz1 = h * 0.62, h - 0.055
    bands = (((bz0, bz1),) if not slatted else
             ((bz0, bz0 + (bz1 - bz0) * 0.40),
              (bz0 + (bz1 - bz0) * 0.60, bz1)))
    for bi, (z0b, z1b) in enumerate(bands):
        back = P.box(f"FoldingChair_Back{bi}", SEAT,
                     (-px - POST_T / 2.0 + JOIN, sy1 - POST_T + 0.002, z0b),
                     (px + POST_T / 2.0 - JOIN, sy1 - 0.008, z1b))
        prims.append(P.rotate_x(back, -rake, about=(sy1, seat_h)))
    cap = P.box("FoldingChair_Cap", FRAME,
                (-px - POST_T / 2.0 - 0.004, sy1 - POST_T - 0.010, h - 0.048),
                (px + POST_T / 2.0 + 0.004, sy1 + 0.002, h))
    prims.append(P.rotate_x(cap, -rake, about=(sy1, seat_h)))
    # THE LEGS: a front pair splaying forward and a rear pair splaying back,
    # each with a foot that owns its own bit of the floor.
    for tag, (ax, ay, ty, sign) in (
            ("F0", (-px, sy0 + 0.02, y0 + FOOT_T, -1)),
            ("F1", (px, sy0 + 0.02, y0 + FOOT_T, -1)),
            ("R0", (-px, sy1 - 0.03, y1 - FOOT_T, 1)),
            ("R1", (px, sy1 - 0.03, y1 - FOOT_T, 1))):
        lean = math.atan2(abs(ty - ay), seat_h)
        leg = P.box(f"FoldingChair_Leg{tag}", FRAME,
                    (ax - CHAIR_LEG_T / 2.0, ay - CHAIR_LEG_T / 2.0, FOOT_T - JOIN),
                    (ax + CHAIR_LEG_T / 2.0, ay + CHAIR_LEG_T / 2.0,
                     seat_h - SEAT_T + JOIN))
        prims.append(P.rotate_x(leg, sign * lean, about=(ay, seat_h - SEAT_T)))
        prims.append(P.box(f"FoldingChair_Foot{tag}", FRAME,
                           (ax - CHAIR_LEG_T / 2.0 - 0.004, ty - FOOT_T,
                            0.0),
                           (ax + CHAIR_LEG_T / 2.0 + 0.004, ty + FOOT_T,
                            FOOT_T)))
    prims.append(P.box("FoldingChair_Brace", FRAME,
                       (-px, sy0 + 0.02, seat_h * 0.42),
                       (px, sy0 + 0.02 + BRACE_T, seat_h * 0.42 + BRACE_T)))
    # THE RAKE OVERSHOOTS THE SLOT in z -- the cap rail is turned about the
    # seat, so its far corner rises: measured 1.9 mm over a 0.78 m slot,
    # 0.5 mm over a 0.92 m one. `prims.fit_exact` takes it back out, the way
    # `dartboard` does with its open doors.
    prims, colliders = P.fit_exact(prims, (x0, y0, 0.0), (x1, y1, h),
                                   [((x0, y0, 0.0), (x1, y1, h))])
    facts = {"variant": variant, "back": "slats" if slatted else "panel",
             "seat_h_m": round(seat_h, 4),
             "rake_deg": RAKE_DEG, "tris": P.tri_count(prims)}
    return {"prims": prims, "collision": colliders, "facts": facts}


def bounds(got):
    return P.bounds(got["prims"])
