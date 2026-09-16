"""The four flat-art species, planned in pure Python (no bpy).

Zoo 0.98.0: `poster`, `hanging_banner`, `ceiling_hanger` and `aisle_sign`.
The reference is `docs/SET_DRESSING_REFERENCES.md`, "The card shop is not
dense enough, and what dense means (2026-09-16)", properties 3 and 4 --
things hang, and the wall above the shelving is where the posters live. The
art itself is `core/flat_art.py`; this file is the geometry it is stretched
over, and the two are separate for the reason `card_art` and
`pack_wall_forms` are: one is pixels and one is metres.

FRAME AND UNITS: metres, Z up, the slot's box, -Y the aisle (the side a
shopper stands on), +Y the wall, base at z = 0, plan centred on x = y = 0.
Every plan fills its slot box EXACTLY -- `validate.fit_*` gates a slot-fit
module on its built bounds equalling the slot to 2 cm and `core.pivot`
re-centres from them.

THE WHOLE SPECIES SET IS TWO TRIANGLES AND A TEXTURE, and that is the
argument for building it at all. The walker asked for density and the
standing rule is performance over look; flat art is the one kind of density
that is nearly free in geometry. The measured figures are in the 0.98.0
release note; the short version is that a saturated room's worth of this
set is under 1,500 triangles against the 10,664 the shipped card shop
measured, and one `cubicle_bank` is budgeted 24,000.

WHERE THE COST ACTUALLY IS, and it is not here: the atlas. Every quad in
one module names a tile in ONE image (`recipes/_card_atlas.py`), so a
module is ONE extra draw call however many quads it carries, and the atlas
is named by a digest of its own pixels, so two posters whose art is
identical share one image in the .blend and one in the GLB. Per-quad
materials would be the alternative and would cost a draw each; the numbers
for both are in the release note, measured rather than asserted.

NO TWO FACES WITHIN 2 mm OF A PLANE, and the ladders below are how. Every
depth here is a FRACTION OF THE SLOT'S DEPTH rather than an absolute, which
is the one decision in this file worth arguing with. An absolute ladder is
what a real frame has -- a 3 mm mat is 3 mm whatever it is hung in -- but
the plan must fill the slot's depth exactly, so an absolute ladder gets
squeezed by `fit_exact` and the separations move with it. Fractions scale
instead: the worst case is the genome's MINIMUM depth, it is checked there
once (`min_rung_m`), and a deeper slot simply builds a chunkier frame.

WHAT HANGS FROM, WHICH NOTHING IN THIS PIPELINE HAD DONE. See `HANG_NOTE`.
"""
from __future__ import annotations

import math

from . import card_brands as CB
from . import prims as P
from .brands import srgb_to_linear

# --- the shared discipline ---------------------------------------------------

#: `tools/coplanar_probe.py` measures a BUILT scene at 2 mm and floats land
#: on the number, so the pure plans are held to a tenth more -- the same
#: 2.2 mm `tests/test_card_shop.py` uses and for the same reason.
TOL = 0.0022
#: How far a part is buried inside whatever it lands in, and how far an art
#: quad stands proud of the plate behind it. `pack_wall_forms`' numbers.
JOIN = 0.004
ART_PROUD = 0.005

#: mat keys. The recipes map these to materials; a key is not a colour.
FRAME = "frame"
BOARD = "board"
CLOTH = "cloth"
CHAIN = "chain"
ART = "art"

#: WHAT A HANGING THING HANGS FROM -- the question the brief asked to be
#: answered rather than assumed, and the answer is that the hanging point
#: already exists and is NOT geometry.
#:
#: Three candidates were checked, in this order:
#:
#:  1. THE CEILING GRID'S OWN GEOMETRY. There is none to hang from. A
#:     dropped ceiling in this pipeline is a `ceiling` slot built by
#:     `recipes/ceiling.py` -> `_arch.build_slab`, which emits ONE solid
#:     `Ceiling_Panel`, and the grid is a Pixelcoat skin on its underside
#:     (`ceiling_tile` in `skins.KNOWN_KINDS`). There are no T-bars, no
#:     runners and no tile edges in the mesh, so there is nothing a chain
#:     could be attached to and nothing to align a hanger's pitch against.
#:  2. A DELI COUNTER LIGHT ANCHOR. `core/fixtures.py` has exactly the
#:     mechanism -- `mount: "hang"` puts a body's TOP at the anchor and
#:     leaves it below, added in 0.94.0 after a club can was built inside
#:     the slab -- but it is the LIGHT pipeline: its input is a
#:     `<building>.lights.json` and every row in `FIXTURES` is a lamp.
#:     A painted dragon is not a lamp and putting one on that manifest
#:     would make Lux spawn a Light3D at it.
#:  3. A DELI COUNTER PROP SLOT, HUNG. This is the one, and it already
#:     ships. `level_design._piece`'s `under` field is the gap between a
#:     piece's TOP and the ceiling PLANE, and `_piece_lift` turns it into
#:     the centre height: `_clear_height(spec) - under - h/2`. Zoo's
#:     `pennant_row` has hung from it since 0.95.0 and Deli Counter's own
#:     test says why it is `under` and not a fixed lift -- "a fixed 2.95
#:     would have been right at the card shop's 3.4 m storey and 0.6 m
#:     inside the slab at the strip club's 3.6 m one".
#:
#: So the Zoo-side rule is the one written into the three hanging species
#: here: THE TOP OF THE SLOT BOX IS THE CEILING PLANE. A hanger's chain
#: starts at z = h and the painted plate hangs below it, which is the
#: mirror of `fixtures`' `hang` mount and needs nothing new downstream --
#: Deli Counter adds one `_piece(..., under=_CEILING_AIR)` row per species
#: and the piece arrives at the right height at every storey height.
HANG_NOTE = "the top of the slot box is the ceiling plane; see the docstring"

#: `deli_counter/agent_contract.json` clearances.min_headroom_m, read
#: 2026-09-16. Copied and cited the way `vault_forms.MIN_HEADROOM` and
#: `cubicle_bank`'s `aisle_min` are, because Zoo has no reader for that file.
MIN_HEADROOM = 2.0
#: The shortest storey the library places into, and the slab cap and air gap
#: `level_design._clear_height` subtracts from it. `_CEILING_AIR` is spent
#: TWICE -- once inside `_clear_height` and again as the piece's own `under`
#: -- and both are here because both are between the storey and the top of
#: a hung piece.
SHORT_STOREY = 3.0
SLAB_CAP = 0.3
CEILING_AIR = 0.05


def hang_max_height(story=SHORT_STOREY, cap=SLAB_CAP, air=CEILING_AIR,
                    headroom=MIN_HEADROOM):
    """The tallest a piece hung under the ceiling may be before its BOTTOM
    comes below a body's headroom.

    DERIVED, NOT CHOSEN, and this is the number the two hanging genomes'
    `height.max` is. `level_design._clear_height` is the storey less the
    thicker slab less `_CEILING_AIR`; the piece's own `under` spends that
    air again; what is left above `headroom` is the drop. At the library's
    shortest storey that is 3.0 - 0.3 - 0.05 - 0.05 - 2.0 = 0.60 m.

    A THICKER SLAB MAKES IT SMALLER and Zoo cannot see the slab, so this is
    a genome cap and not a guarantee: the placement is Deli Counter's and
    `_piece_lift` is where a storey with a 0.5 m cap would have to be
    refused. Said here rather than left implicit, because a cap that looks
    like a guarantee is worse than one that does not.
    """
    return round(float(story) - float(cap) - 2.0 * float(air)
                 - float(headroom), 4)


def min_rung_m(planes):
    """The closest two of a set of parallel plane offsets, in metres. The
    measurement `tests/test_coincident_faces.py` makes on `stop_sign`'s
    ladder, in the units this file authors in."""
    ys = sorted(planes.values())
    return min((b - a) for a, b in zip(ys, ys[1:]))


def _quad(part, tile, verts, flip=False):
    """One art quad naming a tile. `_card_atlas.build_art` reads `tile`,
    `verts`, `faces` and `uvs`; `flip` mirrors U for the back face of a
    double-sided sign, so both sides read the right way round."""
    p = P.mesh(part, ART, verts, [(0, 1, 2, 3)])
    p["tile"] = tile
    u0, u1 = (1.0, 0.0) if flip else (0.0, 1.0)
    p["uvs"] = [((u0, 0.0), (u1, 0.0), (u1, 1.0), (u0, 1.0))]
    return p


def _face_quad(part, tile, cx, cz, w, h, y, flip=False):
    """An art quad in the XZ plane at depth ``y``, facing -Y (or +Y when
    flipped), wound so its normal points at the viewer."""
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    z0, z1 = cz - h / 2.0, cz + h / 2.0
    if flip:
        return _quad(part, tile, [(x1, y, z0), (x0, y, z0),
                                  (x0, y, z1), (x1, y, z1)], flip=True)
    return _quad(part, tile, [(x0, y, z0), (x1, y, z0),
                              (x1, y, z1), (x0, y, z1)])


def _game(key, n=0):
    return CB.game_order(key)[n % len(CB.GAMES)]


def linear(hex_srgb, k=1.0):
    """An sRGB hex from `card_brands`, deepened by ``k`` and in the linear
    0..1 a Blender colour socket takes. The planners return these so the
    recipes do not each carry a colour conversion."""
    return [round(srgb_to_linear(c) * float(k), 5)
            for c in CB.hex_rgb(hex_srgb)]


# --- poster ------------------------------------------------------------------

#: THE DEPTH LADDER, as fractions of the slot's depth, measured from the
#: FRONT face (-d/2). Every rung is at least `LADDER_MIN` of the depth apart,
#: so at the genome's 0.02 m minimum the closest pair is 3.2 mm -- above the
#: 2.2 mm window with room for the float. `tests/test_flat_art.py` measures
#: this rather than trusting it.
#:
#: Front to back: the frame's face, the mat's face, the ART QUAD, the
#: plate's own front, the mat's back, and the frame and plate backs together
#: on the wall plane -- which is allowed because the frame is a RING and the
#: plate fills the aperture inside the mat, so the two are disjoint in x and
#: z and no pair of faces overlaps.
FRAME_FRONT = 0.00
MAT_FRONT = 0.22
PLATE_ART = 0.44
PLATE_FRONT = 0.60
MAT_BACK = 0.80
BACK = 1.00
LADDER_MIN = 0.16

#: The frame's rail width and the mat's reveal, as fractions of the SHORTER
#: side, so a tall thin poster does not get a rail wider than its aperture.
RAIL_K = 0.055
MAT_K = 0.075
#: The tilt a `tilted` poster carries, in degrees, by variant. The walker's
#: reference is "mounted high and slightly tilted"; past about eight degrees
#: a poster reads as fallen rather than hung, and the shrink `_tilt_fit`
#: applies to keep it inside its slot grows fast.
TILTS = (3.5, -5.0, 6.5, -2.5)
FORMS = ("framed", "bare", "tilted")


def _tilt_fit(w, h, deg):
    """The un-rotated size whose ROTATED bounding box is exactly ``w`` x
    ``h``, or None when there is not one.

    A rectangle (a, b) turned by t has bounds (a*c + b*s, a*s + b*c) with
    c = cos t, s = sin t. Setting those equal to (w, h) and solving:

        a = (w*c - h*s) / (c*c - s*s)      b = (h*c - w*s) / (c*c - s*s)

    WHY SOLVE IT RATHER THAN LET `fit_exact` DO IT. `fit_exact` maps each
    axis independently, so squeezing a rotated rectangle back into its slot
    shears it -- the corners stop being square and the art is subtly
    trapezoidal. Solving first means the rotation lands ON the slot and
    nothing is squeezed. Returns None past 45 degrees or where the slot is
    too far from square to hold a turned rectangle at all, and the caller
    falls back to a smaller tilt rather than shipping a sheared one.
    """
    t = math.radians(abs(float(deg)))
    c, s = math.cos(t), math.sin(t)
    den = c * c - s * s
    if den <= 1e-9:
        return None
    a = (w * c - h * s) / den
    b = (h * c - w * s) / den
    if a <= 1e-4 or b <= 1e-4:
        return None
    return a, b


def _poster_plate(prims, tiles, w, h, d, game, key, maker):
    """The plate and its art quad, filling ``w`` x ``h`` centred on origin."""
    y0 = -d / 2.0
    prims.append(P.box("Poster_Plate", BOARD,
                       (-w / 2.0, y0 + PLATE_FRONT * d, -h / 2.0),
                       (w / 2.0, y0 + BACK * d, h / 2.0)))
    tile = "plate"
    tiles[tile] = {"kind": "poster", "game": game["id"], "maker": maker["id"],
                   "w_m": round(w, 4), "h_m": round(h, 4), "key": key}
    prims.append(_face_quad("Poster_Art", tile, 0.0, 0.0,
                            w - 2.0 * JOIN, h - 2.0 * JOIN,
                            y0 + PLATE_ART * d))


def _ring(prims, part, mat, w, h, t, y0, y1):
    """A closed rectangular ring: outer size ``w`` x ``h``, rail width ``t``,
    spanning ``y0``..``y1`` in depth. ONE mesh, sixteen quads.

    FOUR BOXES WAS THE FIRST DRAFT AND IT CANNOT BE MADE TO WORK, which is
    worth writing down because four boxes is the obvious way and every
    variation of it fails the same measurement. A ring's four rails have to
    meet somewhere, and wherever they meet they either BUTT -- two faces on
    one plane, the whole rail section in overlap -- or they OVERLAP, in
    which case they share the ring's own outer silhouette: x = +/- w/2 is a
    face of the left rail AND of the top rail over the top rail's depth,
    whatever inset either one is given. Measured on the first draft at every
    genome corner: 8 pairs per poster at 0.00 mm, 4.4 cm2 apiece.

    One mesh has no such pair, because its own four front trapezoids are
    coplanar but ADJACENT -- they share edges and overlap in zero area,
    which is below `coincident_pairs`' `min_area`. It is also cheaper: 32
    triangles against a box ring's 48.

    WINDING, because this is hand-wound geometry and a mesh with inverted
    normals is a hole in the wall. Outer corners run counter-clockwise in
    the XZ plane; a face's normal is (B - A) x (C - A), so a -Y face runs
    +X then +Z. `tests/test_flat_art.py` measures every face's normal
    against the direction it should point rather than trusting this note.
    """
    x, z = w / 2.0, h / 2.0
    xi, zi = x - t, z - t
    outer = ((-x, -z), (x, -z), (x, z), (-x, z))
    inner = ((-xi, -zi), (xi, -zi), (xi, zi), (-xi, zi))
    verts = ([(a, y0, b) for a, b in outer] + [(a, y0, b) for a, b in inner]
             + [(a, y1, b) for a, b in outer] + [(a, y1, b) for a, b in inner])
    O0, I0, O1, I1 = 0, 4, 8, 12          # base index of each corner ring
    faces = []
    for k in range(4):
        k1 = (k + 1) % 4
        faces.append((O0 + k, O0 + k1, I0 + k1, I0 + k))          # front, -Y
        faces.append((I1 + k, I1 + k1, O1 + k1, O1 + k))          # back, +Y
        faces.append((O1 + k, O1 + k1, O0 + k1, O0 + k))          # outer wall
        faces.append((I0 + k, I0 + k1, I1 + k1, I1 + k))          # inner wall
    prims.append(P.mesh(part, mat, verts, faces))


def plan_poster(w, d, h, params=None, variant=0, key="poster"):
    """``{"prims", "tiles", "collision", "facts"}`` for one wall poster."""
    params = params or {}
    form = params.get("form") or "auto"
    if form in (None, "auto"):
        form = FORMS[variant % len(FORMS)]
    if form not in FORMS:
        raise ValueError(f"poster: unknown form {form!r}")
    game = _game(f"{key}|{variant}", variant)
    maker = CB.maker_for(f"{key}|{variant}")
    prims, tiles = [], {}
    y0 = -d / 2.0
    tilt = 0.0

    if form == "framed":
        rail = max(0.012, min(w, h) * RAIL_K)
        matw = max(0.010, min(w, h) * MAT_K)
        _ring(prims, "Poster_Frame", FRAME, w, h, rail, y0, y0 + BACK * d)
        _ring(prims, "Poster_Mat", CLOTH, w - 2.0 * (rail - JOIN),
              h - 2.0 * (rail - JOIN), matw,
              y0 + MAT_FRONT * d, y0 + MAT_BACK * d)
        # THE MAT IS TWO EXTRA QUADS' WORTH OF RING, NOT A PAINTED BORDER,
        # and the reference is explicit that it has to be: "the mat is what
        # makes it read as framed rather than taped to the wall". Painting a
        # border into the plate's texture puts the reveal in the SAME plane
        # as the art, and what a mat actually does is drop the art 4 mm back
        # so the frame casts onto it. The whole ring is 32 triangles; the
        # `bare` form does not want them, and does not get them.
        pw = w - 2.0 * (rail - JOIN) - 2.0 * (matw - JOIN)
        ph = h - 2.0 * (rail - JOIN) - 2.0 * (matw - JOIN)
        _poster_plate(prims, tiles, pw, ph, d, game, key, maker)
    elif form == "bare":
        _poster_plate(prims, tiles, w, h, d, game, key, maker)
    else:                                            # tilted
        for cand in (TILTS[variant % len(TILTS)],) + TILTS:
            got = _tilt_fit(w, h, cand)
            if got:
                tilt = cand
                break
        else:
            got, tilt = (w, h), 0.0
        _poster_plate(prims, tiles, got[0], got[1], d, game, key, maker)
        prims = [P.rotate_y(p, math.radians(tilt)) for p in prims]

    prims, _ = P.fit_exact(prims, (-w / 2.0, -d / 2.0, 0.0),
                           (w / 2.0, d / 2.0, h))
    return {"prims": prims, "tiles": tiles, "collision": [],
            # THE MAT TAKES THE GAME'S OWN ACCENT, DEEPENED, and not the
            # reference's red: the reference is one frame on one wall and
            # this is a species a room gets eight of. A deepened accent
            # contrasts with the silver frame the way the red does and puts
            # the poster's own colour on the thing beside the art, which is
            # what the mat is for. The plate behind the art is near-black so
            # a bare edge does not read as paper.
            "colours": ((tuple(linear(game["accent"], 0.42)),
                         tuple(linear(game["ground"], 0.25))),),
            "facts": {"form": form, "variant": variant, "tilt_deg": tilt,
                      "game": game["name"], "maker": maker["short"],
                      "tiles": len(tiles), "tris": P.tri_count(prims),
                      "mat_rgb": linear(game["accent"], 0.42),
                      "plate_rgb": linear(game["ground"], 0.25),
                      "rung_m": round(min_rung_m(poster_planes(d)), 5)}}


def poster_planes(d):
    """Every plane the framed poster puts perpendicular to Y, as offsets
    from its front face. The same shape `test_coincident_faces.py` reads off
    `stop_sign`, and the thing `min_rung_m` is asked about."""
    return {"frame_front": FRAME_FRONT * d, "mat_front": MAT_FRONT * d,
            "art": PLATE_ART * d, "plate_front": PLATE_FRONT * d,
            "mat_back": MAT_BACK * d, "back": BACK * d}


# --- hanging_banner ----------------------------------------------------------

#: A banner's parts as fractions of its own height: the straps that carry it,
#: the rod through its head, and the weighted hem along its foot. A printed
#: banner without a hem bar curls, which is why every one in the references
#: has a visible bar at the bottom.
STRAP_H = 0.10
ROD_H = 0.055
HEM_H = 0.05
#: The cloth's own thickness, as a fraction of the slot depth. The rod and
#: the hem bar take the whole depth; the cloth is thinner than both, so its
#: faces are inside theirs and the art quad still clears the rod's own face.
CLOTH_K = 0.34


def plan_banner(w, d, h, params=None, variant=0, key="hanging_banner"):
    """A printed cloth banner on a rod, hung from two straps.

    THE STRAPS' SPREAD IS THE VARIANT, for `plan_hanger`'s reason: four
    banners over one wall run have to be four modules.
    """
    params = params or {}
    game = _game(f"{key}|{variant}", variant + 1)
    prims, tiles = [], {}
    strap = h * STRAP_H
    rod = h * ROD_H
    hem = h * HEM_H
    cloth_t = d * CLOTH_K
    cy0, cy1 = -cloth_t / 2.0, cloth_t / 2.0
    ry0, ry1 = -d / 2.0, d / 2.0
    # the straps: the top of the slot box is what they hang from (HANG_NOTE)
    sx = w * (0.30 + 0.04 * (variant % 4))
    for tag, x in (("L", -sx), ("R", sx)):
        prims.append(P.box(f"Banner_Strap{tag}", CHAIN,
                           (x - d * LINK_T / 2.0, -d * LINK_T / 2.0, h - strap),
                           (x + d * LINK_T / 2.0, d * LINK_T / 2.0, h)))
    top = h - strap + JOIN
    prims.append(P.box("Banner_Rod", CHAIN, (-w / 2.0, ry0, top - rod),
                       (w / 2.0, ry1, top)))
    foot = 0.0
    prims.append(P.box("Banner_Hem", CHAIN, (-w / 2.0, ry0, foot),
                       (w / 2.0, ry1, foot + hem)))
    prims.append(P.box("Banner_Cloth", CLOTH,
                       (-w / 2.0 + JOIN, cy0, foot + hem - JOIN),
                       (w / 2.0 - JOIN, cy1, top - rod + JOIN)))
    cw = w - 4.0 * JOIN
    ch = (top - rod + JOIN) - (foot + hem - JOIN) - 2.0 * JOIN
    tile = "face"
    tiles[tile] = {"kind": "banner", "game": game["id"],
                   "w_m": round(cw, 4), "h_m": round(max(ch, 0.02), 4),
                   "key": key}
    cz = (foot + hem + top - rod) / 2.0
    prims.append(_face_quad("Banner_Art", tile, 0.0, cz, cw, ch,
                            cy0 - d * ART_OUT))
    prims, _ = P.fit_exact(prims, (-w / 2.0, -d / 2.0, 0.0),
                           (w / 2.0, d / 2.0, h))
    return {"prims": prims, "tiles": tiles, "collision": [],
            "colours": ((tuple(linear(game["ground"], 0.30)),
                         tuple(linear(game["border"], 0.50))),),
            "facts": {"variant": variant, "game": game["name"],
                      "tiles": len(tiles), "tris": P.tri_count(prims),
                      # the cloth's own hem and rod, so a banner's hardware
                      # is the game's dark and not the room's grey (the
                      # contrast rule: a prop that falls back to the
                      # building default disappears into it)
                      "cloth_rgb": linear(game["ground"], 0.30),
                      "rod_rgb": linear(game["border"], 0.50),
                      "cloth_m": (round(cw, 3), round(ch, 3))}}


# --- ceiling_hanger and aisle_sign -------------------------------------------

#: A drop chain's links: how many, how thick as a fraction of the slot
#: depth, and how much of each link's pitch is metal (the rest is the gap
#: between links, which is what makes it read as a chain rather than a rod).
#:
#: THREE BOXES AND NOT A MODELLED CHAIN. At the distance a body reads a
#: ceiling hanger -- two metres below it, looking up -- a chain IS a dashed
#: line, and a modelled link costs 12 triangles apiece for a shape nobody
#: resolves. The links are DISJOINT in z, which is also what keeps them out
#: of the coincident-face measurement: two boxes that do not touch cannot
#: share a plane, and a staggered overlapping chain (the first draft) put
#: 0.5 * LINK_T between two faces, which at the genome's minimum depth was
#: 1.6 mm and inside the 2.2 mm window.
LINKS = 3
LINK_T = 0.16
LINK_FILL = 0.62
#: How much of a hanger's height is chain. The rest is the painted plate.
DROP_K = 0.34
#: An aisle sign hangs off two short drops rather than one, because a
#: lettered board on one chain swings and a real one does not.
SIGN_DROP_K = 0.26
#: How far an art quad stands off the board behind it, as a fraction of the
#: slot depth. FRACTIONAL and not `ART_PROUD`, for the reason the poster's
#: ladder is: an absolute 5 mm on a 0.03 m slot is a sixth of the depth, and
#: the whole plan would be stretched by `fit_exact` to put it back. At the
#: genome's 0.03 m minimum this is 4.8 mm.
ART_OUT = 0.16


def _drops(prims, xs, d, z0, z1, part="Chain"):
    """``LINKS`` separate links between ``z0`` and ``z1`` at each x in
    ``xs``, the bottom one buried `JOIN` into whatever is below."""
    t = d * LINK_T
    span = max(1e-4, z1 - z0)
    step = span / LINKS
    for i, x in enumerate(xs):
        for k in range(LINKS):
            lo_z = z0 + k * step - (JOIN if k == 0 else 0.0)
            hi_z = z0 + k * step + step * LINK_FILL
            if k == LINKS - 1:
                hi_z = z1
            prims.append(P.box(f"{part}_{i}_{k}", CHAIN,
                               (x - t / 2.0, -t / 2.0, lo_z),
                               (x + t / 2.0, t / 2.0, hi_z)))


def _hung_board(prims, tiles, w, d, h, drop_k, xs, spec, part, key):
    """A painted board on drops: the chain from the ceiling plane (z = h)
    down to the board, the board itself, and ONE tile on both of its faces.

    BOTH FACES CARRY ONE TILE. A hanging sign is printed both sides, and
    painting the second side is a second tile of atlas for a difference
    nobody can see from either side -- so the back quad is the front's tile
    with U mirrored.

    The board fills the slot's depth less the art's stand-off each side, so
    the quads land exactly on +/- d/2 and nothing is stretched.
    """
    drop = h * drop_k
    board_h = h - drop
    _drops(prims, xs, d, board_h, h, part)
    plate_t = d * (1.0 - 2.0 * ART_OUT)
    prims.append(P.box(part + "_Board", BOARD,
                       (-w / 2.0, -plate_t / 2.0, 0.0),
                       (w / 2.0, plate_t / 2.0, board_h)))
    bw, bh = w - 2.0 * JOIN, board_h - 2.0 * JOIN
    tiles["face"] = dict(spec, w_m=round(bw, 4),
                         h_m=round(max(bh, 0.02), 4), key=key)
    for flip, y in ((False, -d / 2.0), (True, d / 2.0)):
        prims.append(_face_quad(part + ("_ArtBack" if flip else "_Art"),
                                "face", 0.0, board_h / 2.0, bw, bh, y,
                                flip=flip))
    return board_h


def plan_hanger(w, d, h, params=None, variant=0, key="ceiling_hanger"):
    """The painted model on a drop chain -- the reference's dragon and
    kraken, in an invented game's colours.

    THE DROP IS THE VARIANT. A shop hangs four of these at four lengths off
    one ceiling; making the chain the thing that moves means four hangers in
    one room are four modules rather than one module four times, which is
    what `module_variants` has to mean (`kit.honour_dressing` refuses a
    species whose variants differ only in wear noise).
    """
    params = params or {}
    game = _game(f"{key}|{variant}", variant + 2)
    drop_k = DROP_K + 0.06 * (variant % 4)
    prims, tiles = [], {}
    board_h = _hung_board(prims, tiles, w, d, h, drop_k, (0.0,),
                          {"kind": "hanger", "game": game["id"]},
                          "Hanger", key)
    prims, _ = P.fit_exact(prims, (-w / 2.0, -d / 2.0, 0.0),
                           (w / 2.0, d / 2.0, h))
    return {"prims": prims, "tiles": tiles, "collision": [],
            "colours": ((tuple(linear(game["border"], 0.45)),
                         tuple(linear(game["accent"], 0.30))),),
            "facts": {"variant": variant, "game": game["name"],
                      "tiles": len(tiles), "tris": P.tri_count(prims),
                      "board_rgb": linear(game["border"], 0.45),
                      "chain_rgb": linear(game["accent"], 0.30),
                      "drop_m": round(h - board_h, 3),
                      "board_m": round(board_h, 3), "hangs_from": HANG_NOTE}}


def plan_aisle_sign(w, d, h, params=None, variant=0, key="aisle_sign"):
    """The hand-lettered sign hung over an aisle naming what is under it."""
    params = params or {}
    says = params.get("says")
    if not says:
        says = CB.AISLE_SAYS[variant % len(CB.AISLE_SAYS)]
    spread = 0.30 + 0.04 * (variant % 4)
    prims, tiles = [], {}
    xs = (-w * spread, w * spread)
    board_h = _hung_board(prims, tiles, w, d, h, SIGN_DROP_K, xs,
                          {"kind": "aisle", "says": says}, "AisleSign", key)
    prims, _ = P.fit_exact(prims, (-w / 2.0, -d / 2.0, 0.0),
                           (w / 2.0, d / 2.0, h))
    return {"prims": prims, "tiles": tiles, "collision": [],
            "facts": {"variant": variant, "says": says,
                      "tiles": len(tiles), "tris": P.tri_count(prims),
                      "drop_m": round(h - board_h, 3),
                      "board_m": round(board_h, 3)}}
