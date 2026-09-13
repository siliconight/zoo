"""What sits on a shelf: a Delco-1997 back office and stockroom, planned in
pure Python (no bpy) so the layout is unit-testable.

"Nothing in the cabinets" (the walker). A shelving unit with bare boards
reads as a fixture nobody uses; a stockroom rack reads as a stockroom because
of what is on it. This module decides the contents of one shelf span -- boxes,
binders, ledgers, cans -- and `shelving.build` turns each item into geometry.

THE RULES EVERY ITEM KEEPS, each one a thing a render or a z-buffer punishes:

  * NOTHING OVERHANGS. Every footprint lies inside the span it was given:
    x between the uprights, y between the board's front edge and the back
    panel, top below the board above less HEADROOM.
  * NOTHING SHARES A PLANE. Side-by-side items keep at least MIN_GAP between
    them. An item rests SINK below the surface it stands on, so its bottom is
    inside the board (or the item below) rather than on its top face. A
    stacked item differs from the one below by at least STACK_STEP on every
    side, so the two never share a side plane inside the SINK band.
  * DETERMINISTIC. Every choice comes from the ``rng`` passed in, which the
    recipe draws from its own named stream.

Coordinates are metres in the recipe's frame: x along the run, y front (-)
to back (+) with the open side toward -Y, z up. Colours are linear RGB.

THE PALETTE is chosen for contrast with the shelf, which every shelving style
paints a mid grey (linear 0.43-0.62) and whose uprights and back panel are
that grey at 0.7. Each finish is either well darker (binders, ledgers, kraft
cardboard, coffee cans) or well lighter (banker's boxes) than both;
`tests/test_shelf_stock.py` checks a luminance ratio of at least 1.4 against
every style colour in the genome and its frame shade. 1.4 is chosen, not
derived: it is where the first palette's weakest finish failed. The kinds are ones whose Pixelcoat
packs are tintable (paper, plastic, metal_painted), so the colour survives a
skin library as well as the flat path.
"""
from __future__ import annotations

HEADROOM = 0.02     # clearance under the board above
MIN_GAP = 0.004     # between neighbouring items
SINK = 0.003        # an item's bottom sits this far inside what it stands on
STACK_STEP = 0.006  # a stacked item's sides differ from the one below by this
EDGE = 0.01         # kept clear of the uprights and the board's front edge
BACK_GAP = 0.006    # kept clear of the back panel

#: finish -> (linear RGB, material kind)
PALETTE = {
    "kraft":        ([0.30, 0.19, 0.09], "paper"),     # corrugated cardboard
    "banker":       ([0.86, 0.83, 0.72], "paper"),     # file storage box
    "binder_black": ([0.035, 0.035, 0.04], "plastic"),
    "binder_navy":  ([0.05, 0.08, 0.24], "plastic"),
    "binder_maroon": ([0.30, 0.05, 0.07], "plastic"),
    "binder_green": ([0.06, 0.18, 0.10], "plastic"),
    "ledger_green": ([0.08, 0.20, 0.12], "paper"),     # cloth-bound record book
    "ledger_red":   ([0.34, 0.07, 0.06], "paper"),
    # [0.30, 0.22, 0.13] first; its luminance ratio against the darker frame
    # grey of the delco and industrial_flats styles was 1.29-1.35
    "ledger_tan":   ([0.22, 0.15, 0.08], "paper"),
    "can_blue":     ([0.08, 0.16, 0.42], "metal_painted"),   # coffee can
    "can_red":      ([0.50, 0.08, 0.06], "metal_painted"),
}

BINDERS = ("binder_black", "binder_navy", "binder_maroon", "binder_green")
LEDGERS = ("ledger_green", "ledger_red", "ledger_tan")
CANS = ("can_blue", "can_red")


def _box(finish, x0, x1, y0, y1, z0, z1):
    return {"shape": "box", "finish": finish,
            "min": (x0, y0, z0), "max": (x1, y1, z1)}


def _cyl(finish, cx, cy, r, z0, z1):
    return {"shape": "cyl", "finish": finish,
            "min": (cx - r, cy - r, z0), "max": (cx + r, cy + r, z1)}


def _front_back(rng, y_front, y_back, depth):
    """Place an item ``depth`` deep: pulled toward the aisle with a small
    random setback, never past the back limit."""
    room = (y_back - y_front) - depth
    set_back = rng.uniform(0.0, min(0.04, max(0.0, room)))
    y0 = y_front + set_back
    return y0, y0 + depth


def _binders(rng, x, x1, yf, yb, z0, clear):
    tall = clear - HEADROOM
    if tall < 0.22 or (yb - yf) < 0.22:
        return [], x
    base = rng.choice(BINDERS)
    sz = min(tall, rng.uniform(0.27, 0.305))
    sy = min(yb - yf, rng.uniform(0.24, 0.27))
    y0, y1 = _front_back(rng, yf, yb, sy)
    out = []
    for _ in range(rng.randint(3, 10)):
        t = rng.choice((0.035, 0.05, 0.05, 0.065, 0.08))
        if x + t > x1:
            break
        fin = base if rng.random() < 0.75 else rng.choice(BINDERS)
        # a binder's front edge wanders a centimetre or two: nobody shelves
        # them flush
        jy = rng.uniform(0.0, min(0.02, max(0.0, yb - y1)))
        out.append(_box(fin, x, x + t, y0 + jy, y1 + jy, z0 - SINK, z0 + sz))
        x += t + rng.uniform(MIN_GAP, 0.009)
    return out, x


def _stack(rng, finish_of, x, x1, yf, yb, z0, tall, sx, sy, heights):
    """A stack of boxes, each STACK_STEP or more smaller than the one below on
    every side, so no side plane is shared. Returns items and the used width."""
    out = []
    if x + sx > x1:
        return out, x
    y0, y1 = _front_back(rng, yf, yb, sy)
    bx0, bx1 = x, x + sx
    base = z0 - SINK
    top = z0
    for k, hgt in enumerate(heights):
        if k:
            # shrink every side by STACK_STEP..2 x STACK_STEP
            d = [rng.uniform(STACK_STEP, 2.0 * STACK_STEP) for _ in range(4)]
            nx0, nx1, ny0, ny1 = bx0 + d[0], bx1 - d[1], y0 + d[2], y1 - d[3]
            if nx1 - nx0 < 0.05 or ny1 - ny0 < 0.05:
                break
            bx0, bx1, y0, y1 = nx0, nx1, ny0, ny1
            base = top - SINK
        if (base + SINK + hgt) - z0 > tall:
            break
        top = base + SINK + hgt
        out.append(_box(finish_of(k), bx0, bx1, y0, y1, base, top))
    return out, x + sx


def _boxes(rng, x, x1, yf, yb, z0, clear):
    tall = clear - HEADROOM
    if tall < 0.12 or (yb - yf) < 0.18:
        return [], x
    sx = rng.uniform(0.25, 0.48)
    sy = min(yb - yf, rng.uniform(0.25, 0.45))
    h1 = min(tall, rng.uniform(0.14, 0.34))
    heights = [h1]
    if tall - h1 > 0.14 and rng.random() < 0.4:
        heights.append(min(tall - h1, rng.uniform(0.12, 0.28)))
    return _stack(rng, lambda k: "kraft", x, x1, yf, yb, z0, tall,
                  sx, sy, heights)


def _bankers(rng, x, x1, yf, yb, z0, clear):
    """File storage boxes: 0.31 x 0.39 x 0.26, turned to fit a shallow shelf."""
    tall = clear - HEADROOM
    if tall < 0.265 or (yb - yf) < 0.31:
        return [], x
    sx, sy = (0.31, 0.39) if (yb - yf) >= 0.39 else (0.39, 0.31)
    out = []
    for _ in range(rng.randint(1, 4)):
        heights = [0.26, 0.26] if (tall >= 0.53 and rng.random() < 0.5) else [0.26]
        got, nx = _stack(rng, lambda k: "banker", x, x1, yf, yb, z0, tall,
                         sx, sy, heights)
        if not got:
            break
        out += got
        x = nx + rng.uniform(MIN_GAP, 0.02)
    return out, x


def _ledgers(rng, x, x1, yf, yb, z0, clear):
    tall = clear - HEADROOM
    if tall < 0.04 or (yb - yf) < 0.2:
        return [], x
    sx = rng.uniform(0.28, 0.36)
    sy = min(yb - yf, rng.uniform(0.21, 0.28))
    heights = []
    for _ in range(rng.randint(2, 6)):
        heights.append(rng.uniform(0.025, 0.05))
    colours = [rng.choice(LEDGERS) for _ in heights]
    return _stack(rng, lambda k: colours[k], x, x1, yf, yb, z0, tall,
                  sx, sy, heights)


def _cans(rng, x, x1, yf, yb, z0, clear):
    tall = clear - HEADROOM
    if tall < 0.1 or (yb - yf) < 0.1:
        return [], x
    r = min((yb - yf) / 2.0, rng.uniform(0.05, 0.08))
    hgt = min(tall, rng.uniform(0.11, 0.18))
    fin = rng.choice(CANS)
    out = []
    for _ in range(rng.randint(2, 6)):
        if x + 2 * r > x1:
            break
        y0, _y1 = _front_back(rng, yf, yb, 2 * r)
        out.append(_cyl(fin, x + r, y0 + r, r, z0 - SINK, z0 + hgt))
        x += 2 * r + rng.uniform(0.008, 0.02)
    return out, x


_GROUPS = ((_binders, 3.0), (_boxes, 3.0), (_bankers, 2.0),
           (_ledgers, 2.0), (_cans, 1.5))


def plan_shelf(rng, x0, x1, y_front, y_back, z0, clear):
    """Items for one shelf: the span ``x0..x1`` by ``y_front..y_back`` on a
    surface at ``z0`` with ``clear`` metres to the underside of the board
    above. Returns a list of items, each ``{shape, finish, min, max}`` with
    ``min``/``max`` its bounding box (a can's is its cylinder's)."""
    x0 += EDGE
    x1 -= EDGE
    y_front += EDGE
    y_back -= BACK_GAP
    items = []
    if x1 - x0 < 0.1 or y_back - y_front < 0.08 or clear - HEADROOM < 0.04:
        return items
    x = x0 + rng.uniform(0.0, 0.06)
    stalls = 0
    while x < x1 - 0.05 and stalls < 6:
        total = sum(wt for _f, wt in _GROUPS)
        pick = rng.uniform(0.0, total)
        for fn, wt in _GROUPS:
            pick -= wt
            if pick <= 0.0:
                break
        got, nx = fn(rng, x, x1, y_front, y_back, z0, clear)
        if not got:
            stalls += 1
            continue
        stalls = 0
        items += got
        x = nx + rng.uniform(0.012, 0.06)
        if rng.random() < 0.22:           # a gap where something was taken
            x += rng.uniform(0.12, 0.4)
    return items
