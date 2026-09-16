"""sign_post recipe: a u-channel post and the blade it carries.

From 2026-09-12 to 0.95.0 this file was the placeholder box
`tools/new_species.py` mints -- a 0.10 x 0.10 x 2.40 m pole with nothing on
it -- and that is what the walker photographed on cold run 9060 ("no signs on
the stop signs here anymore?"). Lot 0.73.0 named the legend every post it
stands carries; `core.sign_blade_forms` draws them, and its docstring has the
MUTCD references, the sizes and the two rules the layout turns on.

``form`` is the slot's (``kit.DRESSING_FIELDS``) -- `no_parking`,
`ped_crossing` or `bus_stop`. There is no ``auto``: a legend is not a shape,
so nothing here reads the dims to guess one, and a slot with no form gets the
bare u-channel the species was.

Planned in pure Python and built vertex for vertex by `bpylayer.prim_mesh`.
The post takes the genome's colour and material -- galvanised steel, and the
one thing on the module a style may tint; every sign colour is a constant of
the standard, the way the dartboard's chrome is.

Collision is the POST only: a body walks into a pole, never into a sign face
two metres over its head.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import sign_blade_forms as F


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    form = (plan.get("params") or {}).get("form")
    got = F.plan(w, d, h, form)
    mats = {key: (f"M_SignPost_{key}_{kind}", list(c), kind)
            for key, (c, kind) in F.MATERIALS.items()}
    mats["post"] = (f"M_SignPost_{plan['material']}", list(plan["color"]),
                    plan["material"])
    # THE BEVEL IS CAPPED BY THE FLANGE, not taken from the style as-is --
    # see `sign_blade_forms.post_bevel`, where the zero-area triangles it
    # was making are counted.
    objs = prim_mesh.build(got["prims"], collection,
                           dict(plan, bevel=F.post_bevel(plan.get("bevel"))),
                           streams.stream("wear"), mats, texel=1.2)
    print(f"[sign_post] form={got['form']} blade={got['facts']['blade']} "
          f"sign={got['facts']['sign_m']:.3f} m tris={got['facts']['tris']}")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_face": (0.0, -d / 2.0,
                                         got["facts"]["face_z"])},
            "sign_post": {"form": got["form"],
                          "blade": got["facts"]["blade"],
                          "tris": got["facts"]["tris"]}}
