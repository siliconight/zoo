"""A line of text as neon tube centrelines, from a smooth face (1.156.0).

The walker, 2026-10-31: "Neon is also fun", "liquor store should have neon beer company signs" -- and of every sign on
the slice: "store signage still looks...wrong". A window neon's tubes followed `neon_forms.FONT_5X7`'s skeleton, so a
beer's name read as dot-matrix: glass is bent along a letter's stroke, in a script as often as in capitals. A CC0
single-stroke font would hand over the stroke; none is CC0 (the Hershey fonts are public domain with conditions, the
factory's docs/reference/STORE_SIGNAGE_COMPS.md). So the stroke is FOUND: the line is set in a smooth face
(`smooth_type`, the sign faces Pixelcoat 0.69.0 vendors), thresholded, thinned to one pixel (Zhang-Suen), traced into
polylines between its ends and junctions, cleared of the short spurs a heavy stroke's corners leave
(`SPUR_OF_CAP`) and of the junctions' own fragments, and simplified (Ramer-Douglas-Peucker, `SIMPLIFY_OF_CAP`).

Frame: units of the line's cap height, x to the right from the ink's left, z up from the ink's foot. numpy only: it
runs inside Blender. Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from . import smooth_type as ST

#: the cap height, px, a line is set at before it is thinned: big enough that a script's hairline stays a stroke
CAP_PX = 64
#: a branch from a junction to a free end shorter than this, of the cap, is a stroke's corner, not a stroke
SPUR_OF_CAP = 0.14
#: the simplification's tolerance, of the cap: well inside a tube's own radius (1.158.0: 0.02 -> 0.03, the budget
#: the smoothing below spends)
SIMPLIFY_OF_CAP = 0.03
#: GLASS IS BENT, NOT JOINTED (1.158.0). The walker, of the first renders: the loops read as polygons -- each stroke a
#: chain of straight rods. Every polyline is corner-cut (Chaikin) this many times after it is simplified, its ends
#: kept: one pass doubles a stroke's segments and rounds every bend.
SMOOTH_PASSES = 1
#: a path from one junction to another shorter than this, of the cap, is the gap between two junction clusters, not
#: a stroke: the strokes meeting there cover it, and a tube bent along it is a stub whose caps face its neighbours'
JOIN_FRAG_OF_CAP = 0.08


def _thin(img):
    """Zhang-Suen thinning of a bool image (True = ink)."""
    a = np.pad(img.astype(np.uint8), 1)
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            p2, p3, p4 = a[:-2, 1:-1], a[:-2, 2:], a[1:-1, 2:]
            p5, p6, p7 = a[2:, 2:], a[2:, 1:-1], a[2:, :-2]
            p8, p9 = a[1:-1, :-2], a[:-2, :-2]
            nb = [p2, p3, p4, p5, p6, p7, p8, p9]
            b = sum(n.astype(np.int32) for n in nb)
            seq = nb + [p2]
            t = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(np.int32) for i in range(8))
            c = a[1:-1, 1:-1] == 1
            if step == 0:
                m = c & (b >= 2) & (b <= 6) & (t == 1) & ((p2 * p4 * p6) == 0) & ((p4 * p6 * p8) == 0)
            else:
                m = c & (b >= 2) & (b <= 6) & (t == 1) & ((p2 * p4 * p8) == 0) & ((p2 * p6 * p8) == 0)
            if m.any():
                a[1:-1, 1:-1][m] = 0
                changed = True
    return a[1:-1, 1:-1].astype(bool)


_STEPS = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


def _trace(sk):
    """``[(path, kinds)]``: polylines of (row, col) along a one-pixel skeleton, and closed loops. A thinned
    skeleton's junctions are CLUSTERS of touching pixels -- a staircase leaves three-neighbour pixels every few steps
    along a diagonal -- so the pixels that are not plain stroke (not exactly two neighbours) are grouped into
    clusters, each path runs from one cluster to the next and ends on each cluster's centre, and a stroke runs on
    through a junction instead of breaking there. ``kinds`` names each end: "end" (a free end) or "join"."""
    pts = {(int(r), int(c)) for r, c in zip(*np.nonzero(sk))}

    def nbrs(p):
        return [(p[0] + dr, p[1] + dc) for dr, dc in _STEPS if (p[0] + dr, p[1] + dc) in pts]

    special = {p for p in pts if len(nbrs(p)) != 2}
    cluster = {}
    for p in sorted(special):
        if p in cluster:
            continue
        k = len(set(cluster.values()))
        stack = [p]
        cluster[p] = k
        while stack:
            q = stack.pop()
            for r in nbrs(q):
                if r in special and r not in cluster:
                    cluster[r] = k
                    stack.append(r)
    members = {}
    for p, k in cluster.items():
        members.setdefault(k, []).append(p)
    centre = {k: (sum(p[0] for p in m) / len(m), sum(p[1] for p in m) / len(m)) for k, m in members.items()}
    kind = {k: ("end" if len(m) == 1 and len(nbrs(m[0])) <= 1 else "join") for k, m in members.items()}
    used = set()
    out = []
    for k in sorted(members):
        for n in sorted(members[k]):
            for q in nbrs(n):
                if q in cluster or q in used:
                    continue
                path = [q]
                used.add(q)
                prev, cur = n, q
                end = None
                while True:
                    nxt = [r for r in nbrs(cur) if r != prev and r not in used]
                    hit = [r for r in nxt if r in cluster]
                    if hit:
                        end = cluster[hit[0]]
                        break
                    nxt = [r for r in nxt if r not in cluster]
                    if not nxt:
                        break
                    prev, cur = cur, nxt[0]
                    used.add(cur)
                    path.append(cur)
                if end is None:
                    continue                    # walked into a pixel another path took
                out.append(([centre[k]] + path + [centre[end]], (kind[k], kind[end])))
    # a lone dot: a cluster no path leaves
    for k, m in members.items():
        if not any(q not in cluster for p in m for q in nbrs(p)) and len(m) > 1:
            out.append(([centre[k], centre[k]], ("end", "end")))
    rest = pts - set(cluster) - used
    while rest:
        start = min(rest)
        path, prev, cur = [start], None, start
        while True:
            nxt = [r for r in nbrs(cur) if r != prev and r in rest and r not in path[-3:]]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            if cur == start:
                break
            path.append(cur)
        path.append(start)
        out.append((path, ("join", "join")))
        rest -= set(path)
    return out


def _join_through(paths):
    """Join every pair of paths that meet end to end at a point no third path touches: a junction cluster that only
    continues one stroke (pruning took its spur) would otherwise end two tubes head to head there."""
    paths = [list(p) for p in paths]
    while True:
        ends = {}
        for i, p in enumerate(paths):
            if len(p) < 2 or p[0] == p[-1]:
                continue
            for which, q in ((0, p[0]), (1, p[-1])):
                ends.setdefault((round(q[0], 3), round(q[1], 3)), []).append((i, which))
        pair = next(((k, v) for k, v in sorted(ends.items()) if len(v) == 2 and v[0][0] != v[1][0]), None)
        if pair is None:
            return paths
        (i, wi), (j, wj) = pair[1]
        a = paths[i] if wi == 1 else paths[i][::-1]          # ends at the meeting point
        b = paths[j] if wj == 0 else paths[j][::-1]          # starts there
        paths[i] = a + b[1:]
        del paths[j]


def _chaikin(pts, passes, closed):
    """``pts`` corner-cut ``passes`` times: each segment's quarter points replace its corners; an open line keeps its
    two ends."""
    for _ in range(int(passes)):
        n = len(pts)
        if n < 3:
            break
        segs = [(pts[i], pts[(i + 1) % n]) for i in range(n if closed else n - 1)]
        out = [] if closed else [pts[0]]
        for a, b in segs:
            out.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            out.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        if not closed:
            out.append(pts[-1])
        pts = out
    return pts


def _length(path):
    return sum(math.dist(path[i], path[i + 1]) for i in range(len(path) - 1))


def _rdp(pts, eps):
    if len(pts) < 3:
        return list(pts)
    (ar, ac), (br, bc) = pts[0], pts[-1]
    dr, dc = br - ar, bc - ac
    n = math.hypot(dr, dc)
    if n < 1e-9:
        d = [math.dist(p, pts[0]) for p in pts[1:-1]]
    else:
        d = [abs(dr * (p[1] - ac) - dc * (p[0] - ar)) / n for p in pts[1:-1]]
    i = max(range(len(d)), key=d.__getitem__) + 1
    if d[i - 1] > eps:
        return _rdp(pts[:i + 1], eps)[:-1] + _rdp(pts[i:], eps)
    return [pts[0], pts[-1]]


def strokes(text, face, cap_px=CAP_PX):
    """``(polylines, width, height)``: ``text``'s tube centrelines in ``face``, each a list of (x, z) in cap heights
    (x from the ink's left, z up from its foot), and the ink's extent in cap heights."""
    cov = ST.coverage(text, cap_px, face)
    h, w = cov.shape
    # Zoo's coverage is 0-255 (Pixelcoat's is 0-1): ink is the half-covered pixel, or the anti-aliased fringe thins
    # into ladders
    sk = _thin(cov >= (128 if cov.dtype == np.uint8 else 0.5))
    spur = SPUR_OF_CAP * cap_px
    eps = SIMPLIFY_OF_CAP * cap_px
    kept = []
    for path, kinds in _trace(sk):
        ln = _length(path)
        if "end" in kinds and "join" in kinds and ln < spur:
            continue                       # a corner's spur: a short branch from a junction to a free end
        if kinds == ("join", "join") and ln < JOIN_FRAG_OF_CAP * cap_px:
            continue                       # the gap between two junctions
        kept.append(path)
    out = []
    for path in _join_through(kept):
        simple = _rdp(path, eps)
        if len(simple) < 2:
            continue
        closed = len(simple) > 3 and simple[0] == simple[-1]
        if closed:
            simple = _chaikin(simple[:-1], SMOOTH_PASSES, True)
            simple = simple + [simple[0]]
        else:
            simple = _chaikin(simple, SMOOTH_PASSES, False)
        out.append([(c / cap_px, (h - 1 - r) / cap_px) for r, c in simple])
    return out, w / cap_px, h / cap_px
