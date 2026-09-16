"""folding_table recipe: the play area's table, bare or under a black cloth.

Planned in pure Python by `core.folding_forms.plan_table`. What is ON it is
`_surface_stock`'s `cards` flavour -- playmats, card piles, deck boxes and
dice -- planned once per SIDE of the top, so two players' worth of dressing
face each other across it the way the reference photographs it.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import folding_forms as FF

#: The cloth is near-black and the hem a shade off it, so the two read apart
#: under one light; the frame is the folding table's grey painted steel.
PALETTE = {
    FF.FRAME: ("M_FoldingTable_frame_metal_painted", [0.30, 0.31, 0.32],
               "metal_painted"),
    FF.CLOTH: ("M_FoldingTable_cloth", [0.045, 0.045, 0.050], "cloth"),
    FF.HEM: ("M_FoldingTable_hem", [0.075, 0.075, 0.082], "cloth"),
}


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    got = FF.plan_table(w, d, h, params, params.get("variant") or 0)

    mats = dict(PALETTE)
    mats[FF.TOP] = (f"M_FoldingTable_top_{plan['material']}",
                    list(plan["color"]), plan["material"])
    objs = prim_mesh.build(got["prims"], collection, plan,
                           streams.stream("wear"), mats, texel=1.0)
    # THE STOCK'S HOST COLOUR is the CLOTH's when there is one, because that
    # is what a playmat contrasts against on this table -- `_surface_stock`
    # picks each finish's candidate by contrast with the colour it is handed,
    # and handing it the top's white under a black cloth would pick for the
    # wrong surface.
    host_rgb = (list(PALETTE[FF.CLOTH][1]) if got["facts"]["form"] == "cloth"
                else list(plan["color"]))
    stock = prim_mesh.build_stock(plan, streams, collection, got["regions"],
                                  host_rgb)
    objs += stock
    f = got["facts"]
    print(f"[folding_table] {w:.2f} x {d:.2f} x {h:.2f} form={f['form']} "
          f"variant={f['variant']} frames={f['frames']} "
          f"stock={params.get('stock')} {f['tris']} tris (pure) "
          f"+ {len(stock)} stock object(s)")
    return {"objects": objs, "dressing_objects": stock,
            "collision_boxes": got["collision"],
            "attachments": {"ATT_surface_center": (0.0, 0.0, h)},
            "folding_table": dict(f)}
