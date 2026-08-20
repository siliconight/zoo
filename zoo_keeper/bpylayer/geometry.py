"""bmesh geometry helpers for Zoo recipes.

Design rules:
- bmesh + data API only; no context-dependent bpy.ops for geometry.
- UVs via deterministic cube projection (no smart_project / edit mode).
- Wear via a 'Wear' corner color attribute: concavity darkening + seeded
  noise scaled by the plan's wear value. Godot multiplies it into albedo
  when 'Use as Albedo' is enabled on the material.
"""
from __future__ import annotations

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

WEAR_LAYER = "Wear"


# --- primitives (operate on a shared bmesh) --------------------------------

def new_bm() -> bmesh.types.BMesh:
    return bmesh.new()


def add_box(bm, center, size):
    """Axis-aligned box. center/size are (x, y, z) in meters."""
    ret = bmesh.ops.create_cube(bm, size=1.0)
    verts = ret["verts"]
    mat = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector(size).to_4d())
    bmesh.ops.transform(bm, matrix=mat, verts=verts)
    return verts


def add_cylinder(bm, center, radius, depth, segments=14, axis="Z",
                 cap=True, radius_top=None):
    """Cylinder along +axis through center. radius_top != radius makes a
    truncated cone (cup / tapered limb)."""
    ret = bmesh.ops.create_cone(
        bm, cap_ends=cap, cap_tris=True, segments=segments,
        radius1=radius, radius2=(radius if radius_top is None else radius_top),
        depth=depth)
    verts = ret["verts"]
    rot = Matrix.Identity(4)
    if axis == "X":
        rot = Matrix.Rotation(1.5707963, 4, "Y")
    elif axis == "Y":
        rot = Matrix.Rotation(1.5707963, 4, "X")
    mat = Matrix.Translation(Vector(center)) @ rot
    bmesh.ops.transform(bm, matrix=mat, verts=verts)
    return verts


def add_hemisphere(bm, center, radius_x, radius_y, radius_z, segments=20):
    """Upper hemisphere shell (open bottom), squashed to per-axis radii."""
    ret = bmesh.ops.create_uvsphere(
        bm, u_segments=segments, v_segments=max(6, segments // 2),
        radius=1.0)
    verts = ret["verts"]
    geom = verts + [e for v in verts for e in v.link_edges] + \
        [f for v in verts for f in v.link_faces]
    cut = bmesh.ops.bisect_plane(
        bm, geom=list(set(geom)), dist=1e-5,
        plane_co=(0, 0, 0), plane_no=(0, 0, -1), clear_inner=True)
    keep = [v for v in bm.verts if v.is_valid and v in set(verts)] or \
        [v for v in bm.verts if v.is_valid]
    mat = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector((radius_x, radius_y, radius_z)).to_4d())
    bmesh.ops.transform(bm, matrix=mat, verts=keep)
    return keep


def add_ellipsoid(bm, center, radii, u_seg=10, v_seg=6):
    """Low-poly ellipsoid (faceted, PS1-flavored). radii = (rx, ry, rz).
    Keep u_seg/v_seg small for chunky facets."""
    ret = bmesh.ops.create_uvsphere(
        bm, u_segments=u_seg, v_segments=v_seg, radius=1.0)
    verts = ret["verts"]
    mat = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector(radii).to_4d())
    bmesh.ops.transform(bm, matrix=mat, verts=verts)
    return verts


def jitter_verts(verts, rng, amount):
    """Deterministic per-vertex offset — turns a clean primitive into an
    irregular organic lump. amount is the max offset in meters."""
    if amount <= 0:
        return verts
    for v in verts:
        v.co.x += (rng.random() * 2.0 - 1.0) * amount
        v.co.y += (rng.random() * 2.0 - 1.0) * amount
        v.co.z += (rng.random() * 2.0 - 1.0) * amount
    return verts


def place(verts, pos, rot_z=0.0, scale=1.0):
    """Scale -> Z-rotate -> translate a set of just-built verts. Used to
    lay scattered copies (piles) from core.scatter transforms."""
    m = (Matrix.Translation(Vector(pos))
         @ Matrix.Rotation(rot_z, 4, "Z")
         @ Matrix.Diagonal(Vector((scale, scale, scale)).to_4d()))
    for v in verts:
        v.co = m @ v.co
    return verts


def solidify(bm, thickness):
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=thickness)


#: A fold TIGHTER than this stays smooth; anything sharper becomes a hard
#: edge. 50 degrees is not a preference, it is arithmetic: `bevel_edges` runs
#: `segments=1`, so a chamfer on a 90-degree corner meets each neighbour at
#: exactly 45 degrees. The usual hard-surface default of 30 would mark every
#: chamfer sharp and the whole change would do nothing -- the bevels would
#: still read as facets, which is what they did before this existed.
SMOOTH_ANGLE_DEG = 50.0


def shade_by_angle(bm, angle_deg=SMOOTH_ANGLE_DEG):
    """Smooth shading with hard creases, decided per edge from the geometry.

    WHY THIS IS DONE ON THE BMESH. Blender 4.1 removed `mesh.use_auto_smooth`,
    and its replacement is an operator that adds a Smooth-by-Angle modifier.
    Zoo builds headless, deterministically, with no operators and no modifier
    stack, so neither is available. The same answer is computable directly:
    smooth every face, then mark an edge sharp when its two faces disagree by
    more than `angle_deg`.

    WHAT IT BUYS, in order of how visible it is:

      * Cylinders stop being faceted. `add_cylinder` runs 10-24 segments, so
        neighbouring side faces meet at 15-36 degrees and now blend, while the
        90-degree rim where the side meets the cap stays crisp. A 14-segment
        water tank was reading as a dodecagon.
      * Every bevel becomes a highlight roll-off instead of a facet, which is
        the entire reason `bevel_edges` exists. A bevel on a flat-shaded mesh
        buys geometry and no shading.
      * Box corners stay sharp, because 90 is well clear of the threshold.

    TRIANGLE COUNT IS UNCHANGED, which is what makes this safe to apply to
    every species at once: `validate.evaluate` checks `budgets.tris_lod0`, and
    nothing here adds a face. The exported VERTEX count usually falls, because
    smooth shading lets a corner share one normal where flat shading needed
    three.
    """
    limit = math.cos(math.radians(angle_deg))
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        faces = e.link_faces
        if len(faces) != 2:
            # A boundary or non-manifold edge has no second face to average
            # with. Leaving it hard is the honest answer; smoothing it would
            # blend against a normal that is not there.
            e.smooth = False
            continue
        e.smooth = faces[0].normal.dot(faces[1].normal) >= limit


def taper_z(verts, top_scale, bottom_scale=1.0):
    """Scale X and Y by height: `bottom_scale` at the lowest vertex,
    `top_scale` at the highest, linearly between.

    A frustum rather than a box, in one call, on whatever primitive is in
    hand. Manufactured things are rarely prisms -- a car's greenhouse narrows
    toward the roof, a bin tapers so it stacks, a dumpster's sides lean so the
    lid clears. Faking it by stacking two boxes leaves a 90-degree step that
    `shade_by_angle` correctly keeps sharp, so it reads as two boxes; a real
    taper leaves one continuous face.

    Operates on the verts `add_box` / `add_cylinder` return, matching
    `jitter_verts` and `flatten_base`. A flat set of verts (no height) is left
    alone rather than divided by zero.
    """
    if not verts:
        return
    zs = [v.co.z for v in verts]
    lo, hi = min(zs), max(zs)
    span = hi - lo
    if span <= 1e-9:
        return
    for v in verts:
        t = (v.co.z - lo) / span
        k = bottom_scale + (top_scale - bottom_scale) * t
        v.co.x *= k
        v.co.y *= k


def bevel_edges(bm, offset, segments=1, angle_min=0.6):
    """Bevel sharp edges (dihedral angle above angle_min radians)."""
    if offset <= 0:
        return
    edges = [e for e in bm.edges
             if len(e.link_faces) == 2
             and e.calc_face_angle(0.0) > angle_min]
    if edges:
        bmesh.ops.bevel(bm, geom=edges, offset=offset, segments=segments,
                        profile=0.7, affect="EDGES", clamp_overlap=True)


# --- shape helpers (Layer 3 surface dressing) -------------------------------
#
# WHY THESE EXIST.  `jitter_verts` moves the vertices of a primitive but not
# its FACES: jittering the 8 corners of a cube yields a parallelepiped, and
# jittering a 6x4 ellipsoid yields a lumpy ball with the same 24 facets it
# started with.  Measured on the first dressing kit with `tools/shape_metrics.py`,
# a rubble fragment needed only 7 distinct facing directions to account for 80%
# of its surface area -- it was still a box, however far the corners travelled.
# Irregularity is bounded above by face count, so the fix has to add faces
# (subdivide, fracture) rather than move the ones already there.
#
# Everything here takes the recipe's own `rng` so builds stay deterministic.

def subdivide(bm, verts, cuts=1):
    """Subdivide every edge whose ends are both in `verts`.

    Returns the enlarged vertex set, so a recipe can keep operating on "this
    chunk" while the shared bmesh holds several.
    """
    if cuts < 1:
        return list(verts)
    vs = set(verts)
    edges = [e for e in bm.edges if e.verts[0] in vs and e.verts[1] in vs]
    if not edges:
        return list(verts)
    ret = bmesh.ops.subdivide_edges(bm, edges=edges, cuts=cuts,
                                    use_grid_fill=True)
    # `use_grid_fill` REBUILDS the face interiors, which invalidates the
    # original corner vertices -- measured: all 8 verts of a subdivided cube
    # come back `is_valid == False`. Returning them produces a
    # "BMesh data of type BMVert has been removed" ReferenceError several
    # operations later, a long way from the cause. So the caller's list is
    # rebuilt from the op's own output and filtered, never merged blindly.
    out = {v for v in verts if v.is_valid}
    for key in ("geom", "geom_split", "geom_inner"):
        for g in ret.get(key, []):
            if isinstance(g, bmesh.types.BMVert) and g.is_valid:
                out.add(g)
    return list(out)


def _unit(rng):
    """Uniform random direction on the sphere (Marsaglia)."""
    while True:
        x, y = rng.random() * 2 - 1, rng.random() * 2 - 1
        s = x * x + y * y
        if s < 1.0:
            f = 2.0 * math.sqrt(1.0 - s)
            return Vector((x * f, y * f, 1.0 - 2.0 * s))


def displace_lobes(bm, verts, rng, amount, lobes=3, sharpness=2.0,
                   grain=0.25, center=(0.0, 0.0, 0.0)):
    """Two-frequency displacement along the vertex normal.

    LOW frequency: a few broad lobes, so the solid gains asymmetric bulges the
    way a worn stone does.  HIGH frequency: a small per-vertex grain on top.
    Uniform per-vertex noise alone (what `jitter_verts` does) is
    scale-invariant hash -- it roughens a surface without ever changing the
    silhouette, which is the thing that actually reads at two metres.

    `amount` is the low-frequency amplitude in metres; `grain` is the
    high-frequency amplitude as a fraction of it.
    """
    if amount <= 0 or not verts:
        return list(verts)
    bm.normal_update()
    c = Vector(center)
    dirs = [(_unit(rng), amount * (0.45 + rng.random() * 0.9))
            for _ in range(max(1, lobes))]
    for v in verts:
        if not v.is_valid:
            continue
        rel = v.co - c
        if rel.length > 1e-9:
            u = rel.normalized()
            off = 0.0
            for d, amp in dirs:
                w = u.dot(d)
                if w > 0.0:
                    off += amp * (w ** sharpness)
            off += (rng.random() * 2.0 - 1.0) * amount * grain
            n = v.normal if v.normal.length > 1e-9 else u
            v.co += n * off
    return list(verts)


def fracture(bm, verts, rng, cuts=3, near=0.30, far=0.85,
             center=(0.0, 0.0, 0.0), radius=1.0, steep=0.0):
    """Slice a solid with random half-space planes, capping each cut.

    This is what makes a fragment ANGULAR for real: broken rock IS the
    intersection of half-spaces, so cutting the solid produces flat facets of
    unequal size meeting at sharp dihedrals -- which is the read `rubble_frag`
    claims in its docstring and did not have.  Each cut adds one face, so the
    triangle cost is a few tris per cut and the caller controls it directly.

    `near`/`far` bound how far off `center` a cutting plane may sit, as a
    fraction of `radius`: a plane through the centre halves the fragment, so
    the useful range shaves corners instead.

    `steep` (0..1) biases the cutting planes toward VERTICAL.  A dressing
    fragment is a flat thing lying on the ground, so a randomly oriented plane
    usually shaves the top or the bottom, where nothing can see it -- measured,
    four random cuts left the plan-view outline 98% as boxy as the box it
    started from.  The cuts that change what you see from standing height are
    the ones that cut the plan silhouette, and those are the vertical ones.
    """
    verts = [v for v in verts if v.is_valid]
    c = Vector(center)
    for _ in range(max(0, cuts)):
        if len(verts) < 4:
            break
        no = _unit(rng)
        if steep > 0.0:
            no.z *= max(0.0, 1.0 - steep)
            if no.length < 1e-6:
                no = Vector((1.0, 0.0, 0.0))
            no.normalize()
        co = c + no * (radius * (near + rng.random() * max(0.0, far - near)))
        vs = set(verts)
        geom = list(vs)
        geom += [e for e in bm.edges if e.verts[0] in vs and e.verts[1] in vs]
        geom += [f for f in bm.faces if all(v in vs for v in f.verts)]
        res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7,
                                     plane_co=co, plane_no=no,
                                     clear_outer=True)
        cut = [g for g in res.get("geom_cut", []) if g.is_valid]
        if cut:
            bmesh.ops.contextual_create(bm, geom=cut)
        verts = [g for g in res.get("geom", []) if g.is_valid
                 and isinstance(g, bmesh.types.BMVert)]
        verts += [g for g in cut if isinstance(g, bmesh.types.BMVert)]
        verts = list(set(verts))
    return verts


def flatten_base(verts, tol_frac=0.15, plane_z=None):
    """Shave the underside flat, giving the solid a real footprint.

    An object with no contact face rests on a point or hovers, and both read as
    pasted on rather than lying there.  `tools/shape_metrics.py` reports this
    as `base_contact_ratio`, which measured 0.000 on the first pebble kit and
    0.001 on the first rubble kit -- neither species touched the ground it was
    dressing.

    Cuts at `lo + tol_frac * height` unless `plane_z` names an absolute plane.
    RETURNS the resulting base z, so the caller can translate the solid to sit
    on (or slightly under) the surface without measuring it again.
    """
    live = [v for v in verts if v.is_valid]
    if not live:
        return 0.0
    lo = min(v.co.z for v in live)
    hi = max(v.co.z for v in live)
    cut = (lo + (hi - lo) * tol_frac) if plane_z is None else plane_z
    for v in live:
        if v.co.z < cut:
            v.co.z = cut
    return cut


def zingg_radii(rng, base, equant=0.12, rod=0.22, disc=0.36):
    """Draw (rx, ry, rz) multipliers with the proportions real gravel has.

    Zingg (1935) classifies clasts by b/a and c/b at 2/3; measured river and
    talus populations sit mostly in blade and disc, and only rarely in equant.
    A generator that draws its three extents independently emits equant lumps
    far more often than nature does, and an equant lump is the single most
    "procedural" silhouette available.  The remaining probability after the
    three named classes is blade.
    """
    r = rng.random()
    if r < equant:
        ba, cb = rng.uniform(0.75, 0.95), rng.uniform(0.72, 0.92)
    elif r < equant + rod:
        ba, cb = rng.uniform(0.35, 0.62), rng.uniform(0.72, 0.95)
    elif r < equant + rod + disc:
        ba, cb = rng.uniform(0.72, 0.95), rng.uniform(0.28, 0.60)
    else:
        ba, cb = rng.uniform(0.40, 0.64), rng.uniform(0.32, 0.62)
    a = base
    b = a * ba
    c = b * cb
    return a, b, c


def add_blade(bm, base, height, width, thickness, bend=(0.0, 0.0),
              stations=4, taper=1.6, curl=0.0):
    """One tapered, CURVED blade of vegetation as a closed triangular prism.

    Built directly rather than from `add_cylinder`, because a cone has no
    stations along its length and therefore cannot bend: the first weed_tuft
    kit was five straight tapered spikes, which is why it rendered as paper
    slivers rather than grass.  A blade that reads has three properties a
    straight spike cannot have -- it curves, it is widest near the base, and it
    ends in a point.

    Solid, not a card: a crossed-quad blade is a single-sided plane, and this
    repo has already spent a session chasing one of those.  A card variant with
    an alpha cutout is the right answer for dense foliage later, per "coverage
    first, alpha cutouts second"; it is a different species, not this one.

    `bend` is the horizontal displacement at the tip, applied quadratically so
    the blade leaves the ground vertical and leans as it rises.  `curl` adds a
    cubic term, which is what makes a long blade fold over rather than lean.
    """
    stations = max(2, int(stations))
    ring = []
    for i in range(stations):
        t = i / float(stations)
        w = max(1e-5, width * 0.5 * (1.0 - t ** taper))
        th = max(1e-5, thickness * (1.0 - t * 0.75))
        z = height * t
        dx = bend[0] * t * t + curl * (t ** 3) * bend[0]
        dy = bend[1] * t * t + curl * (t ** 3) * bend[1]
        ring.append([bm.verts.new((base[0] + dx - w, base[1] + dy, base[2] + z)),
                     bm.verts.new((base[0] + dx + w, base[1] + dy, base[2] + z)),
                     bm.verts.new((base[0] + dx, base[1] + dy + th,
                                   base[2] + z))])
    tip = bm.verts.new((base[0] + bend[0] * (1.0 + curl),
                        base[1] + bend[1] * (1.0 + curl),
                        base[2] + height))
    for i in range(stations - 1):
        a, b = ring[i], ring[i + 1]
        for k in range(3):
            k2 = (k + 1) % 3
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    last = ring[-1]
    for k in range(3):
        bm.faces.new((last[k], last[(k + 1) % 3], tip))
    bm.faces.new((ring[0][2], ring[0][1], ring[0][0]))
    verts = [v for r in ring for v in r] + [tip]
    return verts


# --- UVs + wear -------------------------------------------------------------

def cube_project_uv(bm, texel=1.0, offset=(0.0, 0.0, 0.0)):
    """Deterministic box projection: each face mapped by dominant normal
    axis; UVs in world meters * texel so texture density is uniform.

    ``offset`` is added to each vertex before projecting. Zoo's kit modules are
    built in place at world scale, so their local coordinates ARE world ones
    and the default of zero is right for them. Dressing covers are built at the
    origin and transformed afterwards -- without an offset every cover projects
    from the same local box and samples the same patch of texture, which is
    what makes a wall of panel covers read as stamped tiles.
    """
    uv = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    ox, oy, oz = (float(offset[0]), float(offset[1]), float(offset[2]))
    for f in bm.faces:
        n = f.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for loop in f.loops:
            co = loop.vert.co.copy()
            co.x += ox; co.y += oy; co.z += oz
            if az >= ax and az >= ay:
                u, v = co.x, co.y
            elif ax >= ay:
                u, v = co.y, co.z
            else:
                u, v = co.x, co.z
            loop[uv].uv = (u * texel, v * texel)


def _ambient_tint(nz, strength):
    """Cool-from-above / warm-fill-below directional ambient for a face normal.

    ``nz`` is the face normal's up-component (-1 down .. +1 up). Upward faces
    catch cool sky light; downward faces catch warm bounce. Returns an RGB
    multiplier centred on white, scaled by ``strength`` — the "cool up / warm
    down" ambient painters use to give a form depth before any key light.

    Composes with Lux: Lux's sun/ambient does the *runtime* directional light,
    so this is deliberately a *gentle, view-independent form* cue baked into the
    module — the depth a surface has before any light hits it — not a second key
    light. Kept subtle (delco style uses 0.35) so it reads as form under Lux's
    banded diffuse rather than doubling the sun. On the texture side Patina's
    ``lux`` depth preset makes the matching choice: bake form (saturation),
    defer light-dependent colour (shadow tint, distance) to Lux.
    """
    t = (nz + 1.0) * 0.5                         # 0 down .. 1 up
    cool = (0.94, 0.97, 1.05)
    warm = (1.05, 0.98, 0.92)
    return tuple(1.0 + strength * ((c * t + w * (1.0 - t)) - 1.0)
                 for c, w in zip(cool, warm))


def wear_colors(bm, rng, wear, ambient=0.0):
    """Write wear (and optional directional ambient) into a corner color layer.

    Concave verts (avg edge angle) darken; seeded noise adds grime. With
    ``ambient`` > 0, a cool-up / warm-fill-down tint is multiplied in per face
    so modules read with soft form before any external light — the same
    depth-from-ambient cue Patina bakes on the texture side. ``ambient=0``
    keeps the original grayscale wear (byte-identical).
    """
    layer = (bm.loops.layers.color.get(WEAR_LAYER)
             or bm.loops.layers.color.new(WEAR_LAYER))
    vert_dark = {}
    for v in bm.verts:
        angles = [e.calc_face_angle_signed(0.0) for e in v.link_edges
                  if len(e.link_faces) == 2]
        concave = sum(-a for a in angles if a < 0) / max(1, len(angles))
        noise = rng.random()
        dark = min(1.0, concave * 1.5 + noise * 0.5) * wear
        vert_dark[v.index] = 1.0 - min(0.85, dark)
    bm.verts.index_update()
    for f in bm.faces:
        tint = _ambient_tint(f.normal.z, ambient) if ambient else (1.0, 1.0, 1.0)
        for loop in f.loops:
            g = vert_dark.get(loop.vert.index, 1.0)
            loop[layer][:] = (min(1.0, g * tint[0]), min(1.0, g * tint[1]),
                              min(1.0, g * tint[2]), 1.0)


# --- object plumbing ---------------------------------------------------------

def bm_to_object(bm, name, collection, finish=True, bevel=0.0,
                 texel=1.0, rng=None, wear=0.0, ambient=0.0,
                 uv_offset=(0.0, 0.0, 0.0)):
    """Finish a bmesh (bevel -> normals -> shading -> UVs -> wear) and link."""
    if finish:
        bevel_edges(bm, bevel)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        # AFTER recalc, because the decision reads face normals, and BEFORE
        # the UV projection, which does not care either way.
        shade_by_angle(bm)
        cube_project_uv(bm, texel, uv_offset)
        if rng is not None:
            wear_colors(bm, rng, wear, ambient=ambient)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    # Make the wear layer the ACTIVE colour attribute. `export.export_glb`
    # exports `export_vertex_color="ACTIVE"`, and nothing here ever set which
    # one that is -- so the wear written above could sit in the mesh and never
    # reach the file. Measured on a shipped dressing GLB: COLOR_0 was 1.0 on
    # every vertex of all 2098 covers, zero variation between covers AND zero
    # within a single cover, while the `rockay` style declares wear 0.29.
    #
    # `gather_facts` reports `has_wear_colors` by testing that the layer
    # EXISTS, which is why nothing caught it: the layer existed, it just was
    # not the one being exported.
    try:
        if WEAR_LAYER in mesh.color_attributes:
            mesh.color_attributes.active_color = mesh.color_attributes[WEAR_LAYER]
    except (AttributeError, KeyError, TypeError):
        pass          # older Blender colour-attribute API; wear still written
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def bounds_of(objs):
    """(min, max) world-space AABB across objects (transforms assumed
    identity — Zoo builds everything at world scale in-place)."""
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for obj in objs:
        for v in obj.data.vertices:
            co = v.co
            lo.x, lo.y, lo.z = min(lo.x, co.x), min(lo.y, co.y), min(lo.z, co.z)
            hi.x, hi.y, hi.z = max(hi.x, co.x), max(hi.y, co.y), max(hi.z, co.z)
    return lo, hi
