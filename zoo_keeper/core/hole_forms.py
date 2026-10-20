"""A hole in a floor that says why it is there, pure (Zoo 1.114.0; the factory's roadmap 265).

The walker, 2026-10-19, asked why the levels have holes in their floors -- Deli Counter's drop
routes, a 2.2 m square cut clean through a deli's upstairs apartment -- and chose to keep the routes
and give each hole a reason to exist: "if we have holes it should be clear to the player that they
are there, but also some reason other than a perfectly cut square (what is diegetic but a signal to
the human playing the game)". Three species carry it, and everything here is the part that needs no
Blender:

- `hole_edge` (`edge`): the torn edge round the hole, the thing that stops it being a square. On
  the floor, a collar of the floor's own underlayer, torn back irregularly from the cut and jutting
  past it in broken teeth; in the slab's thickness, the joist ends the cut went through; under the
  ceiling, a jagged ring where the ceiling is broken back and shards hanging into the opening. Every
  piece is visual: the slab's rectangular cut stays the collider and the drop's route, so a body
  falls exactly where it did.
- `hole_spoil` (`spoil`): what came down, on the floor below -- the cut-out floor in pieces, the
  ceiling tiles it broke, offcuts, plaster.
- `hole_kit` (`kit`): who did it, beside the hole -- the crew's tarp, cut-off saw, toolbag and a
  work light aimed into the opening.

TWO FORMS. `cut` is a hole made on purpose by somebody in a hurry -- broken through, not sawn
square: ragged where the boards tore, joists cut clean, a drop ceiling punched out below. `broken`
is a floor that gave way -- longer splinters drooping into the opening, joists sheared and hanging,
plaster and lath below. `auto` is `cut`.

THE CONTRACT WITH DELI COUNTER, whose `hole_causes.py` mirrors these numbers as it sizes the
slots: an edge slot reaches `BAND` past the hole each side, and its height is `TOP` (the collar
above the visible floor) + a floor skin + the slab + a ceiling skin (`SKIN` each) + `HANG` (the
lowest hanging piece below the visible ceiling). So the recipe can find, inside its own slot, where
the floor and the ceiling are. A spoil or kit slot stands `SKIRT` below the visible floor, so what
lies on the floor sinks that far into it, as a resting floater does (`core.floaters`).

FRAME AND UNITS: metres; X across the slot's width, Y along its depth, Z up from the slot's
bottom at 0; `build.build_module` re-centres the module. Determinism is by hash (`_u`), as in
`trash_bag_forms`, so a slot's variant names one layout on every machine.
"""
from __future__ import annotations

import math
import zlib

#: An edge slot reaches this far past the hole on each side (Deli Counter mirrors it).
BAND = 0.30
#: The torn collar's top stands this far above the visible floor.
TOP = 0.012
#: A floor or ceiling skin's thickness (Deli Counter's `floors.SKIN_THICK`).
SKIN = 0.02
#: The lowest hanging piece reaches this far below the visible ceiling.
HANG = 0.30
#: Metres of the opening no tooth may close, each way: a body falls past every piece of art.
CLEAR = 1.1
#: A solid resting on a surface sinks this far into it; a flat one stands this far off it
#: (`core.floaters.FLOATER_SKIRT`, `FLOATER_PROUD`).
SKIRT = 0.004
PROUD = 0.003
#: A form names three things: the CAUSE (`cut`, a crew broke through; `broken`, the floor gave way),
#: the floor's CONSTRUCTION (framed, or `_slab` -- concrete, Deli Counter's `concrete` floor), and the
#: CEILING under it (a drop ceiling of tiles, or `_plaster`). `auto` is `cut`, framed, under tiles.
CAUSES = ("cut", "broken")
FORMS = tuple(c + s + p for c in CAUSES for s in ("", "_slab") for p in ("", "_plaster"))
#: The genomes' `module_variants`: a slot's `variant` picks one of these layouts.
VARIANTS = 4
#: Perimeter sample spacing round the hole, metres.
STEP = 0.09
#: How far a lining plate stands off a face it would otherwise share, metres: more than the
#: coincident-face census's 2 mm.
WALL_GAP = 0.004

#: Colours, linear RGB, carried in `Wear` on one material per kind.
COLOURS = {
    "plywood": (0.62, 0.47, 0.30), "floorboard": (0.50, 0.33, 0.19), "joist": (0.55, 0.42, 0.27),
    "joist_old": (0.36, 0.27, 0.18), "tile": (0.82, 0.81, 0.77), "grid": (0.86, 0.86, 0.84),
    "cavity": (0.035, 0.033, 0.03), "lath": (0.40, 0.30, 0.20), "plaster": (0.80, 0.78, 0.73),
    "tarp": (0.12, 0.26, 0.52), "saw": (0.86, 0.40, 0.07), "light": (0.92, 0.70, 0.08),
    "lens": (0.95, 0.94, 0.88), "steel": (0.42, 0.43, 0.45), "blade": (0.30, 0.31, 0.33),
    "rubber": (0.05, 0.05, 0.055), "bag": (0.16, 0.16, 0.17), "cord": (0.85, 0.45, 0.06),
    "concrete": (0.55, 0.54, 0.51), "concrete_fresh": (0.66, 0.65, 0.62), "rebar": (0.36, 0.21, 0.13),
}


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def _u(*k):
    return _h(*k) / 4294967296.0


def _form(form):
    """The form's canonical name: `auto` and empty are `cut`."""
    form = (form or "auto").lower()
    return "cut" if form in ("auto", "") else form


def parse_form(form):
    """``(cause, slab, plaster)`` for a form name; refuses one it does not know."""
    form = _form(form)
    if form not in FORMS:
        raise ValueError("hole form %r is not one of %s" % (form, ", ".join(FORMS)))
    cause = form.split("_", 1)[0]
    return cause, "_slab" in form, form.endswith("_plaster")


# -- the edge ------------------------------------------------------------------------------------

def edge_frame(w, d, h):
    """Where the hole, the floor and the ceiling are inside an edge slot of `w` x `d` x `h`:
    ``{hx, hy}`` the hole's half sizes; ``zf`` the visible floor; ``slab_top``, ``slab_bot``;
    ``zc`` the visible ceiling; ``thick`` the slab."""
    hx, hy = w / 2.0 - BAND, d / 2.0 - BAND
    zf = h - TOP
    zc = HANG
    slab_top, slab_bot = zf - SKIN, zc + SKIN
    return {"hx": hx, "hy": hy, "zf": zf, "zc": zc, "slab_top": slab_top, "slab_bot": slab_bot,
            "thick": slab_top - slab_bot}


def perimeter(hx, hy, step=STEP):
    """Samples round the hole's rectangle, counter-clockwise from its south-west corner:
    ``[(x, y, nx, ny, side)]`` -- the point, its outward normal (a corner takes the bisector) and
    its side ("S", "E", "N", "W"; a corner belongs to the side it starts)."""
    out = []
    corners = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
    normals = [(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)]
    names = ["S", "E", "N", "W"]
    for k in range(4):
        (x0, y0), (x1, y1) = corners[k], corners[(k + 1) % 4]
        n = max(2, int(round(math.hypot(x1 - x0, y1 - y0) / step)))
        prev = normals[k - 1]
        cn = (prev[0] + normals[k][0], prev[1] + normals[k][1])
        ln = math.hypot(*cn)
        out.append((x0, y0, cn[0] / ln, cn[1] / ln, names[k]))
        for i in range(1, n):
            t = i / n
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, normals[k][0], normals[k][1],
                        names[k]))
    return out


def _noise(seed, i, n, octaves=((3, 0.55), (7, 0.30), (13, 0.15))):
    """A smooth closed noise round a loop of `n` samples, 0..1."""
    v = 0.0
    for o, a in octaves:
        ph = _u(seed, "ph", o) * 2.0 * math.pi
        v += a * (0.5 + 0.5 * math.sin(2.0 * math.pi * o * i / n + ph))
    return v


#: A hanging shard's thickness by what it is.
HANGER_THICK = {"tile": 0.016, "grid": 0.03, "plaster": 0.022, "lath": 0.008}


def hang_limit(length, thick):
    """The steepest a `length` x `thick` plate hinged at its top edge may hang and drop no more
    than HANG: length * sin(a) + thick * cos(a) = HANG, in radians (a plate too short to reach
    HANG hangs straight down)."""
    r = math.hypot(length, thick)
    if r <= HANG:
        return math.pi / 2.0
    return math.asin(HANG / r) - math.atan2(thick, length)


def hanger_drop(length, thick, angle_deg):
    """How far below the ceiling a hanger reaches, metres."""
    a = math.radians(angle_deg)
    return length * math.sin(a) + thick * math.cos(a)


def edge_plan(w, d, h, form="auto", variant=0):
    """The torn edge round a hole.

    ``ring``: one ``(ox, oy, ix, iy, droop)`` a perimeter sample -- the collar's outer corner (where
    the floor finish is torn back to), its inner corner (where the underlayer ends: past the cut
    into the opening for a tooth, short of it for a recess) and how far that inner end sags.
    ``joists``: boxes ``(cx, cy, cz, sx, sy, sz, pitch_deg, axis)`` -- the joist ends in the slab's
    thickness, pitched about `axis` where one hangs. ``walls``: plates ``(kind, cx, cy, cz, sx, sy,
    sz)`` lining the cut -- ``void`` the dark floor cavity between joist ends, ``rim`` the rim
    joist's face along the sides the joists run beside. ``hangers``: ``(hx, hy, nx, ny, width, length,
    thick, angle_deg, kind)`` -- a shard hinged at the ceiling's edge at (hx, hy), hanging into
    the opening (along -normal) by `angle_deg` below the ceiling. ``cavity``: ``(ox, oy, ix, iy)``
    a sample -- the ring under the ceiling where it is broken back from the hole.

    The collar's outer edge reaches the slot's faces at one sample a side and the lowest hanger
    reaches the slot's bottom, so the module's bounds are the slot's by construction.
    """
    form = _form(form)
    cause, slab, plaster = parse_form(form)
    f = edge_frame(w, d, h)
    hx, hy = f["hx"], f["hy"]
    seed = ("edge", form, int(variant))
    pts = perimeter(hx, hy)
    n = len(pts)
    broken = cause == "broken"
    # how far a tooth may jut, each way: the opening keeps CLEAR metres clear
    tooth_x = max(0.0, min(0.30 if broken else 0.24, (2.0 * hx - CLEAR) / 2.0))
    tooth_y = max(0.0, min(0.30 if broken else 0.24, (2.0 * hy - CLEAR) / 2.0))
    # the one sample a side whose outer corner lies on the slot's face
    touch = {}
    for s in "SENW":
        idx = [i for i, p in enumerate(pts) if p[4] == s and not (p[2] and p[3])]
        touch[s] = idx[int(_u(seed, "touch", s) * len(idx)) % len(idx)]
    teeth = []
    k = 0
    while k < n:
        if _u(seed, "tooth?", k) < (0.30 if broken else 0.24):
            span = 1 + int(_u(seed, "span", k) * (4 if broken else 3))
            teeth.append((k, span, 0.45 + 0.55 * _u(seed, "len", k)))
            k += span + 1
        else:
            k += 1
    ring = []
    for i, (x, y, nx, ny, side) in enumerate(pts):
        corner = nx != 0.0 and ny != 0.0
        reach = 0.05 + 0.19 * _noise((seed, "out"), i, n) + 0.07 * _u(seed, "o", i)
        if i == touch.get(side) and not corner:
            reach = BAND
        reach = min(reach, BAND if not corner else BAND * 0.85)
        ox, oy = x + nx * reach, y + ny * reach
        # the inner end: never short of the cut -- the underlayer IS the cut's edge, and an end on
        # the slab's cut plane would share it -- so 6 mm past it at least, a tooth where one is
        inner = 0.006 + 0.045 * _noise((seed, "in"), i, n)
        droop = 0.0
        for k0, span, ln in teeth:
            j = (i - k0) % n
            if j < span + 1:
                cap = tooth_x if side in ("E", "W") else tooth_y
                if corner:
                    cap = min(tooth_x, tooth_y)
                shape = 1.0 - abs((j - span / 2.0) / (span / 2.0 + 1.0))
                inner = max(inner, cap * ln * shape)
                droop = max(droop, (0.10 if broken else 0.025) * ln * shape)
        ix, iy = x - nx * inner, y - ny * inner
        ring.append((ox, oy, ix, iy, droop))
    # the joist ends: joists run along Y, so the cut crossed them on the S and N sides
    joists = []
    jt, jd = 0.05, min(0.24, max(0.04, f["thick"] - 0.04))
    jz = f["slab_top"] - 0.02 - jd / 2.0
    x = -hx + 0.08 + 0.32 * _u(seed, "j0")
    j = 0
    while x < hx - 0.06 and not slab:
        for side, sy in (("S", -hy), ("N", hy)):
            proud = 0.015 + (0.10 if broken else 0.05) * _u(seed, "jp", j, side)
            pitch = 0.0
            if broken and _u(seed, "jh", j, side) < 0.35:
                pitch = 14.0 + 24.0 * _u(seed, "ja", j, side)
            inward = 1.0 if side == "S" else -1.0
            back = 0.06
            cy = sy + inward * (proud - back) / 2.0
            joists.append((round(x, 4), round(cy, 4), round(jz, 4), jt, round(proud + back, 4),
                           round(jd, 4), round(pitch * -inward, 3), "X"))
        x += 0.40
        j += 1
    # THE CUT'S OWN WALLS, so the opening reads as a floor broken through and not a slab sawn: on
    # the sides the joists cross, the dark floor cavity between joist ends; on the two sides the
    # joists run along, the rim joist's face. Each a 4 mm plate whose face stands PROUD into the
    # opening off the cut plane, from under the subfloor (2 cm below the slab's top) to the slab's
    # bottom -- so no face of it lies on the slab's, and the joist ends stand in front of it.
    walls = []
    rebar = _rebar(f, seed, broken) if slab else []
    # A void stops WALL_GAP under the joists' tops and runs 3 mm into each joist beside it (its end
    # then no closer than that to the joist's side), and a rim board stops WALL_GAP short of each
    # corner, so no face of one lies within the census's 2 mm of a face of another.
    z_hi, z_lo = f["slab_top"] - 0.02 - WALL_GAP, f["slab_bot"] + 0.002
    wz, wd = (z_hi + z_lo) / 2.0, max(0.02, z_hi - z_lo)
    xs = sorted({round(jx, 4) for jx, *_rest in joists})
    edges_x = [-hx] + [v for x0 in xs for v in (x0 - jt / 2.0 + 0.003, x0 + jt / 2.0 - 0.003)] + [hx]
    for side, sy in (("S", -hy), ("N", hy)):
        inward = 1.0 if side == "S" else -1.0
        for a, b in zip(edges_x[0::2], edges_x[1::2]):
            if b - a > 0.01 and not slab:
                walls.append(("void", round((a + b) / 2.0, 4),
                              round(sy + inward * (PROUD - 0.002), 4), round(wz, 4),
                              round(b - a, 4), 0.004, round(wd, 4)))
    for side, sx in (("W", -hx), ("E", hx)) if not slab else ():
        inward = 1.0 if side == "W" else -1.0
        walls.append(("rim", round(sx + inward * (PROUD - 0.002), 4), 0.0, round(wz, 4),
                      0.004, round(2.0 * hy - 2.0 * (PROUD + WALL_GAP), 4), round(wd, 4)))
    # the hangers: shards hinged at the ceiling's edge, hanging into the opening. A plate of
    # `length` x `thick` hinged at its top edge and turned `a` below the ceiling drops
    # length * sin(a) + thick * cos(a): no hanger may drop past HANG, the slot's bottom, and none
    # may reach further into the opening than CLEAR leaves free
    hangers = []
    kinds = ("plaster", "lath") if plaster else ("tile", "grid")
    count = 6 if plaster else 5
    used = []
    for k in range(count * 3):
        if len(hangers) >= count:
            break
        i = int(_u(seed, "hi", k) * n) % n
        x, y, nx, ny, side = pts[i]
        if nx != 0.0 and ny != 0.0:
            continue
        kind = kinds[1] if _u(seed, "hk", k) < (0.4 if plaster else 0.25) else kinds[0]
        width = (0.03 if kind == "lath" else 0.04 if kind == "grid"
                 else 0.22 + 0.30 * _u(seed, "hw", k))
        if any(abs(x - ux) + abs(y - uy) < (width + uw) / 2.0 + 0.08 for ux, uy, uw in used):
            continue
        used.append((x, y, width))
        thick = HANGER_THICK[kind]
        length = 0.32 + 0.28 * _u(seed, "hl", k)
        free = ((2.0 * hx) if side in ("E", "W") else (2.0 * hy)) - CLEAR
        angle = math.radians(30.0 + 45.0 * _u(seed, "ha", k))
        angle = min(angle, hang_limit(length, thick))
        if length * math.cos(angle) > free / 2.0:
            # too long to hang that shallow: steeper, and shorter if steeper is not allowed
            angle = max(angle, math.acos(min(1.0, (free / 2.0) / length)))
            if angle > hang_limit(length, thick):
                length = max(0.12, free / 2.0 / max(math.cos(hang_limit(length, thick)), 0.2))
                angle = min(hang_limit(length, thick), math.radians(75.0))
        hangers.append([round(x, 4), round(y, 4), nx, ny, round(width, 4), round(length, 4), thick,
                        angle, kind])
    # the lowest hanger reaches the slot's bottom exactly: long enough to (a hole too small to let
    # any hanger hang shallow can leave them all short of HANG), at its own limit's angle, which
    # hangs it steep enough to keep its reach into the opening small
    if hangers:
        low = max(range(len(hangers)), key=lambda q: hangers[q][5])
        hangers[low][5] = round(max(hangers[low][5], HANG + 0.02), 4)
        hangers[low][7] = hang_limit(hangers[low][5], hangers[low][6])
    for hh in hangers:
        hh[7] = round(math.degrees(hh[7]), 6)
    # the cavity: the ceiling broken back from the hole, a jagged ring just under it
    cavity = []
    for i, (x, y, nx, ny, side) in enumerate(pts):
        corner = nx != 0.0 and ny != 0.0
        back = 0.06 + 0.16 * _noise((seed, "cav"), i, n)
        back = min(back, BAND * (0.8 if corner else 0.95))
        cavity.append((x + nx * back, y + ny * back, x, y))
    return {"form": form, "cause": cause, "slab": slab, "plaster": plaster, "frame": f,
            "ring": ring, "joists": joists, "walls": walls, "rebar": rebar,
            "hangers": [tuple(hh) for hh in hangers], "cavity": cavity}


def _rebar(f, seed, broken):
    """A concrete slab's bars where the cut went through it: ``[(x0, y0, z0, x1, y1, z1)]`` rods from
    4 cm inside the slab out past the cut face into the opening -- the top mat, and in a `broken`
    slab half the bottom mat's too; short where a saw went through, long and bent down where the floor
    tore. Spaced 0.30 m along each side; none reaches further in than CLEAR leaves free."""
    hx, hy = f["hx"], f["hy"]
    mats = [f["slab_top"] - 0.05] + ([f["slab_bot"] + 0.05] if broken else [])
    out = []
    sides = (("S", 0.0, -hy, 0.0, -1.0, hx), ("N", 0.0, hy, 0.0, 1.0, hx),
             ("W", -hx, 0.0, -1.0, 0.0, hy), ("E", hx, 0.0, 1.0, 0.0, hy))
    for side, sx, sy, nx, ny, along in sides:
        free = (2.0 * (hy if side in ("S", "N") else hx) - CLEAR) / 2.0
        t = -along + 0.12 + 0.15 * _u(seed, "rb0", side)
        k = 0
        while t < along - 0.10:
            for m, z in enumerate(mats):
                if m == 1 and _u(seed, "rbm", side, k) < 0.5:
                    continue
                if broken:
                    ln = 0.06 + 0.14 * _u(seed, "rbl", side, k, m)
                else:
                    ln = 0.03 + 0.07 * _u(seed, "rbl", side, k, m)
                ln = min(ln, max(0.0, free - 0.02))
                bend = 0.0
                if broken and _u(seed, "rbh", side, k, m) < 0.5:
                    bend = math.radians(20.0 + 40.0 * _u(seed, "rbb", side, k, m))
                px, py = (t, sy) if side in ("S", "N") else (sx, t)
                ix, iy = -nx, -ny                       # into the opening
                x0, y0, z0 = px - ix * 0.04, py - iy * 0.04, z
                x1 = px + ix * ln * math.cos(bend)
                y1 = py + iy * ln * math.cos(bend)
                z1 = z - ln * math.sin(bend)
                out.append(tuple(round(v, 4) for v in (x0, y0, z0, x1, y1, z1)))
            t += 0.30
            k += 1
    return out


# -- the spoil -----------------------------------------------------------------------------------

def _rect_corners(cx, cy, sx, sy, yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    return [(cx + c * ax - s * ay, cy + s * ax + c * ay)
            for ax, ay in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2))]


def _overlap(a, b, gap=0.012):
    """Do two convex polygons (corner lists) come within `gap`? Separating-axis test."""
    for poly in (a, b):
        for i in range(len(poly)):
            x0, y0 = poly[i]
            x1, y1 = poly[(i + 1) % len(poly)]
            ax, ay = y0 - y1, x1 - x0
            ln = math.hypot(ax, ay) or 1.0
            ax, ay = ax / ln, ay / ln
            pa = [px * ax + py * ay for px, py in a]
            pb = [px * ax + py * ay for px, py in b]
            if max(pa) + gap < min(pb) or max(pb) + gap < min(pa):
                return False
    return True


#: A stray thrown to a face stops this far inside it, metres.
EDGE_IN = 0.0002

#: A spoil's bar is straight for two thirds of its length and bent at the third; the bend throws its
#: end sideways by up to this share of the bent third's length (the tangent of the bend, ~14 degrees).
#: The throw is drawn here and is part of the bar's plan width, so the overlap test sees the bent
#: bar. The first build bent it in the recipe after placing it, and the census read a fragment on it.
REBAR_THROW = 0.25

#: What a spoil is made of: (kind, count range, length range, width range, thickness) -- the floor
#: that came down, by cause and construction, then the ceiling it came through, then fragments. A
#: `slab` chunk's thickness is 0: it is a fracture, its height drawn between 5 cm and the slot's.
FLOOR_PIECES = {
    ("cut", False): (("panel", (2, 3), (0.45, 0.85), (0.32, 0.6), 0.022),
                     ("joist", (1, 2), (0.45, 0.85), (0.24, 0.24), 0.05)),
    ("broken", False): (("plank", (4, 6), (0.55, 1.30), (0.09, 0.14), 0.022),
                        ("joist", (1, 1), (0.50, 0.90), (0.24, 0.24), 0.05)),
    ("cut", True): (("slab", (3, 5), (0.22, 0.45), (0.16, 0.38), 0.0),
                    ("rebar", (1, 3), (0.35, 0.80), (0.012, 0.012), 0.012)),
    ("broken", True): (("slab", (4, 6), (0.25, 0.55), (0.18, 0.42), 0.0),
                       ("rebar", (2, 4), (0.45, 1.00), (0.012, 0.012), 0.012)),
}
CEILING_PIECES = {
    False: (("tile", (3, 5), (0.30, 0.60), (0.22, 0.60), 0.016),
            ("grid", (1, 2), (0.55, 1.10), (0.024, 0.024), 0.03)),
    True: (("plaster", (3, 5), (0.20, 0.50), (0.18, 0.42), 0.022),
           ("lath", (3, 6), (0.40, 0.90), (0.03, 0.03), 0.008)),
}
CHUNKS = {"cut": ("chunk", (5, 8), (0.05, 0.14), (0.05, 0.12), 0.0),
          "broken": ("chunk", (6, 10), (0.06, 0.16), (0.05, 0.14), 0.0)}


def spoil_rows(form):
    """The (kind, counts, lengths, widths, thickness) rows a form's spoil is drawn from."""
    cause, slab, plaster = parse_form(form)
    return FLOOR_PIECES[(cause, slab)] + CEILING_PIECES[plaster] + (CHUNKS[cause],)


def spoil_plan(w, d, h, form="auto", variant=0):
    """What came down through the hole: ``[(kind, cx, cy, sx, sy, sz, yaw_rad)]`` lying on the floor
    of a `w` x `d` slot, each at its own height `sz` (<= `h`), none within a centimetre of another
    in plan, most of them under the opening (the slot's middle) and a few thrown to its edges. The
    tallest chunk is `h` tall, and one piece a side reaches the slot's face, so the module's bounds
    are the slot's."""
    form = _form(form)
    parse_form(form)
    seed = ("spoil", form, int(variant))
    placed = []
    polys = []

    def try_place(kind, k, sx, sy, sz, spread, edge=None):
        for t in range(80):
            yaw = _u(seed, kind, k, t, "yaw") * math.pi
            if edge is None:
                cx = (2.0 * _u(seed, kind, k, t, "x") - 1.0) * (w / 2.0) * spread
                cy = (2.0 * _u(seed, kind, k, t, "y") - 1.0) * (d / 2.0) * spread
            else:
                along = (2.0 * _u(seed, kind, k, t, "a") - 1.0) * 0.6
                cx, cy = {"S": (along * w / 2.0, -d / 2.0), "N": (along * w / 2.0, d / 2.0),
                          "W": (-w / 2.0, along * d / 2.0), "E": (w / 2.0, along * d / 2.0)}[edge]
                # pull the piece in until its outermost corner is EDGE_IN inside the face (the
                # stored values are rounded, and a corner on the face can round past it)
                corners = _rect_corners(0.0, 0.0, sx, sy, yaw)
                if edge in ("S", "N"):
                    ext = max(abs(py) for _px, py in corners) + EDGE_IN
                    cy = cy + (ext if edge == "S" else -ext)
                else:
                    ext = max(abs(px) for px, _py in corners) + EDGE_IN
                    cx = cx + (ext if edge == "W" else -ext)
            # judged on the values as they are stored, rounded, so the plan a caller reads is the
            # plan that was checked
            row = (kind, round(cx, 4), round(cy, 4), round(sx, 4), round(sy, 4), round(sz, 4),
                   round(yaw, 5))
            poly = _rect_corners(row[1], row[2], row[3], row[4], row[6])
            if any(abs(px) > w / 2.0 or abs(py) > d / 2.0 for px, py in poly):
                continue
            if any(_overlap(poly, q) for q in polys):
                continue
            polys.append(poly)
            placed.append(row)
            return True
        return False

    # THE KEYSTONE FIRST: one chunk the slot's full height, near the middle where the most came
    # down, placed before anything can crowd it out -- so the module is the slot's height
    for k in range(8):
        if try_place("chunk", 200 + k, 0.11 + 0.04 * _u(seed, "key", k), 0.09, h, 0.35):
            break
    drawn = []
    for kind, (c0, c1), (l0, l1), (w0, w1), thick in spoil_rows(form):
        count = c0 + int(_u(seed, kind, "n") * (c1 - c0 + 1))
        for k in range(count):
            sx = l0 + (l1 - l0) * _u(seed, kind, k, "l")
            sy = w0 + (w1 - w0) * _u(seed, kind, k, "w")
            if kind == "chunk":
                sz = min(h, 0.035 + 0.05 * _u(seed, kind, k, "h"))
            elif kind == "slab":
                sz = min(h, 0.05 + 0.05 * _u(seed, kind, k, "h"))
            else:
                sz = min(h, thick)
            if kind == "rebar":
                # the bar's width is its section `thick`; its plan is that and the bend's throw
                sy = sy + REBAR_THROW * (sx / 3.0) * _u(seed, kind, k, "bend")
            spread = 0.62 if kind in ("panel", "plank", "joist", "slab") else 0.86
            drawn.append((k, kind, sx, sy, sz, spread))
    # ONE OF EACH KIND FIRST, then the rest, each in its rows' order. Placed row by row, a small
    # slot filled with the floor's pieces before the ceiling's were reached, and the ceiling's are
    # what say what the drop came through: the walk-ups' 1.7 x 1.83 m spoil carried no ceiling tile
    # in three variants of four. The draws are keyed by kind and index, so only the order moves.
    for k, kind, sx, sy, sz, spread in sorted(drawn, key=lambda row: row[0] > 0):
        try_place(kind, k, sx, sy, sz, spread)
    # a stray chunk at each face, so the spoil reaches the slot's edges as debris thrown wide does
    for e, side in enumerate("SENW"):
        sx = 0.06 + 0.06 * _u(seed, "stray", side, "l")
        try_place("chunk", 100 + e, sx, sx * 0.8, min(h, 0.03 + 0.02 * _u(seed, "stray", side)),
                  1.0, edge=side)
    return placed


# -- the kit -------------------------------------------------------------------------------------

def kit_plan(w, d, h, form="auto", variant=0):
    """The crew's kit beside a hole they broke through, local +Y toward the hole: a tarp the
    slot's whole width and depth, a work light on a stand at one end aimed down into the opening
    (its head's top at `h`), a cut-off saw in the middle nearest the hole, a toolbag at the other
    end with an extension cord coiled flat in front of it, and a pry bar along the back. The
    zones are fixed so no item can stand in another; `flip` mirrors them end for end.
    ``{"tarp", "saw", "bag", "coil", "bar", "light"}``, each a dict of the numbers the recipe
    builds it from."""
    form = _form(form)
    seed = ("kit", form, int(variant))
    flip = -1.0 if _u(seed, "flip") < 0.5 else 1.0          # which end the light stands at
    tarp = {"w": w, "d": d, "t": 0.012, "fold": 0.11 + 0.04 * _u(seed, "fold")}
    light = {"cx": round(flip * (w / 2.0 - 0.16), 4), "cy": round(d * 0.18, 4),
             "foot": 0.16, "head": (0.22, 0.12, 0.16), "tilt_deg": 38.0, "top": h}
    saw = {"cx": round(flip * (w / 2.0 - 0.58), 4),
           "cy": round(d * (0.12 + 0.05 * _u(seed, "sy")), 4),
           "yaw": round((_u(seed, "syaw") - 0.5) * 0.3, 4), "blade_r": 0.16}
    bag = {"cx": round(-flip * (w / 2.0 - 0.26), 4),
           "cy": round(-d * (0.16 + 0.04 * _u(seed, "by")), 4),
           "yaw": round((_u(seed, "byaw") - 0.5) * 0.3, 4), "sx": 0.44, "sy": 0.24, "sz": 0.26}
    coil = {"cx": round(-flip * (w / 2.0 - 0.17), 4), "cy": round(d * 0.28, 4),
            "r": 0.11, "tube": 0.012, "turns": 3}
    bar = {"cx": round(flip * 0.10, 4), "cy": round(-d * 0.42, 4),
           "len": round(min(0.62, w * 0.45), 4), "r": 0.011}
    return {"form": form, "tarp": tarp, "saw": saw, "bag": bag, "coil": coil, "bar": bar,
            "light": light}
