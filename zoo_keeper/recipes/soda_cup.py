"""Soda cup recipe (low-poly hero): tapered paper cup (wider at the rim),
rolled lip, domed lid, and a straw. Origin at floor center."""
from __future__ import annotations

from ..bpylayer import geometry, materials

SEG = 12  # facet count — low for a PS1 silhouette


def build(plan, streams, collection):
    r = plan["dimensions"]["width"] / 2
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    has_lid = plan["params"].get("lid", 1)
    has_straw = plan["params"].get("straw", 1)
    objs, cboxes = [], []

    def part(bm, name, texel=3.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    # tapered body: narrower base, wider rim
    r_base = r * 0.72
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0, 0, h / 2), r_base, h, segments=SEG,
                          radius_top=r)
    part(bm, "Cup_Body")
    cboxes.append(((-r, -r, 0), (r, r, h)))

    # rolled lip at the rim
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0, 0, h - 0.006), r * 1.04, 0.012, segments=SEG)
    part(bm, "Cup_Lip")

    if has_lid:
        bm = geometry.new_bm()
        geometry.add_cylinder(bm, (0, 0, h + 0.004), r * 1.03, 0.012,
                              segments=SEG)
        part(bm, "Cup_Lid")
        # raised dome center
        bm = geometry.new_bm()
        geometry.add_hemisphere(bm, (0, 0, h + 0.01), r * 0.55, r * 0.55, 0.02,
                                segments=SEG)
        part(bm, "Cup_LidDome")

    if has_straw:
        bm = geometry.new_bm()
        geometry.add_cylinder(bm, (r * 0.3, 0, h + 0.03), 0.006, 0.10,
                              segments=6)
        part(bm, "Cup_Straw")

    cup_mat = materials.make_material(
        f"M_Cup_{plan['material']}", plan["color"], plan["material"])
    lid_mat = materials.make_material("M_Cup_lid", [0.90, 0.90, 0.92],
                                      "plastic")
    straw_mat = materials.make_material("M_Cup_straw", [0.85, 0.85, 0.88],
                                        "plastic")
    for o in objs:
        if "Lid" in o.name:
            materials.assign([o], lid_mat)
        elif "Straw" in o.name:
            materials.assign([o], straw_mat)
        else:
            materials.assign([o], cup_mat)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_lid": (0, 0, h)}}
