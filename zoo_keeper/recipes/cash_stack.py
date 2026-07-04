"""Cash stack recipe: a vertical stack of banded bill straps — heist loot.
Origin at floor center; straps stack up +Z, a paper band wraps each seam."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    bw = plan["dimensions"]["width"]     # bill width  (X)
    bd = plan["dimensions"]["depth"]     # bill depth  (Y)
    rng = streams.stream("wear")
    bevel, wear = plan["bevel"], plan["wear"]
    n = int(plan["params"].get("stacks", 1))
    strap_h = plan["params"].get("strap_h", 0.011)
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=4.0, rng=rng, wear=wear))

    for i in range(n):
        z = strap_h / 2 + i * strap_h
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, 0, z), (bw, bd, strap_h * 0.96))
        part(bm, f"Cash_Stack_{i + 1}")
        # paper band around the middle: proud in Y, inset in X, within height
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, 0, z), (bw * 0.26, bd * 1.05, strap_h * 0.9))
        part(bm, f"Cash_Band_{i + 1}")

    total_h = n * strap_h
    cboxes.append(((-bw / 2, -bd / 2, 0), (bw / 2, bd / 2, total_h)))

    bill = materials.make_material(
        f"M_Cash_{plan['material']}", plan["color"], plan["material"])
    band = materials.make_material("M_Cash_band", [0.86, 0.80, 0.62], "paper")
    bands = [o for o in objs if "Band" in o.name]
    materials.assign(bands, band)
    materials.assign([o for o in objs if o not in bands], bill)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_center": (0, 0, total_h)}}
