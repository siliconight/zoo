"""milk_crate_stack recipe: a stack of plastic milk crates.

Planned in pure Python by `core.milk_crate_forms` -- hollow, open-topped
crates nested 4 mm into each other -- and executed here as ONE submission:
one plastic material, the stack's colour (by variant) in the `Wear` vertex
colour, so a walk-in full of stacks in four colours is still one material.
"""
from __future__ import annotations

from ..bpylayer import geometry, prim_mesh
from ..core import milk_crate_forms as MC


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    variant = MC.resolve(plan)
    got = MC.plan(w, d, h)
    colour = MC.COLOURS[variant % len(MC.COLOURS)]
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"),
                           {"crate": ("M_Crate_plastic", [1.0, 1.0, 1.0], MC.KIND)}, texel=1.0)
    for o in objs:
        geometry.tint_wear(o, colour)
    f = got["facts"]
    print(f"[milk_crate_stack] {f['cols']}x{f['rows']}x{f['layers']} crates colour={variant % len(MC.COLOURS)}")
    return {"objects": objs, "collision_boxes": [f["collision"]], "attachments": {},
            "milk_crate_stack": {"crates": f["crates"], "colour": variant % len(MC.COLOURS)}}
