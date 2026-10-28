"""safe_deposit_boxes recipe: a vault-room wall of deposit boxes (intact state).

An interactive architectural module. Center-pivot, fit-to-exact-dims: a solid metal BACKING slab (rear of the depth),
whose front face is the boxes' doors, plus a bordered GRID of DIVIDERS on the front -- the frame between the doors --
with larger boxes in the bottom rows. The backing reaches the exact (w, d, h) box on width/height/rear and the dividers
reach the front, so fit-to-exact-dims holds; the wall is solid (one collision box).

EACH DOOR CARRIES A BRASS LOCK AND A NUMBER PLATE, AND A FEW BOXES ARE DRAWN (1.140.0, the walker's bank comp 12;
`core.deposit_boxes`, which says why each is what it is). They and the frame are one material: the lock, the plate and
a drawn box's dark cell are colour in the `Wear` vertex colour, so the wall is one submission.

Cheap by construction: (cols+1) vertical + (rows+1) horizontal dividers, not a box per cell, and the grid is capped so
a big wall stays low-poly; the hardware is two small plates a door, unbevelled. Builds only the intact state; a
`drilled` state reuses this art (resolver falls back to the base) until a drilled-boxes art pass.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import arch
from ..core import deposit_boxes as db


def build(plan, streams, collection):
    dims = plan["dimensions"]
    w, d, h = dims["width"], dims["depth"], dims["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    p = plan.get("params", {})
    rng = streams.stream("wear")
    seed = streams.stream("drawn").randrange(1 << 30)
    root = arch.root_name("safe_deposit_boxes")   # "SafeDepositBoxes"
    objs = []
    for name, boxes, rgb in db.layout(w, d, h, p, seed):
        if not boxes:
            continue
        bm = geometry.new_bm()
        for centre, size in boxes:
            geometry.add_box(bm, centre, size)
        # the backing keeps the style's bevel. The frame does not: its crossing bars' chamfers notched each other into
        # a dark dot at every crossing (1.139.0's render), and the hardware is too small to carry one.
        back = name == f"{root}_Backing"
        o = geometry.bm_to_object(bm, name, collection, bevel=bevel if back else 0.0, texel=1.2, rng=rng,
                                  wear=wear * (1.0 if name == f"{root}_Backing" else 0.9))
        geometry.tint_wear(o, rgb)
        objs.append(o)

    materials.assign(objs, materials.make_material(
        f"M_SafeDepositBoxes_{plan['material']}", plan["color"],
        plan["material"]))

    # the wall is solid -> a single envelope collision box (no walking through)
    cboxes = [((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, h / 2.0))]
    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
