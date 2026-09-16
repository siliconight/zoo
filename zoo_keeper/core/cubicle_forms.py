"""Cubicle bank layout: pure plan, no bpy.

Every box the species builds is decided here and executed by
`recipes/cubicle_bank.py`, so the arithmetic that matters -- where the aisle
is, how wide a bay is, whether a panel is tall enough to carry a binder bin --
is testable without Blender, the way `club_forms` and `cigarette_forms` are.

REFERENCE (genome licence notes): a 1990s panel system -- Herman Miller
Action Office, Steelcase 9000. Fabric-faced acoustic screens 1.2-1.7 m tall
on levelling feet, a painted frame with a top trim cap, work surfaces
cantilevered off the panel rails at 0.74 m, a drawer pedestal under each, an
overhead binder bin on the spine where the panel reaches over it, and pods
back to back in rows with a circulation aisle between them.

FRAME AND UNITS. The species' own space, metres, Z-up, base at z = 0 and the
plan centred on x = y = 0; `bpylayer.build` re-centres the finished module,
so the pivot is enforced rather than declared (`core.pivot`).
"""
from __future__ import annotations

from ..recipes._bays import bays

#: Panel thickness: a fabric-faced acoustic screen is 50-65 mm over its frame.
SCREEN_T = 0.06
#: The painted trim cap along the top of every screen.
CAP_T = 0.025
#: A levelling foot's plan size and height.
FOOT_W = 0.09
FOOT_H = 0.035
#: Work-surface slab thickness, and the rail it is cantilevered on.
SURF_T = 0.03
RAIL_T = 0.04
#: Drawer pedestal width, and the gap between its top and the surface above.
PED_W = 0.42
PED_GAP = 0.02
#: How far a cross screen runs from the spine toward the aisle, as a fraction
#: of the band's depth. Less than one BY DEFINITION: the open side is the
#: cubicle's doorway, and closing it would turn the aisle into a row of
#: alcoves and the bank back into a solid.
CROSS_F = 0.62
#: The overhead binder bin: its underside, its height, its depth. A bin needs
#: a panel that reaches over it, so a bank whose screens stop below
#: ``BIN_Z + BIN_H`` gets none -- which is why the library's 1.2 m banks have
#: none and a 1.7 m one would.
BIN_Z = 1.02
BIN_H = 0.32
BIN_D = 0.31

#: Material keys the recipe resolves: the screens' fabric (the genome's, via
#: `dna.UPHOLSTERED`), the painted frame, and the laminate work surfaces.
FABRIC, FRAME, TOP = "fabric", "frame", "top"


def bands(depth, row_min, row_max, aisle_min):
    """``([(y_centre, band_depth), ...], aisle_width)``.

    Two pod bands back to back with a real aisle when the depth carries both,
    one band filling the depth when it does not. A band is capped at
    ``row_max`` and every surplus metre goes to the aisle: a 3 m deep cubicle
    is not a thing and a wide aisle is. The outermost band edges are always
    +/- depth/2, so the built bounds are the slot's at every depth.
    """
    d = float(depth)
    if d < 2.0 * row_min + aisle_min - 1e-9:
        return [(0.0, d)], 0.0
    row_d = min(row_max, (d - aisle_min) / 2.0)
    aisle = d - 2.0 * row_d
    return [(-(d - row_d) / 2.0, row_d), ((d - row_d) / 2.0, row_d)], aisle


def plan(w, d, h, params, variant=0):
    """Everything the recipe builds.

    ``{"boxes": [(name, material_key, (cx, cy, cz), (sx, sy, sz), solid)],
       "regions": [...],  # `_surface_stock.plan_surface` rows, one per bay
       "facts": {...}}``

    ``solid`` is whether the box declares collision. A drawer front, a handle,
    a rail and a levelling foot do not: they sit inside or under something
    that already does, and a collider per drawer is 24 shapes a body can
    never touch. The aisle and the knee space under every surface declare
    nothing at all, which is the point of the species.
    """
    w, d, h = float(w), float(d), float(h)
    row_min = float(params.get("row_min", 1.7))
    row_max = float(params.get("row_max", 2.4))
    aisle_min = float(params.get("aisle_min", 1.1))
    surf_h = min(float(params.get("surface_h", 0.74)), max(0.3, h - 0.2))
    surf_d = float(params.get("surface_d", 0.75))
    bay_max = float(params.get("bay_max", 2.0) or 0.0)
    variant = int(variant or 0)

    runs = bays(w, bay_max)
    rows, aisle = bands(d, row_min, row_max, aisle_min)
    screen_h = h - CAP_T
    boxes, regions = [], []
    bins = 0

    for bi, (by, bd) in enumerate(rows):
        # `out` is +1 for a band whose spine stands on the +Y edge; its
        # sitters face -Y, into the aisle. One band alone takes +Y.
        out = 1 if (by >= 0.0 or len(rows) == 1) else -1
        tag = "" if len(rows) == 1 else f"_B{bi + 1}"
        spine_y = by + out * (bd / 2.0 - SCREEN_T / 2.0)
        boxes.append((f"CubicleBank_Spine{tag}", FABRIC,
                      (0.0, spine_y, screen_h / 2.0),
                      (w, SCREEN_T, screen_h), True))
        boxes.append((f"CubicleBank_Cap{tag}", FRAME,
                      (0.0, spine_y, screen_h + CAP_T / 2.0),
                      (w, SCREEN_T, CAP_T), False))

        cross_d = bd * CROSS_F
        cross_y = spine_y - out * cross_d / 2.0
        edges = ([runs[0][0] - runs[0][1] / 2.0]
                 + [bx + bw / 2.0 for bx, bw in runs])
        # A cross screen on the bank's own edge is pulled in by HALF A FOOT,
        # not half a panel: the levelling foot under it is FOOT_W wide and
        # the panel only SCREEN_T, so clamping to the panel put 15 mm of
        # foot outside the slot on each side and the built width read 8.03
        # against an 8.00 slot -- which `validate.fit_width` measures to 2 cm
        # and `core.pivot` re-centres from. Measured before the clamp moved:
        # bounds x -4.015 .. 4.015.
        edge_in = max(SCREEN_T, FOOT_W) / 2.0
        for ci, ex in enumerate(edges):
            cx = min(max(ex, -w / 2.0 + edge_in), w / 2.0 - edge_in)
            boxes.append((f"CubicleBank_Cross{tag}_{ci}", FABRIC,
                          (cx, cross_y, screen_h / 2.0),
                          (SCREEN_T, cross_d, screen_h), True))
            boxes.append((f"CubicleBank_Cap{tag}_x{ci}", FRAME,
                          (cx, cross_y, screen_h + CAP_T / 2.0),
                          (SCREEN_T, cross_d, CAP_T), False))
            boxes.append((f"CubicleBank_Foot{tag}_{ci}", FRAME,
                          (cx, cross_y - out * (cross_d / 2.0 - FOOT_W / 2.0),
                           FOOT_H / 2.0),
                          (FOOT_W, FOOT_W, FOOT_H), False))

        for ai, (bx, bw) in enumerate(runs):
            btag = f"{tag}_{ai + 1}"
            inner = bw - 2.0 * SCREEN_T
            sd = min(surf_d, cross_d - 0.15)
            if inner < 0.3 or sd < 0.3:
                continue
            surf_y = spine_y - out * (SCREEN_T / 2.0 + sd / 2.0)
            boxes.append((f"CubicleBank_Surface{btag}", TOP,
                          (bx, surf_y, surf_h - SURF_T / 2.0),
                          (inner, sd, SURF_T), True))
            boxes.append((f"CubicleBank_Rail{btag}", FRAME,
                          (bx, spine_y - out * (SCREEN_T / 2.0 + RAIL_T / 2.0),
                           surf_h - SURF_T - 0.05),
                          (inner, RAIL_T, 0.06), False))
            side = 1 if (ai + bi + variant) % 2 == 0 else -1
            n_drawers = 3 if (variant + ai) % 3 == 0 else 2
            ped_x = bx + side * (inner / 2.0 - PED_W / 2.0)
            ped_h = surf_h - SURF_T - PED_GAP
            boxes.append((f"CubicleBank_Pedestal{btag}", TOP,
                          (ped_x, surf_y, ped_h / 2.0),
                          (PED_W, sd * 0.92, ped_h), True))
            gap = 0.012
            dh = (ped_h - gap * (n_drawers + 1)) / n_drawers
            front_y = surf_y - out * (sd * 0.92 / 2.0 + 0.009)
            for k in range(n_drawers):
                z = gap + dh / 2.0 + k * (dh + gap)
                boxes.append((f"CubicleBank_Drawer{btag}_{k + 1}", TOP,
                              (ped_x, front_y, z),
                              (PED_W - 0.03, 0.018, dh), False))
                boxes.append((f"CubicleBank_Handle{btag}_{k + 1}", FRAME,
                              (ped_x, front_y - out * 0.018, z),
                              (PED_W * 0.45, 0.015, 0.015), False))
            if screen_h >= BIN_Z + BIN_H and (variant + ai + bi) % 4 != 3:
                bin_d = min(BIN_D, sd * 0.5)
                boxes.append((f"CubicleBank_Bin{btag}", FRAME,
                              (bx, spine_y - out * (SCREEN_T / 2.0 + bin_d / 2.0),
                               BIN_Z + BIN_H / 2.0),
                              (inner * 0.92, bin_d, BIN_H), True))
                bins += 1
            regions.append((bx - inner / 2.0, bx + inner / 2.0,
                            surf_y - sd / 2.0, surf_y + sd / 2.0, surf_h,
                            3.141592653589793 if out > 0 else 0.0, 0.5, ()))

    return {"boxes": boxes, "regions": regions,
            "facts": {"bands": len(rows), "bays": len(runs),
                      "aisle_m": round(aisle, 4),
                      "band_depth_m": round(rows[0][1], 4),
                      "screen_h_m": round(screen_h, 4),
                      "bins": bins, "variant": variant,
                      "solids": sum(1 for b in boxes if b[4])}}


def bounds(boxes):
    """The plan's own extents -- what `validate.fit_*` measures on the built
    module. A test asserts these are the slot's dims before Blender is asked."""
    lo = [min(c[i] - s[i] / 2.0 for _n, _m, c, s, _k in boxes) for i in range(3)]
    hi = [max(c[i] + s[i] / 2.0 for _n, _m, c, s, _k in boxes) for i in range(3)]
    return tuple(lo), tuple(hi)
