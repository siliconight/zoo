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
from . import prims as P
from . import counter_lottery as CL
from . import paint as PT
from . import smooth_type as ST
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
#: px per metre: a 1.25 mm pixel, a bar 112 px wide, a checker square 40 px.
#: 1.8.0: 350 -> 400 so a square is a whole number of pixels. 1.50.0: 800,
#: the real look -- a wrapper's name in a smooth face needs the pixels, and
#: the image is sampled with filtering. Twice the density is four times the
#: image (800 px wide where it was 400); Level Factory 0.128.0 ships a
#: filtered texture VRAM-compressed.
CANDY_TEXEL = 800
#: Rows between the atlas's bands, and half as many above the first and
#: under the last, each filled with the neighbouring band's own edge row. A
#: filtered, mip-mapped sample at a band's edge reads past it; without these
#: it reads the next band (and, at the image's top and foot, wraps to the
#: far one, because the sampler repeats).
BAND_GUTTER = 16

# --- the lottery dispensers -----------------------------------------------------
LOTTO_W = CL.W
LOTTO_D = CL.D
LOTTO_H = CL.H
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
    "shelf": (WHITE, "laminate"),
}
#: The one material each kind is built with. Laminate keeps the counter's
#: white as its tint, so the body, top, kick and shelves are `WHITE` times a
#: vertex factor; plastic and painted metal are neutral and take their whole
#: colour from the vertex.
#:
#: 1.47.0: there is no `plastic` here any more. The tills' bodies (1.46.0)
#: and the lottery dispensers (1.47.0) were its only users and both are
#: painted into `counter_register.paint_art` now, so the counter makes one
#: draw fewer for that kind.
KIND_BASE = {"laminate": WHITE, "metal_painted": (1.0, 1.0, 1.0)}
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
            # `counter_lottery` (1.47.0): an acrylic case on a black foot,
            # a different game in each, painted into the till's image
            on_top.extend(CL.dispenser(lx, ly0, h, i, CREG.PAINT))
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
    G = BAND_GUTTER
    H = sum(heights) + 2 * CHECKER_PX + G * (len(heights) + 1)
    c = Canvas(W, H, CHECK_LIGHT)
    bands, y = {}, G // 2
    for k in sorted(tiles):
        c.paste(tiles[k]["canvas"], 0, y)
        bands["candy_%d" % k] = (y, y + tiles[k]["size"][1])
        y += tiles[k]["size"][1] + G
    _checker_band(c, y)
    bands["checker"] = (y, y + 2 * CHECKER_PX)
    # the gutters (1.50.0): above a band its first row, under it its last
    stride = W * 3
    for y0, y1 in bands.values():
        top = bytes(c.buf[y0 * stride:(y0 + 1) * stride])
        foot = bytes(c.buf[(y1 - 1) * stride:y1 * stride])
        for g in range(1, G // 2 + 1):
            if y0 - g >= 0:
                c.buf[(y0 - g) * stride:(y0 - g + 1) * stride] = top
            if y1 - 1 + g < H:
                c.buf[(y1 - 1 + g) * stride:(y1 + g) * stride] = foot
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


def _lift(rgb, by):
    return tuple(max(0.0, min(255.0, v + by)) for v in rgb)


def _bar(im, brand, x0, y0, bw, bh):
    """One wrapped bar, faced out (1.50.0, painted): the wrapper graded as
    foil is, its design in the second colour, the short name in the BRAND's
    own face on a plaque of the body colour, the fin crimped flat at each
    end, and the foil's light along its top edge and in one streak."""
    b = CANDY.BY_ID[brand]
    body, second, ink = _rgb(b["body"]), _rgb(b["second"]), _rgb(b["ink"])
    box = (x0, y0, x0 + bw, y0 + bh)
    im.vgrad(box, _lift(body, 14), _lift(body, -16))
    design = b["design"]
    if design == "band":
        im.rect((x0, y0 + bh * 0.35, x0 + bw, y0 + bh * 0.65), second)
    elif design == "stripe":
        im.rect((x0 + bw * 0.08, y0, x0 + bw * 0.20, y0 + bh), second)
        im.rect((x0 + bw * 0.80, y0, x0 + bw * 0.92, y0 + bh), second)
    elif design == "split":
        im.rect((x0, y0, x0 + bw / 2.0, y0 + bh), second)
    elif design == "diag":
        for yy in range(int(bh)):
            xx = x0 + (yy * bw) / max(1, bh)
            im.rect((xx, y0 + yy, xx + max(3, bw // 10), y0 + yy + 1), second)
    else:
        raise ValueError(f"bar {brand}: unknown design {design!r}")
    # the name sits on a plaque of the body colour so it reads over any design
    plaque = (x0 + bw * 0.17, y0 + bh * 0.16, x0 + bw * 0.83, y0 + bh * 0.84)
    im.rrect(plaque, bh * 0.12, body)
    im.text(b["short"], (plaque[0] + 3, plaque[1] + 2, plaque[2] - 3, plaque[3] - 2), ink,
            CANDY.FACE.get(brand, "highway_bold"))
    # the fin at each end: pressed flat, lighter, ribbed by the crimper
    fin = max(4.0, bw * 0.06)
    for fx in (x0, x0 + bw - fin):
        im.rect((fx, y0, fx + fin, y0 + bh), (255, 255, 255), 0.16)
        for x in range(int(fx), int(fx + fin), 2):
            im.rect((x, y0, x + 1, y0 + bh), (0, 0, 0), 0.16)
    # the foil: the room along its top edge and in one streak
    im.rect((x0, y0, x0 + bw, y0 + 1.5), (255, 255, 255), 0.4)
    im.gloss(box, 0.08, 0.3, 0.3, 0.12)


def tier_brands(order, k, variant, per):
    """Tier ``k``'s bars, ``per`` of them: BOXES OF ONE BRAND, two facings
    each, walking the lineup three brands a tier so three tiers show nine
    slots of it and lead with three different bars.

    Until 1.50.0 every slot drew its own brand. A counter rack is stocked by
    the display box, and a box holds one bar."""
    return [order[(3 * k + variant + i // 2) % len(order)] for i in range(per)]


def candy_art(tiers, key, variant):
    """One canvas per tier, `ART_REPEAT_M` wide, of bars faced out, each
    with its shadow on the backing, the tier above's shade across the head
    of the strip, and the shop's own talker. ``{tier: {canvas, name,
    brands, said, unset}}``."""
    out = {}
    order = sorted(CANDY.BAR_IDS, key=lambda i: (_h(key, i), i))
    per = int(ART_REPEAT_M // (BAR_W + BAR_GAP))
    bw = int(BAR_W * CANDY_TEXEL)
    W = int(ART_REPEAT_M * CANDY_TEXEL)
    for k, t in enumerate(tiers):
        z0, z1, _y = t["art"]
        H = max(8, int(round((z1 - z0) * CANDY_TEXEL)))
        im = PT.Img(W, H, (28, 26, 24))
        bh = min(int(BAR_H * CANDY_TEXEL), H - 6)
        pitch = W / per
        brands = tier_brands(order, k, variant, per)
        by = H - bh - 3
        # the tier above keeps the head of this strip in shade
        im.vgrad((0, 0, W, max(1, by - 2)), (12, 11, 10), (28, 26, 24))
        said = []
        # THE DISPLAY BOX'S HEADER. A box of bars ships with its lid scored
        # to fold up behind them as a card: the brand's name over its own
        # bars, which is what reads from the door when a wrapper does not.
        # One a box -- two facings -- in the brand's own face and colours,
        # a little in the tier's shade.
        head_h = min(int(0.070 * CANDY_TEXEL), by - 8)
        if head_h >= 24:
            for i in range(0, per - 1, 2):
                b = CANDY.BY_ID[brands[i]]
                body = _rgb(b["body"])
                hx0 = int(pitch * i + (pitch - bw) / 2.0)
                hx1 = int(pitch * (i + 1) + (pitch - bw) / 2.0) + bw
                card = (hx0, by - 2 - head_h, hx1, by - 2)
                im.rrect((card[0] + 3, card[1] + 3, card[2] + 3, card[3] + 3), 3, (0, 0, 0), 0.5)
                im.rrect(card, 3, body)
                im.vgrad((card[0] + 2, card[1] + 2, card[2] - 2, card[3] - 2), _lift(body, -6), _lift(body, -34))
                im.rect((card[0] + 4, card[3] - 6, card[2] - 4, card[3] - 3), _rgb(b["second"]))
                name = " ".join(b["logo"])
                if im.text(name, (card[0] + 8, card[1] + 5, card[2] - 8, card[3] - 9), _rgb(b["ink"]),
                           CANDY.FACE.get(brands[i], "highway_bold")) is not None:
                    said.append(name)
        for i in range(per):
            bx = int(pitch * i + (pitch - bw) / 2.0)
            im.rrect((bx + 3, by + 3, bx + bw + 4, by + bh + 3), 2, (0, 0, 0), 0.6)
            _bar(im, brands[i], bx, by, bw, bh)
        # THE SHOP'S TALKER, over the first box of the top tier: a yellow tag
        # in the shop's own face. One a metre, on one tier -- a price is said
        # once, where the eye lands first.
        tag_h = int(0.030 * CANDY_TEXEL)
        if k == 0 and by - 10 - max(0, head_h) >= tag_h:
            tx0, ty0 = int(pitch * 0.5 - 0.055 * CANDY_TEXEL), max(2, by - 8 - max(0, head_h) - tag_h)
            tag = (tx0, ty0, tx0 + int(0.11 * CANDY_TEXEL), ty0 + tag_h)
            im.rrect((tag[0] + 2, tag[1] + 2, tag[2] + 2, tag[3] + 2), 3, (0, 0, 0), 0.5)
            im.rrect(tag, 3, (248, 220, 60))
            if im.text(CANDY.SHELF_TALKER, (tag[0] + 4, tag[1] + 3, tag[2] - 4, tag[3] - 3), (150, 20, 16),
                       ST.owned("shop")) is not None:
                said.append(CANDY.SHELF_TALKER)
        c = im.to_canvas()
        digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
        out[k] = {"canvas": c, "size": (W, H), "brands": brands, "said": said, "unset": list(im.unset),
                  "name": f"candy_{key}_t{k}_v{variant % 4}_{W}x{H}_{digest:08x}"}
    return out


def rack_facings(header, others, n, key, variant, r):
    """Row ``r`` of the rack, ``n`` packs: BLOCKS OF ONE BRAND, two to four
    facings wide, walking the lineup -- the top row from the header's brand,
    each row below from further along it.

    Until 1.48.0 every slot drew its own brand, and a rack read as confetti.
    A clerk stocks a rack by the carton: a brand has a run of pushers side by
    side, so the eye finds REDS as a red block and not as forty single packs.
    The run lengths are seeded; which brand follows which is the lineup's.
    """
    pool = ([header] + others) if r == 0 else (others[(4 * r) % len(others):] + others[:(4 * r) % len(others)])
    out, i = [], 0
    while len(out) < n:
        out += [pool[i % len(pool)]] * (2 + _h(key, variant, "rack", r, i) % 3)
        i += 1
    return out[:n]


def rack_art(facts, key, variant):
    """The cigarette rack's raster: a lit header carrying one brand's ad
    and `RACK_ROWS` rows of packs faced out. ``{canvas, size, name,
    header, rows, said}``; row 0 at the TOP."""
    ax0, ax1, az0, az1 = facts["rack"]["art"]
    zh = facts["rack"]["header_z"]
    W = int(round((ax1 - ax0) * RACK_TEXEL))
    H = int(round((az1 - az0) * RACK_TEXEL))
    # 1.48.0: painted with `paint.Img` and smooth type, sampled with
    # filtering (`cigarette_forms`' painters); the band under the art that
    # the slab's other faces show is `CF.DARK_ROWS` deep so a filtered,
    # mip-mapped sample of its middle is still dark
    im = PT.Img(W, H + CF.DARK_ROWS, (12, 12, 12))

    def py(z):
        return int(round((az1 - z) * RACK_TEXEL))
    order = CF.lineup(key)
    header = order[variant % len(order)]
    others = [b for b in order if b != header]
    said = list(CF._ad(im, header, 0, 0, W, py(zh), with_cards=False))
    n = facts["rack"]["n_packs"]
    row_h = (H - py(zh)) / RACK_ROWS
    rows = []
    for r in range(RACK_ROWS):
        ry0 = int(py(zh) + row_h * r)
        ry1 = int(py(zh) + row_h * (r + 1))
        brands = rack_facings(header, others, n, key, variant, r)
        CF._row(im, brands, 0, ry0, W, ry1, n, False, key)
        rows.append(brands)
    im.rect((0, H, W, H + CF.DARK_ROWS), (12, 12, 12))
    c = im.to_canvas()
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H + CF.DARK_ROWS), "header": header, "rows": rows, "said": said,
            "unset": list(im.unset), "dark": (0, H + 4, W, H + CF.DARK_ROWS - 4),
            "name": f"cigrack_{header}_v{variant % 4}_{W}x{H + CF.DARK_ROWS}_{digest:08x}"}


def art_uv(rect, size):
    return CF.uv_rect(rect, size)
