"""The labels on a back bar's bottles, painted in pure Python.

Zoo 0.92.0. One RASTER per back bar: a grid of label cells, one per brand
the unit stocks (`liquor_brands`), and beside them a strip of flat patches
-- a label is a quad standing proud of the bottle's front, and the patch is
what the quad's back samples when it is seen from behind the shelf.

WHY A RASTER AND NOT A COLOURED BAND. A coloured band is what the counter's
surface stock carries, because `prim_mesh.build_stock` has no textured path
and a 6 cm label on a counter is read from three metres. The back bar is
read from the aisle at arm's length -- the walker's frame for it is the
shelves at 1.5 m -- and at that distance a band is a smear and a word is a
word. The lettering is Pixel Operator Bold (`pixel_type`, CC0 via
Pixelcoat), the same face the vending machine, the cigarette machine and
the dartboard set.

LEGIBILITY, MEASURED. `LABEL_PX` is 96 x 128 over a label about 0.075 m
wide, so a pixel is 0.78 mm and the 13-row face at scale 1 stands about
10 mm on the glass -- the size of the small type on a real bottle, and
legible at 1.5 m. A logo line takes the largest whole scale whose ink fits
`LABEL_PX[0] - 2 * MARGIN`; nothing is stretched.

Integer arithmetic on bytes and `zlib.crc32` for every draw, so the same
bytes come out of Blender's Python and a plain test. Frame: row 0 at the
top, as a PNG is stored; `dartboard_art.uv_of` maps a rect to (u, v).
"""
from __future__ import annotations

import zlib

from . import liquor_brands as LB
from . import pixel_type as pt
from .vending_forms import Canvas

#: One label cell, pixels. See the docstring for the 0.78 mm pixel.
LABEL_PX = (96, 128)
#: The flat patch beside the grid: what a label quad's edges sample.
PATCH_PX = 4
MARGIN = 4
#: The foil bands across the top and bottom of a label.
FOIL_TOP = (6, 14)
FOIL_BOTTOM = (108, 118)
#: How many pixels of the cell the logo block may take, from the top band
#: down. The small line and the proof mark take what is left -- and what is
#: left is three lines of the face at `SMALL_STEP`, because the longest
#: `line` in the table (ESSINGTON EEL's, 29 characters) wraps to three at
#: scale 1 and a truncated slogan is not a slogan. At 86 the first render
#: cut five of the fourteen mid-word.
LOGO_BOTTOM = 70
#: Rows between two lines of the small type: the face's own 13 less the 3
#: it leaves under the baseline, so three lines fit between the rule and
#: the bottom band.
SMALL_STEP = pt.LINE - 3


def _wear(c, key, amount):
    """Deterministic grime: darken scattered pixels. A bottle behind a bar
    is not printed yesterday."""
    n = int(c.w * c.h * amount)
    h = zlib.crc32(key.encode("utf-8")) & 0xFFFFFFFF
    for _ in range(n):
        h = (h * 1103515245 + 12345) & 0xFFFFFFFF
        x = (h >> 8) % c.w
        h = (h * 1103515245 + 12345) & 0xFFFFFFFF
        y = (h >> 8) % c.h
        r, g, b = c.get(x, y)
        c.px(x, y, (r * 7 // 8, g * 7 // 8, b * 7 // 8))


def _centre(c, text, y, scale, rgb):
    """One line of the pixel face, centred, at row ``y``. Returns the rows
    it used."""
    w = pt.ink_width(text, scale)
    mask = pt.trim(pt.render(text, scale))
    c.mask(mask, (c.w - w) // 2, y, rgb)
    return len(mask)


def paint_label(brand_id: str, variant: int = 0) -> Canvas:
    """One brand's label as a `Canvas` of `LABEL_PX`."""
    b = LB.BY_ID[brand_id]
    w, h = LABEL_PX
    c = Canvas(w, h, b["ground"])
    ink, foil = b["ink"], b["foil"]
    # the printed border, and the foil bands top and bottom
    c.rect(MARGIN - 2, MARGIN - 2, w - MARGIN + 2, MARGIN - 1, foil)
    c.rect(MARGIN - 2, h - MARGIN + 1, w - MARGIN + 2, h - MARGIN + 2, foil)
    c.rect(MARGIN, FOIL_TOP[0], w - MARGIN, FOIL_TOP[1], foil)
    c.rect(MARGIN, FOIL_BOTTOM[0], w - MARGIN, FOIL_BOTTOM[1], foil)
    # THE LOGO, one line at a time, each at the largest scale whose ink
    # fits. The block is laid from the top band down and centred in what it
    # is given, so a two-line mark sits where a three-line mark's middle is.
    usable = w - 2 * MARGIN
    lines = list(b["logo"])
    scales = [max(1, pt.fit_scale(t, usable, cap=3)) for t in lines]
    lead = 4

    def _heights(ss):
        return [len(pt.trim(pt.render(t, s))) for t, s in zip(lines, ss)]

    # THE BLOCK FITS ITS BOX, and each line fitting the WIDTH is not that.
    # CHESTER CREEK RYE takes scales 1, 2 and 3 -- every line inside the
    # margins -- and stands 62 rows in a 56-row box, so the first render
    # ran "RYE" through "STRAIGHT. MOSTLY.". The tallest line gives up a
    # step until the block fits.
    avail = LOGO_BOTTOM - FOIL_TOP[1]
    heights = _heights(scales)
    while sum(heights) + lead * (len(lines) - 1) > avail and max(scales) > 1:
        k = scales.index(max(scales))
        scales[k] -= 1
        heights = _heights(scales)
    block = sum(heights) + lead * (len(lines) - 1)
    y = FOIL_TOP[1] + max(4, (LOGO_BOTTOM - FOIL_TOP[1] - block) // 2)
    for t, s, hh in zip(lines, scales, heights):
        _centre(c, t, y, s, ink)
        y += hh + lead
    # the rule under the mark, then the small line, wrapped
    c.rect(MARGIN + 10, min(y + 2, LOGO_BOTTOM), w - MARGIN - 10,
           min(y + 3, LOGO_BOTTOM + 1), foil)
    y = min(y + 7, LOGO_BOTTOM + 4)
    small = pt.wrap(b["line"], usable, 1) or [b["line"]]
    for t in small:
        if y + pt.LINE > FOIL_BOTTOM[0] - 1:
            raise ValueError(
                "liquor_brands '%s': line %r does not fit the label "
                "(wrapped to %d lines)" % (brand_id, b["line"], len(small)))
        _centre(c, t, y, 1, ink)
        y += SMALL_STEP
    # the proof mark ON the bottom band, in the ground colour
    _centre(c, b["proof"] + " PROOF", FOIL_BOTTOM[0] + 1, 1, b["ground"])
    _wear(c, f"{brand_id}:{int(variant)}", 0.03 + 0.02 * (int(variant) % 4))
    return c


def label_atlas(brand_ids, key: str = "", variant: int = 0) -> dict:
    """Every brand's label on one raster.

    Returns ``{canvas, rects, size, name, brands}``: ``rects`` maps a brand
    id to its pixel box (x0, y0, x1, y1) and ``<id>_patch`` to its flat
    patch, row 0 at the top. Deterministic: the same ids in the same order
    give the same bytes and the same name.
    """
    ids = list(brand_ids)
    lw, lh = LABEL_PX
    cols = min(4, max(1, len(ids)))
    rows = (len(ids) + cols - 1) // cols
    w = cols * lw + PATCH_PX
    h = max(rows * lh, PATCH_PX * len(ids))
    canvas = Canvas(w, h, (0, 0, 0))
    rects = {}
    for i, bid in enumerate(ids):
        cx, cy = (i % cols) * lw, (i // cols) * lh
        canvas.paste(paint_label(bid, variant), cx, cy)
        rects[bid] = (cx, cy, cx + lw, cy + lh)
        px, py = cols * lw, i * PATCH_PX
        canvas.rect(px, py, px + PATCH_PX, py + PATCH_PX, LB.BY_ID[bid]["ground"])
        rects[bid + "_patch"] = (px, py, px + PATCH_PX, py + PATCH_PX)
    digest = zlib.crc32(bytes(canvas.buf)) & 0xFFFFFFFF
    return {"canvas": canvas, "rects": rects, "size": (w, h),
            "brands": tuple(ids), "key": str(key),
            "name": f"backbar_labels_{w}x{h}_{digest:08x}"}


def painted_strings(brand_ids) -> list:
    """Every string an atlas of these brands paints: for the denylist."""
    out = []
    for bid in brand_ids:
        out += LB.painted_strings(bid)
    return out
