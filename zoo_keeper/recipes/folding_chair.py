"""folding_chair recipe: the play area's chair.

Planned in pure Python by `core.folding_forms.plan_chair`: a seat pan on four
splayed legs with a raked back on two posts under a cap rail. BOXES AND NOT
TUBES -- `prims.rod` at eight segments is 48 triangles a leg against a box's
12, and at the distance a play area is seen from the silhouette is the splay
and not the section.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import folding_forms as FF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    got = FF.plan_chair(w, d, h, params, params.get("variant") or 0)

    # THE SLOT'S MATERIAL NAMES THE PAN and the frame stays painted steel: a
    # folding chair is a black frame with a moulded seat, and the seat is the
    # part a room's palette changes.
    mats = {
        FF.FRAME: ("M_FoldingChair_frame_metal_painted", [0.13, 0.13, 0.14],
                   "metal_painted"),
        FF.PAN: (f"M_FoldingChair_pan_{plan['material']}",
                 list(plan["color"]), plan["material"]),
        FF.SEAT: (f"M_FoldingChair_back_{plan['material']}",
                  list(plan["color"]), plan["material"]),
    }
    objs = prim_mesh.build(got["prims"], collection, plan,
                           streams.stream("wear"), mats, texel=1.0)
    f = got["facts"]
    print(f"[folding_chair] {w:.2f} x {d:.2f} x {h:.2f} "
          f"seat={f['seat_h_m']:.3f} rake={f['rake_deg']} back={f['back']} "
          f"variant={f['variant']} {f['tris']} tris (pure)")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {}, "folding_chair": dict(f)}
