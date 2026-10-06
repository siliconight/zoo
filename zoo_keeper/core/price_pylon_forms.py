"""The gas station's price pylon, decided in pure Python: the base, the
posts, the brand cabinet, the price cabinet, the strip, and every pixel of
what glows.

Zoo 1.19.0, species `price_pylon`. Asked for by name, 2026-09-28: "do the
price pylon next". The references: docs/SET_DRESSING_REFERENCES.md, "A pylon
sign at the road. Tall, freestanding, at the kerb where a driver reads it
before the building -- the second half of a strip's signage, and the one a
player sees from three streets away. Owner: Zoo (a species) plus Lot (at
the frontage, facing the road)"; docs/proposals/GAS_STATION_SHOP.md on the
pumps, "dollars-per-gallon to the nine-tenths -- 1.55, 1.45 9/10 ... the 9/10
fraction is the detail that reads as 1997 at a glance"; and the walker's
store-at-night photographs, where a lit box sign on a pole is one of the
two lights the street has.

WHAT IS BUILT, in the recipe frame (metres, Z up, floor 0, CENTRE pivot,
the faces at -Y and +Y, both read):

  * a concrete PLINTH, and two steel POSTS rising from it;
  * the BRAND CABINET on top -- FLAPPAHS, the store's own name -- and the
    PRICE CABINET under it, three grades a row each with the price to the
    nine-tenths, and a strip under that, OPEN 24 HRS;
  * every cabinet a painted steel box with its two faces lit.

BOTH FACES READ. A pylon stands across the road's line, so a driver from
either direction reads one face; the back face maps its art with u
reversed, or it reads mirrored.

GLOWING WITHOUT A LIGHT: one backlit image (`M_Pylon_<art>_Face`, so Lux's
power cut takes it), the cooler wall's idiom. It is the brightest thing on
the street at night by emission, and costs no light.

TWO SUBMISSIONS: painted steel and concrete (colours in the `Wear` vertex
colour), and the glow -- there is no glass.

NO TWO FACES SHARE A PLANE (`prims.coincident_pairs` empty).
"""
from __future__ import annotations

import re
import zlib

from . import pixel_type as pt
from . import prims as P
from .vending_forms import Canvas

#: Lot's request (long side first), then the genome's range.
#:
#: 3.4 x 0.7 x 9.0 SINCE 1.26.0, the width the range's top and the rest in
#: proportion (x1.42; the height at the range's top). The walker, 2026-09-29:
#: "yes, make the pylon bigger". THE WIDTH IS WHAT READS: eight 5-wide letters
#: across the face fit the name at 3 texels a stroke on a 2.4 m pylon and 5 on
#: a 3.4 m one (80 px/m, 3.75 -> 6.25 cm), and a stroke of 3.75 cm read as a
#: word at 12 m on cold run 9108's walk copy -- so the same frame should carry
#: FLAPPAHS about 20 m. The digits go 3 -> 4 (5 cm).
DC_SIZES = ((3.4, 0.7, 9.0),)
RANGES = {"width": (1.6, 3.4), "depth": (0.3, 0.8), "height": (4.5, 9.0)}

BURY = 0.004
PLINTH_H = 0.5
POST = 0.20
POST_IN = 0.35            # a post's centre in from the pylon's end
BRAND_F = 0.23            # the cabinets' heights, fractions of the pylon's
PRICE_F = 0.25
STRIP_F = 0.07
GAP_F = 0.012             # between cabinets, a steel band
FACE_PROUD = 0.003
FACE_IN = 0.05            # a lit face inset from its cabinet's edges

STORE = "FLAPPAHS"
STRIP = "OPEN 24 HRS"
#: The grades, top to bottom: (name, the pump reference's body colour).
GRADES = (("REGULAR", (200, 200, 204)), ("PLUS", (200, 30, 36)), ("SUPER", (220, 170, 40)))
#: 1997 Delaware County, dollars a gallon, by variant; each prints with 9/10.
PRICE_SETS = (("1.19", "1.29", "1.39"), ("1.15", "1.25", "1.35"),
              ("1.21", "1.31", "1.41"), ("1.17", "1.27", "1.37"))
#: The brand's colourways by variant: field, rule, ink -- the coffee sign's
#: (`coffee_island_forms.COLOURWAYS`), so the store's two signs are one brand.
COLOURWAYS = (((24, 78, 52), (226, 206, 150), (246, 238, 214)),
              ((70, 36, 20), (226, 176, 92), (250, 236, 206)),
              ((22, 44, 82), (214, 196, 150), (240, 236, 222)),
              ((96, 22, 26), (232, 212, 170), (248, 240, 222)))

MATERIALS = {
    "cabinet": ((0.10, 0.11, 0.12), "metal_painted"),
    "post": ((0.30, 0.31, 0.33), "metal_painted"),
    "band": ((0.62, 0.63, 0.65), "metal_painted"),
    "plinth": ((0.52, 0.50, 0.46), "metal_painted"),
}
KIND_BASE = {"metal_painted": (1.0, 1.0, 1.0)}
GLOW_EMISSION = 1.4       # a sign read from three streets away: over the cooler's 1.0
GLOW_ALBEDO = 0.6
TEXEL = 80                # px a metre: a 2.4 m face is ~190 px wide
_VARIANT = re.compile(r"_n\d+(?=_|$)")


def vertex_tint(mat_key):
    rgb, kind = MATERIALS[mat_key]
    return kind, tuple(c / b for c, b in zip(rgb, KIND_BASE[kind]))


def resolve(plan_):
    params = plan_.get("params") or {}
    module = plan_.get("module") or {}
    return int(module.get("variant") or params.get("variant") or 0)


def lit_box(part, lo, hi, region):
    """A face panel: its -Y face maps onto ``region``, its +Y face onto the
    same region with u reversed (read from behind), the rest take ``edge``."""
    p = P.box(part, "glow", lo, hi)
    x0, _y0, z0 = lo
    x1, _y1, z1 = hi

    def uv(i, rev):
        x, _y, z = p["verts"][i]
        u = (x - x0) / (x1 - x0)
        return (region, 1.0 - u if rev else u, (z - z0) / (z1 - z0))
    p["uvs"] = [tuple(uv(i, False) for i in f) if k == 2 else
                tuple(uv(i, True) for i in f) if k == 4 else
                tuple(("edge",) for _ in f)
                for k, f in enumerate(p["faces"])]
    return p


def bands(h):
    """``{name: (z0, z1)}`` of the three cabinets, top down, and the posts'
    reach: under the brand, the prices, then the strip."""
    bh, ph, sh, g = BRAND_F * h, PRICE_F * h, STRIP_F * h, GAP_F * h
    brand = (h - bh, h)
    price = (brand[0] - g - ph, brand[0] - g)
    strip = (price[0] - g - sh, price[0] - g)
    return {"brand": brand, "price": price, "strip": strip}


def layout(w, d, h, variant=0):
    out = []
    B = bands(h)
    # the plinth, the posts, a steel band between cabinets
    out.append(P.box("Pylon_Plinth", "plinth", (-w / 2.0 * 0.9, -d / 2.0, 0.0), (w / 2.0 * 0.9, d / 2.0, PLINTH_H)))
    px = w / 2.0 - POST_IN
    for s in (-1, 1):
        out.append(P.box("Pylon_Post", "post", (s * px - POST / 2.0, -POST / 2.0, PLINTH_H - BURY),
                         (s * px + POST / 2.0, POST / 2.0, B["strip"][0] + BURY)))
    # the cabinets: the steel box a little narrower than the faces' carrier,
    # its lit panels proud of both of its faces
    for name, (z0, z1) in (("brand", B["brand"]), ("price", B["price"]), ("strip", B["strip"])):
        cw = w if name != "strip" else w * 0.86
        cd = d if name != "strip" else d * 0.8
        out.append(P.box("Pylon_Cabinet", "cabinet", (-cw / 2.0, -cd / 2.0 + FACE_PROUD + 0.001, z0),
                         (cw / 2.0, cd / 2.0 - FACE_PROUD - 0.001, z1)))
        out.append(lit_box("Pylon_Face", (-cw / 2.0 + FACE_IN, -cd / 2.0, z0 + FACE_IN),
                           (cw / 2.0 - FACE_IN, cd / 2.0, z1 - FACE_IN), name))
    # the steel bands between cabinets, buried in both
    for z0, z1 in ((B["price"][1] - BURY, B["brand"][0] + BURY), (B["strip"][1] - BURY, B["price"][0] + BURY)):
        out.append(P.box("Pylon_Band", "band", (-w / 2.0 * 0.8, -d / 2.0 * 0.6, z0), (w / 2.0 * 0.8, d / 2.0 * 0.6, z1)))
    facts = {"bands": B, "prices": list(PRICE_SETS[variant % len(PRICE_SETS)]),
             "collision": ((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h))}
    return out, facts


def plan(w, d, h, variant=0):
    prims, facts = layout(w, d, h, variant)
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


# --- the glow -------------------------------------------------------------------------

INK = (20, 20, 22)
WHITE = (250, 250, 244)
HEAD_FACE = "monogram"     # the slush machine's reason: bold's N reads as H


#: THE TYPE IS SET AS LARGE AS THE FACE ALLOWS (1.25.0). The walker,
#: 2026-09-29: "do the pylon brand sign at night next". MEASURED on cold run
#: 9107's walk copy, the pylon rebuilt and swapped in, one camera 12 m out
#: square to the face: the brand FIELD read at night (luma 125, the price
#: panel 251) -- what did not read, at night or at noon, was any LETTER.
#: 1.19.0 fitted the name and the dollars by one integer scale to their
#: width, so FLAPPAHS stood 0.26 m tall in a 1.4 m face and the dollars 0.18
#: m in a 0.5 m row, 2-3 texels a stroke; a 184-texel face drawn ~110 px wide
#: is minified, and the frame softens anything under a few pixels, so both
#: were a smudge and a blank.
#:
#: NAME_FILL: the name keeps its width-fitted scale -- eight letters across
#: the face are the horizontal limit -- and is stretched in whole rows to
#: fill this fraction of the face's height, the rule and margins kept.
#: Measured: the brand's detail (luma standard deviation) 48 -> 59 at night,
#: 26 -> 33 at noon, the name a bold word where it was a smear.
NAME_FILL = 0.5
#: DIGITS_AT / DIGITS_W: the dollars start after the widest grade label
#: (the chip and REGULAR at m5x7 scale 1 end at 56 of 184 px) and may take
#: this much of the face, which fits them at scale 3 with the 9/10 after --
#: 3 texels a stroke where 1.19.0 had 2. The frame at 12 m did not resolve
#: them either way (price detail 11 -> 11); set large because the face has
#: the room and a closer camera does.
DIGITS_AT = 0.36
DIGITS_W = 0.40


def _tall(mask, height):
    """``mask`` stretched in whole rows to the tallest that fits ``height``."""
    k = max(1, int(height // max(1, len(mask))))
    return [row for row in mask for _ in range(k)]


def _scale(text, width, height, face, cap):
    for k in range(cap, 0, -1):
        if pt.ink_width(text, k, face) <= width and pt.line(face) * k <= height:
            return k
    return 0


def _stamp(c, text, x, y, scale, face, colour):
    m = pt.trim(pt.render(text, scale, face))
    c.mask(m, x, y, colour)
    return len(m[0]), len(m)


def price_text(price):
    """The row's printed price: the dollars, and the nine-tenths."""
    return price, "9/10"


def art(w, h, variant=0):
    """ONE image: the brand face (`brand`), the price face (`price`), the
    strip (`strip`), and an `edge` block. ``{canvas, size, rects, name,
    said}``; rects are pixel boxes, row 0 at the top."""
    field, rule, ink = COLOURWAYS[variant % len(COLOURWAYS)]
    B = bands(h)
    fw = w - 2 * FACE_IN
    FW = int(round(fw * TEXEL))
    SW = int(round((w * 0.86 - 2 * FACE_IN) * TEXEL))
    BH = int(round((B["brand"][1] - B["brand"][0] - 2 * FACE_IN) * TEXEL))
    PH = int(round((B["price"][1] - B["price"][0] - 2 * FACE_IN) * TEXEL))
    SH = int(round((B["strip"][1] - B["strip"][0] - 2 * FACE_IN) * TEXEL))
    W, H = FW, BH + PH + SH + 10
    c = Canvas(W, H, INK)
    rects, said = {}, []
    # the brand: the store's name on its field, a rule round it
    c.rect(0, 0, FW, BH, field)
    c.rect(2, 2, FW - 2, 4, rule)
    c.rect(2, BH - 4, FW - 2, BH - 2, rule)
    s = _scale(STORE, FW - 12, BH - 16, HEAD_FACE, 6)
    m = _tall(pt.trim(pt.render(STORE, s, HEAD_FACE)), (BH - 16) * NAME_FILL)
    c.mask(m, (FW - len(m[0])) // 2, (BH - len(m)) // 2, rule, grow=1)
    c.mask(m, (FW - len(m[0])) // 2, (BH - len(m)) // 2, ink)
    said.append(STORE)
    rects["brand"] = (0, 0, FW, BH)
    # the prices: a grade a row, white panels, black digits, the 9/10 small
    y0 = BH + 2
    c.rect(0, y0, FW, y0 + PH, (236, 236, 230))
    row = PH // len(GRADES)
    prices = PRICE_SETS[variant % len(PRICE_SETS)]
    # ONE scale for every grade's name: fitted each on its own, REGULAR set
    # at half PLUS's size in the first render
    gs = min(_scale(g, FW * 0.38, row - 6, "m5x7", 2) for g, _c in GRADES)
    for i, ((grade, gc), price) in enumerate(zip(GRADES, prices)):
        ry = y0 + i * row
        c.rect(0, ry, FW, ry + 1, INK)
        c.rect(0, ry + 1, max(6, FW // 16), ry + row, gc)                 # the grade's colour
        _stamp(c, grade, max(6, FW // 16) + 4, ry + (row - pt.line("m5x7") * gs) // 2, gs, "m5x7", INK)
        dollars, tenths = price_text(price)
        dx = int(FW * DIGITS_AT)
        ds = _scale(dollars, FW * DIGITS_W, row - 6, HEAD_FACE, 5)
        md = _tall(pt.trim(pt.render(dollars, ds, HEAD_FACE)), row - 6)
        c.mask(md, dx, ry + (row - len(md)) // 2, INK)
        dw = len(md[0])
        ts = max(1, ds // 2)
        _stamp(c, tenths, dx + dw + 3, ry + (row - pt.line(HEAD_FACE) * ds) // 2 + 1, ts, "m5x7", INK)
        said.append(f"{grade} {dollars} {tenths}")
    rects["price"] = (0, y0, FW, y0 + PH)
    # the strip
    y1 = y0 + PH + 2
    c.rect(0, y1, SW, y1 + SH, rule)
    ss = _scale(STRIP, SW - 8, SH - 4, "m5x7", 3)
    m = pt.trim(pt.render(STRIP, ss, "m5x7"))
    c.mask(m, (SW - len(m[0])) // 2, y1 + (SH - len(m)) // 2, field)
    said.append(STRIP)
    rects["strip"] = (0, y1, SW, y1 + SH)
    y2 = y1 + SH + 2
    rects["edge"] = (0, y2, 4, y2 + 4)
    c.rect(*rects["edge"], INK)
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H), "rects": rects, "said": said,
            "name": f"pylon_v{variant % 4}_{W}x{H}_{digest:08x}"}
