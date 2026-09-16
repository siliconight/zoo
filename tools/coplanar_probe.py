"""Coincident-face probe: which faces of a built prop share a plane and overlap.

Run inside Blender:

    blender -b --python tools/coplanar_probe.py -- --glb a.glb [b.glb ...]
    blender -b --python tools/coplanar_probe.py -- --species simple_car \
        --dims 1.75 4.3 1.45 [--theme delco_1997] [--out <dir>]

`--glb` imports a GLB that a job already wrote (name the job before reading
anything into the numbers). `--species` plans one prop slot through
`core.kit.plan_kit` and builds it with `build.build_module`, the path a
`zoo_kit_build` job takes, then probes the scene it left behind.

WHAT IT MEASURES. Every pair of triangles, across all visual mesh objects
(collision `-col` objects and `_LOD` copies excluded), whose planes are
parallel and whose plane offsets differ by at most `--tol` metres, and whose
projections onto that plane overlap by more than `--min-area` square metres.
Pairs are aggregated per (object A, object B, facing, gap) and reported with
the summed overlap area.

  * facing SAME: both faces look the same way from the same plane. Whatever
    can see one can see the other, so the depth test decides per pixel.
  * facing OPP: the faces are back to back (two solids in contact). Zoo's
    materials export `doubleSided: true` (measured on verify/*.glb), so these
    are not culled; they are occluded only when both solids are closed and
    the contact is interior.

FRAME AND UNITS. Blender world space, Z up, metres. A GLB is converted by the
glTF importer from Y-up, so its frame matches the recipe's. A gap of 0.0 is
exact coincidence; a non-zero gap below `--tol` is near-coincidence, which a
depth buffer resolves at some distances and not others.

It prints the table and stops. It does not name a cause.
"""
from __future__ import annotations

import json
import math
import os
import sys


def _args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    out = {"glb": [], "species": None, "dims": None, "theme": "delco_1997",
           "out": None, "tol": 0.002, "min_area": 1e-6, "json": None,
           "normal_tol": 1e-3}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--glb":
            i += 1
            while i < len(argv) and not argv[i].startswith("--"):
                out["glb"].append(argv[i])
                i += 1
            continue
        if a == "--dims":
            out["dims"] = [float(argv[i + 1]), float(argv[i + 2]),
                           float(argv[i + 3])]
            i += 4
            continue
        key = a.lstrip("-").replace("-", "_")
        if key in ("tol", "min_area", "normal_tol"):
            out[key] = float(argv[i + 1])
        elif key in out:
            out[key] = argv[i + 1]
        i += 2
    return out


# --- 2D convex clipping ------------------------------------------------------

def _clip(subject, clip):
    """Sutherland-Hodgman: `subject` clipped by convex CCW polygon `clip`."""
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


def _ccw(poly):
    return poly if _area(poly) >= 0 else list(reversed(poly))


# --- gathering ---------------------------------------------------------------

def _triangles(bpy, mathutils, objs):
    tris = []
    for o in objs:
        me = o.data
        me.calc_loop_triangles()
        mw = o.matrix_world
        nm = mw.to_3x3().inverted().transposed()
        for lt in me.loop_triangles:
            p = [mw @ me.vertices[i].co for i in lt.vertices]
            n = (p[1] - p[0]).cross(p[2] - p[0])
            if n.length < 1e-12:
                continue
            n.normalize()
            tris.append((o.name, p, n))
    return tris


def _canon(n, tol):
    """A sign-free key for a normal direction, and the sign that maps it."""
    comps = (n.x, n.y, n.z)
    sign = 1.0
    for c in comps:
        if abs(c) > tol:
            sign = 1.0 if c > 0 else -1.0
            break
    q = tuple(round(sign * c / tol) for c in comps)
    return q, sign


def probe(bpy, mathutils, objs, tol, min_area, normal_tol, samples=0):
    """Rows of coincident face pairs. ``samples`` > 0 additionally records up
    to that many world-space points inside each row's overlap, on the plane
    half-way between the two faces, under the row's ``samples`` key -- the
    seed `tools/coplanar_census.py` needs to ask whether anything stands in
    front of the pair. Zero (the default) changes nothing about the rows."""
    tris = _triangles(bpy, mathutils, objs)
    groups = {}
    for name, p, n in tris:
        key, sign = _canon(n, normal_tol)
        cn = n * sign
        d = cn.dot(p[0])
        groups.setdefault(key, []).append((d, sign, name, p, cn))
    agg = {}
    pts = {}
    for key, items in groups.items():
        items.sort(key=lambda t: t[0])
        cn = items[0][4]
        # plane basis
        ref = mathutils.Vector((1, 0, 0)) if abs(cn.x) < 0.9 else mathutils.Vector((0, 1, 0))
        u = cn.cross(ref).normalized()
        v = cn.cross(u).normalized()
        proj = []
        for d, sign, name, p, _cn in items:
            poly = _ccw([(q.dot(u), q.dot(v)) for q in p])
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
                gap_mm = round(abs(dj - di) * 1000.0, 2)
                pair = tuple(sorted((ni, nj)))
                k = (pair[0], pair[1], facing, gap_mm,
                     tuple(round(c, 3) for c in (cn * si)))
                agg[k] = agg.get(k, 0.0) + a
                if samples and len(pts.setdefault(k, [])) < samples:
                    dm = (di + dj) / 2.0
                    cx = sum(c[0] for c in inter) / len(inter)
                    cy = sum(c[1] for c in inter) / len(inter)
                    pts[k].append(tuple(cn * dm + u * cx + v * cy))
    rows = [{"a": k[0], "b": k[1], "facing": k[2], "gap_mm": k[3],
             "normal_of_a": list(k[4]), "overlap_m2": round(v, 6)}
            for k, v in agg.items()]
    if samples:
        for r, k in zip(rows, agg.keys()):
            r["samples"] = [[round(c, 6) for c in p] for p in pts.get(k, [])]
    rows.sort(key=lambda r: (r["facing"] != "SAME", -r["overlap_m2"]))
    return rows, len(tris)


def _visual_meshes(bpy, scene):
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    return [o for o in scene.objects if o.type == "MESH"
            and not o.name.endswith(_COL_SUFFIXES) and "_LOD" not in o.name]


def _report(label, rows, ntris, tol):
    print(f"[coplanar] {label}: {ntris} tris, {len(rows)} coincident pairs "
          f"(gap <= {tol * 1000:.1f} mm), frame = Blender world, Z up, m")
    for r in rows:
        print(f"[coplanar]   {r['facing']:4} gap {r['gap_mm']:6.2f} mm  "
              f"overlap {r['overlap_m2'] * 1e4:9.2f} cm2  "
              f"n={tuple(r['normal_of_a'])}  {r['a']}  <->  {r['b']}")


def main():
    args = _args()
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo not in sys.path:
        sys.path.insert(0, repo)
    import bpy
    import mathutils

    results = {}
    for glb in args["glb"]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=os.path.abspath(glb))
        objs = _visual_meshes(bpy, bpy.context.scene)
        rows, n = probe(bpy, mathutils, objs, args["tol"], args["min_area"],
                        args["normal_tol"])
        _report(os.path.basename(glb), rows, n, args["tol"])
        results[glb] = rows

    if args["species"]:
        from zoo_keeper.bpylayer import build
        from zoo_keeper.core import kit
        sp = args["species"]
        w, d, h = args["dims"]
        plan = kit.plan_kit({"building_id": "coplanar_probe", "slots": [{
            "slot_id": f"{sp}_0", "role": "prop", "size_mod": "full",
            "style": 1, "species": sp,
            "fit": {"dims": [w, d, h], "pivot": "center"}}]},
            theme=args["theme"], style=1)
        out = os.path.abspath(args["out"] or os.path.join(os.getcwd(), "_coplanar"))
        res = build.build_module(plan["modules"][0], out, theme=args["theme"],
                                 style=1, options={"save_blend": False})
        print(f"[coplanar] built {res['stem']} status="
              f"{res['report']['status']} -> {out}")
        for c in res["report"]["checks"]:
            if c["level"] != "pass" or c["id"] == "tri_budget":
                print(f"[coplanar]   check {c['id']}: {c['level']} {c['msg']}")
        objs = _visual_meshes(bpy, bpy.context.scene)
        rows, n = probe(bpy, mathutils, objs, args["tol"], args["min_area"],
                        args["normal_tol"])
        _report(res["stem"], rows, n, args["tol"])
        results[res["stem"]] = rows

    if args["json"]:
        with open(args["json"], "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1)


# `blender --python` runs this file as __main__; a test imports `probe` from it
if __name__ == "__main__":
    main()
