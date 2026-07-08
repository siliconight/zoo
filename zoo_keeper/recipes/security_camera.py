"""security_camera recipe: a wall-mounted CCTV camera — mount plate (against the
wall, +Y), a short arm, the body, a lens looking into the room (-Y), and a
status LED. Built centered so the bbox is (w, d, h); the genome's `wall` anchor
mates the mount plate to a wall. Face toward -Y."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    by = d / 2.0        # wall side (+Y)
    fy = -d / 2.0       # room side (-Y)
    objs, cboxes = [], []

    def part(bm, name, texel=2.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    # mount plate flush to the wall (spans full height so the bbox reaches h)
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, by - 0.015, 0.0), (w * 0.7, 0.03, h))
    part(bm, "SecurityCamera_Mount")

    # arm from the plate out to the body
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, d * 0.18, h * 0.12), (0.045, d * 0.4, 0.045))
    part(bm, "SecurityCamera_Arm")

    # body: the main camera box, angled to look down into the room
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, -d * 0.12, -h * 0.02), (w, d * 0.5, h * 0.62))
    part(bm, "SecurityCamera_Body")
    cboxes.append(((-w / 2.0, -d * 0.37, -h / 2.0), (w / 2.0, d * 0.13,
                                                     h * 0.29)))

    # lens looking out the front (-Y)
    lens_c = (0.0, fy + 0.03, -h * 0.02)
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, lens_c, h * 0.18, 0.06, segments=16, axis="Y")
    part(bm, "SecurityCamera_Lens")

    # tiny status LED
    bm = geometry.new_bm()
    geometry.add_box(bm, (w * 0.28, fy + 0.02, h * 0.12), (0.02, 0.02, 0.02))
    part(bm, "SecurityCamera_LED")

    body_mat = materials.make_material(
        f"M_SecurityCamera_{plan['material']}", plan["color"], plan["material"])
    lens_mat = materials.make_material("M_SecurityCamera_lens",
                                       [0.03, 0.04, 0.06], "glass")
    led_mat = materials.make_material("M_SecurityCamera_led",
                                      [0.85, 0.08, 0.05], "plastic")
    for o in objs:
        if "Lens" in o.name:
            materials.assign([o], lens_mat)
        elif "LED" in o.name:
            materials.assign([o], led_mat)
        else:
            materials.assign([o], body_mat)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_lens": lens_c}}
