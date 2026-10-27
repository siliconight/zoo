"""drive_up_tube recipe: a bank's drive-up lane station -- a pedestal cabinet on a curb island, the pneumatic tube's
carrier receptacle at a car window's height, a speaker grille and a call button, the tube rising out of its top.

Zoo 1.138.0, from the walker's bank list, outside (the factory's docs/reference/BANK_INTERIOR_COMPS.md, researched): "a
drive-up lane with a pneumatic tube (the canister to the teller and back) was common from the 1960s and dwindled only
with the ATM." Minted by `tools/new_species.py`; shaped here. The canopy over the lane is not this species: Lot lays
the lane and `canopy_lights` already roofs a forecourt.

ONE MATERIAL: the island's concrete, the cabinet's paint, the receptacle's dark mouth, the grille, the button and the
tube's steel are COLOUR ONLY, in the `Wear` vertex colour (`geometry.tint_wear`): one submission.

Recipe frame: centre pivot, the lane at -Y, where a driver's window comes alongside. The module is exactly (w, d, h):
the island is the footprint, the tube the height.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

ISLAND_H = 0.15          # a curb's height
CAB_W_F, CAB_D_F = 0.70, 0.62
CAB_TOP = 1.55           # the cabinet's top over the ground: a sedan's roof
#: the receptacle: its sill at a car window's height (1.05 m, the sill of a sedan's window), 0.38 m wide
REC_SILL = 1.05
REC = (0.38, 0.30)       # width, height
REC_DEPTH = 0.16         # how far the dark mouth goes into the cabinet
REC_LIP = 0.035          # the hood's lip stands this far proud of the cabinet's face
GRILLE = (0.18, 0.12)
GRILLE_Z = 1.42
BUTTON = 0.035
TUBE_R = 0.065
COLLAR = (0.11, 0.12)    # the tube's collar on the cabinet: radius, height
BURY = 0.004
SHY = 0.003         # a part this far off another's plane: past the census's 2.2 mm
SEG = 12

ISLAND_RGB = (0.60, 0.59, 0.56)
CAB_RGB = (0.76, 0.72, 0.60)
MOUTH_RGB = (0.07, 0.07, 0.08)
LIP_RGB = (0.62, 0.63, 0.64)
GRILLE_RGB = (0.16, 0.16, 0.17)
BUTTON_RGB = (0.75, 0.12, 0.10)
TUBE_RGB = (0.66, 0.67, 0.69)


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    wear = plan["wear"]
    rng = streams.stream("wear")
    objs = []
    floor = -h / 2.0

    def finish(bm, name, rgb):
        o = geometry.bm_to_object(bm, name, collection, bevel=0.0, texel=1.2, rng=rng, wear=wear)
        geometry.tint_wear(o, rgb)
        objs.append(o)

    def box(name, lo, hi, rgb):
        bm = geometry.new_bm()
        geometry.add_box(bm, tuple((lo[i] + hi[i]) / 2.0 for i in range(3)), tuple(hi[i] - lo[i] for i in range(3)))
        finish(bm, name, rgb)

    # the curb island: the whole footprint
    box("DriveUp_Island", (-w / 2.0, -d / 2.0, floor), (w / 2.0, d / 2.0, floor + ISLAND_H), ISLAND_RGB)
    # the cabinet, set back from the lane so the receptacle's lip stays inside the island
    cw, cd = w * CAB_W_F, d * CAB_D_F
    cy0 = -d / 2.0 + REC_LIP + 0.02
    cab_lo = (-cw / 2.0, cy0, floor + ISLAND_H - BURY)
    cab_hi = (cw / 2.0, cy0 + cd, floor + CAB_TOP)
    box("DriveUp_Cabinet", cab_lo, cab_hi, CAB_RGB)
    # the receptacle: a dark mouth sunk into the cabinet's face, a steel hood over it standing proud
    rw, rh = REC
    rz0 = floor + REC_SILL
    # the mouth's face 6 mm proud of the cabinet's and 29 mm behind the hood's, so the hood frames it as a recess; 4 mm
    # inside the hood's bars, clear of their planes (the census's 2.2 mm)
    m_in = 0.004
    box("DriveUp_Mouth", (-rw / 2.0 + m_in, cy0 - 0.006, rz0 + m_in), (rw / 2.0 - m_in, cy0 + REC_DEPTH, rz0 + rh - m_in),
        MOUTH_RGB)
    bm = geometry.new_bm()
    lip = 0.03
    for lo, hi in (((-rw / 2.0 - lip, cy0 - REC_LIP, rz0 + rh), (rw / 2.0 + lip, cy0 + BURY, rz0 + rh + lip)),
                   ((-rw / 2.0 - lip, cy0 - REC_LIP, rz0 - lip), (rw / 2.0 + lip, cy0 + BURY, rz0)),
                   # the sides run halfway into the top and the bottom, and stand SHY of them by 3 mm on every
                   # outer face (front, back, outside): ended on the bars, the census read their ends on the bars'
                   # faces; run into them flush, it read their fronts, backs and outsides on the bars' planes
                   ((-rw / 2.0 - lip + SHY, cy0 - REC_LIP + SHY, rz0 - lip / 2.0),
                    (-rw / 2.0, cy0 + BURY + SHY, rz0 + rh + lip / 2.0)),
                   ((rw / 2.0, cy0 - REC_LIP + SHY, rz0 - lip / 2.0),
                    (rw / 2.0 + lip - SHY, cy0 + BURY + SHY, rz0 + rh + lip / 2.0))):
        geometry.add_box(bm, tuple((lo[i] + hi[i]) / 2.0 for i in range(3)), tuple(hi[i] - lo[i] for i in range(3)))
    finish(bm, "DriveUp_Hood", LIP_RGB)
    # the speaker grille and the call button on the face above it, standing a few mm proud
    gw, gh = GRILLE
    gz = floor + GRILLE_Z
    # buried twice as deep as the hood: at one depth the census read their backs on one plane inside the cabinet
    box("DriveUp_Grille", (-gw / 2.0, cy0 - 0.006, gz - gh / 2.0), (gw / 2.0, cy0 + 2.0 * BURY, gz + gh / 2.0),
        GRILLE_RGB)
    bx = gw / 2.0 + 0.06
    box("DriveUp_Button", (bx - BUTTON / 2.0, cy0 - 0.012, gz - BUTTON / 2.0),
        (bx + BUTTON / 2.0, cy0 + BURY, gz + BUTTON / 2.0), BUTTON_RGB)
    # the tube: a collar on the cabinet's top, the tube out of it to the slot's top
    tc_y = cy0 + cd / 2.0
    bm = geometry.new_bm()
    cr, chh = COLLAR
    geometry.add_cylinder(bm, (0.0, tc_y, cab_hi[2] - BURY + chh / 2.0), cr, chh + BURY, segments=SEG, axis="Z")
    finish(bm, "DriveUp_Collar", TUBE_RGB)
    bm = geometry.new_bm()
    t0 = cab_hi[2] + chh - 0.02
    geometry.add_cylinder(bm, (0.0, tc_y, (t0 + h / 2.0) / 2.0), TUBE_R, h / 2.0 - t0, segments=SEG, axis="Z")
    finish(bm, "DriveUp_Tube", TUBE_RGB)
    body = materials.make_material(f"M_DriveUp_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, body)
    # the island and the cabinet stop a body or a car; the tube overhead is out of reach
    return {"objects": objs,
            "collision_boxes": [((-w / 2.0, -d / 2.0, floor), (w / 2.0, d / 2.0, floor + ISLAND_H)),
                                (cab_lo, cab_hi)],
            "attachments": {"ATT_tube_top": (0.0, tc_y, h / 2.0)}}
