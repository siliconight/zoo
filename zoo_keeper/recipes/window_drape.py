"""window_drape recipe: two velvet panels drawn shut across a den's window.

Planned in pure Python by `core.window_drape_forms.plan_drape`, built by
`bpylayer.prim_mesh`. ONE material -- the genome's velvet, in the style's
colour -- so the pelmet and both panels pack into one mesh, one draw a
window. No collision: the window's own pane seals the opening.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import window_drape_forms as WDF


def _hex(c):
    return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c[:3])


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    got = WDF.plan_drape(w, d, h)
    rgb = list(plan["color"])
    kind = plan["material"]
    mats = {"velvet": (f"M_WindowDrape_{kind}_{_hex(rgb)}", rgb, kind)}
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    return {"objects": objs, "collision_boxes": got["collision"], "attachments": {}}
