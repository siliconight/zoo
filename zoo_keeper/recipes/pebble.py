"""pebble recipe: a few small stones sitting on a surface — Layer 3 micro relief.

WHY THIS EXISTS. `docs/SURFACE_DRESSING.md` defines Layer 3 as collisionless
detail scattered over an assembled site, and Zoo shipped fifty species with
none of them in that layer: no grass, pebbles, rubble, litter, leaves or roots.
Nothing could be placed because nothing existed to place. This is the first of
four.

HEIGHT IS THE CONTRACT, NOT A STYLE CHOICE. The genome caps height at 0.10 m,
under the 0.117 m `unassisted_step_max` derived in `lot/site_steps.py` for this
stack's 0.4 m capsule. Below that a body steps over the object anyway, so
passing through it is not a visible lie; above it the engine calls the contact
a WALL and walking through instead is the "believable but false traversal
promise" the guide forbids. The whole first kit is deliberately micro-band, so
every placement is unconditionally legal and the traversed-space rule is never
the thing under test on the first pass.

NO COLLISION, BY CONSTRUCTION. `collision_boxes` is empty and the genome says
`"collision": false`. Zoo already raises ZOO_DRESSING_HAS_COLLISION as a
blocker for a dressing asset that declares collision; this species cannot trip
it because it never builds one.

SHAPE, SECOND PASS. The first version drew width, depth and height
independently and jittered the vertices of a 6x4 ellipsoid. Measured with
`tools/shape_metrics.py`, that gave b/a = 0.97 (a ball in plan), 12 distinct
facing directions, and `base_contact_ratio` 0.000 -- it was a lumpy sphere
hovering over the floor, and no amount of extra jitter could have fixed it,
because jitter moves vertices and the silhouette is made of faces. Three
changes, each answering one measurement:

  - `zingg_radii` draws the three extents as a PROPORTION rather than
    independently, so the population lands where real gravel lands (mostly
    blade and disc) instead of defaulting to equant.
  - `displace_lobes` adds a few broad bulges along the vertex normals, which
    moves the silhouette; per-vertex jitter only roughens the surface.
  - `flatten_base` shaves the underside so the stone has a footprint, then it
    is sunk by a fraction of that so it reads as sitting IN the ground rather
    than balanced on it.

The bevel is deliberately 0 here: on this species it was spending roughly two
thirds of the triangle budget on edges that carry no silhouette at two metres,
and those triangles buy more shape as facets.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")

    count = max(1, int(plan["params"].get("stones", 3)))
    facets_u = int(plan["params"].get("facets_u", 8))
    facets_v = int(plan["params"].get("facets_v", 5))
    # A stone half-buried reads as part of the ground rather than dropped on
    # it -- but the flat facet, not the burial, is what sells the contact, so
    # this is now a shallow tuck under the floor plane rather than a third of
    # the stone. It also keeps the footprint from being coplanar with the
    # floor it sits on, which is where z-fighting comes from.
    sink = float(plan["params"].get("sink", 0.15))
    lobes = int(plan["params"].get("lobes", 3))

    bm = geometry.new_bm()
    for i in range(count):
        # Deterministic spread and size from the one stream, as gold_bar and
        # cash_stack do -- a second named stream is not an attested API here.
        f = 0.55 + rng.random() * 0.45
        a, b, c = geometry.zingg_radii(rng, w * f)
        c = min(c, h)                          # the genome's height cap wins
        verts = geometry.add_ellipsoid(bm, (0.0, 0.0, 0.0),
                                       (a / 2.0, b / 2.0, c / 2.0),
                                       u_seg=facets_u, v_seg=facets_v)
        geometry.displace_lobes(bm, verts, rng, min(a, b, c) * 0.30,
                                lobes=lobes, sharpness=1.5, grain=0.25)
        base_z = geometry.flatten_base(verts, tol_frac=0.16)
        ox = (rng.random() * 2.0 - 1.0) * w * 0.5
        oy = (rng.random() * 2.0 - 1.0) * d * 0.5
        geometry.place(verts, (ox, oy, -base_z - c * sink),
                       rot_z=rng.random() * 6.2831853)

    stones = geometry.bm_to_object(bm, "Dress_Pebble", collection,
                                   bevel=bevel, texel=6.0, rng=rng, wear=wear)
    materials.assign([stones], materials.make_material(
        f"M_Pebble_{plan['material']}", plan["color"], plan["material"]))

    return {"objects": [stones], "collision_boxes": [], "attachments": {}}
