"""booth_seat recipe: a bar or diner booth, or a 1990s couch -- one species
with a ``form`` param.

Planned in pure Python by `core.booth_forms` (the parts and the rules are in
its docstring) and built vertex for vertex by `bpylayer.prim_mesh`. The
upholstery takes the genome's colour and kind; booth panels, kick and cap
rail are dark wood and a couch's feet darker, sub-part finishes from
`booth_forms.MATERIALS`, because the wood of a booth is not the vinyl on it.

THE UPHOLSTERY IS ``plan["upholstery"]`` (0.89.0, `dna.UPHOLSTERED`), not
``plan["material"]``. A Deli Counter sofa volume carries `wood`, and 0.88.0
read that as the upholstery: the club walk's couch shipped with
`M_Skin_wood_delco_1997` on its cushions and no leather anywhere. A slot's
material on an upholstered species is its FRAME -- the panels, kick, cap
and feet take it in their own colours -- unless it names an upholstery
kind, in which case it is the upholstery and the frame keeps its wood. On
the prompt path (no module) the plan carries no `upholstery` and the
material is the upholstery, as it always was.

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
    uph = plan.get("upholstery") or {"material": plan["material"], "frame": None,
                                     "color": plan["color"]}
    kind = uph["material"]
    frame = uph.get("frame")
    mats = {}
    for key, (c, k) in booth_forms.MATERIALS.items():
        # the frame parts are the wooden ones; a slot's frame kind replaces
        # their wood and keeps their colour (a dark leg is a dark leg)
        kk = frame if (frame and k == "wood") else k
        mats[key] = (f"M_BoothSeat_{key}_{kk}", list(c), kk)
    mats["upholstery"] = (f"M_BoothSeat_upholstery_{kind}", list(uph["color"]), kind)
    objs = prim_mesh.build(got["prims"], collection, plan,
                           streams.stream("wear"), mats, texel=1.0)
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {}}
