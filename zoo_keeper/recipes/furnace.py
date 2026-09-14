"""furnace recipe: the basement's mechanical anchor -- a 1990s upflow gas
furnace or a gas water heater, one species with a ``form`` param.

Planned in pure Python by `core.furnace_forms` (its docstring has the parts
and the rules) and built vertex for vertex by `bpylayer.prim_mesh`. The
cabinet, tank and inducer take the genome's colour and kind; the doors are
that colour darkened; duct, pipe, pad, valve and sticker are sub-part
finishes from `furnace_forms.MATERIALS`, because galvanised duct is
galvanised whatever colour the cabinet is painted.

``form`` is the slot's (``kit.DRESSING_FIELDS``) when Deli Counter writes
one, else the genome's ``auto``, which reads the form off the dims.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import furnace_forms


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    form = (plan.get("params") or {}).get("form", "auto")
    got = furnace_forms.plan(w, d, h, form)
    kind = plan["material"]
    colour = list(plan["color"])
    mats = {key: (f"M_Furnace_{key}_{k}", list(c), k)
            for key, (c, k) in furnace_forms.MATERIALS.items()}
    mats["body"] = (f"M_Furnace_body_{kind}", colour, kind)
    mats["door"] = (f"M_Furnace_door_{kind}", [v * 0.82 for v in colour], kind)
    objs = prim_mesh.build(got["prims"], collection, plan,
                           streams.stream("wear"), mats, texel=1.2)
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {}}
