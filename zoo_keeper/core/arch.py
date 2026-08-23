"""Architectural module geometry (pure): decompose a center-pivot wall slab
(with an optional passable void) into axis-aligned boxes.

Architectural modules (wall / doorway / window / breach / wallEnd) are a
different kind of species from Zoo's props. They are the parts Deli Counter
swaps into a greybox building's wall slots, so they follow different rules:

- CENTER pivot, not bottom-center. Geometry is centered on the origin in all
  three axes; Deli Counter drops the module onto a slot transform (the slot's
  center) with no conversion.
- fit-to-EXACT-dims, not sampled. The module is built at the slot's authored
  width/depth/height; Deli Counter instances it at that size and NEVER scales
  it (the width is baked into the filename, e.g. ``_w200`` = exactly 2.00 m).

The box tiling here guarantees the union's outer bounding box equals
``(w, d, h)`` exactly: the left/right jambs always reach ``+/-w/2`` and span the
full height, and every box spans the full depth. So a doorway/window/breach is
a *hole in a slab of the exact requested size* — fit-to-exact-dims validation
passes by construction.

Coordinates: centered on the origin. x in [-w/2, w/2] (width), y in [-d/2, d/2]
(thickness), z in [-h/2, h/2] (height). The floor of the module is at z=-h/2.
"""
from __future__ import annotations

# species whose slab is solid (no void)
#: Species with no passable opening, EVER. Listed rather than left to fall
#: off the end of `void_for`, because "solid by accident" is how a ceiling
#: skin ended up capping a stairwell -- see PLATE_SPECIES below.
#: `prop` is a vault, a counter, a desk, a crate stack: a solid object
#: built to a Deli Counter volume's exact dims. It is not architecture and
#: nothing walks through it.
_SOLID = ("wall", "wallEnd", "prop")

#: Species built as a horizontal PLATE rather than a standing slab. Their holes
#: are in x/y and are cut by :func:`plate_parts`; ``void_for`` returns None for
#: them, which it also did by falling off the end -- saying so is the point,
#: because "solid by accident" is how a ceiling skin ended up capping a
#: stairwell.
PLATE_SPECIES = ("floor", "ceiling", "roof")

#: Plates that STILL emit collision. `PLATE_SPECIES` used to carry two
#: independent facts at once -- "its holes are in x/y" and "it emits no
#: collision" -- because floors and ceilings happen to be both. A roof is the
#: first species that is a plate AND collides, and the conflation had nowhere
#: to put it, so `roof` sat in `_SOLID` instead and got neither the void
#: tiling nor a way to say it wanted collision.
#:
#: Measured 2026-08-09 on `bank_branch_a04`: Deli Counter cut the ladder's
#: through-hole in its own roof slab (`slab_col_2-colonly`, corners 15.45 /
#: 16.55 / -10.90) and Zoo laid `roof_rockay_01_w4000.glb` over it as one
#: solid 40 x 30 panel carrying `Roof-colonly`. The walk bot stalled against a
#: collider named `Roof` at the slab underside -- a ladder climbing a full
#: storey into roof. That is the same failure `plate_parts` was written for,
#: one surface up.
#:
#: A floor or ceiling skin declares `collision: "none"` and means it; the roof
#: slot declares `collision: "trimesh"` and now gets it, tiled around the void
#: rather than over it.
PLATE_COLLIDES = ("roof",)

_EPS = 1e-6

# clean part-name prefixes (species.title() would mangle the camelCase wallEnd)
_ROOT = {"wallEnd": "WallEnd"}


def root_name(species: str) -> str:
    """Object-name prefix for a module's parts, e.g. 'wallEnd' -> 'WallEnd'."""
    if species in _ROOT:
        return _ROOT[species]
    return "".join(p[:1].upper() + p[1:] for p in species.split("_"))


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def authored_void(w: float, h: float, opening, jamb_x0: float, jamb_x1: float):
    """The void a slot's own ``fit.openings`` entry asks for, or None.

    THE OPENING IS AUTHORED UPSTREAM AND WAS BEING THROWN AWAY. Deli Counter
    writes the real aperture on every doorway/window/breach slot --
    ``{"kind": "door", "width": 1.2, "height": 2.2, "sill": 0.0}`` -- and
    :func:`void_for` never read it, deriving a hole from genome FRACTIONS of
    the module height instead. On a 3.7 m storey that is not a near miss:

        slot asks          this used to cut     error
        1.20 x 2.20 @0.00  0.96 x 3.48 @0.00    +1.28 m tall
        1.50 x 2.20 @0.00  1.26 x 3.60 @0.00    +1.40 m tall   (breach)
        3.00 x 1.40 @0.80  2.76 x 1.67 @1.29    +0.27 m, +0.49 m up

    A door became a slit running floor to ceiling and every window floated
    half a metre high, which is what the facade reads as "unconventional
    window shapes". The fractions stay as the fallback for a module with no
    authored opening -- a greybox kit, or a species DC does not describe.

    WIDTH IS STILL JAMB-CLAMPED. DC authors the module exactly as wide as its
    aperture, so honouring the width literally would leave no jamb, and with
    no jamb nothing in :func:`slab_parts` spans the module's full height and
    fit-to-exact-dims stops passing by construction. A narrower authored width
    IS honoured -- a 1.0 m door in a 2.0 m module is a real thing to ask for.

    ONE OPENING PER MODULE. ``slab_parts`` tiles around a single rect, so a
    slot listing two apertures gets its first; every slot measured so far
    lists exactly one. Two would want a different tiling, not a loop here.
    """
    if not opening:
        return None
    oh = float(opening.get("height") or 0.0)
    if oh <= 0.0:
        return None                       # nothing authored -> use the genome
    hh = h / 2.0
    x0, x1 = jamb_x0, jamb_x1
    ow = float(opening.get("width") or 0.0)
    if ow > 0.0:
        half = min(ow / 2.0, (x1 - x0) / 2.0)
        x0, x1 = -half, half
    z0 = -hh + _clamp(float(opening.get("sill") or 0.0), 0.0, h)
    z1 = min(z0 + oh, hh)
    if z1 - z0 <= _EPS or x1 - x0 <= _EPS:
        return None                       # degenerate -> use the genome
    return {"x0": x0, "x1": x1, "z0": z0, "z1": z1}


def void_for(species: str, w: float, h: float, params: dict | None = None):
    """The passable opening for a module, in centered coords, or None (solid).

    Returned dict has x0<x1 (opening left/right) and z0<z1 (bottom/top). The
    opening never touches the outer width edges (jambs always survive), so the
    slab's outer footprint stays exact. Openings that reach the floor use
    ``z0 == -h/2`` (no sill) so a player can walk/see through.

    ``params["opening"]`` is the slot's OWN authored aperture and wins over
    every per-species rule below -- see :func:`authored_void`. The rules are
    the fallback, not the contract.
    """
    params = params or {}
    if species in _SOLID or species in PLATE_SPECIES:
        return None

    # symmetric jambs; never let the opening swallow the whole width
    jamb = float(params.get("jamb", 0.12))
    if w > 0.24:
        jamb = _clamp(jamb, 0.02, (w - 0.20) / 2.0)
    else:
        jamb = 0.02
    x0, x1 = -w / 2.0 + jamb, w / 2.0 - jamb
    hh = h / 2.0

    authored = authored_void(w, h, params.get("opening"), x0, x1)
    if authored is not None:
        return authored

    if species == "doorway":
        header = min(float(params.get("header", 0.22)), h * 0.40)
        return {"x0": x0, "x1": x1, "z0": -hh, "z1": hh - header}

    if species == "breach":
        # a punched hole to the floor with only a thin lintel remaining; the
        # blown/rough look is a later art pass — this is the clean cutout.
        lintel = min(float(params.get("lintel", 0.10)), h * 0.25)
        return {"x0": x0, "x1": x1, "z0": -hh, "z1": hh - lintel}

    if species == "window":
        sill = _clamp(float(params.get("sill", 0.35)), 0.05, 0.7)   # frac of h
        head = _clamp(float(params.get("head", 0.20)), 0.05, 0.7)   # frac of h
        z0 = -hh + h * sill
        z1 = hh - h * head
        if z1 <= z0:  # degenerate short module -> center a modest slot
            z0, z1 = -h * 0.2, h * 0.2
        return {"x0": x0, "x1": x1, "z0": z0, "z1": z1}

    if species == "vault_door":
        # a heavy portal: thick jambs (from the genome's larger jamb), a header,
        # and a raised threshold LIP you step over (vaults sit proud of the
        # floor). The armored leaf fills this opening in the closed state.
        header = min(float(params.get("header", 0.20)), h * 0.35)
        lip = min(float(params.get("sill_lip", 0.15)), h * 0.20)
        return {"x0": x0, "x1": x1, "z0": -hh + lip, "z1": hh - header}

    return None


def slab_parts(w: float, d: float, h: float, void: dict | None):
    """Boxes tiling a centered w x d x h slab around an optional void.

    Returns a list of ``(name, (cx, cy, cz), (sx, sy, sz))``. With no void this
    is a single ``Panel``; with a void it is up to four boxes (Jamb_L, Jamb_R,
    Sill, Header) whose union outer bbox is exactly ``(w, d, h)``.
    """
    hw, hh = w / 2.0, h / 2.0
    if not void:
        return [("Panel", (0.0, 0.0, 0.0), (round(w, 6), round(d, 6),
                                            round(h, 6)))]

    x0, x1 = void["x0"], void["x1"]
    z0, z1 = void["z0"], void["z1"]
    parts = []

    # left / right jambs: full height, reach the outer width edges
    if x0 > -hw + _EPS:
        cw = x0 - (-hw)
        parts.append(("Jamb_L", ((-hw + x0) / 2.0, 0.0, 0.0),
                      (round(cw, 6), round(d, 6), round(h, 6))))
    if x1 < hw - _EPS:
        cw = hw - x1
        parts.append(("Jamb_R", ((x1 + hw) / 2.0, 0.0, 0.0),
                      (round(cw, 6), round(d, 6), round(h, 6))))

    # sill (below opening) / header (above opening): span the opening width
    ow = x1 - x0
    if z0 > -hh + _EPS:
        ch = z0 - (-hh)
        parts.append(("Sill", ((x0 + x1) / 2.0, 0.0, (-hh + z0) / 2.0),
                      (round(ow, 6), round(d, 6), round(ch, 6))))
    if z1 < hh - _EPS:
        ch = hh - z1
        parts.append(("Header", ((x0 + x1) / 2.0, 0.0, (z1 + hh) / 2.0),
                      (round(ow, 6), round(d, 6), round(ch, 6))))
    return parts


#: A plate's voids are inset from its edges by this much so the union's outer
#: bbox still equals the authored (w, d, h). Same law as the jambs in
#: :func:`void_for` -- fit-to-exact-dims has to pass by construction, and a
#: stairwell cut hard against a wall would otherwise shrink the plate. Two
#: centimetres of rim at the lip of a hole is invisible from below and carries
#: no collision.
PLATE_RIM = 0.02


def plate_voids(w: float, d: float, voids, rim: float = PLATE_RIM):
    """Clip rectangular voids to a centered w x d plate, dropping degenerates.

    ``voids`` are dicts with x0/y0/x1/y1 in the plate's own centered coords.
    Returns a normalised list, sorted, so the tiling below is deterministic.
    """
    hw, hd = w / 2.0, d / 2.0
    lo_x, hi_x = -hw + rim, hw - rim
    lo_y, hi_y = -hd + rim, hd - rim
    out = []
    for v in voids or ():
        x0 = _clamp(min(float(v["x0"]), float(v["x1"])), lo_x, hi_x)
        x1 = _clamp(max(float(v["x0"]), float(v["x1"])), lo_x, hi_x)
        y0 = _clamp(min(float(v["y0"]), float(v["y1"])), lo_y, hi_y)
        y1 = _clamp(max(float(v["y0"]), float(v["y1"])), lo_y, hi_y)
        if x1 - x0 <= _EPS or y1 - y0 <= _EPS:
            continue          # entirely outside the plate, or a sliver
        out.append({"x0": round(x0, 6), "y0": round(y0, 6),
                    "x1": round(x1, 6), "y1": round(y1, 6)})
    return sorted(out, key=lambda v: (v["x0"], v["y0"], v["x1"], v["y1"]))


def plate_parts(w: float, d: float, h: float, voids=None):
    """Boxes tiling a centered w x d x h PLATE around rectangular voids.

    The horizontal counterpart of :func:`slab_parts`. That one cuts a hole in
    the x/z plane -- a doorway in a standing wall -- and a floor's hole is in
    x/y, so the two cannot share machinery however similar they read.

    THIS IS WHY IT EXISTS. Deli Counter's slabs are trimesh precisely because
    stairwells, ramps and hatches boolean-cut holes in them; a floor or ceiling
    skin laid over one as a plain rectangle caps those holes. Visually you get
    a ceiling above a staircase, and if the skin carries collision you cannot
    climb it.

    The tiling is a guillotine grid: every void edge becomes a cut line, cells
    whose centre lies in a void are dropped, and surviving cells are merged
    along x. Deterministic, exact, and it handles any number of voids including
    overlapping ones. Returns ``(name, (cx, cy, cz), (sx, sy, sz))`` like
    :func:`slab_parts`; with no voids it is a single ``Panel``, byte-identical
    to the old solid behaviour.
    """
    vs = plate_voids(w, d, voids)
    if not vs:
        return [("Panel", (0.0, 0.0, 0.0), (round(w, 6), round(d, 6),
                                            round(h, 6)))]
    hw, hd = w / 2.0, d / 2.0
    xs = sorted({-hw, hw} | {v["x0"] for v in vs} | {v["x1"] for v in vs})
    ys = sorted({-hd, hd} | {v["y0"] for v in vs} | {v["y1"] for v in vs})

    def covered(cx, cy):
        return any(v["x0"] < cx < v["x1"] and v["y0"] < cy < v["y1"]
                   for v in vs)

    rects = []
    for j in range(len(ys) - 1):
        y0, y1 = ys[j], ys[j + 1]
        if y1 - y0 <= _EPS:
            continue
        cy = (y0 + y1) / 2.0
        run_x0 = None
        for i in range(len(xs) - 1):
            x0, x1 = xs[i], xs[i + 1]
            if x1 - x0 <= _EPS:
                continue
            if covered((x0 + x1) / 2.0, cy):
                if run_x0 is not None:
                    rects.append((run_x0, prev_x1, y0, y1))
                    run_x0 = None
                continue
            if run_x0 is None:
                run_x0 = x0
            prev_x1 = x1
        if run_x0 is not None:
            rects.append((run_x0, prev_x1, y0, y1))

    return [("Plate_%d" % n,
             (round((r[0] + r[1]) / 2.0, 6), round((r[2] + r[3]) / 2.0, 6),
              0.0),
             (round(r[1] - r[0], 6), round(r[3] - r[2], 6), round(h, 6)))
            for n, r in enumerate(rects)]


#: Largest edge a plate's VISUAL part may have, in metres. Roadmap item 54:
#: Godot's GL Compatibility renderer lights at most 8 positional lights per
#: MESH (`max_lights_per_object`, engine default 8), and a mesh is an object,
#: so a 52 x 32 m roof panel is one light budget for a whole building --
#: measured across lot_demo_001's five buildings as 111 meshes over 8, worst
#: one at 36 lights, showing up as a hard brightness step where two slabs
#: meet. Splitting the visual into tiles gives every ~8 m patch its own
#: budget, which is how walls (2 m modules, 6 lights or fewer) never had the
#: problem. Eight metres is a starting value the per-mesh light census
#: (tools/mesh_light_census.py) has to confirm; item 41 measures the opposite
#: failure (1389-node fragmentation), so the answer is "as few tiles as the
#: census allows", not "smaller is safer".
PLATE_TILE = 8.0


def tile_parts(parts, tile: float = PLATE_TILE):
    """Split any part wider than ``tile`` (in x or y) into a grid of tiles.

    Input and output are ``(name, center, size)`` lists in the shape
    :func:`slab_parts` / :func:`plate_parts` emit, so this composes after
    either. VISUAL-ONLY BY CONTRACT: the caller keeps building collision from
    the untiled list (the same split `relief_parts` already has -- `slab` is
    the structure and the collider, `visual` is what the renderer sees), so
    no collision box on any existing build moves by a millimetre.

    The grid divides the part into equal cells (``ceil(extent / tile)`` per
    axis) rather than walking fixed strides, so there is never a sliver tile
    at one edge -- an 8.05 m part becomes two 4.025 m tiles, not an 8 m tile
    and a 5 cm strip that item 41 would rightly call noise. Cell edges are
    computed once and shared between neighbours, so abutting tiles meet at
    the same coordinate and the union's outer bbox stays exactly the part's
    own. A part already inside the tile on both axes passes through
    UNTOUCHED, name included -- every wall, jamb, sill and small plate is
    byte-identical to what it was before this function existed.
    """
    if not tile or tile <= 0.0:
        return list(parts)

    def edges(lo, extent, n):
        # INTERIOR cut lines are snapped to whole millimetres; the OUTER two
        # are the part's own bounds, untouched. The snap is what makes the
        # 6-decimal rounding below LOSSLESS: an equal division of 52 m into 7
        # puts cuts at repeating decimals, and rounding each tile's center
        # and size independently then disagrees with its neighbour's at the
        # sixth decimal -- a micron crack, invisible on screen but a lie in
        # the data, and `parts_bbox` no longer returns the authored dims.
        # Cells differ from equal by at most half a millimetre, which no
        # census or fit check can see.
        return ([lo] + [round(lo + extent * k / n, 3) for k in range(1, n)]
                + [lo + extent])

    out = []
    for name, c, s in parts:
        nx = int((s[0] - _EPS) // tile) + 1 if s[0] > tile + _EPS else 1
        ny = int((s[1] - _EPS) // tile) + 1 if s[1] > tile + _EPS else 1
        if nx == 1 and ny == 1:
            out.append((name, c, s))
            continue
        xe = edges(c[0] - s[0] / 2.0, s[0], nx)
        ye = edges(c[1] - s[1] / 2.0, s[1], ny)
        for j in range(ny):
            for i in range(nx):
                out.append((f"{name}_t{j}_{i}",
                            (round((xe[i] + xe[i + 1]) / 2.0, 6),
                             round((ye[j] + ye[j + 1]) / 2.0, 6), c[2]),
                            (round(xe[i + 1] - xe[i], 6),
                             round(ye[j + 1] - ye[j], 6), s[2])))
    return out


#: Facade relief defaults. Overridable per style through the genome's params,
#: which is where the VARIATION belongs -- one rhythm on every wall of every
#: building is the failure mode this replaces, not a goal.
RELIEF = {
    "bay": 2.4,        # target pier-to-pier spacing, metres
    "pier": 0.14,      # width of the full-depth strip between bays
    "reveal": 0.05,    # how far each field is recessed, PER FACE
    "base": 0.45,      # plinth height, full depth
    "cap": 0.12,       # cornice height, full depth
    "min_field": 0.40,  # narrower than this and a bay is noise, not rhythm
}


def relief_parts(w: float, d: float, h: float, style: dict | None = None):
    """A solid wall's visual geometry: plinth, piers, RECESSED fields, cap.

    WHY THIS EXISTS, and why it is not a cover. Facade articulation used to be
    additive -- Patina emitted ``panel_field`` and ``pilaster`` orders and Zoo
    built each as a thin box standing PROUD of the wall: 1.2 cm for a panel,
    5 cm for a pilaster. A module's collider is built from the same slab as its
    visual, so the wall's collision volume ends exactly at the wall's face, and
    anything proud of that face is by construction non-collision geometry
    sitting in space a body can occupy. That is the standing rule -- no
    dressing in walkable space -- broken by the shape of the solution, not by
    a placement mistake.

    It cannot be fixed by aiming the covers better. Pointing them into the
    building put 546 panel fields inside rooms; pointing them out put the same
    546 into the gaps between buildings, which Lot makes into routes. Both are
    walkable. There is no third direction.

    So the relief is SUBTRACTIVE and lives inside the module. The plinth, the
    piers and the cap span the full authored depth; only the fields between
    them are pulled back, and they are pulled back on BOTH faces. Three
    consequences, all of them the point:

      * the outer bbox is still exactly ``(w, d, h)`` -- the plinth alone
        guarantees it -- so fit-to-exact-dims passes as before;
      * nothing exists outside the collision volume, so the rule cannot be
        violated rather than merely being checked for;
      * the module needs no idea which face is the street. A one-sided carve
        would need one, and the module is instanced at slots of every
        orientation, so it would be the outward-direction bug again, this time
        baked into the mesh where no per-slot transform can flip it.

    Returns the same ``(name, center, size)`` shape as :func:`slab_parts`.
    Collision is NOT derived from this -- the caller keeps using the solid
    slab, so the collider is unchanged from every previous build.
    """
    s = dict(RELIEF)
    s.update(style or {})
    hw, hh = w / 2.0, h / 2.0
    base = _clamp(float(s["base"]), 0.0, h * 0.35)
    cap = _clamp(float(s["cap"]), 0.0, h * 0.15)
    fh = h - base - cap
    pier = float(s["pier"])
    reveal = _clamp(float(s["reveal"]), 0.0, d * 0.35)
    n = max(1, int(round(w / float(s["bay"]))))
    bw = w / n
    # n bays need n+1 piers, and the two end piers are FLUSH with the module
    # edges rather than centred on them -- a pier centred on x = -w/2 would
    # hang half its width into the neighbouring module and double up at every
    # seam, which is the 6 cm overhang the old pilaster had at 225 slots.
    if fh <= _EPS or bw - pier < float(s["min_field"]) or reveal <= _EPS:
        return [("Panel", (0.0, 0.0, 0.0), (round(w, 6), round(d, 6),
                                            round(h, 6)))]

    parts = []
    if base > _EPS:
        parts.append(("Base", (0.0, 0.0, -hh + base / 2.0),
                      (round(w, 6), round(d, 6), round(base, 6))))
    if cap > _EPS:
        parts.append(("Cap", (0.0, 0.0, hh - cap / 2.0),
                      (round(w, 6), round(d, 6), round(cap, 6))))

    fz = -hh + base + fh / 2.0
    fd = d - 2.0 * reveal
    edges = [-hw + bw * i for i in range(n + 1)]
    for i, x in enumerate(edges):
        if i == 0:
            cx, pw = -hw + pier / 2.0, pier
        elif i == n:
            cx, pw = hw - pier / 2.0, pier
        else:
            cx, pw = x, pier
        parts.append(("Pier_%d" % i, (round(cx, 6), 0.0, round(fz, 6)),
                      (round(pw, 6), round(d, 6), round(fh, 6))))
    for i in range(n):
        x0 = (-hw + pier) if i == 0 else edges[i] + pier / 2.0
        x1 = (hw - pier) if i == n - 1 else edges[i + 1] - pier / 2.0
        if x1 - x0 <= _EPS:
            continue
        parts.append(("Field_%d" % i,
                      (round((x0 + x1) / 2.0, 6), 0.0, round(fz, 6)),
                      (round(x1 - x0, 6), round(fd, 6), round(fh, 6))))
    return parts


def parts_bbox(parts):
    """Outer (min_xyz, max_xyz) AABB across a list of slab_parts boxes."""
    lo = [1e9, 1e9, 1e9]
    hi = [-1e9, -1e9, -1e9]
    for _name, c, s in parts:
        for i in range(3):
            lo[i] = min(lo[i], c[i] - s[i] / 2.0)
            hi[i] = max(hi[i], c[i] + s[i] / 2.0)
    return tuple(lo), tuple(hi)


def collision_boxes(parts):
    """((min_xyz),(max_xyz)) per solid box — the passable void gets none, so
    doorways / windows / breaches are walk/shoot-through."""
    out = []
    for _name, c, s in parts:
        lo = tuple(c[i] - s[i] / 2.0 for i in range(3))
        hi = tuple(c[i] + s[i] / 2.0 for i in range(3))
        out.append((lo, hi))
    return out
