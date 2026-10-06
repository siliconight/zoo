"""Flat-top grill recipe: heavy steel cabinet, flat cooktop plate, raised
splash guards, front grease trap, control knobs, legs. All box/cylinder —
proven primitives. Origin at floor center, controls face -Y."""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import flat_top_grill_forms as grill_forms


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

    # The parts, from core.flat_top_grill_forms: the cabinet stands
    # KNOB_PROUD shallower than the slot and set back, so the knobs end on the
    # slot's front face and the module measures exactly (w, d, h) (1.80.0).
    for name, shape, centre, size in grill_forms.layout(w, d, h, n_knobs):
        bm = geometry.new_bm()
        if shape == "box":
            geometry.add_box(bm, centre, size)
        else:
            radius, length, axis = size
            geometry.add_cylinder(bm, centre, radius, length, segments=12,
                                  axis=axis)
        part(bm, name, texel=2.0 if name == "Grill_Cooktop" else 1.0)
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, h)))

    # plan["material"], not the literal "metal". These three were hard-coded,
    # which made this species' genome INERT: editing materials.default or a
    # style's material changed nothing at all, silently. A grill is stainless,
    # so its genome now says metal_bare and these follow it.
    kind = plan["material"]
    steel = materials.make_material("M_Grill_steel", plan["color"], kind)
    top = materials.make_material("M_Grill_cooktop",
                                  _darker(plan["color"], 0.4), kind)
    dark = materials.make_material("M_Grill_trim",
                                   _darker(plan["color"], 0.6), kind)
    for o in objs:
        if "Cooktop" in o.name or "GreaseTrap" in o.name:
            materials.assign([o], top)
        elif "Knob" in o.name or "Leg" in o.name:
            materials.assign([o], dark)
        else:
            materials.assign([o], steel)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_cook_center": (0, 0, h)}}
