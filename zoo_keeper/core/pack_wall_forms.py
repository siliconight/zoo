"""The card shop's pack wall -- a gondola bay of booster displays, planned in
pure Python (no bpy).

Zoo 0.95.0. The reference (`docs/SET_DRESSING_REFERENCES.md`): "The pack
wall: floor-to-ceiling gondola shelving of booster displays in tight rows,
each row a different product, with a coloured header sign over each bay
naming the game. The walker's photo is one long aisle of it. Also pegboard
or slatwall with hanging blister packs and binders."

FRAME AND UNITS: metres, Z up, the slot's box, -Y the aisle, +Y the wall,
base at z = 0, plan centred on x = y = 0.

A BAY IS THE UNIT AND A RUN IS BAYS. `_bays` divides the slot at `bay_max`
(1.20 m, a real gondola bay) and each bay gets its OWN game, its own header
and its own product mix -- so a 6 m aisle authored as one volume is five
different bays rather than one bay five times, and Deli Counter can also
place five 1.2 m slots and get five different bays from `module_variants`.
Both were needed: 579 of the 721 placements `_bays` was written for are
longer than any one unit of their species, and the walker's photo is an
aisle.

THE BACK IS `slatwall`. Pixelcoat 0.44.0 ships `slatwall_retail`, and this
release adds the kind to `skins.KNOWN_KINDS` -- before it, a slot asking for
it built the genome default and said nothing (see `kit.plan_kit`'s UNKNOWN
MATERIAL KIND line, which exists because of it).

ONE PART PER PLANE. The two end uprights own -X, +X, -Y, z = 0 and z = h
between them (they are disjoint in x, so two parts on the -Y plane never
overlap); the back panel owns +Y. Everything else is inboard and buried
`JOIN` into whatever it meets. `tests/test_card_shop.py` runs
`prims.coincident_pairs` at 2.2 mm over the genome's corners and every
variant.

STOCK IS BOXES WITH A TEXTURE, capped by `CAPS` -- see there for the
measurement.

HOW MANY SHELVES A BAY CARRIES IS THE BAY'S OWN HEIGHT, AND THE CAP IS
DERIVED (0.99.0). It was `CAPS["shelves_per_bay"] = 6`, which bound at
every height the genome allows, so raising a bay from 2.2 m to 3.2 m drew
exactly the same triangles -- 1,416 on a 2.4 m bay at both -- and bought
nothing but a wider gap between the same six shelves: a 0.259 pitch became
a 0.401 one over a 0.092 m booster box. `max_rows` derives the cap from
`budgets.tris_per_bay` and `budgets.tris_lod0` instead, and the height
derives the count. See `BAY_BUDGET` for why the per-BAY budget is the one
that binds.
"""
from __future__ import annotations

from . import card_brands as CB
from . import prims as P
from ..recipes._bays import bays

JOIN = 0.004
SINK = 0.003
ART_PROUD = 0.005

#: The gondola frame. An upright is the bay's end post, full height; the
#: base is the deep bottom shelf a real gondola stands towers of boxes on.
UPRIGHT_T = 0.040
#: A slatwall panel is 19 mm MDF plus its aluminium insert. 24 and not 18
#: because the `Y_IN` ladder below has to fit FIVE parts inside it at 4 mm
#: steps and still keep the innermost 4 mm clear of the panel's own face:
#: at 18 mm the peg row and the base shared that face exactly.
BACK_T = 0.024
SHELF_T = 0.022
SHELF_SET = 0.010            # a shelf's front, back from the upright's face
#: EVERY PART GETS ITS OWN INSET, and that is the whole discipline of this
#: module. Two parts inset by the SAME number meet on every plane their other
#: two ranges share, and the probe reports it: measured on a 2.4 m bay, the
#: kick against the base over both x planes and the back y (0.514 m2), the
#: back against every kick over z = 0, the back against every shelf over its
#: own front face, and every shelf against its bay's upright over the
#: upright's inner face -- 28 pairs from four collisions of one number. The
#: ladders below step by `JOIN` and every part is buried at least `JOIN`
#: inside whatever it lands in.
#:
#: From the bay's EDGE, inward (the upright is `UPRIGHT_T` / 2 = 20 mm each
#: side of that edge, so every one of these is inside it):
X_IN = {"kick": 0.004, "base": 0.008, "shelf": 0.012, "header": 0.016}
#: From the slot's BACK plane, forward (the back panel is `BACK_T` = 18 mm
#: deep, so every one of these is inside it):
Y_IN = {"upright": 0.020, "kick": 0.016, "base": 0.012, "shelf": 0.008,
        "peg": 0.004}
BASE_H = 0.140
KICK_SET = 0.040
#: The header sign over the bay: its height, how far it is set back from the
#: uprights' front plane, its thickness, and the gap under the bay top.
HEADER_H = 0.180
HEADER_SET = 0.008
HEADER_T = 0.022
HEADER_DROP = 0.030
#: Shelf pitch: the tallest product plus room to get a hand in. Derived from
#: `BOX_H` rather than chosen, so a bigger box moves the shelves with it.
BOX_W, BOX_H, BOX_D = 0.135, 0.092, 0.072
#: A hanging blister pack: card and bubble. The DEPTH is 30 mm and not
#: 22 because it hangs off the slatwall, whose panel is `BACK_T` = 24 --
#: at 22 the whole pack sat INSIDE the panel and its front face landed
#: 2 mm in front of the panel's, on every peg of every peg row.
PEG_W, PEG_H, PEG_D = 0.078, 0.145, 0.030
#: WHAT ONE ROW NEEDS OF THE BAY'S HEIGHT, and it is measured from the
#: TALLEST thing a row stands, which is the blister pack and not the box.
#: `BOX_H + 0.075` was the whole of it until 0.99.0 and it was 53 mm short
#: of a peg row, which is why the peg row needed a MEASURED-clear escape
#: hatch below: the count said a row fitted and the row did not. The 0.075
#: is the original author's reach-in and is kept as it was written.
SHELF_CLEAR = max(BOX_H, PEG_H) + 0.075
#: ...and the PLANK is part of the pitch. `int(room / SHELF_CLEAR)` never
#: produced a pitch of `SHELF_CLEAR`; it produced `room / (n + 1)`, which is
#: a different number, and the cap hid that at every height in the genome's
#: range. Pitch is derived from this one value now, so the guards below --
#: `BOX_H + 0.020` and `PEG_H + 0.025` -- sit 50 mm under it and no
#: threshold is asked of two spellings of one quantity.
SHELF_PITCH_MIN = SHELF_CLEAR + SHELF_T

GLASS, METAL, BODY, BACK, STOCK, ART = "glass", "metal", "body", "back", "stock", "art"

#: WHAT THE CAPS BUY AND WHICH QUESTION THEY ANSWER, re-measured on
#: 0.99.0's derived shelf count at the genome's largest slot (8.0 x 0.6 x
#: 3.2, seven bays):
#:
#:     these caps          322 items   5,470 tris   766 a bay, 7 shelves
#:     caps lifted to 99   280 items   4,630 tris   646 a bay, 4 shelves
#:
#: against 6,000 for the module and `BAY_BUDGET` for a bay. THEY NO LONGER
#: HOLD THE BUDGET -- `max_rows` does -- and lifting them makes a bay
#: CHEAPER rather than dearer: a wider row costs more, so fewer rows fit
#: the bay budget, and seven shelves of six become four shelves of seven.
#: What these caps decide now is the SHAPE of the spend, and a gondola is
#: read as rows. A bay is 1.2 m and a booster box is 0.135 m, so "as many
#: as fit" is 8 a shelf; 6 leaves the gap a real gondola has where somebody
#: has taken one.
#:
#: At 99 a peg row carries TWELVE against a box row's seven, so the peg row
#: is the DEARER of the two -- which is why `bay_tris` prices the worst of
#: the four variants instead of assuming the pegged row is the cheap one.
#:
#: THE 0.95.0 FIGURES THIS COMMENT CARRIED WERE WRONG, kept here so nobody
#: rediscovers them. It recorded "406 items 5,684 tris" with the caps at 99,
#: "287 items 4,046 tris" with them on, and "578 triangles a bay", all at
#: 8.0 x 0.5 x 2.4. The ITEM count reproduces -- 287 -- and not one of the
#: triangle figures does: 0.98.0 draws 4,896 and 684 a bay at that slot, and
#: 637 items / 10,300 with the caps lifted. 578 travelled: it is in this
#: species' genome note beside the correct 4,896 (a sentence that disagrees
#: with itself, since 4,896 over seven bays is 699), and in Deli Counter's
#: `_PIECES` comment as "578 triangles a bay against 6,000".
CAPS = {
    "boxes_per_shelf": 6,
    "pegs_per_row": 5,
}

#: ONE ROW IN `PEG_EVERY` IS HUNG BLISTER PACKS rather than faced boxes.
#: Read by the planner AND by `bay_tris`, because the cap has to price the
#: mix the planner actually builds -- one quantity, one spelling.
PEG_EVERY = 4

#: WHAT THE PIECES COST, so the caps below are arithmetic rather than
#: taste. `prims.box` is 12 triangles and `_quad` is 2, so a faced product
#: is 14; a shelf plank is one box; a bay's own frame is its kick, its
#: base, its header and the header's art (12 + 12 + 12 + 2); a module
#: carries one slatwall back and one upright per bay edge.
#: `test_card_shop` asserts every one of these against the planner, the way
#: `pennant_row`'s does -- a cap whose arithmetic has gone stale is a
#: comment.
TRIS_ITEM = 14
TRIS_SHELF = 12
TRIS_BAY_FRAME = 38
TRIS_BACK = 12
TRIS_UPRIGHT = 12

#: THE MODULE BUDGET, `budgets.tris_lod0` in the genome. Defaulted here so
#: the planner runs without a kit; `test_card_shop` holds it against the
#: genome so the two cannot drift.
BUDGET = 6000

#: THE BAY BUDGET, `budgets.tris_per_bay`, AND WHY THE MODULE BUDGET IS NOT
#: WHAT HOLDS THIS SPECIES.
#:
#: Every other species in the card shop is placed once or twice. A room
#: stands EIGHT pack walls: Deli Counter 0.140.0's `_PIECES` allows four
#: wall runs (`most` 4, worst palette size 3.6 m, three bays each) and two
#: islands (`most` 2), each of which is `twin` and therefore two modules of
#: 2.4 m, two bays each. Twenty bays in one room. 6,000 a module never
#: binds on any of them -- at 3.6 m it would pay for nineteen shelves a bay
#: -- so a cap derived from it alone would be a cap that cannot fire, which
#: is indistinguishable from no cap at all.
#:
#: The room is what binds, and its budget is Deli Counter's
#: `_CARD_SHOP_ROOM_TRIS` = 24,000, which is one `cubicle_bank` -- the
#: figure this changelog offered for scale in 0.95.0. The rest of that
#: room's worst case is 8,192 (two display cases 2 x 1,148, two returns
#: 2 x 760, four pennant rows 4 x 892, two CRTs 2 x 404), and the eight
#: gondola modules carry 432 of frame between them (4 x (12 + 4 x 12) for
#: the 3.6 m runs, 4 x (12 + 3 x 12) for the islands). So:
#:
#:     24,000 - 8,192 - 432 = 15,376, over twenty bays = 768 a bay
#:
#: MEASURED, not asserted: at 768 a bay carries seven shelves and draws
#: 766; an eighth costs 862 and puts the room at 25,864. Seven puts it at
#: 23,944 of 24,000. The expensive version -- pitch held at
#: `SHELF_PITCH_MIN` at every height, which is ten shelves at 3.2 m -- is
#: 1,054 a bay and 30,008 a room, 125 % of the budget. What the room cannot
#: afford is written into the release entry rather than quietly dropped.
#:
#: This is the one dial. Raising `budgets.tris_per_bay` makes a gondola
#: denser and nothing else has to move with it.
BAY_BUDGET = 768


def bay_tris(rows, cols_box, cols_peg, variant=None):
    """What ONE bay draws with `rows` product rows, and therefore
    ``rows - 1`` shelves -- the bottom row stands on the base and needs no
    plank under it.

    `variant` None prices the WORST of the four, which is what a cap has to
    use: the peg row's phase moves with the variant, and a bay whose rows
    do not divide by `PEG_EVERY` carries one more cheap row in some phases
    than in others.
    """
    def items(v):
        peg = sum(1 for si in range(rows) if (si + v) % PEG_EVERY == 3)
        return peg * cols_peg + (rows - peg) * cols_box

    n = (max(items(v) for v in range(PEG_EVERY)) if variant is None
         else items(int(variant)))
    return TRIS_BAY_FRAME + (rows - 1) * TRIS_SHELF + n * TRIS_ITEM


def module_tris(rows, n_bays, cols_box, cols_peg, variant=None):
    """What the whole module draws: the slatwall back, an upright per bay
    edge, and `n_bays` bays of `bay_tris`."""
    return (TRIS_BACK + TRIS_UPRIGHT * (n_bays + 1)
            + n_bays * bay_tris(rows, cols_box, cols_peg, variant))


def max_rows(n_bays, cols_box, cols_peg, budget=BUDGET, bay_budget=BAY_BUDGET):
    """THE CAP, DERIVED: the most product rows a bay can carry with BOTH
    budgets still met -- the bay's own and the module's.

    Replaces a hand-set ``CAPS["shelves_per_bay"] = 6``, which bound at
    every height in the genome's range (2.2 to 3.2) and therefore made
    height buy nothing: a 2.4 m bay measured 1,416 triangles at 2.2 m and
    1,416 at 3.2 m, and the only thing a taller bay did was re-space the
    same six shelves from a 0.259 pitch to a 0.401 one over 0.092 m boxes.
    """
    rows = 1
    while rows < 256:
        nxt = rows + 1
        if bay_tris(nxt, cols_box, cols_peg) > int(bay_budget):
            break
        if module_tris(nxt, n_bays, cols_box, cols_peg) > int(budget):
            break
        rows = nxt
    return rows


def _quad(part, tile, verts):
    p = P.mesh(part, ART, verts, [(0, 1, 2, 3)])
    p["tile"] = tile
    p["uvs"] = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))]
    return p


def _faced(prims, tiles, part, tile, spec, cx, y_front, z0, sx, sy, sz, mat=STOCK):
    """A product faced out on a shelf: a box sunk `SINK` into the shelf with
    its art `ART_PROUD` in front of its own measured face."""
    lo = (cx - sx / 2.0, y_front, z0 - SINK)
    hi = (cx + sx / 2.0, y_front + sy, z0 + sz)
    prims.append(P.box(part, mat, lo, hi))
    tiles[tile] = spec
    y = lo[1] - ART_PROUD
    w, hgt = sx * 0.93, (hi[2] - lo[2]) * 0.93
    cz = (lo[2] + hi[2]) / 2.0
    prims.append(_quad(part + "Art", tile,
                       [(cx - w / 2, y, cz - hgt / 2), (cx + w / 2, y, cz - hgt / 2),
                        (cx + w / 2, y, cz + hgt / 2), (cx - w / 2, y, cz + hgt / 2)]))


def plan(w, d, h, params=None, variant=0, key="pack_wall",
         budget=BUDGET, bay_budget=BAY_BUDGET):
    """Everything the recipe builds: ``{"prims", "tiles", "collision",
    "facts"}``."""
    w, d, h = float(w), float(d), float(h)
    params = params or {}
    variant = int(variant or 0)
    bay_max = float(params.get("bay_max", 1.20) or 1.20)
    games = CB.game_order(key)
    maker = CB.maker_for(key)
    prims, tiles = [], {}
    x0, x1 = -w / 2.0, w / 2.0
    y0, y1 = -d / 2.0, d / 2.0
    runs = bays(w, bay_max)
    items = 0
    # THE CAP, BEFORE THE LOOP, because it is the module's as well as the
    # bay's. `bays` divides a run into EQUAL bays, so every bay takes the
    # same columns and the same cap -- if that ever stops being true this
    # has to move inside the loop.
    ax_w = runs[0][1] - 2 * X_IN["shelf"]
    cols_box = min(CAPS["boxes_per_shelf"], int(ax_w / (BOX_W + 0.010)))
    cols_peg = min(CAPS["pegs_per_row"], int(ax_w / (PEG_W + 0.012)))
    cap_rows = max_rows(len(runs), cols_box, cols_peg, budget, bay_budget)
    rows = n_shelf = 0
    pitch = 0.0

    # THE BACK -- slatwall, owning +Y. It stops short of z = 0 and z = h,
    # which are the uprights'.
    prims.append(P.box("PackWall_Back", BACK,
                       (x0 + UPRIGHT_T - JOIN, y1 - BACK_T, 0.004),
                       (x1 - UPRIGHT_T + JOIN, y1, h - 0.004)))
    # THE UPRIGHTS -- one per bay edge. The two OUTER ones own -X, +X, -Y,
    # z = 0 and z = h; the inner ones are the same section, inboard.
    edges = [runs[0][0] - runs[0][1] / 2.0] + [cx + bw / 2.0 for cx, bw in runs]
    edges = sorted(set(round(e, 6) for e in edges))
    for ei, ex in enumerate(edges):
        ex = min(max(ex, x0 + UPRIGHT_T / 2.0), x1 - UPRIGHT_T / 2.0)
        prims.append(P.box(f"PackWall_Upright{ei}", METAL,
                           (ex - UPRIGHT_T / 2.0, y0, 0.0),
                           (ex + UPRIGHT_T / 2.0, y1 - Y_IN["upright"], h)))

    for bi, (cx, bw) in enumerate(runs):
        g = games[(bi + variant) % len(games)]
        e0, e1 = cx - bw / 2.0, cx + bw / 2.0
        if bw - 2 * X_IN["header"] < 0.25:
            continue
        fy = y0 + SHELF_SET                       # a shelf's front plane
        if y1 - Y_IN["shelf"] - fy < 0.10:
            continue

        def bx(part):
            return e0 + X_IN[part], e1 - X_IN[part]

        def byk(part):
            return y1 - Y_IN[part]

        kx0, kx1 = bx("kick")
        prims.append(P.box(f"PackWall_Kick{bi}", BODY,
                           (kx0, fy + KICK_SET, 0.008),
                           (kx1, byk("kick"), BASE_H - 0.030 + JOIN)))
        sx0, sx1 = bx("base")
        prims.append(P.box(f"PackWall_Base{bi}", BODY,
                           (sx0, fy, BASE_H - 0.030), (sx1, byk("base"), BASE_H)))
        # HEADER -- a coloured sign over the bay, with the game's name on it
        hx0, hx1 = bx("header")
        hz1 = h - HEADER_DROP
        hz0 = hz1 - HEADER_H
        prims.append(P.box(f"PackWall_Header{bi}", BODY,
                           (hx0, y0 + HEADER_SET, hz0),
                           (hx1, y0 + HEADER_SET + HEADER_T, hz1)))
        tile = f"header_{g['id']}"
        tiles[tile] = {"kind": "header", "game": g["id"],
                       "w_m": hx1 - hx0, "h_m": HEADER_H, "key": key}
        hy = y0 + HEADER_SET - ART_PROUD
        prims.append(_quad(f"PackWall_HeaderArt{bi}", tile,
                           [(hx0 + 0.006, hy, hz0 + 0.006),
                            (hx1 - 0.006, hy, hz0 + 0.006),
                            (hx1 - 0.006, hy, hz1 - 0.006),
                            (hx0 + 0.006, hy, hz1 - 0.006)]))
        # SHELVES, from the base up to the header
        ax0, ax1 = bx("shelf")
        aby = byk("shelf")
        room = hz0 - 0.040 - BASE_H
        # HOW MANY ROWS THE BAY'S OWN HEIGHT TAKES, then the budgets. The
        # first term is what the reference asks for ("product goes to the
        # ceiling, not to waist height"); the second is what a room with
        # twenty of these bays in it can pay for. `rows` rows means
        # `rows - 1` shelves: the bottom row stands on the base.
        rows = max(1, min(int(room / SHELF_PITCH_MIN), cap_rows))
        n_shelf = rows - 1
        pitch = room / rows
        clear = pitch - SHELF_T
        for si in range(rows):
            z = BASE_H + pitch * si
            if si:
                prims.append(P.box(f"PackWall_Shelf{bi}_{si}", METAL,
                                   (ax0, fy + 0.002, z - SHELF_T), (ax1, aby, z)))
            # WHICH ROW SELLS WHAT. Every row a different product, as the
            # reference has it: boosters faced out on most rows and one row
            # of blister packs against the slatwall. A row is drawn only
            # where the MEASURED clear takes the product -- without that
            # check the peg row ran its tops into the shelf above, 2.14 mm,
            # on every bay narrow enough to pitch its shelves tight.
            gg = games[(bi + variant + si) % len(games)]
            if ((si + variant) % PEG_EVERY == 3 and PEG_D + 0.02 < aby - fy
                    and PEG_H + 0.025 < clear):
                cols = cols_peg
                pp = (ax1 - ax0) / max(1, cols)
                for k in range(cols):
                    t = f"box_{gg['id']}"
                    _faced(prims, tiles, f"PackWall_Peg{bi}_{si}_{k}", t,
                           {"kind": "box", "game": gg["id"], "maker": maker["id"],
                            "w_m": PEG_W, "h_m": PEG_H, "key": key},
                           ax0 + pp * (k + 0.5), byk("peg") - PEG_D,
                           z, PEG_W, PEG_D, PEG_H)
                    items += 1
                continue
            if BOX_H + 0.02 > clear or BOX_D + 0.02 > aby - fy:
                continue
            cols = cols_box
            pp = (ax1 - ax0) / max(1, cols)
            for k in range(cols):
                t = f"box_{gg['id']}"
                _faced(prims, tiles, f"PackWall_Box{bi}_{si}_{k}", t,
                       {"kind": "box", "game": gg["id"], "maker": maker["id"],
                        "w_m": BOX_W, "h_m": BOX_H, "key": key},
                       ax0 + pp * (k + 0.5), fy + 0.016, z, BOX_W, BOX_D, BOX_H)
                items += 1

    facts = {"bays": len(runs), "items": items, "variant": variant,
             "tiles": len(tiles), "tris": P.tri_count(prims),
             "per_bay_tris": round(P.tri_count(prims) / max(1, len(runs))),
             "shelves_per_bay": n_shelf, "rows_per_bay": rows,
             "cap_rows": cap_rows, "pitch_m": round(pitch, 4),
             "bay_budget": int(bay_budget), "budget": int(budget),
             "games": [games[(b + variant) % len(games)]["id"]
                       for b in range(len(runs))]}
    return {"prims": prims, "tiles": tiles,
            "collision": [((x0, y0, 0.0), (x1, y1, h))], "facts": facts}


def bounds(got):
    return P.bounds(got["prims"])
