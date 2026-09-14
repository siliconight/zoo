"""Primitives as plain vertex and face lists -- pure Python, no bpy.

The interior species (carton_stack, furnace, dust_sheet, pool_table,
booth_seat) and the surface stock planner describe their geometry here and
`bpylayer.prim_mesh` turns the SAME lists into bmesh faces, vertex for
vertex. That is the point of the module: what a unit test measures is what
Blender builds (before the recipe's bevel), so the extents contract, the
triangle count and the coincident-face rule can be checked without Blender
and cannot drift from the build.

A primitive is a dict::

    {"part": "Furnace_Cabinet",   # object it is built into
     "mat":  "body",              # material key the recipe resolves
     "bevel": True,               # whether the recipe's bevel applies
     "verts": [(x, y, z), ...],
     "faces": [(i, j, k, ...), ...]}   # indices into verts, CCW from outside

Frame and units: metres, Z up, the recipe's own frame (base-up, x along the
piece's length, -Y its front). Faces are convex polygons; a quad whose four
corners are not coplanar is split the way `triangles` splits it.
"""
from __future__ import annotations

import math

# --- construction -------------------------------------------------------------


def _prim(part, mat, verts, faces, bevel=False):
    return {"part": part, "mat": mat, "bevel": bool(bevel),
            "verts": [tuple(float(c) for c in v) for v in verts],
            "faces": [tuple(f) for f in faces]}


def box(part, mat, lo, hi, bevel=False):
    """Axis-aligned box from its min and max corners."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5),
         (2, 3, 7, 6), (3, 0, 4, 7)]
    return _prim(part, mat, v, f, bevel)


def box_c(part, mat, center, size, bevel=False):
    """Axis-aligned box from its centre and size."""
    c, s = center, size
    return box(part, mat, (c[0] - s[0] / 2, c[1] - s[1] / 2, c[2] - s[2] / 2),
               (c[0] + s[0] / 2, c[1] + s[1] / 2, c[2] + s[2] / 2), bevel)


def cyl(part, mat, center_xy, r, z0, z1, segments=8, r_top=None, phase=0.0,
        bevel=False):
    """A faceted cylinder (or frustum, with ``r_top``) standing on z0.

    ``phase`` turns the ring in radians. With the default 0 a vertex sits on
    +X; ``phase = pi / segments`` puts a flat facet facing +X instead."""
    cx, cy = center_xy
    rt = r if r_top is None else r_top
    n = int(segments)
    v = []
    for k in range(n):
        a = phase + 2.0 * math.pi * k / n
        v.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
    for k in range(n):
        a = phase + 2.0 * math.pi * k / n
        v.append((cx + rt * math.cos(a), cy + rt * math.sin(a), z1))
    f = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for k in range(n):
        k1 = (k + 1) % n
        f.append((k, k1, n + k1, n + k))
    return _prim(part, mat, v, f, bevel)


def sphere(part, mat, center, radii, u=8, v=5, bevel=False):
    """A faceted UV sphere: ``u`` segments round, ``v`` rings pole to pole."""
    cx, cy, cz = center
    rx, ry, rz = radii
    verts = [(cx, cy, cz - rz)]
    for j in range(1, v):
        th = math.pi * j / v - math.pi / 2.0
        for k in range(u):
            a = 2.0 * math.pi * k / u
            verts.append((cx + rx * math.cos(th) * math.cos(a),
                          cy + ry * math.cos(th) * math.sin(a),
                          cz + rz * math.sin(th)))
    verts.append((cx, cy, cz + rz))
    top = len(verts) - 1
    faces = []
    for k in range(u):
        faces.append((0, 1 + (k + 1) % u, 1 + k))
    for j in range(v - 2):
        a0 = 1 + j * u
        a1 = 1 + (j + 1) * u
        for k in range(u):
            k1 = (k + 1) % u
            faces.append((a0 + k, a0 + k1, a1 + k1, a1 + k))
    last = 1 + (v - 2) * u
    for k in range(u):
        faces.append((last + k, last + (k + 1) % u, top))
    return _prim(part, mat, verts, faces, bevel)


def prism(part, mat, footprint, z0, z1, bevel=False):
    """A vertical prism over a convex CCW footprint polygon [(x, y), ...]."""
    n = len(footprint)
    v = [(x, y, z0) for x, y in footprint] + [(x, y, z1) for x, y in footprint]
    f = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for k in range(n):
        k1 = (k + 1) % n
        f.append((k, k1, n + k1, n + k))
    return _prim(part, mat, v, f, bevel)


def mesh(part, mat, verts, faces, bevel=False):
    return _prim(part, mat, verts, faces, bevel)


# --- transforms (return new primitives) -------------------------------------


def _map(p, fn):
    q = dict(p)
    q["verts"] = [fn(v) for v in p["verts"]]
    return q


def translate(p, d):
    return _map(p, lambda v: (v[0] + d[0], v[1] + d[1], v[2] + d[2]))


def rotate_z(p, a, about=(0.0, 0.0)):
    c, s = math.cos(a), math.sin(a)
    ox, oy = about

    def fn(v):
        x, y = v[0] - ox, v[1] - oy
        return (ox + c * x - s * y, oy + s * x + c * y, v[2])
    return _map(p, fn)


def rotate_x(p, a, about=(0.0, 0.0)):
    """About the X axis through (y, z) = ``about``."""
    c, s = math.cos(a), math.sin(a)
    oy, oz = about

    def fn(v):
        y, z = v[1] - oy, v[2] - oz
        return (v[0], oy + c * y - s * z, oz + s * y + c * z)
    return _map(p, fn)


def rotate_y(p, a, about=(0.0, 0.0)):
    """About the Y axis through (x, z) = ``about``."""
    c, s = math.cos(a), math.sin(a)
    ox, oz = about

    def fn(v):
        x, z = v[0] - ox, v[2] - oz
        return (ox + c * x + s * z, v[1], oz - s * x + c * z)
    return _map(p, fn)


def lay_along_x(p):
    """Turn a Z-up primitive (a `cyl`) to lie along +X: z -> x."""
    return _map(p, lambda v: (v[2], v[1], -v[0]))


def lay_along_y(p):
    """Turn a Z-up primitive to lie along +Y: z -> y."""
    return _map(p, lambda v: (v[0], v[2], -v[1]))


def recolour(p, part=None, mat=None):
    q = dict(p)
    if part is not None:
        q["part"] = part
    if mat is not None:
        q["mat"] = mat
    return q


def fit_exact(prims, lo, hi, boxes=()):
    """Map every vertex, per axis, so the primitives' bounds are exactly
    ``lo``..``hi``; return ``(prims, boxes)`` with the collision boxes mapped
    the same way.

    WHY A PLANNER ENDS WITH THIS. A detail stands a few mm proud because that
    is what the object looks like -- a label on a carton front, the tape over
    its end -- and the slot is exact. The planners lay the body out to the
    slot and let the details overshoot; this takes the overshoot back out.
    The scale is within a percent of 1, so a 3 mm offset stays 3 mm to a
    hundredth of a millimetre and no face pair the planner kept apart is
    brought within the coincident-face tolerance. `geometry.fit_to` is the
    same idea for a recipe that measures after building; this one runs
    before, so the tests measure what ships.
    """
    blo, bhi = bounds(prims)
    k, c0, c1 = [], [], []
    for a in range(3):
        span = bhi[a] - blo[a]
        k.append((hi[a] - lo[a]) / span if span > 1e-12 else 1.0)
        c0.append(blo[a])
        c1.append(lo[a])

    def fn(v):
        return tuple(c1[a] + (v[a] - c0[a]) * k[a] for a in range(3))
    out = [_map(p, fn) for p in prims]

    def clamp(v):
        return tuple(min(hi[a], max(lo[a], v[a])) for a in range(3))
    # a box drawn at the slot's size is mapped too, and where the plan fell
    # short of the slot that pushed it past the slot (a 0.4 m dust sheet's
    # collider, first test run): a collider never leaves the module's bounds
    ob = [(clamp(fn(a)), clamp(fn(b))) for a, b in boxes]
    return out, ob


# --- measurement --------------------------------------------------------------


def bounds(prims):
    """((xmin, ymin, zmin), (xmax, ymax, zmax)) over every vertex."""
    lo = [1e18, 1e18, 1e18]
    hi = [-1e18, -1e18, -1e18]
    for p in prims:
        for v in p["verts"]:
            for k in range(3):
                lo[k] = min(lo[k], v[k])
                hi[k] = max(hi[k], v[k])
    return tuple(lo), tuple(hi)


def tri_count(prims):
    """Triangles before any bevel: an n-gon is n - 2."""
    return sum(len(f) - 2 for p in prims for f in p["faces"])


def triangles(p):
    """Fan triangulation of every face: [(a, b, c), ...] as coordinates."""
    out = []
    vs = p["verts"]
    for f in p["faces"]:
        for k in range(1, len(f) - 1):
            out.append((vs[f[0]], vs[f[k]], vs[f[k + 1]]))
    return out


def footprint_xy(prims):
    """Every vertex's (x, y) -- the input a no-overhang test needs."""
    return [(v[0], v[1]) for p in prims for v in p["verts"]]


# --- coincident faces (a pure port of tools/coplanar_probe.py) ---------------


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _clip(subject, clip):
    def inside(p, a, b):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -1e-12

    def cross(p1, p2, a, b):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = dx * ey - dy * ex
        if abs(den) < 1e-18:
            return p2
        t = ((a[0] - p1[0]) * ey - (a[1] - p1[1]) * ex) / den
        return (p1[0] + t * dx, p1[1] + t * dy)

    out = list(subject)
    n = len(clip)
    for k in range(n):
        a, b = clip[k], clip[(k + 1) % n]
        inp, out = out, []
        if not inp:
            break
        s = inp[-1]
        for e in inp:
            if inside(e, a, b):
                if not inside(s, a, b):
                    out.append(cross(s, e, a, b))
                out.append(e)
            elif inside(s, a, b):
                out.append(cross(s, e, a, b))
            s = e
    return out


def _area(poly):
    s = 0.0
    for k in range(len(poly)):
        x1, y1 = poly[k]
        x2, y2 = poly[(k + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def coincident_pairs(prims, tol=0.002, min_area=1e-6, normal_tol=1e-3):
    """Pairs of triangles, across ALL primitives, whose planes are parallel,
    whose plane offsets differ by at most ``tol`` metres and whose overlap
    on that plane exceeds ``min_area`` square metres.

    The same measurement `tools/coplanar_probe.py` makes on a built scene,
    with the same defaults, so a count of zero here is the claim that one
    will print zero there -- before bevel, which only cuts corners inward.
    Returns rows ``{a, b, facing, gap_mm, overlap_m2}`` aggregated per
    (part a, part b, facing, gap), SAME-facing rows first.
    """
    groups = {}
    for p in prims:
        for tri in triangles(p):
            n = _cross(_sub(tri[1], tri[0]), _sub(tri[2], tri[0]))
            ln = math.sqrt(_dot(n, n))
            if ln < 1e-12:
                continue
            n = (n[0] / ln, n[1] / ln, n[2] / ln)
            sign = 1.0
            for c in n:
                if abs(c) > normal_tol:
                    sign = 1.0 if c > 0 else -1.0
                    break
            key = tuple(round(sign * c / normal_tol) for c in n)
            cn = (n[0] * sign, n[1] * sign, n[2] * sign)
            groups.setdefault(key, []).append((_dot(cn, tri[0]), sign,
                                               p["part"], tri, cn))
    agg = {}
    for items in groups.values():
        items.sort(key=lambda t: t[0])
        cn = items[0][4]
        ref = (1.0, 0.0, 0.0) if abs(cn[0]) < 0.9 else (0.0, 1.0, 0.0)
        u = _cross(cn, ref)
        lu = math.sqrt(_dot(u, u))
        u = (u[0] / lu, u[1] / lu, u[2] / lu)
        w = _cross(cn, u)
        proj = []
        for d, sign, name, tri, _cn in items:
            poly = [(_dot(q, u), _dot(q, w)) for q in tri]
            if _area(poly) < 0:
                poly.reverse()
            xs = [c[0] for c in poly]
            ys = [c[1] for c in poly]
            proj.append((d, sign, name, poly, (min(xs), max(xs), min(ys), max(ys))))
        m = len(proj)
        for i in range(m):
            di, si, ni, pi, bi = proj[i]
            j = i + 1
            while j < m and proj[j][0] - di <= tol:
                dj, sj, nj, pj, bj = proj[j]
                j += 1
                if bi[1] <= bj[0] or bj[1] <= bi[0] or bi[3] <= bj[2] or bj[3] <= bi[2]:
                    continue
                inter = _clip(pi, pj)
                if len(inter) < 3:
                    continue
                a = abs(_area(inter))
                if a < min_area:
                    continue
                facing = "SAME" if si == sj else "OPP"
                gap = round(abs(dj - di) * 1000.0, 2)
                pair = tuple(sorted((ni, nj)))
                k = (pair[0], pair[1], facing, gap)
                agg[k] = agg.get(k, 0.0) + a
    rows = [{"a": k[0], "b": k[1], "facing": k[2], "gap_mm": k[3],
             "overlap_m2": round(v, 8)} for k, v in agg.items()]
    rows.sort(key=lambda r: (r["facing"] != "SAME", -r["overlap_m2"]))
    return rows


# --- 2D footprints (placement) ------------------------------------------------


def rect_poly(cx, cy, sx, sy, yaw):
    """Corners of a sx by sy rectangle centred on (cx, cy), turned ``yaw``."""
    c, s = math.cos(yaw), math.sin(yaw)
    out = []
    for dx, dy in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2),
                   (sx / 2, sy / 2), (-sx / 2, sy / 2)):
        out.append((cx + c * dx - s * dy, cy + s * dx + c * dy))
    return out


def poly_separated(a, b, gap):
    """True when convex polygons ``a`` and ``b`` are at least ``gap`` apart
    along some edge normal of either (separating-axis test).

    A SUPERSET TEST, and deliberately: a gap asked per axis is a box, not a
    radius, so this can call two polygons too close near a corner when their
    true distance is up to sqrt(2) * gap. For placement that errs toward
    leaving space, which is harmless; it can never pass two footprints that
    overlap.
    """
    for poly in (a, b):
        n = len(poly)
        for k in range(n):
            x0, y0 = poly[k]
            x1, y1 = poly[(k + 1) % n]
            nx, ny = y1 - y0, -(x1 - x0)
            ln = math.hypot(nx, ny)
            if ln < 1e-12:
                continue
            nx, ny = nx / ln, ny / ln
            pa = [px * nx + py * ny for px, py in a]
            pb = [px * nx + py * ny for px, py in b]
            if min(pb) - max(pa) >= gap or min(pa) - max(pb) >= gap:
                return True
    return False


def poly_inside_rect(poly, x0, x1, y0, y1):
    return all(x0 - 1e-12 <= x <= x1 + 1e-12 and y0 - 1e-12 <= y <= y1 + 1e-12
               for x, y in poly)


def poly_inside_poly(inner, outer, inset):
    """Every vertex of ``inner`` at least ``inset`` inside convex CCW
    ``outer`` (distance to each edge line)."""
    n = len(outer)
    for k in range(n):
        x0, y0 = outer[k]
        x1, y1 = outer[(k + 1) % n]
        ex, ey = x1 - x0, y1 - y0
        ln = math.hypot(ex, ey)
        if ln < 1e-12:
            continue
        for px, py in inner:
            # left of a CCW edge is inside; signed distance
            dist = (ex * (py - y0) - ey * (px - x0)) / ln
            if dist < inset - 1e-12:
                return False
    return True


# --- shapes the interior species share ---------------------------------------


def rod(part, mat, p0, p1, r0, r1=None, segments=8, bevel=False):
    """A faceted frustum from point ``p0`` (radius r0) to ``p1`` (r1), for a
    cue, a pipe or a leg that is not vertical."""
    r1 = r0 if r1 is None else r1
    ax = _sub(p1, p0)
    ln = math.sqrt(_dot(ax, ax))
    a = (ax[0] / ln, ax[1] / ln, ax[2] / ln)
    ref = (0.0, 0.0, 1.0) if abs(a[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = _cross(a, ref)
    lu = math.sqrt(_dot(u, u))
    u = (u[0] / lu, u[1] / lu, u[2] / lu)
    v = _cross(a, u)
    n = int(segments)
    verts = []
    for base, r in ((p0, r0), (p1, r1)):
        for k in range(n):
            t = 2.0 * math.pi * k / n
            c, s = math.cos(t) * r, math.sin(t) * r
            verts.append((base[0] + u[0] * c + v[0] * s,
                          base[1] + u[1] * c + v[1] * s,
                          base[2] + u[2] * c + v[2] * s))
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for k in range(n):
        k1 = (k + 1) % n
        faces.append((k, k1, n + k1, n + k))
    return _prim(part, mat, verts, faces, bevel)


def pillow(part, mat, lo, hi, crown, bevel=False):
    """A box whose top is crowned: a 3 x 3 vertex grid over the top, the
    centre ``crown`` above the corners and each edge's middle half that.
    The sides are convex pentagons, so every face stays planar."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    xm, ym = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]
    top = {}
    for i, x in enumerate((x0, xm, x1)):
        for j, y in enumerate((y0, ym, y1)):
            edge = (i == 1) + (j == 1)
            top[(i, j)] = len(verts)
            verts.append((x, y, z1 + crown * (0.0, 0.5, 1.0)[edge]))
    t = top
    faces = [(3, 2, 1, 0),
             (t[0, 0], t[1, 0], t[1, 1], t[0, 1]), (t[1, 0], t[2, 0], t[2, 1], t[1, 1]),
             (t[0, 1], t[1, 1], t[1, 2], t[0, 2]), (t[1, 1], t[2, 1], t[2, 2], t[1, 2]),
             (0, 1, t[2, 0], t[1, 0], t[0, 0]),          # front (-Y)
             (1, 2, t[2, 2], t[2, 1], t[2, 0]),          # +X
             (2, 3, t[0, 2], t[1, 2], t[2, 2]),          # back (+Y)
             (3, 0, t[0, 0], t[0, 1], t[0, 2])]          # -X
    return _prim(part, mat, verts, faces, bevel)
