"""Chair recipe: seat slab, back panel, post legs, optional arms.

BAYS (roadmap 44). Deli Counter's `waiting_seats` (5.0 x 2.0 x 0.6),
`bench_row` (2.8 x 1.0 x 0.9) and `booth_seating` (2.0 x 1.2 x 1.1) are
ROWS of seating; a chair is 0.4-0.6 m wide. `_bays.bays` divides the width
into seats of at most `bay_max` (genome params), each with its own seat,
back, legs and arms -- a row of joined chairs, which is what a waiting
room has. The seat height is the smaller of the chair's own 0.45 and the
authored height less a hand, so a 0.6 m bench is a bench and not a stool
with a two-centimetre back. One bay is the chair this recipe always built.

The boxes come from `_chair_row.layout`, which is pure so the suite can
check them without Blender; its docstring records why the back stands off
the module's back plane and why neighbouring chairs no longer touch (cold
run 9052).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ._bays import bay_max_of
from ._chair_row import layout


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs = []

    lay = layout(w, d, h, bay_max_of(plan), legs=plan["params"]["legs"],
                 has_arms=bool(plan["params"].get("has_arms")))
    for name, boxes in lay["parts"]:
        bm = geometry.new_bm()
        for centre, size in boxes:
            geometry.add_box(bm, centre, size)
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, rng=rng, wear=wear))
    mat = materials.make_material(
        f"M_Chair_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": list(lay["collision"]),
            "attachments": {"ATT_seat_center": (0, 0, lay["seat_h"])}}
