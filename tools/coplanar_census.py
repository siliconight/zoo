"""Coincident-face census: every species Zoo can build, at every genome corner.

Run inside Blender:

    blender -b --python tools/coplanar_census.py -- --json out/census.json
    blender -b --python tools/coplanar_census.py -- --species stop_sign bench

WHAT IT MEASURES. For each species genome under `zoo_keeper/genome/species`,
at each of the genome's `min`, `default` and `max` corners (width, depth,
height together), it plans ONE slot through `core.kit.plan_kit` and builds it
with `bpylayer.build.build_module` -- the path a `zoo_kit_build` job takes and
the path `tools/coplanar_probe.py --species` already takes -- and then runs
`coplanar_probe.probe` over the visual meshes the build left in the scene, at
the probe's own defaults (tol 2 mm, min_area 1 mm^2, normal_tol 1e-3).

It reports what the probe reports, per species and corner: the pairs, their
areas, their separations and their facings. It does not say which are
defects; `facing` and `gap_mm` are the measurement and the reading is a
judgement that belongs in the reply.

THE ROLE A SPECIES IS PLANNED UNDER is not a free choice: `kit.plan_kit`
honours a slot's `species` hint only for `VOLUME_ROLES` (`prop`). A species
whose name IS a role -- wall, floor, ceiling, roof, doorway, window,
wallCorner, wallEnd, breach, vault_door, skylight -- is planned under that
role instead, because a `prop` slot asking for `wall` gets a slab. The map
below is read off `kit.PLATE_ROLES`, `VOLUME_ROLES`, `CORNER_ROLES` and
`OPENING_ROLES` at import, so it cannot drift from them silently.

FRAME AND UNITS. Blender world space, Z up, metres; areas printed in cm2 and
stored in m2, gaps in mm.

A species that cannot be planned or built is recorded with its error rather
than skipped: a census with a hole in it that nobody can see is worse than a
short one.
"""
from __future__ import annotations

import json
import os
import sys
import traceback


def _args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    out = {"species": [], "json": None, "out": None, "theme": "delco_1997",
           "style": 1, "tol": 0.002, "min_area": 1e-6, "normal_tol": 1e-3,
           "corners": ["min", "default", "max"]}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--species", "--corners"):
            key = a.lstrip("-")
            out[key] = []
            i += 1
            while i < len(argv) and not argv[i].startswith("--"):
                out[key].append(argv[i])
                i += 1
            continue
        key = a.lstrip("-").replace("-", "_")
        if key in ("tol", "min_area", "normal_tol"):
            out[key] = float(argv[i + 1])
        elif key == "style":
            out[key] = int(argv[i + 1])
        elif key in out:
            out[key] = argv[i + 1]
        i += 2
    return out


def _repo():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _role_map(kit):
    """species name -> (role, size_mod), for the names that ARE roles."""
    m = {}
    for r in kit.PLATE_ROLES + kit.CORNER_ROLES + kit.OPENING_ROLES + ("wall",):
        m[r] = (r, "full")
    m["wallEnd"] = ("wall", "end")
    return m


#: How far a ray may travel before "nothing in front of it" is the answer.
#: The largest module in the library is a 40 m plate, so 60 m crosses any of
#: them twice.
_REACH = 60.0


def _bvh(mathutils, objs):
    """One BVH over every visual mesh, in world space."""
    verts, polys = [], []
    for o in objs:
        me = o.data
        me.calc_loop_triangles()
        mw = o.matrix_world
        base = len(verts)
        verts.extend(tuple(mw @ v.co) for v in me.vertices)
        polys.extend(tuple(base + i for i in lt.vertices)
                     for lt in me.loop_triangles)
    return mathutils.bvhtree.BVHTree.FromPolygons(verts, polys)


def _first_hit(bvh, origin, direction, skip):
    """Distance from ``origin`` to the first surface more than ``skip``
    metres away along ``direction``, or None if there is none within
    `_REACH`. Hits inside ``skip`` are the pair's own two faces -- the
    distance returned is the real one, measured from the origin, not one
    with the skip window taken back off it."""
    travelled = 0.0
    p = origin.copy()
    for _ in range(64):
        hit = bvh.ray_cast(p + direction * 1e-6, direction, _REACH - travelled)
        if hit[3] is None:
            return None
        travelled += hit[3] + 1e-6
        if travelled > skip:
            return travelled
        p = hit[0]
    return None


def exposure(mathutils, bvh, rows):
    """For each row, how deep inside the solid its coincident pair sits.

    A pair of faces on one plane is only something a depth buffer can argue
    about where a viewer can see it. This casts a ray from inside the pair's
    overlap out along the plane normal, both ways, and reports the distance
    to the first surface it meets on each side -- 0.0 where it meets none,
    which is the pair lying on the outside of the prop.

    It reports two distances and stops. Whether a given cover is enough is a
    question about the depth buffer's precision at a viewing distance, and
    that argument belongs in the reply.
    """
    for r in rows:
        pts = r.pop("samples", []) or []
        n = mathutils.Vector(r["normal_of_a"]).normalized()
        skip = r["gap_mm"] / 1000.0 + 2e-4
        pos, neg = [], []
        for p in pts:
            o = mathutils.Vector(p)
            for d, acc in ((n, pos), (-n, neg)):
                hit = _first_hit(bvh, o, d, skip)
                acc.append(0.0 if hit is None else hit)
        r["cover_pos_mm"] = round(min(pos) * 1000.0, 3) if pos else None
        r["cover_neg_mm"] = round(min(neg) * 1000.0, 3) if neg else None
        if pos and neg:
            r["cover_mm"] = min(r["cover_pos_mm"], r["cover_neg_mm"])
    return rows


def _corner_dims(g, which):
    d = g["dimensions"]
    return [float(d["width"][which]), float(d["depth"][which]),
            float(d["height"][which])]


def _clear(bpy):
    bpy.ops.wm.read_factory_settings(use_empty=True)


def run(bpy, mathutils, probe_mod, species, corners, theme, style, out_dir,
        tol, min_area, normal_tol):
    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import kit
    roles = _role_map(kit)
    rows = []
    for sp in species:
        gpath = os.path.join(_repo(), "zoo_keeper", "genome", "species",
                             sp + ".json")
        with open(gpath, encoding="utf-8") as f:
            g = json.load(f)
        for which in corners:
            dims = _corner_dims(g, which)
            rec = {"species": sp, "corner": which,
                   "dims": [round(v, 4) for v in dims]}
            try:
                _clear(bpy)
                role, size_mod = roles.get(sp, ("prop", "full"))
                slot = {"slot_id": f"{sp}_0", "role": role,
                        "size_mod": size_mod, "style": style,
                        "fit": {"dims": dims, "pivot": "center"}}
                if role == "prop":
                    slot["species"] = sp
                plan = kit.plan_kit({"building_id": "coplanar_census",
                                     "slots": [slot]}, theme=theme, style=style)
                if not plan["modules"]:
                    rec["error"] = "plan_kit returned no module"
                    rows.append(rec)
                    continue
                mod = plan["modules"][0]
                res = build.build_module(mod, out_dir, theme=theme, style=style,
                                         options={"save_blend": False})
                rec["stem"] = res["stem"]
                rec["built_species"] = mod.get("species")
                rec["status"] = res["report"]["status"]
                objs = probe_mod["_visual_meshes"](bpy, bpy.context.scene)
                pairs, ntris = probe_mod["probe"](bpy, mathutils, objs, tol,
                                                  min_area, normal_tol,
                                                  samples=3)
                rec["tris"] = ntris
                rec["pairs"] = exposure(mathutils, _bvh(mathutils, objs), pairs)
            except Exception as exc:                      # recorded, not hidden
                rec["error"] = f"{type(exc).__name__}: {exc}"
                rec["traceback"] = traceback.format_exc()[-1200:]
            rows.append(rec)
            _print(rec)
    return rows


def _print(rec):
    head = f"[census] {rec['species']}/{rec['corner']} " \
           f"{'x'.join(str(v) for v in rec['dims'])}"
    if "error" in rec:
        print(f"{head}: ERROR {rec['error']}")
        return
    pairs = rec.get("pairs") or []
    print(f"{head}: {rec['tris']} tris, {len(pairs)} pairs")
    for r in pairs:
        print(f"[census]    {r['facing']:4} gap {r['gap_mm']:6.2f} mm  "
              f"overlap {r['overlap_m2'] * 1e4:9.2f} cm2  "
              f"cover {r.get('cover_mm')} mm  {r['a']} <-> {r['b']}")


def main():
    args = _args()
    repo = _repo()
    if repo not in sys.path:
        sys.path.insert(0, repo)
    import bpy
    import mathutils

    src = open(os.path.join(repo, "tools", "coplanar_probe.py"),
               encoding="utf-8").read()
    probe_mod = {"__name__": "coplanar_probe_lib"}
    exec(compile(src, "coplanar_probe.py", "exec"), probe_mod)

    gdir = os.path.join(repo, "zoo_keeper", "genome", "species")
    species = args["species"] or sorted(
        f[:-5] for f in os.listdir(gdir) if f.endswith(".json"))
    out_dir = os.path.abspath(args["out"] or os.path.join(os.getcwd(), "_census"))
    rows = run(bpy, mathutils, probe_mod, species, args["corners"],
               args["theme"], args["style"], out_dir, args["tol"],
               args["min_area"], args["normal_tol"])

    bad = [r for r in rows if r.get("pairs")]
    err = [r for r in rows if "error" in r]
    print(f"[census] {len(rows)} builds, {len(bad)} with coincident pairs, "
          f"{len(err)} that did not build")
    if args["json"]:
        with open(args["json"], "w", encoding="utf-8") as f:
            json.dump({"tol": args["tol"], "min_area": args["min_area"],
                       "normal_tol": args["normal_tol"], "theme": args["theme"],
                       "style": args["style"], "rows": rows}, f, indent=1)


if __name__ == "__main__":
    main()
