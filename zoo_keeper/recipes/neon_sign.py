"""neon_sign recipe: a club's name in lit glass tube on a dark backer, for a
wall.

Planned in pure Python by `core.neon_forms.plan_sign` (the lettering, the
layout and why the tubes are built the way they are are in its docstring)
from the one name table, `core.club_names`: the slot's ``variant`` IS the
name's index. Built by `bpylayer.prim_mesh`. The backer takes the genome's
colour and kind; the tubes are emissive in the palette's two colours, named
``M_NeonSign_<hex>_Face`` so each colour is its own material and Lux's
power cut takes every one of them.

No collision: a sign on a wall above head height. The back of the backer is
the slot's +Y face, the wall; the lettering faces -Y.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import club_names
from ..core import neon_forms as NF


def _hex(c):
    return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c[:3])


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    variant = int((plan.get("params") or {}).get("variant", 0) or 0)
    got = NF.plan_sign(w, d, h, variant)
    kind = plan["material"]
    mats = {key: (f"M_NeonSign_{key}_{k}", list(c), k)
            for key, (c, k) in NF.MATERIALS.items()}
    mats["backer"] = (f"M_NeonSign_backer_{kind}", list(plan["color"]), kind)
    for key, rgb in got["colours"].items():
        mats[key] = (f"M_NeonSign_{_hex(rgb)}_Face", list(rgb), "emissive",
                     club_names.NEON_STRENGTH)
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    return {"objects": objs, "collision_boxes": [],
            "attachments": {"ATT_face": (0.0, -d / 2, h / 2)}}
