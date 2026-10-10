"""The backdrop beyond the plate's edge, planned in pure Python (Zoo 1.95.0, roadmap 228 step C).

The walker picked E from the edge menu (`docs/findings/edge_menu/` at the factory root): a
chain-link fence at the plate's edge, rows of rowhomes with lit windows behind it and a water
tower as the landmark, under a sodium glow. The menu's mockup drew the houses as boxes with a
window quad per lit window and found they "read as buildings by their lit windows, and only by
those": flat-roofed blocks need a roofline. This module plans what the two recipes draw:

  * `backdrop_rowhome`: ONE painted box with a cornice, a chimney and a stoop, its windows and
    door in the paint, the lit ones in the emission map. One material, one surface, so a band of
    houses is one MultiMesh and one draw a side (CLAUDE.md: draw calls are the budget, and
    colour-only variation belongs in instance data or an atlas, never in a material).
  * `water_tower`: a tank on four braced legs with a beacon, the one cue the menu's frames read
    as a landmark.

EXACT FIT (roadmap 44, Zoo's contract for every kit module): a module's extents ARE the slot's
dims. So the rowhome's body is narrower than the slot by the cornice's overhang, shallower by the
stoop, and lower by the chimney, and the whole stands exactly (w, d, h); the tower's cap is no
wider than its tank and its beacon's top is the slot's top. The first build of each failed
`fit_width`, `fit_depth` and `fit_height` for want of this.

Both are BACKDROP: no collision, never inside the playable extent, placed by Lot's bands (step
D) and composed by Level Factory as MultiMeshes (step E). Nothing here needs bpy.
"""
from __future__ import annotations

import math
import random

# --- the rowhome's facade ------------------------------------------------------------------------

#: The painted image: the facade in the left FACADE_PX columns, a brick strip for the sides and
#: back, a dark strip for the roof, the cornice and the stoop. Nearest-filtered and clamped, as
#: every painted face is, so a region never bleeds into its neighbour.
FACADE_PX = 64
STRIP_PX = 16
IMG_W = FACADE_PX + 2 * STRIP_PX
IMG_H = 128
STOREYS = 3
#: a window, metres; two a storey, the ground storey's left one a door
WINDOW_W = 0.9
WINDOW_H = 1.4
DOOR_W = 1.0
DOOR_H = 2.1
#: the mockup's rule: one window in five is lit, and one in five of those is a TV's blue
LIT_SHARE = 0.2
TV_SHARE = 0.2
#: the roofline the mockup lacked, metres: the cornice overhangs the body by CORNICE_SIDE each
#: side and CORNICE_OUT in front; the stoop stands STOOP[1] in front of the body; the chimney
#: adds CHIMNEY[2] above it. All inside the slot's dims.
CORNICE_SIDE = 0.1
CORNICE_OUT = 0.3
CORNICE_H = 0.4
CHIMNEY = (0.6, 0.6, 1.0)
STOOP = (1.4, 0.9, 0.5)
#: A part that stands on or against another is pushed this far INTO it, so no
#: face of one lies in a face of the other: `tools/coplanar_census.py` found
#: the cornice's back on the body's front, the chimney's foot on the roof,
#: the tower's legs' tops on the tank's bottom and its cap's foot on the
#: tank's top (the cruiser's `INSET`, for the same reason). A pair of faces
#: in one plane fights at every distance.
INSET = 0.004

WARM = (255, 200, 122)
TV_BLUE = (140, 166, 242)
UNLIT = (22, 24, 30)
LIT_PANE = (150, 118, 72)
DOOR = (30, 26, 24)
TAR = (28, 28, 30)


def body_dims(w: float, d: float, h: float) -> tuple:
    """The body box inside a slot of (w, d, h): its (width, depth, height) and
    the y of its front plane in the module frame (front toward -Y)."""
    bw = w - 2.0 * CORNICE_SIDE
    bd = d - STOOP[1]
    bh = h - CHIMNEY[2]
    y_front = -d / 2.0 + STOOP[1]
    return bw, bd, bh, y_front


def windows(bw: float, bh: float) -> list:
    """The facade's openings, in facade metres from its bottom-left corner:
    ``[(kind, x0, z0, x1, z1), ...]`` with kind "window" or "door", two a storey,
    the ground storey's left one the door. ``bw``, ``bh`` are the body's."""
    out = []
    storey = bh / STOREYS
    for s in range(STOREYS):
        for j, cx in enumerate((bw * 0.25, bw * 0.75)):
            if s == 0 and j == 0:
                out.append(("door", cx - DOOR_W / 2.0, 0.0, cx + DOOR_W / 2.0, DOOR_H))
                continue
            sill = s * storey + storey * 0.3
            out.append(("window", cx - WINDOW_W / 2.0, sill, cx + WINDOW_W / 2.0, sill + WINDOW_H))
    return out


def lit_pattern(key: str, n: int) -> list:
    """Which of ``n`` windows are lit, deterministic for ``key`` (a module's stem):
    ``[None | "warm" | "tv", ...]``. Two widths or heights are two keys, so a band
    drawn from a few modules shows a few patterns."""
    rng = random.Random("backdrop_rowhome|" + key)
    out = []
    for _ in range(n):
        if rng.random() < LIT_SHARE:
            out.append("tv" if rng.random() < TV_SHARE else "warm")
        else:
            out.append(None)
    return out


def _px_x(x: float, bw: float) -> int:
    return int(round(x / bw * FACADE_PX))


def _px_z(z: float, bh: float) -> int:
    """Image rows run top down; facade metres run bottom up."""
    return int(round(IMG_H - z / bh * IMG_H))


def facade_boxes(bw: float, bh: float) -> list:
    """`windows` as pixel boxes ``(kind, x0, y0, x1, y1)`` on the facade region."""
    out = []
    for kind, x0, z0, x1, z1 in windows(bw, bh):
        out.append((kind, _px_x(x0, bw), _px_z(z1, bh), _px_x(x1, bw), _px_z(z0, bh)))
    return out


def paint(bw: float, bh: float, brick, key: str):
    """The albedo and emission images for a facade of body width ``bw`` and
    height ``bh``, as `core.paint.Img`s: brick with its courses, a cornice
    band, the windows (lit ones warm or a TV's blue), the door; the emission
    black but for the lit panes. Returns (albedo, emission, lit), ``lit`` the
    pattern used."""
    from . import paint as P
    base = tuple(int(round(c * 255)) for c in brick)
    dark = tuple(max(0, int(c * 0.82)) for c in base)
    darker = tuple(max(0, int(c * 0.6)) for c in base)
    img = P.Img(IMG_W, IMG_H, base)
    emi = P.Img(IMG_W, IMG_H, (0, 0, 0))
    # courses on the facade and the brick strip, every fourth row
    for y in range(0, IMG_H, 4):
        img.rect((0, y, FACADE_PX + STRIP_PX, y + 1), dark)
    # the roof strip
    img.rect((FACADE_PX + STRIP_PX, 0, IMG_W, IMG_H), TAR)
    # the cornice: a darker band under the parapet, a lighter line on the parapet's top
    img.rect((0, 0, FACADE_PX, 3), tuple(min(255, int(c * 1.15)) for c in base))
    img.rect((0, 3, FACADE_PX, 8), darker)
    boxes = facade_boxes(bw, bh)
    lit = lit_pattern(key, sum(1 for b in boxes if b[0] == "window"))
    k = 0
    for kind, x0, y0, x1, y1 in boxes:
        if kind == "door":
            img.rect((x0, y0, x1, y1), DOOR)
            continue
        state = lit[k]
        k += 1
        if state is None:
            img.rect((x0, y0, x1, y1), UNLIT)
        else:
            img.rect((x0, y0, x1, y1), LIT_PANE)
            emi.rect((x0, y0, x1, y1), TV_BLUE if state == "tv" else WARM)
        # a sill
        img.rect((x0 - 1, y1, x1 + 1, y1 + 1), darker)
    return img, emi, lit


def uv_for(co, normal, w: float, d: float, h: float):
    """Where a corner of the rowhome lands in the painted image, in Blender's
    UV space (v 0 at the image's bottom). The body's front face (normal toward
    -Y, on the body's own front plane) takes the facade; the roof, the
    cornice's and stoop's faces take the dark strip; everything else the brick
    strip, courses running with height and a metre of brick a strip width."""
    x, y, z = co
    nx, ny, nz = normal
    bw, bd, bh, y_front = body_dims(w, d, h)
    z0 = -h / 2.0
    v = min(1.0, max(0.0, (z - z0) / bh))
    if ny < -0.5 and abs(y - y_front) < 1e-3:
        return (min(1.0, max(0.0, (x + bw / 2.0) / bw)) * FACADE_PX / IMG_W, v)
    if nz > 0.5 or ny < -0.5 or z > z0 + bh + 1e-4:
        u0 = (FACADE_PX + STRIP_PX) / IMG_W
        return (u0 + ((x + y) % 1.0) * (STRIP_PX - 2) / IMG_W + 1.0 / IMG_W, v)
    u0 = FACADE_PX / IMG_W
    return (u0 + ((x + y) % 1.0) * (STRIP_PX - 2) / IMG_W + 1.0 / IMG_W, v)


def rowhome_parts(w: float, d: float, h: float) -> list:
    """The boxes the recipe adds, ``[(name, centre, size), ...]`` in the module
    frame (Z up, centre pivot, front toward -Y), standing exactly (w, d, h)
    together: the body, the cornice at the top of its front, a chimney on the
    roof near the back, the stoop at the door."""
    bw, bd, bh, y_front = body_dims(w, d, h)
    z0 = -h / 2.0
    body_top = z0 + bh
    door_x = -bw / 4.0
    # the cornice's back, the stoop's back and the chimney's foot stand INSET
    # inside the body; the cornice's top sits INSET under the body's, so no
    # face shares a plane with another
    cornice_d = CORNICE_OUT + INSET
    stoop_d = STOOP[1] + INSET
    chimney_h = CHIMNEY[2] + INSET
    return [
        ("body", (0.0, y_front + bd / 2.0, z0 + bh / 2.0), (bw, bd, bh)),
        ("cornice", (0.0, y_front + INSET - cornice_d / 2.0, body_top - INSET - CORNICE_H / 2.0),
         (w, cornice_d, CORNICE_H)),
        ("chimney", (bw / 4.0, y_front + bd - 0.8, body_top - INSET + chimney_h / 2.0),
         (CHIMNEY[0], CHIMNEY[1], chimney_h)),
        # the stoop's foot stands INSET above the body's, or the strip of it
        # inside the body lies in the body's bottom plane (the census' last
        # pair, 56 cm2: the stoop's width by the inset)
        ("stoop", (door_x, -d / 2.0 + stoop_d / 2.0, z0 + INSET + STOOP[2] / 2.0),
         (STOOP[0], stoop_d, STOOP[2])),
    ]


def extents(parts) -> tuple:
    """(width, depth, height) spanned by ``[(name, centre, size), ...]``."""
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for _n, c, s in parts:
        for i in range(3):
            lo[i] = min(lo[i], c[i] - s[i] / 2.0)
            hi[i] = max(hi[i], c[i] + s[i] / 2.0)
    return tuple(hi[i] - lo[i] for i in range(3))


# --- the water tower -----------------------------------------------------------------------------

#: fractions of the tower's height: the legs' top and the tank's top; the cap runs from the
#: tank's top to the beacon, whose top is the slot's top
LEG_TOP = 0.70
TANK_TOP = 0.90
LEG = 0.5
BRACE_AT = (0.3, 0.55)
BRACE = 0.18
BEACON_R = 0.6
BEACON_RGB = (1.0, 0.12, 0.08)
BEACON_STRENGTH = 3.0
TANK_SEGMENTS = 16


def tower_parts(w: float, h: float) -> dict:
    """The tower's pieces in the module frame: four legs with two rings of
    braces, the tank (its radius the slot's half width, so the extents are
    exact), its cap no wider than the tank, and the beacon whose top is the
    slot's top. Returns a dict of lists of (centre, size) for the boxes and
    the cylinders' figures."""
    z0 = -h / 2.0
    r = w / 2.0
    leg_r = r * 0.7
    legs, braces = [], []
    # the legs reach INSET into the tank's bottom; the braces run between the
    # legs' inner faces and INSET into them, the ring's two directions one
    # brace-thickness apart in height so no two cross in one plane
    leg_h = h * LEG_TOP + INSET
    for sx in (-1, 1):
        for sy in (-1, 1):
            legs.append(((sx * leg_r, sy * leg_r, z0 + leg_h / 2.0), (LEG, LEG, leg_h)))
    span = 2.0 * leg_r - LEG + 2.0 * INSET
    for f in BRACE_AT:
        z = z0 + h * f
        braces.append(((0.0, -leg_r, z), (span, BRACE, BRACE)))
        braces.append(((0.0, leg_r, z), (span, BRACE, BRACE)))
        braces.append(((-leg_r, 0.0, z + BRACE), (BRACE, span, BRACE)))
        braces.append(((leg_r, 0.0, z + BRACE), (BRACE, span, BRACE)))
    tank_h = h * (TANK_TOP - LEG_TOP)
    cap_top = h - 2.0 * BEACON_R
    cap_h = cap_top - h * TANK_TOP + INSET
    return {
        "legs": legs, "braces": braces,
        "tank": ((0.0, 0.0, z0 + h * LEG_TOP + tank_h / 2.0), r, tank_h),
        "cap": ((0.0, 0.0, z0 + h * TANK_TOP - INSET + cap_h / 2.0), r, cap_h),
        "beacon": ((0.0, 0.0, z0 + h - BEACON_R), BEACON_R),
    }


def tower_tris_estimate(segments: int = TANK_SEGMENTS) -> int:
    """What the tower costs in triangles, for the genome's budget: boxes at 12,
    two cylinders at 4 a segment, a 10 x 6 sphere at about 100."""
    return 12 * (4 + 8) + 2 * 4 * segments + int(math.ceil(10 * 6 * 2 * 0.9))


# --- the backdrop tree (1.96.0) ------------------------------------------------------------------
#
# The parkland and roadside recipes' belt: a trunk and a faceted crown, the
# menu's mockup's shape, cheap enough that a belt of six hundred is a few
# MultiMeshes. Not a street tree: those are grown branch by branch at two
# thousand triangles for a kerb the player walks past; a backdrop tree stands
# behind the fence, twenty to forty metres off.

#: the trunk's share of the height, and its width
TREE_STEM = 0.35
TREE_TRUNK = 0.4
#: the crown's facets: twelve around (a vertex on both axes, so the extents
#: are the slot's, as `water_tank` learned at fourteen) and six up
TREE_U_SEG = 12
TREE_V_SEG = 6
#: a dark green a backdrop crown reads as at night and by day, before the
#: style's own leaf; the trunk's bark
TREE_LEAF = (0.16, 0.26, 0.14)
TREE_BARK = (0.24, 0.19, 0.15)


def tree_parts(w: float, h: float) -> dict:
    """The tree in the module frame: a trunk box from the foot to the crown's
    centre and a crown ellipsoid whose top is the slot's top and whose width
    and depth are the slot's width."""
    z0 = -h / 2.0
    stem = h * TREE_STEM
    rz = (h - stem) / 2.0
    return {
        "trunk": ((0.0, 0.0, z0 + (stem + rz) / 2.0), (TREE_TRUNK, TREE_TRUNK, stem + rz)),
        "crown": ((0.0, 0.0, z0 + stem + rz), (w / 2.0, w / 2.0, rz)),
    }


def tree_tris_estimate() -> int:
    return 12 + TREE_U_SEG * TREE_V_SEG * 2


# --- the backdrop warehouse (1.96.0) -------------------------------------------------------------
#
# The yards recipe's far bands: a long low box with roof monitors, its front
# painted as siding with a roll-up door and a strip of high windows, a few of
# them lit. One material, one surface, as the rowhome.

MONITOR_H = 1.2
MONITORS = 3
DOOR_W_WH = 4.0
DOOR_H_WH = 4.0
WINDOW_STRIP_H = 0.8
WINDOW_PITCH = 3.0
WH_LIT_SHARE = 0.33
COOL = (200, 215, 235)
#: a lit industrial pane by day: the cool white's own tint, not the rowhome's warm one
COOL_PANE = (168, 178, 192)
WH_SIDING = (0.56, 0.56, 0.52)


def warehouse_parts(w: float, d: float, h: float) -> list:
    """The boxes the recipe adds, standing exactly (w, d, h): the body under
    the monitors' height, and MONITORS roof monitors along the roof's centre,
    each INSET into it so no foot lies in the roof's plane."""
    z0 = -h / 2.0
    bh = h - MONITOR_H
    body_top = z0 + bh
    out = [("body", (0.0, 0.0, z0 + bh / 2.0), (w, d, bh))]
    mw = w / (2 * MONITORS + 1)
    for i in range(MONITORS):
        cx = -w / 2.0 + mw * (2 * i + 1.5)
        out.append((f"monitor_{i}", (cx, 0.0, body_top - INSET + (MONITOR_H + INSET) / 2.0),
                    (mw, d * 0.6, MONITOR_H + INSET)))
    return out


def warehouse_openings(bw: float, bh: float) -> list:
    """The front's openings in facade metres from the bottom-left: a roll-up
    door in the left third and a strip of high windows along the top."""
    out = [("door", bw / 6.0 - DOOR_W_WH / 2.0, 0.0, bw / 6.0 + DOOR_W_WH / 2.0, DOOR_H_WH)]
    top = bh - 0.6
    x = bw / 3.0 + 1.0
    while x + WINDOW_PITCH * 0.6 <= bw - 1.0:
        out.append(("window", x, top - WINDOW_STRIP_H, x + WINDOW_PITCH * 0.6, top))
        x += WINDOW_PITCH
    return out


def warehouse_lit(key: str, n: int) -> list:
    """Which high windows are lit: about one in three, cool white, deterministic
    for the module's stem."""
    rng = random.Random("backdrop_warehouse|" + key)
    return ["cool" if rng.random() < WH_LIT_SHARE else None for _ in range(n)]


def paint_warehouse(bw: float, bh: float, siding, key: str):
    """The albedo and emission images for a warehouse's front: siding with its
    vertical seams, a dark roll-up door, the high windows (the lit ones cool
    white in the emission). Returns (albedo, emission, lit)."""
    from . import paint as P
    base = tuple(int(round(c * 255)) for c in siding)
    seam = tuple(max(0, int(c * 0.86)) for c in base)
    dark = tuple(max(0, int(c * 0.55)) for c in base)
    img = P.Img(IMG_W, IMG_H, base)
    emi = P.Img(IMG_W, IMG_H, (0, 0, 0))
    for x in range(0, FACADE_PX + STRIP_PX, 3):
        img.rect((x, 0, x + 1, IMG_H), seam)
    img.rect((FACADE_PX + STRIP_PX, 0, IMG_W, IMG_H), TAR)
    img.rect((0, 0, FACADE_PX, 4), dark)
    boxes = []
    for kind, x0, z0, x1, z1 in warehouse_openings(bw, bh):
        boxes.append((kind, int(round(x0 / bw * FACADE_PX)), int(round(IMG_H - z1 / bh * IMG_H)),
                      int(round(x1 / bw * FACADE_PX)), int(round(IMG_H - z0 / bh * IMG_H))))
    lit = warehouse_lit(key, sum(1 for b in boxes if b[0] == "window"))
    k = 0
    for kind, x0, y0, x1, y1 in boxes:
        if kind == "door":
            img.rect((x0, y0, x1, y1), dark)
            for y in range(y0, y1, 3):
                img.rect((x0, y, x1, y + 1), seam)
            continue
        state = lit[k]
        k += 1
        img.rect((x0, y0, x1, y1), COOL_PANE if state else UNLIT)
        if state:
            emi.rect((x0, y0, x1, y1), COOL)
    return img, emi, lit


def warehouse_uv_for(co, normal, w: float, d: float, h: float):
    """Where a corner of the warehouse lands in its painted image: the body's
    front (normal toward -Y at the body's front plane) takes the facade, the
    roof and the monitors the tar strip, the sides and back the siding strip."""
    x, y, z = co
    nx, ny, nz = normal
    z0 = -h / 2.0
    bh = h - MONITOR_H
    v = min(1.0, max(0.0, (z - z0) / bh))
    if ny < -0.5 and abs(y + d / 2.0) < 1e-3:
        return (min(1.0, max(0.0, (x + w / 2.0) / w)) * FACADE_PX / IMG_W, v)
    if nz > 0.5 or z > z0 + bh + 1e-4:
        u0 = (FACADE_PX + STRIP_PX) / IMG_W
        return (u0 + ((x + y) % 1.0) * (STRIP_PX - 2) / IMG_W + 1.0 / IMG_W, v)
    u0 = FACADE_PX / IMG_W
    return (u0 + ((x + y) % 1.0) * (STRIP_PX - 2) / IMG_W + 1.0 / IMG_W, v)
