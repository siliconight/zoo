"""sign_post, planned in pure Python: a u-channel post and the blade it carries.

Roadmap 153's street kit left one hole in it. `stop_sign` is a drawn sign;
`sign_post` was the placeholder box `tools/new_species.py` minted on
2026-09-12 -- a 0.10 x 0.10 x 2.40 m pole with nothing on it -- and a pole
with nothing on it is what the walker photographed on cold run 9060 ("no
signs on the stop signs here anymore?"). Lot 0.73.0 answered the half it
owns: every post it stands now NAMES the legend it carries, in the piece's
`blade` field and on the slot as Zoo's dressing `form`. This module draws
the three legends Lot names.

  * ``no_parking``   MUTCD **R8-3a**, the SYMBOLIC No Parking sign: a square
                     white sign with a black border and a black P inside a
                     red circle with a red slash through it (FHWA MUTCD,
                     Figure 2B-17 long description). Lot posts it at a
                     junction corner, where parking is prohibited within
                     30 ft of a signal or stop sign (75 Pa.C.S. 3353; MUTCD
                     R7/R8 series). The symbol version is chosen over R7-1's
                     NO PARKING ANY TIME on purpose: one glyph instead of
                     sixteen, and it is the corner sign that needs no street
                     name on it.
  * ``ped_crossing`` MUTCD **W11-2** Pedestrian warning -- a yellow diamond,
                     black border, black walking figure -- over the
                     **W16-7P** diagonal downward arrow plaque, which the
                     Manual requires below a post-mounted W11-2 placed at the
                     crossing point itself. Black legend and border on
                     retroreflective yellow, both of them.
  * ``bus_stop``     the stop's flag, before the shelter. NOT a MUTCD sign --
                     no part of the Manual governs a transit agency's flag --
                     so it is the one blade here that is a design rather than
                     a standard: a 12 x 18 in vertical flag, BUS over STOP in
                     white on a transit field, spelled from `recipes/_legend`
                     with no glyph added to it.

WHY A PICTOGRAM WHEREVER ONE EXISTS. `recipes/_legend`'s own docstring
records that K M N V W X Y Z are absent because a diagonal stroke does not
fit a three-by-five grid whose only cut is a stroke-square corner -- a
decision, not a gap. Drawing R8-3a instead of R7-1 and W11-2 instead of a
word keeps it a decision: nothing here needs a letter the set does not have,
and BUS STOP is spelled entirely out of the stop sign's own four glyphs plus
the B and U the container stencil added in 0.82.0. The legend set is
unchanged by this release.

SIZES ARE MUTCD INCHES AND THE MODULE'S BOX FALLS OUT OF THEM. A sign's size
and its mounting height are the standard; the slot is what they add up to.
`MODULE_DIMS` is that arithmetic, and Lot's `site_furniture.BLADE_DIMS` is
the same table on the other side of the pipe -- `tests/test_sign_post.py`
pins these numbers and Lot's `tests/test_site_furniture.py` pins those,
because neither repo can import the other.

  * mounting: MUTCD Section 2A.18 -- 7 ft to the bottom of the major sign in
    a business, commercial or residential area where parking or pedestrian
    movements occur, 5 ft to the bottom of a secondary plaque under it.
  * R8-3a at 12 x 12 in, W11-2 at 30 x 30 in (the conventional-road size),
    W16-7P at 24 x 12 in.
  * A 30 x 30 in diamond is a 30 in SQUARE stood on its point, so the box it
    needs is 30 * sqrt(2) = 42.43 in across. That is why `ped_crossing` is
    1.078 m wide and 3.211 m tall where `no_parking` is 0.305 by 2.438: a
    pedestrian crossing sign really is a third again as tall as a parking
    sign and three and a half times as wide, and a street where they came
    out the same size is a street nobody looked at.

THE POST IS THE ONLY COLLIDER, exactly as `stop_sign.py` has it: a body
walks into a pole, never into a sign face two metres over its head.

THE RULES the interior species keep (`core/carton_forms.py`, 0.94.0/0.95.0):
extents exactly w x d x h with the base at z = 0, no two faces within 2 mm of
one plane where they overlap, colliders inside the bounds, deterministic.
`tests/test_sign_post.py` holds every form at every genome corner.

TWO THINGS THAT LOOK LIKE STYLE AND ARE NOT.

1. THE Y STACK IS A LADDER AND EVERY RUNG IS LOAD-BEARING. Eleven parallel
   planes stack up behind a sign face -- slash, symbol, coloured face, blade,
   web, flanges, front and back of each -- and every one of them overlaps
   every other in projection, so the 2 mm rule applies to all fifty-five
   pairs at once and not to neighbours. `_Y` lays them on a 4 mm grid in
   front of the post and a 3 mm grid through it; the closest pair in the
   built module is 3.0 mm and a test asserts it. Moving one offset on its
   own is how that gets broken.
2. A MULTI-CELL SHAPE IS ONE SOLID, NOT A PILE OF THEM. A ring built as
   sixteen closed quads has sixteen pairs of internal walls sitting on one
   plane facing each other at nil separation, and so does a glyph built cell
   by cell -- the coincident-face probe reports every one of them. `_solid`
   is `stop_sign._glyph_solid`'s rule generalised: shared vertices, faces
   front and back, and a wall ONLY on an edge no neighbouring cell walks the
   other way. Every cell complex here is authored to share its vertices
   exactly so that rule can find them.

Frame: metres, Z up, base-up, x centred, -Y the face -- the direction
`lot.site_furniture.plate_facing` reads and `_facing_driver` turns.
"""
from __future__ import annotations

import math

from . import prims as P

IN = 0.0254

FORMS = ("no_parking", "ped_crossing", "bus_stop")

#: MUTCD Section 2A.18 mounting heights, inches: the bottom of the major
#: sign, and the bottom of a secondary plaque mounted under it.
MOUNT_MAJOR_IN = 84.0
MOUNT_MINOR_IN = 60.0

#: MUTCD sign sizes, inches. A diamond's size is the SIDE of the square it
#: is, not the width of the box it needs.
R8_3A_IN = 12.0
W11_2_SIDE_IN = 30.0
W16_7P_IN = (24.0, 12.0)
#: Not MUTCD: a transit flag, at the size an American stop flag is made.
BUS_FLAG_IN = (12.0, 18.0)

#: A 3 lb/ft u-channel sign post: 2.5 in across the web.
POST_W = 2.5 * IN
#: The module depth every blade form asks for. The ladder below needs 36 mm
#: in front of the flanges' back; 60 mm leaves the channel 33 mm deep, which
#: is the section.
MODULE_D = 0.060

#: The y ladder, as offsets BACK from the module's front face (-d/2). See
#: the module docstring: these are not eleven independent choices.
_Y = {
    "slash_front": 0.000,
    "symbol_front": 0.004,
    "face_front": 0.008,
    "blade_front": 0.012,
    "face_back": 0.016,
    "symbol_back": 0.020,
    "slash_back": 0.024,
    "web_front": 0.027,
    "blade_back": 0.030,
    "flange_front": 0.033,
    "web_back": 0.036,
}
#: How far a flange stands in from the web's own faces, so the two never
#: share an x plane over the three millimetres they overlap in y, nor a z
#: plane at the post's foot and head.
FLANGE_INSET = 0.003
FLANGE_T = 0.008
FLANGE_END = 0.004


def post_bevel(style_bevel):
    """The bevel the post may actually take, given how thin a flange is.

    MEASURED ON THE BUILT GLB, not reasoned about. Every `sign_post` style
    carries bevel 0.006, and a 6 mm bevel on an 8 mm flange eats most of the
    flange: of the post's 132 triangles, 32 came out ZERO-AREA on the
    no-parking module and 28 on the other two -- a quarter of the post,
    shipped to every client, drawing nothing. They do not show in
    `prims.tri_count`, which counts the plan and not the bevel, and they do
    not show in `build_module`'s own tally either; `tools/coplanar_probe.py`
    skips a triangle whose normal is degenerate, so the gap between its
    count and the GLB's was the only place they were visible at all.

    A quarter of the thinnest section is the most a bevel can take off it
    and still leave a corner: 2 mm here, which on a 63.5 mm web is the same
    softened edge it was and on the flange is a chamfer rather than a
    collapse.
    """
    return min(float(style_bevel or 0.0), FLANGE_T * 0.25)

#: material key -> (linear RGB, kind). The post takes the genome's colour and
#: kind; every sign colour is a constant of the STANDARD rather than a style
#: choice, the way the dartboard's chrome and the hydrant's chains are
#: (`tests/test_material_options_closed.py` keeps `sign_post` in BARE).
MATERIALS = {
    "white": ([0.86, 0.86, 0.84], "metal_painted"),
    "black": ([0.04, 0.04, 0.045], "metal_painted"),
    # the same red as stop_sign's face: one street, one highway red
    "red": ([0.62, 0.07, 0.09], "metal_painted"),
    # MUTCD highway yellow, held back from full chroma the way every other
    # painted colour in this repo is
    "yellow": ([0.90, 0.58, 0.02], "metal_painted"),
    # a transit flag's field: a deep blue nobody's brand owns
    "transit": ([0.05, 0.12, 0.30], "metal_painted"),
}

#: The slot each form asks for: (width, depth, height) in metres, derived
#: from the inches above and pinned by a test. Lot writes these; nothing
#: here chooses them.
MODULE_DIMS = {
    "no_parking": (R8_3A_IN * IN, MODULE_D,
                   (MOUNT_MAJOR_IN + R8_3A_IN) * IN),
    "ped_crossing": (W11_2_SIDE_IN * math.sqrt(2.0) * IN, MODULE_D,
                     (MOUNT_MAJOR_IN + W11_2_SIDE_IN * math.sqrt(2.0)) * IN),
    "bus_stop": (BUS_FLAG_IN[0] * IN, MODULE_D,
                 (MOUNT_MAJOR_IN + BUS_FLAG_IN[1]) * IN),
}

#: Blade border width, as a fraction of the sign's short side, and the floor
#: under it -- see `border_of`, where both are argued.
BORDER_FRAC = 0.055
#: `prims.coincident_pairs`' own default, and `tools/coplanar_probe.py`'s:
#: the separation two overlapping faces have to keep. Named here because the
#: border width is derived from it rather than chosen against it.
COPLANAR_TOL = 0.002
#: The prohibition ring, as fractions of the R8-3a sign's side.
RING_R = 0.385
RING_T = 0.085
RING_SEGMENTS = 16
#: The P inside the ring, as a fraction of the sign's side. It has to clear
#: the ring's inner radius: at 0.44 the glyph's far corner is 0.255 of the
#: side from the centre against an inner radius of 0.300.
P_HEIGHT = 0.44
#: The pedestrian figure's height, as a fraction of the W11-2 square's side.
FIGURE_H = 0.58
#: The bus flag's legend height, as a fraction of the flag's width.
FLAG_LEGEND_H = 0.26

_KEY = 1e-7


def min_width(form):
    """The narrowest module this form can be drawn in and still keep every
    overlapping pair of faces off the coplanar tolerance.

    The species' genome spans a BARE POLE at 0.09 m and a 30 in diamond at
    1.08 m, so "the genome's minimum width" is not a size every form can be
    -- which is what a species whose forms are different SIGNS means. This
    is the per-form floor, derived rather than chosen, and every dim Lot
    writes clears it by a factor of three.

    Only the lettered flag binds: `_legend` sets a word's inter-glyph gap at
    `GAP` (0.08) of the legend height, the legend is `FLAG_LEGEND_H` (0.26)
    of the flag's width, so the gap between two letters is 0.0208 w and
    falls to the 2 mm tolerance at w = 0.0962 m. The other two blades carry a
    pictogram or a single glyph and have no such gap; their floor is the
    border, which `border_of` holds above the tolerance at any size.
    """
    from ..recipes import _legend
    if form != "bus_stop":
        return 0.0
    # ROUNDED UP TO THE MILLIMETRE, because `coincident_pairs` flags a pair
    # whose planes differ by AT MOST the tolerance: at the exact solution the
    # gap IS 2.000 mm and the row still prints.
    return math.ceil(1000.0 * COPLANAR_TOL
                     / (_legend.GAP * FLAG_LEGEND_H)) / 1000.0


def pick_form(form):
    """The blade to build, or None for the bare post.

    ``auto`` HERE MEANS NO BLADE, and that is a narrower thing than it means
    anywhere else. For `furnace` and `booth_seat` auto reads the footprint or
    the height and PICKS, because a water heater is a different shape from a
    furnace. A legend is not a shape: the dims in `MODULE_DIMS` identify the
    form only because this module derived them FROM the legends in the first
    place, so an auto that read them back would be reading its own arithmetic
    and calling it evidence. Lot names the blade because Lot is what knows
    what the post is for; asked nothing, this draws the bare pole.

    IT MUST STILL BE FIRST IN THE GENOME'S LIST, and that is not decoration.
    `dna._default_params` takes ``spec[0]`` as a list param's canonical
    default, so an undressed module gets whatever is listed first -- with the
    blades alone in the list, every plain `sign_post` in the library built a
    No Parking sign. Caught in the frame, not by the suite, because the suite
    was calling `plan` directly; `test_an_undressed_post_is_still_a_bare_pole`
    goes through `dna` for that reason.
    """
    return form if form in FORMS else None


# --- flat cell complexes ------------------------------------------------------


def _ccw(poly):
    """``poly`` wound counter-clockwise seen from the FRONT (x right, z up).

    That winding puts the authored order's normal on -Y by the right-hand
    rule -- the same convention `stop_sign._glyph_solid` documents. Applying
    it to every cell is also what makes `_solid`'s shared-edge rule work:
    two adjacent cells both wound CCW always walk their shared edge in
    opposite directions.
    """
    area = 0.0
    n = len(poly)
    for k in range(n):
        x0, z0 = poly[k]
        x1, z1 = poly[(k + 1) % n]
        area += x0 * z1 - x1 * z0
    return list(poly) if area >= 0.0 else list(reversed(poly))


def _solid(part, mat, polys, y0, y1):
    """One closed solid from flat cells, extruded from ``y0`` to ``y1``.

    Cells share vertices by coordinate, and a wall is built only on an edge
    no neighbouring cell walks the other way -- so the inside of a ring or a
    glyph has no faces in it at all. See the module docstring's second note
    for why that is not an optimisation.
    """
    index, pts = {}, []

    def vid(p):
        key = (round(p[0] / _KEY), round(p[1] / _KEY))
        if key not in index:
            index[key] = len(pts)
            pts.append(p)
        return index[key]

    cells = [[vid(p) for p in _ccw(poly)] for poly in polys]
    n = len(pts)
    verts = [(x, y0, z) for x, z in pts] + [(x, y1, z) for x, z in pts]
    faces = []
    edges = set()
    for cell in cells:
        faces.append(tuple(cell))
        faces.append(tuple(i + n for i in reversed(cell)))
        for k in range(len(cell)):
            edges.add((cell[k], cell[(k + 1) % len(cell)]))
    for a, b in edges:
        if (b, a) not in edges:
            faces.append((b, a, a + n, b + n))
    return P.mesh(part, mat, verts, faces, False)


def _rect(cx, cz, sx, sz):
    return [(cx - sx / 2.0, cz - sz / 2.0), (cx + sx / 2.0, cz - sz / 2.0),
            (cx + sx / 2.0, cz + sz / 2.0), (cx - sx / 2.0, cz + sz / 2.0)]


def _diamond(cx, cz, across):
    """A square on its point, ``across`` from point to point."""
    r = across / 2.0
    return [(cx, cz - r), (cx + r, cz), (cx, cz + r), (cx - r, cz)]


def _disc(cx, cz, r, segments):
    return [(cx + r * math.cos(2.0 * math.pi * k / segments),
             cz + r * math.sin(2.0 * math.pi * k / segments))
            for k in range(segments)]


def border_of(short_side):
    """The blade's border width for a sign whose short side is
    ``short_side``.

    MUTCD borders run about a sixteenth of the side on a small regulatory
    sign (3/8 in on 12 in); `BORDER_FRAC` is a little heavier so the border
    still reads at the distance a player meets a street sign from. The FLOOR
    is not taste: the border is the perpendicular gap between the blade's rim
    wall and the coloured field's, so a border under the coplanar probe's
    2 mm puts two walls on one plane. Measured at the genome's 0.09 m corner
    before the floor existed: the W16-7P plaque's field stood 1.11 mm inside
    its blade and the probe reported the pair.
    """
    return max(2.0 * COPLANAR_TOL, short_side * BORDER_FRAC)


def _rect_inset(cx, cz, sx, sz, border):
    """A rectangle inside `_rect(cx, cz, sx, sz)` with ``border`` of blade
    showing on all four sides.

    PER AXIS, not by scaling toward the centroid: a uniform scale leaves a
    non-square rectangle with two different borders -- 2.0 mm across and
    1.0 mm up on the plaque, which is the pair the probe found.
    """
    return _rect(cx, cz, sx - 2.0 * border, sz - 2.0 * border)


def _diamond_inset(cx, cz, across, border):
    """A diamond inside `_diamond(cx, cz, across)` with ``border`` of blade
    showing perpendicular to each of its four edges. A diamond IS equidistant
    from its centre on every edge, so here a scale is the offset -- and the
    apothem is ``across / (2 * sqrt(2))``, which is where the factor comes
    from."""
    return _diamond(cx, cz, across - 2.0 * math.sqrt(2.0) * border)


def _lerp(a, b, t):
    """The point ``t`` of the way from ``a`` to ``b``.

    Splitting an edge so a neighbouring cell can share it has to land ON the
    edge. Typing the split point out to four places puts it a hundredth of a
    millimetre off, which makes the cell concave -- and a concave cell is
    fanned from its first vertex by `prims.triangles`, which turns one face
    into a triangle wound the other way and reports itself as a coincident
    pair at nil separation. Measured on the pedestrian figure's hip and
    shoulder: two cross products of -1e-05, one 2.3 mm^2 row.
    """
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _bar(cx, cz, length, width, angle):
    """A ``length`` by ``width`` rectangle centred on (cx, cz), turned
    ``angle`` radians counter-clockwise."""
    c, s = math.cos(angle), math.sin(angle)
    return [(cx + c * dx - s * dz, cz + s * dx + c * dz)
            for dx, dz in ((-length / 2.0, -width / 2.0),
                           (length / 2.0, -width / 2.0),
                           (length / 2.0, width / 2.0),
                           (-length / 2.0, width / 2.0))]


def _ring(cx, cz, r_out, r_in, segments):
    """An annulus as ``segments`` quads that share their radial edges."""
    out = []
    for k in range(segments):
        a0 = 2.0 * math.pi * k / segments
        a1 = 2.0 * math.pi * (k + 1) / segments
        out.append([(cx + r_in * math.cos(a0), cz + r_in * math.sin(a0)),
                    (cx + r_in * math.cos(a1), cz + r_in * math.sin(a1)),
                    (cx + r_out * math.cos(a1), cz + r_out * math.sin(a1)),
                    (cx + r_out * math.cos(a0), cz + r_out * math.sin(a0))])
    return out


def _glyph_polys(text, height, cx, cz):
    """`recipes/_legend`'s word as flat cells in (x, z), centred on
    ``(cx, cz)``. Imported here rather than at module scope so `core` keeps
    its one-way dependency on `recipes`; `_legend` itself is pure Python."""
    from ..recipes import _legend
    glyphs, _size = _legend.legend(text, height)
    out = []
    for verts2d, faces in glyphs:
        for f in faces:
            out.append([(cx + verts2d[i][0], cz + verts2d[i][1]) for i in f])
    return out


# --- the post -----------------------------------------------------------------


def _base(d, has_slash):
    """Where the y ladder starts, so that its FRONTMOST rung lands exactly on
    the module's front face and `fit_exact` has nothing to take back.

    Only `no_parking` has a slash; on the other two the symbol is the
    frontmost thing, and starting the ladder at ``-d/2`` would leave the
    plan 4 mm shy of the slot and let the fit stretch every gap in it by
    7 %. The rungs' spacing is what matters, not where the ladder is nailed.
    """
    return -d / 2.0 - (0.0 if has_slash else _Y["symbol_front"])


def _post(prims, boxes, w, d, z_top, base):
    """The u-channel, base to ``z_top``, and the only collision box.

    With a blade (``base`` given) the section is the real 3 lb/ft channel and
    the module's width belongs to the sign; WITHOUT one the module IS the
    post, so the web takes the slot's whole width and depth rather than
    being squeezed into them by `fit_exact`. That bare pole is what a slot
    with no form still resolves to, and it is the only shape this species
    had until now.
    """
    y0 = -d / 2.0
    if base is not None:
        web_w = POST_W
        y_web = (base + _Y["web_front"], base + _Y["web_back"])
        y_flange = (base + _Y["flange_front"], d / 2.0)
        flange_t = FLANGE_T
    else:
        web_w = w
        web_t = max(0.006, d * 0.10)
        y_web = (y0, y0 + web_t)
        y_flange = (y_web[1] - 0.003, d / 2.0)
        flange_t = min(0.008, w * 0.12)
    prims.append(P.box("SignPost_Post", "post",
                       (-web_w / 2.0, y_web[0], 0.0),
                       (web_w / 2.0, y_web[1], z_top), bevel=True))
    x_out = web_w / 2.0 - FLANGE_INSET
    for sgn in (-1.0, 1.0):
        xs = sorted((sgn * x_out, sgn * (x_out - flange_t)))
        prims.append(P.box("SignPost_Post", "post",
                           (xs[0], y_flange[0], FLANGE_END),
                           (xs[1], y_flange[1], z_top - FLANGE_END),
                           bevel=True))
    boxes.append(((-web_w / 2.0, y_web[0], 0.0),
                  (web_w / 2.0, d / 2.0, z_top)))


# --- the blades ---------------------------------------------------------------


def _blade(prims, base, outline, face_outline, face_mat, border_mat="black",
           part="SignPost_Blade"):
    """The blade and the coloured field standing proud of it, the way
    `stop_sign` stands its red octagon proud of its white border. A blade's
    own edge is its border colour: MUTCD borders are painted ON the blank,
    and a rim around the field is the same two solids either way."""
    prims.append(_solid(part, border_mat, [outline],
                        base + _Y["blade_front"], base + _Y["blade_back"]))
    prims.append(_solid(part + "_Face", face_mat, [face_outline],
                        base + _Y["face_front"], base + _Y["face_back"]))


def _no_parking(w, d, h):
    """MUTCD R8-3a: a square white sign, black border, black P inside a red
    circle with a red slash through it."""
    prims, boxes = [], []
    side = w
    cz = h - side / 2.0
    base = _base(d, True)
    border = border_of(side)
    _blade(prims, base, _rect(0.0, cz, side, side),
           _rect_inset(0.0, cz, side, side, border), "white")
    prims.append(_solid("SignPost_Symbol", "red",
                        _ring(0.0, cz, side * RING_R,
                              side * (RING_R - RING_T), RING_SEGMENTS),
                        base + _Y["symbol_front"], base + _Y["symbol_back"]))
    prims.append(_solid("SignPost_Legend", "black",
                        _glyph_polys("P", side * P_HEIGHT, 0.0, cz),
                        base + _Y["symbol_front"], base + _Y["symbol_back"]))
    # the slash runs upper-left to lower-right across the whole circle and
    # rides its own rung, because it crosses both the ring and the P
    prims.append(_solid("SignPost_Symbol_Slash", "red",
                        [_bar(0.0, cz, side * RING_R * 2.0, side * RING_T,
                              -math.pi / 4.0)],
                        base + _Y["slash_front"], base + _Y["slash_back"]))
    _post(prims, boxes, w, d, h - side * 0.06, base)
    return prims, boxes, {"blade": "R8-3a", "sign_m": round(side, 4),
                         "face_z": cz}


def _pedestrian(cx, cz, height):
    """The W11-2 walking figure: a detached head over a torso with one swung
    arm and two striding legs.

    The MUTCD symbol's head IS detached, which is convenient, and the rest
    is ONE cell complex over a shared vertex table -- the torso carries the
    two hip vertices the legs hang off and the two shoulder vertices the arm
    does, so every internal edge is walked both ways and `_solid` builds no
    wall inside the figure. Coordinates are fractions of the figure's
    height about its own centre; the stride and the swung arm are what make
    it read as a person walking rather than as a blob, and at the size a
    driver sees it the silhouette is the whole sign.
    """
    u = height

    def at(x, z):
        return (cx + x * u, cz + z * u)

    head = _disc(cx + 0.015 * u, cz + 0.415 * u, 0.088 * u, 8)
    # the torso, with the hip split for the legs and the back edge split for
    # the arm: [hip back, hip mid, hip front, shoulder front, shoulder back,
    #           arm top, arm bottom]. Both splits are INTERPOLATED, not
    #           typed -- see `_lerp`.
    t_hip_b, t_hip_f = at(-0.085, -0.010), at(0.090, -0.030)
    t_sh_f, t_sh_b = at(0.120, 0.270), at(-0.075, 0.300)
    t_hip_m = _lerp(t_hip_b, t_hip_f, 0.5)
    a_top, a_bot = _lerp(t_sh_b, t_hip_b, 0.274), _lerp(t_sh_b, t_hip_b, 0.597)
    torso = [t_hip_b, t_hip_m, t_hip_f, t_sh_f, t_sh_b, a_top, a_bot]
    lead_leg = [at(0.130, -0.415), at(0.215, -0.395), t_hip_f, t_hip_m]
    trail_leg = [at(-0.235, -0.430), at(-0.150, -0.440), t_hip_m, t_hip_b]
    arm = [a_bot, a_top, at(-0.232, 0.062), at(-0.248, -0.036)]
    return [head, torso, lead_leg, trail_leg, arm]


def _arrow(cx, cz, length, width, angle):
    """A shaft and a head, sharing the shaft's end edge.

    The head is authored as a FIVE-sided cell -- tip, two base corners and
    the two shaft corners between them -- so the shaft's far edge is an edge
    of the head as well and `_solid` takes the wall between them out. A
    three-sided head with a wider base would not share that edge, and an
    arrow drawn as one concave outline would be fanned wrong by
    `prims.triangles`.
    """
    c, s = math.cos(angle), math.sin(angle)

    def at(u, v):
        return (cx + c * u - s * v, cz + s * u + c * v)

    tip = length / 2.0
    base = tip - length * 0.42
    hw = width * 1.55
    shaft = [at(-tip, -width / 2.0), at(base, -width / 2.0),
             at(base, width / 2.0), at(-tip, width / 2.0)]
    head = [at(tip, 0.0), at(base, -hw), at(base, -width / 2.0),
            at(base, width / 2.0), at(base, hw)]
    return [shaft, head]


def _ped_crossing(w, d, h):
    """MUTCD W11-2 over W16-7P: a yellow diamond with the walking figure, and
    the diagonal arrow plaque the Manual requires under a post-mounted one at
    the crossing."""
    prims, boxes = [], []
    across = w                       # point to point
    side = across / math.sqrt(2.0)   # the square the diamond is
    cz = h - across / 2.0
    base = _base(d, False)
    outline = _diamond(0.0, cz, across)
    _blade(prims, base, outline,
           _diamond_inset(0.0, cz, across, border_of(side)), "yellow")
    prims.append(_solid("SignPost_Symbol", "black",
                        _pedestrian(0.0, cz, side * FIGURE_H),
                        base + _Y["symbol_front"], base + _Y["symbol_back"]))

    # the plaque: 24 x 12 in under a 30 in sign, its bottom at 5 ft where the
    # sign's is at 7 ft -- all four numbers in proportion to the side
    pw = side * (W16_7P_IN[0] / W11_2_SIDE_IN)
    ph = side * (W16_7P_IN[1] / W11_2_SIDE_IN)
    gap = side * ((MOUNT_MAJOR_IN - MOUNT_MINOR_IN - W16_7P_IN[1])
                  / W11_2_SIDE_IN)
    pcz = cz - across / 2.0 - gap - ph / 2.0
    plaque = _rect(0.0, pcz, pw, ph)
    _blade(prims, base, plaque,
           _rect_inset(0.0, pcz, pw, ph, border_of(ph)), "yellow",
           part="SignPost_Plaque")
    # THE ARROW POINTS DOWN AND TO THE DRIVER'S LEFT, and that is a choice
    # this module is making rather than reading: MUTCD's plaque comes in a
    # left and a right, and Lot's `BLADE_AT_PATH` says only that the post
    # stands at a footpath cut. Down-left aims it at the carriageway the
    # crossing runs across, which is where the sign is for. When Lot passes
    # the side, this takes it.
    prims.append(_solid("SignPost_Plaque_Arrow", "black",
                        _arrow(0.0, pcz, ph * 0.74, ph * 0.15,
                               math.radians(225.0)),
                        base + _Y["symbol_front"], base + _Y["symbol_back"]))
    # THE POST STOPS AT OR BELOW THE DIAMOND'S WIDEST POINT, so it never
    # shows beside the upper point. `max(0, ...)` is not defensive: on a
    # diamond narrower than four channel widths the subtraction alone put
    # the post's top face 1.28 mm from the plaque's, which the probe
    # reported at the genome's 0.1 m corner.
    _post(prims, boxes, w, d,
          cz + max(0.0, across / 2.0 - 2.0 * POST_W), base)
    return prims, boxes, {"blade": "W11-2 + W16-7P", "sign_m": round(side, 4),
                         "face_z": cz}


def _bus_stop(w, d, h):
    """The stop's flag: a vertical rectangle, BUS over STOP in white on a
    transit field, in a white border. Not a MUTCD sign."""
    prims, boxes = [], []
    fw = w
    fh = w * (BUS_FLAG_IN[1] / BUS_FLAG_IN[0])
    cz = h - fh / 2.0
    base = _base(d, False)
    border = border_of(fw)
    outline = _rect(0.0, cz, fw, fh)
    _blade(prims, base, outline, _rect_inset(0.0, cz, fw, fh, border),
           "transit", border_mat="white")
    lh = fw * FLAG_LEGEND_H
    polys = _glyph_polys("BUS", lh, 0.0, cz + fh * 0.185)
    polys += _glyph_polys("STOP", lh, 0.0, cz - fh * 0.185)
    prims.append(_solid("SignPost_Legend", "white", polys,
                        base + _Y["symbol_front"], base + _Y["symbol_back"]))
    _post(prims, boxes, w, d, h - fh * 0.05, base)
    return prims, boxes, {"blade": "transit flag", "sign_m": round(fw, 4),
                         "face_z": cz}


def _bare(w, d, h):
    """No blade: the u-channel alone, at the slot's own section."""
    prims, boxes = [], []
    _post(prims, boxes, w, d, h, None)
    return prims, boxes, {"blade": "none", "sign_m": 0.0, "face_z": h / 2.0}


_BUILDERS = {"no_parking": _no_parking, "ped_crossing": _ped_crossing,
             "bus_stop": _bus_stop}


def plan(w, d, h, form=None):
    """The post and the blade it carries, laid out to the slot and fitted to
    it exactly.

    Returns ``{prims, collision, form, overshoot_m, facts}``; ``form`` is the
    blade built, or None for the bare pole.
    """
    built = pick_form(form)
    prims, boxes, facts = _BUILDERS.get(built, _bare)(w, d, h)
    lo, hi = P.bounds(prims)
    overshoot = max(abs(lo[0] + w / 2.0), abs(hi[0] - w / 2.0),
                    abs(lo[1] + d / 2.0), abs(hi[1] - d / 2.0),
                    abs(lo[2]), abs(hi[2] - h))
    prims, boxes = P.fit_exact(prims, (-w / 2.0, -d / 2.0, 0.0),
                               (w / 2.0, d / 2.0, h), boxes)
    facts["tris"] = P.tri_count(prims)
    return {"prims": prims, "collision": boxes, "form": built,
            "overshoot_m": round(overshoot, 6), "facts": facts}
