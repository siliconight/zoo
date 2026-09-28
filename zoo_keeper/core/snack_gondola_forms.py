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
  * CHIP BAGS on every shelf, faced out: each a real bag -- a puffed front,
    flat sides (`prims.pillow` stood on its back) -- its front printed from
    one image (`bag_art`), the rest of it its brand's colour from the same
    image;
  * END CAPS at both ends when the run is long enough: three shelves facing
    out along the aisle, stacked with more bags.

REAL STRUCTURE, NOT A PRINTED CARD. The walker's standing preference: a bag
is a bag-shaped solid with its print on it, not a picture of a row of bags
on a flat panel. It costs 22 triangles a bag.

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


def bag(x, y_front, z0, bw, bh, brand):
    """One bag, its puffed front toward -Y at ``y_front``, standing on
    ``z0`` (buried `BURY`), centred on ``x``. A `prims.pillow` built on its
    back and turned up: its crowned top becomes the front. ``uvs`` put the
    four front quads on the brand's tile and every other face on the
    brand's colour block."""
    # the pillow in a local frame: x across, y is the bag's height, z its depth
    p = P.pillow("Snack_Bag", "bag", (-bw / 2.0, 0.0, 0.0), (bw / 2.0, bh, BAG_D), BAG_CROWN)
    # turn +Z (the crown) to -Y and +Y (the bag's height) to +Z
    p = P.rotate_x(p, math.pi / 2.0, about=(0.0, 0.0))
    p = P.translate(p, (x, y_front + BAG_D + BAG_CROWN, z0 - BURY))
    # faces 1-4 are the crowned top -- the front now
    xs = [v[0] for v in p["verts"]]
    zs = [v[2] for v in p["verts"]]
    x0, x1, zb, zt = min(xs), max(xs), min(zs), max(zs)
    uvs = []
    for k, f in enumerate(p["faces"]):
        if 1 <= k <= 4:
            uvs.append(tuple(("tile_" + brand, (p["verts"][i][0] - x0) / (x1 - x0),
                              (p["verts"][i][2] - zb) / (zt - zb)) for i in f))
        else:
            uvs.append(tuple(("solid_" + brand,) for _ in f))
    p["uvs"] = uvs
    return p


def _side(xs0, xs1, bays_, h, d, key, variant, face):
    """One shelved face of the run (the -Y one), over x ``xs0..xs1``."""
    out, n_bags = [], 0
    levels, pitch = shelf_levels(h)
    y_front = -d / 2.0 + 0.02                         # the shelves' front edge
    y_back = -SPINE_T / 2.0 + BURY                    # buried into the spine
    bh = min(0.30, pitch - SHELF_T - 0.06)
    for bi, (bx, bw) in enumerate(bays_):
        sx0, sx1 = bx - bw / 2.0 + UPRIGHT_W / 2.0 + 0.004, bx + bw / 2.0 - UPRIGHT_W / 2.0 - 0.004
        for k, z in enumerate(levels):
            if k:        # the deck is the kick's top
                out.append(P.box("Snack_Shelf", "steel", (sx0, y_front, z - SHELF_T), (sx1, y_back, z)))
            out.append(P.box("Snack_Strip", "strip", (sx0 + 0.003, y_front - STRIP_T, z - STRIP_H + 0.004),
                             (sx1 - 0.003, y_front + BURY, z + 0.006)))
            n = max(1, int((sx1 - sx0 - 0.02) // (BAG_W + BAG_GAP)))
            span = n * BAG_W + (n - 1) * BAG_GAP
            bx0 = (sx0 + sx1) / 2.0 - span / 2.0 + BAG_W / 2.0
            for i in range(n):
                brand = SB.IDS[(_h(key, variant, face, bi, k) + i // 2) % len(SB.IDS)]
                # a pair of facings a brand, as a real shelf is stocked
                out.append(bag(bx0 + i * (BAG_W + BAG_GAP), y_front + 0.014, z, BAG_W, bh, brand))
                n_bags += 1
    return out, n_bags


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
    side, n_bags = _side(xa, xb, bays_, h, d, key, variant, "a")
    other, n_b = _side(xa, xb, bays_, h, d, key, variant, "b")
    out += side + [P.rotate_z(p, math.pi, about=(0.0, 0.0)) for p in other]
    n_bags += n_b
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
            # the cap's upright back, full height of its shelves, against the end panel
            # its bottom 12 mm into the kick: at the spine's 4 mm the two shared it
            cap.append(P.box("Snack_Frame", "steel", (ct - 0.03, ys0 - 0.02, KICK_H - 0.012),
                             (ct, ys1 + 0.02, levels[-1] + 0.10)))
            out += cap if s < 0 else [P.rotate_z(p, math.pi, about=(0.0, 0.0)) for p in cap]
    facts = {"bays": len(bays_), "bay_width": bays_[0][1], "end_caps": caps, "bags": n_bags,
             "shelves": len(shelf_levels(h)[0]), "run": L,
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


def bag_art():
    """ONE image for every bag: a front tile a brand (`tile_<id>`) and a
    solid block of its body colour (`solid_<id>`) for its sides and back.
    ``{canvas, size, rects, said, name}``; rects are pixel boxes, row 0 at
    the top."""
    tw, th = TILE
    rows = int(math.ceil(len(SB.BRANDS) / float(COLS)))
    W, H = COLS * tw, rows * th + 8
    c = Canvas(W, H, (20, 20, 20))
    rects, said = {}, []
    for i, b in enumerate(SB.BRANDS):
        x0, y0 = (i % COLS) * tw, (i // COLS) * th
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
        m = pt.trim(pt.render(b["short"], 1, "m5x7"))
        mx = x0 + (tw - len(m[0])) // 2
        my = y0 + th * 18 // 100
        c.rect(mx - 2, my - 1, mx + len(m[0]) + 2, my + len(m) + 1, tuple(max(0, v - 60) for v in body))
        c.mask(m, mx, my, ink)
        said.append(b["short"])
        rects["tile_" + b["id"]] = (x0, y0, x0 + tw, y0 + th)
        sx = i * 5
        c.rect(sx, rows * th + 2, sx + 4, rows * th + 6, body)
        rects["solid_" + b["id"]] = (sx, rows * th + 2, sx + 4, rows * th + 6)
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H), "rects": rects, "said": said,
            "name": f"snackbags_{W}x{H}_{digest:08x}"}
