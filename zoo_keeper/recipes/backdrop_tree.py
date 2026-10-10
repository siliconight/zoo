"""backdrop_tree recipe: the tree of the parkland and roadside backdrop recipes (Zoo 1.96.0,
roadmap 228).

A trunk and one faceted crown, the edge menu's mockup's shape, for a belt that stands behind the
fence twenty to forty metres off and is composed as a few MultiMeshes. Not a street tree: those
are grown branch by branch at two thousand triangles for a kerb the player walks past. Bark on the
trunk and the style's vegetation on the crown, two materials; the crown's twelve facets put a
vertex on both axes so the extents are the slot's. `core.backdrop_forms.tree_parts` holds the
proportions. Centre pivot, bottom at -h/2, no collision.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import backdrop_forms as BF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    h = plan["dimensions"]["height"]
    wear = plan["wear"]
    rng = streams.stream("wear")
    parts = BF.tree_parts(w, h)
    (tc, ts) = parts["trunk"]
    bm = geometry.new_bm()
    geometry.add_box(bm, tc, ts)
    trunk = geometry.bm_to_object(bm, "BackdropTree_Trunk", collection, bevel=0.0,
                                  texel=1.0, rng=rng, wear=wear)
    materials.assign([trunk], materials.make_material(
        f"M_BackdropTree_{plan['material']}", plan["color"], plan["material"]))
    (cc, radii) = parts["crown"]
    bm = geometry.new_bm()
    geometry.add_ellipsoid(bm, cc, radii, u_seg=BF.TREE_U_SEG, v_seg=BF.TREE_V_SEG)
    crown = geometry.bm_to_object(bm, "BackdropTree_Crown", collection, bevel=0.0,
                                  texel=0.6, rng=rng, wear=wear * 0.5)
    materials.assign([crown], materials.make_material(
        "M_BackdropTree_vegetation", BF.TREE_LEAF, "vegetation"))
    return {"objects": [trunk, crown], "collision_boxes": [], "attachments": {}}
