"""street_tree recipe: a kerb tree in a grate -- trunk, crown, grate.

Roadmap 153, the waiting places: "a tree in a kerb grate (the contract's
alpha-cutout foliage, the first species that needs it)". A bark cylinder
for the trunk, a crown of CUTOUT CARDS -- four vertical planes crossed at
45 degrees, one foliage tile each, wearing the `foliage` kind, a
leaf-cluster pack whose alpha is tested rather than blended (Pixelcoat
0.32.0, `materials._textured`), so the crown reads as leaf mass with sky
between -- and a flat iron grate at grade. Without a foliage pack the
cards are flat green planes, which is the honest state of an unskinned
crown.

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

import math

from ..bpylayer import geometry, materials

TRUNK_D = 0.30
GRATE = 1.2
GRATE_T = 0.03
CARD_T = 0.02


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0

    def part(bm, name, texel=1.2, part_bevel=None, smooth=True, uv_offset=(0.0, 0.0, 0.0)):
        obj = geometry.bm_to_object(
            bm, name, collection, bevel=bevel if part_bevel is None else part_bevel,
            texel=texel, rng=rng, wear=wear, uv_offset=uv_offset,
            **({} if smooth else {"smooth_angle": 0.0}))
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

    # crown: the upper 0.6 of the height as CARDS. Four vertical planes
    # through the axis at 0, 45, 90 and 135 degrees, the crown's full
    # height; the axis-aligned pair is the slot's width and the diagonal
    # pair is that times root two, so every card's extents are the slot's
    # (w, d). ONE TILE PER CARD: the foliage pack is authored at
    # `meters_per_tile` = the card's width with its cutout faded to
    # nothing inside an ellipse centred on the tile's corner, and the
    # crown's UVs are cube-projected about the crown's own centre
    # (`uv_offset`), so each card's UVs run -0.5..0.5 across one tile and
    # the card's edge is the canopy's, not a hard line. Cold run 9031's
    # frames: the tile repeated 2.7 times across the card and the two
    # horizontal cards read as shelves; both gone. A card is a 2 cm box:
    # two faces, no culling.
    crown_h = h * 0.6
    crown_c = h / 2.0 - crown_h / 2.0
    bm = geometry.new_bm()
    span = max(w, d)
    for k in range(4):
        length = span if k % 2 == 0 else span * math.sqrt(2.0)
        verts = geometry.add_box(bm, (0.0, 0.0, crown_c), (length, CARD_T, crown_h))
        geometry.place(verts, (0.0, 0.0, 0.0), rot_z=math.radians(45.0 * k))
    crown = part(bm, "StreetTree_Crown", texel=1.0, part_bevel=0.0, smooth=False,
                 uv_offset=(0.0, 0.0, -crown_c))

    bark = materials.make_material(
        f"M_StreetTree_{plan['material']}", plan["color"], plan["material"])
    leaf = materials.make_material("M_StreetTree_foliage",
                                   [0.30, 0.45, 0.20], "foliage")
    iron = materials.make_material("M_StreetTree_metal_bare", [0.2, 0.2, 0.21],
                                   "metal_bare")
    materials.assign([trunk], bark)
    materials.assign([crown], leaf)
    materials.assign([grate], iron)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
