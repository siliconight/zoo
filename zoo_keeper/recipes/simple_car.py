"""Simple car recipe: body, cabin, four wheels, bumpers. Length runs +Y."""
from __future__ import annotations

from ..bpylayer import geometry, materials

CABIN = {  # body_style -> (length frac, y-center frac)
    "sedan": (0.45, 0.02), "hatchback": (0.52, 0.10), "coupe": (0.40, -0.02),
}


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    length = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    seg = plan["params"]["wheel_segments"]
    wheel_r = h * 0.22
    body_z0 = wheel_r * 0.85
    body_h = h * 0.55 - body_z0 + h * 0.10
    cabin_h = h - (body_z0 + body_h)
    objs, cboxes = [], []

    def part(bm, name, texel=0.5):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel,
            rng=rng, wear=wear))

    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, body_z0 + body_h / 2),
                     (w, length * 0.96, body_h))
    part(bm, "Car_Body")
    cboxes.append(((-w / 2, -length / 2, body_z0),
                   (w / 2, length / 2, body_z0 + body_h)))

    cfrac, cshift = CABIN.get(plan["params"]["body_style"], CABIN["sedan"])
    clen = length * cfrac
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, length * cshift, body_z0 + body_h + cabin_h / 2),
                     (w * 0.86, clen, cabin_h))
    part(bm, "Car_Cabin")
    cboxes.append(((-w * 0.43, length * cshift - clen / 2,
                    body_z0 + body_h),
                   (w * 0.43, length * cshift + clen / 2, h)))

    wheel_y = length * 0.32
    wheel_x = w / 2 - 0.04
    i = 0
    for sy in (-1, 1):
        for sx in (-1, 1):
            i += 1
            bm = geometry.new_bm()
            geometry.add_cylinder(bm, (sx * wheel_x, sy * wheel_y, wheel_r),
                                  radius=wheel_r, depth=0.22,
                                  segments=seg, axis="X")
            part(bm, f"Car_Wheel_{i}", texel=1.0)

    # Windows: thin tinted panes sitting proud of the cabin faces (TDD
    # required part). One object, four panes; near-zero bevel and wear so
    # the glass stays clean.
    zc = body_z0 + body_h + cabin_h * 0.52
    pane_h = cabin_h * 0.55
    cy = length * cshift
    bm = geometry.new_bm()
    for sy in (-1, 1):  # windshield / rear window
        geometry.add_box(bm, (0, cy + sy * clen / 2, zc),
                         (w * 0.70, 0.02, pane_h))
    for sx in (-1, 1):  # side windows
        geometry.add_box(bm, (sx * w * 0.43, cy, zc),
                         (0.02, clen * 0.72, pane_h))
    objs.append(geometry.bm_to_object(
        bm, "Car_Windows", collection, bevel=0.001, texel=0.5,
        rng=rng, wear=0.0))

    for tag, sy in (("F", -1), ("R", 1)):
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, sy * (length / 2 - 0.02),
                              body_z0 + 0.05),
                         (w * 0.98, 0.10, 0.14))
        part(bm, f"Car_Bumper_{tag}")

    body_mat = materials.make_material(
        f"M_Car_{plan['material']}", plan["color"], plan["material"])
    dark = materials.make_material(
        "M_Car_trim_rubber", [0.05, 0.05, 0.05], "rubber")
    glass = materials.make_material(
        "M_Car_glass", [0.05, 0.08, 0.10], "glass")
    body = [o for o in objs if "Body" in o.name or "Cabin" in o.name]
    windows = [o for o in objs if "Windows" in o.name]
    materials.assign(body, body_mat)
    materials.assign(windows, glass)
    materials.assign([o for o in objs if o not in body and o not in windows],
                     dark)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_roof": (0, 0, h),
                            "ATT_driver_seat": (-w * 0.22, -length * 0.05,
                                                body_z0 + body_h),
                            "ATT_trunk": (0, length * 0.42,
                                          body_z0 + body_h)}}
