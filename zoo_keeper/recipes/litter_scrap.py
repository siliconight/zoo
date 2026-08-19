"""litter_scrap recipe: flat crumpled scraps — Layer 3 litter.

The guide places trash "against walls or traffic boundaries", so this species
exists to be a seam and edge marker rather than a field scatter. It is the
flattest thing in the kit: the genome caps height at 0.03 m, which is inside
`FLUSH_M = 0.02`-adjacent territory in `lot/site_steps.py` and nowhere near the
0.117 m `unassisted_step_max`, so it cannot even be argued about.

A scrap is a thin plate with its TOP surface displaced only -- a crumple, not a
lump. Displacing both faces would thicken it into a pebble with the wrong
material.

SHAPE, SECOND PASS. This was the best of the first kit, and the reason is worth
recording because it is the whole diagnosis in one species: crumpling the top
verts of a box was the ONLY operation in the first four recipes that produced
non-coplanar faces, so it was the only one whose silhouette actually moved.
It was still working with four corners, though -- one quad, four vertices, and
therefore exactly one fold. Subdividing the plate first gives the crumple
interior vertices to work with, so a scrap can fold more than once; measured,
that is the difference between 4 facing directions and enough to read as paper.
The cost is small because the plate is quads and it starts at 24 triangles
against a 200 budget.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")

    count = max(1, int(plan["params"].get("scraps", 2)))
    crumple = float(plan["params"].get("crumple", 0.55))
    # One cut turns the plate's 4 corners into 9 vertices, so the crumple has
    # somewhere to fold. Two is affordable here and reads as tighter creasing.
    cuts = max(0, int(plan["params"].get("cuts", 1)))

    bm = geometry.new_bm()
    for i in range(count):
        f = 0.5 + rng.random() * 0.5
        sx, sy = w * f, d * f
        verts = geometry.add_box(bm, (0.0, 0.0, 0.0), (sx, sy, h))
        verts = geometry.subdivide(bm, verts, cuts)
        top = [v for v in verts if v.is_valid and v.co.z > 0.0]
        for v in top:
            v.co.z += rng.random() * h * crumple
            v.co.x += (rng.random() * 2.0 - 1.0) * sx * 0.12
            v.co.y += (rng.random() * 2.0 - 1.0) * sy * 0.12
        # A scrap lies ON the surface; the base was already flat, this just
        # guarantees the subdivision did not leave it wavy.
        base_z = geometry.flatten_base(verts, tol_frac=0.05)
        ox = (rng.random() * 2.0 - 1.0) * w * 0.6
        oy = (rng.random() * 2.0 - 1.0) * d * 0.6
        geometry.place(verts, (ox, oy, -base_z),
                       rot_z=rng.random() * 6.2831853)

    scraps = geometry.bm_to_object(bm, "Dress_LitterScrap", collection,
                                   bevel=bevel, texel=10.0, rng=rng, wear=wear)
    materials.assign([scraps], materials.make_material(
        f"M_Litter_{plan['material']}", plan["color"], plan["material"]))

    return {"objects": [scraps], "collision_boxes": [], "attachments": {}}
