"""A stack of plastic milk crates, decided in pure Python.

Zoo 1.14.0, species `milk_crate_stack`. Deli Counter 0.149.0 furnishes a
walk-in cooler as cold storage -- backstock racks, cartons, "a milk crate
stack" (the task that found a grill in gas_station_a02's walk-in) -- and its
`test_furnish` holds that every furnished piece routes to a species ("a
generated piece that routes to nothing is a grey box, which is the defect
furnishing exists to reduce"). So the crate is Zoo's to grow, and here it is.

WHAT IS BUILT, in the recipe frame (metres, Z up, floor 0, CENTRE pivot):
crates in a grid of ``cols x rows`` a layer, ``layers`` high, each a HOLLOW
open-topped crate -- a bottom plate and four walls -- sitting 4 mm into the
one below, as real crates nest. The walker's standing preference is real
structure: a crate stack is crates, not a box painted like one.

NO TWO FACES SHARE A PLANE: side walls own a crate's footprint, its front
and back walls stand 4 mm in and 4 mm lower; the bottom plate is 4 mm inside
the walls; neighbouring crates in a layer leave 6 mm between them; and every
other layer steps in 6 mm, so a stack's outside faces alternate. The slot is
filled exactly by the even layers' outer walls and the top layer's rim.

ONE SUBMISSION: one plastic material, the stack's colour (one of `COLOURS`,
by variant) in the `Wear` vertex colour.
"""
from __future__ import annotations

import re
import zlib

from . import prims as P

#: Deli Counter's `milk_crates` piece sizes (long side first).
DC_SIZES = ((0.35, 0.35, 1.0), (0.7, 0.35, 1.3), (0.35, 0.35, 0.66), (0.7, 0.7, 1.0))
RANGES = {"width": (0.3, 0.8), "depth": (0.3, 0.8), "height": (0.3, 1.4)}

CRATE = 0.34              # a crate's nominal footprint (13 in)
CRATE_H = 0.28            # and height (11 in)
WALL = 0.012
PLATE = 0.015
NEST = 0.004              # a crate sits this far into the one below
GAP = 0.003               # half the space between neighbouring crates
STEP = 0.006              # every other layer steps in
BURY = 0.004

#: A stack's colour by variant: red, blue, orange, green (linear).
COLOURS = ((0.55, 0.05, 0.04), (0.05, 0.16, 0.50), (0.80, 0.30, 0.02), (0.06, 0.35, 0.10))
KIND = "plastic"
_VARIANT = re.compile(r"_n\d+(?=_|$)")


def resolve(plan_):
    params = plan_.get("params") or {}
    module = plan_.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    return variant


def grid(w, d, h):
    return (max(1, int(round(w / CRATE))), max(1, int(round(d / CRATE))), max(1, int(round(h / CRATE_H))))


def crate(x0, x1, y0, y1, z0, z1):
    """One open-topped crate filling [x0..x1] x [y0..y1] x [z0..z1]."""
    out = [
        # the side walls own the crate's footprint in y and its full height
        P.box("Crate", "crate", (x0, y0, z0 + PLATE - BURY), (x0 + WALL, y1, z1)),
        P.box("Crate", "crate", (x1 - WALL, y0, z0 + PLATE - BURY), (x1, y1, z1)),
        # the front and back walls stand 4 mm in, run into the side walls,
        # and stop 8 mm under the rim -- the crate above sits 4 mm into this
        # one, and at 4 mm its plate lay exactly on their tops
        P.box("Crate", "crate", (x0 + WALL - BURY, y0 + 0.004, z0 + PLATE - 2 * BURY),
              (x1 - WALL + BURY, y0 + 0.004 + WALL, z1 - 0.008)),
        P.box("Crate", "crate", (x0 + WALL - BURY, y1 - 0.004 - WALL, z0 + PLATE - 2 * BURY),
              (x1 - WALL + BURY, y1 - 0.004, z1 - 0.008)),
        # the bottom plate, 30 mm inside the walls: at 4-8 mm its edges came
        # within 2 mm of the crate below's inner faces whichever way the layers
        # stepped. From above it reads as a crate's grid floor with a margin.
        P.box("Crate", "crate", (x0 + 0.030, y0 + 0.030, z0), (x1 - 0.030, y1 - 0.030, z0 + PLATE)),
    ]
    return out


def layout(w, d, h):
    cols, rows, layers = grid(w, d, h)
    cw, cd, ch = w / cols, d / rows, h / layers
    out = []
    for L in range(layers):
        step = STEP if L % 2 else 0.0
        z0 = L * ch - (NEST if L else 0.0)
        z1 = (L + 1) * ch
        for i in range(cols):
            for j in range(rows):
                x0 = -w / 2.0 + i * cw + (GAP if i else step)
                x1 = -w / 2.0 + (i + 1) * cw - (GAP if i < cols - 1 else step)
                y0 = -d / 2.0 + j * cd + (GAP if j else step)
                y1 = -d / 2.0 + (j + 1) * cd - (GAP if j < rows - 1 else step)
                out += crate(x0, x1, y0, y1, z0, z1)
    facts = {"cols": cols, "rows": rows, "layers": layers, "crates": cols * rows * layers,
             "collision": ((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h))}
    return out, facts


def plan(w, d, h):
    prims, facts = layout(w, d, h)
    return {"prims": prims, "facts": facts}


def signed_volume(p):
    vs = p["verts"]
    tot = 0.0
    for f in p["faces"]:
        a = vs[f[0]]
        for k in range(1, len(f) - 1):
            b, c = vs[f[k]], vs[f[k + 1]]
            tot += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return tot / 6.0
