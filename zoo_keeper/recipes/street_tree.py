"""street_tree recipe: a kerb tree in a grate -- trunk, crown, grate.

Roadmap 153, the waiting places: "a tree in a kerb grate (the contract's
alpha-cutout foliage, the first species that needs it)". This is the
honest first state of one: a bark cylinder for the trunk, a crown that is
a faceted volume in the vegetation grammar rather than cutout cards --
the cards are the drawing this file is waiting for -- and a flat iron
grate at grade.

WHAT COLLIDES, AND WHY ONLY THAT. The slot is the crown's footprint
(w x d) by the tree's height, because that is the space the tree takes;
but a body walks under a crown and bumps a trunk, so the collision box is
the trunk alone. Lot draws the greybox box for this slot at the GRATE's
footprint (`site_furniture.FOOTPRINT`), not the crown's, so the navmesh
carves the column a body meets and not the canopy it walks under; the
greybox over-blocks the trunk by the grate's margin and never under-blocks
it. Centre pivot like every module: z runs -h/2 .. +h/2.

Proportions: trunk 0.3 m across up to 0.4 of the height; crown the upper
0.6 of the height at the slot's width, tapered top and bottom so it reads
as a canopy and not a crate; grate 1.2 m square and 0.03 m thick.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

TRUNK_D = 0.30
GRATE = 1.2
GRATE_T = 0.03


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0

    def part(bm, name, texel=1.2, part_bevel=None):
        obj = geometry.bm_to_object(
            bm, name, collection, bevel=bevel if part_bevel is None else part_bevel,
            texel=texel, rng=rng, wear=wear)
        objs.append(obj)
        return obj

    # grate at grade
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + GRATE_T / 2.0),
                     (min(GRATE, w), min(GRATE, d), GRATE_T))
    grate = part(bm, "StreetTree_Grate", part_bevel=0.0)

    # trunk: grade to 0.4 h, and the only collider
    trunk_top = z0 + h * 0.4
    trunk_h = trunk_top - z0
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + trunk_h / 2.0),
                          TRUNK_D / 2.0, trunk_h, segments=8,
                          radius_top=TRUNK_D * 0.4)
    trunk = part(bm, "StreetTree_Trunk")
    cboxes.append(((-TRUNK_D / 2.0, -TRUNK_D / 2.0, z0),
                   (TRUNK_D / 2.0, TRUNK_D / 2.0, trunk_top)))

    # crown: the upper 0.6 of the height, its full width at its waist --
    # two frustums, the lower widening up to (w, d) and the upper narrowing
    # from it, so the silhouette is a canopy and the extents are the slot's
    crown_h = h * 0.6
    crown_lo = h / 2.0 - crown_h
    waist = crown_lo + crown_h * 0.4
    bm = geometry.new_bm()
    lower = geometry.add_box(bm, (0.0, 0.0, (crown_lo + waist) / 2.0),
                             (w, d, waist - crown_lo))
    geometry.taper_z(lower, 1.0, 0.7)
    upper = geometry.add_box(bm, (0.0, 0.0, (waist + h / 2.0) / 2.0),
                             (w, d, h / 2.0 - waist))
    geometry.taper_z(upper, 0.5, 1.0)
    crown = part(bm, "StreetTree_Crown", texel=0.6, part_bevel=0.0)

    bark = materials.make_material(
        f"M_StreetTree_{plan['material']}", plan["color"], plan["material"])
    leaf = materials.make_material("M_StreetTree_vegetation",
                                   [0.22, 0.38, 0.16], "vegetation")
    iron = materials.make_material("M_StreetTree_metal_bare", [0.2, 0.2, 0.21],
                                   "metal_bare")
    materials.assign([trunk], bark)
    materials.assign([crown], leaf)
    materials.assign([grate], iron)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
