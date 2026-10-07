"""The corner deli's service case, decided in pure Python: the enamel base and
its trim, the curved front glass, the steel top the staff work on, the doors
behind, the lit deck -- and every pixel of what is on it.

Zoo 1.81.0, species `deli_case`. Deli Counter's corner deli has stood a
`deli_case_cover` in front of its deli counter since the recipe was written,
and no species answered to the name, so it built as a plain box wearing
glass: in cold run 9189's composed deli_a01,
`prop_delco_1997_03_w700_d110_h130_mglass`, a 7 m slab. It is the one piece
that says what the building is. The walker's store references put "a
hoagie/deli counter further back" in the 1990s store
(docs/SET_DRESSING_REFERENCES.md, 2026-09-15); a corner deli is that counter
as a whole business.

THE BRIEF (the authorship guide's three questions).
  * What it is for. The family behind it slices to order, and the case
    shows what there is. Whole logs lie on their sides with the cut end to
    the glass, so a customer can tell the provolone from the ham; the salads
    sit in steel pans in front; every pan has a white card with its price.
  * Who touches it. Customers lean on the bumper and point through the
    glass; the staff reach in from behind through the doors and wrap on the
    steel top. Shoes scuff the black kick.
  * What it is made of. A white enamel base with one accent band and a
    steel bumper rail, curved glass, a stainless top, one fluorescent tube
    under the top's front edge lighting the deck -- and the plastic parsley a
    deli lines its pans with.

WHAT IS BUILT, in the recipe frame (metres, Z up, floor 0, CENTRE pivot, x
along the run, -Y the CUSTOMER, +Y the staff):
  * the KICK, set back; the BASE, enamel; the TRIM band and the BUMPER rail,
    proud of the base at the slot's front;
  * the DECK, whose top is the lit image of the cards, the parsley, the pans
    and the trays, one tile a bay;
  * the FRONT GLASS, curved in `FACETS` facets from its foot at the deck to
    its head under the top, and an END PANE of glass at each end;
  * the TOP, stainless, the slot's full width, and the TUBE under its front
    edge;
  * the REAR glass on the staff side, over a black rail;
  * the LOGS and BLOCKS on the deck's back half: cylinders and boxes whose cut
    faces, toward the glass, carry a painted cross-section.

THREE SUBMISSIONS whatever the length, the cooler wall's: painted metal
(every enamel, steel and black part, its colour in the `Wear` vertex colour),
the glass, and the glow -- the deck, the tube and every log and block on ONE
backlit image, ``M_DeliCase_<art>_Face``, which Lux's power cut takes.

NO TWO FACES SHARE A PLANE (`prims.coincident_pairs` at the test's 2.2 mm is
empty): every part meeting another is buried into it, and every pair of
parallel faces whose projections overlap stands 4 mm or more apart.
"""
from __future__ import annotations

import math
import re
import zlib

from . import card_art as CA
from . import paint as PT
from . import prims as P
from . import smooth_type as ST

#: Deli Counter's volume: `deli_case_cover` as Deli Counter 0.199.0 trims it
#: off its wall, and as it stood before. Then the genome's range.
DC_SIZES = ((5.815, 1.1, 1.3), (7.0, 1.1, 1.3))
RANGES = {"width": (1.2, 8.0), "depth": (0.8, 1.4), "height": (1.1, 1.5)}

BURY = 0.004
KICK_H = 0.10
KICK_SET = 0.05           # the kick behind the slot's front
BASE_SET = 0.012          # the base's front behind the slot's: the trim stands proud
BASE_BACK = 0.020         # the base's back inside the slot's
END_T = 0.020             # an end pane's thickness
END_IN = 0.005            # an end pane's outer face inside the slot's end
BODY_IN = 0.012           # the base's ends inside the slot's
TRIM_IN = 0.018           # the trim's and the bumper's ends inside the slot's
KICK_IN = 0.030
DECK_T = 0.02
DECK_Z_MAX = 0.80         # the deck's top: a case shows its product at the hip
DECK_HEAD = 0.45          # the least the glass rises above the deck
GLASS_T = 0.008
GLASS_RUN = 0.42          # the glass's head this far behind the slot's front
GLASS_FOOT = 0.016        # the glass's foot this far behind the slot's front
FACETS = 3
TOP_T = 0.035
TUBE_W = 0.035
TUBE_T = 0.014
REAR_IN = 0.030           # the rear glass's plane inside the slot's back
PANE_OUT = 0.010          # an end pane's curve outside the glass's outer face: its
                          # front then stands 6 mm off the base's (at 6 mm out, 2)
PANE_BACK = 0.008         # an end pane's back inside the slot's
BAY = 1.2                 # a case section; the deck is painted a bay at a time
TILES_MAX = 6             # bays past this reuse a tile: a long case, a bounded image
PIECE_GAP = 0.04          # between two pieces on the deck
LOG_SINK = 0.006          # a log's flat bottom facet under the deck's top
TEXEL = 300               # px a metre of the deck image
CUT_PX = 72               # a cut face's tile
SWATCH_PX = 16            # a casing's tile: sampled at its centre

#: Colours (linear) and surface kind of every part that does not glow.
MATERIALS = {
    "enamel": ((0.86, 0.86, 0.83), "metal_painted"),
    "trim": ((0.55, 0.08, 0.07), "metal_painted"),
    "steel": ((0.70, 0.71, 0.72), "metal_painted"),
    "black": ((0.02, 0.02, 0.022), "metal_painted"),
    "glass": ((0.80, 0.86, 0.88), "glass"),
}
KIND_BASE = {"metal_painted": (1.0, 1.0, 1.0), "glass": (0.80, 0.86, 0.88)}
#: The accent band, by variant: deli red, walnut, Kelly green, navy.
TRIM_COLOURS = ((0.55, 0.08, 0.07), (0.30, 0.17, 0.08), (0.05, 0.28, 0.12), (0.06, 0.10, 0.30))
GLASS_OPACITY = 0.20
#: The glow's emission and its dimmed diffuse copy. The cooler's is 1.0 and
#: backlit; this deck is product under a tube, so it starts lower. To be
#: judged on the walk.
GLOW_EMISSION = 0.7
GLOW_ALBEDO = 0.6

#: What lies on the deck's back half: (shape, casing sRGB, size). A log is a
#: cylinder on its side, its cut end to the glass: (radius, length). A block
#: is a box: (width, length, height).
PIECES = {
    "provolone": ("log", (226, 196, 112), (0.066, 0.34)),
    "genoa": ("log", (128, 40, 38), (0.050, 0.30)),
    "capicola": ("log", (118, 34, 26), (0.055, 0.28)),
    "ham": ("log", (214, 140, 120), (0.070, 0.26)),
    "turkey": ("log", (196, 148, 92), (0.064, 0.27)),
    "roast_beef": ("log", (88, 50, 34), (0.060, 0.24)),
    "american": ("block", (238, 162, 44), (0.10, 0.24, 0.09)),
    "swiss": ("block", (238, 222, 160), (0.12, 0.22, 0.10)),
}
#: The salads in front, painted: (fill sRGB, fleck sRGB).
PANS = {
    "potato_salad": ((236, 220, 160), (150, 120, 60)),
    "coleslaw": ((232, 236, 214), (110, 160, 70)),
    "macaroni_salad": ((240, 226, 180), (220, 140, 60)),
    "roasted_peppers": ((190, 40, 30), (240, 120, 30)),
    "olives": ((40, 46, 30), (90, 110, 50)),
    "cherry_peppers": ((200, 30, 30), (250, 210, 200)),
    "tuna_salad": ((214, 196, 156), (150, 140, 110)),
    "chicken_salad": ((236, 224, 190), (120, 170, 80)),
}
PRICES = ("2.99", "3.49", "3.99", "4.49", "4.99", "5.99", "6.49", "7.99")
PAN = (0.165, 0.17)       # a sixth pan, across and deep
PAN_GAP = 0.015
_VARIANT = re.compile(r"_n\d+(?=_|$)")


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def resolve(plan_):
    params = plan_.get("params") or {}
    module = plan_.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    key = _VARIANT.sub("", module.get("stem") or "") or "deli_case"
    return key, variant


def vertex_tint(mat_key, variant=0):
    """``(kind, factor)``: the surface kind a part builds in and the vertex
    colour that tints that kind's base to the part's colour."""
    rgb, kind = MATERIALS[mat_key]
    if mat_key == "trim":
        rgb = TRIM_COLOURS[variant % len(TRIM_COLOURS)]
    return kind, tuple(c / b for c, b in zip(rgb, KIND_BASE[kind]))


def deck_z(h):
    return min(DECK_Z_MAX, h - DECK_HEAD)


def bays(w):
    """``(n, bay_width)``: the case's sections between its end panes."""
    run = w - 2.0 * (END_IN + END_T)
    n = max(1, int(round(run / BAY)))
    return n, run / n


def _glass_curve(y_foot, z_foot, y_head, z_head, inset=0.0):
    """The front glass's profile, foot to head, as ``FACETS + 1`` points
    ``(y, z)``: a quarter ellipse about ``(y_head, z_foot)``, upright at the
    foot and level at the head, ``inset`` inside it."""
    ry, rz = (y_head - y_foot) - inset, (z_head - z_foot) - inset
    out = []
    for k in range(FACETS + 1):
        t = 0.5 * math.pi * k / FACETS
        out.append((y_head - ry * math.cos(t), z_foot + rz * math.sin(t)))
    return out


def _glass(x0, x1, outer, inner):
    """The curved pane as one primitive: a slab between the two profiles,
    capped at both ends. Every face is a convex quad."""
    n = len(outer)
    verts = [(x0, y, z) for y, z in outer] + [(x1, y, z) for y, z in outer] \
        + [(x0, y, z) for y, z in inner] + [(x1, y, z) for y, z in inner]
    o0, o1, i0, i1 = 0, n, 2 * n, 3 * n
    faces = []
    for k in range(n - 1):
        faces.append((o0 + k, o1 + k, o1 + k + 1, o0 + k + 1))      # outside
        faces.append((i0 + k + 1, i1 + k + 1, i1 + k, i0 + k))      # inside
        faces.append((o0 + k, o0 + k + 1, i0 + k + 1, i0 + k))      # the x0 end
        faces.append((o1 + k + 1, o1 + k, i1 + k, i1 + k + 1))      # the x1 end
    faces.append((o0, i0, i1, o1))                                  # the foot
    faces.append((o0 + n - 1, o1 + n - 1, i1 + n - 1, i0 + n - 1))  # the head
    return P.mesh("DeliCase_Glass", "glass", verts, faces)


def _end_pane(xa, xb, profile, y_back, z_low):
    """An end pane: the case's display profile -- the glass's outer curve, the
    top's underside, the back -- between ``xa`` and ``xb``. Convex: the curve
    bulges outward."""
    pts = [(profile[0][0], z_low)] + list(profile) + [(y_back, profile[-1][1]), (y_back, z_low)]
    # drop the first curve point when it repeats the foot's (y) at z_low
    poly = []
    for p in pts:
        if not poly or abs(poly[-1][0] - p[0]) > 1e-9 or abs(poly[-1][1] - p[1]) > 1e-9:
            poly.append(p)
    n = len(poly)
    verts = [(xa, y, z) for y, z in poly] + [(xb, y, z) for y, z in poly]
    # the polygon runs foot -> head -> back -> down: clockwise seen from +X,
    # so the xb face takes it reversed to look outward along +X
    faces = [tuple(range(n)), tuple(n + k for k in reversed(range(n)))]
    for k in range(n):
        k1 = (k + 1) % n
        faces.append((k1, k, n + k, n + k1))
    return P.mesh("DeliCase_EndPane", "glass", verts, faces)


def glow_box(part, lo, hi, faces):
    """A box on the glow image. ``faces`` maps a face index (`P.box`'s: 0
    bottom, 1 top, 2 -Y, 3 +X, 4 +Y, 5 -X) to ``("region", name)`` -- the
    face mapped edge to edge onto that rect -- or ``("solid", name)``, its
    centre; a face not named takes the dark pixel."""
    p = P.box(part, "glow", lo, hi)
    x0, y0, z0 = lo
    x1, y1, z1 = hi

    def corner(k, i):
        x, y, z = p["verts"][i]
        how = faces.get(k)
        if how is None:
            return ("dark",)
        if how[0] == "solid":
            return ("solid", how[1])
        if k in (0, 1):
            return (how[1], (x - x0) / (x1 - x0), (y - y0) / (y1 - y0))
        if k in (2, 4):
            return (how[1], (x - x0) / (x1 - x0), (z - z0) / (z1 - z0))
        return (how[1], (y - y0) / (y1 - y0), (z - z0) / (z1 - z0))
    p["uvs"] = [tuple(corner(k, i) for i in f) for k, f in enumerate(p["faces"])]
    return p


def _deck(xs, y0, y1, z0, z1, regions):
    """The deck as ONE closed mesh, cut at each bay's edge ``xs``: a top face
    a bay mapping its tile, the rest dark. Boxes a bay each met face to face
    at every joint (a coplanar pair the length of the deck's depth)."""
    verts = []
    for x in xs:
        verts += [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)]
    faces, uvs = [], []
    for i in range(len(xs) - 1):
        a, b = 4 * i, 4 * (i + 1)
        u = lambda k, x0=xs[i], x1=xs[i + 1], r=regions[i]: (
            r, (verts[k][0] - x0) / (x1 - x0), (verts[k][1] - y0) / (y1 - y0))
        top = (a + 3, b + 3, b + 2, a + 2)
        faces.append(top)
        uvs.append(tuple(u(k) for k in top))
        for f in ((a + 1, b + 1, b + 0, a + 0),          # bottom
                  (a + 0, b + 0, b + 3, a + 3),          # front, -Y
                  (b + 1, a + 1, a + 2, b + 2)):         # back, +Y
            faces.append(f)
            uvs.append(tuple(("dark",) for _ in f))
    last = 4 * (len(xs) - 1)
    for f in ((1, 0, 3, 2), (last + 0, last + 1, last + 2, last + 3)):   # -X, +X ends
        faces.append(f)
        uvs.append(tuple(("dark",) for _ in f))
    p = P.mesh("DeliCase_Glow", "glow", verts, faces)
    p["uvs"] = uvs
    return p


def _log(kind, xc, y_front, z_floor, r, length, segments=12):
    """A log on its side on the deck, its cut end at ``y_front`` toward the
    glass. Its flat bottom facet lies `LOG_SINK` under the deck's top: at
    `BURY` from the centre, a 12-gon's facet stood 1.6-2.1 mm under it, a
    coplanar pair. The cut face maps the ``<kind>_cut`` disc, the casing the
    ``<kind>_side`` swatch."""
    zc = z_floor + r * math.cos(math.pi / segments) - LOG_SINK
    p = P.lay_along_y(P.cyl("DeliCase_Glow", "glow", (xc, -zc), r, y_front, y_front + length,
                            segments=segments, phase=math.pi / segments))
    n = segments
    uvs = []
    for k, f in enumerate(p["faces"]):
        if k == 0:                                  # the cut, toward the glass
            row = []
            for i in f:
                x, _y, z = p["verts"][i]
                row.append((kind + "_cut", 0.5 + 0.5 * (x - xc) / r, 0.5 + 0.5 * (z - zc) / r))
            uvs.append(tuple(row))
        else:
            uvs.append(tuple(("solid", kind + "_side") for _ in f))
    p["uvs"] = uvs
    assert len(p["faces"]) == n + 2
    return p


def layout(w, d, h, key="deli_case", variant=0):
    """Every part at slot (w, d, h): ``(prims, facts)``."""
    out = []
    yf, yb = -d / 2.0, d / 2.0
    hx = w / 2.0
    dz = deck_z(h)
    z_top0 = h - TOP_T                       # the top's underside
    # --- the base ---------------------------------------------------------------
    out.append(P.box("DeliCase_Kick", "black", (-hx + KICK_IN, yf + KICK_SET, 0.0),
                     (hx - KICK_IN, yb - BASE_BACK - 0.010, KICK_H)))
    out.append(P.box("DeliCase_Base", "enamel", (-hx + BODY_IN, yf + BASE_SET, KICK_H - BURY),
                     (hx - BODY_IN, yb - BASE_BACK, dz - DECK_T + BURY)))
    out.append(P.box("DeliCase_Trim", "trim", (-hx + TRIM_IN, yf, dz - 0.16),
                     (hx - TRIM_IN, yf + BASE_SET + BURY, dz - 0.10)))
    out.append(P.box("DeliCase_Bumper", "steel", (-hx + TRIM_IN, yf, dz - 0.07),
                     (hx - TRIM_IN, yf + BASE_SET + BURY, dz - 0.035)))
    # --- the glass, the panes, the top and the tube ---------------------------------
    z_foot = dz - 0.03
    y_foot = yf + GLASS_FOOT
    y_head = yf + min(GLASS_RUN, 0.45 * d)
    z_head = z_top0 + 0.009                 # 9 mm up into the top
    outer = _glass_curve(y_foot, z_foot, y_head, z_head)
    inner = _glass_curve(y_foot, z_foot, y_head, z_head, inset=GLASS_T)
    xin = hx - END_IN - END_T               # the panes' inner faces
    out.append(_glass(-xin - BURY, xin + BURY, outer, inner))
    # THE PANES FRAME THE GLASS: their curve `PANE_OUT` outside its outer
    # face, so no facet of either lies within the coplanar test of the other
    # (0.4-2.0 mm when the pane followed the glass); their backs `PANE_BACK`
    # inside the slot's, past the rear glass and its rail
    frame = _glass_curve(y_foot, z_foot, y_head, z_head, inset=-PANE_OUT)
    for s in (-1, 1):
        xa, xb = sorted((s * (hx - END_IN), s * xin))
        out.append(_end_pane(xa, xb, frame, yb - PANE_BACK, z_foot - 0.008))
    out.append(P.box("DeliCase_Top", "steel", (-hx, y_head - 0.015, z_top0), (hx, yb, h)))
    tube = glow_box("DeliCase_Glow", (-xin + 0.02, y_head + 0.010, z_top0 - TUBE_T),
                    (xin - 0.02, y_head + 0.010 + TUBE_W, z_top0 + BURY),
                    {k: ("solid", "tube") for k in range(6)})
    out.append(tube)
    # --- the staff side ---------------------------------------------------------------
    yr = yb - REAR_IN
    out.append(P.box("DeliCase_Rear", "glass", (-xin - BURY, yr - GLASS_T / 2.0, dz - 0.010),
                     (xin + BURY, yr + GLASS_T / 2.0, z_top0 + 0.006)))
    # the rail's ends 5 mm inside the base's (at 1 mm they were a pair)
    out.append(P.box("DeliCase_Rail", "black", (-hx + BODY_IN + 0.005, yr - 0.015, dz - 0.030),
                     (hx - BODY_IN - 0.005, yr + 0.015, dz + 0.020)))
    # --- the deck: a tile a bay ----------------------------------------------------------
    n, bw = bays(w)
    dy0, dy1 = yf + 0.030, yr - 0.015 - 0.005
    xs = [-xin + 0.006] + [-xin + i * bw for i in range(1, n)] + [xin - 0.006]
    tiles = [i % TILES_MAX for i in range(n)]
    out.append(_deck(xs, dy0, dy1, dz - DECK_T, dz, ["bay_%d" % t for t in tiles]))
    # --- the pieces on the deck's back half -------------------------------------------
    kinds = sorted(PIECES)
    order = sorted(kinds, key=lambda k: _h(key, variant, "piece", k))
    x = -xin + 0.05
    placed = []
    j = 0
    y_stop = dy1 - 0.03
    while True:
        kind = order[j % len(order)]
        shape, _rgb, size = PIECES[kind]
        width = 2.0 * size[0] if shape == "log" else size[0]
        if x + width > xin - 0.05:
            break
        if shape == "log":
            r, length = size
            out.append(_log(kind, x + r, y_stop - length, dz, r, length))
        else:
            bw_, length, bh = size
            out.append(glow_box("DeliCase_Glow", (x, y_stop - length, dz - BURY),
                                (x + bw_, y_stop, dz - BURY + bh),
                                {2: ("region", kind + "_cut"), **{k: ("solid", kind + "_side")
                                                                  for k in (0, 1, 3, 4, 5)}}))
        placed.append(kind)
        x += width + PIECE_GAP + 0.01 * (_h(key, variant, "gap", j) % 3)
        j += 1
    facts = {"bays": n, "bay_width": bw, "tiles": sorted(set(tiles)), "pieces": placed,
             "deck": (dy0, dy1), "deck_z": dz, "glass_head": (y_head, z_head),
             "collision": ((-hx, yf, 0.0), (hx, yb, h))}
    return out, facts


def plan(w, d, h, key="deli_case", variant=0):
    """``{prims, facts}`` -- the slot filled exactly."""
    prims, facts = layout(w, d, h, key, variant)
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


# --- the glow --------------------------------------------------------------------------

def _lift(rgb, by):
    return tuple(max(0.0, min(255.0, c + by)) for c in rgb)


def _px(m):
    return int(round(m * TEXEL))


def _flecks(im, box, rgb, n, size, seed):
    x0, y0, x1, y1 = box
    for k in range(n):
        hx = _h(seed, k, "x") % 1000 / 1000.0
        hy = _h(seed, k, "y") % 1000 / 1000.0
        cx, cy = x0 + hx * (x1 - x0), y0 + hy * (y1 - y0)
        im.disc(cx, cy, size * (0.6 + 0.8 * (_h(seed, k, "s") % 100) / 100.0), rgb, 0.85)


def _pan(im, box, kind, seed):
    """A steel sixth-pan seen from above: the rim, then the salad, mounded --
    lighter in the middle, where the tube is -- and flecked."""
    fill, fleck = PANS[kind]
    x0, y0, x1, y1 = box
    im.rrect((x0, y0, x1, y1), 3, (196, 198, 200))                    # the rim
    im.rect((x0, y0, x1, y0 + 2), (236, 238, 240), 0.8)
    inner = (x0 + 4, y0 + 4, x1 - 4, y1 - 4)
    im.rrect(inner, 4, fill)
    im.vgrad(inner, _lift(fill, 10), _lift(fill, -14))
    if kind == "olives":
        _flecks(im, inner, (24, 26, 18), 40, 4.5, seed)
        _flecks(im, inner, fleck, 14, 4.0, seed + 1)
    elif kind == "cherry_peppers":
        _flecks(im, inner, (220, 36, 34), 18, 7.0, seed)
        _flecks(im, inner, (150, 20, 20), 10, 3.0, seed + 1)
    elif kind == "roasted_peppers":
        for k in range(9):
            yy = inner[1] + (k + 0.5) * (inner[3] - inner[1]) / 9.0
            im.rect((inner[0] + 2, yy - 2, inner[2] - 2, yy + 2), fleck if k % 2 else _lift(fill, 20), 0.9)
    else:
        _flecks(im, inner, fleck, 30, 1.6, seed)
        _flecks(im, inner, _lift(fill, 24), 20, 2.4, seed + 7)
    im.edge_dark(inner, 4, 0.30)


def _card(im, box, price):
    """A white price card standing at the deck's front edge."""
    x0, y0, x1, y1 = box
    im.rect((x0 + 1, y0 + 2, x1 + 1, y1 + 2), (0, 0, 0), 0.25)       # its shadow
    im.rect(box, (248, 248, 242))
    im.rect((x0, y0, x1, y0 + 2), (200, 30, 30))                      # the red header
    im.text(price, (x0 + 2, y0 + 3, x1 - 2, y1 - 1), (24, 24, 28), ST.owned("shop"), min_cap=4)


def _parsley(im, x0, x1, ya, yb):
    """The plastic parsley: a green fringe, tooth by tooth."""
    im.rect((x0, ya, x1, yb), (30, 110, 40))
    step = 5
    for k, x in enumerate(range(int(x0), int(x1), step)):
        im.tri_down(x + step / 2.0, ya, step / 2.0, (yb - ya) * 0.9,
                    (60, 160, 60) if k % 2 else (40, 136, 50), 0.9)


def _tray(im, box, meat, seed):
    """A tray of sliced meat on white deli paper: fanned shingles."""
    x0, y0, x1, y1 = box
    im.rect(box, (236, 234, 226))
    m = PIECES[meat][1]
    k = 0
    x = x0 + 4
    while x < x1 - 14:
        im.disc(x + 10, (y0 + y1) / 2.0 + (k % 2) * 3 - 1.5, 10, _lift(m, 30 if meat in ("ham", "turkey") else 50), 1.0)
        im.disc(x + 10, (y0 + y1) / 2.0 + (k % 2) * 3 - 1.5, 10, _lift(m, -10), 0.25)
        x += 9
        k += 1
    im.edge_dark(box, 3, 0.2)


def _deck_tile(t, bw, depth, key, variant):
    """One bay's deck, seen from above: row 0 is the BACK, the last row the
    front at the glass's foot. From the front: the cards, the parsley, the
    pans, a second fringe, the trays; behind them the liner the logs lie on,
    lit brightest under the tube."""
    W, H = max(40, _px(bw)), max(40, _px(depth))
    im = PT.Img(W, H, (214, 216, 218))
    im.vgrad((0, 0, W, H), (198, 200, 204), (224, 226, 228))
    seed = _h(key, variant, "bay", t)
    pans = sorted(PANS, key=lambda k: _h(seed, "pan", k))
    pw, pd = _px(PAN[0]), _px(PAN[1])
    gap = _px(PAN_GAP)
    n_pan = max(1, (W - gap) // (pw + gap))
    x_start = (W - (n_pan * pw + (n_pan - 1) * gap)) // 2
    y_card0, y_card1 = H - _px(0.050), H - _px(0.008)
    y_fr0, y_fr1 = H - _px(0.074), H - _px(0.050)
    y_pan1 = y_fr0 - 2
    y_pan0 = y_pan1 - pd
    for i in range(n_pan):
        x0 = x_start + i * (pw + gap)
        _pan(im, (x0, y_pan0, x0 + pw, y_pan1), pans[i % len(pans)], seed + i)
        cw = _px(0.064)
        cx = x0 + (pw - cw) // 2
        _card(im, (cx, y_card0, cx + cw, y_card1), PRICES[_h(seed, "price", i) % len(PRICES)])
    _parsley(im, 0, W, y_fr0, y_fr1)
    _parsley(im, 0, W, y_pan0 - _px(0.024), y_pan0 - 2)
    # the trays: sliced meat behind the pans
    y_tr1 = y_pan0 - _px(0.034)
    y_tr0 = y_tr1 - _px(0.11)
    meats = [k for k in sorted(PIECES) if PIECES[k][0] == "log"]
    tw = _px(0.30)
    x = _px(0.03)
    k = 0
    while x + tw < W - _px(0.03):
        _tray(im, (x, y_tr0, x + tw, y_tr1), meats[_h(seed, "tray", k) % len(meats)], seed + k)
        x += tw + _px(0.05)
        k += 1
    # the tube's light: brightest across the deck under it
    im.vignette((0, 0, W, H), 0.18)
    return im.to_canvas()


def _cut_face(kind):
    """A piece's cross-section, the disc (or the block's face) a customer
    sees through the glass."""
    S = CUT_PX
    shape, casing, _size = PIECES[kind]
    im = PT.Img(S, S, casing)
    c = S / 2.0
    if shape == "block":
        face = {"american": (244, 178, 60), "swiss": (244, 230, 172)}[kind]
        im.rect((0, 0, S, S), face)
        im.vgrad((0, 0, S, S), _lift(face, 8), _lift(face, -10))
        if kind == "swiss":
            for k in range(7):
                im.disc(8 + (_h(kind, k, "x") % (S - 16)), 8 + (_h(kind, k, "y") % (S - 16)),
                        3 + _h(kind, k) % 5, _lift(face, -40), 0.9)
        im.edge_dark((0, 0, S, S), 4, 0.3)
        return im.to_canvas()
    rim = _lift(casing, -30)
    im.disc(c, c, c, rim)                                  # the casing's edge
    inside = {"provolone": (246, 236, 196), "genoa": (176, 52, 58), "capicola": (190, 70, 66),
              "ham": (236, 160, 158), "turkey": (238, 218, 186), "roast_beef": (176, 72, 70)}[kind]
    im.disc(c, c, c - 3, inside)
    if kind == "roast_beef":
        im.disc(c, c, c - 3, (130, 76, 60), 0.6)            # done at the edge
        im.disc(c, c, c - 10, inside)                       # rare in the middle
    if kind == "genoa":
        _flecks(im, (8, 8, S - 8, S - 8), (240, 226, 214), 34, 1.6, 11)
        _flecks(im, (8, 8, S - 8, S - 8), (40, 20, 20), 14, 1.0, 12)
    if kind == "capicola":
        for k in range(5):
            im.disc(c + (_h(kind, k, "x") % 30) - 15, c + (_h(kind, k, "y") % 30) - 15,
                    4 + _h(kind, k) % 6, (232, 214, 204), 0.7)
    if kind in ("ham", "turkey"):
        im.disc(c, c, c - 3, _lift(inside, 18), 0.35)
    if kind == "provolone":
        for k in range(4):
            im.disc(c + (_h(kind, k, "x") % 34) - 17, c + (_h(kind, k, "y") % 34) - 17, 1.5,
                    _lift(inside, -30), 0.8)
    im.gloss((0, 0, S, S), 0.12)
    return im.to_canvas()


def _swatch(rgb):
    return PT.Img(SWATCH_PX, SWATCH_PX, rgb).to_canvas()


def glow_art(w, d, h, key="deli_case", variant=0):
    """ONE image for everything that glows: a deck tile a bay (to
    `TILES_MAX`), each piece's cut face and casing, the white tube and the
    dark block, packed with a gutter each tile bleeds into, because the image
    is sampled with filtering. ``{canvas, size, rects, name, unset}``; rects
    are pixel boxes, row 0 at the top."""
    n, bw = bays(w)
    dy0 = -d / 2.0 + 0.030
    dy1 = d / 2.0 - REAR_IN - 0.020
    tiles, unset = [], []
    for t in range(min(n, TILES_MAX)):
        c = _deck_tile(t, bw, dy1 - dy0, key, variant)
        unset += c.unset
        tiles.append(("bay_%d" % t, c))
    for kind in sorted(PIECES):
        tiles.append((kind + "_cut", _cut_face(kind)))
        tiles.append((kind + "_side", _swatch(PIECES[kind][1])))
    tiles.append(("tube", PT.Img(24, 24, (255, 255, 248)).to_canvas()))
    tiles.append(("dark", PT.Img(24, 24, (14, 14, 16)).to_canvas()))
    A = CA.atlas(tiles, f"delicaseglow_v{variant % 4}", gutter=CA.SMOOTH_GUTTER, bleed=True)
    A["unset"] = unset
    return A
