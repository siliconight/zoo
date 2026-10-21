"""stanchion_run recipe: one straight run of retractable-belt queue stanchions, posts and belt.

Factory roadmap 267, the walker's 2026-10-20 photo of a queue indoors: black posts on round bases, a flat black belt
taut between them at waist height. `core.stanchion_run_forms` lays the run out in pure Python -- the reference sizes,
the posts' spacing, why no two faces meet and no open end shows -- and `bpylayer.prim_mesh` builds those lists vertex
for vertex, so what its tests measure is what ships.

One material whatever the length: black powder coat, the belt in the same black. Collision: the posts and the belt
line, as the plan gives them.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import stanchion_run_forms as F


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    got = F.plan(w, d, h)
    mats = {F.MAT: (f"M_StanchionRun_{plan['material']}", list(plan["color"]), plan["material"])}
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"), mats, texel=1.2)
    print(f"[stanchion_run] {w:.3f} x {d:.3f} x {h:.3f} tris={got['facts']['tris']} posts={got['facts']['posts']}")
    return {"objects": objs, "collision_boxes": got["collision"], "attachments": {},
            "stanchion_run": {"tris": got["facts"]["tris"], "posts": got["facts"]["posts"]}}
