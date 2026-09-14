"""The vending machine, decided in pure Python: layout, brand, artwork.

Zoo 0.87.0. `recipes/vending_machine.py` only executes what this returns, so
every size, every brand pick and every pixel of the panel is testable without
Blender.

WHAT 0.86.0 SHIPPED, measured before anything moved: a body box the slot's
size with a tinted "glass" slab, a side panel, a coin slot and a tray hung on
its front -- the coin slot's front 45 mm in front of the body, so a 0.75 m
slot built 0.795 m deep and failed its own `fit_depth` (Deli Counter's
furnish agent reported it; `country_club_a01`'s kit log reads FAIL on
`prop_vending_machine_delco_1997_04_w85_d75_h183`). Nothing on it was lit.

WHAT IS BUILT, in the module frame (Z up, metres, centre pivot, front toward
-Y, +X to a viewer's right):

  * the CABINET, the slot's full width and height, from just inside the door
    to the back;
  * the DOOR, a slab across the front standing `REVEAL` inside the cabinet's
    sides and top, with three apertures cut through it: the big PANEL
    aperture on the left, the COLUMN aperture on the right, and the delivery
    FLAP under the panel;
  * the backlit PANEL in its aperture, carrying the brand's artwork;
  * in the column: a dark PLATE, the price DISPLAY (bezel and lit lens), the
    COIN MECH plate with a coin slot, a bill mouth and a reject button, a
    column of six lit selection BUTTONS each labelled with a product, the
    COIN RETURN, and the T-handle LOCK;
  * the delivery BIN (dark cavity) behind a tilted FLAP;
  * the recessed KICK plate.

THE SLOT IS EXACT: the door's front IS the slot's front plane, the cabinet is
the slot's width, height and back, and nothing stands proud of the door --
every column part is recessed into its aperture, the frontmost 4 mm behind
the plane. So the module measures the slot on every axis at any genome size
with no scaling (`extents` is the arithmetic, the bpy test the measurement).

NO TWO FACES SHARE A PLANE. Every insert is BURY larger than its aperture
and runs BURY past the door's back into the cabinet; inserts that meet the
same back plane never overlap; stacked parts are buried into what they stand
on. BURY is three times `tools/coplanar_probe.py`'s 2 mm window.

GLOW. The panel, the buttons and the display lens are glTF-emissive, named
for Lux's emissive binder (`M_*_Face`, `M_*_Lens`) so a power cut kills them
with the building's fixtures. Their base colour is the same artwork dimmed by
`*_ALBEDO` (a backlit panel is not a mirror of the room); their emission is
the artwork at `*_EMISSION`. The numbers are measured in a Godot 4.7 walk
copy; the CHANGELOG entry for 0.87.0 has the frames.
"""
from __future__ import annotations

import math
import re
import struct
import zlib

from . import brands as brand_table
from . import pixel_type as pt

# --- the frame --------------------------------------------------------------------

#: How far the door stands inside the cabinet's sides and top: a real door is
#: a separate box hung on the cabinet's face, and the seam reads.
REVEAL = 0.008
DOOR_T = 0.065
STILE = 0.04
MULLION = 0.035
#: The selection column, a constant: buttons are sized for a hand, not the slot.
COL_W = 0.19
KICK_H = 0.09
KICK_SET = 0.03
KICK_LIFT = 0.004
#: The door's bottom rail, from the kick to the panel, holds the flap.
BOTTOM_RAIL = 0.30
TOP_RAIL = 0.07
PANEL_SET = 0.014
COL_SET = 0.03
FLAP_MARGIN = 0.05
FLAP_H = 0.17
FLAP_BOTTOM = 0.06
BIN_SET = 0.05
FLAP_TOP_SET = 0.034
FLAP_BOTTOM_SET = 0.012
FLAP_T = 0.006
#: Burial past a contact plane: 3 x the coplanar probe's 2 mm.
BURY = 0.006
N_BUTTONS = 6
BUTTON = (0.14, 0.046)
BUTTON_PITCH = 0.058

# --- the art -----------------------------------------------------------------------

#: Panel artwork density, pixels per metre: a 4 mm pixel, crisp under the
#: nearest-neighbour filter every Pixelcoat pack asks for.
TEXEL = 256
#: Button labels and the price display at twice that, so a product name in
#: the 16 px face fits a 14 cm button.
LABEL_TEXEL = 512
PRICE = "75¢"
LED = "#ff3a1a"

# --- the glow ---------------------------------------------------------------------
#
# MEASURED, not chosen, in two scratch copies of the vault-room walk (Godot 4.7,
# gl_compatibility, RTX 2060, `tools/look_shots.py`, 8-bit sRGB after tonemap
# and Lux post, Rec.709 luma): the same four machines built at each strength,
# shot close at the basement wall (Heavy Rain preset, fluorescent-lit), the
# lobby (Heavy Rain) and outdoors (the theme's delco_summer_afternoon, the
# brightest light this level has). Panel pixels are those that brighten by
# more than 8 codes from strength 0 to 1; "pinned" is any channel >= 250,
# "white" all channels >= 235.
#
#                       strength 0    1.0     1.5     2.0     3.0
#   basement  luma            28.9  110.8   142.5   165.5   194.2
#             saturation      0.63   0.54    0.49    0.45    0.36
#             white %         0.00   0.00    0.00    2.85    8.03
#   summer    luma            47.5  120.6   149.8   172.1   201.2
#   outdoors  saturation      0.76   0.78    0.71    0.61    0.45
#             pinned %        0.00   0.00   68.52   70.46   90.33
#
# 1.0 is the highest strength with nothing pinned or white in either preset:
# 3.8 x its unlit luma in the basement, and the art's own saturation (0.81 -
# 0.89 in the PNG) kept under the summer sun. REFUTED, kept: 2.0 was the first
# value, from the fixtures' lenses; it washed every panel toward pastel under
# Heavy Rain and pinned 70 % of the panel outdoors.
#
# GLOW. The Environment's glow does render in Compatibility here: at 3.0 a
# ring 3-24 px outside the panel brightens by 12.0 codes with the preset's
# glow on and -0.4 with it off (basement). At 1.0 the ring moves 0.3, because
# Heavy Rain's glow_hdr_threshold is 1.1 -- a halo is the preset's lever, not
# this one.
PANEL_EMISSION = 1.0
LENS_EMISSION = 1.0
PANEL_ALBEDO = 0.35
LENS_ALBEDO = 0.35

#: Trim that is not the brand's paint.
BLACK = (0.018, 0.018, 0.02)
CHROME = (0.62, 0.63, 0.64)


def panel_size(w, h):
    """(width, height) of the panel aperture in metres."""
    pw = w - 2.0 * REVEAL - 2.0 * STILE - MULLION - COL_W
    ph = h - KICK_H - BOTTOM_RAIL - TOP_RAIL - REVEAL
    return pw, ph


def _box(x0, x1, y0, y1, z0, z1):
    return (min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1),
            min(z0, z1), max(z0, z1))


def _centred(cx, cz, sx, sz, y0, y1):
    return _box(cx - sx / 2.0, cx + sx / 2.0, y0, y1, cz - sz / 2.0, cz + sz / 2.0)


def layout(w, d, h):
    """Every part of a machine at slot (w, d, h). Boxes are
    (x0, x1, y0, y1, z0, z1) in the module frame."""
    pw, ph = panel_size(w, h)
    if pw < 0.2 or ph < 0.6:
        raise ValueError(f"slot {w} x {d} x {h} leaves a {pw:.3f} x {ph:.3f} panel")
    z0, z1 = -h / 2.0, h / 2.0
    yf = -d / 2.0
    xd0, xd1 = -w / 2.0 + REVEAL, w / 2.0 - REVEAL
    px0 = xd0 + STILE
    px1 = px0 + pw
    cx0 = px1 + MULLION
    cx1 = cx0 + COL_W
    zd0, zd1 = z0 + KICK_H, z1 - REVEAL
    pz0 = zd0 + BOTTOM_RAIL
    pz1 = zd1 - TOP_RAIL
    fx0, fx1 = px0 + FLAP_MARGIN, px1 - FLAP_MARGIN
    fz0 = zd0 + FLAP_BOTTOM
    fz1 = fz0 + FLAP_H
    back = yf + DOOR_T + BURY          # where every insert ends, in the cabinet
    yc = yf + COL_SET                  # the column plate's face
    cxm = (cx0 + cx1) / 2.0

    L = {"w": w, "d": d, "h": h, "z0": z0, "yf": yf,
         "panel_m": (pw, ph),
         "apertures": {"panel": (px0, px1, pz0, pz1), "column": (cx0, cx1, pz0, pz1),
                       "flap": (fx0, fx1, fz0, fz1)},
         "door": {"xs": (xd0, px0, fx0, fx1, px1, cx0, cx1, xd1),
                  "zs": (zd0, fz0, fz1, pz0, pz1, zd1),
                  "y": (yf, yf + DOOR_T)}}
    L["cabinet"] = _box(-w / 2.0, w / 2.0, yf + DOOR_T - BURY, d / 2.0, z0, z1)
    L["panel"] = _box(px0 - BURY, px1 + BURY, yf + PANEL_SET, back, pz0 - BURY, pz1 + BURY)
    L["column_plate"] = _box(cx0 - BURY, cx1 + BURY, yc, back, pz0 - BURY, pz1 + BURY)
    L["bin"] = _box(fx0 - BURY, fx1 + BURY, yf + BIN_SET, back, fz0 - BURY, fz1 + BURY)
    L["kick"] = _box(xd0 + 0.012, xd1 - 0.012, yf + KICK_SET, back,
                     z0 + KICK_LIFT, zd0 + BURY)
    # the flap: hinged at the top, its bottom edge swung toward the room
    L["flap"] = {"x": (fx0 - BURY, fx1 + BURY),
                 "top": (fz1 + BURY, yf + FLAP_TOP_SET),
                 "bottom": (fz0 + 0.012, yf + FLAP_BOTTOM_SET),
                 "t": FLAP_T}

    # --- the column, from its top down ---------------------------------------------
    tz = pz1
    behind = yc + BURY
    dz = tz - 0.06
    L["display_bezel"] = _centred(cxm, dz, 0.13, 0.05, yf + 0.016, behind)
    L["display_lens"] = _centred(cxm, dz, 0.10, 0.032, yf + 0.011, yf + 0.016 + BURY)
    mz = tz - 0.18
    L["coin_mech"] = _centred(cxm, mz, 0.15, 0.15, yf + 0.018, behind)
    front_of_mech = yf + 0.018 + BURY
    L["coin_slot"] = _centred(cxm + 0.04, mz + 0.03, 0.010, 0.040, yf + 0.012, front_of_mech)
    L["bill_mouth"] = _centred(cxm - 0.02, mz - 0.035, 0.085, 0.012, yf + 0.012, front_of_mech)
    L["reject"] = _centred(cxm + 0.045, mz - 0.035, 0.022, 0.022, yf + 0.012, front_of_mech)
    top = mz - 0.075 - 0.03
    L["buttons"] = []
    for i in range(N_BUTTONS):
        bz = top - BUTTON[1] / 2.0 - i * BUTTON_PITCH
        L["buttons"].append(_centred(cxm, bz, BUTTON[0], BUTTON[1], yf + 0.010, behind))
    last = top - (N_BUTTONS - 1) * BUTTON_PITCH - BUTTON[1]
    rz = last - 0.04 - 0.035
    L["coin_return"] = _centred(cxm, rz, 0.09, 0.07, yf + 0.012, behind)
    L["return_mouth"] = _centred(cxm, rz - 0.01, 0.06, 0.025, yf + 0.006, yf + 0.012 + BURY)
    lz = rz - 0.035 - 0.07
    L["lock"] = _centred(cxm, lz, 0.035, 0.06, yf + 0.014, behind)
    L["lock_handle"] = _centred(cxm, lz, 0.012, 0.045, yf + 0.004, yf + 0.014 + BURY)
    if L["lock"][4] < pz0 + 0.02:
        raise ValueError(f"slot height {h} leaves no room for the column")
    return L


#: Every plain box part (not the door grid, not the flap), by name.
BOX_PARTS = ("cabinet", "panel", "column_plate", "bin", "kick", "display_bezel",
             "display_lens", "coin_mech", "coin_slot", "bill_mouth", "reject",
             "coin_return", "return_mouth", "lock", "lock_handle")


def boxes(L):
    """[(part, box)] for every box, the buttons one row each."""
    out = [(k, L[k]) for k in BOX_PARTS]
    out += [("buttons", b) for b in L["buttons"]]
    return out


def door_cells(L):
    """The door as a grid: (xs, zs, filled) where filled[i][j] says whether
    column i, row j is door (True) or aperture (False)."""
    xs, zs = L["door"]["xs"], L["door"]["zs"]
    holes = list(L["apertures"].values())
    filled = []
    for i in range(len(xs) - 1):
        col = []
        cx = (xs[i] + xs[i + 1]) / 2.0
        for j in range(len(zs) - 1):
            cz = (zs[j] + zs[j + 1]) / 2.0
            inside = any(a[0] < cx < a[1] and a[2] < cz < a[3] for a in holes)
            col.append(not inside)
        filled.append(col)
    return xs, zs, filled


def door_boundary_edges(filled):
    """Count of cell edges with door on one side only (the door's walls)."""
    ni, nj = len(filled), len(filled[0])
    n = 0
    for i in range(ni):
        for j in range(nj):
            if not filled[i][j]:
                continue
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = i + di, j + dj
                if not (0 <= a < ni and 0 <= b < nj) or not filled[a][b]:
                    n += 1
    return n


def triangles(L):
    """What the recipe emits: 12 per box, 12 for the flap, and the door's
    grid -- two per cell face front and back, two per wall."""
    _xs, _zs, filled = door_cells(L)
    cells = sum(sum(1 for f in col if f) for col in filled)
    return 12 * len(boxes(L)) + 12 + 4 * cells + 2 * door_boundary_edges(filled)


def extents(L):
    """(xmin, xmax, ymin, ymax, zmin, zmax) over every part."""
    bx = [b for _k, b in boxes(L)]
    xs, zs = L["door"]["xs"], L["door"]["zs"]
    y0, y1 = L["door"]["y"]
    bx.append((xs[0], xs[-1], y0, y1, zs[0], zs[-1]))
    f = L["flap"]
    ys = (f["top"][1], f["bottom"][1], f["top"][1] + f["t"], f["bottom"][1] + f["t"])
    bx.append((f["x"][0], f["x"][1], min(ys), max(ys), f["bottom"][0], f["top"][0]))
    return tuple(fn(b[k] for b in bx) for k in range(6)
                 for fn in ((min,) if k % 2 == 0 else (max,)))


# --- brand ---------------------------------------------------------------------------

_VARIANT = re.compile(r"_n\d+(?=_|$)")


def pick_brand(plan, streams=None):
    """The machine's brand id, deterministically.

    In order: an explicit ``params.brand`` from the table; for a module, the
    brand at index ``variant`` of an order drawn from the stem WITHOUT its
    variant suffix -- so the variants of one slot are always different
    brands, and variant 0 of two different stems usually differ too; for a
    prompt-built specimen, a draw from its own stream.
    """
    asked = (plan.get("params") or {}).get("brand")
    if asked and asked in brand_table.BY_ID:
        return asked
    module = plan.get("module") or {}
    stem = module.get("stem")
    if stem:
        base = _VARIANT.sub("", stem)
        order = sorted(brand_table.IDS,
                       key=lambda i: (zlib.crc32(f"{base}:{i}".encode("utf-8")), i))
        return order[int(module.get("variant") or 0) % len(order)]
    if streams is not None:
        return streams.stream("vending_brand").choice(brand_table.IDS)
    return brand_table.IDS[0]


def lineup(brand_id, key=""):
    """The six products behind the buttons: the machine's own brand first,
    then five others in an order drawn from ``key``."""
    others = sorted((i for i in brand_table.IDS if i != brand_id),
                    key=lambda i: (zlib.crc32(f"{key}:{brand_id}:{i}".encode("utf-8")), i))
    return [brand_id] + others[:N_BUTTONS - 1]


def paint_for(plan, brand):
    """Cabinet paint: the brand's, unless the prompt asked for a colour (a
    plan colour that differs from its style block's)."""
    block = plan.get("style_block") or {}
    colour = [round(float(c), 4) for c in plan.get("color", [])]
    styled = [round(float(c), 4) for c in block.get("color", colour)]
    if colour and colour != styled:
        return tuple(colour)
    return tuple(brand_table.srgb_to_linear(c) for c in brand_table.hex_rgb(brand["cabinet"]))


# --- raster ------------------------------------------------------------------------------

_BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


class Canvas:
    """An RGB raster, row 0 at the top."""

    def __init__(self, w, h, rgb=(0, 0, 0)):
        self.w, self.h = int(w), int(h)
        self.buf = bytearray(bytes(rgb) * (self.w * self.h))

    def px(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(rgb)

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return tuple(self.buf[i:i + 3])

    def rect(self, x0, y0, x1, y1, rgb):
        x0, x1 = max(0, int(x0)), min(self.w, int(x1))
        y0, y1 = max(0, int(y0)), min(self.h, int(y1))
        if x1 <= x0:
            return
        row = bytes(rgb) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def mask(self, m, ox, oy, rgb, grow=0):
        """Stamp a mask at (ox, oy); ``grow`` dilates it by a square of that
        radius first (an outline)."""
        if grow <= 0:
            for y, r in enumerate(m):
                for x, v in enumerate(r):
                    if v:
                        self.px(ox + x, oy + y, rgb)
            return
        done = set()
        for y, r in enumerate(m):
            for x, v in enumerate(r):
                if not v:
                    continue
                for yy in range(y - grow, y + grow + 1):
                    for xx in range(x - grow, x + grow + 1):
                        if (xx, yy) not in done:
                            done.add((xx, yy))
                            self.px(ox + xx, oy + yy, rgb)

    def paste(self, other, ox, oy):
        for y in range(other.h):
            ty = oy + y
            if not 0 <= ty < self.h:
                continue
            src = other.buf[y * other.w * 3:(y + 1) * other.w * 3]
            i = (ty * self.w + ox) * 3
            self.buf[i:i + len(src)] = src

    def png(self):
        """The raster as PNG bytes: 8-bit RGB, filter 0, zlib level 9 -- the
        same bytes for the same pixels, every build."""
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.buf[y * stride:(y + 1) * stride]

        def chunk(tag, data):
            body = tag + data
            return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))


def _lerp(a, b, t):
    return tuple(int(round(a[k] + (b[k] - a[k]) * t)) for k in range(3))


def luminance(rgb):
    """WCAG relative luminance of an sRGB 0..255 colour."""
    lin = [brand_table.srgb_to_linear(c) for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


EMBLEMS = ("disc", "burst", "bubbles", "drop", "stripes", "wave")


def _emblem(c, brand, cx, cy, r):
    col = brand_table.hex_rgb(brand["emblem"])
    edge = brand_table.hex_rgb(brand["edge"])
    shape = brand["shape"]
    seed = zlib.crc32(brand["id"].encode("utf-8"))
    if shape == "disc":
        for y in range(int(cy - r - 3), int(cy + r + 4)):
            for x in range(int(cx - r - 3), int(cx + r + 4)):
                dd = math.hypot(x - cx, y - cy)
                if dd <= r:
                    c.px(x, y, col)
                elif dd <= r + 3:
                    c.px(x, y, edge)
    elif shape == "burst":
        for y in range(int(cy - r), int(cy + r + 1)):
            for x in range(int(cx - r), int(cx + r + 1)):
                a = math.atan2(y - cy, x - cx)
                rr = r * (0.62 + 0.38 * (1.0 if math.cos(8 * a) > 0.0 else 0.0))
                if math.hypot(x - cx, y - cy) <= rr:
                    c.px(x, y, col)
    elif shape == "bubbles":
        for k in range(7):
            s = (seed >> (k * 3)) & 0x3F
            bx = cx + (((s * 37) % 100) / 100.0 - 0.5) * 1.6 * r
            by = cy + (((s * 61 + k * 29) % 100) / 100.0 - 0.5) * 1.8 * r
            br = r * (0.14 + 0.08 * (k % 3))
            for y in range(int(by - br - 2), int(by + br + 3)):
                for x in range(int(bx - br - 2), int(bx + br + 3)):
                    dd = math.hypot(x - bx, y - by)
                    if br - 2 <= dd <= br:
                        c.px(x, y, col)
                    elif dd < br * 0.35 and x < bx and y < by:
                        c.px(x, y, col)
    elif shape == "drop":
        for y in range(int(cy - 1.6 * r), int(cy + r + 1)):
            for x in range(int(cx - r), int(cx + r + 1)):
                if y >= cy:
                    inside = math.hypot(x - cx, y - cy) <= r
                else:
                    half = r * (y - (cy - 1.6 * r)) / (1.6 * r)
                    inside = abs(x - cx) <= half
                if inside:
                    c.px(x, y, col)
    elif shape == "stripes":
        band = max(4, int(r / 3))
        for y in range(int(cy - r), int(cy + r)):
            for x in range(c.w):
                if ((x + y) // band) % 3 == 0:
                    c.px(x, y, col)
    elif shape == "wave":
        amp, thick = r * 0.25, max(3, int(r * 0.18))
        for k in (-1, 0, 1):
            for x in range(c.w):
                yy = cy + k * r * 0.6 + amp * math.sin(x * 2 * math.pi / max(8, c.w / 1.5))
                for y in range(int(yy - thick / 2), int(yy + thick / 2) + 1):
                    c.px(x, y, col)
    else:
        raise ValueError(f"brand {brand['id']}: unknown emblem {shape!r}")


def _logo_scales(lines, max_w, max_h):
    """A whole scale per logo line: each line as large as fits the width, but
    never more than one step above the smallest line (so SCRAPPLE over SODA
    reads as one mark, not a word and a headline), and the stack within
    ``max_h`` (cap height 9 px and a 3 px gap per scale unit)."""
    fits = [pt.fit_scale(t, max_w) for t in lines]
    if min(fits) < 1:
        raise ValueError(f"logo {lines!r}: a line is wider than {max_w} px at scale 1")
    floor = min(fits)
    scales = [min(f, floor + 1) for f in fits]
    while sum(12 * s for s in scales) > max_h and max(scales) > 1:
        k = scales.index(max(scales))
        scales[k] -= 1
    return scales


def _slogan_layout(text, max_w, max_h):
    """(scale, lines): the largest scale whose wrap fits ``max_h``."""
    for s in (3, 2, 1):
        lines = pt.wrap(text, max_w, s)
        if lines is not None and len(lines) * pt.LINE * s <= max_h:
            return s, lines
    lines = pt.wrap(text, max_w, 1)
    if lines is None:
        raise ValueError(f"slogan {text!r}: a word is wider than {max_w} px")
    return 1, lines


def paint_panel(brand, pw_px, ph_px):
    """The backlit panel's artwork. Returns (canvas, facts)."""
    top = brand_table.hex_rgb(brand["bg"][0])
    bottom = brand_table.hex_rgb(brand["bg"][1])
    ink = brand_table.hex_rgb(brand["ink"])
    edge = brand_table.hex_rgb(brand["edge"])
    s_ink = brand_table.hex_rgb(brand["slogan_ink"])
    c = Canvas(pw_px, ph_px)
    steps = 7
    for y in range(ph_px):
        lv = steps * y / max(1, ph_px - 1)
        row = _BAYER[y % 4]
        for x in range(pw_px):
            k = min(steps, int(lv + row[x % 4] / 16.0))
            c.px(x, y, _lerp(top, bottom, k / steps))
    margin = max(4, pw_px // 32)
    # the emblem, between the drink line and the slogan
    _emblem(c, brand, pw_px / 2.0, ph_px * 0.53, pw_px * 0.42)

    # logo
    # the logo needs to clear only the frame and its own 1 px outline and
    # shadow, not the text margin: at the 0.85 m slot Deli Counter asks for,
    # SCRAPPLE at scale 2 is 126 px of ink on a 135 px panel
    fr = max(2, pw_px // 64)
    scales = _logo_scales(brand["logo"], pw_px - 2 * fr - 3, int(ph_px * 0.40))
    y = margin + 2
    logo_rows = []
    for line, s in zip(brand["logo"], scales):
        grow = 1
        m = pt.trim(pt.render(line, s))
        x = (pw_px - len(m[0])) // 2
        c.mask(m, x + grow, y + grow, edge, grow=grow)       # drop shadow
        c.mask(m, x, y, edge, grow=grow)
        c.mask(m, x, y, ink)
        logo_rows.append((line, s, x, y, len(m[0]), len(m)))
        y += len(m) + 3 * s + grow
    logo_bottom = y

    # the drink, small, under the logo. Text below clears only the frame: the
    # genome's narrowest machine has a 97 px panel, and "CHEESESTEAK" is 87 px
    text_w = pw_px - 2 * fr - 4
    drink = pt.wrap(brand["drink"].upper(), text_w, 1)
    if drink is None:
        raise ValueError(f"brand {brand['id']}: a drink word is wider than {text_w} px")
    y += 2
    for line in drink:
        m = pt.trim(pt.render(line, 1))
        x = (pw_px - len(m[0])) // 2
        c.mask(m, x, y, edge, grow=1)
        c.mask(m, x, y, s_ink)
        y += len(m) + 4

    # the slogan on a band of the outline colour at the bottom
    # 30 % of the panel: at Deli Counter's 1.0 m machine that lets 11 of the
    # 12 slogans set at scale 2 (26 %: 5), which is the difference between a
    # 9 px and a 4 px cap at 4.7 m in a 1600 x 900 frame. At 0.85 m the width
    # is the limit and this changes nothing.
    ss, lines = _slogan_layout(brand["slogan"], text_w, int(ph_px * 0.30))
    block = len(lines) * pt.LINE * ss
    pad = 3 * ss
    by1 = ph_px - margin
    by0 = by1 - block - 2 * pad
    c.rect(0, by0, pw_px, by1, edge)
    yy = by0 + pad
    for line in lines:
        m = pt.render(line, ss)
        x = (pw_px - pt.ink_width(line, ss)) // 2
        c.mask(m, x, yy, s_ink)
        yy += pt.LINE * ss

    # the frame
    c.rect(0, 0, pw_px, fr, edge)
    c.rect(0, ph_px - fr, pw_px, ph_px, edge)
    c.rect(0, 0, fr, ph_px, edge)
    c.rect(pw_px - fr, 0, pw_px, ph_px, edge)
    return c, {"logo_scale": scales, "logo": logo_rows, "logo_bottom": logo_bottom,
               "slogan_scale": ss, "slogan_lines": lines, "slogan_band": (by0, by1),
               "drink_lines": drink}


def label_colours(brand):
    """(background, text) for a product's button: the darker of its two
    background colours, and whichever of its own colours reads best on it."""
    a, b = (brand_table.hex_rgb(v) for v in brand["bg"])
    bg = a if luminance(a) < luminance(b) else b
    cands = [brand_table.hex_rgb(brand[k]) for k in ("ink", "slogan_ink", "edge", "emblem")]
    cands += [(255, 255, 255), (16, 16, 16)]
    return bg, max(cands, key=lambda col: contrast(col, bg))


def paint_label(brand, lw, lh):
    bg, fg = label_colours(brand)
    c = Canvas(lw, lh, bg)
    edge = brand_table.hex_rgb(brand["edge"])
    c.rect(0, 0, lw, 1, edge)
    c.rect(0, lh - 1, lw, lh, edge)
    c.rect(0, 0, 1, lh, edge)
    c.rect(lw - 1, 0, lw, lh, edge)
    m = pt.trim(pt.render(brand["short"], 1))
    c.mask(m, (lw - len(m[0])) // 2, (lh - len(m)) // 2, fg)
    return c


def paint_display(dw, dh):
    c = Canvas(dw, dh, (8, 8, 8))
    m = pt.trim(pt.render(PRICE, 1))
    c.mask(m, (dw - len(m[0])) // 2, (dh - len(m)) // 2, brand_table.hex_rgb(LED))
    return c


def art(L, brand_id, key=""):
    """The machine's one texture: panel, six labels, the display and a dark
    patch, packed side by side. Returns a dict with the canvas, its pixel
    rects (x0, y0, x1, y1, row 0 at the top) and a name unique to its
    pixels' inputs."""
    brand = brand_table.BY_ID[brand_id]
    pw_m, ph_m = L["panel_m"]
    pw, ph = int(round(pw_m * TEXEL)), int(round(ph_m * TEXEL))
    lw, lh = int(round(BUTTON[0] * LABEL_TEXEL)), int(round(BUTTON[1] * LABEL_TEXEL))
    dx0, dz0 = L["display_lens"][0], L["display_lens"][4]
    dw = int(round((L["display_lens"][1] - dx0) * LABEL_TEXEL))
    dh = int(round((L["display_lens"][5] - dz0) * LABEL_TEXEL))
    products = lineup(brand_id, key)
    side = max(lw, dw)
    W = pw + 2 + side + 2
    stack = N_BUTTONS * (lh + 2) + dh + 2 + 6
    H = max(ph, stack)
    canvas = Canvas(W, H, (10, 10, 12))
    panel, facts = paint_panel(brand, pw, ph)
    canvas.paste(panel, 0, 0)
    rects = {"panel": (0, 0, pw, ph)}
    x = pw + 2
    y = 0
    for i, pid in enumerate(products):
        canvas.paste(paint_label(brand_table.BY_ID[pid], lw, lh), x, y)
        rects[f"button_{i}"] = (x, y, x + lw, y + lh)
        y += lh + 2
    canvas.paste(paint_display(dw, dh), x, y)
    rects["display"] = (x, y, x + dw, y + dh)
    y += dh + 2
    rects["dark"] = (x, y, x + 4, y + 4)
    digest = zlib.crc32(bytes(canvas.buf)) & 0xFFFFFFFF
    return {"canvas": canvas, "rects": rects, "size": (W, H), "products": products,
            "brand": brand_id, "facts": facts,
            "name": f"{brand_id}_{W}x{H}_{digest:08x}"}


def uv_rect(rect, size):
    """A pixel rect -> (u0, v0, u1, v1), v up (Blender and glTF read a
    PNG's first row as the TOP of the image, v = 1 there)."""
    x0, y0, x1, y1 = rect
    W, H = size
    return (x0 / W, 1.0 - y1 / H, x1 / W, 1.0 - y0 / H)


def resolve(plan, streams=None):
    dims = plan["dimensions"]
    L = layout(float(dims["width"]), float(dims["depth"]), float(dims["height"]))
    bid = pick_brand(plan, streams)
    module = plan.get("module") or {}
    key = _VARIANT.sub("", module.get("stem") or "") or bid
    L["brand"] = bid
    L["art"] = art(L, bid, key)
    L["paint"] = paint_for(plan, brand_table.BY_ID[bid])
    return L
