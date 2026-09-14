"""cargo_container recipe: an ISO shipping container, 10, 20, 40 or 45 ft.

REBUILT, 0.82.0. The walker, walk 9052_rain, looking at `cover_136`: "this
needs some more love to look like a cargo container". What shipped was the
minting placeholder -- one bevelled box, 44 tris, on a near-white tintable
metal pack tinted grey. `core/container_forms.py` records the measurement
and every decision below; this file only executes them.

WHAT IS BUILT, in the module frame (Z up, metres, centre pivot, length along
Y, door end at -Y):

  * EIGHT CORNER CASTINGS are the envelope. Their outer faces stand
    `CAST_INSET` inside the slot, and the oval apertures on their outer faces
    lie ON the slot's faces -- so the slot's extents are the castings', the
    way a real box is gauged. The castings' bottoms are the slot's floor.
  * THE FRAME: corner posts, top and bottom side rails (with fork pockets on
    a 10 or 20 ft box), a top and bottom rail across the blind end, a door
    header and sill.
  * THE SKIN: trapezoidal corrugated sides and blind end, a corrugated roof,
    each a single sheet whose edges run INTO the frame member beside them.
  * THE DOORS: two leaves, each a frame ring with a pressed infill, four
    locking bars with cam keepers top and bottom, guides, handles and
    retainers, four hinges a leaf, a dark seam between the leaves.
  * THE MARKINGS: ISO 6346 owner code, serial and boxed check digit on the
    right leaf and both sides, the size-type code, a GROSS / TARE block, a
    CSC plate, a warning triangle, and on a carrier's box its name down each
    side. Glyphs are `_legend`'s faceted cells, flat, and they FOLLOW the
    corrugation: a glyph is cut at every rib break and each piece lies on
    its own crest, flank or valley.
  * FORM: every sheet's crests, flanks and valleys are separate surfaces on
    the box's paint at 1.0, 0.80 and 0.66 (`CargoContainer_Walls` and
    `_Doors`, `_RibFlanks`, `_RibValleys`), so the ribs read under a sky
    with no direction, where faceting alone does not
    (`container_forms.FORM_SHADE` has the measurement).
  * WEAR: rust streaks off the top rail and up from the bottom rail, a
    touch-up patch on some walls, and a vertex-colour pass that darkens the
    bottom of the box and varies the paint rib by rib.

NO TWO FACES SHARE A PLANE. Every face of every part stands at a named
distance from the slot boundary on its axis (the constants below), chosen
so no two planes that can overlap are within tools/coplanar_probe.py's 2 mm,
and every flat detail stands `DETAIL_PROUD` off the surface it is painted
on, measured along the wall's outward normal.

A CONTAINER IS CLOSED, SO ITS SKIN IS ONE-SIDED. The sheets and the painted
details are single faces wound outward. No camera reaches the inside: every
sheet edge is buried in a frame member and the door seam is backed.

Collision is the full box: Lot stands it in a lane as cover, and a crew walks
around six metres of steel, not through its corrugations.
"""
from __future__ import annotations

from mathutils import Vector

from ..bpylayer import geometry, materials
from ..core import container_forms as cf
from . import _legend

#: How far a painted detail (glyph, rust, patch, plate) stands off its
#: surface, along the surface's outward normal. On a 39 degree flank the
#: perpendicular distance is 5 x cos(39) = 3.9 mm, still clear of the
#: probe's 2 mm.
DETAIL_PROUD = 0.005
#: A detail painted on a detail (the lines on the CSC plate, the yellow of
#: the warning triangle on its black border) stands this far off that one.
DETAIL_ON_DETAIL = 0.004

#: ISO 1161 corner casting, metres: along the length, across, tall.
CAST_L, CAST_W, CAST_H = 0.178, 0.162, 0.118
#: The castings' outer faces stand this far inside the slot; the apertures
#: painted on them lie on the slot's faces.
CAST_INSET = 0.004
#: Aperture half-sizes: side and end (78 x 51 mm oval), top (124 x 64 mm).
HOLE_SIDE = (0.039, 0.0255)
HOLE_TOP = (0.062, 0.032)

# Planes, as distances IN from the slot's face on their axis. Grouped by the
# face they share an axis with; within a group every value differs by at
# least 4 mm wherever two members can overlap in projection.
# -- the long sides (X)
POST_SIDE = 0.008
BOTTOM_RAIL_SIDE = 0.012
TOP_RAIL_SIDE = 0.016
SIDE_CREST = 0.026            # SIDE_PROFILE depth 0.040 -> valley at 0.066
POCKET_LIP_SIDE = 0.016
POCKET_BACK_SIDE = 0.070
BOTTOM_RAIL_T = 0.080
TOP_RAIL_T = 0.060
REAR_POST_W, FRONT_POST_W = 0.150, 0.120
# -- the door end (-Y)
REAR_POST_END = 0.008
LEVER_END = 0.007
HUB_END = 0.012
KEEPER_END = 0.014
GUIDE_END = 0.015
RETAINER_END = 0.017
HINGE_END = 0.024
BAR_CENTRE = 0.034
BAR_R = 0.017
HEADER_END = 0.044
SILL_END = 0.046
LEAF_FRONT = 0.050
LEAF_BACK = 0.100
LEAF_CREST = 0.056            # channel depth 0.024 -> valley at 0.080
SEAM_BACK = (0.105, 0.125)
REAR_POST_D = 0.200
# -- the blind end (+Y)
FRONT_POST_END = 0.008
FRONT_BOTTOM_RAIL_END = 0.012
FRONT_TOP_RAIL_END = 0.016
END_CREST = 0.026
FRONT_RAIL_D = 0.100
FRONT_POST_D = 0.120
# -- the top (Z) and the bottom (Z, measured up from the floor)
TOP_RAIL_TOP = 0.008
HEADER_TOP = 0.012
FRONT_TOP_RAIL_TOP = 0.016
ROOF_CREST = 0.030            # ROOF_PROFILE depth 0.020 -> valley at 0.050
TOP_RAIL_H = 0.100
HEADER_H = 0.178              # header bottom 0.190 below the top
FRONT_TOP_RAIL_H = 0.120
BOTTOM_RAIL_BOTTOM = 0.0125   # a bottom side rail clears the floor by 12.5 mm
SILL_BOTTOM = 0.016
FRONT_BOTTOM_RAIL_BOTTOM = 0.020
BOTTOM_RAIL_H = 0.160
SILL_H = 0.130
FRONT_BOTTOM_RAIL_H = 0.150
POCKET_LIP_DROP = 0.004       # the lip's top stands 4 mm under the rail's
POCKET_BACK_BOTTOM = 0.024
#: How far one member runs into the member that hides its end.
BURY = 0.010
SHEET_BURY = 0.020

# The doors.
SEAM = 0.005                  # half the gap between the leaves
LEAF_OUTER = 0.130            # leaf's hinge edge, in from the side
LEAF_BOTTOM = 0.100           # leaf's bottom, up from the floor
LEAF_TOP = 0.150              # leaf's top, down from the top
LEAF_RING = 0.055             # leaf frame member width
LEAF_TOP_BAND = 0.45          # flat band above the channels
LEAF_BOTTOM_BAND = 0.15
BAR_AT = (0.16, 0.72)         # bar positions across a leaf, from the seam
LEVER_LEN = 0.26
HANDLE_Z = 1.15               # handle height above the floor
HINGE_AT = (0.08, 0.36, 0.64, 0.92)


def _v(x, y, z):
    return Vector((x, y, z))


def _face(bm, verts, want):
    """A face wound so its normal points along ``want``."""
    f = bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(want) < 0.0:
        f.normal_flip()
    return f


def _box(bm, lo, hi):
    geometry.add_box(bm, tuple((a + b) / 2.0 for a, b in zip(lo, hi)),
                     tuple(b - a for a, b in zip(lo, hi)))


class _Wall:
    """A corrugated surface: ``base(u, v)`` is the crest plane, ``n`` the
    outward normal, ``pts`` the profile breakpoints along u."""

    def __init__(self, base, n, pts):
        self.base, self.n, self.pts = base, Vector(n), pts

    def at(self, u, v, lift=0.0):
        return self.base(u, v) + self.n * (cf.profile_at(self.pts, u) + lift)

    def sheet(self, bm, v0, v1):
        rows = [[bm.verts.new(self.base(u, v) + self.n * off)
                 for (u, off) in self.pts] for v in (v0, v1)]
        form = _form_layer(bm)
        for k in range(len(self.pts) - 1):
            f = _face(bm, [rows[0][k], rows[0][k + 1], rows[1][k + 1], rows[1][k]],
                      self.n)
            um = (self.pts[k][0] + self.pts[k + 1][0]) / 2.0
            f[form] = cf.FORM_SHADE[cf.segment_kind(self.pts, um)]

    def paint(self, bm, poly, lift=DETAIL_PROUD):
        """A flat ``(u, v)`` polygon painted onto the corrugation."""
        n = 0
        for piece in cf.split_at(poly, self.pts):
            _face(bm, [bm.verts.new(self.at(u, v, lift)) for u, v in piece],
                  self.n)
            n += 1
        return n


def _text(wall, bm, text, height, uc, vc, sign, lift=DETAIL_PROUD,
          box_last=False):
    """Lay ``text`` centred at (uc, vc) on ``wall``; glyph x runs along
    ``sign`` * u. Returns the (u0, v0, u1, v1) it covers."""
    glyphs, (tw, th) = _legend.legend(text, height)
    for verts2d, faces in glyphs:
        for f in faces:
            wall.paint(bm, [(uc + sign * verts2d[i][0], vc + verts2d[i][1])
                            for i in f], lift)
    pad = 0.0
    if box_last and glyphs:
        # the check digit's box: a ring of four bars round the last glyph
        xs = [x for x, _z in glyphs[-1][0]]
        pad = 0.22 * height
        t = 0.09 * height
        x0, x1 = min(xs) - pad, max(xs) + pad
        z0, z1 = -th / 2.0 - pad, th / 2.0 + pad
        for bx0, bz0, bx1, bz1 in ((x0, z1 - t, x1, z1), (x0, z0, x1, z0 + t),
                                   (x0, z0 + t, x0 + t, z1 - t),
                                   (x1 - t, z0 + t, x1, z1 - t)):
            us = sorted((uc + sign * bx0, uc + sign * bx1))
            wall.paint(bm, [(us[0], vc + bz0), (us[1], vc + bz0),
                            (us[1], vc + bz1), (us[0], vc + bz1)], lift)
    half_u = tw / 2.0 + pad
    return (uc - half_u, vc - th / 2.0 - pad, uc + half_u, vc + th / 2.0 + pad)


def _hex_hole(bm, centre, axis_u, axis_v, n, a, b):
    """A flat elongated hexagon (a casting aperture) facing ``n``."""
    c = Vector(centre)
    au, av = Vector(axis_u), Vector(axis_v)
    pts = [(-a, 0.0), (-a / 2.0, -b), (a / 2.0, -b), (a, 0.0), (a / 2.0, b),
           (-a / 2.0, b)]
    _face(bm, [bm.verts.new(c + au * u + av * v) for u, v in pts], Vector(n))


def _ring(bm, x0, x1, z0, z1, t, y_front, y_back):
    """A rectangular frame ring in XZ, ``t`` wide, from y_front to y_back (a
    door leaf's frame). Closed: front, back, outer and inner walls."""
    outer = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    inner = [(x0 + t, z0 + t), (x1 - t, z0 + t), (x1 - t, z1 - t), (x0 + t, z1 - t)]
    fo = [bm.verts.new((x, y_front, z)) for x, z in outer]
    fi = [bm.verts.new((x, y_front, z)) for x, z in inner]
    bo = [bm.verts.new((x, y_back, z)) for x, z in outer]
    bi = [bm.verts.new((x, y_back, z)) for x, z in inner]
    cx, cz = (x0 + x1) / 2.0, (z0 + z1) / 2.0
    for k in range(4):
        j = (k + 1) % 4
        _face(bm, [fo[k], fo[j], fi[j], fi[k]], _v(0, -1, 0))
        _face(bm, [bo[k], bo[j], bi[j], bi[k]], _v(0, 1, 0))
        mid_o = _v((outer[k][0] + outer[j][0]) / 2.0 - cx, 0,
                   (outer[k][1] + outer[j][1]) / 2.0 - cz)
        _face(bm, [fo[k], fo[j], bo[j], bo[k]], mid_o)
        _face(bm, [fi[k], fi[j], bi[j], bi[k]], -mid_o)


#: A face float layer naming each sheet face's `container_forms.FORM_SHADE`;
#: `_sort_by_form` reads it to deal the faces out to one mesh per shade, and
#: the layer does not survive that copy.
FORM_LAYER = "cc_form"


def _form_layer(bm):
    return (bm.faces.layers.float.get(FORM_LAYER)
            or bm.faces.layers.float.new(FORM_LAYER))


def _sort_by_form(bm, targets):
    """Copy each face of ``bm`` into ``targets[kind]`` by the form shade it
    was built with (a face without one is a crest), then free ``bm``.
    Winding is kept, so every normal still points out."""
    form = bm.faces.layers.float.get(FORM_LAYER)
    for f in bm.faces:
        val = f[form] if form is not None else 0.0
        kind = "crest"
        for k, s in cf.FORM_SHADE.items():
            if val > 0.0 and abs(val - s) < 1e-4:
                kind = k
        tgt = targets[kind]
        tgt.faces.new([tgt.verts.new(v.co) for v in f.verts])
    bm.free()


def _wear(bm, wear, z_floor, seed, ambient=0.0, grime=0.45, grain=0.22):
    """Write the `Wear` corner colour: the style's cool-up / warm-down ambient
    (`geometry._ambient_tint`, as `geometry.wear_colors` applies it), darker
    toward the floor, and a per-rib grain -- vertices at the same (x, y)
    share a value, so a rib's top and bottom agree and the variation reads as
    vertical streaks. (Measured in walk 9052_rain: cover modules import with
    vertex colour off, so none of this is drawn there today; the rib form is
    in the materials for that reason -- `container_forms.FORM_SHADE`.)"""
    layer = (bm.loops.layers.color.get(geometry.WEAR_LAYER)
             or bm.loops.layers.color.new(geometry.WEAR_LAYER))
    w = max(0.0, min(1.0, float(wear)))
    bm.normal_update()
    for f in bm.faces:
        tint = geometry._ambient_tint(f.normal.z, ambient) if ambient else (1.0, 1.0, 1.0)
        for loop in f.loops:
            co = loop.vert.co
            k = (int(round(co.x * 40.0)) * 73856093) ^ (int(round(co.y * 40.0)) * 19349663) ^ seed
            r = ((k * 2654435761) & 0xFFFF) / 65535.0
            up = max(0.0, 1.0 - (co.z - z_floor) / 0.7)
            g = (1.0 - w * grime * up) * (1.0 - w * grain * r)
            loop[layer][:] = (min(1.0, g * tint[0]), min(1.0, g * tint[1]),
                              min(1.0, g * tint[2]), 1.0)


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    wear = plan["wear"]
    f = cf.resolve(plan, streams)
    wear_rng = streams.stream("container_wear")
    seed = int(wear_rng.random() * 1e9)
    W2, D2, Z0, Z1 = w / 2.0, d / 2.0, -h / 2.0, h / 2.0

    bms = {k: geometry.new_bm() for k in (
        "walls", "frame", "doors", "hardware", "apertures", "markings",
        "plates", "warning", "rust", "patch")}
    B = bms

    # --- castings and apertures --------------------------------------------
    for sx in (-1, 1):
        for sy in (-1, 1):
            xo = sx * (W2 - CAST_INSET)
            xi = sx * (W2 - CAST_INSET - CAST_W)
            yo = sy * (D2 - CAST_INSET)
            yi = sy * (D2 - CAST_INSET - CAST_L)
            for top in (False, True):
                z0 = Z1 - CAST_INSET - CAST_H if top else Z0
                z1 = Z1 - CAST_INSET if top else Z0 + CAST_H
                _box(B["frame"], (min(xo, xi), min(yo, yi), z0),
                     (max(xo, xi), max(yo, yi), z1))
                cy, cx, cz = (yo + yi) / 2.0, (xo + xi) / 2.0, (z0 + z1) / 2.0
                _hex_hole(B["apertures"], (sx * W2, cy, cz), (0, 1, 0), (0, 0, 1),
                          (sx, 0, 0), *HOLE_SIDE)
                _hex_hole(B["apertures"], (cx, sy * D2, cz), (1, 0, 0), (0, 0, 1),
                          (0, sy, 0), *HOLE_SIDE)
                if top:
                    _hex_hole(B["apertures"], (cx, cy, Z1), (0, 1, 0), (1, 0, 0),
                              (0, 0, 1), *HOLE_TOP)

    z_post0 = Z0 + CAST_H - BURY
    z_post1 = Z1 - CAST_INSET - CAST_H + BURY
    y_cast_in = D2 - CAST_INSET - CAST_L + BURY      # a rail's end, buried
    for sx in (-1, 1):
        def xs(a, b):
            return (min(sx * (W2 - a), sx * (W2 - b)), max(sx * (W2 - a), sx * (W2 - b)))
        # corner posts
        x0, x1 = xs(POST_SIDE, REAR_POST_W)
        _box(B["frame"], (x0, -D2 + REAR_POST_END, z_post0),
             (x1, -D2 + REAR_POST_D, z_post1))
        x0, x1 = xs(POST_SIDE, FRONT_POST_W)
        _box(B["frame"], (x0, D2 - FRONT_POST_D, z_post0),
             (x1, D2 - FRONT_POST_END, z_post1))
        # top side rail
        x0, x1 = xs(TOP_RAIL_SIDE, TOP_RAIL_SIDE + TOP_RAIL_T)
        _box(B["frame"], (x0, -y_cast_in, Z1 - TOP_RAIL_TOP - TOP_RAIL_H),
             (x1, y_cast_in, Z1 - TOP_RAIL_TOP))
        # bottom side rail, cut round the fork pockets
        x0, x1 = xs(BOTTOM_RAIL_SIDE, BOTTOM_RAIL_SIDE + BOTTOM_RAIL_T)
        zb0, zb1 = Z0 + BOTTOM_RAIL_BOTTOM, Z0 + BOTTOM_RAIL_BOTTOM + BOTTOM_RAIL_H
        cuts = [-y_cast_in]
        for pc in f["pockets"]:
            cuts += [pc - cf.POCKET_W / 2.0, pc + cf.POCKET_W / 2.0]
        cuts.append(y_cast_in)
        for ya, yb in zip(cuts[0::2], cuts[1::2]):
            _box(B["frame"], (x0, ya, zb0), (x1, yb, zb1))
        for pc in f["pockets"]:
            lx0, lx1 = xs(POCKET_LIP_SIDE, BOTTOM_RAIL_SIDE + BOTTOM_RAIL_T - 0.006)
            _box(B["frame"], (lx0, pc - cf.POCKET_W / 2.0 - BURY, zb0 + cf.POCKET_H),
                 (lx1, pc + cf.POCKET_W / 2.0 + BURY, zb1 - POCKET_LIP_DROP))
            bx0, bx1 = xs(POCKET_BACK_SIDE, POCKET_BACK_SIDE + 0.008)
            # its ends run half as far into the rail as the lip's, so the
            # two never share an end plane
            _box(B["apertures"], (bx0, pc - cf.POCKET_W / 2.0 - BURY / 2.0,
                                  Z0 + POCKET_BACK_BOTTOM),
                 (bx1, pc + cf.POCKET_W / 2.0 + BURY / 2.0, zb0 + cf.POCKET_H + BURY))

    # the blind end's rails, the door end's header and sill
    xr = W2 - FRONT_POST_W + BURY
    _box(B["frame"], (-xr, D2 - FRONT_RAIL_D, Z0 + FRONT_BOTTOM_RAIL_BOTTOM),
         (xr, D2 - FRONT_BOTTOM_RAIL_END, Z0 + FRONT_BOTTOM_RAIL_BOTTOM + FRONT_BOTTOM_RAIL_H))
    _box(B["frame"], (-xr, D2 - FRONT_RAIL_D, Z1 - FRONT_TOP_RAIL_TOP - FRONT_TOP_RAIL_H),
         (xr, D2 - FRONT_TOP_RAIL_END, Z1 - FRONT_TOP_RAIL_TOP))
    xh = W2 - REAR_POST_W + 0.015
    _box(B["frame"], (-xh, -D2 + HEADER_END, Z1 - HEADER_TOP - HEADER_H),
         (xh, -D2 + REAR_POST_D + 0.06, Z1 - HEADER_TOP))
    _box(B["frame"], (-xh, -D2 + SILL_END, Z0 + SILL_BOTTOM),
         (xh, -D2 + REAR_POST_D + 0.06, Z0 + SILL_BOTTOM + SILL_H))

    # --- the skin ------------------------------------------------------------
    taken = {1: [], -1: []}
    walls = {}
    v_side0 = Z0 + BOTTOM_RAIL_BOTTOM + BOTTOM_RAIL_H - SHEET_BURY
    v_side1 = Z1 - TOP_RAIL_TOP - TOP_RAIL_H + SHEET_BURY
    u_side0 = -D2 + REAR_POST_D - SHEET_BURY
    u_side1 = D2 - FRONT_POST_D + SHEET_BURY
    side_pts = cf.corrugation(u_side0, u_side1, cf.SIDE_PROFILE)
    for sx in (-1, 1):
        xc = sx * (W2 - SIDE_CREST)
        wall = _Wall(lambda u, v, xc=xc: _v(xc, u, v), (sx, 0, 0), side_pts)
        wall.sheet(B["walls"], v_side0, v_side1)
        walls[sx] = wall

    end_pts = cf.corrugation(-(W2 - FRONT_POST_W + SHEET_BURY),
                             W2 - FRONT_POST_W + SHEET_BURY, cf.SIDE_PROFILE)
    yc = D2 - END_CREST
    _Wall(lambda u, v: _v(u, yc, v), (0, 1, 0), end_pts).sheet(
        B["walls"], Z0 + FRONT_BOTTOM_RAIL_BOTTOM + FRONT_BOTTOM_RAIL_H - SHEET_BURY,
        Z1 - FRONT_TOP_RAIL_TOP - FRONT_TOP_RAIL_H + SHEET_BURY)

    roof_pts = cf.corrugation(-D2 + REAR_POST_D + 0.06 - SHEET_BURY,
                              D2 - FRONT_RAIL_D + SHEET_BURY, cf.ROOF_PROFILE)
    zc = Z1 - ROOF_CREST
    _Wall(lambda u, v: _v(v, u, zc), (0, 0, 1), roof_pts).sheet(
        B["walls"], -(W2 - TOP_RAIL_SIDE - TOP_RAIL_T + SHEET_BURY),
        W2 - TOP_RAIL_SIDE - TOP_RAIL_T + SHEET_BURY)

    # --- the doors -------------------------------------------------------------
    lz0, lz1 = Z0 + LEAF_BOTTOM, Z1 - LEAF_TOP
    ly0, ly1 = -D2 + LEAF_FRONT, -D2 + LEAF_BACK
    leaf_walls = {}
    for sx in (-1, 1):
        xa, xb = SEAM, W2 - LEAF_OUTER
        x0, x1 = (xa, xb) if sx > 0 else (-xb, -xa)
        _ring(B["doors"], x0, x1, lz0, lz1, LEAF_RING, ly0, ly1)
        iz0, iz1 = lz0 + LEAF_RING, lz1 - LEAF_RING
        pts = cf.channels(iz0 - SHEET_BURY, iz1 + SHEET_BURY,
                          LEAF_TOP_BAND + SHEET_BURY, LEAF_BOTTOM_BAND + SHEET_BURY)
        yl = -D2 + LEAF_CREST
        leaf = _Wall(lambda u, v, yl=yl: _v(v, yl, u), (0, -1, 0), pts)
        leaf.sheet(B["doors"], x0 + LEAF_RING - SHEET_BURY, x1 - LEAF_RING + SHEET_BURY)
        leaf_walls[sx] = (leaf, x0 + LEAF_RING, x1 - LEAF_RING, iz0, iz1)
    _box(B["apertures"], (-0.03, -D2 + SEAM_BACK[0], lz0 + 0.02),
         (0.03, -D2 + SEAM_BACK[1], lz1 - 0.02))

    leaf_w = W2 - LEAF_OUTER - SEAM
    zh = max(lz0 + 0.3, min(lz1 - 0.6, Z0 + HANDLE_Z))
    guide_z = (Z0 + 0.45, Z1 - 0.62)
    bar_x = {}
    for sx in (-1, 1):
        bar_x[sx] = []
        for i, frac in enumerate(BAR_AT):
            xb = sx * (SEAM + frac * leaf_w)
            bar_x[sx].append(xb)
            yb = -D2 + BAR_CENTRE
            z0b, z1b = Z0 + SILL_BOTTOM + 0.05, Z1 - HEADER_TOP - 0.08
            geometry.add_cylinder(B["hardware"], (xb, yb, (z0b + z1b) / 2.0), BAR_R,
                                  z1b - z0b, segments=6, axis="Z")
            for kz0, kz1 in ((Z0 + 0.03, Z0 + 0.12), (Z1 - 0.16, Z1 - 0.06)):
                _box(B["hardware"], (xb - 0.04, -D2 + KEEPER_END, kz0),
                     (xb + 0.04, -D2 + HEADER_END + 0.016, kz1))
            for gz in guide_z:
                _box(B["hardware"], (xb - 0.03, -D2 + GUIDE_END, gz - 0.025),
                     (xb + 0.03, -D2 + LEAF_CREST + 0.029, gz + 0.025))
            # handle: hub on the bar, lever, retainer at its free end. The
            # inner bar's handle points away from the seam and the outer
            # bar's toward it, so the two never meet.
            _box(B["hardware"], (xb - 0.035, -D2 + HUB_END, zh - 0.04),
                 (xb + 0.035, -D2 + LEAF_CREST + 0.029, zh + 0.04))
            direction = sx if i == 0 else -sx
            xe = xb + direction * LEVER_LEN
            _box(B["hardware"], (min(xb, xe), -D2 + LEVER_END, zh - 0.018),
                 (max(xb, xe), -D2 + LEVER_END + 0.020, zh + 0.018))
            xr_ = xe - direction * 0.02
            _box(B["hardware"], (xr_ - 0.028, -D2 + RETAINER_END, zh - 0.035),
                 (xr_ + 0.028, -D2 + LEAF_CREST + 0.029, zh + 0.035))
        # hinges straddle the leaf's hinge edge and the post
        for frac in HINGE_AT:
            hz = lz0 + frac * (lz1 - lz0)
            hx0, hx1 = sorted((sx * (W2 - 0.21), sx * (W2 - 0.14)))
            _box(B["hardware"], (hx0, -D2 + HINGE_END, hz - 0.045),
                 (hx1, -D2 + LEAF_BACK - 0.010, hz + 0.045))

    # --- markings ----------------------------------------------------------------
    code = f"{f['owner']} {f['serial']} {f['check']}"
    leaf, ix0, ix1, iz0, iz1 = leaf_walls[1]
    gap0, gap1 = bar_x[1][0] + 0.03, bar_x[1][1] - 0.03
    th = min(0.085, (gap1 - gap0) / cf.text_width(len(code), 1.0) * 0.96)
    band_top = min(iz1, Z1 - HEADER_TOP - HEADER_H)
    line1 = band_top - 0.06 - th
    # door text: u is height on a leaf, v is x -- glyph x -> v, glyph z -> u
    _door_text(leaf, B["markings"], code, th, (gap0 + gap1) / 2.0, line1, box_last=True)
    _door_text(leaf, B["markings"], f["size_type"], th, (gap0 + gap1) / 2.0,
               line1 - 1.9 * th)

    left, lix0, lix1, liz0, liz1 = leaf_walls[-1]
    lg0, lg1 = bar_x[-1][1] + 0.03, bar_x[-1][0] - 0.03
    rows = (f"GROSS {f['gross']}", f"TARE {f['tare']}")
    wh = min(0.05, (lg1 - lg0) / cf.text_width(max(len(r) for r in rows), 1.0) * 0.96)
    for k, row in enumerate(rows):
        _door_text(left, B["markings"], row, wh, (lg0 + lg1) / 2.0,
                   line1 - k * 1.7 * wh)
    # the warning triangle, outboard of the left leaf's outer bar
    tx = (bar_x[-1][1] + lix0) / 2.0
    tz = line1 - 0.02
    s = min(0.13, abs(bar_x[-1][1] - lix0) * 0.7)
    # (u, v) = (z, x); a black triangle, and the yellow one inset about the
    # centroid on top of it
    tri = [(tz - s * 0.43, tx - s / 2.0), (tz - s * 0.43, tx + s / 2.0), (tz + s * 0.43, tx)]
    left.paint(B["apertures"], tri, DETAIL_PROUD)
    cu = sum(p[0] for p in tri) / 3.0
    cv = sum(p[1] for p in tri) / 3.0
    tri_in = [(cu + (u - cu) * 0.62, cv + (v - cv) * 0.62) for u, v in tri]
    left.paint(B["warning"], tri_in, DETAIL_PROUD + DETAIL_ON_DETAIL)
    # the CSC plate, on the left leaf's crest band between its channels
    pz = iz0 + LEAF_BOTTOM_BAND + (iz1 - iz0 - LEAF_TOP_BAND - LEAF_BOTTOM_BAND) / 8.0 * 4.0
    pxc = (bar_x[-1][0] + bar_x[-1][1]) / 2.0
    pw, ph = 0.20, 0.10
    left.paint(B["plates"], [(pz - ph / 2, pxc - pw / 2), (pz - ph / 2, pxc + pw / 2),
                             (pz + ph / 2, pxc + pw / 2), (pz + ph / 2, pxc - pw / 2)])
    for j in range(3):
        lz = pz + ph / 2 - 0.022 - j * 0.026
        left.paint(B["apertures"], [(lz - 0.006, pxc - pw / 2 + 0.02), (lz - 0.006, pxc + pw / 2 - 0.02 - 0.04 * j),
                                    (lz + 0.006, pxc + pw / 2 - 0.02 - 0.04 * j), (lz + 0.006, pxc - pw / 2 + 0.02)],
                   DETAIL_PROUD + DETAIL_ON_DETAIL)

    # the sides: code near the door end, carrier name down the middle
    side_th = 0.085
    v_top_visible = Z1 - TOP_RAIL_TOP - TOP_RAIL_H
    v_bot_visible = Z0 + BOTTOM_RAIL_BOTTOM + BOTTOM_RAIL_H
    for sx in (-1, 1):
        wall = walls[sx]
        cw = cf.text_width(len(code), side_th)
        uc = -D2 + REAR_POST_D + 0.25 + cw / 2.0
        vc = v_top_visible - 0.10 - side_th / 2.0
        taken[sx].append(_text(wall, B["markings"], code, side_th, uc, vc, sx,
                               box_last=True))
        if f["carrier"]:
            ch = cf.carrier_height(f["carrier"], u_side1 - u_side0, h)
            vcn = (v_top_visible + v_bot_visible) / 2.0 + 0.04
            taken[sx].append(_text(wall, B["markings"], f["carrier"], ch, 0.0, vcn, sx))
        patch = cf.plan_patch((u_side0, u_side1), v_bot_visible, v_top_visible,
                              wear, wear_rng, taken[sx])
        if patch:
            u0, v0, u1, v1 = patch["rect"]
            wall.paint(B["patch"], [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
            taken[sx].append(patch["rect"])
            f["patches"] = f.get("patches", 0) + 1
        streaks = cf.plan_rust(side_pts, v_bot_visible + 0.002, v_top_visible - 0.002,
                               wear, wear_rng, taken[sx])
        for st in streaks:
            # a streak is widest where the water leaves the rail and runs
            # out to a point: `width` of the crest at the rail, `taper` of
            # that at its far end
            u0, v0, u1, v1 = st["rect"]
            um = (u0 + u1) / 2.0
            wide = (u1 - u0) / 2.0 * st["width"]
            thin = wide * st["taper"]
            if st["hang"]:
                poly = [(um - wide, v1), (um - thin, v0), (um + thin, v0), (um + wide, v1)]
            else:
                poly = [(um - wide, v0), (um + wide, v0), (um + thin, v1), (um - thin, v1)]
            wall.paint(B["rust"], poly)
        f.setdefault("rust", []).append(len(streaks))

    # --- objects and materials ----------------------------------------------------
    # the sheets' flanks and valleys become their own meshes on darker paint
    # (container_forms.FORM_SHADE); the crests stay Walls and Doors
    bms["flanks"], bms["valleys"] = geometry.new_bm(), geometry.new_bm()
    for key in ("walls", "doors"):
        crest = geometry.new_bm()
        _sort_by_form(bms[key], {"crest": crest, "flank": bms["flanks"],
                                 "valley": bms["valleys"]})
        bms[key] = crest
    names = {"walls": "CargoContainer_Walls", "frame": "CargoContainer_Frame",
             "doors": "CargoContainer_Doors", "hardware": "CargoContainer_Hardware",
             "flanks": "CargoContainer_RibFlanks", "valleys": "CargoContainer_RibValleys",
             "apertures": "CargoContainer_Apertures",
             "markings": "CargoContainer_Markings", "plates": "CargoContainer_Plates",
             "warning": "CargoContainer_Warning", "rust": "CargoContainer_Rust",
             "patch": "CargoContainer_Patch"}
    kind = plan["material"]
    paint = tuple(f["paint"])

    def hexof(c):
        return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c)

    patch_col = cf.PRIMER if f["patch_primer"] else tuple(c * 0.72 for c in paint)
    flank_col = tuple(c * cf.FORM_SHADE["flank"] for c in paint)
    valley_col = tuple(c * cf.FORM_SHADE["valley"] for c in paint)
    mats = {
        "walls": materials.make_material(f"M_CargoContainer_paint_{hexof(paint)}", list(paint), kind),
        "frame": materials.make_material(f"M_CargoContainer_paint_{hexof(paint)}", list(paint), kind),
        "doors": materials.make_material(f"M_CargoContainer_paint_{hexof(paint)}", list(paint), kind),
        "flanks": materials.make_material(
            f"M_CargoContainer_paint_{hexof(flank_col)}", list(flank_col), kind),
        "valleys": materials.make_material(
            f"M_CargoContainer_paint_{hexof(valley_col)}", list(valley_col), kind),
        "hardware": materials.make_material(f"M_CargoContainer_hw_{hexof(f['hardware'])}",
                                            list(f["hardware"]), kind),
        "apertures": materials.make_material("M_CargoContainer_aperture", list(cf.APERTURE), kind),
        "markings": materials.make_material(f"M_CargoContainer_mark_{hexof(f['mark'])}",
                                            list(f["mark"]), kind),
        "plates": materials.make_material("M_CargoContainer_plate", list(cf.PLATE), kind),
        "warning": materials.make_material("M_CargoContainer_warning", list(cf.WARNING_YELLOW), kind),
        "rust": materials.make_material("M_CargoContainer_rust", list(cf.RUST), kind),
        "patch": materials.make_material(f"M_CargoContainer_patch_{hexof(patch_col)}",
                                         list(patch_col), kind),
    }
    objs = []
    painted = ("walls", "frame", "doors", "hardware", "flanks", "valleys")
    for key, bm in bms.items():
        if not bm.faces:
            bm.free()
            continue
        # every edge hard: a faceted rib and a faceted bar, not a smoothed wave
        geometry.shade_by_angle(bm, 1.0)
        geometry.cube_project_uv(bm, 1.0)
        _wear(bm, wear if key in painted else wear * 0.4, Z0, seed,
              ambient=plan.get("ambient", 0.0))
        obj = geometry.bm_to_object(bm, names[key], collection, finish=False)
        materials.assign([obj], mats[key])
        objs.append(obj)

    print(f"[container] {f['length_class']} {f['size_type']} paint={f['paint_name']} "
          f"code={code} carrier={f['carrier']} pockets={len(f['pockets'])} "
          f"rust={f.get('rust')} patches={f.get('patches', 0)} "
          f"{'primer' if f['patch_primer'] else 'dark'}")

    cboxes = [((-W2, -D2, Z0), (W2, D2, Z1))]
    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)
    return {"objects": objs, "collision_boxes": cboxes,
            "form": {k: v for k, v in f.items() if not isinstance(v, tuple)},
            "attachments": {"ATT_top": (0.0, 0.0, Z1),
                            "ATT_doors": (0.0, -D2, 0.0)}}


def _door_text(leaf, bm, text, height, xc, zc, box_last=False):
    """Text on a door leaf, whose wall is parametrised (u = z, v = x). Glyph
    x runs along +X, which reads left to right from outside the door end."""
    glyphs, (tw, th) = _legend.legend(text, height)
    for verts2d, faces in glyphs:
        for fc in faces:
            leaf.paint(bm, [(zc + verts2d[i][1], xc + verts2d[i][0]) for i in fc])
    if box_last and glyphs:
        xs = [x for x, _z in glyphs[-1][0]]
        pad, t = 0.22 * height, 0.09 * height
        x0, x1 = min(xs) - pad, max(xs) + pad
        z0, z1 = -th / 2.0 - pad, th / 2.0 + pad
        for bx0, bz0, bx1, bz1 in ((x0, z1 - t, x1, z1), (x0, z0, x1, z0 + t),
                                   (x0, z0 + t, x0 + t, z1 - t),
                                   (x1 - t, z0 + t, x1, z1 - t)):
            leaf.paint(bm, [(zc + bz0, xc + bx0), (zc + bz0, xc + bx1),
                            (zc + bz1, xc + bx1), (zc + bz1, xc + bx0)])
