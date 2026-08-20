"""Simple car recipe: body, cabin, four wheels, bumpers. Length runs +Y.

REWRITTEN AFTER LOOKING AT IT. The first version had the right dimensions and
the wrong assembly: a 0.64 m wheel and a 2.75 m wheelbase, both correct to
within a few centimetres of a real sedan, hung on a single full-width slab
with a cabin sitting on top of it. Rendered, it read as a toy pickup. The four
faults, in the order they cost:

  * ONE UNBROKEN SLAB from 0.27 to 0.94 m, full width top to bottom. No
    beltline, no shoulder, nothing for a highlight to break on.
  * THE CABIN SAT ON THE BODY with a 12.3 cm step per side and no transition,
    which is what made it read as a separate box balanced on a plank.
  * WHEELS 4 cm INBOARD of the widest point, with no arch. A disc pressed
    against a flat wall reads as stuck on.
  * THE CABIN WAS CENTRED, so hood and trunk were the same length. A sedan has
    a long hood and a short deck; symmetric reads as a cab-over truck.

None of that needed new dimensions. It needed the body split into a rocker, a
body and a shoulder, the wheels tucked under an overhang, and the greenhouse
tapered instead of stacked. Triangle cost is a few hundred against a 12,000
budget.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

CABIN = {  # body_style -> (length frac, y-center frac)
    # +Y is the REAR (the front bumper is placed at -Y), so a positive shift
    # moves the greenhouse back and lengthens the hood. The old table was
    # near-centred, which is why every body style read as a pickup.
    "sedan": (0.46, 0.07), "hatchback": (0.54, 0.12), "coupe": (0.40, 0.03),
}

#: Fractions of the overall width. The shoulder tapers to meet the cabin, so
#: the step between them is ~2.5 cm rather than the 12.3 cm that made the
#: cabin look balanced on top of the body.
ROCKER_W, SHOULDER_TOP, CABIN_W, ROOF_W = 0.88, 0.93, 0.90, 0.88

#: How far the widest body point overhangs the tyre. This IS the wheel arch:
#: there is no boolean here, and none is needed -- a wheel tucked under an
#: overhanging shoulder reads as arched, and a wheel flush with the side does
#: not, whatever else is true about it.
WHEEL_INSET = 0.11


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    length = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    seg = plan["params"]["wheel_segments"]
    wheel_r = h * 0.22
    objs, cboxes = [], []

    # Height bands. The body overlaps the rocker and the shoulder overlaps the
    # body on purpose: an overlap is one solid after shading, a butt joint is
    # a seam that catches light along its whole length.
    rocker_z0, rocker_z1 = wheel_r * 0.55, h * 0.32
    body_z0, body_z1 = h * 0.21, h * 0.565
    shoulder_z1 = h * 0.655
    cabin_z0 = shoulder_z1

    def part(bm, name, texel=0.5):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel,
            rng=rng, wear=wear))

    # --- rocker: narrow and low, so the body above it overhangs the tyres ---
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, (rocker_z0 + rocker_z1) / 2),
                     (w * ROCKER_W, length * 0.80, rocker_z1 - rocker_z0))
    part(bm, "Car_Body_Rocker")

    # --- main body: the widest point, and the arch overhang ----------------
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, (body_z0 + body_z1) / 2),
                     (w, length * 0.96, body_z1 - body_z0))
    part(bm, "Car_Body")

    # --- shoulder: tapers in to meet the greenhouse ------------------------
    bm = geometry.new_bm()
    verts = geometry.add_box(bm, (0, 0, (body_z1 + shoulder_z1) / 2),
                             (w, length * 0.94, shoulder_z1 - body_z1))
    geometry.taper_z(verts, SHOULDER_TOP)
    part(bm, "Car_Body_Shoulder")

    cboxes.append(((-w / 2, -length / 2, rocker_z0),
                   (w / 2, length / 2, shoulder_z1)))

    # --- greenhouse: tapered, not a box on a plank -------------------------
    cfrac, cshift = CABIN.get(plan["params"]["body_style"], CABIN["sedan"])
    clen = length * cfrac
    cy = length * cshift
    bm = geometry.new_bm()
    verts = geometry.add_box(bm, (0, cy, (cabin_z0 + h) / 2),
                             (w * CABIN_W, clen, h - cabin_z0))
    geometry.taper_z(verts, ROOF_W / CABIN_W)
    part(bm, "Car_Cabin")
    cboxes.append(((-w * CABIN_W / 2, cy - clen / 2, cabin_z0),
                   (w * CABIN_W / 2, cy + clen / 2, h)))

    # --- wheels, tucked under the overhang ---------------------------------
    wheel_y = length * 0.32
    wheel_x = w / 2 - WHEEL_INSET
    for i, (sy, sx) in enumerate(
            [(sy, sx) for sy in (-1, 1) for sx in (-1, 1)], start=1):
        bm = geometry.new_bm()
        geometry.add_cylinder(bm, (sx * wheel_x, sy * wheel_y, wheel_r),
                              radius=wheel_r, depth=0.22,
                              segments=seg, axis="X")
        part(bm, f"Car_Wheel_{i}", texel=1.0)

    # --- glazing: INSET, so it reads as glass in an aperture ---------------
    # The old panes stood proud of the cabin faces, which reads as a sticker.
    # Sitting them just inside the (now tapered) greenhouse gives the pillars
    # something to be.
    zc = cabin_z0 + (h - cabin_z0) * 0.55
    pane_h = (h - cabin_z0) * 0.52
    inset = 0.015
    cw = w * CABIN_W * ((ROOF_W / CABIN_W) + 1.0) / 2.0    # width at the panes
    bm = geometry.new_bm()
    for sy in (-1, 1):                       # windshield / rear window
        geometry.add_box(bm, (0, cy + sy * (clen / 2 - inset), zc),
                         (cw * 0.80, 0.02, pane_h))
    for sx in (-1, 1):                       # side glass, short of the pillars
        geometry.add_box(bm, (sx * (cw / 2 - inset), cy, zc),
                         (0.02, clen * 0.66, pane_h))
    objs.append(geometry.bm_to_object(
        bm, "Car_Windows", collection, bevel=0.001, texel=0.5,
        rng=rng, wear=0.0))

    # --- bumpers ------------------------------------------------------------
    for tag, sy in (("F", -1), ("R", 1)):
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, sy * (length / 2 - 0.03),
                              body_z0 + (body_z1 - body_z0) * 0.22),
                         (w * 0.96, 0.12, (body_z1 - body_z0) * 0.34))
        part(bm, f"Car_Bumper_{tag}")

    body_mat = materials.make_material(
        f"M_Car_{plan['material']}", plan["color"], plan["material"])
    dark = materials.make_material(
        "M_Car_trim_rubber", [0.05, 0.05, 0.05], "rubber")
    glass = materials.make_material(
        "M_Car_glass", [0.05, 0.08, 0.10], "glass")
    # Name-prefix match, not a substring hunt: the body is now four objects
    # and `"Body" in name` would have quietly handed the rocker and shoulder
    # to the rubber material.
    body = [o for o in objs
            if o.name.startswith(("Car_Body", "Car_Cabin"))]
    windows = [o for o in objs if o.name.startswith("Car_Windows")]
    materials.assign(body, body_mat)
    materials.assign(windows, glass)
    materials.assign([o for o in objs if o not in body and o not in windows],
                     dark)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_roof": (0, cy, h),
                            "ATT_driver_seat": (-w * 0.22, cy - clen * 0.15,
                                                cabin_z0),
                            "ATT_trunk": (0, length * 0.42, shoulder_z1)}}
