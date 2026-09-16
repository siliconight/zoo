"""display_case recipe: the card shop's glass-top showcase counter.

Planned in pure Python by `core.display_case_forms` -- the shell, the shelves,
the stock and which art each item carries -- and built by `bpylayer.prim_mesh`,
except the ART QUADS, which carry their own UVs into one atlas painted by
`core.card_art` (`recipes/_card_atlas.py` does that for this species and for
`pack_wall`).

FORMS: ``flat`` and ``L``; ``auto`` takes the L when the slot is deep enough
to carry a return run with a staff aisle behind the main one.

WHAT STANDS ON THE COUNTER does not move the module's fit. The white card
storage boxes and the register are returned as ``dressing_objects``, the same
rule that lets a monitor stand on a desk -- `validate.fit_height` measures
the module, and a tower of boxes is not the module.

COLLISION IS THE TOP'S OWN FOOTPRINT, one box per quad of it. For an L that
is the point: one box over the slot would wall off the inside of the corner,
which is where the staff stand.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import display_case_forms as DF

#: Material key -> (name, linear rgb, kind). The case's own palette: the
#: glass, the aluminium frame, the laminate deck, and a neutral for the
#: stock, whose colour is carried by the art quad standing in front of it.
PALETTE = {
    DF.GLASS: ("M_DisplayCase_glass", [0.62, 0.68, 0.70], "glass"),
    DF.METAL: ("M_DisplayCase_frame_metal_bare", [0.66, 0.67, 0.69], "metal_bare"),
    DF.DECK: ("M_DisplayCase_deck_laminate", [0.72, 0.69, 0.62], "laminate"),
    DF.STOCK: ("M_DisplayCase_stock_paper", [0.55, 0.52, 0.47], "paper"),
}


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    stem = (plan.get("module") or {}).get("stem") or "display_case"
    got = DF.plan(w, d, h, params, params.get("variant") or 0, key=stem)

    mats = dict(PALETTE)
    # THE SLOT'S MATERIAL NAMES THE BODY, not the glass and not the frame: a
    # case in a wood-panelled shop has a wood body and the same aluminium and
    # the same glass, exactly as `wood` on a sofa names its legs.
    mats[DF.BODY] = (f"M_DisplayCase_body_{plan['material']}",
                     list(plan["color"]), plan["material"])

    solid = [p for p in got["prims"] if not p.get("tile")]
    in_slot = [p for p in solid if not p.get("above")]
    above = [p for p in solid if p.get("above")]
    objs = prim_mesh.build(in_slot, collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    dressing = prim_mesh.build(above, collection, plan, streams.stream("wear"),
                               mats, texel=1.0)
    from ._card_atlas import build_art
    art, atlas = build_art(got["prims"], collection,
                           dict(plan, _tiles=got["tiles"]), streams,
                           "DisplayCase")
    for obj in art:
        (dressing if obj.name.endswith("_Above") else objs).append(obj)

    f = got["facts"]
    print(f"[display_case] {w:.2f} x {d:.2f} x {h:.2f} form={f['form']} "
          f"runs={f['runs']} shelves={f['shelves']} items={f['items']} "
          f"variant={f['variant']} maker={f['maker']} tiles={f['tiles']} "
          f"atlas={atlas['name'] if atlas else '-'} "
          f"{f['tris']} tris (pure), {f['colliders']} collision box(es)")
    return {"objects": objs + dressing, "dressing_objects": dressing,
            "collision_boxes": got["collision"], "attachments": {},
            "display_case": dict(f, atlas=atlas["name"] if atlas else None)}
