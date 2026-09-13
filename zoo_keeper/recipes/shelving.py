"""shelving recipe: freestanding shelf unit (store gondola / stockroom rack).

Two side uprights, N evenly spaced shelf boards, optional back panel.
Origin at floor center; shelves open toward -Y (customer/picking side).
Proportions read the identity: wide+low+wood = retail gondola, tall+deep+
metal = stockroom racking — same recipe, different plan.

BAYS (roadmap 44). A shelf AISLE in a Deli Counter spec is 6-7 m long; one
2.4 m unit cannot be it. `_bays.bays` divides the width into equal bays of
at most `bay_max` (genome params), an upright stands at every bay boundary
and each bay carries its own boards and back panel -- the shape a real run
of gondolas has, uprights shared between neighbours. One bay is the unit
this recipe always built.

STOCK (0.78.0). "Nothing in the cabinets" (the walker): the shelves were
bare boards. Every shelf but the top one now carries a back office's worth
of boxes, binders, ledgers and cans, planned by `_shelf_stock.plan_shelf`
from the recipe's own "stock" stream -- a named stream, so the wear noise of
the frame is exactly what it was.

NO COINCIDENT FACES (0.78.0). Measured with tools/coplanar_probe.py on the
2.0 x 0.4 x 1.9 module cold run 9049 shipped (Zoo 0.76.0), 24 coincident
pairs, all gap 0.00 mm: the back panel ran the full height, so its top face
lay in the top board's top face (113.6 cm2, both facing up, the one pair a
player could see from above a low unit) and its bottom in the bottom board's
bottom; and boards and back panel stopped exactly at the uprights' inner
faces, so their end faces touched the uprights and each other. The back panel
now runs from the middle of the bottom board to the middle of the top board,
boards and back panel reach BURY into the uprights, the back panel stands
BACK_INSET in from the uprights' rear faces and the board stack stops LIFT
short of their top and bottom faces, so the embed does not lay any face in
an upright's.

The same arithmetic found a gap nobody had reported: a board used to span
``bx +/- (bw/2 - up)``, which reaches the inner face of an END upright but
stops up/2 = 25 mm short of a SHARED one, so on a multi-bay run every middle
upright stood free of the boards either side of it. Spans are now taken from
the uprights' own faces.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from . import _shelf_stock
from ._bays import bay_max_of, bays

#: How far boards and the back panel reach into the uprights.
BURY = 0.005
#: How far the back panel's rear face stands in from the uprights' rear faces.
BACK_INSET = 0.004
#: How far the lowest board's underside and the highest board's top stand in
#: from the uprights' bottom and top faces.
LIFT = 0.003
BACK_T = 0.02
#: Stock cylinders (cans) are faceted, not round.
CAN_SEGMENTS = 8


def _darker(c, f=0.7):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    n_shelves = max(2, int(plan["params"]["shelves"]))
    back = bool(plan["params"].get("back", 1))
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.4, rng=rng, wear=wear))

    up = 0.05
    runs = bays(w, bay_max_of(plan))
    # uprights: the two ends, and one at every boundary between bays
    edges = [-w / 2 + up / 2] + [bx + bw / 2 for bx, bw in runs[:-1]] + [w / 2 - up / 2]
    for i, x in enumerate(edges):
        side = "L" if i == 0 else ("R" if i == len(edges) - 1 else "M%d" % i)
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, 0.0, h / 2), (up, d, h))
        part(bm, f"Shelf_Upright_{side}")

    board = 0.035
    # the board stack stops LIFT short of the uprights' top and bottom faces:
    # a board reaching BURY into an upright would otherwise lay its top (or
    # bottom) face in the upright's over that strip
    pitch = (h - board - 2 * LIFT) / (n_shelves - 1)
    front_y = -d * 0.48
    back_rear = d / 2 - BACK_INSET
    back_front = back_rear - BACK_T
    # with a back panel, a board ends in the middle of it; without, where it
    # always did
    board_back = (back_rear + back_front) / 2 if back else d * 0.48
    stock_rng = streams.stream("stock")
    stock = []
    for bi, (bx, bw) in enumerate(runs):
        tag = "" if len(runs) == 1 else f"_B{bi + 1}"
        # the clear span between this bay's two uprights, face to face
        left, right = edges[bi] + up / 2, edges[bi + 1] - up / 2
        span_c, span_w = (left + right) / 2, (right - left) + 2 * BURY
        for i in range(n_shelves):
            z = LIFT + board / 2 + i * pitch
            bm = geometry.new_bm()
            geometry.add_box(bm, (span_c, (front_y + board_back) / 2, z),
                             (span_w, board_back - front_y, board))
            part(bm, f"Shelf_Board_{i + 1}{tag}")
            if i < n_shelves - 1:
                stock += _shelf_stock.plan_shelf(
                    stock_rng, left, right, front_y,
                    back_front if back else d * 0.48,
                    z + board / 2, pitch - board)
        if back:
            bm = geometry.new_bm()
            # half the boards' bury, so its end faces and theirs are not one
            # plane inside the upright
            geometry.add_box(bm, (span_c, (back_rear + back_front) / 2, h / 2),
                             (span_w - BURY, BACK_T, h - board - 2 * LIFT))
            part(bm, f"Shelf_Back{tag}")
    structure = list(objs)

    # stock: one object per finish, flat-faceted (no bevel) to stay cheap
    by_finish = {}
    for it in stock:
        by_finish.setdefault(it["finish"], []).append(it)
    stock_objs = {}
    for finish in sorted(by_finish):
        bm = geometry.new_bm()
        for it in by_finish[finish]:
            lo, hi = it["min"], it["max"]
            if it["shape"] == "cyl":
                geometry.add_cylinder(
                    bm, ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2,
                         (lo[2] + hi[2]) / 2),
                    (hi[0] - lo[0]) / 2, hi[2] - lo[2],
                    segments=CAN_SEGMENTS, axis="Z")
            else:
                geometry.add_box(bm, tuple((lo[k] + hi[k]) / 2 for k in range(3)),
                                 tuple(hi[k] - lo[k] for k in range(3)))
        obj = geometry.bm_to_object(bm, f"Shelf_Stock_{finish}", collection,
                                    bevel=0.0, texel=1.4, rng=rng, wear=wear)
        objs.append(obj)
        stock_objs[finish] = obj

    # collision: the full unit as one solid (cover object; per-shelf collision
    # is loot-system territory, not the shell's)
    cboxes.append(((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h)))

    surface = materials.make_material(
        f"M_Shelf_{plan['material']}", plan["color"], plan["material"])
    frame = materials.make_material(
        f"M_Shelf_frame_{plan['material']}", _darker(plan["color"]),
        plan["material"])
    frame_objs = [o for o in structure
                  if "Upright" in o.name or "Back" in o.name]
    materials.assign([o for o in structure if o not in frame_objs], surface)
    materials.assign(frame_objs, frame)
    for finish, obj in stock_objs.items():
        colour, kind = _shelf_stock.PALETTE[finish]
        materials.assign([obj], materials.make_material(
            f"M_Shelf_stock_{finish}", colour, kind))
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_shelf_top": (0.0, 0.0, h)}}
