"""The card shop's showcase counter, planned in pure Python (no bpy).

Zoo 0.95.0. The reference (`docs/SET_DRESSING_REFERENCES.md`, "The walker's
trading card shop references"): "Showcase counters are the centrepiece:
glass-top, glass-front, aluminium-framed display cases in an L or U, two or
three glass shelves inside, every shelf packed with sealed boxes, tins and
blister packs, graded cards in slabs lying flat on the top shelf, loose packs
in piles." And from the 1990s photo the shop is built to: "A glass-top
showcase counter in front with a chrome frame, stacks of white card storage
boxes and toploaders on top".

FRAME AND UNITS: metres, Z up, the slot's own box -- x along the counter, -Y
the CUSTOMER side, +Y the staff side, base at z = 0, plan centred on
x = y = 0. `bpylayer.build` re-centres the finished module.

A RUN IS BUILT FACE BY FACE, and that is what makes the L work. Every run
is a body box plus a verdict per horizontal face: GLAZED (rails, mullions
and a pane -- the customer side), an END pane, a BACK with sliding doors
(the staff side), or buried. A flat case is one run glazed on -Y; an L is a
main run glazed on -Y and a corner run glazed on BOTH -Y and +X, which is
how the frontage turns the corner in one plane instead of two boxes meeting.
`_fbox` places every part in the face's own frame -- along the face, inward
from its plane -- so the same arithmetic serves all four orientations and
there is one set of offsets to keep off each other rather than four.

THE TOP OWNS THE BOUNDS. Of the six planes the slot measures, the glass top
owns z = h and all four sides (a counter top overhangs its body, which is
both true and the cheapest way to keep one part per plane) and the kick owns
z = 0. Everything else is `OVERHANG` inboard and buried `JOIN` up into the
glass. The top is ONE mesh for an L as well as for a flat case: two convex
quads sharing the inside corner's edge, never a concave n-gon, because
`prims.triangles` fans a face and fanning a concave hexagon makes triangles
that overlap each other on their own plane -- wrong geometry AND a
coincident pair against itself.

WHERE THE TWO RUNS MEET THEY DO NOT TOUCH. The corner run's near end stops
`CORNER_GAP` short of the main run's back rather than overlapping it. An
overlap there puts two bodies' side faces in one plane over the overlap
band, which is the defect `back_bar` records as "parts reaching the same
wall or the same end are STEPPED"; a gap costs one 8 mm shadow line on the
STAFF side of an inside corner, under a continuous glass top, and the
measurement that matters (`prims.coincident_pairs` at 2.2 mm over every
genome corner, both forms and every variant) reads zero.

THE STOCK IS CAPPED BY COUNT, NOT BY FIT -- see `CAPS` for each cap and
what the uncapped draw measured.
"""
from __future__ import annotations

from . import card_brands as CB
from . import prims as P
from ..recipes._bays import bays

FORMS = ("flat", "L", "auto")

# --- the shell ---------------------------------------------------------------

#: Parts that meet overlap by this; nothing in this species butts.
JOIN = 0.004
#: A thing standing on a surface sinks this far into it (`_shelf_stock`'s
#: rule, and the same reason: a bottom face resting exactly on a top face is
#: a coincident pair with no epsilon).
SINK = 0.003
#: How far an art quad stands proud of the face it is printed on. MEASURED
#: at 3.5 mm first and the probe reported every one of them: the offset was
#: taken from the surface the item STANDS on rather than from the item's own
#: face, and a box that sinks `SINK` into its shelf has its top `SINK / 2`
#: lower than that arithmetic assumed -- 3.5 mm became 2.0 mm, which is the
#: tolerance exactly. Every quad is placed off the item's measured face now.
ART_PROUD = 0.005
#: How far the glass top overhangs the body on every side. A real counter
#: top does; here it is also what lets ONE part own all four side planes.
OVERHANG = 0.012
#: The gap between an L's two runs at the inside corner. Derived: it must
#: exceed the coplanar window (2.2 mm in the tests, 2 mm in
#: `tools/coplanar_probe.py`) by enough that a float does not close it, and
#: it is the only thing standing between two bodies' side planes.
CORNER_GAP = 0.008
#: Toe kick: how far it is recessed from the body, and how tall.
KICK_SET = 0.05
KICK_H = 0.10
#: Glass: the top slab, the front and end panes, and a shelf.
TOP_T = 0.016
PANE_T = 0.010
SHELF_T = 0.008
#: The aluminium frame, measured INWARD from the glazed face's own plane.
#: Each part gets its own band and no two bands touch: the rails own the
#: face, the pane sits just behind them, the mullions behind that.
RAIL_T = 0.030
PANE_SET = 0.004
POST_SET = 0.018
POST_T = 0.026
#: The laminate deck the stock stands on, and the staff-side back panel.
DECK_T = 0.022
BACK_T = 0.014
#: How far a part that is NOT the end pane stays off an end plane. Each
#: value is a different part's inset, and they differ on purpose: two parts
#: sharing one inset share a side plane wherever their other ranges overlap,
#: which is how `Deck` and `RailLo` were first measured as a pair.
IN_RAIL = PANE_T + JOIN
IN_DECK = PANE_T + 0.010
IN_BACK = PANE_T + 0.016
#: The return run's horizontal faces are offset by this where it meets the
#: main run, so no two of them share a plane in the corner.
LEG_STEP = 0.005
#: THE OUTSIDE CORNER IS A POST, and it had to be. Where a run is glazed on
#: two adjacent faces, each face's rails, pane and mullions ran into the
#: corner and the two frames occupied the same square: identical z faces
#: over 0.030 x 0.030, which `coincident_pairs` reported as 0.0008 m2 a
#: pair, three pairs a corner. Trimming both frames back to a single square
#: column is what an extruded showcase frame actually does. The column
#: stands `CORNER_PROUD` out of BOTH body planes -- so it shares neither,
#: and 4 mm is well inside the top's 12 mm overhang.
CORNER_W = 0.040
CORNER_PROUD = 0.004

#: Material keys the recipe resolves.
GLASS, METAL, BODY, DECK, STOCK, ART = "glass", "metal", "body", "deck", "stock", "art"

#: WHAT EACH CAP IS AND WHAT IT BUYS, measured rather than asserted. The
#: budget is 3,000 (genome `budgets.tris_lod0`). At the genome's largest
#: slot, 6.0 x 3.0 x 1.25 form L:
#:
#:     caps lifted to 99 ("as many as fit")   209 items   3,434 tris
#:     these caps                              78 items   1,600 tris
#:     the first caps tried (7/3/6/4/5)        47 items   1,166 tris
#:
#: So the cap is load-bearing: uncapped is 114 % of budget at the corner
#: that matters, and it gets worse every time somebody widens the genome,
#: because "as many as fit" has no ceiling. It is also not the ONLY thing
#: paying -- the first caps were nearly twice as tight as the budget needed
#: and were loosened to spend the headroom, because the reference's shelves
#: are FULL and a half-stocked case is the wrong kind of cheap. What a
#: further raise would buy is measured above; it costs about 21 triangles
#: an item.
CAPS = {
    "boxes_per_shelf": 16,     # sealed booster boxes, faced out
    "tins_per_shelf": 6,
    "slabs_per_shelf": 12,     # graded cards lying flat on the top shelf
    "piles_per_shelf": 8,      # loose packs in a heap
    "storage_per_run": 6,      # white card boxes on the counter top
}

#: HOW FAR A VARIANT SHUFFLES A SHELF ALONG, metres. Without it two of the
#: four variants of a FLAT case were the same geometry -- the variant moves
#: which game each item wears and which end an L turns, and a flat case has
#: no end to turn, so variants 0 and 2 built identical vertices and
#: `kit.honour_dressing` would have been carrying a difference that was not
#: there. Nobody faces a shelf to the millimetre either.
NUDGE = (0.0, 0.007, -0.006, 0.013)


def _nudged(cx, half, x0, x1, variant, sign=1.0):
    """``cx`` shuffled by the variant, CLAMPED so the item stays inside the
    shelf run. Without the clamp the smallest case (0.9 x 0.45) pushed a
    booster box's side face to 1.9 mm off the shelf's own end -- a nudge
    that moves stock off the thing it stands on is not a variant, it is a
    defect wearing one's clothes."""
    return min(max(cx + sign * NUDGE[int(variant) % len(NUDGE)],
                   x0 + half), x1 - half)

#: Sizes, metres: a sealed booster box faced out, a tin, a graded slab, a
#: pile of loose packs, a white card-storage box.
BOX_W, BOX_H, BOX_D = 0.135, 0.092, 0.072
TIN_W, TIN_H, TIN_D = 0.200, 0.055, 0.135
SLAB_W, SLAB_L, SLAB_T = 0.086, 0.130, 0.011
PILE_W, PILE_D = 0.070, 0.100
STORE_W, STORE_D, STORE_H = 0.155, 0.345, 0.130

FACES = ("-X", "+X", "-Y", "+Y")
#: face -> (axis along the face, axis of its outward normal, that sign)
_AXES = {"-Y": (0, 1, -1), "+Y": (0, 1, 1), "-X": (1, 0, -1), "+X": (1, 0, 1)}
#: A face's tag in a part name: no sign characters, so every part name is
#: a plain identifier the genome's `parts` list can prefix-match.
_TAG = {"-Y": "Ym", "+Y": "Yp", "-X": "Xm", "+X": "Xp"}


def _case_depth(params, d):
    want = float((params or {}).get("case_depth", 0.60))
    return max(0.40, min(want, d))


def pick_form(asked, w, d, params=None):
    """``auto`` takes the L when the slot is deep enough for a return run
    with a staff aisle behind the main one, and wide enough to have a corner
    at one end. Otherwise flat."""
    asked = (asked or "auto").lower()
    if asked in ("flat", "l"):
        return "L" if asked == "l" else "flat"
    case_d = _case_depth(params or {}, d)
    return "L" if (d >= 2.0 * case_d + 0.10 and w >= 2.0 * case_d) else "flat"


# --- placement helpers -------------------------------------------------------


def _fbox(part, mat, face, body, a0, a1, d0, d1, z0, z1):
    """A box on ``face`` of ``body`` = ``((x0, x1), (y0, y1))``: ``a0..a1``
    along the face, ``d0..d1`` measured INWARD from its plane, ``z0..z1`` up.
    One frame for all four orientations."""
    along, out, sgn = _AXES[face]
    plane = body[out][1] if sgn > 0 else body[out][0]
    lo, hi = [0.0, 0.0, z0], [0.0, 0.0, z1]
    lo[along], hi[along] = a0, a1
    lo[out], hi[out] = sorted((plane - sgn * d0, plane - sgn * d1))
    return P.box(part, mat, tuple(lo), tuple(hi))


def _quad(part, tile, verts, uvs):
    p = P.mesh(part, ART, verts, [(0, 1, 2, 3)])
    p["tile"] = tile
    p["uvs"] = [uvs]
    return p


def _stood(part, mat, cx, cy, z0, sx, sy, sz, above=False):
    """A box standing on a surface at ``z0``, sunk `SINK` into it. Returns
    ``(prim, lo, hi)`` -- the MEASURED corners, so every art quad is placed
    off the face it prints on rather than off the surface underneath."""
    lo = (cx - sx / 2.0, cy - sy / 2.0, z0 - SINK)
    hi = (cx + sx / 2.0, cy + sy / 2.0, z0 + sz)
    p = P.box(part, mat, lo, hi)
    if above:
        p["above"] = True
    return p, lo, hi


_UV = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))


def _face_out(part, tile, lo, hi, inset=0.93, above=False):
    """The art on a box's CUSTOMER face (-Y), `ART_PROUD` in front of it."""
    cx, cz = (lo[0] + hi[0]) / 2.0, (lo[2] + hi[2]) / 2.0
    w, hgt = (hi[0] - lo[0]) * inset, (hi[2] - lo[2]) * inset
    y = lo[1] - ART_PROUD
    p = _quad(part, tile, [(cx - w / 2, y, cz - hgt / 2), (cx + w / 2, y, cz - hgt / 2),
                           (cx + w / 2, y, cz + hgt / 2), (cx - w / 2, y, cz + hgt / 2)],
              _UV)
    if above:
        p["above"] = True
    return p


def _face_up(part, tile, lo, hi, inset=0.92):
    """The art on a box's TOP face, `ART_PROUD` above it -- a graded slab
    lying flat on the case's top shelf, a tin's lid."""
    cx, cy = (lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0
    w, dep = (hi[0] - lo[0]) * inset, (hi[1] - lo[1]) * inset
    z = hi[2] + ART_PROUD
    return _quad(part, tile,
                 [(cx - w / 2, cy - dep / 2, z), (cx + w / 2, cy - dep / 2, z),
                  (cx + w / 2, cy + dep / 2, z), (cx - w / 2, cy + dep / 2, z)], _UV)


def _l_top(part, mat, rings, z0, z1):
    """A slab over a footprint given as one or two CONVEX quads sharing an
    edge: one mesh, no concave face."""
    verts, faces, index = [], [], {}

    def vid(x, y, z):
        k = (round(x, 6), round(y, 6), round(z, 6))
        if k not in index:
            index[k] = len(verts)
            verts.append((x, y, z))
        return index[k]

    for ring in rings:
        faces.append(tuple(vid(x, y, z1) for x, y in ring))
        faces.append(tuple(reversed([vid(x, y, z0) for x, y in ring])))
    seen = {}
    for ring in rings:
        for k in range(len(ring)):
            a, b = ring[k], ring[(k + 1) % len(ring)]
            key = tuple(sorted(((round(a[0], 6), round(a[1], 6)),
                                (round(b[0], 6), round(b[1], 6)))))
            seen[key] = seen.get(key, 0) + 1
    for ring in rings:
        for k in range(len(ring)):
            a, b = ring[k], ring[(k + 1) % len(ring)]
            key = tuple(sorted(((round(a[0], 6), round(a[1], 6)),
                                (round(b[0], 6), round(b[1], 6)))))
            if seen[key] != 1:                    # the shared inside edge
                continue
            faces.append((vid(a[0], a[1], z0), vid(b[0], b[1], z0),
                          vid(b[0], b[1], z1), vid(a[0], a[1], z1)))
    return P.mesh(part, mat, verts, faces)


# --- the stock ---------------------------------------------------------------


def _shelf_items(prims, tiles, tag, games, maker, x0, x1, y0, y1, z, clear,
                 role, key, variant):
    """One shelf run's stock, capped by `CAPS`. ``role`` is what this shelf
    sells: ``sealed`` (booster boxes, with tins behind them), ``slabs``
    (graded cards lying flat, which the reference puts on the shelf a
    customer looks DOWN on) or ``piles`` (loose packs heaped up)."""
    n = 0
    span, dep = x1 - x0, y1 - y0
    if span < 0.12 or dep < 0.08:
        return 0
    if role == "slabs":
        if SLAB_L + 0.02 > dep:
            role = "piles"
        else:
            cols = min(CAPS["slabs_per_shelf"], int(span / (SLAB_W + 0.018)))
            pitch = span / max(1, cols)
            for k in range(cols):
                g = games[(k + variant) % len(games)]
                p, lo, hi = _stood(f"DisplayCase_Slab{tag}_{k}", STOCK,
                                   _nudged(x0 + pitch * (k + 0.5), SLAB_W / 2.0, x0, x1,
                                           variant), (y0 + y1) / 2.0, z,
                                   SLAB_W, SLAB_L, SLAB_T)
                prims.append(p)
                tile = f"slab_{g['id']}"
                tiles[tile] = {"kind": "slab", "game": g["id"],
                               "w_m": SLAB_W, "h_m": SLAB_L, "key": key}
                prims.append(_face_up(f"DisplayCase_SlabArt{tag}_{k}", tile,
                                      lo, hi, inset=0.94))
                n += 1
            return n
    if role == "piles":
        cols = min(CAPS["piles_per_shelf"], int(span / (PILE_W + 0.03)))
        pitch = span / max(1, cols)
        for k in range(cols):
            hgt = 0.045 + 0.012 * ((k + variant) % 3)
            if hgt + 0.02 > clear:
                break
            p, _lo, _hi = _stood(f"DisplayCase_Pile{tag}_{k}", STOCK,
                                 _nudged(x0 + pitch * (k + 0.5), PILE_W / 2.0, x0, x1,
                                         variant), (y0 + y1) / 2.0, z,
                                 PILE_W, min(PILE_D, dep * 0.8), hgt)
            prims.append(p)
            n += 1
        return n
    cols = min(CAPS["boxes_per_shelf"], int(span / (BOX_W + 0.014)))
    pitch = span / max(1, cols)
    if BOX_H + 0.02 <= clear and BOX_D + 0.02 <= dep:
        for k in range(cols):
            g = games[(k + variant) % len(games)]
            p, lo, hi = _stood(f"DisplayCase_Box{tag}_{k}", STOCK,
                               _nudged(x0 + pitch * (k + 0.5), BOX_W / 2.0, x0, x1,
                                       variant), y0 + BOX_D / 2.0 + 0.012,
                               z, BOX_W, BOX_D, BOX_H)
            prims.append(p)
            tile = f"box_{g['id']}"
            tiles[tile] = {"kind": "box", "game": g["id"], "maker": maker["id"],
                           "w_m": BOX_W, "h_m": BOX_H, "key": key}
            prims.append(_face_out(f"DisplayCase_BoxArt{tag}_{k}", tile, lo, hi))
            n += 1
    if TIN_H + 0.02 <= clear and TIN_D + 0.01 <= dep - (BOX_D + 0.024):
        tins = min(CAPS["tins_per_shelf"], int(span / (TIN_W + 0.02)))
        tpitch = span / max(1, tins)
        for k in range(tins):
            g = games[(k + variant + 1) % len(games)]
            p, lo, hi = _stood(f"DisplayCase_Tin{tag}_{k}", STOCK,
                               _nudged(x0 + tpitch * (k + 0.5), TIN_W / 2.0, x0, x1,
                                       variant, -1.0), y1 - TIN_D / 2.0 - 0.008,
                               z, TIN_W, TIN_D, TIN_H)
            prims.append(p)
            tile = f"tin_{g['id']}"
            tiles[tile] = {"kind": "tin", "game": g["id"],
                           "w_m": TIN_W, "h_m": TIN_D, "key": key}
            prims.append(_face_up(f"DisplayCase_TinArt{tag}_{k}", tile, lo, hi,
                                  inset=0.90))
            n += 1
    return n


def _register(prims, tag, cx, cy, z):
    """A 1997 register: a body, a keyboard plate, a pole display on a stem.
    PARTS and not stock -- the call `counter` form `bar` made about its taps
    and its till: a register is bolted where the staff stand, and a jittered
    one is not a register. Returned ABOVE the slot, like a monitor on a
    desk, so it does not move the module's fit."""
    body, _lo, hi = _stood(f"DisplayCase_Till{tag}", BODY, cx, cy, z,
                           0.34, 0.36, 0.15, above=True)
    prims.append(body)
    for p in (P.box_c(f"DisplayCase_TillKeys{tag}", STOCK,
                      (cx, cy - 0.10, hi[2] + 0.014), (0.26, 0.12, 0.012)),
              P.box_c(f"DisplayCase_TillStem{tag}", METAL,
                      (cx, cy + 0.12, hi[2] + 0.10), (0.035, 0.035, 0.18)),
              P.box_c(f"DisplayCase_TillHead{tag}", BODY,
                      (cx, cy + 0.12, hi[2] + 0.21), (0.16, 0.05, 0.08))):
        p["above"] = True
        prims.append(p)


# --- one run -----------------------------------------------------------------


def _span(body, face):
    """``(a0, a1)`` -- the face's extent along itself."""
    along, _out, _sgn = _AXES[face]
    return body[along]


def _run(prims, tiles, tag, body, h, top_z0, step, glazed, ends, backs,
         games, maker, key, variant, params, till=None):
    """Build one run of the case. Returns the number of stock items."""
    (bx0, bx1), (by0, by1) = body
    if bx1 - bx0 < 0.25 or by1 - by0 < 0.25:
        return 0
    bay_max = float(params.get("bay_max", 1.20) or 1.20)
    n_shelves = max(1, min(3, int(params.get("shelves", 2))))
    body_top = top_z0 + JOIN + step
    deck_z = KICK_H + 0.008 + step
    deck_top = deck_z + DECK_T
    rail_lo = (KICK_H - 0.006 + step, KICK_H + 0.049 + step)
    rail_hi = (body_top - 0.070, body_top - 0.012)
    items = 0

    prims.append(P.box(f"DisplayCase_Kick_{tag}", BODY,
                       (bx0 + KICK_SET, by0 + KICK_SET, 0.0),
                       (bx1 - KICK_SET, by1 - KICK_SET, KICK_H + step)))
    prims.append(P.box(f"DisplayCase_Deck_{tag}", DECK,
                       (bx0 + IN_DECK, by0 + IN_DECK, deck_z),
                       (bx1 - IN_DECK, by1 - IN_DECK, deck_z + DECK_T)))

    # THE CORNER COLUMN, one per pair of adjacent glazed faces.
    corners = []
    for fa in ("-Y", "+Y"):
        for fb in ("-X", "+X"):
            if fa in glazed and fb in glazed:
                corners.append((fa, fb))
    for ci, (fa, fb) in enumerate(corners):
        _al, oa, sa = _AXES[fa]
        _bl, ob, sb = _AXES[fb]
        ya = body[oa][1] if sa > 0 else body[oa][0]
        xb = body[ob][1] if sb > 0 else body[ob][0]
        # TO THE FLOOR, and PROUD of the rails at the top. A column whose
        # z band ended at the rails' shared that plane over the JOIN they
        # overlap by -- 0.00012 m2 a rail, four rails a corner. A showcase's
        # corner extrusion does run to the floor, and the kick is recessed
        # `KICK_SET` so nothing down there meets it.
        lo, hi = [0.0, 0.0, 0.0], [0.0, 0.0, body_top + 0.002]
        lo[oa], hi[oa] = sorted((ya + sa * CORNER_PROUD,
                                 ya - sa * (CORNER_W - CORNER_PROUD)))
        lo[ob], hi[ob] = sorted((xb + sb * CORNER_PROUD,
                                 xb - sb * (CORNER_W - CORNER_PROUD)))
        prims.append(P.box(f"DisplayCase_Corner_{tag}{ci}", METAL,
                           tuple(lo), tuple(hi)))

    def _trim(face):
        """``(a0, a1)`` for ``face``, pulled back to the corner column where
        the perpendicular face is glazed too."""
        along, _o, _s = _AXES[face]
        a0, a1 = body[along]
        lo_f, hi_f = ("-X", "+X") if along == 0 else ("-Y", "+Y")
        cl, ch = lo_f in glazed, hi_f in glazed
        a0 += (CORNER_W - JOIN) if cl else IN_RAIL
        a1 -= (CORNER_W - JOIN) if ch else IN_RAIL
        return a0, a1, cl, ch

    for face in FACES:
        a0, a1, corner_lo, corner_hi = _trim(face)
        if a1 - a0 < 0.05:
            continue
        if face in ends:
            prims.append(_fbox(f"DisplayCase_End{_TAG[face]}_{tag}", GLASS,
                               face, body, a0, a1, 0.0, PANE_T, deck_top, body_top))
        elif face in backs:
            prims.append(_fbox(f"DisplayCase_Back{_TAG[face]}_{tag}", BODY,
                               face, body, a0 + IN_BACK - IN_RAIL, a1 - IN_BACK + IN_RAIL,
                               0.0, BACK_T, KICK_H + step, body_top))
            dw = (a1 - a0) * 0.54
            for di in (0, 1):
                da0 = a0 if di == 0 else a1 - dw
                prims.append(_fbox(f"DisplayCase_Door{_TAG[face]}_{tag}{di}",
                                   GLASS, face, body, da0, da0 + dw,
                                   BACK_T + 0.006 + di * 0.012,
                                   BACK_T + 0.012 + di * 0.012,
                                   deck_top + 0.02, body_top - 0.03))
        elif face in glazed:
            for rn, (rz0, rz1) in (("Lo", rail_lo), ("Hi", rail_hi)):
                # A rail stops ONE `JOIN` inside a corner column and the
                # pane goes TWO, so their end faces are 4 mm apart in there
                # (at one JOIN each they shared a plane: 9.95e-05 m2 a pair,
                # four a corner). MEASURED the other way round first -- rails
                # at two JOIN and pane at one -- and the two rails then
                # reached past each other's 30 mm depth and met in the corner
                # square, which is a worse pair for the same reason.
                prims.append(_fbox(f"DisplayCase_Rail{rn}{_TAG[face]}_{tag}",
                                   METAL, face, body, a0 - JOIN, a1 + JOIN,
                                   0.0, RAIL_T, rz0, rz1))
            # The pane runs INTO the corner column where there is one, and
            # stops short of an end pane where there is not: extending it at
            # a non-corner end would lay its end face in the end pane's inner
            # face, which is the pair the column fix replaced at the corner.
            prims.append(_fbox(f"DisplayCase_Glass{_TAG[face]}_{tag}", GLASS,
                               face, body,
                               a0 - (2 * JOIN if corner_lo else 0.0),
                               a1 + (2 * JOIN if corner_hi else 0.0),
                               PANE_SET, PANE_SET + PANE_T,
                               rail_lo[1] - 0.010, rail_hi[0] + 0.010))
            # ONE MULLION PER BAY EDGE. Emitting a post at each end of each
            # bay put two boxes on every interior edge -- identical, and
            # `coincident_pairs` reported every one of them (0.10816 m2 a
            # pair on a 1.25 m case, which is a whole mullion). Bays share
            # their edges; the posts are the edges, deduped.
            ia0, ia1 = a0, a1
            mid = (ia0 + ia1) / 2.0
            runs_b = bays(ia1 - ia0, bay_max)
            edges = [mid + runs_b[0][0] - runs_b[0][1] / 2.0] + \
                    [mid + cx + bw / 2.0 for cx, bw in runs_b]
            keep = sorted(set(round(e, 6) for e in edges))
            # AT A CORNER THE COLUMN IS THE MULLION. Keeping the end edge as
            # well put the two glazed faces' first mullions in one square,
            # 0.000128 m2 of shared z face a pair; and a mullion 4 mm behind
            # a column is not a thing a frame has.
            if corner_lo:
                keep = keep[1:]
            if corner_hi:
                keep = keep[:-1]
            for pi, pa in enumerate(keep):
                pa = min(max(pa, ia0 + POST_T / 2.0), ia1 - POST_T / 2.0)
                prims.append(_fbox(
                    f"DisplayCase_Post{_TAG[face]}_{tag}{pi}",
                    METAL, face, body, pa - POST_T / 2.0, pa + POST_T / 2.0,
                    POST_SET, POST_SET + POST_T,
                    rail_lo[1] - JOIN, rail_hi[0] + JOIN))

    # SHELVES and what is on them. The vitrine's inside is the body less
    # whatever each face put there; the widest of those insets is the pane
    # plus its mullion, so one number serves.
    inset = POST_SET + POST_T + 0.012
    ix0, ix1 = bx0 + inset, bx1 - inset
    iy0, iy1 = by0 + inset, by1 - inset
    top_of_case = body_top - 0.075
    if top_of_case - deck_top > 0.18 and ix1 - ix0 > 0.2 and iy1 - iy0 > 0.12:
        pitch = (top_of_case - deck_top) / (n_shelves + 1)
        items += _shelf_items(prims, tiles, f"_{tag}D", games, maker,
                              ix0, ix1, iy0, iy1, deck_top, pitch, "sealed",
                              key, variant)
        for si in range(n_shelves):
            sz = deck_top + pitch * (si + 1)
            prims.append(P.box(f"DisplayCase_Shelf_{tag}{si}", GLASS,
                               (ix0 - 0.006, iy0 - 0.006, sz - SHELF_T),
                               (ix1 + 0.006, iy1 + 0.006, sz)))
            role = "slabs" if si == n_shelves - 1 else ("piles" if si % 2 else "sealed")
            items += _shelf_items(prims, tiles, f"_{tag}{si}", games, maker,
                                  ix0, ix1, iy0, iy1, sz, pitch, role,
                                  key, variant + si)

    # ON TOP: towers of white card-storage boxes.
    run_span = bx1 - bx0
    n_store = min(CAPS["storage_per_run"],
                  max(0, int((run_span - 0.5) / (STORE_W + 0.03))))
    cy = max(by0 + STORE_D / 2.0 + 0.02,
             min((by0 + by1) / 2.0, by1 - STORE_D / 2.0 - 0.02))
    for k in range(n_store):
        cx = bx0 + 0.24 + k * (STORE_W + 0.03)
        if cx + STORE_W / 2.0 > bx1 - 0.10:
            break
        # A TILL IS PLACED FIRST AND A BOX GIVES WAY TO IT, which is the
        # rule `counter` form `bar` wrote for a tap tower standing on a
        # register. MEASURED the other way round: on a 0.9 m case the second
        # storage box and the register shared 0.016 m2 of one plane.
        if till and not (cx + STORE_W / 2.0 < till[0] - 0.04
                         or cx - STORE_W / 2.0 > till[1] + 0.04):
            continue
        for s in range(1 + ((k + variant) % 3 == 0)):
            shrink = s * 0.008
            p, lo, hi = _stood(f"DisplayCase_Store_{tag}{k}_{s}", STOCK,
                               cx, cy, h + s * STORE_H,
                               STORE_W - shrink, STORE_D - shrink, STORE_H,
                               above=True)
            prims.append(p)
            said = (k + s + variant) % len(CB.SHOP_SAYS)
            tile = f"label_{maker['id']}_{said}"
            tiles[tile] = {"kind": "label", "maker": maker["id"],
                           "says": CB.SHOP_SAYS[said],
                           "w_m": STORE_W, "h_m": STORE_H, "key": key}
            prims.append(_face_out(f"DisplayCase_StoreArt_{tag}{k}_{s}", tile,
                                   lo, hi, inset=0.88, above=True))
            items += 1
    return items


# --- the plan ----------------------------------------------------------------


def plan(w, d, h, params=None, variant=0, key="display_case"):
    """Everything the recipe builds.

    ``{"prims": [...], "tiles": {key: spec}, "collision": [...],
       "facts": {...}}``. A prim with ``above`` stands on the counter TOP
    and is returned as a dressing object, so it does not move the module's
    fit bounds -- the rule a monitor on a desk already follows. A prim with
    ``tile`` is an art quad naming one of ``tiles``.
    """
    w, d, h = float(w), float(d), float(h)
    params = params or {}
    variant = int(variant or 0)
    form = pick_form(params.get("form"), w, d, params)
    case_d = _case_depth(params, d)
    games = CB.game_order(key)
    maker = CB.maker_for(key)
    prims, tiles = [], {}
    O = OVERHANG

    if form == "flat":
        case_d = d
        runs = [("M", ((-w / 2 + O, w / 2 - O), (-d / 2 + O, -d / 2 + case_d - O)),
                 0.0, {"-Y"}, {"-X", "+X"}, {"+Y"})]
        rings = [[(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]]
    else:
        right = (variant % 2) == 0
        cx0 = (w / 2 - case_d) if right else (-w / 2)
        cx1 = (w / 2) if right else (-w / 2 + case_d)
        mx0 = -w / 2 if right else cx1
        mx1 = cx0 if right else w / 2
        corner_out = "+X" if right else "-X"
        main_end = "-X" if right else "+X"
        # the corner run is glazed on the front AND the outer end; the main
        # run stops CORNER_GAP short of it and keeps its own far end
        runs = [
            ("M", ((mx0 + O, mx1 - O), (-d / 2 + O, -d / 2 + case_d - O)),
             0.0, {"-Y"}, {main_end}, {"+Y"}),
            ("C", ((cx0 + O, cx1 - O), (-d / 2 + O, d / 2 - O)),
             LEG_STEP, {"-Y", corner_out}, {"+Y"},
             {"-X" if right else "+X"}),
        ]
        # the main run's body stops short of the corner run's body
        (a0, a1), yr = runs[0][1]
        if right:
            a1 = cx0 - CORNER_GAP
        else:
            a0 = cx1 + CORNER_GAP
        runs[0] = (runs[0][0], ((a0, a1), yr)) + runs[0][2:]
        # ONE top over both, split at the corner run's near edge
        # THREE QUADS, NOT TWO, and the third is the whole point. A two-quad
        # L has one ring's short side face lying inside the other's long one
        # over the corner: measured as `Top` against `Top`, OPP, 0.0096 m2 --
        # `TOP_T` times the case depth, the corner joint exactly. Quads only
        # cancel a shared side face when they share the WHOLE edge, so the
        # corner band is its own quad and every internal edge is matched.
        back = -d / 2 + case_d
        cut = cx0 if right else cx1
        near = [(-w / 2, -d / 2), (cut, -d / 2), (cut, back), (-w / 2, back)]
        far = [(cut, -d / 2), (w / 2, -d / 2), (w / 2, back), (cut, back)]
        if right:
            rings = [near, far, [(cx0, back), (w / 2, back), (w / 2, d / 2),
                                 (cx0, d / 2)]]
        else:
            rings = [near, far, [(-w / 2, back), (cx1, back), (cx1, d / 2),
                                 (-w / 2, d / 2)]]

    top_z0 = h - TOP_T
    prims.append(_l_top("DisplayCase_Top", GLASS, rings, top_z0, h))
    main = runs[0][1]
    till_x = min(main[0][1] - 0.25,
                 main[0][0] + (main[0][1] - main[0][0]) * 0.82)
    items = 0
    for tag, body, step, glazed, ends, backs in runs:
        items += _run(prims, tiles, tag, body, h, top_z0, step, glazed, ends,
                      backs, games, maker, key, variant, params,
                      till=(till_x - 0.17, till_x + 0.17) if tag == "M" else None)
    _register(prims, "", till_x, (main[1][0] + main[1][1]) / 2.0, h)

    # COLLISION IS THE TOP'S OWN FOOTPRINT, one box per quad of it, and for
    # an L that is the point: a single box over the slot would wall off the
    # inside of the corner, which is where the staff stand and where Deli
    # Counter's own aisle runs. Each box is the counter from the floor to
    # the glass -- a body is stopped by the case, not by the air beside it.
    collision = [((min(x for x, _y in ring), min(y for _x, y in ring), 0.0),
                  (max(x for x, _y in ring), max(y for _x, y in ring), h))
                 for ring in rings]
    facts = {"form": form, "runs": len(runs), "case_depth_m": round(case_d, 4),
             "shelves": max(1, min(3, int(params.get("shelves", 2)))),
             "items": items, "variant": variant, "tiles": len(tiles),
             "tris": P.tri_count(prims), "maker": maker["id"],
             "colliders": len(collision),
             "games": [g["id"] for g in games[:4]]}
    return {"prims": prims, "tiles": tiles, "collision": collision,
            "facts": facts}


def bounds(got):
    """The plan's extents EXCLUDING what stands on the counter top -- what
    `validate.fit_*` measures on the built module."""
    return P.bounds([p for p in got["prims"] if not p.get("above")])
