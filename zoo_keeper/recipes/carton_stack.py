"""carton_stack recipe: cardboard cartons and banker's boxes in seeded stacks.

The geometry is planned in pure Python by `core.carton_forms` (read its
docstring for the rules) and built here vertex for vertex by
`bpylayer.prim_mesh`, so the unit tests measure what ships.

Flat-faceted, no bevel: a carton is a box, and at 36 triangles a box a
basement can hold a dozen stacks. The kraft body takes the genome's colour
and kind; banker white, tape, label and hand hole are sub-part finishes
from `carton_forms.MATERIALS`. Collision is one box per footprint to that
footprint's top.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import carton_forms


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    style = (plan.get("params") or {}).get("style", "auto")
    got = carton_forms.plan(w, d, h, streams.stream("form"), style)
    mats = {}
    for key, (colour, kind) in carton_forms.MATERIALS.items():
        mats[key] = (f"M_CartonStack_{key}_{kind}", list(colour), kind)
    kind = plan["material"]
    mats["kraft"] = (f"M_CartonStack_kraft_{kind}", plan["color"], kind)
    objs = prim_mesh.build(got["prims"], collection, dict(plan, bevel=0.0),
                           streams.stream("wear"), mats, texel=1.0)
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {}}
