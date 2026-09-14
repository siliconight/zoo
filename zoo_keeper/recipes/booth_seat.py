"""booth_seat recipe: a bar or diner booth, or a 1990s couch -- one species
with a ``form`` param.

Planned in pure Python by `core.booth_forms` (the parts and the rules are in
its docstring) and built vertex for vertex by `bpylayer.prim_mesh`. The
upholstery takes the genome's colour and kind; booth panels, kick and cap
rail are dark wood and a couch's feet darker, sub-part finishes from
`booth_forms.MATERIALS`, because the wood of a booth is not the vinyl on it.

``form`` is the slot's (``kit.DRESSING_FIELDS``) when Deli Counter writes
one, else the genome's ``auto``, which reads it off the slot's height.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import booth_forms


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    form = (plan.get("params") or {}).get("form", "auto")
    got = booth_forms.plan(w, d, h, streams.stream("form"), form)
    kind = plan["material"]
    mats = {key: (f"M_BoothSeat_{key}_{k}", list(c), k)
            for key, (c, k) in booth_forms.MATERIALS.items()}
    mats["upholstery"] = (f"M_BoothSeat_upholstery_{kind}", list(plan["color"]), kind)
    objs = prim_mesh.build(got["prims"], collection, plan,
                           streams.stream("wear"), mats, texel=1.0)
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {}}
