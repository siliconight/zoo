"""club_chair recipe: a low barrel-backed tub chair in worn velvet.

Planned in pure Python by `core.club_forms.plan_chair`, built by
`bpylayer.prim_mesh`. The upholstery is `velvet` in one of
`club_forms.VELVETS`, drawn from the module's "form" stream (so the
variant picks it); the feet take the genome's colour and kind; the piping
is dark leather. A couch is `booth_seat` form ``sofa``, not this.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import club_forms as CF


def _hex(c):
    return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c[:3])


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    got = CF.plan_chair(w, d, h, streams.stream("form"))
    kind = plan["material"]
    velvet = got["velvet_rgb"]
    mats = {key: (f"M_ClubChair_{key}_{k}", list(c), k)
            for key, (c, k) in CF.CHAIR_MATERIALS.items()}
    mats["feet"] = (f"M_ClubChair_feet_{kind}", list(plan["color"]), kind)
    mats["velvet"] = (f"M_ClubChair_velvet_{_hex(velvet)}", list(velvet), "velvet")
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_seat": (0.0, 0.0, got["seat_z"])}}
