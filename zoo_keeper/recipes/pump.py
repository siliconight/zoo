"""pump recipe: PLACEHOLDER SILHOUETTE, minted 2026-09-12 by tools/new_species.py.

A solid center-pivot box built to the plan's exact dims, one named part,
collision and a top attachment -- so the species validates, ships and is
counted as itself in every kit report. It is NOT yet a pump: this file
is where the drawing goes. Shape it the way `desk.py` or `counter.py` shape
theirs -- boxes from `geometry.add_box` per part, `part(bm, name)` to turn
each into an object, a collision box per solid, and keep the overall
extents equal to (w, d, h): Deli Counter places this module on a slot of
exactly that size and `validate` fails a module that is not.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.2, rng=rng, wear=wear))

    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, 0.0), (w, d, h))   # centre pivot, like every module
    part(bm, "Pump_Body")
    cboxes.append(((-w / 2, -d / 2, -h / 2), (w / 2, d / 2, h / 2)))

    surface = materials.make_material(
        f"M_Pump_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, surface)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2)}}
