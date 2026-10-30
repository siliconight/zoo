"""wall_pilaster recipe: a flat stone pier on a civic wall -- plinth, shaft, cap (1.150.0, the factory's roadmap 324).

Minted 2026-10-30 by `tools/new_species.py`; shaped here. The vertical slice's bank had a 22 m flank of blank stucco
between its corners. A pilaster used to be a Patina cover, proud of the wall with no collider, and was withdrawn for
standing in walkable space; carving piers into the wall modules cannot follow a bay line, because Deli Counter tiles
each storey round its own openings and the storeys share almost no seams (the factory's docs/findings/slice_look/).
So a pilaster is a solid of its own, placed by Deli Counter and collided like any other.

The shape is `core/pilaster_forms.py`'s. ONE MATERIAL, the plan's (the genome's stone trim). One collider, the slot's
whole box.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core.pilaster_forms import boxes, hidden


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    rng = streams.stream("wear")
    objs = []
    for name, lo, hi in boxes(w, d, h):
        bm = geometry.new_bm()
        geometry.add_box(bm, tuple((lo[i] + hi[i]) / 2.0 for i in range(3)), tuple(hi[i] - lo[i] for i in range(3)))
        geometry.drop_faces(bm, lambda nrm, part=name: hidden(part, nrm))
        objs.append(geometry.bm_to_object(bm, f"WallPilaster_{name}", collection, bevel=plan["bevel"], texel=1.2,
                                          rng=rng, wear=plan["wear"]))
    surface = materials.make_material(f"M_WallPilaster_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, surface)
    return {"objects": objs, "collision_boxes": [((-w / 2, -d / 2, -h / 2), (w / 2, d / 2, h / 2))],
            "attachments": {"ATT_top": (0.0, 0.0, h / 2)}}
