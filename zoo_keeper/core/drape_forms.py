"""dust_sheet, planned in pure Python: a cloth thrown over something nobody
has used in years, the something hidden and only its shape showing.

A shut-up room in a country club basement is the walker's case: furniture
under dust sheets says "stored, not lived in" better than bare furniture
does, and the shape under the cloth is what makes one sheet different from
the next. So the hidden object is a PROFILE drawn from the seed and the
slot's proportions:

  * ``chest``    -- one flat top (a sideboard, a crate, a wardrobe);
  * ``armchair`` -- a high back, two arms, a low seat between them;
  * ``sofa``     -- the same, long, with narrow arms;
  * ``stack``    -- a low wide base with a smaller block on it;
  * ``table``    -- a flat top whose cloth stops well short of the floor,
    the four legs showing below;
  * ``lump``     -- two or three soft heaps, whatever it is.

THE CLOTH. A grid over the hidden object's top, its heights the profile's
with the cloth bridging from high to low (the cloth never sinks below what
it rests on), and a skirt of rings hanging from the grid's boundary to a
hem. The skirt flares out toward the hem, folds in and out along its length
with the fold growing toward the hem, and the hem undulates; at the corners
it pools out to the slot's edge. A turned-under hem ring gives the cloth an
edge with thickness. Everything is seeded.

THE RULES: extents exactly w x d x h (`prims.fit_exact` removes what the
plan misses, reported as ``overshoot_m``); no two faces within 2 mm of one
plane where they overlap (measured by `prims.coincident_pairs` in the
tests); deterministic from the rng passed in.

Frame: metres, Z up, base-up, -Y the front (an armchair's seat faces -Y).
"""
from __future__ import annotations

import math

from . import prims as P

PROFILES = ("chest", "armchair", "sofa", "stack", "table", "lump")
RINGS = 5            # skirt rings between the top's edge and the hem
HEM_TURN = 0.012     # how far the turned hem folds back in
HEM_RISE = 0.02      # and up
LEG = 0.045

#: material key -> (linear RGB, kind); "cloth" is the genome's colour
MATERIALS = {"leg": ([0.16, 0.10, 0.06], "wood")}


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def pick_profile(rng, w, d, h):
    """A profile for these proportions, drawn from the seed."""
    # no lump over 1.3 m: rendered at 1.2 x 0.6 x 1.8 it was a spike, a
    # ghost costume rather than a covered thing
    if h >= 1.3:
        pool = ("chest", "chest", "stack")
    elif w >= 1.4 and h <= 1.1:
        pool = ("sofa", "sofa", "table", "stack", "chest")
    elif max(w, d) <= 1.1 and 0.7 <= h <= 1.2:
        pool = ("armchair", "armchair", "table", "lump", "chest")
    else:
        pool = ("chest", "table", "stack", "lump")
    return rng.choice(pool)


def _support(profile, u, v, h, shape):
    """The hidden object's top height at normalised (u, v) in [0, 1]^2;
    v = 0 is the front."""
    if profile == "armchair" or profile == "sofa":
        arm = shape["arm"]
        if v >= shape["back"]:
            return h
        if u <= arm or u >= 1.0 - arm:
            return h * shape["arm_h"]
        return h * shape["seat_h"]
    if profile == "stack":
        u0, u1, v0, v1 = shape["block"]
        if u0 <= u <= u1 and v0 <= v <= v1:
            return h
        return h * shape["base_h"]
    if profile == "lump":
        best = h * 0.4
        for cu, cv, rad, top in shape["heaps"]:
            dd = ((u - cu) ** 2 + (v - cv) ** 2) / (rad * rad)
            best = max(best, h * (0.4 + (top - 0.4) * math.exp(-dd)))
        return best
    return h


def plan(w, d, h, rng, profile="auto"):
    """``{"prims", "collision", "profile", "overshoot_m"}``."""
    if profile not in PROFILES:
        profile = pick_profile(rng, w, d, h)
    # the skirt's room outside the hidden object: 0.06 x min(w, d) capped at
    # 8 cm first, which rendered a 2 m sheet as a box with a tablecloth's
    # sides -- 2 cm folds cannot read at eye height from 3 m
    m = _clamp(0.09 * min(w, d), 0.04, 0.11)
    X0, X1 = -w / 2 + m, w / 2 - m
    Y0, Y1 = -d / 2 + m, d / 2 - m
    nx = int(_clamp(int((X1 - X0) / 0.14) + 2, 5, 12))
    ny = int(_clamp(int((Y1 - Y0) / 0.14) + 2, 4, 10))

    shape = {
        "arm": rng.uniform(0.14, 0.22) if profile == "armchair" else rng.uniform(0.06, 0.1),
        "back": rng.uniform(0.66, 0.78),
        "arm_h": rng.uniform(0.66, 0.78),
        "seat_h": rng.uniform(0.45, 0.56),
        "base_h": rng.uniform(0.45, 0.65),
        "heaps": [(rng.uniform(0.25, 0.75), rng.uniform(0.25, 0.75),
                   rng.uniform(0.3, 0.5), rng.uniform(0.75, 1.0))
                  for _ in range(rng.randint(2, 3))],
    }
    bu = rng.uniform(0.4, 0.65)
    bv = rng.uniform(0.45, 0.7)
    bu0 = rng.uniform(0.0, 1.0 - bu)
    bv0 = rng.uniform(0.0, 1.0 - bv)
    shape["block"] = (bu0, bu0 + bu, bv0, bv0 + bv)

    # the supports, then the cloth bridging them: never below a support,
    # eased down from a high one over a neighbour or two
    sup = [[_support(profile, i / (nx - 1), j / (ny - 1), h, shape)
            for j in range(ny)] for i in range(nx)]
    # the highest support is the slot's top. A lump's heaps peak between
    # grid points, and left alone its tallest point stood up to 23 cm under
    # h -- which `fit_exact` then stretched back, heaps and hem together
    peak = max(max(row) for row in sup)
    sup = [[v * h / peak for v in row] for row in sup]
    cloth = [row[:] for row in sup]
    for _it in range(2):
        nxt = [row[:] for row in cloth]
        for i in range(nx):
            for j in range(ny):
                acc, n = 0.0, 0
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        ii, jj = i + di, j + dj
                        if 0 <= ii < nx and 0 <= jj < ny:
                            acc += cloth[ii][jj]
                            n += 1
                nxt[i][j] = max(sup[i][j], acc / n)
        cloth = nxt
    wrinkle = min(0.012, 0.01 * h)
    top_z = [[cloth[i][j] - rng.uniform(0.0, wrinkle) for j in range(ny)]
             for i in range(nx)]
    # the edge of the top sags where the cloth starts to fall
    for i in range(nx):
        for j in range(ny):
            if i in (0, nx - 1) or j in (0, ny - 1):
                top_z[i][j] -= rng.uniform(0.005, 0.02)

    verts = []
    grid = [[0] * ny for _ in range(nx)]
    for i in range(nx):
        for j in range(ny):
            grid[i][j] = len(verts)
            verts.append((X0 + (X1 - X0) * i / (nx - 1),
                          Y0 + (Y1 - Y0) * j / (ny - 1), top_z[i][j]))
    faces = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            faces.append((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1],
                          grid[i][j + 1]))

    # the boundary loop, CCW seen from above, with each vertex's outward
    # direction (a corner's is (+/-1, +/-1): it pools to the slot's corner)
    loop = []
    for i in range(nx - 1):
        loop.append((i, 0))
    for j in range(ny - 1):
        loop.append((nx - 1, j))
    for i in range(nx - 1, 0, -1):
        loop.append((i, ny - 1))
    for j in range(ny - 1, 0, -1):
        loop.append((0, j))
    corners = {(0, 0), (nx - 1, 0), (nx - 1, ny - 1), (0, ny - 1)}

    def outward(i, j):
        ox = -1.0 if i == 0 else (1.0 if i == nx - 1 else 0.0)
        oy = -1.0 if j == 0 else (1.0 if j == ny - 1 else 0.0)
        return ox, oy

    npts = len(loop)
    table = profile == "table"
    base_hem = h * rng.uniform(0.35, 0.55) if table else rng.uniform(0.0, 0.04)
    folds = max(3, int(round((2 * (w + d)) / rng.uniform(0.28, 0.42))))
    fold_amp = _clamp(0.4 * m, 0.016, 0.044)
    ph1, ph2 = rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi)
    rings = []
    for k in range(1, RINGS + 2):
        ring = []
        t = min(1.0, k / RINGS)
        for idx, (i, j) in enumerate(loop):
            s = idx / npts
            ox, oy = outward(i, j)
            corner = (i, j) in corners
            zb = verts[grid[i][j]][2]
            hem = base_hem + 0.03 * (0.5 + 0.5 * math.sin(2 * math.pi * s * folds * 0.5 + ph2))
            if corner:
                hem = max(0.0, base_hem - (0.1 if table else 0.03))
            hem = min(hem, zb - 0.05)
            fold = fold_amp * math.sin(2 * math.pi * s * folds + ph1)
            # a shoulder: out early, down late, so the top edge rolls over
            # rather than folding at a right angle; the base flare stops at
            # 0.6 m so a fold has room to swing out as far as it swings in
            out = m * (0.15 + 0.45 * t ** 0.7) + fold * t ** 1.2
            if corner:
                out = m * (0.3 + 0.7 * t)
            out = _clamp(out, 0.004, m)
            z = zb - (zb - hem) * t ** 1.25
            x0, y0, _ = verts[grid[i][j]]
            if k == RINGS + 1:
                # the turned hem: back in and up from the last ring
                out -= HEM_TURN
                z += HEM_RISE
            ring.append(len(verts))
            verts.append((x0 + ox * out, y0 + oy * out, z))
        rings.append(ring)
    prev = [grid[i][j] for (i, j) in loop]
    for ring in rings:
        for idx in range(npts):
            n1 = (idx + 1) % npts
            faces.append((prev[idx], prev[n1], ring[n1], ring[idx]))
        prev = ring
    prims = [P.mesh("DustSheet_Cloth", "cloth", verts, faces)]
    cboxes = [((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h))]

    if table:
        for sx in (-1, 1):
            for sy in (-1, 1):
                cx = sx * (w / 2 - m - 0.05)
                cy = sy * (d / 2 - m - 0.05)
                prims.append(P.box("DustSheet_Leg", "leg",
                                   (cx - LEG / 2, cy - LEG / 2, 0.0),
                                   (cx + LEG / 2, cy + LEG / 2, h * 0.9)))
    lo, hi = P.bounds(prims)
    overshoot = max(abs(lo[0] + w / 2), abs(hi[0] - w / 2), abs(lo[1] + d / 2),
                    abs(hi[1] - d / 2), abs(lo[2]), abs(hi[2] - h))
    prims, cboxes = P.fit_exact(prims, (-w / 2, -d / 2, 0.0), (w / 2, d / 2, h),
                                cboxes)
    return {"prims": prims, "collision": cboxes, "profile": profile,
            "overshoot_m": overshoot}
