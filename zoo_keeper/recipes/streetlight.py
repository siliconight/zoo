"""streetlight recipe: a parking-lot / street pole light — anchor base plate,
steel pole, shoebox head with an emissive sodium lens on the underside. Built
centered; the light-anchor pipeline places the pole TOP (+h/2) at the anchor
point, so Lux's downward spot spawns exactly under the lens and the base
lands on grade. The head sits a hair above the pole top so the lamp point is
never inside geometry. Pole gets a collision box — players bump into poles."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]      # head length
    d = plan["dimensions"]["depth"]      # head width
    h = plan["dimensions"]["height"]     # pole height (grade -> anchor)
    bevel, wear = plan["bevel"], plan["wear"]
    style = plan.get("style_block", {})
    rng = streams.stream("wear")
    z0 = -h / 2.0
    objs, cboxes = [], []

    def part(bm, name, texel=1.5, part_wear=None):
        obj = geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng,
            wear=wear if part_wear is None else part_wear)
        objs.append(obj)
        return obj

    # Anchor base plate.
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + 0.03), 0.16, 0.06, segments=10)
    part(bm, "Streetlight_Base")

    # Pole: grade to the anchor point at +h/2.
    pole_h = h - 0.06
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + 0.06 + pole_h / 2.0),
                          0.06, pole_h, segments=8)
    pole = part(bm, "Streetlight_Pole")
    cboxes.append(((-0.08, -0.08, z0), (0.08, 0.08, h / 2.0)))

    # Shoebox head, floated just above the pole top so the lamp point
    # (exactly at +h/2) sits in clear air under the lens.
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, h / 2.0 + 0.02 + 0.08), (w, d, 0.16))
    head = part(bm, "Streetlight_Head")

    # Lens: emissive underside, protruding a touch below the head.
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, h / 2.0 + 0.015),
                     (w * 0.8, d * 0.75, 0.02))
    lens_obj = geometry.bm_to_object(
        bm, "Streetlight_Lens", collection, bevel=0.0, texel=1.0,
        rng=rng, wear=0.0)
    objs.append(lens_obj)

    mat = materials.make_material(
        f"M_Streetlight_{plan['material']}", plan["color"], plan["material"])
    materials.assign([o for o in objs if o is not lens_obj], mat)
    lens = materials.make_emissive_material(
        "M_Streetlight_Lens",
        style.get("emissive_color", [1.0, 0.62, 0.24]),
        style.get("emissive_strength", 2.5))
    materials.assign([lens_obj], lens)

    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
