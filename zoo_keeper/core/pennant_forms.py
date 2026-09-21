"""The strip of felt pennants along the top of a card shop's wall.

Zoo 0.95.0. The reference (`docs/SET_DRESSING_REFERENCES.md`, the 1990s
shop): "Along the top of the walls, a row of felt TEAM PENNANTS pinned at an
angle, overlapping, in many colours."

FRAME AND UNITS: metres, Z up, the slot's box, -Y the room, +Y the wall.

CHEAP ON PURPOSE, AND THE CAP IS DERIVED FROM THE BUDGET. A pennant is a
triangular prism (8 triangles) plus a hoist band (12), so 20 triangles;
`MAX_PENNANTS` is `(budget - fixed) // 20` rather than a number somebody
liked, which means raising the budget raises the pennant count and nothing
else has to move. At the genome's widest slot the pitch, not the cap, is
what bites.

NOTHING HERE IS LETTERED. A pennant hangs at ceiling height and its ink
would be under two pixels at `card_art.TEXEL`; what a pennant reads as
across a room is a COLOUR and a band, so it is a colour and a band. The
teams it wears are still the invented ones -- `card_brands.TEAMS` -- because
the colours come in pairs from that table and a shop's pennants are its
local clubs.

THEY ARE FLAT AND THEY MUST STILL HAVE A THICKNESS. A zero-thickness
pennant has its front and back faces in one plane with full overlap, which
is a coincident pair at gap 0 -- the worst kind. `FELT_T` is 6 mm: thicker
than felt, thicker than the 2.2 mm window the tests use, and invisible at
the distance this is seen from.

OVERLAPPING PENNANTS ARE LAYERED. Neighbours overlap by `OVERLAP` of their
width, so two pennants in ONE y-plane would share it over that overlap.
They alternate between two layers `LAYER_STEP` apart, and the pitch is set
so a pennant and its SECOND neighbour -- the next one in its own layer --
never meet: `OVERLAP` below 0.5 is what guarantees that, and a test holds it.

REFUTED 2026-09-21: THIS ROW CANNOT BE A MULTIMESH, AND THE REASON IS THE
ENGINE. 1.1.0 left the choice open above the merge result -- "a MultiMesh
would also reach 2 draw calls for the whole row with per-instance colour,
which is Lot's dressing pattern one shelf along" -- and it was chosen. It
does not work, for a reason nobody had measured: **Godot 4.7 does not
implement `EXT_mesh_gpu_instancing`**, the only way a .glb can express
instancing, and it discards it without a word. Three instances of one
triangle reach the engine as one triangle, by both the runtime
(`GLTFDocument.append_from_file`) and the editor (`load()`) paths, and the
extension's name does not occur anywhere in the engine executable. On a
44-pennant row that is 43 pennants deleted from a file that still validates
and still censuses correctly, because the loss happens on import.

So the row stays one mesh per colour. `tools/instancing_probe.py` is the
instrument, `tests/test_gpu_instancing.py` holds the rule with its positive
control, and the two corrections worth carrying forward are these:

  * **It would have been 3 draw calls, not 2.** A pennant wears TWO team
    colours -- `colours[i]` is a (primary, secondary) pair, the felt takes
    the first and the hoist band the second -- so per-instance colour buys
    one MultiMesh per colour ROLE. Batten + felt + band is three. Two needs
    the band's colour in `INSTANCE_CUSTOM` and a shader to choose between
    them, which is a custom material for a prop that today has none.
  * **The capability is not Zoo's.** A MultiMesh reaches Godot here as
    .tscn text from `level_factory/.../dressing_scene.py`, over meshes
    `extract_meshes.gd` pulls out of Zoo's GLBs. Zoo's job would be to emit
    ONE pennant worth instancing; the instancing is the composer's. Note
    that path writes `transform_format`, `instance_count` and `buffer` and
    has no `use_colors`, so per-instance colour does not exist there yet
    either.
"""
from __future__ import annotations

import math

from . import card_brands as CB
from . import prims as P

JOIN = 0.004
#: THE DEPTH LADDER, and every number in it was set by the probe. A layer
#: is four planes -- the band's front and back and the felt's front and back
#: -- and the tests' window is 2.2 mm, so they step by 3 mm and the two
#: LAYERS clear each other by 5. MEASURED at the first attempt (`FELT_T`
#: 6 mm, `BAND_PROUD` 4, `LAYER_STEP` 7): one layer's felt back sat 1.0 mm
#: off the next layer's felt front and the bands 0.6 mm apart, 121 pairs on
#: a 3 m strip. A layer now spans 11 mm and the next starts 5 mm after it.
FELT_T = 0.006
BAND_PROUD = 0.005
BAND_BACK = 0.003
#: The band along the hoist (the pinned edge), as a fraction of the length,
#: and how far below the pennant's own top edge it is stitched. 6 mm and not
#: 2: at 2 the band's top face and the felt's were 2.04 mm apart after
#: `fit_exact`, on every pennant of every strip -- and 2 mm is the window.
BAND_F = 0.16
BAND_TOP = 0.006
#: The batten the pennants are pinned to, at the wall.
BATTEN_T = 0.020
BATTEN_H = 0.045
#: How much of its own width a pennant overlaps its neighbour. Must stay
#: under 0.5 or a pennant reaches its second neighbour, which is in the
#: same layer and therefore in the same plane.
OVERLAP = 0.34
#: The two layers overlapping pennants alternate between: a layer's own
#: 11 mm plus 5 mm of daylight.
LAYER_STEP = 0.016
#: How far a pennant is tipped off plumb, alternating. A pinned pennant is
#: never straight in any of the photographs.
TILT_DEG = 12.0
#: Triangles a pennant costs: the prism's two caps and three sides (8), plus
#: the band's box (12). `MAX_PENNANTS` is derived from this and the budget.
TRIS_PER_PENNANT = 20
FIXED_TRIS = 12

FELT, BAND, BATTEN = "felt", "band", "batten"


def max_pennants(budget):
    """The cap, derived: what is left of the budget after the batten,
    divided by what a pennant costs."""
    return max(1, int((int(budget) - FIXED_TRIS) // TRIS_PER_PENNANT))


def _pennant(tag, cx, z_top, length, width, y_front, tilt, rgb_i):
    """One pennant: a triangular prism pointing down, and its hoist band.

    Built upright in the x-z plane and then turned about Y through ``tilt``
    about its own pin, which leaves y untouched -- so the layer a pennant is
    in survives the tilt.
    """
    half = width / 2.0
    tip_z = z_top - length
    tri = [(cx - half, y_front + FELT_T, z_top),
           (cx + half, y_front + FELT_T, z_top),
           (cx, y_front + FELT_T, tip_z),
           (cx - half, y_front, z_top),
           (cx + half, y_front, z_top),
           (cx, y_front, tip_z)]
    faces = [(3, 4, 5), (2, 1, 0), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    body = P.mesh(f"PennantRow_Felt{tag}", FELT, tri, faces)
    band_h = length * BAND_F
    band = P.box(f"PennantRow_Band{tag}", BAND,
                 (cx - half * 0.96, y_front - BAND_PROUD, z_top - band_h),
                 (cx + half * 0.96, y_front + BAND_BACK, z_top - BAND_TOP))
    out = []
    for p in (body, band):
        out.append(P.rotate_y(p, math.radians(tilt), about=(cx, z_top)))
    out[0]["colour_index"] = rgb_i
    out[1]["colour_index"] = rgb_i
    return out


def plan(w, d, h, params=None, variant=0, key="pennant_row", budget=900):
    """Everything the recipe builds: ``{"prims", "colours", "collision",
    "facts"}``.

    ``colours`` is ``[(primary linear rgb, secondary linear rgb), ...]``
    indexed by each prim's ``colour_index`` -- the recipe makes one material
    per colour, which is what keeps a 25-pennant strip to three draws of
    geometry rather than 25.
    """
    w, d, h = float(w), float(d), float(h)
    params = params or {}
    variant = int(variant or 0)
    teams = CB.team_order(f"{key}|{variant}")
    n_colours = int(params.get("colours", 6) or 6)
    n_colours = max(2, min(len(teams), n_colours))

    x0, x1 = -w / 2.0, w / 2.0
    y0, y1 = -d / 2.0, d / 2.0
    prims = []
    # THE BATTEN at the wall, owning +Y, both ends and z = h.
    prims.append(P.box("PennantRow_Batten", BATTEN,
                       (x0, y1 - BATTEN_T, h - BATTEN_H), (x1, y1, h)))

    length = h - BATTEN_H + JOIN
    width = min(float(params.get("pennant_w", 0.0) or 0.0) or length * 0.42,
                length * 0.60)
    pitch = width * (1.0 - OVERLAP)
    cap = max_pennants(budget)
    n = max(1, min(cap, int(round((w - width) / pitch)) + 1))
    span = w - width
    step = span / max(1, n - 1) if n > 1 else 0.0
    # the pennant bodies sit just behind the room-side plane; the bands own
    # y = -d/2 and every pennant's band reaches it, but two bands only ever
    # share it where they overlap -- and neighbours are in different layers
    y_front = y0 + BAND_PROUD
    for k in range(n):
        cx = x0 + width / 2.0 + step * k
        # THE VARIANT PHASES THE TILT as well as picking the colours: with
        # colours alone, four variants of one slot were four copies of one
        # geometry, and `kit.honour_dressing` would have been carrying a
        # difference that was only skin deep.
        layer = (k + variant) % 2
        tilt = TILT_DEG if layer == 0 else -TILT_DEG
        prims += _pennant(f"{k}", cx, h - BATTEN_H + JOIN, length, width,
                          y_front + layer * LAYER_STEP, tilt,
                          (k + variant) % n_colours)
    # THE TILT OVERSHOOTS THE SLOT, so the plan ends with `prims.fit_exact`
    # -- the module's own answer to "a detail stands a few mm proud and the
    # slot is exact". MEASURED before it: at 14.0 x 0.12 x 0.50 the turned
    # pennants ran 18.8 mm wide and 10.0 mm SHORT of the floor, because a
    # tilt spends vertical drop on horizontal reach. The correction is 0.13 %
    # in x and 2.0 % in z, well inside the "within a percent of 1" the
    # function's docstring gives for not closing a gap somebody kept open --
    # and the probe below is what proves that rather than the docstring.
    prims, _boxes = P.fit_exact(prims, (x0, y0, 0.0), (x1, y1, h))
    colours = [(_lin(teams[i % len(teams)][1]), _lin(teams[i % len(teams)][2]))
               for i in range(n_colours)]
    facts = {"pennants": n, "colours": n_colours, "cap": cap,
             "pitch_m": round(pitch, 4), "width_m": round(width, 4),
             "length_m": round(length, 4), "variant": variant,
             "tris": P.tri_count(prims),
             "teams": [teams[i % len(teams)][0] for i in range(n_colours)]}
    return {"prims": prims, "colours": colours, "collision": [], "facts": facts}


def _lin(hex_srgb):
    """sRGB hex to linear RGB -- the space a genome colour is in."""
    from .brands import srgb_to_linear
    return [round(srgb_to_linear(c), 5) for c in CB.hex_rgb(hex_srgb)]


def bounds(got):
    return P.bounds(got["prims"])
