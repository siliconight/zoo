"""shop_awning recipe: a corner shop's canvas awning over its storefront (1.108.0, factory roadmap 241).

`core.shop_awning_forms` lays it out in pure Python -- the shed, its colours and why no two faces meet are argued
there -- and `bpylayer.prim_mesh` builds those lists vertex for vertex, so what its tests measure is what ships.

One material a module: the canvas, in its form's colour, named for that colour (`M_ShopAwning_canvas_<colour>`), so
two awnings built in one process never share the first one's tint through the material cache. No collision.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import shop_awning_forms as F


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    form = (plan.get("params") or {}).get("form")
    got = F.plan(w, d, h, form)
    mats = {F.MAT: (f"M_ShopAwning_{plan['material']}_{got['colour']}", list(got["rgb"]), plan["material"])}
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"), mats, texel=1.0)
    print(f"[shop_awning] form={got['form']} {w:.3f} x {d:.3f} x {h:.3f} tris={got['facts']['tris']} "
          f"pitch={got['facts']['pitch_deg']}")
    return {"objects": objs, "collision_boxes": [], "attachments": {},
            "shop_awning": {"form": got["form"], "tris": got["facts"]["tris"],
                            "pitch_deg": got["facts"]["pitch_deg"]}}
