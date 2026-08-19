"""rubble_frag recipe: angular broken fragments — Layer 3 low debris.

The counterpart to `pebble`. A pebble is rounded and reads as natural; rubble
is ANGULAR and reads as damage, which is what makes it usable as an
environmental cause marker: the guide's rule 3 is "place rubble near damage",
and a fragment that looks water-worn says the wrong thing.

Height capped at 0.10 m in the genome, under `unassisted_step_max` 0.117 m
(`lot/site_steps.py`). Collisionless by construction; see pebble.py for why
that number and not another.

SHAPE, SECOND PASS -- AND THE REASON THE FIRST ONE COULD NOT WORK. The first
version built "jittered boxes rather than jittered ellipsoids ... the flat
faces and sharp dihedrals survive the low-poly budget and read as fracture".
The premise was right and the method could not deliver it: jittering the eight
corners of a cube produces a parallelepiped. It moves vertices, and the six
faces stay six planes. `tools/shape_metrics.py` measured the result at
`normal_regions_80 = 7` -- seven facing directions accounted for 80% of the
surface, which is a box however far the corners travelled -- with
`base_contact_ratio` 0.001, so it also did not touch the ground.

Real broken rock IS an intersection of half-spaces, so this builds it that way:
`geometry.fracture` slices the solid with random planes and caps each cut. Every
cut adds one flat facet of a size the cut chooses, meeting its neighbours at a
sharp dihedral, and the cost is a few triangles per cut -- so the angularity
the docstring always claimed is now the actual construction rather than a hoped
-for side effect of noise.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")

    count = max(1, int(plan["params"].get("chunks", 4)))
    # Cuts, not jitter. Three to five reads as fracture; below three the box
    # survives, above five the fragment tends toward a rounded polyhedron and
    # stops saying "damage".
    cuts = max(1, int(plan["params"].get("cuts", 4)))
    # Kept as a small weathering pass on top of the cuts: chipped corners, not
    # erosion. This is what `rough` now means.
    rough = float(plan["params"].get("rough", 0.30))

    bm = geometry.new_bm()
    for i in range(count):
        f = 0.35 + rng.random() * 0.65
        a, b, c = geometry.zingg_radii(rng, w * f)
        c = min(c, h)                          # the genome's height cap wins
        verts = geometry.add_box(bm, (0.0, 0.0, 0.0), (a, b, c))
        # `steep` matters more than `cuts`: measured over four seeds, four
        # randomly oriented cuts left the plan-view outline 86% as boxy as the
        # box (plan_hull_fill 0.856), because most random planes shave the top
        # or the bottom where a standing eye cannot see them. Biasing the same
        # four cuts toward vertical takes plan_hull_fill to 0.667 and doubles
        # plan_radial_cv, at one fewer triangle.
        verts = geometry.fracture(bm, verts, rng, cuts=cuts,
                                  near=0.10, far=0.50, steep=0.85,
                                  radius=max(a, b, c) * 0.5)
        geometry.displace_lobes(bm, verts, rng, min(a, b, c) * rough * 0.18,
                                lobes=2, sharpness=2.2, grain=0.6)
        base_z = geometry.flatten_base(verts, tol_frac=0.12)
        ox = (rng.random() * 2.0 - 1.0) * w * 0.55
        oy = (rng.random() * 2.0 - 1.0) * d * 0.55
        geometry.place(verts, (ox, oy, -base_z),
                       rot_z=rng.random() * 6.2831853)

    frags = geometry.bm_to_object(bm, "Dress_RubbleFrag", collection,
                                  bevel=bevel, texel=6.0, rng=rng, wear=wear)
    materials.assign([frags], materials.make_material(
        f"M_Rubble_{plan['material']}", plan["color"], plan["material"]))

    return {"objects": [frags], "collision_boxes": [], "attachments": {}}
