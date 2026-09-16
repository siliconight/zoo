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
SHELF_CLEAR = BOX_H + 0.075

GLASS, METAL, BODY, BACK, STOCK, ART = "glass", "metal", "body", "back", "stock", "art"

#: WHAT THE CAPS BUY, measured at the genome's largest slot (8.0 x 0.5 x
#: 2.4, seven bays) rather than asserted:
#:
#:     caps lifted to 99        406 items    5,684 tris
#:     these caps               287 items    4,046 tris
#:
#: against a budget of 6,000 for the module. A bay is 1.2 m and a booster
#: box is 0.135 m, so "as many as fit" is 8 a shelf; 6 leaves the gap a real
#: gondola has where somebody has taken one. The per-bay figure is the one
#: to compare with the other species: 578 triangles.
CAPS = {
    "boxes_per_shelf": 6,
    "pegs_per_row": 5,
    "shelves_per_bay": 6,
}


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


def plan(w, d, h, params=None, variant=0, key="pack_wall"):
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
        n_shelf = min(CAPS["shelves_per_bay"], int(room / SHELF_CLEAR))
        pitch = room / max(1, n_shelf + 1)
        clear = pitch - SHELF_T
        for si in range(n_shelf + 1):
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
            if ((si + variant) % 4 == 3 and PEG_D + 0.02 < aby - fy
                    and PEG_H + 0.025 < clear):
                cols = min(CAPS["pegs_per_row"], int((ax1 - ax0) / (PEG_W + 0.012)))
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
            cols = min(CAPS["boxes_per_shelf"], int((ax1 - ax0) / (BOX_W + 0.010)))
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
             "games": [games[(b + variant) % len(games)]["id"]
                       for b in range(len(runs))]}
    return {"prims": prims, "tiles": tiles,
            "collision": [((x0, y0, 0.0), (x1, y1, h))], "facts": facts}


def bounds(got):
    return P.bounds(got["prims"])
