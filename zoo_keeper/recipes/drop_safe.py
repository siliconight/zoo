"""drop_safe recipe: a small floor/drop safe — body, recessed door, combo dial,
handle, and a top drop slot. Origin at floor center, face toward -Y."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def _darker(c, f=0.55):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    fy = -d / 2.0
    objs, cboxes = [], []

    def part(bm, name, texel=1.6):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    # body sits back 6cm so the proud door/dial/handle reach the nominal front
    # (-d/2) without pushing the bbox past the genome depth range at any size.
    body_d = max(0.1, d - 0.06)
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, d / 2.0 - body_d / 2.0, h / 2.0),
                     (w, body_d, h))
    part(bm, "DropSafe_Body")
    cboxes.append(((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h)))
    face = -d / 2.0 + 0.06        # body front plane

    # thick door proud of the body face, reaching the nominal front
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, face - 0.03, h * 0.5), (w * 0.82, 0.06, h * 0.78))
    part(bm, "DropSafe_Door")

    # combo dial (a short cylinder proud of the door), centred, front at -d/2
    dial_c = (0.0, fy + 0.02, h * 0.56)
    if plan["params"].get("dial", 1):
        bm = geometry.new_bm()
        geometry.add_cylinder(bm, dial_c, min(w, h) * 0.13, 0.04,
                              segments=16, axis="Y")
        part(bm, "DropSafe_Dial")

    # a stubby lever handle to the side
    bm = geometry.new_bm()
    geometry.add_box(bm, (w * 0.28, fy + 0.03, h * 0.42), (0.05, 0.06, h * 0.30))
    part(bm, "DropSafe_Handle")

    # recessed drop slot across the top front (inside the body -> no protrusion)
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, face + 0.04, h - 0.03), (w * 0.5, 0.06, 0.02))
    part(bm, "DropSafe_Slot")

    body_mat = materials.make_material(
        f"M_DropSafe_{plan['material']}", plan["color"], plan["material"])
    trim = materials.make_material("M_DropSafe_trim",
                                   _darker(plan["color"]), "metal")
    black = materials.make_material("M_DropSafe_slot", [0.02, 0.02, 0.02],
                                    "plastic")
    for o in objs:
        if "Slot" in o.name:
            materials.assign([o], black)
        elif "Dial" in o.name or "Handle" in o.name:
            materials.assign([o], trim)
        else:
            materials.assign([o], body_mat)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_dial": dial_c}}
