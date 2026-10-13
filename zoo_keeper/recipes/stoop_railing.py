"""stoop_railing recipe: the iron railing either side of a rowhouse stoop.

Factory roadmap 240, the walker's calls of 2026-10-13: "railings both sides -- build the railings".
`core.stoop_railing_forms` lays it out in pure Python -- the code's numbers, the two forms and why no
two faces meet are argued there -- and `bpylayer.prim_mesh` builds those lists vertex for vertex, so
what its tests measure is what ships.

One material whatever the form: the iron, in the genome's paint. No collision: Deli Counter writes the
railing's colliders with the stoop's, in the greybox the graders walk.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import stoop_railing_forms as F


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    form = (plan.get("params") or {}).get("form")
    got = F.plan(w, d, h, form)
    mats = {F.MAT: (f"M_StoopRailing_{plan['material']}", list(plan["color"]),
                    plan["material"])}
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"),
                           mats, texel=1.2)
    print(f"[stoop_railing] form={got['form']} {w:.3f} x {d:.3f} x {h:.3f} "
          f"tris={got['facts']['tris']} pickets={got['facts']['pickets']}")
    return {"objects": objs, "collision_boxes": got["collision"], "attachments": {},
            "stoop_railing": {"form": got["form"], "tris": got["facts"]["tris"],
                              "pickets": got["facts"]["pickets"]}}
