"""The litter bin's shape and its paint, pure (Zoo 1.92.0, roadmap 219 note 5).

Lot stands one at each crossing, 1.5 m before the cut, where people wait (`site_furniture`), and
until 1.92.0 it was the PLACEHOLDER SILHOUETTE `tools/new_species.py` minted on 2026-09-12: one
grey box. Now it is a 1990s municipal street bin: a square steel body of vertical slats in the
street-furniture green, a lid with a square mouth and the black bag showing in it, four short
feet, and the township's placard on two faces -- LITTER, and a line in the brand rule's voice.

ONE ATLAS AND ONE MATERIAL, so one draw a bin, as the dumpster is (1.58.0): every prim is a quad
on `_card_atlas`'s atlas, `paint`, and `card_art.paint` sends this module's `litter_` tiles here.
A bin stands at every crossing of a level, so its price is its count; the slats are painted, not
modelled.

FRAME AND UNITS: metres, X across, Y along (the placard faces -Y and +Y), Z up from the ground at
0; `build.build_module` re-centres the module.
"""
from __future__ import annotations

import zlib

from . import machine_parts as MP
from . import paint as PT
from . import prims as P
from . import smooth_type as ST

#: Pixels a metre of paint, as the dumpster's.
TEXEL = 256
FOOT = 0.06              # the feet's height: the body's underside above the ground
FOOT_W = 0.06            # a foot's plan size
FOOT_IN = 0.04           # in from the body's corner
LID_T = 0.06             # the lid's thickness
LID_OVER = 0.02          # how far the lid stands past the body each side
MOUTH = 0.30             # the mouth's width, of the lid's
MOUTH_DEPTH = 0.12       # how far down the bag's top sits under the lid's top

#: The township's street-furniture green, and the paint around it (sRGB 0..255).
GREEN = (36, 72, 50)
STEEL_DARK = (22, 24, 23)
BAG = (16, 16, 18)
PLACARD = (232, 230, 220)
INK = (24, 52, 36)
RUST = (112, 58, 26)
BARE = (150, 152, 154)
#: The placard: LITTER, and a line in the brand rule's voice (invented, Delco, PG-13). A
#: township's sign is an institution's: `smooth_type.OWNERS["maker"]`.
PLACARD_LINES = (("LITTER", 0.55), ("KEEP DELCO CLASSY-ISH", 0.16))
MAKER = ST.owned("maker")
#: The slats: their width and the gap between them, metres.
SLAT = (0.045, 0.014)


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def _px(m):
    return max(8, int(round(m * TEXEL)))


def _lift(rgb, by):
    return tuple(max(0, min(255, c + by)) for c in rgb)


def _box(part, tile, lo, hi, skip=()):
    """An axis-aligned box as quads, each wound and mapped as its viewer sees it; ``skip`` names
    faces left out (front, back, left, right, top, under)."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    faces = {
        "front": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
        "back": [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
        "right": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
        "left": [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
        "top": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        "under": [(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)],
    }
    return [MP.quad(f"{part}_{k}", "paint", tile if isinstance(tile, str) else tile.get(k, tile["*"]), v)
            for k, v in faces.items() if k not in skip]


def plan(w, d, h):
    """``{"prims", "tiles", "collision", "facts"}``: every prim a quad on the one atlas,
    ``paint``. The slot is exact: the lid's outer faces are its width and depth, its top the
    height."""
    lx, ly = w / 2.0, d / 2.0                         # the lid's outer half-sizes
    bx, by = lx - LID_OVER, ly - LID_OVER             # the body's
    zl = h - LID_T                                    # the lid's underside, the body's top
    mx, my = lx * MOUTH, ly * MOUTH                   # the mouth's half-sizes
    zm = h - MOUTH_DEPTH                              # the bag's top
    prims = []
    # the body: four slatted sides and an underside; no top (the lid closes it)
    prims += _box("LitterBin_Body", {"*": "side", "front": "placard", "back": "placard"},
                  (-bx, -by, FOOT), (bx, by, zl), skip=("top",))
    # the lid's edges and its underside's ring outside the body
    prims += _box("LitterBin_Lid", {"*": "lid_edge"}, (-lx, -ly, zl), (lx, ly, h), skip=("top", "under"))
    ring = [((-lx, -ly), (lx, -ly), (bx, -by), (-bx, -by)), ((lx, -ly), (lx, ly), (bx, by), (bx, -by)),
            ((lx, ly), (-lx, ly), (-bx, by), (bx, by)), ((-lx, ly), (-lx, -ly), (-bx, -by), (-bx, by))]
    for k, quad in enumerate(ring):
        # wound to face down
        prims.append(MP.quad(f"LitterBin_LidUnder{k}", "paint", "dark",
                             [(quad[1][0], quad[1][1], zl), (quad[0][0], quad[0][1], zl),
                              (quad[3][0], quad[3][1], zl), (quad[2][0], quad[2][1], zl)]))
    # the lid's top: a frame round the mouth
    frame = [((-lx, -ly), (lx, -ly), (mx, -my), (-mx, -my)), ((lx, -ly), (lx, ly), (mx, my), (mx, -my)),
             ((lx, ly), (-lx, ly), (-mx, my), (mx, my)), ((-lx, ly), (-lx, -ly), (-mx, -my), (-mx, my))]
    for k, quad in enumerate(frame):
        prims.append(MP.quad(f"LitterBin_LidTop{k}", "paint", "lid",
                             [(quad[0][0], quad[0][1], h), (quad[1][0], quad[1][1], h),
                              (quad[2][0], quad[2][1], h), (quad[3][0], quad[3][1], h)]))
    # the mouth's walls, facing in, down to the bag; the bag's top
    walls = [((-mx, my), (mx, my)), ((mx, my), (mx, -my)), ((mx, -my), (-mx, -my)), ((-mx, -my), (-mx, my))]
    for k, (a, b) in enumerate(walls):
        prims.append(MP.quad(f"LitterBin_Mouth{k}", "paint", "bag_wall",
                             [(a[0], a[1], zm), (b[0], b[1], zm), (b[0], b[1], h), (a[0], a[1], h)]))
    prims.append(MP.quad("LitterBin_Bag", "paint", "bag",
                         [(-mx, -my, zm), (mx, -my, zm), (mx, my, zm), (-mx, my, zm)]))
    # the feet: no top (it would lie on the body's underside)
    for name, fx, fy in (("FL", -bx + FOOT_IN, -by + FOOT_IN), ("FR", bx - FOOT_IN, -by + FOOT_IN),
                         ("BL", -bx + FOOT_IN, by - FOOT_IN), ("BR", bx - FOOT_IN, by - FOOT_IN)):
        prims += _box(f"LitterBin_Foot{name}", "dark",
                      (fx - FOOT_W / 2.0, fy - FOOT_W / 2.0, 0.0), (fx + FOOT_W / 2.0, fy + FOOT_W / 2.0, FOOT),
                      skip=("top",))
    body_h = zl - FOOT
    tiles = {
        "side": ("paint", {"kind": "litter_side", "w_m": 2.0 * by, "h_m": body_h}),
        "placard": ("paint", {"kind": "litter_placard", "w_m": 2.0 * bx, "h_m": body_h}),
        "lid": ("paint", {"kind": "litter_lid", "w_m": 2.0 * lx, "h_m": ly - my}),
        "lid_edge": ("paint", {"kind": "litter_lid_edge", "w_m": 2.0 * lx, "h_m": LID_T}),
        "dark": ("paint", {"kind": "litter_dark", "w_m": 0.1, "h_m": 0.1}),
        "bag_wall": ("paint", {"kind": "litter_bag_wall", "w_m": 2.0 * mx, "h_m": MOUTH_DEPTH}),
        "bag": ("paint", {"kind": "litter_bag", "w_m": 2.0 * mx, "h_m": 2.0 * my}),
    }
    return {"prims": prims, "tiles": tiles,
            "collision": ((-lx, -ly, 0.0), (lx, ly, h)),
            "facts": {"tris": P.tri_count(prims), "materials": 1}}


# --- the paint ---------------------------------------------------------------------------------


def _slats(im, w, h, seed):
    """Vertical steel slats in the green, the dark of the inside between them, a frame band top
    and foot, grime risen from the pavement and chips along the edges."""
    ppm = TEXEL
    im.rect((0, 0, w, h), STEEL_DARK)
    sw, gap = max(2, int(SLAT[0] * ppm)), max(1, int(SLAT[1] * ppm))
    x = gap // 2
    k = 0
    while x < w:
        im.vgrad((x, 0, min(w, x + sw), h), _lift(GREEN, 14), _lift(GREEN, -14))
        im.rect((x, 0, min(w, x + 2), h), _lift(GREEN, 22), 0.6)
        k += 1
        x += sw + gap
    band = max(3, int(0.06 * ppm))
    for y0 in (0, h - band):
        im.vgrad((0, y0, w, y0 + band), _lift(GREEN, 10), _lift(GREEN, -18))
    im.grain((0, 0, w, h), 4.0, seed)
    im.vgrad((0, int(h * 0.80), w, h), _lift(GREEN, -20), _lift(GREEN, -46))
    for c in range(max(3, w // 30)):
        r = _h("chip", seed, c)
        cx = r % max(1, w - 4)
        im.rect((cx, (r >> 8) % band, cx + 2 + (r >> 12) % 3, 2 + (r >> 8) % band), BARE, 0.5)
    for s in range(4):
        r = _h("rust", seed, s)
        cx = 3 + r % max(1, w - 6)
        im.rect((cx, h - band - int(h * 0.12), cx + 2, h - band), RUST, 0.30)


def paint(spec):
    """One tile as a Canvas; ``c.unset`` lists every line that did not set."""
    kind = spec["kind"]
    w, h = _px(spec["w_m"]), _px(spec["h_m"])
    if kind in ("litter_side", "litter_placard"):
        im = PT.Img(w, h, GREEN)
        _slats(im, w, h, 31 if kind == "litter_side" else 37)
        if kind == "litter_placard":
            px0, px1 = int(w * 0.16), int(w * 0.84)
            py0, py1 = int(h * 0.16), int(h * 0.46)
            im.rrect((px0, py0, px1, py1), 3, PLACARD)
            im.edge_dark((px0, py0, px1, py1), 3, 0.12)
            ph = py1 - py0
            pad = max(3, (px1 - px0) // 18)
            top = py0 + ph * 0.10
            for text, share in PLACARD_LINES:
                line_h = ph * share
                im.text(text, (px0 + pad, top, px1 - pad, top + line_h), INK, face=MAKER,
                        cap=line_h * 0.9, min_cap=max(5, int(line_h * 0.5)))
                top += line_h + ph * 0.08
        return im.to_canvas()
    if kind == "litter_lid":
        im = PT.Img(w, h, GREEN)
        im.vgrad((0, 0, w, h), _lift(GREEN, 6), _lift(GREEN, -12))
        im.grain((0, 0, w, h), 4.0, 41)
        im.edge_dark((0, 0, w, h), max(3, h // 6), 0.25)
        return im.to_canvas()
    if kind == "litter_lid_edge":
        im = PT.Img(w, h, _lift(GREEN, -8))
        im.grain((0, 0, w, h), 3.0, 43)
        return im.to_canvas()
    if kind == "litter_bag_wall":
        im = PT.Img(w, h, BAG)
        im.vgrad((0, 0, w, h), (34, 34, 36), BAG)
        return im.to_canvas()
    if kind == "litter_bag":
        # the bag's top, and what is on it: a cup's rim, a wrapper, a crumpled flyer
        im = PT.Img(w, h, BAG)
        im.grain((0, 0, w, h), 6.0, 47)
        im.disc(w * 0.34, h * 0.40, w * 0.11, (226, 222, 210))
        im.disc(w * 0.34, h * 0.40, w * 0.085, (40, 34, 30))
        im.rect((w * 0.56, h * 0.58, w * 0.82, h * 0.72), (176, 40, 36))
        im.rect((w * 0.20, h * 0.68, w * 0.44, h * 0.84), (214, 206, 176), 0.85)
        return im.to_canvas()
    if kind == "litter_dark":
        return PT.Img(w, h, STEEL_DARK).to_canvas()
    raise ValueError(f"no litter bin tile {kind!r}")
