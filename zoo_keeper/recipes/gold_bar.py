"""gold_bar recipe: a single gold ingot — heist loot. Origin at floor center;
a beveled bar rests on the surface. No collision (a pickup, like cash)."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")

    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, h / 2.0), (w, d, h))
    ingot = geometry.bm_to_object(bm, "GoldBar_Ingot", collection,
                                  bevel=bevel, texel=2.0, rng=rng, wear=wear)
    materials.assign([ingot], materials.make_material(
        f"M_GoldBar_{plan['material']}", plan["color"], plan["material"]))

    return {"objects": [ingot], "collision_boxes": [], "attachments": {}}
