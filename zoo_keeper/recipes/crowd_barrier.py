"""crowd_barrier recipe: a steel crowd-control barricade, one interlocking panel on its flat feet.

Factory roadmap 267, the walker's look review of 2026-10-20: arena_a02's barriers are to be "Crowd rails (a new
model)". `core.crowd_barrier_forms` lays it out in pure Python -- the reference sizes, the frame, why no two faces meet
and why no open tube end shows -- and `bpylayer.prim_mesh` builds those lists vertex for vertex, so what its tests
measure is what ships.

One material whatever the size: galvanised steel, in the genome's grey. Collision: the panel, as the plan gives it.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import crowd_barrier_forms as F


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    got = F.plan(w, d, h)
    mats = {F.MAT: (f"M_CrowdBarrier_{plan['material']}", list(plan["color"]), plan["material"])}
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"), mats, texel=1.2)
    print(f"[crowd_barrier] {w:.3f} x {d:.3f} x {h:.3f} tris={got['facts']['tris']} "
          f"pickets={got['facts']['pickets']}")
    return {"objects": objs, "collision_boxes": got["collision"], "attachments": {},
            "crowd_barrier": {"tris": got["facts"]["tris"], "pickets": got["facts"]["pickets"]}}
