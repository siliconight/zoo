"""The 1990s coin payphone: its three enclosures, the instrument, the armoured
cord, and its paint -- pure Python, no bpy.

Zoo 1.88.0, roadmap 210. The walker, 2026-10-08: "In the 90s you would pay
with quarters, and the phone is not wireless, it's on a metal cord", with
three photographs read for format only (`docs/reference/PAYPHONE_COMPS.md`).
The walker again, 2026-10-09, on the 1.87.0 frames: the payphone "doesn't
have a phone or appropriate decals". It is also the modern low-poly
standard's second worked example ("a selected close prop": readable text, a
low-sided cable, a real coin-return recess, 1,500-2,500 triangles, one
opaque material where practical).

WHAT IS BUILT (metres, Z up, origin at the ground under the middle, the
caller at -Y), by form:

  booth     (the default, ``auto``): a square post, and on it an enclosure --
            a back panel, two side panels, a flat roof -- with a header
            fascia under the roof's front edge reading PHONE beside the
            company's mark, and a shelf under the instrument.
  pedestal  a compact shroud on the post: short sides round the instrument,
            the roof, no header and no shelf, and the handset pictogram on
            each side panel's outer face.
  wall      no post: the booth's enclosure standing off a wall at the slot's
            back (+Y), with a phone-book binder hanging under the shelf.

And in every form, at its real size whatever the slot:

  the instrument  a stainless coin phone on the back panel: twelve keys proud
                  of a printed face, the coin slot high in a raised bezel, the
                  coin-return RECESS (a real hole, the standard's ask), the
                  coin vault's door with its lock, the instruction card, and
                  the hook-switch cradle on its left with the handset hung in
                  it;
  the cord        an armoured steel sleeve: one swept tube from the
                  handset's foot, down below the instrument and back up into
                  its side.

TWO ATLASES, TWO DRAWS (1.89.0; 1.88.0 drew one). Every prim names a tile;
the paint, the steel, the black plastic and every word are pixels in one image
(`recipes/_card_atlas.build_art`). 1.87.0's payphone was three materials and
three draws of boxes. The second atlas is the LIT one -- the header's face and
the hood's diffuser, their art their own light as well as paint -- and its
material is named `_Face`, so Lux's power cut takes it: the ATM's topper
(`atm_forms`).

THE HOOD LAMP (1.89.0). Cold run 9212 stood a booth at a bus stop, and at
midnight it was a silhouette: no light reached the card, the keys or the
stickers. A real booth's tube sits in its canopy right behind the header,
backlighting the sign and lighting the instrument below it. So the diffuser
hangs under the roof just behind the header (in a pedestal, which has none,
just behind the roof's front edge), and `LAMP` hangs LAMP_EMIT under its
face, in free air -- a lamp inside closed hardware bakes to nothing (Lux
0.65.0's pole, 0.67.0's bulbs) -- carrying `lux_drop`, its height above the
ground, from which Lux's `payphone_hood` row (Lux >= 0.70.0) solves the
lamp's range and energy. Where it hangs was measured, not chosen: with a lamp
stood live in cold run 9212's package (`docs/findings/payphone_light/`),
behind the header the card takes 0.42 per unit of the lamp's energy and the
back panel's top 5.9, against 0.27 and 11.4 with the lamp mid-hood -- the
hot spot halved and the card lit half again.

NO TWO FACES ON ONE PLANE. Every part that rests on another goes into it by
`INSET`, and every face that would lie in a neighbour's plane steps back by
it: twice the coplanar probe's 2 mm window, the cruiser's rule
(`cruiser_forms.INSET`). `prims.coincident_pairs` holds it at every size.

EVERY NAME IS INVENTED: Delco slang, PG-13, held against the factory's
denylists and the real telephone companies and payphone makers of the
1990s (`tests/test_payphone.py`). The Philadelphia area's own phone company
of the time is exactly the kind of mark this must not echo.
"""
from __future__ import annotations

import math
import zlib

from . import machine_parts as MP
from . import paint as PT
from . import prims as P
from . import smooth_type as ST

FORMS = ("booth", "pedestal", "wall")
DEFAULT_FORM = "booth"

#: The phone company. "Youse" is Delco for you lot; the company is the one
#: whose name the whole county already says.
COMPANY = "YOUSETEL"
COMPANY_LINE = "YOUSE TALK. WE TOLL."
#: The instruction card: a notice nobody designed (`smooth_type.OWNERS`).
CARD_LINES = ("LOCAL CALL 25 CENTS", "1  LIFT HANDSET", "2  DEPOSIT COIN",
              "3  DIAL NUMBER", "EMERGENCY 911  NO COIN")
#: What the maker moulded into the face, and the header's word.
FACE_WORDS = ("25 CENTS", "COIN RETURN", "PHONE")
#: Stuck on by somebody else: the shop's hand (`smooth_type.OWNERS`). A
#: bandit sign's number, a pager's, a dare. 555-01xx is the fictional
#: exchange (`dumpster_forms.HAULERS`).
STICKERS = (("WE BUY HOUSES", "CASH", "610-555-0186"),
            ("BEEPER BROKE?", "PAGE ME", "610-555-0131"),
            ("CALL YA MOM", "SHE'S WORRIED", ""))
BINDER_LINES = ("YOUSETEL", "DIRECTORY", "DELCO 1997")
KEYS = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#")

MAKER = ST.owned("maker")
MAKER_SMALL = ST.owned("maker_small")
NOTICE = ST.owned("notice")
NOTICE_BOLD = ST.owned("notice_bold")
SHOP = ST.owned("shop")

#: Every part that rests on another goes into it by this much, and every face
#: that would share a neighbour's plane steps back by it.
INSET = 0.004

# --- the enclosure ---------------------------------------------------------------------
T_BACK = 0.025            # the back panel
T_SIDE = 0.020            # a side panel
T_ROOF = 0.045            # the roof
POST = 0.075              # the post, square
BACK_BELOW = 0.10         # the back panel runs below the side panels by this
HEADER_H = 0.15           # the header fascia under the roof's front edge
T_HEADER = 0.020
SHELF_D = 0.20            # the shelf, front to back
T_SHELF = 0.025
SHELF_UNDER = 0.06        # the shelf's top below the instrument's foot
SHELF_CLEAR = 0.035       # the shelf's left end, right of the cord
PED_BELOW = 0.12          # a pedestal's sides start this far below the instrument
PED_ABOVE = 0.16          # ...and its roof this far above it
CONDUIT = 0.030           # the wall form's line conduit, square, down to the ground
BINDER = (0.20, 0.045, 0.27)     # w, d, h
BINDER_HANG = 0.02        # the binder's top below the shelf's foot
BINDER_RING = 0.008       # its rings' radius

# --- the hood lamp (1.89.0) ------------------------------------------------------------
LENS_D = 0.070            # the diffuser, front to back
LENS_T = 0.014            # how far it hangs under the roof
LENS_GAP = 0.010          # its front behind the header's back face (a pedestal's roof edge)
LENS_END = 0.030          # each end in from a side panel's inner face
LAMP_EMIT = 0.030         # the lamp's marker under the diffuser's face
#: The marker `LuxFixtureSpawner` stands the lamp at; it reads the type from
#: `lux_type`, and from the name when that is absent.
LAMP = "LuxEmit_payphone_hood"
LAMP_TYPE = "payphone_hood"
#: The lit atlas's tiles, and its emission and diffuse copy (the ATM's,
#: `atm_forms.GLOW_EMISSION` and `GLOW_ALBEDO`).
GLOW_TILES = ("header", "lens")
GLOW_EMISSION = 1.0
GLOW_ALBEDO = 0.6

# --- the instrument, at its real size ------------------------------------------------------
INST = (0.19, 0.11, 0.50)        # w, d, h
INST_FOOT = 1.00                 # its foot above the ground, where the slot allows
INST_X = 0.04                    # its centre right of the slot's, so the handset hangs inside
KEY = (0.019, 0.008, 0.017)      # a key: w, proud, h
KEY_PITCH = (0.026, 0.024)
KEYPAD_Z = 0.27                  # the keypad's centre above the instrument's foot
SLOT_BEZEL = (0.040, 0.012, 0.050)
SLOT_BEZEL_AT = (0.050, 0.455)   # its centre from the instrument's centre line, and up
SLOT_HOLE = (0.006, 0.028)       # the coin slot in the bezel's face
SLOT_DEPTH = 0.009
RETURN_HOLE = (0.050, 0.034)     # the coin-return opening: w, h
RETURN_AT = (0.040, 0.150)       # its centre from the centre line, and up
RETURN_DEPTH = 0.030
VAULT = (0.100, 0.006, 0.090)    # the coin vault's door: w, proud, h
VAULT_Z = 0.060
LOCK_R = 0.011
LOCK_PROUD = 0.010
CARD = (0.130, 0.066)            # the instruction card, printed: w, h
CARD_Z = 0.380                   # its centre above the foot
CRADLE = (0.030, 0.070, 0.050)   # out from the left face, front to back, tall
CRADLE_TOP = 0.040               # its top below the instrument's top
GRIP = (0.040, 0.040, 0.150)     # the handset's grip
CUP_R = 0.030                    # each cup's radius
CUP_HALF = 0.025                 # each cup's half-length, sideways
CORD_R = 0.0065
CORD_SIDES = 8
CORD_ENTRY_Z = 0.100             # where it goes into the instrument's left face, above the foot
CORD_DROP = 0.24                 # how far below the instrument's foot its loop hangs
CORD_SAMPLES = 6                 # points a span of its spline

# --- the paint ---------------------------------------------------------------------------
TEXEL = 160                      # pixels a metre of plain paint
FACE_TEXEL = 640                 # ...of the instrument's printed face
HEADER_TEXEL = 300
#: The narrowest header the company's line sets on beside PHONE and the
#: name, measured: it set at 0.66 m and did not at 0.61. A narrower header
#: carries the name alone, by the plan's word, never by a dropped line.
HEADER_LINE_W = 0.66
STICKER_TEXEL = 800              # ...of a sticker, so its lines set
#: A sticker's size, and where each stands on the back panel's front face:
#: (left edge from the instrument's right side, foot above its foot) for the
#: two by the coin slot side, and (left edge in from the left side panel,
#: foot above the instrument's foot) for the one low under the handset.
STICKER = (0.110, 0.065)
STICKER_AT = (("right", 0.030, 0.300), ("right", 0.030, 0.205), ("left", 0.025, -0.110))
STEEL = (176, 180, 184)
STEEL_DARK = (120, 124, 128)
BLACK = (22, 22, 24)
DARK = (10, 10, 11)
POST_BLACK = (30, 31, 33)
WHITE = (238, 236, 228)
HEADER_INK = (250, 250, 246)
CARD_PAPER = (232, 230, 220)
CARD_INK = (24, 26, 30)
RED = (176, 32, 30)
LENS_WHITE = (232, 240, 234)     # a lit diffuser, with the tube's faint green
LENS_TUBE = (252, 253, 248)      # the tube's line through it


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def _srgb8(lin):
    c = 12.92 * lin if lin <= 0.0031308 else 1.055 * lin ** (1.0 / 2.4) - 0.055
    return max(0, min(255, int(round(255.0 * c))))


def _lift(rgb, by):
    return tuple(max(0, min(255, c + by)) for c in rgb)


def resolve_form(asked):
    """``auto``, None and "" are the booth; a name not in `FORMS` is refused."""
    if asked in (None, "", "auto"):
        return DEFAULT_FORM
    if asked not in FORMS:
        raise ValueError(f"payphone: no form {asked!r}; the forms are {', '.join(FORMS)}")
    return asked


# --- the shape -------------------------------------------------------------------------


def _box(part, tile, lo, hi, skip=()):
    """An axis-aligned box as quads, each wound and mapped as its viewer sees
    it (`dumpster_forms._box`); ``skip`` names faces left out because they lie
    inside another part. ``tile`` is one name, or a dict by face with "*"."""
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


def _flat(p, tile):
    """A prim whose every corner samples the middle of a flat tile."""
    p["tile"] = tile
    p["uvs"] = [[(0.5, 0.5)] * len(f) for f in p["faces"]]
    return p


def _printed(part, tile, frame, x0, x1, z0, z1, y):
    """One quad of the instrument's printed face at ``y``, mapped to the
    window of the face's tile it covers, so the print runs on across the
    quads the face is cut into round the coin return."""
    fx0, fx1, fz0, fz1 = frame
    u0, u1 = (x0 - fx0) / (fx1 - fx0), (x1 - fx0) / (fx1 - fx0)
    v0, v1 = (z0 - fz0) / (fz1 - fz0), (z1 - fz0) / (fz1 - fz0)
    return MP.quad(part, "paint", tile, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)],
                   uv=(u0, u1, v0, v1))


def _recess(prefix, tile_face, frame, outer, hole, y, depth):
    """A face ``outer`` = (x0, x1, z0, z1) at ``y`` with a real hole in it:
    four printed strips round the opening, four walls straight back into the
    body, and a dark back ``depth`` behind the face."""
    ox0, ox1, oz0, oz1 = outer
    hx0, hx1, hz0, hz1 = hole
    out = [_printed(f"{prefix}_Face_B", tile_face, frame, ox0, ox1, oz0, hz0, y),
           _printed(f"{prefix}_Face_T", tile_face, frame, ox0, ox1, hz1, oz1, y),
           _printed(f"{prefix}_Face_L", tile_face, frame, ox0, hx0, hz0, hz1, y),
           _printed(f"{prefix}_Face_R", tile_face, frame, hx1, ox1, hz0, hz1, y)]
    yi = y + depth
    out += MP.wells(prefix, hole, hole, y, yi, tile="dark")
    out.append(MP.quad(f"{prefix}_Back", "paint", "dark",
                       [(hx0, yi, hz0), (hx1, yi, hz0), (hx1, yi, hz1), (hx0, yi, hz1)]))
    return out


def _windowed(part, base, rect, y, windows):
    """A face ``rect`` = (x0, x1, z0, z1) at ``y``, looking at -Y, cut into a
    grid by its ``windows`` = [((x0, x1, z0, z1), tile), ...]: a cell inside
    a window shows that window's own tile, every other cell its window of
    ``base``, so the base's paint runs on round the windows."""
    x0, x1, z0, z1 = rect
    xs = sorted({x0, x1} | {v for (a, b, _c, _d), _t in windows for v in (a, b)})
    zs = sorted({z0, z1} | {v for (_a, _b, c, d), _t in windows for v in (c, d)})
    out = []
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            cx0, cx1, cz0, cz1 = xs[i], xs[i + 1], zs[j], zs[j + 1]
            mx, mz = (cx0 + cx1) / 2.0, (cz0 + cz1) / 2.0
            hit = next(((r, t) for r, t in windows if r[0] < mx < r[1] and r[2] < mz < r[3]), None)
            name = f"{part}_{i}_{j}"
            if hit is None:
                out.append(_printed(name, base, rect, cx0, cx1, cz0, cz1, y))
            else:
                out.append(_printed(name, hit[1], hit[0], cx0, cx1, cz0, cz1, y))
    return out


def stickers(L):
    """The stickers that fit on the back panel's front face, as windows:
    clear of the instrument, inside the side panels, none on another."""
    ix0, ix1, _yf, _yb, z0, z1 = L["inst"]
    sxi = L["w"] / 2.0 - INSET - T_SIDE
    sw, sh = STICKER
    out = []
    for k, (side, dx, dz) in enumerate(STICKER_AT):
        x0 = ix1 + dx if side == "right" else -sxi + dx
        r = (x0, x0 + sw, z0 + dz, z0 + dz + sh)
        clear = (r[1] < sxi - 0.01 and r[0] > -sxi + 0.01 and (r[1] < ix0 or r[0] > ix1 or r[3] < z0 or r[2] > z1)
                 and r[2] > L["z_enc0"] and all(r[1] <= o[0] or r[0] >= o[1] or r[3] <= o[2] or r[2] >= o[3]
                                                for o, _t in out))
        if clear:
            out.append((r, f"sticker_{k}"))
    return out


def _catmull(points, samples):
    """Points on a uniform Catmull-Rom spline through ``points``, ends kept."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for s in range(samples):
            t = s / float(samples)
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t
                                    + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3)
                             for k in range(3)))
    out.append(tuple(points[-1]))
    return out


def tube(part, tile, path, r, sides=CORD_SIDES):
    """One swept tube along ``path``: a ring of ``sides`` round every point,
    each ring turned by parallel transport so the tube does not twist, capped
    at both ends. Its corners sample the tile's middle across and run its
    height along the length, so a rib painted across the tile reads round
    the cord."""
    n = len(path)

    def sub(a, b):
        return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

    def unit(a):
        m = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
        return (a[0] / m, a[1] / m, a[2] / m)

    def cross(a, b):
        return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

    def dot(a, b):
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    tangents = []
    for i in range(n):
        a = path[min(i + 1, n - 1)]
        b = path[max(i - 1, 0)]
        tangents.append(unit(sub(a, b)))
    ref = (0.0, 0.0, 1.0) if abs(tangents[0][2]) < 0.9 else (1.0, 0.0, 0.0)
    u = unit(cross(tangents[0], ref))
    verts, lengths, run = [], [], 0.0
    phase = math.pi / sides
    for i, (p, a) in enumerate(zip(path, tangents)):
        if i:
            run += math.sqrt(dot(sub(p, path[i - 1]), sub(p, path[i - 1])))
            u = unit(sub(u, tuple(dot(u, a) * c for c in a)))
        v = cross(a, u)
        for k in range(sides):
            t = 2.0 * math.pi * k / sides + phase
            c, s = math.cos(t) * r, math.sin(t) * r
            verts.append(tuple(p[j] + u[j] * c + v[j] * s for j in range(3)))
        lengths.append(run)
    faces, uvs = [], []
    total = lengths[-1] or 1.0
    for i in range(n - 1):
        for k in range(sides):
            k1 = (k + 1) % sides
            a0, a1 = i * sides + k, i * sides + k1
            faces.append((a0, a1, a1 + sides, a0 + sides))
            va, vb = lengths[i] / total, lengths[i + 1] / total
            uvs.append([(0.5, va), (0.5, va), (0.5, vb), (0.5, vb)])
    faces.append(tuple(reversed(range(sides))))
    uvs.append([(0.5, 0.0)] * sides)
    last = (n - 1) * sides
    faces.append(tuple(range(last, last + sides)))
    uvs.append([(0.5, 1.0)] * sides)
    p = P.mesh(part, "paint", verts, faces)
    p["tile"] = tile
    p["uvs"] = uvs
    return p


def layout(form, w, d, h):
    """Where everything stands, in the slot's frame: the enclosure's planes,
    the instrument's box and the handset's, and the cord's path. Pure
    numbers; `plan` builds prims from them and the tests read them."""
    form = resolve_form(form)
    iw, idp, ih = INST
    y_back = d / 2.0                                             # the enclosure's back plane
    y_bp1 = y_back - 2.0 * INSET                                 # the back panel's back face
    y_bp0 = y_bp1 - T_BACK                                       # ...and its front
    y_face = y_bp0 + INSET - idp                                 # the instrument's face
    top = h
    z_ceiling = top - T_ROOF - (HEADER_H if form != "pedestal" else 0.0)
    inst_z0 = min(INST_FOOT, z_ceiling - ih - 0.04)
    if form == "pedestal":
        inst_z0 = min(INST_FOOT, top - T_ROOF - PED_ABOVE - ih)
        z_enc0 = inst_z0 - PED_BELOW
    else:
        z_enc0 = min(h * 0.40, inst_z0 - SHELF_UNDER - T_SHELF - 0.10)
    ix0, ix1 = INST_X - iw / 2.0, INST_X + iw / 2.0
    cradle_z1 = inst_z0 + ih - CRADLE_TOP
    cradle_z0 = cradle_z1 - CRADLE[2]
    gx = ix0 - GRIP[0] / 2.0 - 0.012                             # the handset's centre line
    gy = y_face + idp * 0.45
    ear_z = cradle_z0 - CUP_R * 0.6
    grip_z1 = ear_z
    grip_z0 = grip_z1 - GRIP[2]
    mouth_z = grip_z0
    cord_a = (gx, gy, mouth_z - CUP_R + INSET)                    # inside the mouth cup's foot
    cord_b = (ix0 + INSET, y_face + idp * 0.55, inst_z0 + CORD_ENTRY_Z)  # inside the left face
    low = inst_z0 - CORD_DROP
    path = _catmull([cord_a,
                     (gx - 0.004, gy - 0.035, cord_a[2] - 0.07),
                     (gx + 0.006, gy - 0.060, low + 0.02),
                     (ix0 - 0.012, gy - 0.050, low),
                     (ix0 - 0.016, gy - 0.025, cord_b[2] - 0.08),
                     (ix0 - 0.022, cord_b[1], cord_b[2] - 0.02),
                     cord_b], CORD_SAMPLES)
    shelf_x0 = max(x for x, _y, _z in path) + CORD_R + SHELF_CLEAR
    # the hood lamp (1.89.0): the diffuser just behind the header's back face
    # (a pedestal has no header: just behind the roof's front edge), between
    # the side panels, its top INSET into the roof; the lamp's marker
    # LAMP_EMIT under its face, in free air
    sxi = w / 2.0 - INSET - T_SIDE
    ly0 = -d / 2.0 + 2.0 * INSET + (T_HEADER if form != "pedestal" else 0.0) + LENS_GAP
    lz1 = top - T_ROOF
    lens = (-(sxi - LENS_END), sxi - LENS_END, ly0, ly0 + LENS_D, lz1 - LENS_T, lz1)
    lamp = (0.0, ly0 + LENS_D / 2.0, lz1 - LENS_T - LAMP_EMIT)
    return {"form": form, "w": w, "d": d, "h": h, "y_back": y_back, "y_bp0": y_bp0, "y_bp1": y_bp1,
            "y_face": y_face, "top": top, "z_enc0": z_enc0, "inst": (ix0, ix1, y_face, y_bp0 + INSET,
                                                                       inst_z0, inst_z0 + ih),
            "cradle_z": (cradle_z0, cradle_z1), "grip": (gx, gy, grip_z0, grip_z1),
            "ear_z": ear_z, "mouth_z": mouth_z, "cord": path, "shelf_x0": shelf_x0,
            "lens": lens, "lamp": lamp}


def _enclosure(L, prims):
    """The post, the panels, the roof, the header and the shelf, by form."""
    form, w, d, h = L["form"], L["w"], L["d"], L["h"]
    top, z0 = L["top"], L["z_enc0"]
    y_front = -d / 2.0
    sx = w / 2.0 - INSET                                   # a side panel's outer face
    sxi = sx - T_SIDE                                      # ...its inner face
    zr = top - T_ROOF
    paint = {"*": "shroud", "right": "side_in", "left": "side_in"}
    # the roof: the slot's footprint at its top
    prims += _box("Payphone_Roof", {"*": "shroud", "top": "roof", "under": "inside"},
                  (-w / 2.0, y_front, zr), (w / 2.0, d / 2.0, top))
    y_side1 = L["y_back"] - INSET
    for name, a, b, out_face in (("SideL", -sx, -sxi, "left"), ("SideR", sxi, sx, "right")):
        tiles = {"*": "shroud", out_face: "pictogram" if form == "pedestal" else "shroud",
                 ("right" if out_face == "left" else "left"): "side_in"}
        prims += _box(f"Payphone_{name}", tiles, (a, y_front + INSET, z0), (b, y_side1, zr + INSET),
                      skip=("top",))
    # the back panel, between the sides and into them, running below them;
    # its front face cut round the stickers so each samples its own tile
    rect = (-sxi - INSET, sxi + INSET, z0 - BACK_BELOW, zr + INSET)
    prims += _box("Payphone_Back", "shroud", (rect[0], L["y_bp0"], rect[2]), (rect[1], L["y_bp1"], rect[3]),
                  skip=("top", "front"))
    prims += _windowed("Payphone_BackFace", "back_in", rect, L["y_bp0"], stickers(L))
    if form != "pedestal":
        # the header fascia under the roof's front edge, between the sides
        prims += _box("Payphone_Header", {"*": "shroud", "front": "header"},
                      (-sxi - INSET, y_front + 2.0 * INSET, zr - HEADER_H),
                      (sxi + INSET, y_front + 2.0 * INSET + T_HEADER, zr + INSET),
                      skip=("top", "left", "right"))
        # the shelf: right of the cord, from the back panel to the right side
        sz1 = L["inst"][4] - SHELF_UNDER
        prims += _box("Payphone_Shelf", "shelf",
                      (L["shelf_x0"], L["y_bp0"] - SHELF_D, sz1 - T_SHELF), (sxi + INSET, L["y_bp0"] + INSET, sz1),
                      skip=("back", "right"))
    # the hood lamp's diffuser (1.89.0): a lit face under a painted rim, its
    # top INSET into the roof
    lx0, lx1, ly0, ly1, lz0, lz1 = L["lens"]
    prims += _box("Payphone_Lens", {"*": "lens_rim", "under": "lens"},
                  (lx0, ly0, lz0), (lx1, ly1, lz1 + INSET), skip=("top",))
    if form != "wall":
        # the post, under the back panel and into it, its back face set in from the panel's
        py1 = L["y_bp1"] - INSET
        prims += _box("Payphone_Post", "post", (-POST / 2.0, py1 - POST, 0.0),
                      (POST / 2.0, py1, z0 - BACK_BELOW + INSET), skip=("under",))
    else:
        # the line's conduit down the wall into the ground, under the back panel
        cy1 = L["y_bp1"] - INSET
        cx = -sxi + 0.06
        prims += _box("Payphone_Conduit", "post", (cx - CONDUIT / 2.0, cy1 - CONDUIT, 0.0),
                      (cx + CONDUIT / 2.0, cy1, z0 - BACK_BELOW + INSET), skip=("under",))
        # the phone book, hanging on two rings under the shelf's foot
        sz0 = L["inst"][4] - SHELF_UNDER - T_SHELF
        bw, bd, bh = BINDER
        bx0 = L["shelf_x0"] + 0.03
        by1 = L["y_bp0"] - 0.02
        prims += _box("Payphone_Binder", {"*": "binder_edge", "front": "binder"},
                      (bx0, by1 - bd, sz0 - BINDER_HANG - bh), (bx0 + bw, by1, sz0 - BINDER_HANG))
        for k, fx in enumerate((0.25, 0.75)):
            x = bx0 + bw * fx
            prims.append(_flat(P.rod(f"Payphone_BinderRing{k}", "paint",
                                     (x, by1 - bd / 2.0, sz0 - BINDER_HANG - INSET),
                                     (x, by1 - bd / 2.0, sz0 + INSET), BINDER_RING, segments=6),
                               "steel"))
    return prims


def _instrument(L, prims):
    """The coin phone, the cradle, the handset and the cord."""
    ix0, ix1, yf, yb, z0, z1 = L["inst"]
    frame = (ix0, ix1, z0, z1)
    xc = (ix0 + ix1) / 2.0
    # the body: everything but the face, which is cut round the coin return
    prims += _box("Payphone_Inst", "steel", (ix0, yf, z0), (ix1, yb, z1), skip=("front", "back"))
    rx, rz = RETURN_AT
    rw, rh = RETURN_HOLE
    hole = (xc + rx - rw / 2.0, xc + rx + rw / 2.0, z0 + rz - rh / 2.0, z0 + rz + rh / 2.0)
    prims += _recess("Payphone_Return", "face", frame, (ix0, ix1, z0, z1), hole, yf, RETURN_DEPTH)
    # the keys, proud of the face, each showing its own legend's window
    kw, kp, kh = KEY
    px, pz = KEY_PITCH
    for i, label in enumerate(KEYS):
        col, row = i % 3, i // 3
        cx = xc + (col - 1) * px
        cz = z0 + KEYPAD_Z + (1.5 - row) * pz
        x0, x1, kz0, kz1 = cx - kw / 2.0, cx + kw / 2.0, cz - kh / 2.0, cz + kh / 2.0
        name = f"Payphone_Key{i}"
        prims += _box(name, "steel_key", (x0, yf - kp, kz0), (x1, yf + INSET, kz1), skip=("back", "front"))
        prims.append(_printed(f"{name}_front", "face", frame, x0, x1, kz0, kz1, yf - kp))
    # the coin slot: a raised bezel with a slot cut in it
    bw, bp, bh = SLOT_BEZEL
    bx, bz = SLOT_BEZEL_AT
    bxc, bzc = xc + bx, z0 + bz
    b_outer = (bxc - bw / 2.0, bxc + bw / 2.0, bzc - bh / 2.0, bzc + bh / 2.0)
    prims += _box("Payphone_Slot", "steel", (b_outer[0], yf - bp, b_outer[2]), (b_outer[1], yf + INSET, b_outer[3]),
                  skip=("front", "back"))
    sw, sh = SLOT_HOLE
    s_hole = (bxc - sw / 2.0, bxc + sw / 2.0, bzc - sh / 2.0, bzc + sh / 2.0)
    prims += _recess("Payphone_SlotFace", "bezel", b_outer, b_outer, s_hole, yf - bp, SLOT_DEPTH)
    # the coin vault's door and its lock
    vw, vp, vh = VAULT
    prims += _box("Payphone_Vault", {"*": "steel", "front": "vault"},
                  (xc - vw / 2.0, yf - vp, z0 + VAULT_Z - vh / 2.0), (xc + vw / 2.0, yf + INSET, z0 + VAULT_Z + vh / 2.0),
                  skip=("back",))
    # the lock starts INSET inside the body: begun 2 mm proud of the face, its
    # inner cap sat on the coplanar probe's 2 mm window and float32 decided
    # (the census found it at the genome's min and max corners, not the default)
    prims.append(_flat(P.rod("Payphone_Lock", "paint", (xc + vw * 0.30, yf + INSET, z0 + VAULT_Z),
                             (xc + vw * 0.30, yf - vp - LOCK_PROUD, z0 + VAULT_Z), LOCK_R, segments=10,
                             phase=math.pi / 10), "steel_key"))
    # the hook-switch cradle on the left face
    cz0, cz1 = L["cradle_z"]
    cw, cd, _ch = CRADLE
    prims += _box("Payphone_Cradle", "black", (ix0 - cw, yf + 0.006, cz0), (ix0 + INSET, yf + 0.006 + cd, cz1),
                  skip=("right",))
    # the handset: a grip between two cups, hung with its ear cup in the cradle
    gx, gy, gz0, gz1 = L["grip"]
    gw, gd, _gh = GRIP
    prims += _box("Payphone_Grip", "black", (gx - gw / 2.0, gy - gd / 2.0, gz0), (gx + gw / 2.0, gy + gd / 2.0, gz1),
                  skip=("top", "under"))
    for name, z in (("Ear", L["ear_z"]), ("Mouth", L["mouth_z"])):
        prims.append(_flat(P.rod(f"Payphone_{name}Cup", "paint", (gx - CUP_HALF, gy, z), (gx + CUP_HALF, gy, z),
                                 CUP_R, segments=12, phase=math.pi / 12), "black"))
    # the cord: one armoured sleeve from the handset's foot to the instrument
    prims.append(tube("Payphone_Cord", "cord", L["cord"], CORD_R))
    return prims


def plan(w, d, h, form="auto", rgb=(0.22, 0.26, 0.32)):
    """``{"prims", "tiles", "collision", "layout", "lamp", "facts"}``: every
    prim on one of two atlases, ``paint`` or ``glow`` (`GLOW_TILES`, 1.89.0),
    and ``lamp`` the hood lamp's marker -- its name, where it hangs, and the
    payload it carries. ``rgb`` is the shroud's linear paint (the genome's
    style colour), lettered and worn in the tiles."""
    L = layout(form, w, d, h)
    prims = []
    _enclosure(L, prims)
    _instrument(L, prims)
    # the lit atlas (1.89.0): the header's face and the diffuser's
    for p in prims:
        if p.get("tile") in GLOW_TILES:
            p["mat"] = "glow"
    paint = tuple(_srgb8(c) for c in rgb[:3])
    ix0, ix1, _yf, _yb, z0, z1 = L["inst"]
    zr = L["top"] - T_ROOF
    enc_h = zr - L["z_enc0"]

    def spec(kind, w_m, h_m, atlas="paint", **more):
        return (atlas, dict({"kind": kind, "w_m": w_m, "h_m": h_m, "paint": paint, "form": L["form"]}, **more))

    tiles = {
        "shroud": spec("payphone_shroud", 0.40, 0.80),
        "side_in": spec("payphone_side_in", d, enc_h),
        "back_in": spec("payphone_back_in", w, enc_h + BACK_BELOW),
        "inside": spec("payphone_inside", 0.30, 0.30),
        "roof": spec("payphone_roof", 0.30, 0.20),
        "post": spec("payphone_post", 0.10, 0.60),
        "steel": spec("payphone_steel", 0.15, 0.15),
        "steel_key": spec("payphone_steel_key", 0.04, 0.04),
        "face": spec("payphone_face", ix1 - ix0, z1 - z0),
        "bezel": spec("payphone_bezel", SLOT_BEZEL[0], SLOT_BEZEL[2]),
        "vault": spec("payphone_vault", VAULT[0], VAULT[2]),
        "dark": spec("payphone_dark", 0.05, 0.05),
        "black": spec("payphone_black", 0.06, 0.06),
        "cord": spec("payphone_cord", 0.02, 0.16),
        "lens_rim": spec("payphone_lens_rim", 0.10, 0.03),
        "lens": spec("payphone_lens", L["lens"][1] - L["lens"][0], LENS_D, atlas="glow"),
    }
    if L["form"] != "pedestal":
        hw = 2.0 * (w / 2.0 - INSET - T_SIDE + INSET)
        tiles["header"] = spec("payphone_header", hw, HEADER_H, atlas="glow", line=hw >= HEADER_LINE_W)
        tiles["shelf"] = spec("payphone_shelf", 0.30, 0.20)
    else:
        tiles["pictogram"] = spec("payphone_pictogram", d, enc_h)
    if L["form"] == "wall":
        tiles["binder"] = spec("payphone_binder", BINDER[0], BINDER[2])
        tiles["binder_edge"] = spec("payphone_binder_edge", 0.10, 0.10)
    for _r, name in stickers(L):
        tiles[name] = spec("payphone_sticker", STICKER[0], STICKER[1], row=int(name.split("_")[1]))
    # collision: the instrument and the back panel as one column, the post
    # under it; a body walks into the booth's mouth, not through its back
    ix0, ix1, yf, _yb, z0, _z1 = L["inst"]
    collision = [((-w / 2.0, yf - 0.02, L["z_enc0"] - BACK_BELOW), (w / 2.0, L["y_bp1"], L["top"]))]
    sx = w / 2.0 - INSET
    for a, b in ((-sx, -sx + T_SIDE), (sx - T_SIDE, sx)):
        collision.append(((a, -d / 2.0 + INSET, L["z_enc0"]), (b, L["y_back"] - INSET, L["top"] - T_ROOF)))
    if L["form"] != "wall":
        collision.append(((-POST / 2.0, L["y_bp1"] - INSET - POST, 0.0),
                          (POST / 2.0, L["y_bp1"] - INSET, L["z_enc0"] - BACK_BELOW)))
    return {"prims": prims, "tiles": tiles, "collision": collision, "layout": L,
            "lamp": {"name": LAMP, "at": L["lamp"],
                     "props": {"lux_type": LAMP_TYPE, "lux_drop": L["lamp"][2]}},
            "facts": {"form": L["form"], "company": COMPANY, "tris": P.tri_count(prims), "materials": 2}}


# --- the paint -------------------------------------------------------------------------


def _px(m, texel=TEXEL):
    return max(8, int(round(m * texel)))


def _outdoor(im, w, h, body, seed, grime=0.5):
    """Paint that lives outside: lighter where the sky falls, grime risen
    from the ground, scratches, a few chips to bare metal."""
    im.vgrad((0, 0, w, h), _lift(body, 14), _lift(body, -18))
    im.grain((0, 0, w, h), 3.5, seed)
    im.vgrad((0, int(h * 0.80), w, h), _lift(body, -14), _lift(body, int(-40 * grime)))
    for k in range(max(2, w // 30)):
        r = _h("chip", seed, k)
        x = r % max(1, w - 4)
        y = (r >> 8) % max(1, h - 3)
        im.rect((x, y, x + 2 + (r >> 12) % 3, y + 1 + (r >> 16) % 2), (150, 152, 154), 0.55)
    im.edge_dark((0, 0, w, h), max(2, w * 0.04), 0.18)


def _tag(im, box, seed, rgb):
    """A marker tag: a looping stroke of discs, the shape of a name nobody can
    read, scrawled across ``box``."""
    x0, y0, x1, y1 = box
    r = max(1.5, (y1 - y0) * 0.06)
    steps = 90
    for s in range(steps):
        t = s / float(steps)
        x = x0 + (x1 - x0) * t
        wob = math.sin(t * 19.0 + (seed % 7)) * 0.32 + math.sin(t * 7.0 + (seed % 5)) * 0.18
        y = (y0 + y1) / 2.0 + (y1 - y0) * wob
        im.disc(x, y, r, rgb, 0.85)


def _sticker(im, box, lines, seed):
    """A sticker somebody slapped on: a white rectangle, a bold top line, the
    rest under it, one corner peeling grey."""
    x0, y0, x1, y1 = [int(v) for v in box]
    im.rect((x0, y0, x1, y1), WHITE)
    hh = y1 - y0
    pad = max(1, (x1 - x0) // 14)
    rows = [t for t in lines if t]
    step = hh / float(len(rows))
    for k, text in enumerate(rows):
        ink = RED if k == 0 else CARD_INK
        im.text(text, (x0 + pad, y0 + step * k + 1, x1 - pad, y0 + step * (k + 1) - 1), ink,
                face=SHOP if k == 0 else ST.owned("shop_small"), min_cap=4)
    if seed % 2:
        im.rect((x1 - pad * 2, y0, x1, y0 + pad * 2), (190, 190, 186))


def paint(spec):
    """One tile as a Canvas; ``c.unset`` lists every line that did not set."""
    kind = spec["kind"]
    body = tuple(spec.get("paint", (60, 70, 86)))
    if kind == "payphone_face":
        return _face(spec)
    if kind == "payphone_header":
        w, h = _px(spec["w_m"], HEADER_TEXEL), _px(spec["h_m"], HEADER_TEXEL)
        im = PT.Img(w, h, body)
        im.vgrad((0, 0, w, h), _lift(body, 22), _lift(body, -10))
        split = int(w * 0.62)
        im.text("PHONE", (w * 0.04, h * 0.14, split - w * 0.02, h * 0.86), HEADER_INK, face=MAKER)
        im.rect((split, int(h * 0.16), split + max(2, w // 160), int(h * 0.84)), _lift(body, 60))
        if spec.get("line"):
            im.text(COMPANY, (split + w * 0.03, h * 0.20, w * 0.97, h * 0.62), HEADER_INK, face=MAKER)
            im.text(COMPANY_LINE, (split + w * 0.03, h * 0.62, w * 0.97, h * 0.86), _lift(body, 90),
                    face=MAKER_SMALL, min_cap=4)
        else:
            im.text(COMPANY, (split + w * 0.03, h * 0.20, w * 0.97, h * 0.80), HEADER_INK, face=MAKER)
        im.grain((0, 0, w, h), 2.0, 5)
        return im.to_canvas()
    if kind == "payphone_pictogram":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, body)
        _outdoor(im, w, h, body, 17)
        # the stamped handset, the glyph everybody reads: a grip lying across
        # the top with a cup turned down at each end, in a ring, PHONE under.
        # The first frame stood the grip upright between two cups, and from
        # the sidewalk it read as a capital I.
        cx, cy, rr = w * 0.5, h * 0.36, min(w, h) * 0.30
        ink = _lift(body, 70)
        im.disc(cx, cy, rr, ink)
        im.disc(cx, cy, rr * 0.86, body)
        im.rrect((cx - rr * 0.58, cy - rr * 0.30, cx + rr * 0.58, cy - rr * 0.08), rr * 0.10, ink)
        for side in (-1, 1):
            x0 = cx + side * rr * 0.58
            x1 = cx + side * rr * 0.26
            im.rrect((min(x0, x1), cy - rr * 0.14, max(x0, x1), cy + rr * 0.30), rr * 0.12, ink)
        im.text("PHONE", (w * 0.12, h * 0.62, w * 0.88, h * 0.74), _lift(body, 70), face=MAKER)
        return im.to_canvas()
    if kind == "payphone_side_in":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, _lift(body, -10))
        _outdoor(im, w, h, _lift(body, -10), 23, grime=0.8)
        _tag(im, (w * 0.10, h * 0.55, w * 0.90, h * 0.70), 3, (24, 24, 26))
        _tag(im, (w * 0.20, h * 0.25, w * 0.75, h * 0.33), 8, (150, 30, 140))
        return im.to_canvas()
    if kind == "payphone_back_in":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, _lift(body, -12))
        _outdoor(im, w, h, _lift(body, -12), 29, grime=0.7)
        _tag(im, (w * 0.06, h * 0.12, w * 0.40, h * 0.20), 11, (24, 24, 26))
        return im.to_canvas()
    if kind == "payphone_sticker":
        # its own tile at sticker density, so its lines set; the panel's
        # grime round it is the base tile's
        w, h = _px(spec["w_m"], STICKER_TEXEL), _px(spec["h_m"], STICKER_TEXEL)
        im = PT.Img(w, h, WHITE)
        k = int(spec["row"])
        _sticker(im, (0, 0, w, h), STICKERS[k], k + 1)
        im.grain((0, 0, w, h), 2.0, 43 + k)
        im.edge_dark((0, 0, w, h), max(2, w * 0.04), 0.25)
        return im.to_canvas()
    if kind in ("payphone_shroud", "payphone_roof", "payphone_inside", "payphone_shelf"):
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        base = {"payphone_shroud": body, "payphone_roof": _lift(body, 8),
                "payphone_inside": _lift(body, -26), "payphone_shelf": _lift(body, -6)}[kind]
        im = PT.Img(w, h, base)
        _outdoor(im, w, h, base, _h(kind) % 997, grime=0.6 if kind != "payphone_roof" else 0.2)
        return im.to_canvas()
    if kind == "payphone_post":
        w, h = _px(spec["w_m"]), _px(spec["h_m"])
        im = PT.Img(w, h, POST_BLACK)
        _outdoor(im, w, h, POST_BLACK, 31, grime=0.3)
        return im.to_canvas()
    if kind in ("payphone_steel", "payphone_steel_key", "payphone_bezel", "payphone_vault"):
        texel = FACE_TEXEL if kind != "payphone_steel" else TEXEL * 2
        w, h = _px(spec["w_m"], texel), _px(spec["h_m"], texel)
        im = PT.Img(w, h, STEEL)
        im.vgrad((0, 0, w, h), _lift(STEEL, 16), _lift(STEEL, -22))
        for k in range(h // 2):
            im.rect((0, 2 * k, w, 2 * k + 1), _lift(STEEL, -8 if k % 2 else 6), 0.35)
        im.grain((0, 0, w, h), 2.5, _h(kind) % 997)
        if kind == "payphone_bezel":
            im.edge_dark((0, 0, w, h), max(2, w * 0.12), 0.30)
        if kind == "payphone_vault":
            im.edge_dark((0, 0, w, h), max(2, w * 0.05), 0.40)
            im.text("COIN BOX", (w * 0.10, h * 0.10, w * 0.62, h * 0.30), STEEL_DARK, face=MAKER_SMALL, min_cap=4)
        return im.to_canvas()
    if kind == "payphone_dark":
        w, h = _px(spec["w_m"], 400), _px(spec["h_m"], 400)
        im = PT.Img(w, h, DARK)
        im.vgrad((0, 0, w, h), (34, 34, 36), (6, 6, 7))
        return im.to_canvas()
    if kind == "payphone_black":
        w, h = _px(spec["w_m"], 400), _px(spec["h_m"], 400)
        im = PT.Img(w, h, BLACK)
        im.vgrad((0, 0, w, h), (44, 44, 48), (14, 14, 15))
        im.gloss((0, 0, w, h), strength=0.12)
        return im.to_canvas()
    if kind == "payphone_cord":
        w, h = _px(spec["w_m"], 800), _px(spec["h_m"], 800)
        im = PT.Img(w, h, STEEL_DARK)
        # the sleeve's spiral ribs, one every few millimetres down its length
        for k in range(0, h, 4):
            im.rect((0, k, w, k + 2), _lift(STEEL, 10))
        im.grain((0, 0, w, h), 3.0, 37)
        return im.to_canvas()
    if kind == "payphone_binder":
        w, h = _px(spec["w_m"], 400), _px(spec["h_m"], 400)
        im = PT.Img(w, h, (30, 30, 34))
        im.vgrad((0, 0, w, h), (44, 44, 50), (20, 20, 24))
        lines = BINDER_LINES
        for k, text in enumerate(lines):
            im.text(text, (w * 0.12, h * (0.18 + 0.16 * k), w * 0.88, h * (0.30 + 0.16 * k)), (196, 186, 120),
                    face=MAKER if k == 0 else MAKER_SMALL, min_cap=4)
        im.edge_dark((0, 0, w, h), max(2, w * 0.05), 0.4)
        return im.to_canvas()
    if kind == "payphone_binder_edge":
        w, h = _px(spec["w_m"], 200), _px(spec["h_m"], 200)
        im = PT.Img(w, h, (26, 26, 30))
        return im.to_canvas()
    if kind == "payphone_lens":
        # the diffuser a tube shines through (1.89.0), on the lit atlas: its
        # art is its own light. The tube's line runs its length, a little
        # brighter; the prismatic panel's ribs cross it, faint
        w, h = _px(spec["w_m"], 400), _px(spec["h_m"], 400)
        im = PT.Img(w, h, LENS_WHITE)
        im.rect((0, int(h * 0.36), w, int(h * 0.64)), LENS_TUBE, 0.8)
        for k in range(0, w, 4):
            im.rect((k, 0, k + 1, h), _lift(LENS_WHITE, -14), 0.35)
        im.edge_dark((0, 0, w, h), max(2, h * 0.08), 0.20)
        return im.to_canvas()
    if kind == "payphone_lens_rim":
        # the diffuser's frame, the canopy's own metal, darker
        w, h = _px(spec["w_m"], 400), _px(spec["h_m"], 400)
        im = PT.Img(w, h, _lift(body, -40))
        im.grain((0, 0, w, h), 2.0, 47)
        return im.to_canvas()
    raise ValueError(f"no payphone tile {kind!r}")


def _face(spec):
    """The instrument's printed face, as the quads cut round the coin return
    and the keys' fronts sample it: the card at the top, the slot's legend by
    its bezel, a key's legend where the key stands, COIN RETURN over the
    opening, the company at the foot. Coordinates follow `_instrument`."""
    iw, _idp, ih = INST
    w, h = _px(spec["w_m"], FACE_TEXEL), _px(spec["h_m"], FACE_TEXEL)
    im = PT.Img(w, h, STEEL)
    im.vgrad((0, 0, w, h), _lift(STEEL, 14), _lift(STEEL, -20))
    for k in range(h // 2):
        im.rect((0, 2 * k, w, 2 * k + 1), _lift(STEEL, -6 if k % 2 else 5), 0.3)
    im.grain((0, 0, w, h), 2.0, 41)

    def px(x_m):                      # metres right of the face's left edge -> pixels
        return x_m / iw * w

    def pz(z_m):                      # metres above its foot -> pixels from the top
        return (1.0 - z_m / ih) * h

    xc = iw / 2.0
    # the instruction card under its clear cover: paper, a ruled head, lines
    cw, chh = CARD
    c0x, c1x = px(xc - cw / 2.0), px(xc + cw / 2.0)
    c0z, c1z = pz(CARD_Z + chh / 2.0), pz(CARD_Z - chh / 2.0)
    im.rect((c0x - 2, c0z - 2, c1x + 2, c1z + 2), STEEL_DARK)
    im.rect((c0x, c0z, c1x, c1z), CARD_PAPER)
    rows = CARD_LINES
    step = (c1z - c0z) / float(len(rows))
    for k, text in enumerate(rows):
        ink = RED if text.startswith("EMERGENCY") else CARD_INK
        im.text(text, (c0x + 3, c0z + step * k + 1, c1x - 3, c0z + step * (k + 1) - 1), ink,
                face=NOTICE_BOLD if k == 0 else NOTICE, min_cap=4)
    im.gloss((c0x, c0z, c1x, c1z), strength=0.20)
    # the slot's legend, left of its bezel
    bx, bz = SLOT_BEZEL_AT
    bw, _bp, bh = SLOT_BEZEL
    im.text("25 CENTS", (px(xc + bx - bw / 2.0 - 0.075), pz(bz + 0.012), px(xc + bx - bw / 2.0 - 0.006),
                         pz(bz - 0.012)), CARD_INK, face=MAKER, min_cap=4)
    # the keys' legends, each at its key
    kw, _kp, kh = KEY
    px_, pz_ = KEY_PITCH
    for i, label in enumerate(KEYS):
        col, row = i % 3, i // 3
        cx = xc + (col - 1) * px_
        cz = KEYPAD_Z + (1.5 - row) * pz_
        box = (px(cx - kw / 2.0), pz(cz + kh / 2.0), px(cx + kw / 2.0), pz(cz - kh / 2.0))
        im.rect(box, _lift(STEEL, 10))
        im.text(label, (box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1), CARD_INK, face=MAKER, min_cap=4)
    # COIN RETURN over the opening
    rx, rz = RETURN_AT
    rw, rh = RETURN_HOLE
    im.text("COIN RETURN", (px(xc + rx - rw / 2.0 - 0.02), pz(rz + rh / 2.0 + 0.020), px(xc + rx + rw / 2.0 + 0.004),
                            pz(rz + rh / 2.0 + 0.004)), CARD_INK, face=MAKER_SMALL, min_cap=4)
    # the company, low on the face
    im.text(COMPANY, (px(0.012), pz(0.125), px(xc + rx - rw / 2.0 - 0.010), pz(0.105)), STEEL_DARK,
            face=MAKER, min_cap=4)
    im.edge_dark((0, 0, w, h), max(2, w * 0.03), 0.25)
    return im.to_canvas()


def all_strings():
    """Every word painted on a payphone, for the invented-names test."""
    out = [COMPANY, COMPANY_LINE, "PHONE", "COIN BOX"] + list(CARD_LINES) + list(FACE_WORDS) + list(BINDER_LINES)
    for sticker in STICKERS:
        out += [t for t in sticker if t]
    return out
