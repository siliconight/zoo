"""Flat-top grill recipe: heavy steel cabinet, flat cooktop plate, raised
splash guards, front grease trap, control knobs, legs. All box/cylinder —
proven primitives. Origin at floor center, controls face -Y."""
from __future__ import annotations

from ..bpylayer import geometry, materials

PLATE_T = 0.03
GUARD_T = 0.02


def _darker(c, f=0.7):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    n_knobs = plan["params"].get("knobs", 3)
    objs, cboxes = [], []

    def part(bm, name, texel=1.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    leg_h = 0.12
    guard_h = 0.12
    surface_z = h - guard_h            # cooking surface (~counter height)
    body_h = surface_z - PLATE_T - leg_h

    # cabinet body
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, leg_h + body_h / 2), (w, d, body_h))
    part(bm, "Grill_Body")
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, h)))

    # cooktop plate — top surface at counter height
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, surface_z - PLATE_T / 2),
                     (w * 0.98, d * 0.98, PLATE_T))
    part(bm, "Grill_Cooktop", texel=2.0)

    # splash guards rise from the surface to the overall height
    gz = surface_z + guard_h / 2
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, d / 2 - GUARD_T / 2, gz), (w, GUARD_T, guard_h))
    part(bm, "Grill_SplashGuard_B")
    for side, sx in (("L", -1), ("R", 1)):
        bm = geometry.new_bm()
        geometry.add_box(bm, (sx * (w / 2 - GUARD_T / 2), 0, gz),
                         (GUARD_T, d, guard_h))
        part(bm, f"Grill_SplashGuard_{side}")

    # grease trap slot along the front lip
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, -d / 2 + 0.02, surface_z - PLATE_T - 0.015),
                     (w * 0.7, 0.03, 0.03))
    part(bm, "Grill_GreaseTrap")

    # control knobs on the front
    for i in range(n_knobs):
        x = (i - (n_knobs - 1) / 2) * (w * 0.14)
        bm = geometry.new_bm()
        geometry.add_cylinder(bm, (x, -d / 2 - 0.02, leg_h + body_h * 0.6),
                              0.022, 0.03, segments=12, axis="Y")
        part(bm, f"Grill_Knob_{i + 1}")

    # legs
    i = 0
    for sx in (-1, 1):
        for sy in (-1, 1):
            i += 1
            bm = geometry.new_bm()
            geometry.add_box(bm, (sx * (w / 2 - 0.06), sy * (d / 2 - 0.06),
                                  leg_h / 2), (0.05, 0.05, leg_h))
            part(bm, f"Grill_Leg_{i}")

    steel = materials.make_material("M_Grill_steel", plan["color"], "metal")
    top = materials.make_material("M_Grill_cooktop",
                                  _darker(plan["color"], 0.4), "metal")
    dark = materials.make_material("M_Grill_trim",
                                   _darker(plan["color"], 0.6), "metal")
    for o in objs:
        if "Cooktop" in o.name or "GreaseTrap" in o.name:
            materials.assign([o], top)
        elif "Knob" in o.name or "Leg" in o.name:
            materials.assign([o], dark)
        else:
            materials.assign([o], steel)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_cook_center": (0, 0, h)}}
