"""A vault's wall of safe-deposit boxes, as the walker's comp 12 shows one (1.140.0): numbered steel doors with a
brass lock each, larger boxes in the bottom rows, and a few boxes drawn.

The factory's docs/reference/BANK_INTERIOR_COMPS.md, comp 12: "a free-standing bank of numbered steel boxes with brass
locks, several pulled open". Until 1.140.0 the wall was a grid of dividers on a backing, and the recipe's own note left
"numbers, handles and keyholes" to "a Delco art pass" that nobody made; built on Deli Counter's wall material, it stood
in concrete (the factory's docs/findings/bank_interior/, frames 09 and 10).

REFERENCE: a 1990s bank's box wall. Rows of doors on a steel frame, the small boxes (2 x 5 in fronts, about 5 x 13 cm)
in most rows and the large ones (5 x 10 in and up) at the bottom, where they are easy to lift out. Each door carries
TWO keyholes side by side in a brass escutcheon -- the guard's key and the renter's, both needed -- and a stamped
number plate. A renter's box is drawn out whole and carried to a booth, so a drawn box is a dark empty cell, not a door
swung open: a door hinged into the room would stand outside the slot's exact dims.

ONE MATERIAL. The doors are the backing's front face and the frame is the dividers, as before; the escutcheons, the
number plates and a drawn box's dark cell are COLOUR ONLY, in the `Wear` vertex colour (`geometry.tint_wear`), the
check desk's brass pockets' rule. One submission a wall however many boxes it has.

Pure: no Blender. `recipes/safe_deposit_boxes.py` draws what `layout` returns.
"""
from __future__ import annotations

import random

#: the door face is the backing's front, `FRAME_PROUD` behind the frame's: a box wall's doors stand nearly flush in
#: their frame. 1.139.0's frame stood 30 % of the depth proud (9 cm on a 0.3 m wall), and the first render of the
#: hardware read as pigeonholes.
FRAME_PROUD = 0.015
#: the bottom `LARGE_ROWS` rows are boxes of two rows' height (at most half the rows)
LARGE_ROWS = 2
#: the lock: one escutcheon carrying both keyholes, on the door's right as a person facing it sees it (-x: the doors
#: face +y), at its middle
LOCK_W, LOCK_H = 0.040, 0.026
#: the number plate, on the door's upper left (+x)
PLATE_W, PLATE_H = 0.036, 0.012
#: hardware stands this far proud of the door, and runs `BURY` into it
HW_T = 0.003
BURY = 0.002
#: where a stile and a rail cross they share no face: the rail's front stands `RAIL_BACK` behind the stile's and its
#: back `STILE_BURY - BURY` in front of the stile's -- both past the coplanar census's 2 mm tolerance
#: (tools/coplanar_census.py), which a first 1 mm setback was not
RAIL_BACK = 0.003
STILE_BURY = 0.006
#: a drawn box's cell: dark, inset from the frame by `DRAWN_INSET`
DRAWN_INSET = 0.004
#: about one box in this many is drawn; at least one on a wall of any size, at most `DRAWN_MAX`
DRAWN_SHARE = 25
DRAWN_MAX = 6

STEEL = (1.0, 1.0, 1.0)
BRASS = (0.80, 0.63, 0.30)
PLATE = (0.88, 0.82, 0.62)
DRAWN = (0.06, 0.06, 0.07)


def grid_count(usable, cell, cap):
    n = int(round(usable / cell)) if cell > 1e-6 else 1
    return max(1, min(n, int(cap)))


def grid(w, h, params):
    """``(uw, uh, cols, rows, margin, bar)``: the frame's usable span and its columns and rows, the recipe's rule
    since 1.0."""
    p = params or {}
    cell = float(p.get("cell", 0.22))
    bar = float(p.get("bar", 0.03))
    margin = min(float(p.get("margin", 0.06)), min(w, h) * 0.3)
    uw = max(0.05, w - 2.0 * margin)
    uh = max(0.05, h - 2.0 * margin)
    cols = grid_count(uw, cell, int(p.get("max_cols", 16)))
    rows = grid_count(uh, cell, int(p.get("max_rows", 16)))
    return uw, uh, cols, rows, margin, bar


def row_bounds(uh, rows):
    """The z of every horizontal divider, bottom to top: one a row boundary, except that the bottom `LARGE_ROWS`
    boxes are two rows high, so every other boundary under them is left out."""
    ch = uh / rows
    large = min(LARGE_ROWS, rows // 4)
    skip = {2 * k + 1 for k in range(large)}
    return [-uh / 2.0 + j * ch for j in range(rows + 1) if j not in skip]


def cells(w, h, params):
    """Every box's door as ``(i, j, x0, z0, x1, z1)``: column ``i``, row ``j`` from the bottom, its opening between
    the dividers' faces."""
    uw, uh, cols, rows, _margin, bar = grid(w, h, params)
    cw = uw / cols
    zs = row_bounds(uh, rows)
    out = []
    for j in range(len(zs) - 1):
        for i in range(cols):
            x = -uw / 2.0 + i * cw
            out.append((i, j, x + bar / 2.0, zs[j] + bar / 2.0, x + cw - bar / 2.0, zs[j + 1] - bar / 2.0))
    return out


def drawn(n, seed):
    """Which of ``n`` boxes are drawn: about one in `DRAWN_SHARE`, at least one, at most `DRAWN_MAX`, by ``seed``."""
    k = max(1, min(DRAWN_MAX, n // DRAWN_SHARE))
    return set(random.Random(int(seed)).sample(range(n), min(k, n)))


def layout(w, d, h, params=None, seed=0):
    """``[(part, [(centre, size), ...], rgb)]`` in the recipe frame (centre pivot, the doors facing +y), exactly
    (w, d, h): the backing, the frame, and each door's lock and number plate, or its dark cell where the box is
    drawn."""
    uw, uh, cols, rows, _margin, bar = grid(w, h, params)
    front_d = min(FRAME_PROUD, d * 0.3)
    back_d = d - front_d
    door = -d / 2.0 + back_d                       # the doors' face
    cw = uw / cols
    parts = [("SafeDepositBoxes_Backing", [((0.0, -d / 2.0 + back_d / 2.0, 0.0), (w, back_d, h))], STEEL)]
    # NO TWO OF THE FRAME'S FACES SHARE A PLANE (1.140.0): every bar runs into the doors' face rather than onto it,
    # the stiles deeper than the rails, and the rails stand `RAIL_BACK` behind the stiles' front, so where they cross
    # neither a front nor a back is shared. 1.139.0's frame was every one of the species' 884 coincident pairs
    # (tests/test_coincident_faces.py).
    v0, v1 = door - STILE_BURY, d / 2.0
    r0, r1 = door - BURY, d / 2.0 - RAIL_BACK
    frame = [((-uw / 2.0 + i * cw, (v0 + v1) / 2.0, 0.0), (bar, v1 - v0, uh)) for i in range(cols + 1)]
    frame += [((0.0, (r0 + r1) / 2.0, z), (uw, r1 - r0, bar)) for z in row_bounds(uh, rows)]
    parts.append(("SafeDepositBoxes_Divider", frame, STEEL))
    doors = cells(w, h, params)
    out = drawn(len(doors), seed)
    hw_y = door + (HW_T - BURY) / 2.0
    hw_d = HW_T + BURY
    locks, plates, holes = [], [], []
    for k, (_i, _j, x0, z0, x1, z1) in enumerate(doors):
        if k in out:
            holes.append((((x0 + x1) / 2.0, hw_y, (z0 + z1) / 2.0),
                          (x1 - x0 - 2.0 * DRAWN_INSET, hw_d, z1 - z0 - 2.0 * DRAWN_INSET)))
            continue
        lw, lh = min(LOCK_W, (x1 - x0) * 0.4), min(LOCK_H, (z1 - z0) * 0.5)
        locks.append(((x0 + 0.012 + lw / 2.0, hw_y, (z0 + z1) / 2.0), (lw, hw_d, lh)))
        pw, ph = min(PLATE_W, (x1 - x0) * 0.4), min(PLATE_H, (z1 - z0) * 0.25)
        plates.append(((x1 - 0.010 - pw / 2.0, hw_y, z1 - 0.010 - ph / 2.0), (pw, hw_d, ph)))
    parts.append(("SafeDepositBoxes_Lock", locks, BRASS))
    parts.append(("SafeDepositBoxes_Plate", plates, PLATE))
    if holes:
        parts.append(("SafeDepositBoxes_Drawn", holes, DRAWN))
    return parts
