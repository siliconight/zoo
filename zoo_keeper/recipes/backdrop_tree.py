"""backdrop_tree recipe: the tree of the parkland and roadside backdrop recipes (Zoo 1.97.0,
roadmap 228 step F).

A trunk that flares at the foot and forks into three limbs, under a crown of seven overlapping
lobes at different heights: the limbs' three, a top lobe on the axis, and three fillers between
them, lower. The walker, on cold run 9227's parkland, of 1.96.0's trunk box under one faceted
sphere: "those trees in the distance are a little lazy imo (giant lolipops vs. trees)". The form
follows the slot's proportions (`core.backdrop_forms.tree_form`): a squat slot is a broad oak, a
tall one a vase-shaped elm, between them a round maple. Bark on the trunk and the limbs, the
style's vegetation on the lobes, two materials and two objects, as before; the sum is fitted to
the slot exactly (`geometry.fit_to`), so the extents are the slot's whatever the lobes do. Not a
street tree: those are grown branch by branch at two thousand triangles for a kerb the player
walks past; this one stands behind the fence twenty to ninety metres off, in a MultiMesh. Centre
pivot, bottom at -h/2, no collision.
"""
from __future__ import annotations

import bmesh
from mathutils import Matrix, Vector

from ..bpylayer import geometry, materials
from ..core import backdrop_forms as BF

CONE_SEG = 8


def _cone(bm, a, b, r0, r1):
    """A truncated cone from point a (radius r0) to point b (radius r1)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    length = d.length
    verts = geometry.add_cylinder(bm, (0.0, 0.0, 0.0), r0, length, segments=CONE_SEG,
                                  axis="Z", cap=True, radius_top=r1)
    rot = Vector((0.0, 0.0, 1.0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    mat = Matrix.Translation((a + b) * 0.5) @ rot
    bmesh.ops.transform(bm, matrix=mat, verts=verts)
    return verts


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    wear = plan["wear"]
    rng = streams.stream("wear")
    seed = int(rng.random() * 360)
    tree = BF.tree_plan(w, h, seed)

    bm = geometry.new_bm()
    foot, top, rf, rt = tree["trunk"]
    _cone(bm, foot, top, rf, rt)
    for root, tip, r0, r1 in tree["limbs"]:
        _cone(bm, root, tip, r0, r1)
    trunk = geometry.bm_to_object(bm, "BackdropTree_Trunk", collection, bevel=0.0,
                                  texel=1.0, rng=rng, wear=wear)
    materials.assign([trunk], materials.make_material(
        f"M_BackdropTree_{plan['material']}", plan["color"], plan["material"]))

    bm = geometry.new_bm()
    for centre, radii in tree["lobes"]:
        verts = geometry.add_ellipsoid(bm, centre, radii, u_seg=BF.TREE_LOBE_U, v_seg=BF.TREE_LOBE_V)
        geometry.displace_lobes(bm, verts, rng, radii[0] * BF.TREE_LOBE_WOBBLE, lobes=3,
                                center=centre)
    crown = geometry.bm_to_object(bm, "BackdropTree_Crown", collection, bevel=0.0,
                                  texel=0.6, rng=rng, wear=wear * 0.5)
    materials.assign([crown], materials.make_material(
        "M_BackdropTree_vegetation", BF.TREE_LEAF, "vegetation"))

    # THE SLOT IS EXACT AND THE LOBES ARE NOT: the plan's lobes reach about the
    # width and the foot and the top lobe stand at -h/2 and h/2; the fit makes
    # every extent the slot's and keeps the foot on the ground, the union being
    # centred where the frame is.
    geometry.fit_to([trunk, crown], (w, d, h))
    return {"objects": [trunk, crown], "collision_boxes": [], "attachments": {}}
