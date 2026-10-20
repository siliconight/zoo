"""hole_edge recipe: the torn edge round a hole in a floor (Zoo 1.114.0; the factory's roadmap 265).

The walker, 2026-10-19: a hole should be "clear to the player" and have "some reason other than a
perfectly cut square". Deli Counter cuts its drop holes as rectangles, and the rectangle stays the
collider and the drop's route; this is what a person sees instead. Every decision is
`core.hole_forms.edge_plan`, which is pure and tested; this file only turns it into meshes.

- THE COLLAR: the floor's underlayer where the finish is torn back from the hole -- one ring of
  shared vertices, its outer edge jagged across the floor, its inner edge never short of the cut
  (at least 6 mm past it, so no face of it lies on the slab's or the skin's cut planes) and, in
  teeth, well past it, sagging where it juts. It stands `TOP` above the floor skin and sinks
  `SKIRT` into it, the way a resting floater does.
- THE JOIST ENDS the cut went through, in the slab's thickness on the two sides that cross them,
  proud of the cut face by their own ragged amounts; in `broken`, some hang from the face. Between
  them the floor's dark cavity, and on the other two sides the rim joist's face, so the opening's
  walls read as a floor broken through and not a slab sawn.
- THE HANGERS under the ceiling: tile shards and a bent grid tee (`cut`), plaster and lath
  (`broken`), each hinged at the ceiling's edge and hanging into the opening -- never further down
  than the slot's bottom, the lowest exactly to it.
- THE CAVITY: under the ceiling, a jagged ring where it is broken back from the hole -- one-sided,
  facing down, `PROUD` below the ceiling skin -- dark where a drop ceiling lost its tiles, lath
  where plaster fell.

NOTHING HERE COLLIDES: a body falls through the rectangle Deli Counter cut, past every piece of
this. The bounds are the slot's by construction (the collar reaches each face at one sample, the
lowest hanger reaches the bottom), so nothing is fitted after. One object a colour, one material a
kind; Zoo's export packs them a material each.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials
from ..core import hole_forms as HF


def _ring(bm, ring, z_top, z_bot_out, thick):
    """The collar: quads between consecutive samples, top, bottom and both walls; returns verts."""
    n = len(ring)
    vt_o, vb_o, vt_i, vb_i = [], [], [], []
    for ox, oy, ix, iy, droop in ring:
        vt_o.append(bm.verts.new((ox, oy, z_top)))
        vb_o.append(bm.verts.new((ox, oy, z_bot_out)))
        top_i = z_top - droop
        vt_i.append(bm.verts.new((ix, iy, top_i)))
        vb_i.append(bm.verts.new((ix, iy, top_i - thick)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vt_o[i], vt_o[j], vt_i[j], vt_i[i]))       # top
        bm.faces.new((vb_o[j], vb_o[i], vb_i[i], vb_i[j]))       # bottom
        bm.faces.new((vb_o[i], vb_o[j], vt_o[j], vt_o[i]))       # outer wall
        bm.faces.new((vt_i[i], vt_i[j], vb_i[j], vb_i[i]))       # inner wall
    bm.normal_update()
    return vt_o + vb_o + vt_i + vb_i


def _cavity(bm, cavity, z):
    """The broken-back ceiling: a one-sided strip between the jagged outer line and the hole's edge,
    `PROUD` below the ceiling skin. Wound to face down; `_face_down` makes sure of it after the
    finish, whose normal pass may turn an open strip either way."""
    n = len(cavity)
    vo = [bm.verts.new((ox, oy, z)) for ox, oy, _ix, _iy in cavity]
    vi = [bm.verts.new((ix, iy, z)) for _ox, _oy, ix, iy in cavity]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vo[i], vi[i], vi[j], vo[j]))


def _face_down(obj):
    """Reverse an object's faces if they face up on the whole: the cavity is seen only from below."""
    import bmesh
    me = obj.data
    if sum(p.normal.z for p in me.polygons) <= 0.0:
        return False
    b = bmesh.new()
    b.from_mesh(me)
    bmesh.ops.reverse_faces(b, faces=b.faces[:])
    b.to_mesh(me)
    b.free()
    me.update()
    return True


def _rod(bm, p0, p1, r, segments=6):
    """A cylinder from point `p0` to `p1`: a reinforcing bar."""
    from mathutils import Matrix, Vector
    a, b = Vector(p0), Vector(p1)
    axis = b - a
    verts = geometry.add_cylinder(bm, (0.0, 0.0, 0.0), r, axis.length, segments=segments)
    rot = Vector((0.0, 0.0, 1.0)).rotation_difference(axis.normalized()).to_matrix().to_4x4()
    m = Matrix.Translation((a + b) / 2.0) @ rot
    for v in verts:
        v.co = m @ v.co
    return verts


def _rotate_x(verts, pivot, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    for v in verts:
        y, z = v.co.y - pivot[1], v.co.z - pivot[2]
        v.co.y = pivot[1] + y * c - z * s
        v.co.z = pivot[2] + y * s + z * c


def _hanger(bm, hx, hy, nx, ny, width, length, thick, angle_deg, z_hinge):
    """A plate hinged along the hole's edge at (hx, hy, z_hinge), reaching into the opening (along
    -normal) and turned `angle_deg` below the ceiling, its top face on the hinge line."""
    a = math.radians(angle_deg)
    # local frame: u into the opening, s along the edge, t down through the plate
    ux, uy = -nx, -ny
    sx, sy = -uy, ux
    pts = []
    # the plate runs along (cos a, -sin a) into the opening and down; its thickness along the
    # perpendicular (-sin a, -cos a). RETRACTED, kept: the first build offset the thickness along
    # (+sin a, -cos a), which is not perpendicular, so every shard was a sheared sliver |cos 2a|
    # of its thickness thick -- 1.4 mm of a 16 mm tile at 42 degrees -- found by the coincident-face
    # census as a plate's two faces 1.43 mm apart over its whole area.
    for s in (-width / 2.0, width / 2.0):
        for u in (0.0, length):
            for t in (0.0, thick):
                horiz = u * math.cos(a) - t * math.sin(a)
                down = u * math.sin(a) + t * math.cos(a)
                pts.append((hx + ux * horiz + sx * s, hy + uy * horiz + sy * s, z_hinge - down))
    vs = [bm.verts.new(p) for p in pts]
    # vs index: s(0/1)*4 + u(0/1)*2 + t(0/1)
    q = lambda s, u, t: vs[s * 4 + u * 2 + t]                      # noqa: E731
    for f in ((q(0, 0, 0), q(0, 1, 0), q(1, 1, 0), q(1, 0, 0)),   # top
              (q(0, 0, 1), q(1, 0, 1), q(1, 1, 1), q(0, 1, 1)),   # underside
              (q(0, 0, 0), q(0, 0, 1), q(0, 1, 1), q(0, 1, 0)),   # one side
              (q(1, 0, 0), q(1, 1, 0), q(1, 1, 1), q(1, 0, 1)),   # the other
              (q(0, 1, 0), q(0, 1, 1), q(1, 1, 1), q(1, 1, 0)),   # the free end
              (q(0, 0, 0), q(1, 0, 0), q(1, 0, 1), q(0, 0, 1))):  # the hinge end
        bm.faces.new(f)
    return vs


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    form = params.get("form", "auto")
    variant = int(params.get("variant", 0) or 0)
    rng = streams.stream("wear")
    wear, ambient = plan["wear"], plan.get("ambient", 0.0)
    ep = HF.edge_plan(w, d, h, form, variant)
    f = ep["frame"]
    broken, slab, plaster = ep["cause"] == "broken", ep["slab"], ep["plaster"]
    objs = []

    def finish(bm, name, kind, colour, tint=(1.0, 1.0, 1.0), bevel=0.0, texel=1.5):
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel, texel=texel, rng=rng,
                                    wear=wear, ambient=ambient)
        if tint != (1.0, 1.0, 1.0):
            geometry.tint_wear(obj, tint)
        materials.assign([obj], materials.make_material(f"M_HoleEdge_{kind}", colour, kind))
        objs.append(obj)
        return obj

    # THE BODY is the genome's material: the floor's structure (collar, joists, lath, the broken
    # cavity) is built of it; the ceiling's tile and plaster are what they are
    body = plan["material"]
    wood = HF.COLOURS["plywood"]
    # the collar
    bm = geometry.new_bm()
    _ring(bm, ep["ring"], h, f["zf"] - HF.SKIRT, HF.TOP + HF.SKIRT)
    if slab:
        # a slab's own edge, spalled: fresh concrete, lighter than the worn floor round it
        finish(bm, "HoleEdge_Collar", "concrete", HF.COLOURS["concrete_fresh"])
    else:
        finish(bm, "HoleEdge_Collar", body, wood,
               tint=tuple(a / b for a, b in zip(HF.COLOURS["floorboard"], wood)) if broken
               else (1.0, 1.0, 1.0))
    if ep["rebar"]:
        bm = geometry.new_bm()
        for x0, y0, z0, x1, y1, z1 in ep["rebar"]:
            _rod(bm, (x0, y0, z0), (x1, y1, z1), 0.008)            # a #5 bar, 16 mm
        finish(bm, "HoleEdge_Rebar", "metal", HF.COLOURS["rebar"], texel=2.0)

    # the joist ends, pitched about their top edge at the cut face where one hangs
    bm = geometry.new_bm() if ep["joists"] else None
    for cx, cy, cz, sx, sy, sz, pitch, _axis in ep["joists"]:
        verts = geometry.add_box(bm, (cx, cy, cz), (sx, sy, sz))
        if pitch:
            face_y = -f["hy"] if cy < 0 else f["hy"]
            _rotate_x(verts, (cx, face_y, cz + sz / 2.0), pitch)
    for kind, cx, cy, cz, sx, sy, sz in ep["walls"]:
        if kind == "rim":
            geometry.add_box(bm, (cx, cy, cz), (sx, sy, sz))
    if bm is not None:
        finish(bm, "HoleEdge_Joists", body, wood,
               tint=tuple(a / b for a, b in zip(HF.COLOURS["joist_old" if broken else "joist"], wood)),
               texel=1.2)

    # the hangers, by what they are
    groups = {}
    for hx, hy, nx, ny, width, length, thick, angle, kind in ep["hangers"]:
        groups.setdefault(kind, []).append((hx, hy, nx, ny, width, length, thick, angle))
    tile = HF.COLOURS["tile"]
    looks = {"tile": ("ceiling_tile", tile, (1.0, 1.0, 1.0)),
             "grid": ("ceiling_tile", tile, tuple(a / b for a, b in zip(HF.COLOURS["grid"], tile))),
             "plaster": ("plaster", HF.COLOURS["plaster"], (1.0, 1.0, 1.0)),
             "lath": (body, wood, tuple(a / b for a, b in zip(HF.COLOURS["lath"], wood)))}
    for kind in sorted(groups):
        bm = geometry.new_bm()
        for hx, hy, nx, ny, width, length, thick, angle in groups[kind]:
            _hanger(bm, hx, hy, nx, ny, width, length, thick, angle, f["zc"])
        mat_kind, colour, tint = looks[kind]
        finish(bm, f"HoleEdge_Hang_{kind}", mat_kind, colour, tint=tint, texel=1.0)

    # the floor cavity between the joist ends: dark, in a material this module already has
    dark = HF.COLOURS["cavity"]
    voids = [wl for wl in ep["walls"] if wl[0] == "void"]
    if voids:
        bm = geometry.new_bm()
        for _kind, cx, cy, cz, sx, sy, sz in voids:
            geometry.add_box(bm, (cx, cy, cz), (sx, sy, sz))
        if plaster:
            finish(bm, "HoleEdge_Voids", body, wood, tint=tuple(a / b for a, b in zip(dark, wood)))
        else:
            finish(bm, "HoleEdge_Voids", "ceiling_tile", tile,
                   tint=tuple(a / b for a, b in zip(dark, tile)))
    # the cavity under the ceiling: dark where tiles came out, lath where plaster fell
    bm = geometry.new_bm()
    _cavity(bm, ep["cavity"], f["zc"] - HF.PROUD)
    if plaster:
        cav = finish(bm, "HoleEdge_Cavity", body, wood,
                     tint=tuple(a / b for a, b in zip(HF.COLOURS["lath"], wood)), texel=0.8)
    else:
        cav = finish(bm, "HoleEdge_Cavity", "ceiling_tile", tile,
                     tint=tuple(a / b for a, b in zip(HF.COLOURS["cavity"], tile)), texel=0.8)
    _face_down(cav)

    print(f"[hole_edge] {w:.2f} x {d:.2f} x {h:.3f} form={ep['form']} variant={variant} "
          f"ring={len(ep['ring'])} joists={len(ep['joists'])} rebar={len(ep['rebar'])} "
          f"hangers={len(ep['hangers'])} "
          f"slab={f['thick']:.3f}")
    return {"objects": objs, "collision_boxes": [], "attachments": {}}
