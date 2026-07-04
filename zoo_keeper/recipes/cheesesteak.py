"""Cheesesteak recipe (flagship low-poly hero) — SIMPLIFIED.

Lesson from viewing it in Godot: at PS1/N64 fidelity, fewer + bigger reads
better than many + small. So the filling is now ONE lumpy jittered meat mound
(not a scatter of chunks) and ONE draped cheese sheet, and the sesame seeds
are a small set PROJECTED onto the crust surface (analytic ellipsoid skin) so
none float. Spend polys on silhouette; let color + vertex wear do the rest.

Open seeded hoagie: bottom roll + two crust walls forming a channel that
cradles the meat mound. Length along Y; origin at floor center.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import scatter


def _warm(c, f):
    return [min(1.0, v * f) for v in c]


def _surface_z(x, y, ellipsoids):
    """Topmost ellipsoid-skin z at (x, y), or None if outside them all.
    Lets seeds sit ON the curved crust instead of a flat plane."""
    best = None
    for (cx, cy, cz), (rx, ry, rz) in ellipsoids:
        t = 1.0 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2
        if t > 0.0:
            z = cz + rz * (t ** 0.5)
            best = z if best is None else max(best, z)
    return best


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]       # X (cross-section)
    length = plan["dimensions"]["depth"]  # Y (long axis)
    h = plan["dimensions"]["height"]      # Z
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    place_rng = streams.stream("dims")
    objs, cboxes = [], []

    def part(bm, name, texel=4.0, bev=None):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel if bev is None else bev,
            texel=texel, rng=rng, wear=wear))

    bun_h = h * 0.55
    bun = ((0, 0, bun_h * 0.5), (w / 2, length / 2, bun_h * 0.65))
    wall_l = ((-w * 0.30, 0, bun_h * 0.9), (w * 0.24, length * 0.47, bun_h * 0.5))
    wall_r = ((w * 0.30, 0, bun_h * 0.9), (w * 0.24, length * 0.47, bun_h * 0.5))

    # --- bottom of the roll --------------------------------------------------
    bm = geometry.new_bm()
    vs = geometry.add_ellipsoid(bm, bun[0], bun[1], u_seg=12, v_seg=6)
    geometry.jitter_verts(vs, place_rng, w * 0.03)
    part(bm, "Steak_Bun")
    cboxes.append(((-w / 2, -length / 2, 0), (w / 2, length / 2, h)))

    # --- two crust walls forming the open channel ---------------------------
    for side, ell in (("L", wall_l), ("R", wall_r)):
        bm = geometry.new_bm()
        rv = geometry.add_ellipsoid(bm, ell[0], ell[1], u_seg=10, v_seg=5)
        geometry.jitter_verts(rv, place_rng, w * 0.03)
        objs.append(geometry.bm_to_object(
            bm, f"Steak_Roll_{side}", collection, bevel=bevel, texel=4.0,
            rng=rng, wear=wear))

    # --- ONE lumpy meat mound cradled in the channel ------------------------
    bm = geometry.new_bm()
    mv = geometry.add_ellipsoid(bm, (0, 0, bun_h * 1.0),
                                (w * 0.24, length * 0.42, bun_h * 0.35),
                                u_seg=10, v_seg=5)
    geometry.jitter_verts(mv, place_rng, w * 0.06)   # heavy = lumpy steak
    part(bm, "Steak_Meat", texel=8.0)

    # --- ONE draped cheese sheet over the meat ------------------------------
    bm = geometry.new_bm()
    cv = geometry.add_box(bm, (0, 0, bun_h * 1.12),
                          (w * 0.5, length * 0.6, 0.006))
    geometry.jitter_verts(cv, place_rng, w * 0.06)
    part(bm, "Steak_Cheese", texel=6.0)

    # --- sesame seeds projected onto the crust (few, flush, no float) -------
    crust = [bun, wall_l, wall_r]
    seeds = geometry.new_bm()
    placed = 0
    for t in scatter.scatter_transforms(
            22, place_rng, area=(w * 0.42, length * 0.46),
            base_z=0.0, layer_rise=0.0, scale_range=(0.7, 1.3)):
        x, y, _ = t["pos"]
        z = _surface_z(x, y, crust)
        if z is None:
            continue
        sv = geometry.add_box(seeds, (0, 0, 0), (w * 0.028, w * 0.045, w * 0.02))
        geometry.place(sv, (x, y, z + 0.003), t["rot_z"], t["scale"])
        placed += 1
    if placed:
        part(seeds, "Steak_Seeds", texel=1.0, bev=0.0)  # no bevel = cheap
    else:
        seeds.free()

    # materials
    bun_mat = materials.make_material("M_Steak_bun", plan["color"], "paper")
    crust_mat = materials.make_material(
        "M_Steak_crust", _warm(plan["color"], 0.82), "paper")
    meat_mat = materials.make_material("M_Steak_meat", [0.32, 0.19, 0.11],
                                       "leather")
    cheese_mat = materials.make_material("M_Steak_cheese", [0.90, 0.86, 0.64],
                                         "plastic")
    seed_mat = materials.make_material("M_Steak_seed", [0.93, 0.88, 0.72],
                                       "paper")
    for o in objs:
        if "Meat" in o.name:
            materials.assign([o], meat_mat)
        elif "Cheese" in o.name:
            materials.assign([o], cheese_mat)
        elif "Seeds" in o.name:
            materials.assign([o], seed_mat)
        elif "Roll" in o.name:
            materials.assign([o], crust_mat)
        else:
            materials.assign([o], bun_mat)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_center": (0, 0, h)}}
