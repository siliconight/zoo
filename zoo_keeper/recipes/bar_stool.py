"""bar_stool recipe: a padded round seat on a chrome column with a footring
and a domed base.

Planned in pure Python by `core.club_forms.plan_stool`, built by
`bpylayer.prim_mesh`. The column, footring and base take the genome's colour
and kind (bright bare metal); the seat is vinyl -- `plastic` -- in one of
`club_forms.SEATS`, drawn from the module's "form" stream; the pan under it
is black paint.
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
    got = CF.plan_stool(w, d, h, streams.stream("form"))
    kind = plan["material"]
    seat = got["seat_rgb"]
    mats = {key: (f"M_BarStool_{key}_{k}", list(c), k)
            for key, (c, k) in CF.STOOL_MATERIALS.items()}
    mats["column"] = (f"M_BarStool_column_{kind}", list(plan["color"]), kind)
    mats["seat"] = (f"M_BarStool_seat_{_hex(seat)}", list(seat), "plastic")
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_seat": (0.0, 0.0, h)}}
