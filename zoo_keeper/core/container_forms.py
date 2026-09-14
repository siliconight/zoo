"""The ISO shipping container, as decisions: size class, corrugation, paint,
markings and weathering. Pure Python (no bpy), so every number the
`cargo_container` recipe builds from is testable without Blender.

WHAT 0.80.0 SHIPPED, measured before this file existed. Walk 9052_rain's
`cover/prop_cargo_container_delco_1997_01_w244_d606_h259.glb` (Zoo site kit
job of cold run 9052): one part, `CargoContainer_Body`, 44 tris -- a 6 mm
bevelled box -- plus a 12-tri collider, on one material,
`M_Skin_metal_painted_delco_1997_807d75`. That material is the delco_1997
`metal_painted_neutral` pack (Pixelcoat 0.16.0: 128 px, 1.2 m a tile,
albedo 232..255 in every channel, `tintable`) multiplied by the genome's
grey #807d75. There was no corrugation anywhere -- not in the mesh and not
in the texture, which is a near-white grain -- and the only variation on
6 m faces was the per-vertex wear noise of 48 vertices, interpolated
corner to corner. That is the "plain flat box with a blotchy green-grey
noise skin" the walker reported.

WHAT A CONTAINER IS HERE. Frame: Zoo's module frame, Z up, metres, centre
pivot; width along X, LENGTH ALONG Y, the door end at -Y (the species
convention: a front faces -Y) and the blind end at +Y.

  * the envelope is the eight corner castings: nothing stands outside them,
    which is how a real one stacks, and it makes the slot's exact fit a
    property of eight boxes;
  * corner posts, top and bottom side rails, a top and bottom rail across
    the blind end, a door header and a sill across the door end;
  * corrugated side walls and blind end (trapezoidal, vertical ribs),
    a corrugated roof (ribs across it), two door leaves with a frame and
    pressed horizontal channels;
  * four locking bars with cam keepers, guides, handles and retainers;
    four hinges per leaf; fork pockets in the bottom side rails of 10 and
    20 ft boxes;
  * an ISO 6346 owner code, serial and check digit on the right leaf and
    both sides, the size-type code, a weight block, a CSC plate, a warning
    triangle, and on some boxes a carrier name down the side;
  * paint from a period palette, rust streaks off the top rail and up from
    the bottom rail, and the odd touch-up patch.

NOTHING HERE IS A REAL COMPANY. The carrier names and owner prefixes are
invented, spelled from the glyph set `recipes/_legend.py` carries; whether a
prefix happens to be registered with the BIC has not been checked.
"""
from __future__ import annotations

import math

# --- size ------------------------------------------------------------------

#: ISO 668 nominal lengths, metres, and the ISO 6346 length character.
NOMINAL = (("10ft", 2.991, "1"), ("20ft", 6.058, "2"),
           ("40ft", 12.192, "4"), ("45ft", 13.716, "L"))

#: ISO 6346 height character by external height: 8 ft (2.438) "0",
#: 8 ft 6 in (2.591) "2", 9 ft 6 in high cube (2.896) "5". Thresholds are
#: the midpoints between the three heights.
HEIGHT_CODES = ((2.743, "5"), (2.514, "2"), (0.0, "0"))

#: Fork pockets: ISO 1496-1 asks for 355 x 115 mm minimum; 360 x 115 is
#: built. Centres 2050 mm apart on a 20 ft box (the standard spacing). A
#: 10 ft box has no standard spacing; 900 mm is CHOSEN, not taken from a
#: table. 40 and 45 ft boxes are not fork-lifted and have no pockets.
POCKET_W = 0.360
POCKET_H = 0.115
POCKET_CENTRES = {"20ft": 2.050, "10ft": 0.900}


def length_class(depth: float) -> tuple[str, str]:
    """(name, ISO length character) of the nominal length nearest ``depth``."""
    name, _l, code = min(NOMINAL, key=lambda t: abs(t[1] - float(depth)))
    return name, code


def height_code(height: float) -> str:
    for lo, code in HEIGHT_CODES:
        if float(height) >= lo:
            return code
    return HEIGHT_CODES[-1][1]


def size_type(depth: float, height: float) -> str:
    """ISO 6346 size-type code, general purpose with vents (G1): 22G1 for a
    standard 20 ft box, 42G1 a 40 ft, 45G1 a 40 ft high cube, L5G1 a 45."""
    _name, lc = length_class(depth)
    return lc + height_code(height) + "G1"


def pocket_centres(depth: float) -> list[float]:
    """Y of each fork pocket's centre, symmetric about the middle."""
    name, _c = length_class(depth)
    if name not in POCKET_CENTRES:
        return []
    half = POCKET_CENTRES[name] / 2.0
    return [-half, half]


# --- corrugation -----------------------------------------------------------

#: The trapezoid profiles, as (pitch, crest, flank run, depth) in metres.
#:
#: SIDE and END: a real side panel runs about 280 mm a pitch at 36 mm deep.
#: Built at 300 mm and 40 mm with a 50 mm flank run (a 39 degree flank):
#: slightly coarser and deeper, so each flank is a facet wide enough to carry
#: its own shade. At 30 m and 1600 px over a 70 degree field the pitch is
#: about 12 px and a flank about 2 px -- the rib reads, and nothing is fine
#: enough to alias into moire short of a hundred metres. Every edge is left
#: hard: a faceted rib, not a smoothed wave.
#:
#: ROOF: shallower and wider, 420 mm at 20 mm. The street sees it from
#: rooftops only, and the wider pitch halves its triangles.
SIDE_PROFILE = (0.300, 0.100, 0.050, 0.040)
ROOF_PROFILE = (0.420, 0.160, 0.050, 0.020)


def corrugation(a: float, b: float, profile=SIDE_PROFILE) -> list[tuple[float, float]]:
    """Breakpoints ``[(u, offset), ...]`` of a trapezoid profile over [a, b].

    ``offset`` is 0 on a crest and ``-depth`` in a valley. A whole number of
    pitches is fitted, the pitch stretched to fill the span exactly, and the
    sheet starts and ends on half a crest -- so both ends run flat into the
    post or rail that buries them.
    """
    pitch, crest, flank, depth = profile
    span = float(b) - float(a)
    n = max(1, int(round(span / pitch)))
    k = span / (n * pitch)
    valley = pitch - crest - 2.0 * flank
    pts = [(a, 0.0)]
    for i in range(n):
        p0 = a + i * pitch * k
        for du, off in ((crest / 2.0, 0.0), (crest / 2.0 + flank, -depth),
                        (crest / 2.0 + flank + valley, -depth),
                        (crest / 2.0 + 2.0 * flank + valley, 0.0)):
            pts.append((p0 + du * k, off))
    pts.append((b, 0.0))
    return pts


def channels(a: float, b: float, top_band: float, bottom_band: float,
             count: int = 4, valley: float = 0.120, flank: float = 0.025,
             depth: float = 0.024) -> list[tuple[float, float]]:
    """A door leaf's pressed channels, as breakpoints over [a, b] (u = height).

    Flat bands top and bottom -- the top one is where the owner code is
    painted -- and ``count`` channels spaced evenly between them.
    """
    lo, hi = a + bottom_band, b - top_band
    pts = [(a, 0.0)]
    pitch = (hi - lo) / count
    for i in range(count):
        c = lo + (i + 0.5) * pitch
        half = valley / 2.0 + flank
        pts += [(c - half, 0.0), (c - valley / 2.0, -depth),
                (c + valley / 2.0, -depth), (c + half, 0.0)]
    pts.append((b, 0.0))
    return pts


#: Form, by the part of the rib a face lies on: the paint a crest, flank and
#: valley are each built in, as a fraction of the box's paint.
#:
#: WHY. The first in-engine frames (walk 9052_rain, Godot 4.7 GL
#: Compatibility, overcast rain) showed the corrugation almost gone: under a
#: sky with no direction every facet of a rib receives the same light, so a
#: faceted flank has nothing to shade it. The same module rendered in Blender
#: under a sun read strongly -- two lights, two answers, and the level ships
#: under the first. A valley is recessed and a flank half-recessed whatever
#: the light, so they are built darker.
#:
#: REFUTED, kept above what replaced it: this shade was first baked into the
#: `Wear` vertex colour, the way `geometry.wear_colors` darkens concave
#: vertices on every other species. The GLB carried it (the walls' COLOR_0
#: median fell from 0.863 to 0.515) and the frame did not move: over a
#: patch-free strip of the side wall, mean luma 47.4 -> 47.1 and the 3 px
#: column step 3.32 -> 3.07. The dial was dead, not the idea -- every
#: surface of the imported container, car and box truck in that walk has
#: `vertex_color_use_as_albedo = false`, so no cover module's COLOR_0 is
#: drawn at all. Built into the MATERIAL, the shade does not depend on it.
FORM_SHADE = {"crest": 1.0, "flank": 0.80, "valley": 0.66}


def segment_kind(points, u: float) -> str:
    """"crest", "flank" or "valley" for the profile segment holding ``u``."""
    depth = -min(o for _u, o in points)
    for (u0, o0), (u1, o1) in zip(points, points[1:]):
        if u0 - 1e-9 <= u <= u1 + 1e-9:
            if abs(o0) < 1e-9 and abs(o1) < 1e-9:
                return "crest"
            if depth > 0 and abs(o0 + depth) < 1e-9 and abs(o1 + depth) < 1e-9:
                return "valley"
            return "flank"
    return "crest"


def profile_at(points, u: float) -> float:
    """Offset of the profile at ``u`` (linear between breakpoints, clamped)."""
    if u <= points[0][0]:
        return points[0][1]
    for (u0, o0), (u1, o1) in zip(points, points[1:]):
        if u <= u1:
            if u1 - u0 <= 1e-12:
                return o1
            t = (u - u0) / (u1 - u0)
            return o0 + (o1 - o0) * t
    return points[-1][1]


def _clip_half(poly, u, keep_below):
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        pin = p[0] <= u if keep_below else p[0] >= u
        qin = q[0] <= u if keep_below else q[0] >= u
        if pin:
            out.append(p)
        if pin != qin:
            t = (u - p[0]) / (q[0] - p[0])
            out.append((u, p[1] + (q[1] - p[1]) * t))
    return out


def _area(poly):
    return sum(poly[k][0] * poly[(k + 1) % len(poly)][1]
               - poly[(k + 1) % len(poly)][0] * poly[k][1]
               for k in range(len(poly))) / 2.0


#: A painted vertex this close to a rib break is moved onto it.
SNAP = 0.001


def split_at(poly, points, min_area=1e-8, snap=SNAP):
    """Cut a convex ``(u, v)`` polygon at every breakpoint ``u`` it spans.

    Each piece lies between two neighbouring breakpoints, where the profile
    is one straight segment -- so each piece, lifted onto the profile, is a
    flat face on one crest, flank or valley. That is what lets paint follow
    the ribs instead of floating over them.

    A vertex within ``snap`` of a breakpoint is moved onto it first. Without
    that, a glyph edge 0.3 mm from a rib break was cut into a 0.3 mm sliver:
    measured in the 0.82.0 sweep (2.475 x 10.199 x 2.802, style 6), the only
    coincident pair in 118 builds, reported at 1.63 mm because a triangle
    that thin has no trustworthy normal. Moving a vertex by at most 1 mm is
    invisible; a sliver is a z-fight.
    """
    us = sorted({round(u, 9) for u, _o in points})

    def _snap(u):
        for b in us:
            if abs(u - b) < snap:
                return b
        return u

    poly = [(_snap(u), v) for u, v in poly]
    if abs(_area(poly)) <= min_area:
        return []
    umin = min(p[0] for p in poly)
    umax = max(p[0] for p in poly)
    cuts = [u for u in us if umin + 1e-9 < u < umax - 1e-9]
    bounds = [umin] + cuts + [umax]
    pieces = []
    for lo, hi in zip(bounds, bounds[1:]):
        piece = _clip_half(_clip_half(list(poly), lo, False), hi, True)
        if len(piece) >= 3 and abs(_area(piece)) > min_area:
            pieces.append(piece)
    return pieces


# --- paint -----------------------------------------------------------------

#: Box paint, linear RGB, weighted. The walker's references: a red 40 ft, a
#: weathered grey-blue 20 ft, a clean orange 20 ft; and the period's leasing
#: and carrier colours -- maroon, blue, green, grey, a dirty white. The
#: tintable `metal_painted` pack multiplies these into its near-white grain.
PAINT = {
    "red": ((0.40, 0.035, 0.025), 0.16),
    "maroon": ((0.16, 0.022, 0.018), 0.14),
    "orange": ((0.70, 0.20, 0.028), 0.08),
    "blue": ((0.022, 0.075, 0.23), 0.15),
    "grey_blue": ((0.15, 0.21, 0.27), 0.13),
    "green": ((0.030, 0.14, 0.065), 0.12),
    "grey": ((0.30, 0.31, 0.31), 0.12),
    "white": ((0.66, 0.66, 0.62), 0.10),
}
#: Paint that takes dark lettering; everything else is lettered white.
LIGHT_PAINT = ("white",)
MARK_WHITE = (0.80, 0.80, 0.77)
MARK_DARK = (0.030, 0.030, 0.034)
#: Rust as it runs: the oxide's orange-brown, lighter than the dried stain a
#: first attempt used (0.19, 0.068, 0.028), which on orange and red paint
#: rendered as dark slots in the wall rather than as rust.
RUST = (0.30, 0.105, 0.035)
APERTURE = (0.018, 0.018, 0.020)
PLATE = (0.52, 0.52, 0.49)
WARNING_YELLOW = (0.78, 0.56, 0.02)
#: Hardware (bars, keepers, handles, hinges) is the box's own paint, darker:
#: on a real box it is painted with the doors, and dirtier.
HARDWARE_SHADE = 0.55
#: A touch-up patch is primer grey or the paint gone darker.
PRIMER = (0.26, 0.25, 0.23)


def _weighted(rng, pairs):
    total = float(sum(w for _k, w in pairs))
    r = rng.random() * total
    acc = 0.0
    for k, w in pairs:
        acc += w
        if r < acc:
            return k
    return pairs[-1][0]


def pick_paint(plan: dict, rng) -> tuple[str, tuple]:
    """(name, linear rgb). A prompt colour, or a style block that says
    ``"paint": "fixed"``, wins; otherwise the palette, weighted. The draw is
    taken either way, so asking for a colour never shifts later draws."""
    name = _weighted(rng, [(k, v[1]) for k, v in PAINT.items()])
    block = plan.get("style_block") or {}
    colour = [round(float(c), 4) for c in plan.get("color", [])]
    styled = [round(float(c), 4) for c in block.get("color", colour)]
    if colour and (colour != styled or block.get("paint") == "fixed"):
        return "asked", tuple(colour)
    return name, PAINT[name][0]


def mark_colour(paint_name: str, paint) -> tuple:
    if paint_name in LIGHT_PAINT:
        return MARK_DARK
    lum = 0.2126 * paint[0] + 0.7152 * paint[1] + 0.0722 * paint[2]
    return MARK_DARK if lum > 0.45 else MARK_WHITE


# --- markings --------------------------------------------------------------

#: Invented 1990s carriers: (name painted down the side, owner prefix).
CARRIERS = (("SEAHOLT", "SHL"), ("PORTALIS", "PTL"), ("TRADEPAC", "TDP"),
            ("GALEOTA", "GLT"), ("ALBATROS", "ABT"))
#: Invented leasing-pool prefixes: a leased box carries a code and no name.
LESSORS = ("DCR", "BFA", "HLS", "CGT", "CFR")
#: How often a box carries its carrier's name down the side.
NAME_CHANCE = 0.55

#: ISO 6346 letter values: A = 10, skipping every multiple of 11.
_LETTER_VALUES = {}
_v = 10
for _ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    if _v % 11 == 0:
        _v += 1
    _LETTER_VALUES[_ch] = _v
    _v += 1


def check_digit(owner: str, serial: str) -> int:
    """ISO 6346 check digit of a four-letter owner code and six-digit serial."""
    code = (owner + serial).upper()
    if len(code) != 10:
        raise ValueError(f"owner+serial must be 10 characters, got {code!r}")
    total = 0
    for i, ch in enumerate(code):
        val = _LETTER_VALUES[ch] if ch.isalpha() else int(ch)
        total += val * (2 ** i)
    return total % 11 % 10


def pick_marks(depth: float, height: float, rng) -> dict:
    """Owner code, serial, check digit, size-type, carrier name and the
    weight block, all from ``rng``."""
    carrier = rng.random() < NAME_CHANCE
    ci = int(rng.random() * len(CARRIERS)) % len(CARRIERS)
    li = int(rng.random() * len(LESSORS)) % len(LESSORS)
    serial = "%06d" % int(rng.random() * 1000000)
    name, prefix = CARRIERS[ci] if carrier else (None, LESSORS[li])
    owner = prefix + "U"
    lclass, _c = length_class(depth)
    # ISO 668 max gross 30,480 kg for every class here; tare by class,
    # rounded the way a data plate states it.
    tare = {"10ft": 1300, "20ft": 2200, "40ft": 3750, "45ft": 4800}[lclass]
    tare += 10 * int(rng.random() * 12)
    gross = 30480
    return {"owner": owner, "serial": serial,
            "check": check_digit(owner, serial),
            "size_type": size_type(depth, height),
            "carrier": name, "gross": gross, "tare": tare,
            "net": gross - tare}


def text_width(n_chars: int, height: float, letter_w: float = 0.52,
               gap: float = 0.08) -> float:
    """The width `_legend.legend` lays ``n_chars`` out at (spaces included)."""
    return (n_chars * letter_w + max(0, n_chars - 1) * gap) * height


def carrier_height(name: str, length: float, height: float) -> float:
    """Letter height for a carrier name down a side: 0.23 of the box's height,
    and no more than lets the name fill 0.72 of the wall's length."""
    fit = 0.72 * length / max(1e-6, text_width(len(name), 1.0))
    return max(0.10, min(0.23 * height, fit))


# --- weathering ------------------------------------------------------------

def rects_overlap(a, b, pad=0.0) -> bool:
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0]
                or a[3] + pad <= b[1] or b[3] + pad <= a[1])


def crest_bands(points) -> list[tuple[float, float]]:
    """The flat crest runs of a profile, as (u0, u1)."""
    out = []
    for (u0, o0), (u1, o1) in zip(points, points[1:]):
        if abs(o0) < 1e-9 and abs(o1) < 1e-9 and u1 - u0 > 1e-6:
            out.append((u0, u1))
    return out


def plan_rust(points, v0: float, v1: float, wear: float, rng, taken,
              margin: float = 0.012) -> list[dict]:
    """Rust streaks on one corrugated wall, as ``(u0, v0, u1, v1)`` rectangles
    on crest runs plus how the streak tapers.

    Streaks hang from the top rail (rain runs off the rail's lip) and bloom
    up from the bottom rail (standing water). The count scales with the wall's
    length and the style's wear; a streak never overlaps ``taken`` (markings
    and patches already placed), which is what keeps any two flat details
    from sharing a plane.
    """
    bands = [(a + margin, b - margin) for a, b in crest_bands(points)
             if b - a > 2.5 * margin]
    length = points[-1][0] - points[0][0]
    n = int(round(max(0.0, wear) * length * 2.2))
    out = []
    tries = 0
    while len(out) < n and bands and tries < n * 8:
        tries += 1
        u0, u1 = bands[int(rng.random() * len(bands)) % len(bands)]
        hang = rng.random() < 0.7
        run = (v1 - v0) * (0.18 + rng.random() * 0.42 if hang
                           else 0.06 + rng.random() * 0.12)
        rect = ((u0, v1 - run, u1, v1) if hang else (u0, v0, u1, v0 + run))
        if any(rects_overlap(rect, t, pad=0.01) for t in taken + [r["rect"] for r in out]):
            continue
        out.append({"rect": rect, "hang": hang,
                    "width": 0.35 + rng.random() * 0.5,
                    "taper": 0.05 + rng.random() * 0.35})
    return out


def plan_patch(length_u: tuple, v0: float, v1: float, wear: float, rng,
               taken) -> dict | None:
    """At most one touch-up patch on a wall, over a few ribs, where nothing
    else is painted. Whether a box's patches are primer or darker paint is
    decided once per box (`resolve`), so both sides agree."""
    if rng.random() > 0.25 + 0.5 * max(0.0, min(1.0, wear)):
        return None
    for _ in range(8):
        w = 0.5 + rng.random() * 0.9
        hgt = (v1 - v0) * (0.18 + rng.random() * 0.25)
        u = length_u[0] + 0.3 + rng.random() * max(0.0, length_u[1] - length_u[0] - 0.6 - w)
        v = v0 + 0.25 + rng.random() * max(0.0, (v1 - v0) - 0.5 - hgt)
        rect = (u, v, u + w, v + hgt)
        if not any(rects_overlap(rect, t, pad=0.02) for t in taken):
            return {"rect": rect}
    return None


def resolve(plan: dict, streams) -> dict:
    """Every decision the recipe executes, each from its own stream --
    `container_paint`, `container_marks`, `container_patch` -- so a later
    decision never re-rolls
    a box's paint or its code."""
    dims = plan["dimensions"]
    depth, height = float(dims["depth"]), float(dims["height"])
    f = {}
    f["length_class"], _c = length_class(depth)
    f["pockets"] = pocket_centres(depth)
    f["paint_name"], f["paint"] = pick_paint(plan, streams.stream("container_paint"))
    f["mark"] = mark_colour(f["paint_name"], f["paint"])
    f["hardware"] = tuple(c * HARDWARE_SHADE for c in f["paint"])
    f.update(pick_marks(depth, height, streams.stream("container_marks")))
    f["patch_primer"] = streams.stream("container_patch").random() < 0.5
    return f


def _check_digit_self_test():
    """ISO 6346's published example: CSQU 305438, check digit 3."""
    return check_digit("CSQU", "305438") == 3


assert _check_digit_self_test()
assert math.isclose(sum(v[1] for v in PAINT.values()), 1.0)
