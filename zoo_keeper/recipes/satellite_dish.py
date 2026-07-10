"""satellite_dish recipe: a pole-mounted dish — pole, arm, flattened-ellipsoid
dish, feed horn. Faces -Y like the security camera. Built centered; bottom at
-h/2. Visual-only (genome collision: false)."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    z0 = -h / 2.0
    objs = []

    def part(bm, name, texel=2.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    pole_h = h * 0.75
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, d * 0.25, z0 + pole_h / 2),
                          0.035, pole_h, segments=8)
    part(bm, "SatelliteDish_Pole")

    dish_z = z0 + pole_h * 0.95
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, d * 0.05, dish_z), (0.05, d * 0.45, 0.05))
    part(bm, "SatelliteDish_Arm")

    r = w / 2.0
    bm = geometry.new_bm()
    geometry.add_ellipsoid(bm, (0.0, -d * 0.2, dish_z + r * 0.3),
                           (r, r * 0.22, r), u_seg=12, v_seg=6)
    part(bm, "SatelliteDish_Dish")

    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, -d / 2 + 0.04, dish_z + r * 0.3),
                     (0.06, 0.08, 0.06))
    part(bm, "SatelliteDish_Feed")

    mat = materials.make_material(
        f"M_SatelliteDish_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": [], "attachments": {}}
