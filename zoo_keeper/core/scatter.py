"""Deterministic scatter placement — the 'pile' primitive's brain.

'Model one chunk, duplicate, randomize rotation/scale, join into a pile' is
core to low-poly (PS1/N64) food and clutter. The *placement* is pure math and
lives here so it's unit-testable; the bpy layer (geometry.place) just applies
these transforms to freshly-built verts.
"""
from __future__ import annotations

import math


def scatter_transforms(n, rng, area, base_z=0.0, layer_rise=0.006,
                       scale_range=(0.85, 1.15), max_rot=math.pi):
    """Return n deterministic {pos, rot_z, scale} placements filling an
    elliptical footprint.

    area = (rx, ry) half-extents in meters. Points are disk-uniform so the
    pile reads evenly; each successive item rises slightly (layer_rise) so a
    heap builds height instead of a flat sheet.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    rx, ry = area
    out = []
    for i in range(n):
        ang = rng.random() * 2.0 * math.pi
        rad = math.sqrt(rng.random())          # uniform over the disk
        x = math.cos(ang) * rad * rx
        y = math.sin(ang) * rad * ry
        z = base_z + i * layer_rise
        scale = scale_range[0] + rng.random() * (scale_range[1] - scale_range[0])
        rot_z = (rng.random() * 2.0 - 1.0) * max_rot
        out.append({"pos": (round(x, 5), round(y, 5), round(z, 5)),
                    "rot_z": round(rot_z, 5), "scale": round(scale, 5)})
    return out
