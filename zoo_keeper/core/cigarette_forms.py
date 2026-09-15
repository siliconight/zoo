"""cigarette_machine, decided in pure Python: the layout, the brands in it and
every pixel behind its glass.

Zoo 0.91.0. The walker's three photos are the same machine, the floor-
standing PULL-KNOB kind of the 1970s to the 1990s: a cabinet about 0.85 m
wide, 0.45 m deep and 1.2 m tall on short black splayed legs; a chrome frame
and top trim with a brass strip and a round key lock across the top;
woodgrain panels either side of the front; behind the front a HEADER ad with
a price card and a warning sticker, then two ROWS of packs faced out, each
over a strip that says sales to minors are forbidden, each over a steel
shelf of PULL KNOBS; a coin slot and a coin return down the right; a pull-out
delivery tray across the bottom.

WHAT IS BUILT, in the recipe frame (metres, Z up, base-up, the wall the
slot's +Y face, the front -Y, +X to a viewer's right):

  * the BODY, painted near-black, standing on four splayed LEGS with pads;
  * two WOOD side panels, standing 4 mm proud of the front;
  * the TOP cap in chrome, the BRASS strip on its front and the LOCK;
  * the FRAME, one closed solid over a cell grid (the vending machine's
    door, `vending_forms.door_cells`) with two apertures cut through it:
    the DISPLAY, and the delivery TRAY under the coin column and display;
  * the DISPLAY panel in its aperture, carrying the art (`art`): the header
    ad lit faintly, the rest painted;
  * two KNOB SHELVES in chrome with a pull knob per pack column -- a shaft
    and a cap, real geometry -- in chrome or amber by variant;
  * the COIN plate with its slot, the RETURN plate with its button and
    mouth, and the TRAY's drawer front and handle.

THE SLOT IS EXACT: the knob caps are the slot's front plane, the rear leg
pads its back and the splayed pads its sides, and `prims.fit_exact` ends the
plan within a fraction of a percent. Collision is the cabinet's box -- a
body walks into a machine, not between its legs.

NO TWO FACES SHARE A PLANE (`prims.coincident_pairs` is empty): every part
that meets another is buried a depth no other part at that joint uses.

FORMS: ``pull_knob`` (and ``auto``, the default) has a second ad between the
rows; ``pull_knob_split`` has the black panel that says CIGARETTES there.

THE BRANDS are `cigarette_brands`' invented ones; which brand is on the
header, which packs fill the rows, the knobs' finish and whether cream
display cards stand behind the packs are the module's variant
(`resolve`), drawn from the stem without its variant like the vending
machine's brand.
"""
from __future__ import annotations

import re
import zlib

from . import cigarette_brands as CB
from . import pixel_type as pt
from . import prims as P
from .vending_forms import Canvas, _BAYER, _lerp

FORMS = ("pull_knob", "pull_knob_split")
#: Deli Counter's slots (`level_design._PIECES`) and the genome's range.
DC_SIZES = ((0.88, 0.45, 1.5), (0.9, 0.48, 1.55))
RANGES = {"width": (0.78, 1.02), "depth": (0.40, 0.58), "height": (1.30, 1.75)}

# --- the frame -------------------------------------------------------------------

LEG_FRAC = 0.2            # the legs' share of the slot's height
SPLAY = 0.03              # each side, the pads past the cabinet
SIDE_T = 0.025            # a wood side panel
BODY_IN = 0.022           # the body's side inside the panel's outer face
FRAME_T = 0.032
STILE = 0.030
MULLION = 0.030
COL_W = 0.110
TOP_H_FRAC = 0.075        # of the cabinet's height
SHELF_OUT = 0.028         # a knob shelf's front past the frame's
KNOB_LEN = 0.042          # a knob's cap past the shelf
KNOB_R = 0.013
SHAFT_R = 0.006
PACK_PITCH = 0.052
DISPLAY_SET = 0.020       # the display's face behind the frame's
#: The cabinet's zones from its bottom, as fractions of its height (a 1.2 m
#: cabinet: the tray 0.14, a knob shelf 0.07, a strip 0.035, a pack row 0.17,
#: the middle 0.11, the header 0.26, the top 0.09).
ZONES = (("kick", 0.025), ("tray", 0.117), ("shelf_2", 0.058), ("strip_2", 0.029),
         ("row_2", 0.142), ("middle", 0.092), ("shelf_1", 0.058), ("strip_1", 0.029),
         ("row_1", 0.142), ("header", 0.233), ("top", 0.075))

# --- the art ---------------------------------------------------------------------

#: Display artwork density: a 1.4 mm pixel, so a pack 52 mm wide is 36 px
#: and its name in the 16 px face fits on it.
TEXEL = 700
#: The header ad's glow and its dimmed diffuse copy (`materials.
#: make_backlit_material`). FAINT: some machines had a lit header, most of
#: the light in a club is somebody else's.
#:
#: MEASURED, and kept where it was set: `strip_club_a01`'s two machines
#: (variants 1 and 3) built at each strength and swapped into a scratch copy
#: of `_runs/walk_9057_rain` (Heavy Rain as shipped), Godot 4.7
#: gl_compatibility, `tools/look_shots.py` 1600 x 900, a camera 1.5 m in front
#: of each. The knob read back from every GLB (factor 0.5 / 1.0, then 1.0 with
#: KHR strength 1.5). Header pixels are those brightening more than 8 codes
#: from 0 to 1.5 (18,697 and 19,105); 8-bit sRGB after tonemap and Lux post,
#: Rec.709 luma:
#:
#:          strength     0      0.5    1.0    1.5
#:   luma             21.8   47.6   61.2   84.3    (main floor, BOULEVARD BUTTS)
#:                    14.9   45.8   58.8   77.4    (VIP wing, DELCO REDS)
#:   pinned / white %    0      0      0      0     both
#:
#: 0.5 is 2.2 - 3.1 x the unlit header and nothing clips even at 1.5 under
#: the rain preset. Not measured: the summer preset.
HEADER_EMISSION = 0.5
HEADER_ALBEDO = 0.6
#: Roughness of the painted display behind its glass (`make_painted_material`).
DISPLAY_ROUGHNESS = 0.4

BODY = (0.035, 0.030, 0.028)
CHROME = (0.66, 0.66, 0.66)
BRASS = (0.60, 0.44, 0.16)
AMBER = (0.80, 0.34, 0.03)
BLACK = (0.015, 0.015, 0.016)
WOOD = (0.30, 0.19, 0.12)
MATERIALS = {
    "body": (BODY, "metal_painted"),
    "wood": (WOOD, "wood_stained"),
    "chrome": (CHROME, "metal_bare"),
    "brass": (BRASS, "metal_bare"),
    "black": (BLACK, "metal_painted"),
    "amber": (AMBER, "plastic"),
}

#: Burial depths at the joints, each 3 mm or more from the others there.
BURY = 0.006
_VARIANT = re.compile(r"_n\d+(?=_|$)")


def pick_form(form):
    return form if form in FORMS else "pull_knob"


def zones(z0, hc):
    """{zone: (z_bottom, z_top)} for a cabinet ``hc`` tall standing on ``z0``."""
    total = sum(f for _n, f in ZONES)
    out, z = {}, z0
    for name, f in ZONES:
        dz = hc * f / total
        out[name] = (z, z + dz)
        z += dz
    return out


def _slab(part, mat, xs, zs, filled, y0, y1):
    """One closed solid over a cell grid (x columns ``xs``, z rows ``zs``;
    ``filled[i][j]`` says whether column i, row j is solid): a front and a
    back quad per solid cell, a wall where a solid cell meets a hole or the
    edge. Shared corners are one vertex, so there is no internal face."""
    verts, index = [], {}

    def v(i, j, layer):
        k = (i, j, layer)
        if k not in index:
            index[k] = len(verts)
            verts.append((xs[i], (y0, y1)[layer], zs[j]))
        return index[k]
    faces = []
    ni, nj = len(xs) - 1, len(zs) - 1
    for i in range(ni):
        for j in range(nj):
            if not filled[i][j]:
                continue
            faces.append((v(i, j, 0), v(i + 1, j, 0), v(i + 1, j + 1, 0), v(i, j + 1, 0)))
            faces.append((v(i, j, 1), v(i, j + 1, 1), v(i + 1, j + 1, 1), v(i + 1, j, 1)))
            for (di, dj), (a, b) in (((0, -1), ((i, j), (i + 1, j))),
                                     ((1, 0), ((i + 1, j), (i + 1, j + 1))),
                                     ((0, 1), ((i + 1, j + 1), (i, j + 1))),
                                     ((-1, 0), ((i, j + 1), (i, j)))):
                p, q = i + di, j + dj
                if 0 <= p < ni and 0 <= q < nj and filled[p][q]:
                    continue
                faces.append((v(*a, 0), v(*a, 1), v(*b, 1), v(*b, 0)))
    return P.mesh(part, mat, verts, faces)


def layout(w, d, h, knobs="chrome"):
    """Every part at slot (w, d, h) before the fit: ``{prims, facts}``."""
    legs = LEG_FRAC * h
    hc = h - legs
    wc = w - 2.0 * SPLAY
    Z = zones(legs, hc)
    top_z0 = Z["top"][0]
    yf = -d / 2.0 + SHELF_OUT + KNOB_LEN          # the frame's front
    yb = d / 2.0 - 0.004                          # the body's back
    xi = wc / 2.0 - BODY_IN                       # the body's side
    prims = []
    # the body and its wood sides
    prims.append(P.box("Cig_Body", "body", (-xi, yf + FRAME_T - BURY, legs), (xi, yb, top_z0 + BURY)))
    for s in (-1, 1):
        x0, x1 = sorted((s * wc / 2.0, s * (wc / 2.0 - SIDE_T)))
        prims.append(P.box("Cig_Wood", "wood", (x0, yf - 0.004, legs - 0.004), (x1, d / 2.0 - 0.012, top_z0 + 0.010)))
    # the top, the brass strip and the lock
    prims.append(P.box("Cig_Top", "chrome", (-wc / 2.0 - 0.004, yf - 0.008, top_z0), (wc / 2.0 + 0.004, d / 2.0 - 0.008, h)))
    bz0, bz1 = top_z0 + 0.22 * (h - top_z0), h - 0.22 * (h - top_z0)
    prims.append(P.box("Cig_Brass", "brass", (-wc / 2.0 + 0.03, yf - 0.015, bz0), (wc / 2.0 - 0.03, yf - 0.002, bz1)))
    lz = (bz0 + bz1) / 2.0
    lr = min(0.018, 0.45 * (bz1 - bz0))
    # the lock's back 3 mm behind the top's face and 3 mm short of the
    # brass's back: 2.0 mm passed the pure probe by float and failed Blender's
    prims.append(P.rod("Cig_Lock", "chrome", (0.0, yf - 0.005, lz), (0.0, yf - 0.030, lz), lr, segments=10))
    prims.append(P.rod("Cig_Lock", "black", (0.0, yf - 0.027, lz), (0.0, yf - 0.033, lz), 0.35 * lr, segments=5))
    # the frame: stiles, the column, the rails, with the display and tray cut
    fx0 = -xi - 0.003                              # 3 mm into the wood
    fx1 = xi + 0.003
    dx0 = -xi + STILE
    cx1 = xi - STILE
    cx0 = cx1 - COL_W
    dx1 = cx0 - MULLION
    # a 12 mm rail over the header: the aperture's top would otherwise be
    # the top cap's underside, one plane
    disp = (Z["strip_2"][0], Z["header"][1] - 0.012)
    tray = (Z["tray"][0] + 0.012, Z["tray"][1] - 0.012)
    xs = (fx0, dx0, dx1, cx0, cx1, fx1)
    zs = (legs + 0.004, tray[0], tray[1], disp[0], disp[1], top_z0 + 0.003)
    holes = [(dx0, dx1, disp[0], disp[1]), (dx0, cx1, tray[0], tray[1])]
    filled = []
    for i in range(len(xs) - 1):
        col = []
        cx = (xs[i] + xs[i + 1]) / 2.0
        for j in range(len(zs) - 1):
            cz = (zs[j] + zs[j + 1]) / 2.0
            col.append(not any(a < cx < b and c < cz < e for a, b, c, e in holes))
        filled.append(col)
    prims.append(_slab("Cig_Frame", "chrome", xs, zs, filled, yf, yf + FRAME_T))
    # the display insert, BURY larger than its aperture
    prims.append(display_prim(dx0, dx1, disp[0], disp[1], Z["header"][0], yf + DISPLAY_SET,
                              yf + FRAME_T + BURY))
    # the knob shelves and knobs
    n_packs = max(6, int((dx1 - dx0 - 0.01) // PACK_PITCH))
    pitch = (dx1 - dx0) / n_packs
    knob_mat = "amber" if knobs == "amber" else "chrome"
    for key, back in (("shelf_1", yf + DISPLAY_SET + 0.009), ("shelf_2", yf + 0.006)):
        z0, z1 = Z[key]
        prims.append(P.box("Cig_Shelf", "chrome", (dx0 + 0.003, yf - SHELF_OUT, z0 + 0.004),
                           (dx1 - 0.003, back, z1 - 0.005)))
        kz = (z0 + z1) / 2.0
        for k in range(n_packs):
            kx = dx0 + pitch * (k + 0.5)
            prims.append(P.rod("Cig_Knob", "chrome", (kx, yf - SHELF_OUT + 0.004, kz),
                               (kx, yf - SHELF_OUT - 0.024, kz), SHAFT_R, segments=7))
            prims.append(P.rod("Cig_Knob", knob_mat, (kx, yf - SHELF_OUT - 0.020, kz),
                               (kx, yf - SHELF_OUT - KNOB_LEN, kz), KNOB_R, KNOB_R * 0.92, segments=8))
    # the coin column: slot plate, return plate, button and mouth
    ccx = (cx0 + cx1) / 2.0
    hz0, hz1 = Z["header"]
    cz = (Z["row_1"][0] + Z["header"][0]) / 2.0
    prims.append(P.box("Cig_Coin", "chrome", (cx0 + 0.012, yf - 0.010, cz - 0.07), (cx1 - 0.012, yf + 0.006, cz + 0.07)))
    prims.append(P.box("Cig_Coin", "black", (ccx - 0.004, yf - 0.014, cz + 0.015), (ccx + 0.004, yf - 0.004, cz + 0.05)))
    rz = (Z["row_2"][0] + Z["middle"][1]) / 2.0
    prims.append(P.box("Cig_Return", "chrome", (cx0 + 0.016, yf - 0.016, rz - 0.06), (cx1 - 0.016, yf + 0.004, rz + 0.06)))
    prims.append(P.rod("Cig_Return", "chrome", (ccx, yf - 0.012, rz + 0.025), (ccx, yf - 0.030, rz + 0.025),
                       0.012, segments=8))
    prims.append(P.box("Cig_Return", "black", (ccx - 0.025, yf - 0.020, rz - 0.045), (ccx + 0.025, yf - 0.010, rz - 0.020)))
    # the delivery tray's drawer and handle
    prims.append(P.box("Cig_Tray", "chrome", (dx0 + 0.004, yf - 0.020, tray[0] + 0.004),
                       (cx1 - 0.004, yf + FRAME_T + BURY + 0.006, tray[1] - 0.004)))
    tz = (tray[0] + tray[1]) / 2.0
    txm = (dx0 + cx1) / 2.0
    prims.append(P.box("Cig_Tray", "black", (txm - 0.15, yf - 0.024, tz + 0.004), (txm + 0.15, yf - 0.014, tz + 0.020)))
    # the legs, splayed, on pads
    lx = wc / 2.0 - 0.06
    for sx in (-1, 1):
        for fy, py in ((yf + 0.10, yf + 0.03), (yb - 0.06, d / 2.0 - 0.025)):
            top = (sx * lx, fy, legs + 0.025)
            pad = (sx * (w / 2.0 - 0.025), py)
            prims.append(P.rod("Cig_Leg", "black", top, (pad[0], pad[1], 0.014), 0.014, 0.011, segments=8))
            prims.append(P.cyl("Cig_Leg", "black", pad, 0.025, 0.0, 0.020, segments=8))
    facts = {"legs": legs, "cabinet_h": hc, "zones": Z, "display": (dx0, dx1, disp[0], disp[1]),
             "tray": (dx0, cx1, tray[0], tray[1]), "n_packs": n_packs, "pitch": pitch,
             "yf": yf, "collision": ((-wc / 2.0, yf - 0.004, legs), (wc / 2.0, d / 2.0, h))}
    return {"prims": prims, "facts": facts}


def display_prim(dx0, dx1, dz0, dz1, zh, y0, y1):
    """The display insert: a box BURY larger than its aperture whose front
    is two quads split at the header's bottom ``zh`` -- the header lit, the
    rest painted -- with ``uvs`` mapping the APERTURE to the art edge to edge
    (a corner BURY outside it samples past the raster's edge, which the
    material clamps) and ``face_mats`` naming each face's material. Adjacent
    quads in one plane share an edge, not an area, so they are no pair."""
    X0, X1, Z0, Z1 = dx0 - BURY, dx1 + BURY, dz0 - BURY, dz1 + BURY
    verts = [(X0, y0, Z0), (X1, y0, Z0), (X1, y0, zh), (X0, y0, zh), (X1, y0, Z1), (X0, y0, Z1),
             (X0, y1, Z0), (X1, y1, Z0), (X1, y1, Z1), (X0, y1, Z1)]
    faces = [(0, 1, 2, 3), (3, 2, 4, 5), (6, 9, 8, 7), (0, 6, 7, 1), (5, 4, 8, 9),
             (6, 0, 3, 5, 9), (7, 8, 4, 2, 1)]
    p = P.mesh("Cig_Display", "display", verts, faces)
    p["face_mats"] = ["paint", "lit", "paint", "paint", "paint", "paint", "paint"]

    def uv(i):
        x, _y, z = verts[i]
        return ((x - dx0) / (dx1 - dx0), (z - dz0) / (dz1 - dz0))
    p["uvs"] = [tuple(("art",) + uv(i) for i in f) if k < 2 else tuple(("dark", 0.5, 0.5) for _ in f)
                for k, f in enumerate(faces)]
    return p


def plan(w, d, h, knobs="chrome"):
    """``{prims, collision, facts, scale}``, fitted exactly to the slot."""
    L = layout(w, d, h, knobs)
    prims = L["prims"]
    lo, hi = P.bounds(prims)
    scale = (w / (hi[0] - lo[0]), d / (hi[1] - lo[1]), h / (hi[2] - lo[2]))
    fitted, boxes = P.fit_exact(prims, (-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h),
                                [L["facts"]["collision"]])
    return {"prims": fitted, "collision": boxes, "facts": L["facts"], "scale": scale}


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


# --- the variant ---------------------------------------------------------------------

def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def lineup(key):
    """Every brand in the order a module keyed ``key`` uses them."""
    return sorted(CB.IDS, key=lambda i: (_h(key, i), i))


def resolve(plan_, streams=None):
    """``(header_brand, variant, key, knobs, cards)`` for a build plan: the
    header is index ``variant`` of `lineup` keyed by the stem without its
    variant (an explicit ``params.brand`` wins); odd variants have amber
    knobs; variants 1 and 2 stand cream display cards behind the packs."""
    params = plan_.get("params") or {}
    module = plan_.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    key = _VARIANT.sub("", module.get("stem") or "") or "cigarette_machine"
    asked = params.get("brand")
    brand = asked if asked in CB.BY_ID else lineup(key)[variant % len(CB.IDS)]
    knobs = "amber" if variant % 2 else "chrome"
    cards = variant % 4 in (1, 2)
    return brand, variant, key, knobs, cards


# --- the art -----------------------------------------------------------------------------

def _rgb(h):
    return CB.hex_rgb(h)


def _pack(c, brand, x0, y0, pw, ph):
    """One pack, faced out: the body, its design in the second colour, the
    short name, and a filter-coloured band across the top of the pack."""
    b = CB.BY_ID[brand]
    body, second, ink = _rgb(b["pack"]), _rgb(b["second"]), _rgb(b["ink"])
    c.rect(x0, y0, x0 + pw, y0 + ph, body)
    design = b["design"]
    if design == "band":
        c.rect(x0, y0 + ph * 45 // 100, x0 + pw, y0 + ph * 70 // 100, second)
    elif design == "split":
        c.rect(x0, y0, x0 + pw, y0 + ph * 40 // 100, second)
    elif design == "stripe":
        c.rect(x0 + pw * 60 // 100, y0, x0 + pw * 80 // 100, y0 + ph, second)
    elif design == "disc":
        r = pw * 0.30
        cx, cy = x0 + pw / 2.0, y0 + ph * 0.30
        for yy in range(int(cy - r), int(cy + r) + 1):
            for xx in range(int(cx - r), int(cx + r) + 1):
                if (xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2 <= r * r:
                    c.px(xx, yy, second)
    elif design == "diamond":
        r = pw * 0.34
        cx, cy = x0 + pw / 2.0, y0 + ph * 0.32
        for yy in range(int(cy - r), int(cy + r) + 1):
            for xx in range(int(cx - r), int(cx + r) + 1):
                if abs(xx + 0.5 - cx) + abs(yy + 0.5 - cy) <= r:
                    c.px(xx, yy, second)
    elif design == "bars":
        for f in (0.18, 0.28):
            c.rect(x0, y0 + int(ph * f), x0 + pw, y0 + int(ph * f) + max(2, ph // 20), second)
    else:
        raise ValueError(f"pack {brand}: unknown design {design!r}")
    m = pt.trim(pt.render(b["short"], 1))
    ty = y0 + ph * 72 // 100 - len(m) // 2 if design != "band" else y0 + ph * 57 // 100 - len(m) // 2
    text_ink = ink if design != "band" else (ink if sum(second) < 360 else (16, 16, 16))
    c.mask(m, x0 + (pw - len(m[0])) // 2, ty, text_ink)
    # the cellophane catches the light along the top edge
    c.rect(x0, y0, x0 + pw, y0 + 1, tuple(min(255, v + 50) for v in body))


def _gradient(c, x0, y0, x1, y1, top, bottom):
    steps = 7
    hh = max(1, y1 - y0 - 1)
    for y in range(y0, y1):
        lv = steps * (y - y0) / hh
        row = _BAYER[y % 4]
        for x in range(x0, x1):
            k = min(steps, int(lv + row[x % 4] / 16.0))
            c.px(x, y, _lerp(top, bottom, k / steps))


def _text_block(c, lines, x0, x1, y, ink, scale, shadow=None):
    for line in lines:
        m = pt.trim(pt.render(line, scale))
        x = x0 + (x1 - x0 - len(m[0])) // 2
        if shadow:
            c.mask(m, x + 1, y + 1, shadow, grow=0)
        c.mask(m, x, y, ink)
        y += len(m) + 3 * scale
    return y


def _ad(c, brand, x0, y0, x1, y1, with_cards=True):
    """A brand's ad: its gradient, the logo as large as fits, a big pack,
    the slogan, and (on the header) the price card and the warning sticker."""
    b = CB.BY_ID[brand]
    top, bottom = _rgb(b["bg"][0]), _rgb(b["bg"][1])
    _gradient(c, x0, y0, x1, y1, top, bottom)
    W, H = x1 - x0, y1 - y0
    said = []
    # the pack, big, on the left
    pw = max(20, int(W * 0.16))
    ph = min(int(pw * 1.55), int(H * 0.72))
    px0, py0 = x0 + max(6, W // 24), y0 + (H - ph) // 2
    c.rect(px0 + 3, py0 + 3, px0 + pw + 3, py0 + ph + 3, (8, 8, 8))
    _pack(c, brand, px0, py0, pw, ph)
    # the logo and slogan on the right of it
    tx0 = px0 + pw + max(6, W // 30)
    card_w = max(pt.ink_width(CB.PRICE[1], 1), pt.ink_width(CB.PRICE[0], 2)) + 8
    tx1 = x1 - (card_w + 12 if with_cards else 6)
    avail = tx1 - tx0
    scale = 3
    while scale > 1 and max(pt.ink_width(l, scale) for l in b["logo"]) > avail:
        scale -= 1
    logo_h = len(b["logo"]) * (pt.LINE * scale)
    y = y0 + max(4, (H - logo_h - 2 * pt.LINE) // 3)
    y = _text_block(c, b["logo"], tx0, tx1, y, (250, 246, 232), scale, shadow=(10, 6, 4))
    said += list(b["logo"])
    lines = pt.wrap(b["slogan"], avail, 1) or [b["slogan"]]
    _text_block(c, lines[:2], tx0, tx1, y + 2, (236, 220, 170), 1)
    said += lines[:2]
    if with_cards:
        # the price card: white, black type, taped on
        cw = card_w
        ch = pt.LINE * 2 + pt.LINE + 6
        cx0, cy0 = x1 - cw - 6, y0 + 6
        c.rect(cx0, cy0, cx0 + cw, cy0 + ch, (244, 242, 232))
        c.rect(cx0 + cw // 2 - 6, cy0 - 2, cx0 + cw // 2 + 6, cy0 + 3, (200, 196, 170))
        yy = _text_block(c, [CB.PRICE[0]], cx0, cx0 + cw, cy0 + 3, (20, 20, 20), 2)
        _text_block(c, [CB.PRICE[1]], cx0, cx0 + cw, yy - 2, (170, 20, 20), 1)
        said += list(CB.PRICE)
        # the warning sticker, bottom right
        ww = max(pt.ink_width(l, 1) for l in CB.WARNING) + 6
        wh = len(CB.WARNING) * (pt.LINE - 2) + 6
        if ww <= W - (px0 - x0) - pw - 8 and wh <= H // 2:
            wx0, wy0 = x1 - ww - 4, y1 - wh - 4
            c.rect(wx0, wy0, wx0 + ww, wy0 + wh, (236, 236, 228))
            c.rect(wx0, wy0, wx0 + ww, wy0 + 1, (40, 40, 40))
            yy = wy0 + 2
            for line in CB.WARNING:
                m = pt.trim(pt.render(line, 1))
                c.mask(m, wx0 + 3, yy, (24, 24, 24))
                yy += pt.LINE - 2
            said += list(CB.WARNING)
    return said


def _row(c, brands, x0, y0, x1, y1, n, cards, key):
    """A row of pack windows: a black backing (or cream display cards with
    black notches), one pack faced out per knob column."""
    W, H = x1 - x0, y1 - y0
    pitch = W / n
    c.rect(x0, y0, x1, y1, (10, 10, 10))
    for k in range(n):
        wx0 = int(x0 + pitch * k) + 1
        wx1 = int(x0 + pitch * (k + 1)) - 1
        if cards:
            c.rect(wx0, y0 + 2, wx1, y1 - 2, (232, 222, 196))
            # the notch: a black triangle cut into the card's top
            mid = (wx0 + wx1) / 2.0
            for yy in range(y0 + 2, y0 + 2 + max(4, H // 7)):
                half = (y0 + 2 + max(4, H // 7) - yy) * 0.9
                for xx in range(int(mid - half), int(mid + half) + 1):
                    c.px(xx, yy, (10, 10, 10))
        pw = min(pack_px(), wx1 - wx0 - 4)
        ph = min(int(pw * 1.55), H - 10)
        px0 = (wx0 + wx1 - pw) // 2
        py0 = y1 - ph - 4
        _pack(c, brands[k % len(brands)], px0, py0, pw, ph)
        # the window's glass edge
        c.rect(wx0 - 1, y0, wx0, y1, (60, 60, 60))


def pack_px():
    """A pack's width in the rows, pixels."""
    return int(PACK_PITCH * TEXEL * 0.92)


def _strip(c, x0, y0, x1, y1):
    c.rect(x0, y0, x1, y1, (226, 224, 214))
    c.rect(x0, y0, x1, y0 + 1, (120, 120, 116))
    text = CB.MINORS if pt.ink_width(CB.MINORS, 1) <= x1 - x0 - 6 else CB.MINORS_SHORT
    m = pt.trim(pt.render(text, 1))
    c.mask(m, x0 + (x1 - x0 - len(m[0])) // 2, y0 + (y1 - y0 - len(m)) // 2, (30, 30, 30))
    return text


def art(facts, brand, variant, key, form, cards):
    """The display's raster: header, rows, strips and the middle, with the
    knob shelf in front of the middle painted dark. Returns ``{canvas,
    rects, size, name, brands, said}``; rects are pixel boxes (x0, y0, x1,
    y1), row 0 at the TOP of the display."""
    dx0, dx1, dz0, dz1 = facts["display"]
    Z = facts["zones"]
    W = int(round((dx1 - dx0) * TEXEL))
    H = int(round((dz1 - dz0) * TEXEL))
    c = Canvas(W, H + 6, (12, 12, 12))

    def py(z):
        return int(round((dz1 - z) * TEXEL))
    rects = {}
    order = lineup(key)
    header = brand
    others = [b for b in order if b != header]
    said = []
    n = facts["n_packs"]
    # header
    y0, y1 = max(0, py(Z["header"][1])), py(Z["header"][0])
    rects["header"] = (0, y0, W, y1)
    said += _ad(c, header, 0, y0, W, y1, with_cards=True)
    # rows and strips: the first row leads with the header's brand
    row_brands = {1: [header] + others[:4], 2: others[4:9] or others[:5]}
    for r in (1, 2):
        ry0, ry1 = py(Z["row_%d" % r][1]), py(Z["row_%d" % r][0])
        rects["row_%d" % r] = (0, ry0, W, ry1)
        brands = [row_brands[r][(_h(key, variant, r, k) % len(row_brands[r]))] for k in range(n)]
        if r == 1:
            brands[0] = header          # the first column sells what the header does
        _row(c, brands, 0, ry0, W, ry1, n, cards, key)
        sy0, sy1 = py(Z["strip_%d" % r][1]), py(Z["strip_%d" % r][0])
        rects["strip_%d" % r] = (0, sy0, W, sy1)
        said.append(_strip(c, 0, sy0, W, sy1))
    # the shelf in front of the middle: dark
    ky0, ky1 = py(Z["shelf_1"][1]), py(Z["shelf_1"][0])
    c.rect(0, ky0, W, ky1, (14, 14, 14))
    my0, my1 = py(Z["middle"][1]), py(Z["middle"][0])
    rects["middle"] = (0, my0, W, my1)
    middle = None
    if form == "pull_knob_split":
        c.rect(0, my0, W, my1, (8, 8, 8))
        scale = 3
        while scale > 1 and (pt.ink_width(CB.PANEL_WORD, scale) > W - 20 or pt.LINE * scale > my1 - my0 - 4):
            scale -= 1
        m = pt.trim(pt.render(CB.PANEL_WORD, scale))
        c.mask(m, (W - len(m[0])) // 2 + 1, my0 + (my1 - my0 - len(m)) // 2 + 1, (60, 60, 60))
        c.mask(m, (W - len(m[0])) // 2, my0 + (my1 - my0 - len(m)) // 2, (214, 214, 208))
        said.append(CB.PANEL_WORD)
    else:
        # the variant walks the middle ad too: 0.91.0's first contact sheet
        # showed one brand there on all four variants of a stem
        middle = others[(5 + 3 * variant) % len(others)]
        said += _ad(c, middle, 0, my0, W, my1, with_cards=False)
    rects["dark"] = (0, H + 1, 4, H + 5)
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "rects": rects, "size": (W, H + 6), "said": said,
            "brands": {"header": header, "rows": row_brands, "middle": middle},
            "name": f"cig_{header}_{form}_v{variant % 4}_{W}x{H + 6}_{digest:08x}"}


def uv_rect(rect, size):
    x0, y0, x1, y1 = rect
    W, H = size
    return (x0 / W, 1.0 - y1 / H, x1 / W, 1.0 - y0 / H)
