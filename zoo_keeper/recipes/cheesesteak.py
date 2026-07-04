"""Cheesesteak recipe (flagship low-poly hero). A proper Philly open hoagie:
a seeded split roll (bottom + two crust walls) with a channel cradling a
scattered meat pile, draped whiz/provolone, and onion bits. PS1/N64 detail —
faceted, jittered, deterministic; no sculpting. Length runs along Y; origin
at floor center.

Reference: a long seeded Italian roll, split open, filling in the groove.
Showcases add_ellipsoid, jitter_verts, and core.scatter via geometry.place.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import scatter


def _warm(c, f):
    return [min(1.0, v * f) for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]       # X (cross-section)
    length = plan["dimensions"]["depth"]  # Y (long axis)
    h = plan["dimensions"]["height"]      # Z
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    place_rng = streams.stream("dims")
    n_meat = plan["params"].get("meat_chunks", 12)
    objs, cboxes = [], []

    def part(bm, name, texel=4.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    bun_h = h * 0.55

    # --- bottom of the roll: elongated, flattened, jittered ellipsoid -------
    bm = geometry.new_bm()
    vs = geometry.add_ellipsoid(bm, (0, 0, bun_h * 0.5),
                                (w / 2, length / 2, bun_h * 0.65),
                                u_seg=12, v_seg=6)
    geometry.jitter_verts(vs, place_rng, w * 0.03)
    part(bm, "Steak_Bun", texel=4.0)
    cboxes.append(((-w / 2, -length / 2, 0), (w / 2, length / 2, h)))

    # --- two crust walls forming the open roll, leaving a center channel ----
    for side, sx in (("L", -1), ("R", 1)):
        bm = geometry.new_bm()
        rv = geometry.add_ellipsoid(bm, (sx * w * 0.30, 0, bun_h * 0.9),
                                    (w * 0.24, length * 0.47, bun_h * 0.5),
                                    u_seg=10, v_seg=5)
        geometry.jitter_verts(rv, place_rng, w * 0.03)
        objs.append(geometry.bm_to_object(
            bm, f"Steak_Roll_{side}", collection, bevel=bevel, texel=4.0,
            rng=rng, wear=wear))

    # --- meat pile: chunks cradled low in the channel between the walls -----
    meat = geometry.new_bm()
    chunk = (w * 0.16, w * 0.16, w * 0.10)
    for t in scatter.scatter_transforms(
            n_meat, place_rng, area=(w * 0.16, length * 0.40),
            base_z=bun_h * 0.70, layer_rise=w * 0.015,
            scale_range=(0.7, 1.2)):
        cv = geometry.add_box(meat, (0, 0, 0), chunk)
        geometry.jitter_verts(cv, place_rng, w * 0.045)
        geometry.place(cv, t["pos"], t["rot_z"], t["scale"])
    part(meat, "Steak_Meat", texel=8.0)

    # --- cheese: draped, jittered sheets over the meat, in the channel ------
    for i in range(2):
        bm = geometry.new_bm()
        cv = geometry.add_box(
            bm, (0, (i - 0.5) * length * 0.26, bun_h * 0.98),
            (w * 0.48, length * 0.28, 0.005))
        geometry.jitter_verts(cv, place_rng, w * 0.06)
        part(bm, f"Steak_Cheese_{i + 1}", texel=6.0)

    # --- onion bits (optional) ----------------------------------------------
    if plan["params"].get("onions", 1):
        bm = geometry.new_bm()
        for t in scatter.scatter_transforms(
                7, place_rng, area=(w * 0.14, length * 0.36),
                base_z=bun_h * 0.85, layer_rise=w * 0.010,
                scale_range=(0.6, 1.0)):
            ov = geometry.add_box(bm, (0, 0, 0), (w * 0.09, w * 0.02, w * 0.05))
            geometry.jitter_verts(ov, place_rng, w * 0.02)
            geometry.place(ov, t["pos"], t["rot_z"], t["scale"])
        part(bm, "Steak_Onion", texel=8.0)

    # --- sesame seeds scattered across the crust (the Philly signature) -----
    seeds = geometry.new_bm()
    for t in scatter.scatter_transforms(
            44, place_rng, area=(w * 0.44, length * 0.46),
            base_z=bun_h * 1.12, layer_rise=0.0,
            scale_range=(0.7, 1.3)):
        sv = geometry.add_box(seeds, (0, 0, 0), (w * 0.03, w * 0.05, w * 0.02))
        geometry.jitter_verts(sv, place_rng, w * 0.01)
        geometry.place(sv, t["pos"], t["rot_z"], t["scale"])
    part(seeds, "Steak_Seeds", texel=1.0)

    # materials
    bun_mat = materials.make_material("M_Steak_bun", plan["color"], "paper")
    crust_mat = materials.make_material(
        "M_Steak_crust", _warm(plan["color"], 0.82), "paper")
    meat_mat = materials.make_material("M_Steak_meat", [0.32, 0.19, 0.11],
                                       "leather")
    cheese_mat = materials.make_material("M_Steak_cheese", [0.90, 0.86, 0.64],
                                         "plastic")
    onion_mat = materials.make_material("M_Steak_onion", [0.90, 0.88, 0.80],
                                        "plastic")
    seed_mat = materials.make_material("M_Steak_seed", [0.93, 0.88, 0.72],
                                       "paper")
    for o in objs:
        if "Meat" in o.name:
            materials.assign([o], meat_mat)
        elif "Cheese" in o.name:
            materials.assign([o], cheese_mat)
        elif "Onion" in o.name:
            materials.assign([o], onion_mat)
        elif "Seeds" in o.name:
            materials.assign([o], seed_mat)
        elif "Roll" in o.name:
            materials.assign([o], crust_mat)
        else:
            materials.assign([o], bun_mat)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_center": (0, 0, h)}}
