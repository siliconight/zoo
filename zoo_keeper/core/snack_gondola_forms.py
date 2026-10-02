"""The convenience store's snack gondola, decided in pure Python: the island
of shelving, the end caps, every chip bag on it, and every pixel of their
fronts.

Zoo 1.13.0, species `snack_gondola`. Asked for by name, 2026-09-28: "do the
snack gondolas next". The reference (docs/SET_DRESSING_REFERENCES.md, the
walker's convenience store references): "gondola shelving, four or five
shelves of chip bags faced out, end caps stacked with more chips".

WHERE IT STANDS. Deli Counter's store aisles -- `gondola_aisle_N` in
gas_station_a02 and fuel_stop_heist, and from 0.150.0 the gas-station
family's `aisle_N` and the storefront stores' `aisle_shelf_N`, renamed --
which until this species built as plain boxes (or, for `aisle_shelf`, bare
`shelving` with nothing on it). An island: both long faces are shopped.

WHAT IS BUILT, in the recipe frame (metres, Z up, floor 0, CENTRE pivot,
x along the aisle, both +Y and -Y shopped):

  * a dark KICK the length of the run; a pegboard SPINE up the middle; a
    steel UPRIGHT at every bay joint and an END PANEL at each end; a TOP RAIL;
  * per side and per bay, SHELVES up the height, each with a white PRICE
    STRIP on its front edge;
  * CHIP BAGS on every shelf, faced out: each a real bag -- pinched flat at
    its top and bottom seals and puffed between them (`bag`) -- its front
    printed from
    one image (`bag_art`), the rest of it its brand's colour from the same
    image;
  * END CAPS at both ends when the run is long enough: three shelves facing
    out along the aisle, stacked with more bags.

REAL STRUCTURE, NOT A PRINTED CARD. The walker's standing preference: a bag
is a bag-shaped solid with its print on it, not a picture of a row of bags
on a flat panel. It costs 28 triangles a bag (1.42.0; the pillow it
replaced was 22).

MORE THAN CHIPS (1.40.0). The walker's 90s snack references: "fruit snacks,
lunch kits, snack cakes on shelves, candy". The -Y face stays the chip aisle;
the +Y face is SECTIONS, a bay each: YUMMYJAWNS snack cakes (flat cartons, one
flavour a shelf -- stripes of colour), fruit snacks, lunch kits (upright
boxes) and bagged candy. A carton is a 12-triangle box with its front on its
tile; every product is on the bags' one image. A lunch kit belongs in a
cooler and stands here anyway: the cooler's doors are a different species
and the walker asked to see them on the shelves.

TWO SUBMISSIONS WHATEVER THE LENGTH: the steel (every structural part and
the price strips, colour in the `Wear` vertex colour) and the bags (one
painted image).

The +Y side is the -Y side turned half round about the centre, and the +X
end cap the -X one, so both faces read the right way round.
"""
from __future__ import annotations

import math
import re
import zlib

from . import candy_brands as CB
from . import pixel_type as pt
from . import prims as P
from . import snack_brands as SB
from .vending_forms import Canvas

#: Deli Counter's volumes (long side first), then the genome's range.
DC_SIZES = ((6.0, 1.0, 1.6), (10.0, 0.9, 1.8), (7.0, 0.7, 1.6))
RANGES = {"width": (1.2, 14.0), "depth": (0.6, 1.5), "height": (1.2, 2.2)}

BURY = 0.004
KICK_H = 0.10
SPINE_T = 0.03
UPRIGHT_W = 0.04
TOP_RAIL_H = 0.04
BAY_MAX = 1.22
SHELF_T = 0.022
SHELF_PITCH_MIN = 0.32    # a shelf's height to the next: a bag and a hand
STRIP_T = 0.012
STRIP_H = 0.030
ENDCAP_D = 0.32           # an end cap's depth along the aisle
ENDCAP_MIN_W = 2.2        # shorter runs have no end caps
BAG_W = 0.19
BAG_D = 0.07
BAG_GAP = 0.02
BAG_CROWN = 0.03          # the puff of a bag's front
#: A BAG'S SHAPE (1.42.0), from the walker's tutorials: the top and bottom
#: rows of the sheet are pinned and stay flat -- the seals -- and pressure
#: fills what is between. The seal's edge is this thick; the belly runs
#: between these fractions of the bag's height, at this fraction of its
#: width (a filled bag draws in at the waist).
SEAL_T = 0.008
BELLY = (0.30, 0.70)
BELLY_W = 0.94

#: WHAT A BAY OF THE SECTIONED FACE SELLS (1.40.0), cycled along the run.
SECTIONS = ("cake", "fruit", "kit", "candy")
#: kind: (width, height, depth, gap, facings a product, form). Zero facings
#: is one product the whole shelf: a YUMMYJAWNS flavour is a stripe.
STOCK = {
    "chips": (BAG_W, 0.30, BAG_D, BAG_GAP, 2, "bag"),
    "cake": (0.20, 0.16, 0.06, 0.012, 0, "box"),
    "fruit": (0.135, 0.18, 0.05, 0.012, 3, "box"),
    "kit": (0.135, 0.18, 0.04, 0.012, 3, "box"),
    "candy": (0.125, 0.17, 0.05, 0.016, 2, "bag"),
}
CANDY_CROWN = 0.02

MATERIALS = {
    "steel": ((0.72, 0.73, 0.74), "metal_painted"),
    "kick": ((0.10, 0.10, 0.11), "metal_painted"),
    "board": ((0.84, 0.83, 0.80), "metal_painted"),
    "strip": ((0.93, 0.93, 0.90), "metal_painted"),
}
KIND_BASE = {"metal_painted": (1.0, 1.0, 1.0)}
_VARIANT = re.compile(r"_n\d+(?=_|$)")


def vertex_tint(mat_key):
    rgb, kind = MATERIALS[mat_key]
    return kind, tuple(c / b for c, b in zip(rgb, KIND_BASE[kind]))


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def resolve(plan_):
    params = plan_.get("params") or {}
    module = plan_.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    key = _VARIANT.sub("", module.get("stem") or "") or "snack_gondola"
    return key, variant


def shelf_levels(h):
    """z of each shelf's top, the kick's deck first, up to where a bag no
    longer fits under the top rail."""
    top = h - TOP_RAIL_H - 0.02
    n = max(2, int((top - KICK_H) // SHELF_PITCH_MIN))
    pitch = (top - KICK_H) / n
    return [KICK_H + k * pitch for k in range(n)], pitch


def bag(x, y_front, z0, bw, bh, brand, depth=BAG_D, crown=BAG_CROWN):
    """One bag, its front toward -Y at ``y_front``, standing on ``z0``
    (buried `BURY`), centred on ``x``; ``depth + crown`` is its thickness at
    the belly.

    FOUR RINGS UP ITS HEIGHT, lofted: the bottom seal's edge (`SEAL_T`
    thick, full width), the belly's foot and head (full thickness,
    `BELLY_W` of the width), the top seal's edge. Pinched at the seals and
    fat between, front and back alike -- the walker's tutorials, without
    the simulation. Fourteen planar quads: the bottom cap, three toward -Y
    (``front``: shoulder, belly, shoulder), three to each other side, the
    top cap. ``uvs`` put the front on the brand's tile by x and z and every
    other face on the brand's colour block."""
    thick = depth + crown
    yc = y_front + thick / 2.0
    zb = z0 - BURY
    rings = ((0.0, 1.0, SEAL_T), (BELLY[0], BELLY_W, thick), (BELLY[1], BELLY_W, thick),
             (1.0, 1.0, SEAL_T))
    verts = []
    for f, wk, t in rings:
        hw = bw * wk / 2.0
        z = zb + bh * f
        verts += [(x - hw, yc - t / 2.0, z), (x + hw, yc - t / 2.0, z),
                  (x + hw, yc + t / 2.0, z), (x - hw, yc + t / 2.0, z)]
    faces = [(0, 3, 2, 1)]                                    # the bottom cap
    spans = [(4 * i, 4 * i + 4) for i in range(len(rings) - 1)]
    faces += [(a, a + 1, b + 1, b) for a, b in spans]         # the front, -Y
    faces += [(a + 1, a + 2, b + 2, b + 1) for a, b in spans]     # +X
    faces += [(a + 2, a + 3, b + 3, b + 2) for a, b in spans]     # the back, +Y
    faces += [(a + 3, a, b, b + 3) for a, b in spans]             # -X
    top = 4 * (len(rings) - 1)
    faces.append((top, top + 1, top + 2, top + 3))            # the top cap
    p = P.mesh("Snack_Bag", "bag", verts, faces)
    front = tuple(range(1, 1 + len(spans)))
    x0, x1 = x - bw / 2.0, x + bw / 2.0
    uvs = []
    for k, f in enumerate(p["faces"]):
        if k in front:
            # clamped: a ring's own corner is the tile's edge to a rounding
            uvs.append(tuple(("tile_" + brand,
                              min(1.0, max(0.0, (p["verts"][i][0] - x0) / (x1 - x0))),
                              min(1.0, max(0.0, (p["verts"][i][2] - zb) / bh))) for i in f))
        else:
            uvs.append(tuple(("solid_" + brand,) for _ in f))
    p["uvs"] = uvs
    p["front"] = front
    return p


def carton(x, y_front, z0, bw, bh, bd, brand):
    """One carton (1.40.0): a box standing on ``z0`` (buried `BURY`), its
    front toward -Y at ``y_front``, centred on ``x``. `prims.box`'s face 2
    is its -Y face, corners (0, 1, 5, 4): the tile's bottom-left, bottom-
    right, top-right, top-left. Every other face is the brand's colour."""
    p = P.box("Snack_Bag", "bag", (x - bw / 2.0, y_front, z0 - BURY),
              (x + bw / 2.0, y_front + bd, z0 - BURY + bh))
    t = "tile_" + brand
    uvs = []
    for k, f in enumerate(p["faces"]):
        if k == 2:
            uvs.append(((t, 0.0, 0.0), (t, 1.0, 0.0), (t, 1.0, 1.0), (t, 0.0, 1.0)))
        else:
            uvs.append(tuple(("solid_" + brand,) for _ in f))
    p["uvs"] = uvs
    p["front"] = (2,)
    return p


def section(key, variant, face, bi):
    """What bay ``bi`` of ``face`` sells: face "a" is the chip aisle, face
    "b" cycles `SECTIONS` from a start the gondola's own name picks."""
    if face == "a":
        return "chips"
    return SECTIONS[(_h(key, variant, "section") + bi) % len(SECTIONS)]


def product(kind, key, variant, face, bi, k, i):
    """The product at facing ``i`` of shelf ``k``. Chips keep 1.13.0's
    formula exactly, so the chip aisle is the one that shipped."""
    if kind == "chips":
        return SB.IDS[(_h(key, variant, face, bi, k) + i // 2) % len(SB.IDS)]
    if kind == "candy":
        return CB.IDS[(_h(key, variant, face, bi, k) + i // 2) % len(CB.IDS)]
    ids = SB.BOXED_IDS[kind]
    facings = STOCK[kind][4]
    return ids[(_h(key, variant, face, bi) + k + (i // facings if facings else 0)) % len(ids)]


def _side(xs0, xs1, bays_, h, d, key, variant, face):
    """One shelved face of the run (the -Y one), over x ``xs0..xs1``."""
    out, n_bags, stock = [], 0, {}
    levels, pitch = shelf_levels(h)
    y_front = -d / 2.0 + 0.02                         # the shelves' front edge
    y_back = -SPINE_T / 2.0 + BURY                    # buried into the spine
    for bi, (bx, bw) in enumerate(bays_):
        sx0, sx1 = bx - bw / 2.0 + UPRIGHT_W / 2.0 + 0.004, bx + bw / 2.0 - UPRIGHT_W / 2.0 - 0.004
        kind = section(key, variant, face, bi)
        iw, ih, idp, gap, _facings, form = STOCK[kind]
        bh = min(ih, pitch - SHELF_T - 0.06)
        for k, z in enumerate(levels):
            if k:        # the deck is the kick's top
                out.append(P.box("Snack_Shelf", "steel", (sx0, y_front, z - SHELF_T), (sx1, y_back, z)))
            out.append(P.box("Snack_Strip", "strip", (sx0 + 0.003, y_front - STRIP_T, z - STRIP_H + 0.004),
                             (sx1 - 0.003, y_front + BURY, z + 0.006)))
            n = max(1, int((sx1 - sx0 - 0.02) // (iw + gap)))
            span = n * iw + (n - 1) * gap
            bx0 = (sx0 + sx1) / 2.0 - span / 2.0 + iw / 2.0
            for i in range(n):
                brand = product(kind, key, variant, face, bi, k, i)
                x = bx0 + i * (iw + gap)
                if form == "box":
                    out.append(carton(x, y_front + 0.014, z, iw, bh, idp, brand))
                elif kind == "candy":
                    out.append(bag(x, y_front + 0.014, z, iw, bh, brand, idp, CANDY_CROWN))
                else:
                    # a pair of facings a brand, as a real shelf is stocked
                    out.append(bag(x, y_front + 0.014, z, iw, bh, brand))
                n_bags += 1
                stock[kind] = stock.get(kind, 0) + 1
    return out, n_bags, stock


def layout(w, d, h, key="snack_gondola", variant=0):
    """Every part at slot (w, d, h): ``(prims, facts)``."""
    out = []
    caps = w >= ENDCAP_MIN_W
    L = w - 2.0 * ENDCAP_D if caps else w
    xa, xb = -L / 2.0, L / 2.0
    bays_ = [(xa + (L / math.ceil(L / BAY_MAX - 1e-9)) * (i + 0.5), L / math.ceil(L / BAY_MAX - 1e-9))
             for i in range(int(math.ceil(L / BAY_MAX - 1e-9)))]
    # --- the frame ------------------------------------------------------------------
    # EACH PART BURIES INTO THE END PANELS AT ITS OWN DEPTH, 4 mm or more from
    # every neighbour: the panels are the run's first and last 20 mm; the top
    # rail stops 4 mm in, the kick 6 (and 4 mm off the floor -- the panels own
    # z = 0), the spine 12, an end cap's back plate 16. The first cut ran them
    # to the panels' faces and to each other's in a 12 mm panel: 3-6
    # coincident pairs a build.
    out.append(P.box("Snack_Kick", "kick", (xa + 0.006, -d / 2.0 + 0.02, 0.004),
                     (xb - 0.006, d / 2.0 - 0.02, KICK_H)))
    out.append(P.box("Snack_Spine", "board", (xa + 0.012, -SPINE_T / 2.0, KICK_H - BURY),
                     (xb - 0.012, SPINE_T / 2.0, h - TOP_RAIL_H + BURY)))
    # the top rail 6 mm under the end panels' tops, which own z = h
    out.append(P.box("Snack_Frame", "steel", (xa + 0.004, -SPINE_T / 2.0 - 0.006, h - TOP_RAIL_H),
                     (xb - 0.004, SPINE_T / 2.0 + 0.006, h - 0.006)))
    for j in range(1, len(bays_)):
        ux = xa + j * bays_[0][1]
        # 12 mm past the spine's ends and 6 mm proud of the top rail's faces
        out.append(P.box("Snack_Frame", "steel", (ux - UPRIGHT_W / 2.0, -SPINE_T / 2.0 - 0.012, KICK_H - 0.012),
                         (ux + UPRIGHT_W / 2.0, SPINE_T / 2.0 + 0.012, h - TOP_RAIL_H + 0.012)))
    # the end panels, full depth, at each end of the run
    for s in (-1, 1):
        ex0, ex1 = sorted((s * L / 2.0, s * (L / 2.0 - 0.020)))
        out.append(P.box("Snack_Frame", "steel", (ex0, -d / 2.0, 0.0), (ex1, d / 2.0, h)))
    # --- both faces: build -Y, turn it half round for +Y ----------------------------------
    side, n_bags, stock = _side(xa, xb, bays_, h, d, key, variant, "a")
    other, n_b, stock_b = _side(xa, xb, bays_, h, d, key, variant, "b")
    out += side + [P.rotate_z(p, math.pi, about=(0.0, 0.0)) for p in other]
    n_bags += n_b
    for kind, n in stock_b.items():
        stock[kind] = stock.get(kind, 0) + n
    # --- the end caps: three shelves out along the aisle, at each end -----------------------
    if caps:
        for s in (-1, 1):
            cap = []
            ex = -w / 2.0                                   # built at -X, facing -X
            # its back plate's face 4 mm into the end panel (the first cut had
            # it 8 mm OUTSIDE the panel); kick and shelves stop 10 mm inside it
            ct = -L / 2.0 + 0.016
            ce = -L / 2.0 - 0.004            # the cap's kick and shelves end, inside its back plate
            cap.append(P.box("Snack_Kick", "kick", (ex + 0.02, -d / 2.0 + 0.04, 0.0),
                             (ce, d / 2.0 - 0.04, KICK_H)))
            levels, pitch = shelf_levels(h * 0.75)
            bh = min(0.30, pitch - SHELF_T - 0.06)
            ys0, ys1 = -d / 2.0 + 0.05, d / 2.0 - 0.05
            for k, z in enumerate(levels):
                if k:
                    cap.append(P.box("Snack_Shelf", "steel", (ex + 0.02, ys0, z - SHELF_T), (ce, ys1, z)))
                # the price strips are the cap's front-most part and reach the
                # slot's end exactly, so the module fills its slot
                cap.append(P.box("Snack_Strip", "strip", (ex, ys0 + 0.003, z - STRIP_H + 0.004),
                                 (ex + 0.02 + BURY, ys1 - 0.003, z + 0.006)))
                n = max(1, int((ys1 - ys0 - 0.02) // (BAG_W + BAG_GAP)))
                span = n * BAG_W + (n - 1) * BAG_GAP
                for i in range(n):
                    brand = SB.IDS[(_h(key, variant, "cap", s, k) + i // 2) % len(SB.IDS)]
                    # built facing -Y at the origin, then turned to face -X
                    b = bag(0.0, 0.0, z, BAG_W, bh, brand)
                    b = P.rotate_z(b, -math.pi / 2.0, about=(0.0, 0.0))
                    by = ys0 + (ys1 - ys0 - span) / 2.0 + BAG_W / 2.0 + i * (BAG_W + BAG_GAP)
                    cap.append(P.translate(b, (ex + 0.02 + 0.014, by, 0.0)))
                    n_bags += 1
                    stock["chips"] = stock.get("chips", 0) + 1
            # the cap's upright back, full height of its shelves, against the end panel
            # its bottom 12 mm into the kick: at the spine's 4 mm the two shared it
            cap.append(P.box("Snack_Frame", "steel", (ct - 0.03, ys0 - 0.02, KICK_H - 0.012),
                             (ct, ys1 + 0.02, levels[-1] + 0.10)))
            out += cap if s < 0 else [P.rotate_z(p, math.pi, about=(0.0, 0.0)) for p in cap]
    facts = {"bays": len(bays_), "bay_width": bays_[0][1], "end_caps": caps, "bags": n_bags,
             "shelves": len(shelf_levels(h)[0]), "run": L, "stock": stock,
             "collision": ((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h))}
    return out, facts


def plan(w, d, h, key="snack_gondola", variant=0):
    prims, facts = layout(w, d, h, key, variant)
    return {"prims": prims, "facts": facts}


def signed_volume(p):
    vs = p["verts"]
    tot = 0.0
    for f in p["faces"]:
        a = vs[f[0]]
        for k in range(1, len(f) - 1):
            b, c = vs[f[k]], vs[f[k + 1]]
            tot += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return tot / 6.0


# --- the bags' fronts ---------------------------------------------------------------------

TILE = (40, 60)          # a bag's front, pixels
COLS = 6
CARTON_TILE = (48, 38)   # a YUMMYJAWNS carton's front: 0.20 x 0.16 m
SMALL_TILE = (36, 48)    # a fruit-snack box, a lunch kit, a candy bag
SMALL_COLS = 6
CREAM = (250, 244, 228)
MARK_RED = (200, 30, 40)


def _set(c, text, x0, y, tw, ink, plate=None):
    """``text`` in m5x7, centred on a tile ``tw`` wide whose left edge is
    ``x0``, its top at ``y``. A word wider than the tile is a defect, not a
    crop: it raises."""
    m = pt.trim(pt.render(text, 1, "m5x7"))
    assert len(m[0]) <= tw - 2, (text, len(m[0]), tw)
    mx = x0 + (tw - len(m[0])) // 2
    if plate is not None:
        c.rect(mx - 2, y - 1, mx + len(m[0]) + 2, y + len(m) + 1, plate)
    c.mask(m, mx, y, ink)


def _dark(rgb, by=60):
    return tuple(max(0, v - by) for v in rgb)


def _paint_bag(c, x0, y0, b):
    tw, th = TILE
    body, second, ink = SB.hex_rgb(b["body"]), SB.hex_rgb(b["second"]), SB.hex_rgb(b["ink"])
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    if b["design"] == "band":
        c.rect(x0, y0 + th * 40 // 100, x0 + tw, y0 + th * 62 // 100, second)
    elif b["design"] == "window":
        c.rect(x0 + 8, y0 + th * 55 // 100, x0 + tw - 8, y0 + th * 85 // 100, second)
        # the chips through the window
        for k in range(5):
            c.rect(x0 + 11 + k * 4, y0 + th * 62 // 100 + (k % 2) * 4, x0 + 14 + k * 4,
                   y0 + th * 62 // 100 + (k % 2) * 4 + 3, (230, 190, 90))
    elif b["design"] == "stripe":
        for k in range(3):
            c.rect(x0, y0 + th * (25 + k * 22) // 100, x0 + tw, y0 + th * (25 + k * 22) // 100 + 3, second)
    else:
        c.rect(x0, y0 + th // 2, x0 + tw, y0 + th, second)
    # the crimped seals, top and bottom
    c.rect(x0, y0, x0 + tw, y0 + 3, tuple(min(255, v + 40) for v in body))
    c.rect(x0, y0 + th - 3, x0 + tw, y0 + th, tuple(max(0, v - 40) for v in body))
    _set(c, b["short"], x0, y0 + th * 18 // 100, tw, ink, _dark(body))
    return [b["short"]]


def _paint_cake(c, x0, y0, b):
    """A YUMMYJAWNS carton: the wordmark on a cream band, the flavour's
    colour under it -- the shelf's stripe -- and the flavour's name."""
    tw, th = CARTON_TILE
    body, second, ink = SB.hex_rgb(b["body"]), SB.hex_rgb(b["second"]), SB.hex_rgb(b["ink"])
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    c.rect(x0, y0, x0 + tw, y0 + 13, CREAM)
    _set(c, SB.CAKE_MARK, x0, y0 + 3, tw, MARK_RED)
    c.rect(x0, y0 + 13, x0 + tw, y0 + 15, second)
    _set(c, b["short"], x0, y0 + 20, tw, ink)
    c.rect(x0 + 4, y0 + 31, x0 + tw - 4, y0 + 33, second)
    c.rect(x0, y0 + th - 1, x0 + tw, y0 + th, _dark(body, 40))
    return [SB.CAKE_MARK, b["short"]]


def _paint_fruit(c, x0, y0, b):
    """A fruit-snack box: the name, and the pieces loose down its front."""
    tw, th = SMALL_TILE
    body, second, ink = SB.hex_rgb(b["body"]), SB.hex_rgb(b["second"]), SB.hex_rgb(b["ink"])
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    c.rect(x0, y0, x0 + tw, y0 + 2, second)
    _set(c, b["short"], x0, y0 + 6, tw, ink, _dark(body))
    pieces = (second, (240, 80, 60), (90, 200, 90), (250, 150, 40))
    for k in range(9):
        px, py = x0 + 5 + (k % 3) * 10 + (k // 3 % 2) * 2, y0 + 20 + (k // 3) * 8
        c.rect(px, py, px + 5, py + 4, pieces[k % len(pieces)])
    c.rect(x0, y0 + th - 3, x0 + tw, y0 + th, _dark(body, 40))
    return [b["short"]]


def _paint_kit(c, x0, y0, b):
    """A lunch kit: the name on its band, and the tray through the window --
    crackers, meat, cheese."""
    tw, th = SMALL_TILE
    body, second, ink = SB.hex_rgb(b["body"]), SB.hex_rgb(b["second"]), SB.hex_rgb(b["ink"])
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    c.rect(x0, y0 + 3, x0 + tw, y0 + 15, second)
    _set(c, b["short"], x0, y0 + 6, tw, ink)
    c.rect(x0 + 3, y0 + 19, x0 + tw - 3, y0 + th - 4, (60, 40, 30))
    c.rect(x0 + 5, y0 + 21, x0 + 15, y0 + th - 6, (222, 184, 116))       # crackers
    c.rect(x0 + 17, y0 + 21, x0 + tw - 5, y0 + 29, (212, 112, 112))      # meat
    c.rect(x0 + 17, y0 + 31, x0 + tw - 5, y0 + th - 6, (242, 172, 44))   # cheese
    return [b["short"]]


def _paint_candy(c, x0, y0, b):
    """A bag of the counter rack's candy: the wrapper's own colours and
    design (`candy_brands`), crimped top and bottom."""
    tw, th = SMALL_TILE
    body, second, ink = CB.hex_rgb(b["body"]), CB.hex_rgb(b["second"]), CB.hex_rgb(b["ink"])
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    if b["design"] == "band":
        c.rect(x0, y0 + 24, x0 + tw, y0 + 36, second)
    elif b["design"] == "stripe":
        for k in range(3):
            c.rect(x0, y0 + 22 + k * 8, x0 + tw, y0 + 24 + k * 8, second)
    elif b["design"] == "split":
        c.rect(x0, y0 + th // 2, x0 + tw, y0 + th, second)
    else:                                   # diag: a stepped band, corner to corner
        for k in range(9):
            c.rect(x0 + k * 4, y0 + 40 - k * 2, x0 + k * 4 + 4, y0 + 46 - k * 2, second)
    c.rect(x0, y0, x0 + tw, y0 + 3, tuple(min(255, v + 40) for v in body))
    c.rect(x0, y0 + th - 3, x0 + tw, y0 + th, _dark(body, 40))
    _set(c, b["short"], x0, y0 + 8, tw, ink, _dark(body))
    return [b["short"]]


def bag_art():
    """ONE image for every product on the gondola: a front tile each
    (`tile_<id>`) and a solid block of its body colour (`solid_<id>`) for
    its sides and back. The chip bags' tiles are where 1.13.0 put them; the
    cartons, the small boxes and the candy bags are the rows under them.
    ``{canvas, size, rects, said, name}``; rects are pixel boxes, row 0 at
    the top."""
    tw, th = TILE
    rows = int(math.ceil(len(SB.BRANDS) / float(COLS)))
    cakes = [b for b in SB.BOXED if b["kind"] == "cake"]
    small = [(b, _paint_fruit if b["kind"] == "fruit" else _paint_kit)
             for b in SB.BOXED if b["kind"] != "cake"] + [(b, _paint_candy) for b in CB.BRANDS]
    small_rows = int(math.ceil(len(small) / float(SMALL_COLS)))
    y_cake = rows * th
    y_small = y_cake + CARTON_TILE[1]
    y_solid = y_small + small_rows * SMALL_TILE[1]
    W, H = COLS * tw, y_solid + 8
    assert len(cakes) * CARTON_TILE[0] <= W and SMALL_COLS * SMALL_TILE[0] <= W
    c = Canvas(W, H, (20, 20, 20))
    rects, said, solids = {}, [], []

    def put(b, x0, y0, size, said_):
        assert "tile_" + b["id"] not in rects, b["id"]
        rects["tile_" + b["id"]] = (x0, y0, x0 + size[0], y0 + size[1])
        said.extend(said_)
        solids.append(b)

    for i, b in enumerate(SB.BRANDS):
        x0, y0 = (i % COLS) * tw, (i // COLS) * th
        put(b, x0, y0, TILE, _paint_bag(c, x0, y0, b))
    for i, b in enumerate(cakes):
        x0 = i * CARTON_TILE[0]
        put(b, x0, y_cake, CARTON_TILE, _paint_cake(c, x0, y_cake, b))
    for i, (b, paint) in enumerate(small):
        x0, y0 = (i % SMALL_COLS) * SMALL_TILE[0], y_small + (i // SMALL_COLS) * SMALL_TILE[1]
        put(b, x0, y0, SMALL_TILE, paint(c, x0, y0, b))
    assert len(solids) * 5 <= W, len(solids)
    for i, b in enumerate(solids):
        sx = i * 5
        c.rect(sx, y_solid + 2, sx + 4, y_solid + 6, SB.hex_rgb(b["body"]))
        rects["solid_" + b["id"]] = (sx, y_solid + 2, sx + 4, y_solid + 6)
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H), "rects": rects, "said": said,
            "name": f"snackbags_{W}x{H}_{digest:08x}"}
