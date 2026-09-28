"""The convenience store's service counter, decided in pure Python: the
checkerboard trim, the registers and lottery dispensers, the candy rack on
the customer face and the cigarette rack overhead -- and every pixel of
the wrappers and packs.

Zoo 1.7.0, `counter` FORM ``service``. The walker's 1990s photograph of the
store's service island (docs/SET_DRESSING_REFERENCES.md, "The walker's
convenience store references", 2026-09-15): "a long white laminate SERVICE
COUNTER ... edged with a black-and-white CHECKERBOARD trim band at the top
and bottom. Inside the U: the register stations (beige 1990s registers with
pole displays) and the cigarette rack ... The counter front is a candy rack
-- tiered shelves of brightly wrapped bars facing the customer." And from
the modern stores: "the cigarette rack -- a wall unit of shelves of packs
faced out in their brand colours, a lit header panel ... scratch-off lottery
dispensers on the counter." Asked for by name 2026-09-27: "start with the
service counter, cigarette overhead and candy rack".

WHY A FORM AND NOT A SPECIES. Deli Counter's `gas_station` preset already
stands a `register_counter` volume (6.0 x 0.9 x 1.1) that `intent` resolves
to `counter` by keyword, and `kit.honour_dressing` carries a slot's ``form``
to the recipe. `bar` (0.92.0) is the precedent: the club's bar is the same
counter with a fit-out. This is the store's.

WHAT IS BUILT, in the recipe's frame (metres, Z up, -Y the CUSTOMER side,
+Y the service side, +X to the customer's right):

  * TRIM: two bands on the customer face, one under the top's overhang and
    one above the kick, painted with a tiling black-and-white checker
    (`checker_canvas`, a 2 x 2 image; the UVs repeat it at `CHECK` metres a
    square). Real geometry, 6 mm proud of the body, so the bands read in
    profile and not only in paint.
  * REGISTERS at every ``ATT_register`` station the recipe reserves, the
    same beige body, screen and key plate `back_bar_forms.counter_fitout`
    stands on the club's bar -- one register, one shape, whatever the
    counter is selling.
  * LOTTERY DISPENSERS beside each register on the customer edge of the
    top: up to three red acrylic towers with a painted ticket face, the
    "scratch-off lottery dispensers on the counter" the walker saw.
  * THE CANDY RACK on the customer face between the bands: `TIERS` shelves,
    the lowest proudest, each carrying a painted strip of wrapped bars
    faced out (`candy_brands`, `_bar`). The strip's UVs repeat one metre
    of art along the run, so a 6 m counter paints 350 px, not 2,100.
  * THE CIGARETTE RACK OVERHEAD: two chrome posts up from the service edge
    of the top carrying a black rack, `RACK_ROWS` rows of packs faced out
    to the CUSTOMER over the clerk's head (`cigarette_brands`, the pull-knob
    machine's own `_pack`), under a header strip lit faintly at the
    machine's measured strength (`M_Counter_CigRack_<art>_Face`, so Lux's
    power cut takes it). Posts and not a ceiling hanger, because the
    recipe does not know the room's height and a rack that stands on its
    counter is complete in any room.

THE MODULE'S FIT BOUNDS STAY THE COUNTER'S. Everything on or above the top
is returned as ``on_top`` and the recipe reports it as ``dressing_objects``,
the rule that lets a register stand on a desk (0.92.0). The trim and the
rack tiers are ``inside``: within the slot's box, proud of the body but
inside the top's overhang.

NO TWO FACES SHARE A PLANE among the fit-out's own primitives
(`prims.coincident_pairs` is empty), and every part that meets the counter
body is buried `BURY` into it. The body itself is bmesh, not a primitive,
and is not in that check; what the test holds is the fit-out.

THE BUDGET is `TRI_BUDGET` for the whole fit-out, set before the layout was
drawn: two registers, six dispensers, two bands, three tiers with their
strips, two posts, a rack and its two art faces come to a few hundred
triangles, and the counter's own budget (7,000 with `bar_dense`) is not
moved.
"""
from __future__ import annotations

import re
import zlib

from . import candy_brands as CANDY
from . import cigarette_brands as CB
from . import cigarette_forms as CF
from . import pixel_type as pt
from . import prims as P
from . import counter_register as CREG
from .back_bar_forms import REG_D, REG_H, REG_SCREEN_H, REG_W
from .vending_forms import Canvas

#: Burial at every joint with the counter, and between the fit-out's own
#: parts that stand on each other. 3x the 2 mm coplanar window.
BURY = 0.006
#: The whole fit-out, both lists. A cap on drift, not a frame cost.
TRI_BUDGET = 1400

# --- the trim -----------------------------------------------------------------
#: A checker square, metres; two rows per band. 1.8.0: 0.045 -> 0.05, so a
#: whole number of squares (20) fits the painted atlas's one-metre repeat --
#: the trim now shares the candy's image, and a non-integer count would put a
#: half square at every metre along the counter.
CHECK = 0.05
TRIM_H = 2 * CHECK
TRIM_T = 0.006           # proud of the body's face
TRIM_INSET = 0.02        # short of the top's ends

# --- the candy rack -------------------------------------------------------------
TIERS = 3
TIER_LIP = 0.02          # a shelf's thickness
#: The tiers' reach is the top's overhang (see `fitout`), not a constant.
BAR_W = 0.140            # a wrapped bar, faced out
BAR_H = 0.048
BAR_GAP = 0.010
#: The art repeats every `ART_REPEAT_M` along the run.
ART_REPEAT_M = 1.0
#: px per metre: a 2.5 mm pixel, a bar 56 px wide, a checker square 20 px.
#: 1.8.0: 350 -> 400 so a square is a whole number of pixels.
CANDY_TEXEL = 400

# --- the lottery dispensers -----------------------------------------------------
LOTTO_W = 0.11
LOTTO_D = 0.09
LOTTO_H = 0.28
LOTTO_PITCH = 0.13
LOTTO_MAX = 3
LOTTO_IN = 0.07          # from the top's customer edge

# --- the cigarette rack overhead ------------------------------------------------
POST_R = 0.016
POST_H = 1.30            # above the top: the rack's top at h + POST_H
POST_IN = 0.06           # posts in from the service edge
RACK_H = 0.42
RACK_D = 0.30
RACK_W_MAX = 2.4
RACK_W_MIN = 0.6
RACK_ROWS = 3
HEADER_FRAC = 0.24       # of the rack's height, the lit strip on top
RACK_SET = 0.012         # the art face behind the rack's front edge
PACK_PITCH = CF.PACK_PITCH
RACK_TEXEL = CF.TEXEL

BLACK = (0.015, 0.015, 0.016)
CHROME = (0.66, 0.66, 0.66)
WHITE = (0.86, 0.85, 0.82)
LOTTO_RED = (0.72, 0.10, 0.10)
#: Each primitive's ``mat`` key -> (its colour, its surface kind).
#:
#: 1.8.0: ONE MATERIAL PER KIND, the colour in the vertex. 1.7.0 shipped these
#: as six materials and the counter as 15 submissions for 14 materials, five
#: of which differed from another in nothing but colour -- the thing
#: CLAUDE.md's draw-call rule names first. Now the recipe builds one
#: material per KIND (`KIND_BASE` is its tint) and multiplies each part's
#: colour, divided by that base, into its `Wear` attribute
#: (`geometry.tint_wear`); `merge.pack_by_material` then packs every part of
#: a kind into one mesh. The posts moved from bare to painted metal to share
#: the rack's kind: painted silver where 1.7.0 had chrome, on two 16 mm posts.
CHROME_PAINT = (0.62, 0.62, 0.63)
MATERIALS = {
    "black": (BLACK, "metal_painted"),
    "chrome": (CHROME_PAINT, "metal_painted"),
    "beige": ((0.60, 0.57, 0.48), "plastic"),
    "key_dark": ((0.16, 0.16, 0.17), "plastic"),
    "lotto": (LOTTO_RED, "plastic"),
    "shelf": (WHITE, "laminate"),
}
#: The one material each kind is built with. Laminate keeps the counter's
#: white as its tint, so the body, top, kick and shelves are `WHITE` times a
#: vertex factor; plastic and painted metal are neutral and take their whole
#: colour from the vertex.
KIND_BASE = {"laminate": WHITE, "plastic": (1.0, 1.0, 1.0), "metal_painted": (1.0, 1.0, 1.0)}
#: The counter's own parts, as factors on `KIND_BASE["laminate"]`, chosen to
#: land where 1.7.0's separate materials did -- the merge is not a restyle.
#: MEASURED by a headless Godot readback of both builds: 1.7.0's top was
#: `laminate_d3d0c9` (0.96 of the body, kept), its staff shelves the body's
#: own white (1.0, kept), and its kick base the SLOT's `drywall` skin at a
#: wear mean of 0.73 -- a light grey, not a design; 0.80 of the white
#: laminate keeps it light rather than turning it black, which would have
#: been a look change nobody asked for.
BODY_TINT = {"Top": (0.96, 0.96, 0.96), "Base": (0.80, 0.80, 0.80), "Body": (1.0, 1.0, 1.0),
             "Shelf": (1.0, 1.0, 1.0)}


def vertex_tint(mat_key):
    """``(kind, factor)``: the material a ``mat`` key is built with, and the
    colour its parts multiply into their `Wear` to reach `MATERIALS`'s."""
    rgb, kind = MATERIALS[mat_key]
    base = KIND_BASE[kind]
    return kind, tuple(c / b for c, b in zip(rgb, base))
_VARIANT = re.compile(r"_n\d+(?=_|$)")


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def resolve(plan_):
    """``(key, variant)``: the stem without its variant, and the variant --
    what the wrappers, the packs and the header are drawn from."""
    params = plan_.get("params") or {}
    module = plan_.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    key = _VARIANT.sub("", module.get("stem") or "") or "counter_service"
    return key, variant


# --- the geometry ------------------------------------------------------------------

def rack_width(w):
    """The rack is shorter than its counter by 0.6 m, capped at `RACK_W_MAX`
    and never under `RACK_W_MIN` -- a 0.8 m counter carries a 0.6 m rack,
    not a 1.2 m one hanging past both ends."""
    return max(RACK_W_MIN, min(RACK_W_MAX, w - 0.6))


def rack_centre(w, rw, regs, top_w):
    """Where the rack stands along the counter: centred when its posts
    clear every register station, else the nearest centre that does. A
    post through a register measured as one coincident plane (both stand
    on the top at 6.0 x 0.9) and would have been a post through a register.
    Returns ``(cx, rw)``; the width shrinks in 0.1 m steps if no centre
    clears at the full width."""
    clear = REG_W / 2.0 + POST_R + 0.03
    limit = top_w / 2.0 - 0.03
    while rw >= RACK_W_MIN:
        half = rw / 2.0 - 0.05
        cands = [0.0]
        step = 0.25
        k = 1
        while step * k + rw / 2.0 <= limit:
            cands += [step * k, -step * k]
            k += 1
        for cx in cands:
            if all(abs(cx + s * half - ax) >= clear for s in (-1, 1) for ax in regs):
                return cx, rw
        rw = round(rw - 0.1, 3)
    # A counter too short for the narrowest rack to clear its register --
    # 0.8 m, a kiosk -- gets no rack, not a post through the till.
    return None, 0.0


def fitout(w, d, h, attachments, top_w, face_y, base_h, top_t, key="counter_service",
           variant=0):
    """``(inside, on_top, facts)``: the primitive lists and where things
    landed. ``face_y`` is the body's customer face, ``base_h`` the kick's
    height, ``top_t`` the top's thickness -- the recipe's own numbers."""
    inside, on_top = [], []
    x0, x1 = -top_w / 2.0 + TRIM_INSET, top_w / 2.0 - TRIM_INSET
    facts = {"key": key, "variant": variant}

    # --- the trim bands, proud of the face, buried into the body ---------------
    zt1 = h - top_t - 0.004
    zt0 = zt1 - TRIM_H
    zb0 = base_h + 0.004
    zb1 = zb0 + TRIM_H
    for name, (za, zb) in (("top", (zt0, zt1)), ("bottom", (zb0, zb1))):
        # one object each (a painted part is built on its own), so named apart
        p = P.box("Counter_Trim_" + name, "checker", (x0, face_y - TRIM_T, za), (x1, face_y + BURY, zb))
        # PAINTED, with UVs from x and z: (u, v) = (x * su + ou, z * sv + ov).
        # The checker image is two squares across, so one UV unit is 2 * CHECK
        # metres either way, and the band's bottom edge is a row boundary.
        p["paint"] = "checker"
        # BAND-LOCAL: u repeats every `ART_REPEAT_M` (the atlas is one metre
        # wide, 20 squares), v runs 0..1 across the band; `atlas_v` maps v
        # into the checker's rows of the painted atlas.
        p["uv_xz"] = (1.0 / ART_REPEAT_M, -x0 / ART_REPEAT_M, 1.0 / TRIM_H, -za / TRIM_H)
        inside.append(p)
    facts["trim"] = {"top": (zt0, zt1), "bottom": (zb0, zb1)}

    # --- the candy rack between the bands -----------------------------------------
    span0, span1 = zb1 + 0.012, zt0 - 0.012
    tier_h = (span1 - span0) / TIERS
    # THE RACK STAYS INSIDE THE SLOT. A walk-into solid must sit inside its
    # collision, and the module's collision is the counter's box, so the
    # tiers reach no further than the top's overhang: the lowest to 4 mm
    # short of the slot's front, the others stepped back evenly. On Deli
    # Counter's 0.9 m counter that is 63 mm -- a shallow rack under the
    # overhang, which is what a counter-front rack is.
    reach_max = (d / 2.0 + face_y) - 0.004
    tiers = []
    for k in range(TIERS):
        reach = reach_max * (TIERS - k) / TIERS                 # the lowest reaches most
        z_shelf = span0 + (TIERS - 1 - k) * tier_h              # tier 0 is the top
        yf = face_y - reach
        # the shelf lip: 3 mm short of the trim's ends so no end plane is shared
        inside.append(P.box("Counter_CandyTier", "shelf",
                            (x0 + 0.003, yf, z_shelf), (x1 - 0.003, face_y + BURY, z_shelf + TIER_LIP)))
        # the strip of bars standing on it, leaning on the face: its front a
        # plane of its own, its back buried a different depth than the shelf's
        art_z0 = z_shelf + TIER_LIP - 0.004
        art_z1 = z_shelf + tier_h - 0.030
        art_y0 = yf + 0.018
        p = P.box("Counter_CandyArt_T%d" % (k + 1), "candy", (x0 + 0.006, art_y0, art_z0),
                  (x1 - 0.006, face_y + BURY / 2.0, art_z1))
        # BAND-LOCAL like the trim: u repeats every `ART_REPEAT_M`, v runs
        # 0..1 up the strip, and `atlas_v` maps it into this tier's rows
        p["paint"] = "candy_%d" % k
        p["uv_xz"] = (1.0 / ART_REPEAT_M, -(x0 + 0.006) / ART_REPEAT_M,
                      1.0 / (art_z1 - art_z0), -art_z0 / (art_z1 - art_z0))
        inside.append(p)
        tiers.append({"z": z_shelf, "reach": reach, "art": (art_z0, art_z1, art_y0)})
    facts["tiers"] = tiers

    # --- the registers and the lottery beside them --------------------------------
    regs = []
    ry = d / 2.0 - REG_D / 2.0 - 0.06
    stations = sorted((ax, name) for name, (ax, _ay, _az) in attachments.items()
                      if name.startswith("ATT_register"))
    for ax, _name in stations:
        regs.append(ax)
        # `counter_register.station` (1.16.0): the green display lit, the
        # pole display, the keys at the clerk's end. Its windows carry
        # ``uvs`` and ``mat`` ``vfd``; the recipe builds them on their image.
        solid, lit = CREG.station(ax, ry, h)
        on_top.extend(solid + lit)
    lottos = []
    ly0 = -d / 2.0 + LOTTO_IN
    for ax in regs:
        for i in range(LOTTO_MAX):
            lx = ax + REG_W / 2.0 + 0.10 + i * LOTTO_PITCH
            if lx + LOTTO_W / 2.0 > top_w / 2.0 - 0.03:
                break
            if any(abs(lx - bx) < REG_W / 2.0 + LOTTO_W / 2.0 + 0.02 for bx in regs if bx != ax):
                break
            on_top.append(P.box("Counter_Lottery", "lotto",
                                (lx - LOTTO_W / 2.0, ly0, h - 0.004 - 0.002 * i),
                                (lx + LOTTO_W / 2.0, ly0 + LOTTO_D, h + LOTTO_H - 0.01 * i)))
            lottos.append(lx)
    facts["registers"] = regs
    facts["lottery"] = lottos

    # --- the cigarette rack overhead ------------------------------------------------
    cx, rw = rack_centre(w, rack_width(w), regs, top_w)
    if cx is None:
        facts["rack"] = None
        return inside, on_top, facts
    py = d / 2.0 - POST_IN
    z_top = h + POST_H
    z_rack0 = z_top - RACK_H
    for s in (-1, 1):
        px = cx + s * (rw / 2.0 - 0.05)
        # the post's top is buried into the rack, not flush with its bottom
        on_top.append(P.cyl("Counter_CigPost", "chrome", (px, py), POST_R, h - 0.004,
                            z_rack0 + BURY, segments=8))
    ry0, ry1 = py - RACK_D * 0.55, py + RACK_D * 0.45
    on_top.append(P.box("Counter_CigRack", "black", (cx - rw / 2.0, ry0, z_rack0), (cx + rw / 2.0, ry1, z_top)))
    # the art face: a thin slab set into the rack's customer face, its front
    # `RACK_SET` behind the rack's front plane, painted rows under a lit header
    ax0, ax1 = cx - rw / 2.0 + 0.02, cx + rw / 2.0 - 0.02
    az0, az1 = z_rack0 + 0.02, z_top - 0.02
    zh = az1 - (az1 - az0) * HEADER_FRAC
    on_top.append(rack_art_prim(ax0, ax1, az0, az1, zh, ry0 - RACK_SET + 0.004, ry0 + BURY))
    facts["rack"] = {"w": rw, "cx": cx, "z": (z_rack0, z_top), "y": (ry0, ry1), "art": (ax0, ax1, az0, az1),
                     "header_z": zh, "n_packs": max(6, int((ax1 - ax0 - 0.01) // PACK_PITCH))}
    return inside, on_top, facts


def rack_art_prim(x0, x1, z0, z1, zh, y_front, y_back):
    """The rack's art slab: a box whose front is two quads split at the
    header's bottom ``zh`` -- the header lit, the rows painted -- with UVs
    mapping the slab's front edge to edge onto the art, the same shape as
    `cigarette_forms.display_prim`."""
    verts = [(x0, y_front, z0), (x1, y_front, z0), (x1, y_front, zh), (x0, y_front, zh),
             (x1, y_front, z1), (x0, y_front, z1),
             (x0, y_back, z0), (x1, y_back, z0), (x1, y_back, z1), (x0, y_back, z1)]
    faces = [(0, 1, 2, 3), (3, 2, 4, 5), (6, 9, 8, 7), (0, 6, 7, 1), (5, 4, 8, 9),
             (6, 0, 3, 5, 9), (7, 8, 4, 2, 1)]
    p = P.mesh("Counter_CigRackArt", "rack_art", verts, faces)
    p["face_mats"] = ["paint", "lit", "paint", "paint", "paint", "paint", "paint"]

    def uv(i):
        x, _y, z = verts[i]
        return ((x - x0) / (x1 - x0), (z - z0) / (z1 - z0))
    p["uvs"] = [tuple(("art",) + uv(i) for i in f) if k < 2 else tuple(("dark", 0.5, 0.5) for _ in f)
                for k, f in enumerate(faces)]
    return p


# --- the art ---------------------------------------------------------------------------

#: A checker square's pixels in the atlas: `CHECK` at `CANDY_TEXEL`, exact.
CHECKER_PX = int(round(CHECK * CANDY_TEXEL))
CHECK_LIGHT = (240, 238, 232)
CHECK_DARK = (14, 14, 14)


def _checker_band(c, y0):
    """Two rows of checker squares, `CHECKER_PX` each, across the whole
    width of ``c`` from row ``y0``. The width is a whole number of squares
    (`paint_atlas` asserts it), so the pattern meets itself at the repeat."""
    n = CHECKER_PX
    for row in range(2):
        for col in range(c.w // n):
            dark = (row + col) % 2 == 1
            c.rect(col * n, y0 + row * n, (col + 1) * n, y0 + (row + 1) * n,
                   CHECK_DARK if dark else CHECK_LIGHT)


def paint_atlas(tiers, key, variant):
    """ONE image for every painted part of the counter but the rack: the
    candy tiers and the checker band stacked top to bottom, one metre of
    art wide. Zoo 1.8.0; 1.7.0 painted four images into four materials.

    The UVs repeat along the counter (u), which is why the parts can share
    a REPEAT sampler: every band is exactly one period wide. Across a band
    (v) nothing repeats -- each part's v is 0..1 of its own band, which
    `atlas_v` maps into the band's rows inset half a pixel, so the nearest
    sample on a band's edge never reads the neighbouring band.

    ``{canvas, size, name, bands: {band: (y0, y1)}, candy: {tier: brands}}``;
    rows are pixel rows, 0 at the TOP, as `Canvas` draws them."""
    W = int(round(ART_REPEAT_M * CANDY_TEXEL))
    assert W % CHECKER_PX == 0 and (W // CHECKER_PX) % 2 == 0, (W, CHECKER_PX)
    tiles = candy_art(tiers, key, variant)
    heights = [tiles[k]["size"][1] for k in sorted(tiles)]
    H = sum(heights) + 2 * CHECKER_PX
    c = Canvas(W, H, CHECK_LIGHT)
    bands, y = {}, 0
    for k in sorted(tiles):
        c.paste(tiles[k]["canvas"], 0, y)
        bands["candy_%d" % k] = (y, y + tiles[k]["size"][1])
        y += tiles[k]["size"][1]
    _checker_band(c, y)
    bands["checker"] = (y, y + 2 * CHECKER_PX)
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H), "bands": bands,
            "candy": {k: tiles[k]["brands"] for k in tiles},
            "name": f"svcpaint_{key}_v{variant % 4}_{W}x{H}_{digest:08x}"}


def atlas_v(band, size, v_local):
    """A band-local ``v`` (0 at the band's bottom, 1 at its top) as a UV
    ``v`` in the atlas (0 at the image's bottom, glTF's and Blender's
    convention), inset half a pixel at each edge of the band."""
    y0, y1 = band
    H = size[1]
    lo = 1.0 - (y1 - 0.5) / H          # the band's bottom row, in UV
    hi = 1.0 - (y0 + 0.5) / H          # its top row
    return lo + (hi - lo) * v_local


def _rgb(h):
    return CANDY.hex_rgb(h)


def _bar(c, brand, x0, y0, bw, bh):
    """One wrapped bar, faced out: the body, its design in the second
    colour, the short name, and a foil glint along the top edge."""
    b = CANDY.BY_ID[brand]
    body, second, ink = _rgb(b["body"]), _rgb(b["second"]), _rgb(b["ink"])
    c.rect(x0, y0, x0 + bw, y0 + bh, body)
    design = b["design"]
    if design == "band":
        c.rect(x0, y0 + bh * 35 // 100, x0 + bw, y0 + bh * 65 // 100, second)
    elif design == "stripe":
        c.rect(x0 + bw * 8 // 100, y0, x0 + bw * 20 // 100, y0 + bh, second)
        c.rect(x0 + bw * 80 // 100, y0, x0 + bw * 92 // 100, y0 + bh, second)
    elif design == "split":
        c.rect(x0, y0, x0 + bw // 2, y0 + bh, second)
    elif design == "diag":
        for yy in range(bh):
            xx = x0 + (yy * bw) // max(1, bh)
            c.rect(xx, y0 + yy, xx + max(2, bw // 10), y0 + yy + 1, second)
    else:
        raise ValueError(f"bar {brand}: unknown design {design!r}")
    m = pt.trim(pt.render(b["short"], 1))
    tx = x0 + (bw - len(m[0])) // 2
    ty = y0 + (bh - len(m)) // 2
    # the name sits on a plaque of the body colour so it reads over any design
    c.rect(tx - 2, ty - 1, tx + len(m[0]) + 2, ty + len(m) + 1, body)
    c.mask(m, tx, ty, ink)
    c.rect(x0, y0, x0 + bw, y0 + 1, tuple(min(255, v + 60) for v in body))


def candy_art(tiers, key, variant):
    """One canvas per tier, `ART_REPEAT_M` wide, of bars faced out with a
    dark shelf shadow under them. ``{tier: {canvas, name, brands}}``."""
    out = {}
    order = sorted(CANDY.BAR_IDS, key=lambda i: (_h(key, i), i))
    per = int(ART_REPEAT_M // (BAR_W + BAR_GAP))
    bw = int(BAR_W * CANDY_TEXEL)
    W = int(ART_REPEAT_M * CANDY_TEXEL)
    for k, t in enumerate(tiers):
        z0, z1, _y = t["art"]
        H = max(8, int(round((z1 - z0) * CANDY_TEXEL)))
        c = Canvas(W, H, (28, 26, 24))
        bh = min(int(BAR_H * CANDY_TEXEL), H - 6)
        pitch = W / per
        brands = [order[_h(key, variant, k, i) % len(order)] for i in range(per)]
        # the tier leads with a different brand each row so the rack is a
        # mix rather than three rows of one bar
        brands[0] = order[(k + variant) % len(order)]
        for i in range(per):
            bx = int(pitch * i + (pitch - bw) / 2.0)
            by = H - bh - 3
            c.rect(bx + 2, by + 2, bx + bw + 2, by + bh + 2, (10, 10, 10))
            _bar(c, brands[i], bx, by, bw, bh)
        digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
        out[k] = {"canvas": c, "size": (W, H), "brands": brands,
                  "name": f"candy_{key}_t{k}_v{variant % 4}_{W}x{H}_{digest:08x}"}
    return out


def rack_art(facts, key, variant):
    """The cigarette rack's raster: a lit header carrying one brand's ad
    and `RACK_ROWS` rows of packs faced out. ``{canvas, size, name,
    header, rows, said}``; row 0 at the TOP."""
    ax0, ax1, az0, az1 = facts["rack"]["art"]
    zh = facts["rack"]["header_z"]
    W = int(round((ax1 - ax0) * RACK_TEXEL))
    H = int(round((az1 - az0) * RACK_TEXEL))
    c = Canvas(W, H + 6, (12, 12, 12))

    def py(z):
        return int(round((az1 - z) * RACK_TEXEL))
    order = CF.lineup(key)
    header = order[variant % len(order)]
    others = [b for b in order if b != header]
    said = list(CF._ad(c, header, 0, 0, W, py(zh), with_cards=False))
    n = facts["rack"]["n_packs"]
    row_h = (H - py(zh)) / RACK_ROWS
    rows = []
    for r in range(RACK_ROWS):
        ry0 = int(py(zh) + row_h * r)
        ry1 = int(py(zh) + row_h * (r + 1))
        pool = [header] + others if r == 0 else others
        brands = [pool[_h(key, variant, "rack", r, k) % len(pool)] for k in range(n)]
        if r == 0:
            brands[0] = header
        CF._row(c, brands, 0, ry0, W, ry1, n, False, key)
        rows.append(brands)
    c.rect(0, H + 1, 4, H + 5, (12, 12, 12))
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H + 6), "header": header, "rows": rows, "said": said,
            "dark": (0, H + 1, 4, H + 5),
            "name": f"cigrack_{header}_v{variant % 4}_{W}x{H + 6}_{digest:08x}"}


def art_uv(rect, size):
    return CF.uv_rect(rect, size)
