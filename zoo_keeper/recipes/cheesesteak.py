"""Cheesesteak recipe (flagship low-poly hero). An open hoagie: a jittered
bread roll, a scattered pile of jittered meat chunks, draped cheese sheets,
and a few onion bits. PS1/N64 detail — chunky facets, deterministic irregular
geometry, no sculpting. Length runs along Y; origin at floor center.

Showcases the new geometry toolkit: add_ellipsoid, jitter_verts, and
core.scatter transforms applied via geometry.place.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import scatter


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]     # X (cross-section)
    length = plan["dimensions"]["depth"]  # Y (long axis)
    h = plan["dimensions"]["height"]    # Z
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    place_rng = streams.stream("dims")   # separate stream for scatter layout
    n_meat = plan["params"].get("meat_chunks", 12)
    objs, cboxes = [], []

    def part(bm, name, texel=6.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    # --- bread roll: an elongated, flattened, jittered ellipsoid ------------
    bun_h = h * 0.5
    bm = geometry.new_bm()
    vs = geometry.add_ellipsoid(bm, (0, 0, bun_h * 0.5),
                                (w / 2, length / 2, bun_h * 0.7),
                                u_seg=12, v_seg=6)
    geometry.jitter_verts(vs, place_rng, w * 0.04)
    part(bm, "Steak_Bun", texel=4.0)
    cboxes.append(((-w / 2, -length / 2, 0), (w / 2, length / 2, h)))

    # --- meat pile: scattered, jittered chunks along the roll ---------------
    meat = geometry.new_bm()
    chunk = (w * 0.16, w * 0.16, w * 0.12)
    for t in scatter.scatter_transforms(
            n_meat, place_rng, area=(w * 0.32, length * 0.42),
            base_z=bun_h * 0.85, layer_rise=w * 0.05,
            scale_range=(0.7, 1.25)):
        cv = geometry.add_box(meat, (0, 0, 0), chunk)
        geometry.jitter_verts(cv, place_rng, w * 0.05)
        geometry.place(cv, t["pos"], t["rot_z"], t["scale"])
    part(meat, "Steak_Meat", texel=8.0)

    # --- cheese: a couple of draped, jittered thin sheets -------------------
    for i in range(2):
        bm = geometry.new_bm()
        cv = geometry.add_box(
            bm, (0, (i - 0.5) * length * 0.28, bun_h * 1.25),
            (w * 0.7, length * 0.34, 0.006))
        geometry.jitter_verts(cv, place_rng, w * 0.05)
        part(bm, f"Steak_Cheese_{i + 1}", texel=6.0)

    # --- onion bits (optional) ----------------------------------------------
    if plan["params"].get("onions", 1):
        bm = geometry.new_bm()
        for t in scatter.scatter_transforms(
                6, place_rng, area=(w * 0.28, length * 0.4),
                base_z=bun_h * 1.05, layer_rise=w * 0.02,
                scale_range=(0.6, 1.0)):
            ov = geometry.add_box(bm, (0, 0, 0), (w * 0.1, w * 0.02, w * 0.06))
            geometry.jitter_verts(ov, place_rng, w * 0.02)
            geometry.place(ov, t["pos"], t["rot_z"], t["scale"])
        part(bm, "Steak_Onion", texel=8.0)

    bun_mat = materials.make_material("M_Steak_bun", plan["color"], "paper")
    meat_mat = materials.make_material("M_Steak_meat", [0.34, 0.20, 0.12],
                                       "leather")
    cheese_mat = materials.make_material("M_Steak_cheese", [0.92, 0.72, 0.24],
                                         "plastic")
    onion_mat = materials.make_material("M_Steak_onion", [0.88, 0.86, 0.78],
                                        "plastic")
    for o in objs:
        if "Meat" in o.name:
            materials.assign([o], meat_mat)
        elif "Cheese" in o.name:
            materials.assign([o], cheese_mat)
        elif "Onion" in o.name:
            materials.assign([o], onion_mat)
        else:
            materials.assign([o], bun_mat)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_center": (0, 0, h)}}
