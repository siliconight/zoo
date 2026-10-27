"""wall_clock recipe: a round office wall clock -- a dark rim, a white face, twelve hour marks, two hands.

Zoo 1.136.0, from the walker's bank comps (the factory's docs/reference/BANK_INTERIOR_COMPS.md, 2026-10-27): "a date
clock over the line (2, 4), a wall clock" -- the round schoolhouse clock every 1990s branch hung over its teller line
and in its back office. Minted by `tools/new_species.py`; shaped here.

ONE MATERIAL: the rim's dark, the face's white and the hands' and marks' black are COLOUR ONLY, in the `Wear` vertex
colour (`geometry.tint_wear`): one submission. The hands stand at ten past ten, the catalogue photograph's time, so a
clock never reads as stopped at a time someone chose.

Recipe frame: centre pivot, the wall at +Y and the face looking into the room at -Y (`security_camera`'s convention).
The module is exactly (w, d, h): the rim's disc is the width and the height, its depth the slot's depth.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials

SEGMENTS = 24            # a round face that reads round from across a lobby
RIM = 0.035              # the rim's width, the face inside it
FACE_IN = 0.018          # the face this far inside the rim's front: deep enough that the hands stay in the slot
#: an hour mark: width, depth, length. Its depth is two census tolerances and more: half buried in the face, half
#: proud of it, each side clear of the face's plane by more than 2.2 mm
MARK = (0.010, 0.008, 0.030)
#: the plate's edge this far inside the bezel: at 0.5 % of the radius it was a millimetre, inside the census's 2.2
PLATE_IN = 0.005
#: the minute hand stands this far in front of the hour hand and the marks, so the two never share a plane
HAND_STEP = 0.011
HAND_T = 0.006
BURY = 0.004
BACK_GAP = 0.006         # the back plate's front this far behind the face's

RIM_RGB = (0.08, 0.08, 0.09)
FACE_RGB = (0.95, 0.94, 0.90)
INK_RGB = (0.04, 0.04, 0.04)


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    r = min(w, h) / 2.0
    y_front = -d / 2.0
    objs = []

    def obj(bm, name, rgb):
        o = geometry.bm_to_object(bm, name, collection, bevel=0.0, texel=1.2, rng=rng, wear=wear)
        geometry.tint_wear(o, rgb)
        objs.append(o)

    # the rim: an open bezel the slot's whole depth (no caps, so the face shows through it) and a back plate the
    # full radius behind the face, whose ring between the face and the bezel is the rim a lobby reads
    face_y0 = y_front + FACE_IN
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, 0.0), r, d, segments=SEGMENTS, axis="Y", cap=False)
    plate_y0 = face_y0 + BACK_GAP
    geometry.add_cylinder(bm, (0.0, (plate_y0 + d / 2.0) / 2.0, 0.0), r - PLATE_IN, d / 2.0 - plate_y0,
                          segments=SEGMENTS, axis="Y")
    obj(bm, "WallClock_Rim", RIM_RGB)
    # the face: a thin white disc inside the rim, its front FACE_IN behind the bezel's, into the back plate
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, (face_y0 + plate_y0 + BURY) / 2.0, 0.0), r - RIM, plate_y0 + BURY - face_y0,
                          segments=SEGMENTS, axis="Y")
    obj(bm, "WallClock_Face", FACE_RGB)
    # twelve hour marks and two hands, standing proud of the face by their depth
    ink_y = face_y0 - 0.0005                    # 4.5 mm proud of the face, 3.5 mm into it
    bm = geometry.new_bm()
    mr = r - RIM - MARK[2] / 2.0 - 0.008
    for k in range(12):
        a = math.radians(30.0 * k)
        verts = geometry.add_box(bm, (0.0, 0.0, 0.0), (MARK[0], MARK[1], MARK[2]))
        rot = _rot_y(-a)
        for v in verts:
            x, z = v.co.x, v.co.z
            v.co.x = x * rot[0] + z * rot[1] + mr * math.sin(a)
            v.co.z = x * rot[2] + z * rot[3] + mr * math.cos(a)
            v.co.y += ink_y
    # ten past ten: the hour hand at 10:10, the minute hand at 2
    for length, frac, ang in ((0.50, 1.0, 305.0), (0.75, 0.8, 60.0)):
        hl = (r - RIM) * length
        verts = geometry.add_box(bm, (0.0, 0.0, 0.0), (HAND_T * 2.0 * frac + 0.006, MARK[1], hl))
        a = math.radians(ang)
        rot = _rot_y(-a)
        for v in verts:
            x, z = v.co.x, v.co.z + hl / 2.0
            v.co.x = x * rot[0] + z * rot[1]
            v.co.z = x * rot[2] + z * rot[3]
            v.co.y += ink_y - (HAND_STEP if frac < 1.0 else 0.0)
    obj(bm, "WallClock_Ink", INK_RGB)
    surface = materials.make_material(f"M_WallClock_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, surface)
    return {"objects": objs, "collision_boxes": [((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, h / 2.0))],
            "attachments": {"ATT_back": (0.0, d / 2.0, 0.0)}}


def _rot_y(a):
    """(xx, xz, zx, zz) of a turn by ``a`` in the face's plane (x, z)."""
    c, s = math.cos(a), math.sin(a)
    return (c, s, -s, c)
