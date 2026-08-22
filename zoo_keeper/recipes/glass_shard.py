"""glass_shard recipe: flat angular glass fragments -- cosmetic debris.

The art leg of the replicated-destructible pattern (breakable glass): the
authoritative gameplay state of a pane is an id and an intact/broken flag,
and the shards are local, cosmetic, and never cross a wire. This species
builds them ONE OBJECT PER SHARD -- unlike litter/rubble, which merge their
chunks into a single mesh -- because a game that flings debris needs each
piece addressable (the lasertag addon wraps every shard mesh in its own
rigid body and gives it a seeded impulse).

Shape: `geometry.fracture` on a thin plate, cuts biased hard toward
vertical, so each fragment is an intersection of half-spaces -- the same
construction that made rubble_frag read as damage -- at pane thickness.
Glass breaks into straight edges meeting at points, which is exactly what
plane cuts produce; bevel stays 0 because a chipped glass edge IS sharp.

Skinning: the material kind rides the genome (`glass` by default), so the
SAME Pixelcoat pack that skins a window module's pane lands on every shard
at uniform world density -- debris matches the pane it fell out of with
zero per-species work. Kinds without a pack stay flat vertex color, the
progressive art pass as usual.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    wear = plan["wear"]
    ambient = plan.get("ambient", 0.0)
    rng = streams.stream("wear")

    count = max(1, int(plan["params"].get("shards", 9)))
    cuts = max(1, int(plan["params"].get("cuts", 3)))
    spread = float(plan["params"].get("spread", 0.55))

    kind = plan["material"]
    material = materials.make_material(
        f"M_GlassShard_{kind}", plan["color"], kind)

    objs = []
    for i in range(count):
        bm = geometry.new_bm()
        sx = w * 0.30 * (0.45 + rng.random() * 0.55)
        sy = d * 0.30 * (0.45 + rng.random() * 0.55)
        verts = geometry.add_box(bm, (0.0, 0.0, 0.0), (sx, sy, h))
        # Vertical-biased cuts shape the plan silhouette -- on a piece this
        # thin the outline is the entire read.
        verts = geometry.fracture(bm, verts, rng, cuts=cuts,
                                  near=0.15, far=0.60, steep=0.92,
                                  radius=max(sx, sy) * 0.5)
        # Scatter within the footprint; each shard lies flat on z=0, so the
        # set's outer bbox stays inside the genome's width/depth envelope.
        ox = (rng.random() * 2.0 - 1.0) * max(0.0, w * spread * 0.5 - sx * 0.5)
        oy = (rng.random() * 2.0 - 1.0) * max(0.0, d * spread * 0.5 - sy * 0.5)
        geometry.place(verts, (ox, oy, h * 0.5),
                       rot_z=rng.random() * 6.2831853)
        objs.append(geometry.bm_to_object(
            bm, "GlassShard_%02d" % i, collection, bevel=0.0, texel=8.0,
            rng=rng, wear=wear * 0.4, ambient=ambient))

    materials.assign(objs, material)
    return {"objects": objs, "collision_boxes": [], "attachments": {}}
