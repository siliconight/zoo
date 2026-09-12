"""Bays: repeat a species' unit along its width to fill a run (roadmap 44).

Deli Counter authors furniture as RUNS -- an 8 m teller counter, a 7 m
shelf aisle, a 3 m locker bank, a 5 m row of desks -- and measured over
1,443 placements (2026-09-11) 579 of the 721 that name a species are
longer than any single unit of it. The `prop` box fills any length because
it is one slab; a desk cannot be 8 m wide. So a run-capable species declares
`bay_max` in its genome params (the widest one unit reads as), opens its
width range to the run, and its recipe builds ``ceil(w / bay_max)`` equal
bays side by side, each inside the unit's own proportions. Equal division,
never a sliver: a 5.0 m desk run at `bay_max` 2.2 is three 1.667 m desks,
not two full ones and a 0.6 m stub.
"""
from __future__ import annotations

import math


def bays(width: float, bay_max: float) -> list[tuple[float, float]]:
    """``[(x_center, bay_width), ...]`` across ``width``, centred on 0.

    ``bay_max`` <= 0 or None means one bay: the species has not opted in and
    its recipe behaves exactly as it always did.
    """
    w = float(width)
    if not bay_max or float(bay_max) <= 0.0 or w <= float(bay_max) + 1e-9:
        return [(0.0, w)]
    n = max(1, int(math.ceil(w / float(bay_max) - 1e-9)))
    bw = w / n
    return [(-w / 2.0 + bw * (i + 0.5), bw) for i in range(n)]


def bay_max_of(plan: dict) -> float:
    """The plan's `bay_max` param, 0.0 when the species has none."""
    try:
        return float((plan.get("params") or {}).get("bay_max") or 0.0)
    except (TypeError, ValueError):
        return 0.0
