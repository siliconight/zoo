"""Weighted normals: each corner's normal is the area-weighted sum of the faces
in its smooth fan (1.87.0, roadmap 214, trial 1; the walker's modern low-poly
standard, section 5 and Addendum A.4).

WHY. `geometry.shade_by_angle` smooths every fold under 50 degrees, which is
what turns a one-segment bevel into a highlight instead of a facet. But a
corner normal by default weighs the faces of its fan by CORNER ANGLE, so a
big face and the 1.4 cm chamfer beside it count about equally, and every
corner of the big face is pulled toward the chamfer. Measured on a bevelled
0.6 x 0.4 x 0.5 m crate built through `bm_to_object` and read back out of
the GLB the exporter wrote: all 36 big-face corners sat 28.89 degrees off
their face (`docs/findings/weighted_normals/`). The face is shaded as a
dome. That is the defect `bm_to_object`'s docstring measured on a wall panel
at 28.9 degrees and avoided there by keeping every edge hard.

Weighing by AREA lets a big face keep its own normal -- 2.40 degrees mean on
the same crate -- while the chamfer between two big faces rolls from one to
the other: a flat face with a lit edge. Nothing is added. The fans are the
ones the exporter already splits vertices by, so the vertex count, the
triangles and the materials are unchanged (48 vertices either way on the
crate). A part whose folds are all hard -- `shade_by_angle(bm, 1.0)`, or 30
degrees against a 45-degree chamfer -- has one face to a fan and comes out
exactly as before.

PURE PYTHON, so the suite checks it without Blender.
`bpylayer.geometry.weight_normals` reads a mesh into these lists and writes
the answer back as the mesh's custom normals.
"""
from __future__ import annotations

import math


def weighted_corner_normals(faces, normals, areas, smooth_faces, sharp_edges):
    """Per-corner unit normals, in face order and then corner order -- the
    order a Blender mesh stores its corners in.

    ``faces``         each face's vertex indices, in corner order;
    ``normals``       each face's unit normal;
    ``areas``         each face's area, m2;
    ``smooth_faces``  False for a flat-shaded face, whose corners take its own
                      normal;
    ``sharp_edges``   ``frozenset({a, b})`` for every edge marked sharp.

    A FAN is the corners of one vertex joined across every edge that is not
    sharp, borders exactly two faces, has both faces smooth and is walked in
    opposite directions by them (consistent winding). That is where Blender
    itself splits a vertex's normal, so the fans here are the ones the
    exporter splits vertices by.

    A fan whose weighted sum is zero -- every face in it degenerate -- gets
    ``(0, 0, 0)``, which Blender's `normals_split_custom_set` reads as "keep
    the default normal".
    """
    offset, total = [], 0
    for f in faces:
        offset.append(total)
        total += len(f)
    parent = list(range(total))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    # edge -> [(face, corner of the edge's first vertex, of its second,
    #           walked low -> high)]
    edges = {}
    for fi, f in enumerate(faces):
        n = len(f)
        for k in range(n):
            a, b = f[k], f[(k + 1) % n]
            if a == b:
                continue
            key = (a, b) if a < b else (b, a)
            ka, kb = (k, (k + 1) % n) if a < b else ((k + 1) % n, k)
            edges.setdefault(key, []).append((fi, ka, kb, a < b))
    for key, uses in edges.items():
        if len(uses) != 2 or frozenset(key) in sharp_edges:
            continue
        (f0, a0, b0, up0), (f1, a1, b1, up1) = uses
        if up0 == up1 or not (smooth_faces[f0] and smooth_faces[f1]):
            continue
        for c0, c1 in ((offset[f0] + a0, offset[f1] + a1),
                       (offset[f0] + b0, offset[f1] + b1)):
            parent[find(c0)] = find(c1)

    sums = {}
    for fi, f in enumerate(faces):
        nx, ny, nz = normals[fi]
        w = areas[fi]
        for k in range(len(f)):
            s = sums.setdefault(find(offset[fi] + k), [0.0, 0.0, 0.0])
            s[0] += nx * w
            s[1] += ny * w
            s[2] += nz * w
    out = []
    for c in range(total):
        x, y, z = sums[find(c)]
        length = math.sqrt(x * x + y * y + z * z)
        out.append((x / length, y / length, z / length) if length > 0.0
                   else (0.0, 0.0, 0.0))
    return out
