"""water_barrel recipe: a 55-gallon drum.

Roadmap 153, the forecourt. The walker's Call of Duty frames: four blue
drums in a group beside a fence. A drum is a cylinder with two rolling
hoops and a rimmed top and bottom -- the hoops are what stop it reading
as a tube, and they cost eight triangles each.

Collision is the drum. Centre pivot; extents exactly (w, d, h).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

HOOP = 0.035          # how far a rolling hoop stands proud
RIM_H = 0.04


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0
    r = min(w, d) / 2.0

    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, 0.0), r - HOOP, h, segments=12)
    for frac in (0.32, 0.68):
        geometry.add_cylinder(bm, (0.0, 0.0, z0 + h * frac), r, h * 0.07,
                              segments=12)
    for z in (z0 + RIM_H / 2.0, h / 2.0 - RIM_H / 2.0):
        geometry.add_cylinder(bm, (0.0, 0.0, z), r, RIM_H, segments=12)
    obj = geometry.bm_to_object(bm, "WaterBarrel_Drum", collection,
                                bevel=bevel, texel=1.4, rng=rng, wear=wear)
    objs.append(obj)
    cboxes.append(((-r, -r, z0), (r, r, h / 2.0)))

    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)
    mat = materials.make_material(
        f"M_WaterBarrel_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
