"""stair_rail recipe: guard railing for stairs, landings and catwalks.

Square posts along the run (X), a top rail that STEPS between posts to follow
`params.rise` (0 = flat landing rail), optional mid rail at half height.
Origin at the lower end of the run, floor level, rail body toward +Z; the
run climbs toward +X. Chunky faceted read — no sloped geometry, stepped
segments between posts (the PS1 way, and it matches DC's stepped treads).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]        # run length
    d = plan["dimensions"]["depth"]        # member thickness
    h = plan["dimensions"]["height"]       # guard height above tread line
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    n_posts = max(2, int(plan["params"]["posts"]))
    rise = float(plan["params"].get("rise", 0.0))
    mid = bool(plan["params"].get("mid_rail", 1))
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.2, rng=rng, wear=wear))

    post_w = max(d, 0.05)
    span = w - post_w
    for i in range(n_posts):
        t = i / (n_posts - 1)
        x = post_w / 2 + t * span - w / 2
        z0 = rise * t
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, 0.0, z0 + h / 2), (post_w, post_w, h))
        part(bm, f"Rail_Post_{i + 1}")

    # stepped rail segments between consecutive posts (top + optional mid)
    for i in range(n_posts - 1):
        t0 = i / (n_posts - 1)
        t1 = (i + 1) / (n_posts - 1)
        x0 = post_w / 2 + t0 * span - w / 2
        x1 = post_w / 2 + t1 * span - w / 2
        zc = rise * (t0 + t1) / 2          # segment sits at the midpoint rise
        seg_w = (x1 - x0) + post_w * 0.5
        cx = (x0 + x1) / 2
        bm = geometry.new_bm()
        geometry.add_box(bm, (cx, 0.0, zc + h - d / 2), (seg_w, d, d))
        part(bm, f"Rail_Top_{i + 1}")
        if mid:
            bm = geometry.new_bm()
            geometry.add_box(bm, (cx, 0.0, zc + h * 0.5), (seg_w, d * 0.8, d * 0.8))
            part(bm, f"Rail_Mid_{i + 1}")

    # one conservative collision box over the whole run (a thin wall the
    # player can lean on but not pass through)
    cboxes.append(((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h + rise)))

    mat = materials.make_material(
        f"M_Rail_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
