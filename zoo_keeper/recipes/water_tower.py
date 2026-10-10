"""water_tower recipe: the landmark beyond the plate's edge (Zoo 1.95.0, roadmap 228 step C).

A tank on four braced legs with a cap and a red beacon: the one cue the edge menu's frames read
as a landmark, standing some 90 m past the north edge in the mockup. The steel is the style's
painted metal in two parts (the legs and braces; the tank and its cap); the beacon is an
emissive `_Lens` so Lux's binder owns it. Centre pivot, bottom at -h/2, no collision: it is
backdrop. `core.backdrop_forms.tower_parts` holds the proportions.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import backdrop_forms as BF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    parts = BF.tower_parts(w, h)
    objs = []

    bm = geometry.new_bm()
    for centre, size in parts["legs"] + parts["braces"]:
        geometry.add_box(bm, centre, size)
    objs.append(geometry.bm_to_object(bm, "WaterTower_Legs", collection, bevel=bevel,
                                      texel=1.0, rng=rng, wear=wear))

    bm = geometry.new_bm()
    (tc, tr, th) = parts["tank"]
    geometry.add_cylinder(bm, tc, tr, th, segments=BF.TANK_SEGMENTS)
    (cc, cr, ch) = parts["cap"]
    cap = geometry.add_cylinder(bm, cc, cr, ch, segments=BF.TANK_SEGMENTS)
    geometry.taper_z(cap, 0.08)
    objs.append(geometry.bm_to_object(bm, "WaterTower_Tank", collection, bevel=bevel,
                                      texel=1.0, rng=rng, wear=wear))
    steel = materials.make_material(f"M_WaterTower_{plan['material']}", plan["color"],
                                    plan["material"])
    materials.assign(objs, steel)

    bm = geometry.new_bm()
    (bc, br) = parts["beacon"]
    geometry.add_ellipsoid(bm, bc, (br, br, br), u_seg=10, v_seg=6)
    beacon = geometry.bm_to_object(bm, "WaterTower_Beacon", collection, bevel=0.0,
                                   texel=1.0, rng=rng, wear=0.0)
    materials.assign([beacon], materials.make_emissive_material(
        "M_WaterTower_Beacon_Lens", BF.BEACON_RGB, BF.BEACON_STRENGTH))
    objs.append(beacon)
    return {"objects": objs, "collision_boxes": [], "attachments": {}}
