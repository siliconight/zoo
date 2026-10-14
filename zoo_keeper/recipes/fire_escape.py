"""fire_escape recipe: one storey of a steel fire escape on a walk-up's front (1.110.0, factory roadmaps 156 and 241).

The walker's photo of a brick walk-up: "this is something i'd like to see in our toolset, fireescape stairs brick".
`core.fire_escape_forms` lays a storey out in pure Python -- the landing, its guards, the flight that switches back,
the drop ladder, and why no two faces meet -- and `bpylayer.prim_mesh` builds those lists vertex for vertex, so what
its tests measure is what ships.

One material whatever the form: the steel, in the genome's paint. No collision: the lowest landing stands a storey
up, and a walkable fire escape is later work.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import fire_escape_forms as F


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    form = (plan.get("params") or {}).get("form")
    got = F.plan(w, d, h, form)
    mats = {F.MAT: (f"M_FireEscape_{plan['material']}", list(plan["color"]), plan["material"])}
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"), mats, texel=1.2)
    print(f"[fire_escape] form={got['form']} {w:.3f} x {d:.3f} x {h:.3f} tris={got['facts']['tris']}")
    return {"objects": objs, "collision_boxes": [], "attachments": {},
            "fire_escape": {"form": got["form"], "tris": got["facts"]["tris"],
                            "facts": {k: v for k, v in got["facts"].items() if k != "tris"}}}
