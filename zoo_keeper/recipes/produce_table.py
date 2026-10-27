"""produce_table recipe: a supermarket's produce table -- a skirted cabinet, a bed sloped to the shopper, bays of fruit
and vegetables heaped in mounds, a price card at each bay's front.

Zoo 1.132.0, from the walker's grocery comps (the factory's docs/reference/GROCERY_STORE_COMPS.md, 2026-10-26): "a
retro produce section ... neatly arranged fruit and vegetables", produce on tables and in baskets under a category
sign, the comps' 1990s supermarket. REFERENCE: the common wet-rack produce table of the period -- a cabinet skirted
in dark green, its top a bed raked toward the aisle so the back row is higher than the front, divided into bays a
produce kind each, a low rim at the front that holds the heap, a white price card clipped to the rim.

TWO MATERIALS, ONE FOR WOOD AND ONE FOR WHAT IS ON IT. The skirt's green, the rim's and dividers' wood, every heap's
colour and the cards' white are COLOUR-ONLY variation, so they ride the `Wear` vertex colour (`geometry.tint_wear`,
the draw-call rule: "never express colour-only variation as a new material"), and a table is two submissions however
many bays it carries.

THE HEAPS ARE THE VARIANT. Which produce lies in which bay is `PRODUCE[(variant + i) % len(PRODUCE)]`, so tables of
one size in one store differ in their stock rather than standing as one module repeated.

Recipe frame: centre pivot, the FRONT (the shopper's side) at -y, as `chair.py`'s. The module is exactly (w, d, h):
the cabinet is the slot's footprint, and the back riser on the bed's high edge reaches the slot's top.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

#: (name, linear RGB): what lies in a bay, in the order a table's bays take them
PRODUCE = (
    ("apples", (0.55, 0.06, 0.05)),
    ("oranges", (0.85, 0.32, 0.03)),
    ("lemons", (0.86, 0.72, 0.10)),
    ("greens", (0.16, 0.40, 0.08)),
    ("potatoes", (0.42, 0.30, 0.17)),
    ("onions", (0.70, 0.52, 0.28)),
    ("grapes", (0.25, 0.08, 0.22)),
    ("limes", (0.30, 0.55, 0.10)),
)
SKIRT = (0.07, 0.20, 0.10)       # the cabinet's dark green
WOOD = (1.0, 1.0, 1.0)           # the rim and dividers keep the style's own wood
CARD = (0.95, 0.95, 0.92)
#: the bed: its front edge this fraction of the height, its back the full height less the heap
BED_FRONT = 0.72
BAY_W = 0.6                      # a bay's width, about; a table takes round(span / BAY_W) of them
RIM_H = 0.06
RIM_T = 0.03
DIV_T = 0.02
HEAP_H = 0.20                    # a heap's crown above the bed, heaped well over the rim
CARD_W, CARD_H, CARD_T = 0.12, 0.08, 0.006
HEAP_JITTER = 0.025
BURY = 0.01
#: NO TWO FACES SHARE A PLANE (`tests/test_coincident_faces.py`): the rim, dividers and back board stop this short of
#: the slot's ends, the bed starts behind the rim, and the bed's two steps overlap rather than meet.
FACE_GAP = 0.005


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    variant = int(plan.get("variant") or (plan.get("params") or {}).get("variant") or 0)
    rng = streams.stream("wear")
    wood_objs, stock_objs, cboxes = [], [], []
    z0, y0, y1 = -h / 2.0, -d / 2.0, d / 2.0

    def part(name, boxes, rgb, into):
        bm = geometry.new_bm()
        for centre, size in boxes:
            geometry.add_box(bm, centre, size)
        o = geometry.bm_to_object(bm, name, collection, bevel=bevel, texel=1.2, rng=rng, wear=wear)
        geometry.tint_wear(o, rgb)
        into.append(o)

    # the bed's height at the front and back, and at a depth y (a straight rake)
    top = h / 2.0 - HEAP_H
    front = z0 + h * BED_FRONT - HEAP_H

    def bed_z(y):
        return front + (top - front) * (y - y0) / d

    # the cabinet: the slot's footprint, from the floor to under the bed's low edge
    cab_top = front - BURY
    part("ProduceTable_Skirt", [((0.0, 0.0, (z0 + cab_top) / 2.0), (w, d, cab_top - z0))], SKIRT, wood_objs)
    # the bed: a raked slab, built as thin steps so it is boxes, its underside into the cabinet
    steps = 2
    slabs = []
    bed_y0 = y0 + RIM_T - BURY                  # behind the rim's front face, into the rim
    for k in range(steps):
        ya = bed_y0 + (y1 - bed_y0) * k / steps
        yb = bed_y0 + (y1 - bed_y0) * (k + 1) / steps
        if k < steps - 1:
            yb += BURY                          # into the next step, not on its face
        zt = bed_z((ya + yb) / 2.0) - 0.5 * BURY * k
        slabs.append(((0.0, (ya + yb) / 2.0, (cab_top + zt) / 2.0), (w, yb - ya, zt - cab_top + BURY)))
    part("ProduceTable_Bed", slabs, WOOD, wood_objs)
    # the rim at the front, and dividers between the bays
    bays = max(2, int(round(w / BAY_W)))
    bw = w / bays
    part("ProduceTable_Rim", [((0.0, y0 + RIM_T / 2.0, front + RIM_H / 2.0), (w - 2.0 * FACE_GAP, RIM_T, RIM_H + BURY))],
         WOOD, wood_objs)
    # a divider is a low board on the bed, a rim's height above it at its middle -- the heaps stand over it
    divs = []
    for i in range(1, bays):
        x = -w / 2.0 + i * bw
        # from inside the rim to inside the back board, never on either's face
        # (half a bury into the rim: a whole one is the bed's own front face)
        dy0, dy1 = y0 + RIM_T - 0.5 * BURY, y1 - RIM_T - FACE_GAP + BURY
        # its foot inside the cabinet's top, below every step of the bed, its head a rim over the bed's middle
        dz0, dz1 = cab_top + 0.3 * BURY, bed_z(0.0) + RIM_H
        divs.append(((x, (dy0 + dy1) / 2.0, (dz0 + dz1) / 2.0), (DIV_T, dy1 - dy0, dz1 - dz0)))
    if divs:
        part("ProduceTable_Dividers", divs, WOOD, wood_objs)
    # the back riser: a board along the bed's high edge up to the slot's top, which holds the back of every heap
    # and is where a category sign is clipped
    part("ProduceTable_Back", [((0.0, y1 - RIM_T / 2.0 - FACE_GAP, (top - BURY + h / 2.0) / 2.0),
                                (w - 2.0 * FACE_GAP, RIM_T, h / 2.0 - top + BURY))], WOOD, wood_objs)
    # a heap a bay: an ellipsoid low on the bed, its crown at the slot's top at the back
    for i in range(bays):
        name, rgb = PRODUCE[(variant + i) % len(PRODUCE)]
        bm = geometry.new_bm()
        cx = -w / 2.0 + (i + 0.5) * bw
        cy = (y0 + y1) / 2.0
        rx, ry = bw / 2.0 - DIV_T, d / 2.0 - RIM_T
        # the crown at the slot's top less a hair, the base buried in the bed
        cz = h / 2.0 - HEAP_H - 0.005
        verts = geometry.add_ellipsoid(bm, (cx, cy, cz), (rx, ry * 0.9, HEAP_H), u_seg=8, v_seg=4)
        # a heap is lumps, not a gem: every vertex moved a little, from the module's own stream
        geometry.jitter_verts(verts, rng, HEAP_JITTER)
        o = geometry.bm_to_object(bm, "ProduceTable_Heap_%d" % i, collection, bevel=0.0, texel=1.2, rng=rng,
                                  wear=wear)
        geometry.tint_wear(o, rgb)
        stock_objs.append(o)
    # a price card on the rim at each bay's front
    cards = [((-w / 2.0 + (i + 0.5) * bw, y0 - CARD_T / 2.0 + BURY, front + RIM_H + CARD_H / 2.0 - BURY),
              (CARD_W, CARD_T, CARD_H)) for i in range(bays)]
    part("ProduceTable_Cards", cards, CARD, stock_objs)

    # the module is the slot: clip nothing, but assert the heaps stay inside it
    cboxes.append(((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, h / 2.0)))
    wood = materials.make_material(f"M_ProduceTable_{plan['material']}", plan["color"], plan["material"])
    stock = materials.make_material("M_ProduceTable_stock", (1.0, 1.0, 1.0), "plastic")
    materials.assign(wood_objs, wood)
    materials.assign(stock_objs, stock)
    return {"objects": wood_objs + stock_objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
