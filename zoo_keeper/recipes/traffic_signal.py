"""traffic_signal recipe: a mast-arm signal with a luminaire arm.

Roadmap 153, the 1990s American street. A suburban Pennsylvania
intersection carries a galvanised pole on the corner with a mast arm
reaching over the near lanes, a three-lens head hung from its end and a
second head on the pole for the near stop line -- and, on the other side
of the same pole, a cobra-head luminaire arm lighting the junction. That
second arm is why the POLE IS THE MODULE'S CENTRE: the slot is the whole
reach, the pole stands in the middle of it, and the greybox box Lot draws
for the slot is the pole's own column (`site_furniture.FOOTPRINT`) rather
than a five-metre box lying across the carriageway.

The lenses are emissive -- red at the top, amber, green -- so Lux's glow
pass and a night exterior have something to catch, the way the
streetlight's lens does. Which lens is LIT is not baked: all three carry
one emissive material at a low strength, and gameplay or a Lux tuning row
drives `emissive_energy` if a level ever wants a working signal. A signal
whose state is baked is a signal that is wrong half the time.

Extents are exactly (w, d, h). Collision is the POLE only -- a body walks
under an arm.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

POLE_D = 0.22
ARM_D = 0.14
LUM_D = 0.10
HEAD_W = 0.34         # a 12-inch three-lens head
HEAD_D = 0.30
HEAD_H = 1.05
LENS_R = 0.11


def _head(bm, lens_bm, centre):
    """A three-lens head hung with its top at ``centre``, facing -y."""
    cx, cy, cz = centre
    geometry.add_box(bm, (cx, cy, cz - HEAD_H / 2.0), (HEAD_W, HEAD_D, HEAD_H))
    for i in range(3):
        lz = cz - HEAD_H * (0.19 + 0.31 * i)
        y = cy - (HEAD_D / 2.0 + 0.012)
        geometry.add_cylinder(lens_bm, (cx, y, lz), LENS_R, 0.02,
                              segments=8, axis="Y")
        geometry.add_box(bm, (cx, y - 0.055, lz + LENS_R * 0.8),
                         (HEAD_W * 0.92, 0.11, 0.03))          # the visor
    geometry.add_box(bm, (cx, cy, cz + 0.03), (HEAD_W * 0.5, HEAD_D * 0.5, 0.06))


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]      # mast arm + luminaire arm, tip to tip
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]     # grade to the top of the pole
    bevel, wear = plan["bevel"], plan["wear"]
    style = plan.get("style_block", {})
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0
    steel = []

    def part(bm, name, texel=1.4, part_bevel=None):
        obj = geometry.bm_to_object(
            bm, name, collection, bevel=bevel if part_bevel is None else part_bevel,
            texel=texel, rng=rng, wear=wear)
        objs.append(obj)
        steel.append(obj)
        return obj

    mast = w * 0.62                      # the signal arm, over the road
    lum = w - mast                       # the luminaire arm, the other way
    arm_z = h / 2.0 - 0.45
    lum_z = h / 2.0 - 0.12

    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + 0.07), 0.24, 0.14, segments=10)
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + (h - 0.14) / 2.0 + 0.07),
                          POLE_D / 2.0, h - 0.14, segments=10,
                          radius_top=POLE_D * 0.45)
    # the mast arm and its gusset
    geometry.add_cylinder(bm, (mast / 2.0, 0.0, arm_z), ARM_D / 2.0, mast,
                          segments=8, axis="X", radius_top=ARM_D * 0.55)
    geometry.add_box(bm, (POLE_D * 1.2, 0.0, arm_z - 0.22), (0.5, 0.05, 0.42))
    # the luminaire arm, rising to a cobra head over the kerb
    geometry.add_cylinder(bm, (-lum / 2.0, 0.0, lum_z), LUM_D / 2.0, lum,
                          segments=8, axis="X", radius_top=LUM_D * 0.7)
    part(bm, "TrafficSignal_Mast")

    bm = geometry.new_bm()
    lens_bm = geometry.new_bm()
    _head(bm, lens_bm, (mast * 0.92, 0.0, arm_z - 0.08))       # over the road
    _head(bm, lens_bm, (POLE_D * 1.4, 0.0, arm_z - 0.60))      # the near head
    # the cobra head at the luminaire arm's tip
    verts = geometry.add_box(bm, (-lum * 0.94, 0.0, lum_z - 0.07),
                             (0.58, 0.28, 0.14))
    geometry.taper_z(verts, 0.75, 1.0)
    part(bm, "TrafficSignal_Heads", texel=1.6)
    lenses = geometry.bm_to_object(lens_bm, "TrafficSignal_Lenses", collection,
                                   bevel=0.0, texel=1.0, rng=rng, wear=0.0)
    objs.append(lenses)

    cboxes.append(((-POLE_D / 2.0, -POLE_D / 2.0, z0),
                   (POLE_D / 2.0, POLE_D / 2.0, h / 2.0)))

    mat = materials.make_material(
        f"M_TrafficSignal_{plan['material']}", plan["color"], plan["material"])
    materials.assign(steel, mat)
    glow = materials.make_emissive_material(
        "M_TrafficSignal_Lens",
        style.get("emissive_color", [0.95, 0.55, 0.20]),
        style.get("emissive_strength", 1.6))
    materials.assign([lenses], glow)
    # the slot is exact; the detail is not (geometry.fit_to)
    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_lamp": (-lum * 0.94, 0.0, lum_z - 0.14)}}
