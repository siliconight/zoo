"""ladder recipe: fixed vertical service ladder.

Two side rails, cylindrical rungs at constant spacing, optional wall
standoff brackets. Origin at floor center; the ladder plane faces -Y
(climb side), standoffs reach toward +Y (the wall). Proportions match
Deli Counter's generated ladders (0.5 m wide, ~0.3 m rung spacing) so a
Zoo ladder can dress a DC ladder slot without resizing.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]        # standoff from the wall plane
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    spacing = float(plan["params"].get("rung_spacing", 0.0)) or 0.3
    standoffs = bool(plan["params"].get("standoffs", 1))
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.2, rng=rng, wear=wear))

    rail = 0.05
    plane_y = -d / 2 + rail / 2            # the climb plane
    for side, x in (("L", -w / 2 + rail / 2), ("R", w / 2 - rail / 2)):
        bm = geometry.new_bm()
        geometry.add_box(bm, (x, plane_y, h / 2), (rail, rail, h))
        part(bm, f"Ladder_Rail_{side}")

    n_rungs = max(2, int(h / spacing))
    for i in range(n_rungs):
        z = spacing * (i + 1)
        if z > h - 0.05:
            break
        bm = geometry.new_bm()
        geometry.add_cylinder(bm, (0.0, plane_y, z), radius=0.018,
                              depth=w - rail * 2, segments=8, axis="X")
        part(bm, f"Ladder_Rung_{i + 1}")

    if standoffs and d > rail:
        for i, z in enumerate((h * 0.2, h * 0.8)):
            for side, x in (("L", -w / 2 + rail / 2), ("R", w / 2 - rail / 2)):
                bm = geometry.new_bm()
                geometry.add_box(bm, (x, 0.0, z), (rail * 0.8, d - rail, rail * 0.8))
                part(bm, f"Ladder_Standoff_{side}{i + 1}")

    # collision: the climbable slab (game code owns the climb volume itself)
    cboxes.append(((-w / 2, -d / 2, 0.0), (w / 2, -d / 2 + rail, h)))

    mat = materials.make_material(
        f"M_Ladder_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, mat)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_ladder_base": (0.0, plane_y, 0.0),
                            "ATT_ladder_top": (0.0, plane_y, h)}}
