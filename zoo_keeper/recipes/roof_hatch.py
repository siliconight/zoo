"""roof_hatch recipe: a roof scuttle -- a steel curb around a ladder's opening, with a hinged lid.

Factory roadmap 170: 43 roof ladders in the library climb out through a bare hole in the slab. This is
the thing that stands around that hole. The curb is four short walls on the slab, the slot's exact
(w, d, h); the lid is a plate the size of the curb's top, hinged along the back (local -Y) edge.

THE LID IS THE STATE. Deli Counter's `hatch` machine (interactives.py) has two: `open`, the default,
and `closed`. The state rides in on ``plan["module"]["state"]`` (None is open).

- `open`: the lid stands vertical on its hinge (OPEN_DEG 90), the way a hold-open arm holds a real
  scuttle lid, INSIDE the curb's footprint: Deli Counter's placement gate measures a module's whole
  footprint against its slot (0.25 m), and a lid leaning 10 degrees past vertical stood 0.33 m
  outside it on cold run 9315. The climber comes up through the hole and steps
  off toward local +Y -- Deli Counter turns the slot so that is the side the ladder's body occupies
  (`roof_hatch.rot_for`), so the raised lid is behind them. The lid keeps a collision box in this
  state: it is a sheet of steel a body on the roof walks into, and the walker's rule is "if I see
  collision, I expect collision".
- `closed`: the lid lies flush in the curb's top, its own collision box over the hole.

`fit_objects` is the curb: the raised lid is art above the slot, as a swung door leaf is beside its
frame, and must not drag the module's fit or its pivot.

Built centred; bottom at -h/2.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials

STATES = ("open", "closed")
CURB_T = 0.06        # m; the curb wall's thickness
LID_T = 0.035        # m; the lid plate
OPEN_DEG = 90.0      # the lid's angle from flat when open: vertical, inside the curb's footprint
HINGE_R = 0.018      # m; the hinge rod
HINGE_IN = 0.04      # m; the hinge line sits this far inside the back wall's outer face
LIP = 0.005          # m; the lid's edges stop this short of the curb's outer planes
SKIRT = 0.004        # m; the closed lid sinks this far into the curb's top (core.floaters' FLOATER_SKIRT)
#: The floor form's frame, linear RGB: safety yellow, the colour a person reads as "opening here"
#: across a room (1.114.0, the factory's roadmap 265).
SAFETY_YELLOW = (0.86, 0.64, 0.04)


def _ring(bm, w, d, t, z0, z1):
    """A rectangular ring: outer (w, d), wall thickness t, from z0 to z1. Shared vertices."""
    import bmesh
    ox, oy = w / 2.0, d / 2.0
    ix, iy = ox - t, oy - t
    outer = [(-ox, -oy), (ox, -oy), (ox, oy), (-ox, oy)]
    inner = [(-ix, -iy), (ix, -iy), (ix, iy), (-ix, iy)]
    vo0 = [bm.verts.new((x, y, z0)) for x, y in outer]
    vo1 = [bm.verts.new((x, y, z1)) for x, y in outer]
    vi0 = [bm.verts.new((x, y, z0)) for x, y in inner]
    vi1 = [bm.verts.new((x, y, z1)) for x, y in inner]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((vo0[i], vo0[j], vo1[j], vo1[i]))       # outer wall
        bm.faces.new((vi0[j], vi0[i], vi1[i], vi1[j]))       # inner wall, facing in
        bm.faces.new((vo1[i], vo1[j], vi1[j], vi1[i]))       # top
        bm.faces.new((vo0[j], vo0[i], vi0[i], vi0[j]))       # bottom
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    state = (plan.get("module") or {}).get("state") or "open"
    if state not in STATES:
        state = "open"
    z0 = -h / 2.0
    objs, cboxes = [], []

    def part(bm, name, texel=1.5, wear_amount=None):
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel, texel=texel,
                                    rng=rng, wear=wear if wear_amount is None else wear_amount)
        objs.append(obj)
        return obj

    # THE CURB: one ring, outer faces on the slot's edges, the opening between them. Built as
    # one mesh of shared vertices -- 16 verts, 16 quads -- rather than four boxes, because four
    # boxes meeting at the corners put the end walls' outer faces on the long walls' end faces,
    # the same plane facing the same way: the census read 8 coincident pairs a corner that way
    # (`tests/test_coincident_faces.py`). A ring has no two faces on one plane.
    bm = geometry.new_bm()
    _ring(bm, w, d, CURB_T, z0, h / 2.0)
    curb = part(bm, "RoofHatch_Curb")
    cboxes.append(((-w / 2.0, -d / 2.0, z0), (w / 2.0, -d / 2.0 + CURB_T, h / 2.0)))
    cboxes.append(((-w / 2.0, d / 2.0 - CURB_T, z0), (w / 2.0, d / 2.0, h / 2.0)))
    cboxes.append(((-w / 2.0, -d / 2.0, z0), (-w / 2.0 + CURB_T, d / 2.0, h / 2.0)))
    cboxes.append(((w / 2.0 - CURB_T, -d / 2.0, z0), (w / 2.0, d / 2.0, h / 2.0)))

    # THE LID: a plate across the curb's top, resting on it -- sunk SKIRT into it, the way a Zoo
    # floater rests (core.floaters) -- hinged along a line HINGE_IN inside the back wall's outer
    # face, its edges LIP inside the curb's outer planes. So no face of it lies on a plane of the
    # curb, closed or standing, and standing it stays inside the curb's footprint, which is what
    # Deli Counter's placement gate measures. Closed, it stands LID_T above the slot: art above
    # the curb, which is the fit.
    lid_w = w - 2 * LIP
    y_back, y_front = -d / 2.0 + HINGE_IN, d / 2.0 - LIP
    lid_d = y_front - y_back
    lid_z = h / 2.0 - SKIRT + LID_T / 2.0                     # the plate's centre, closed
    hinge = (0.0, y_back, h / 2.0 - SKIRT)                   # the hinge line, along local X
    bm = geometry.new_bm()
    verts = geometry.add_box(bm, (0.0, (y_back + y_front) / 2.0, lid_z), (lid_w, lid_d, LID_T))
    if state == "open":
        # swing the plate about the hinge line by OPEN_DEG: its far (+Y) edge rises until the
        # plate stands on the hinge, its thickness over the back wall, clear of the opening
        ang = math.radians(OPEN_DEG)
        c, s = math.cos(ang), math.sin(ang)
        for v in verts:
            y, z = v.co.y - hinge[1], v.co.z - hinge[2]
            v.co.y = hinge[1] + y * c - z * s
            v.co.z = hinge[2] + y * s + z * c
        # the box the standing plate occupies, read before `part` frees the bmesh
        ys = [v.co.y for v in verts]
        zs = [v.co.z for v in verts]
        lid_box = ((-lid_w / 2.0, min(ys), min(zs)), (lid_w / 2.0, max(ys), max(zs)))
    else:
        lid_box = ((-lid_w / 2.0, y_back, lid_z - LID_T / 2.0),
                   (lid_w / 2.0, y_front, lid_z + LID_T / 2.0))
    lid = part(bm, "RoofHatch_Lid")
    cboxes.append(lid_box)

    # THE HINGE: a rod along the back top edge, bare metal.
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, hinge[1], hinge[2]), HINGE_R, lid_w * 0.9, segments=10, axis="X")
    rod = part(bm, "RoofHatch_Hinge", texel=2.0, wear_amount=0.05)

    # THE FLOOR FORM (1.114.0): the same hatch let into a floor over a drop, its frame Deli
    # Counter's 3 cm, painted safety yellow so the opening reads from across a room; the lid keeps
    # the style's grey. One material either way: in the floor form it is white and each part's
    # colour rides in `Wear` (`geometry.tint_wear`), the draw-call rule for colour-only variation.
    floor = (plan.get("params") or {}).get("form") == "floor"
    if floor:
        geometry.tint_wear(curb, SAFETY_YELLOW)
        geometry.tint_wear(lid, plan["color"])
        paint = materials.make_material(
            f"M_RoofHatch_{plan['material']}_floor", [1.0, 1.0, 1.0], plan["material"])
    else:
        paint = materials.make_material(
            f"M_RoofHatch_{plan['material']}", plan["color"], plan["material"])
    dark = materials.make_material("M_RoofHatch_hinge", [0.16, 0.16, 0.17], "metal_bare")
    materials.assign([curb, lid], paint)
    materials.assign([rod], dark)

    return {"objects": objs, "collision_boxes": cboxes, "fit_objects": [curb],
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
