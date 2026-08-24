"""pendant_fixture recipe: a bare-bulb pendant for the below-grade rule
(DC >= 0.98 derives `pendant` anchors for basements and objective rooms;
roadmap 57's 90s palette). Cord from the slab, a stubby socket, an exposed
bulb. The light-anchor pipeline mounts this 'above', so the recipe's bottom
(-h/2) — the bulb — lands exactly at the anchor, which DC placed 0.6 m below
the ceiling; the cord rises the rest of the height back toward the slab.
The bulb carries the M_*_Lens naming Lux's emissive binder keys on, same as
the wall pack's lens and the troffer's diffuser.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]       # bulb diameter
    h = plan["dimensions"]["height"]      # bulb + socket + cord, total
    bevel, wear = plan["bevel"], plan["wear"]
    style = plan.get("style_block", {})
    rng = streams.stream("wear")
    z0 = -h / 2.0
    r = w / 2.0
    objs = []

    # Bulb: a low-poly ellipsoid at the bottom, faceted on purpose --
    # sixth-gen glass, not a showroom render.
    bm = geometry.new_bm()
    geometry.add_ellipsoid(bm, (0.0, 0.0, z0 + r), (r, r, r * 1.15),
                           u_seg=10, v_seg=6)
    bulb = geometry.bm_to_object(
        bm, "Pendant_Bulb", collection, bevel=0.0, texel=1.0,
        rng=rng, wear=0.0)
    objs.append(bulb)

    # Socket: a squat box cap over the bulb's neck.
    sock_h = min(0.06, h * 0.1)
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + r * 2.0 + sock_h / 2.0),
                     (r * 0.9, r * 0.9, sock_h))
    sock = geometry.bm_to_object(
        bm, "Pendant_Socket", collection, bevel=bevel, texel=1.5,
        rng=rng, wear=wear)
    objs.append(sock)

    # Cord: a thin box from the socket up to the top of the height budget
    # (the slab underside, the way DC spaced the anchor).
    cord_z0 = z0 + r * 2.0 + sock_h
    cord_h = max(h - (r * 2.0 + sock_h), 0.05)
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, cord_z0 + cord_h / 2.0),
                     (0.015, 0.015, cord_h))
    cord = geometry.bm_to_object(
        bm, "Pendant_Cord", collection, bevel=0.0, texel=1.0,
        rng=rng, wear=wear * 0.5)
    objs.append(cord)

    mat = materials.make_material(
        f"M_Pendant_{plan['material']}", plan["color"], plan["material"])
    materials.assign([sock, cord], mat)
    lit = materials.make_emissive_material(
        "M_Pendant_Lens",
        style.get("emissive_color", [1.0, 0.85, 0.62]),
        style.get("emissive_strength", 2.4))
    materials.assign([bulb], lit)

    # No collision: a bulb overhead, above the walk plane by construction.
    return {"objects": objs, "collision_boxes": [], "attachments": {}}
