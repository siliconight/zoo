"""A heap of filled garbage bags, pure (Zoo 1.93.0, roadmap 219 note 11).

The walker, 2026-10-09, after walking club_block_014: "need filled black garbage bags stacked
near the garbage bins". `recipes/trash_bags.py` draws the heap; Lot stands one beside each
building's dumpster. Everything here is the part that needs no Blender: which bags a heap has and
where each sits (`heap`), and how one bag's surface is pushed out of its ellipsoid (`shape`).

WHAT A FILLED BAG IS: a sack that has slumped -- flat where it sits, wider at its belly than a
sphere would be, lumpy where what is in it pushes out, and gathered at the top into a neck and a
knot of its own plastic. A heap is a row of them on the ground across the slot's width and one or
two more thrown on top, leaning into the gaps. Most are black; the odd one is a white kitchen bag
or a green contractor bag, because nobody buys one kind.

ONE MATERIAL, so one draw a heap: the genome's plastic, white, each bag's colour in `Wear`.

FRAME AND UNITS: metres, X across the slot's width, Y along its depth, Z up from the ground at 0;
`build.build_module` re-centres the module.
"""
from __future__ import annotations

import math
import zlib

#: A filled bag's half-sizes when it stands alone, metres: about a 30-gallon bag, slumped.
BAG = (0.24, 0.21, 0.27)
#: How much of a bag's half-height is pressed flat under it, and how much is gathered into its
#: neck at the top.
FLAT = 0.55
NECK = 0.62
#: How far a bag's surface is pushed out by what is in it, of its radius.
LUMP = 0.07
#: The colours a bag comes in, linear RGB. `_colour` makes one bag in twelve white and one green.
COLOURS = {"black": (0.020, 0.020, 0.023), "white": (0.68, 0.68, 0.64),
           "green": (0.030, 0.050, 0.034)}
#: The genome's `module_variants`: a slot's `variant` picks one of these heaps.
VARIANTS = 4


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def _u(*k):
    """A deterministic number in [0, 1) from the keys."""
    return (_h(*k) % 10007) / 10007.0


def _colour(variant, i):
    r = _h("colour", variant, i) % 12
    return "white" if r == 0 else "green" if r == 1 else "black"


def heap(w, d, h, variant=0):
    """The bags of one heap in a ``w`` x ``d`` x ``h`` slot: a list of ``{"centre", "radii",
    "yaw", "lean", "colour", "seed"}``, ``centre`` the bag's middle in recipe space, ``radii`` its
    half-sizes before it is turned, ``yaw`` and ``lean`` degrees. Every bag stands inside the slot
    and the heap fills its width; the top layer rests in the bottom one, not on it, as bags do."""
    v = int(variant or 0) % VARIANTS
    s = min(1.0, h / (2.0 * BAG[2] * 1.35), d / (2.0 * BAG[1]))
    rx, ry, rz = BAG[0] * s, BAG[1] * s, BAG[2] * s
    n_low = max(2, min(5, int(round(w / (2.0 * rx * 0.92)))))
    pitch = (w - 2.0 * rx) / max(1, n_low - 1) if n_low > 1 else 0.0
    bags = []
    for i in range(n_low):
        k = 0.88 + 0.16 * _u("size", v, i)
        radii = (rx * k, ry * (0.90 + 0.12 * _u("depth", v, i)), rz * k)
        x = -w / 2.0 + rx + pitch * i
        y = (d / 2.0 - radii[1]) * (2.0 * _u("y", v, i) - 1.0) * 0.6
        # each bottom stands 3 mm above the last, so no two flat bottoms share a plane
        bags.append({"centre": (x, y, radii[2] * FLAT + 0.002 + 0.003 * i), "radii": radii,
                     "yaw": 360.0 * _u("yaw", v, i), "lean": 14.0 * (_u("lean", v, i) - 0.5),
                     "colour": _colour(v, i), "seed": _h("bag", v, i)})
    # the top layer: one or two bags thrown into the gaps between the bottom row's
    n_top = min(n_low - 1, 1 + v % 2)
    for j in range(n_top):
        gap = (j + 1) * (n_low - 1) / float(n_top + 1)
        a, b = bags[int(math.floor(gap))], bags[min(n_low - 1, int(math.floor(gap)) + 1)]
        x = (a["centre"][0] + b["centre"][0]) / 2.0
        k = 0.82 + 0.12 * _u("tsize", v, j)
        radii = (rx * k, ry * k, rz * k * 0.9)
        z_top = min(h - radii[2], max(a["centre"][2] + a["radii"][2], b["centre"][2] + b["radii"][2])
                    - radii[2] * 0.35)
        bags.append({"centre": (x, 0.0, z_top), "radii": radii,
                     "yaw": 360.0 * _u("tyaw", v, j), "lean": 24.0 * (_u("tlean", v, j) - 0.5),
                     "colour": _colour(v, 10 + j), "seed": _h("top", v, j)})
    return bags


def shape(local, radii, seed):
    """Where one point of a unit-sphere-shaped bag goes: ``local`` its position on the
    ellipsoid of ``radii`` about the bag's centre. Pressed flat under the bag, gathered into the
    neck at the top, lumpy between; deterministic from the point's direction and the bag's seed,
    so a bag is the same bag in every build."""
    x, y, z = local
    rx, ry, rz = radii
    nx, ny, nz = x / rx, y / ry, z / rz                  # on the unit sphere
    # lumps: what is in the bag pushes out, smoothly over its surface
    lump = 1.0 + LUMP * (math.sin(3.1 * nx + 1.7 * (seed % 7)) * math.cos(2.7 * ny + 0.9 * (seed % 5))
                         + 0.6 * math.sin(4.3 * nz + 2.3 * nx + (seed % 11)))
    x, y, z = x * lump, y * lump, z * lump
    # slumped: the belly spreads, the bottom is pressed flat on the ground
    if nz < 0.0:
        spread = 1.0 + 0.12 * (-nz)
        x, y = x * spread, y * spread
    # pressed flat: below the flat line the surface is squeezed to a twentieth of its depth, not
    # clamped onto one plane. RETRACTED, kept: a clamp put every vertex under the line on the
    # same z, and with the lumps a pair of the bottom's triangles folded back to back there
    # (the coplanar probe's one OPP pair on the first heap). Squeezed, the rings keep their order
    # in height, and the bottom still reads flat: about 7 mm of dome on a full-size bag.
    zf = -rz * FLAT
    if z < zf:
        x, y = x * 1.04, y * 1.04
        z = zf + (z - zf) * 0.06
    # the neck: the top gathered toward the axis and drawn up a little
    if nz > NECK:
        t = (nz - NECK) / (1.0 - NECK)
        k = 1.0 - 0.80 * t
        x, y = x * k, y * k
        z = z + rz * 0.10 * t
    return (x, y, z)
