"""utility_pole recipe: a wooden distribution pole and what it carries.

Roadmap 240, the walker's Philly comps: the pole at the corner and along the
kerb that carries the street's cobra-head and its wires. `core.
utility_pole_forms` lays it out in pure Python -- the references, the frame,
the numbers Lot mirrors and the forms are all argued there -- and
`bpylayer.prim_mesh` builds those lists vertex for vertex, so what its tests
measure is what ships.

Four materials whatever the form: the wood takes the genome's colour and
kind (creosote, the one thing a style may tint); the steel, the porcelain and
the lit lens are constants of the pole, the way a sign's colours are the
standard's. The lens is `M_UtilityPole_Lens`, so Lux's emissive binder powers
it with the street's lamps and cuts it with them.

Collision is the POLE only: a body walks under an arm.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import utility_pole_forms as F


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    form = (plan.get("params") or {}).get("form")
    got = F.plan(w, d, h, form)
    style = plan.get("style_block", {})
    mats = {key: (f"M_UtilityPole_{key}", list(c), kind)
            for key, (c, kind) in F.MATERIALS.items()}
    mats["wood"] = (f"M_UtilityPole_{plan['material']}", list(plan["color"]),
                    plan["material"])
    mats["lens"] = ("M_UtilityPole_Lens",
                    list(style.get("emissive_color", F.LENS_COLOUR)), "emissive",
                    float(style.get("emissive_strength", F.LENS_STRENGTH)))
    objs = prim_mesh.build(got["prims"], collection, plan,
                           streams.stream("wear"), mats, texel=1.4)
    px, py = got["facts"]["pole_at"]
    ly, lz = got["facts"]["lens_at"]
    print(f"[utility_pole] form={got['form']} {w:.3f} x {d:.3f} x {h:.3f} "
          f"tris={got['facts']['tris']} overshoot={got['overshoot_m']}")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_lamp": (px, py + ly, lz)},
            "utility_pole": {"form": got["form"], "tris": got["facts"]["tris"],
                             "pole_at": [px, py], "lens_at": [ly, lz]}}
