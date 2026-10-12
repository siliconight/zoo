"""What a wooden utility pole is, in numbers: ONE place, no bpy (roadmap 240).

The walker's three Philly photographs (`docs/reference/PHILLY_STREET_COMPS.md`
at the factory root, 2026-10-11): in two of them the overhead network is the
strongest line in the frame -- a wooden pole at the corner carrying a
cobra-head on a long arm, cobra-heads on poles at the kerb of the rowhouse
street, wires overhead. The factory stood none of it: every lamp its own
steel pole and not one wire. This module says what the pole is; Lot says
where poles stand and draws the wires between them, and it mirrors the
numbers it needs from here (`MODULE_DIMS`, `POLE_AT`, `LENS_AT`, `WIRES`),
because neither repo can import the other.

THE WALKER'S CALLS, 2026-10-12 (`docs/proposals/POLE_LINE_DESIGN.md`): one
side of every street; the full wire set, no house drops; a transformer can
every third or fourth pole; a cobra-head on EVERY pole. So the lamp is not a
form -- every pole carries one -- and the forms are the can or none:

  auto          the pole, its crossarm and three primaries' insulators, the
                neutral and secondary spools, the cable bolts, the cobra-head
                on its arm, the number tag
  transformer   all of that and a pole-top transformer can under the neutral

No street-name blade: Lot cannot post one (`site_furniture.BLADE_AT_JUNCTION`
says why -- no spec names a road), so there is nothing to letter it with.

REFERENCE, US distribution practice, the figures filling blanks the photos
leave (the comps and the walker decide; these do not):

  * a 40 ft wood pole set about 6 ft deep stands about 10.4 m; 0.30 m across
    at grade and 0.19 m at the top (ANSI O5.1 class 4 circumferences);
  * an 8 ft (2.44 m) crossarm, 3-1/2 x 4-1/2 in, a foot under the top, with
    steel braces down to the pole; three pin insulators for the primaries;
  * the neutral a metre or so under the crossarm, the secondary under the
    transformer, the communication cables lowest, everything clearing a road
    at mid-span (NESC: about 4.7 m for communication, more for supply);
  * a cobra-head about 25 ft up on a 6 ft (1.83 m) mast arm, the lens under
    its head, facing the road;
  * a pole-mount transformer about 0.46 m across and 0.86 m tall.

THE FRAME. Metres, Z up from grade, X along the street (the module's width),
-Y toward the road (its front). The pole's axis is NOT the module's centre:
the cobra-head reaches 2.4 m toward the road and the crossarm 1.22 m the
other way, and `fit_exact` maps the drawing's bounds onto the slot's. So
the drawing is laid out about the pole and `POLE_AT` says where the pole
stands in the module (from its centre, at grade) -- Lot puts the slot's
centre there, not on the pole.

Every part a pole carries merges into four materials -- wood, steel, the
insulators' porcelain and the lit lens (`MATERIALS`) -- so a pole draws four
times whatever it carries, and collision is the pole alone: a body walks
under an arm.
"""
from __future__ import annotations

import math

from . import prims as P

#: how far a part set against another is sunk into it: deeper than the
#: coincident-face tolerance (2 mm) so no face pair is left within it
SINK = 0.01

FORMS = ("auto", "transformer")

POLE_H = 10.4              # m above grade: a 40 ft pole set ~6 ft deep
POLE_D_BASE = 0.30         # m across at grade
POLE_D_TOP = 0.19          # m across at the top
POLE_SIDES = 10

ARM_L = 2.44               # m, an 8 ft crossarm, along Y
ARM_W = 0.089              # m, 3-1/2 in (X)
ARM_H = 0.114              # m, 4-1/2 in (Z)
ARM_Z = POLE_H - 0.35      # m, the crossarm's centreline
BRACE_Y = 0.70             # m, where a brace meets the crossarm, each side
BRACE_DROP = 0.60          # m, where it meets the pole, under the crossarm

#: the primaries' pin insulators along the crossarm (Y): two to the road's
#: side of the pole, one to the field's, none on the pole's own line
INSULATOR_Y = (-1.07, -0.41, 1.07)
PIN_H = 0.05               # m of steel pin above the crossarm
INSULATOR_R = (0.058, 0.046)   # m, the skirt and the crown
INSULATOR_H = 0.14         # m, the porcelain's height

NEUTRAL_Z = POLE_H - 1.10      # m, the neutral's spool
SECONDARY_Z = 7.95             # m, the secondary's spool
COMM_Z = (6.40, 6.00)          # m, two communication cables
SPOOL_R = 0.045
SPOOL_H = 0.09
BACK_Y = 0.24                  # m, a spool or bolt's reach from the axis (+Y)

LAMP_MOUNT_Z = 7.20        # m, where the cobra-head's arm leaves the pole
LAMP_ARM_L = 1.83          # m, a 6 ft mast arm
LAMP_RISE = 0.30           # m the arm climbs to the head
LAMP_ARM_D = 0.06          # m, the arm's tube
HEAD_L = 0.62              # m, the cobra-head housing, along -Y
HEAD_W = 0.30              # m (X)
HEAD_H = 0.15              # m (Z)
LENS_L = 0.40              # m, the lens under the head
LENS_W = 0.22
LENS_T = 0.02
LENS_GAP = 0.004           # m between the lens's top and the head's underside

CAN_R = 0.23               # m, a pole-mount transformer
CAN_H = 0.86
CAN_TOP_Z = NEUTRAL_Z - 0.18
CAN_Y = POLE_D_TOP / 2.0 + 0.06 + CAN_R    # its axis, behind the pole (+Y)
BUSHING_R = 0.035
BUSHING_H = 0.10

TAG_Z = 1.80               # m, the pole's number plate
TAG_W, TAG_H, TAG_T = 0.10, 0.05, 0.004

#: (name, colour, kind): the four materials a pole draws with. The wood is
#: creosote brown, the steel galvanised, the porcelain the brown glaze a
#: 1990s Delaware County line carried; the lens is the streetlight's sodium.
MATERIALS = {
    "wood": ([0.24, 0.17, 0.11], "wood"),
    "steel": ([0.55, 0.56, 0.55], "metal_bare"),
    "porcelain": ([0.42, 0.25, 0.14], "plastic"),
}
LENS_COLOUR = [1.0, 0.62, 0.24]
LENS_STRENGTH = 2.5


def _r(z):
    """The pole's radius at height ``z`` (a straight taper), to its corners."""
    t = min(max(z / POLE_H, 0.0), 1.0)
    return (POLE_D_BASE + (POLE_D_TOP - POLE_D_BASE) * t) / 2.0


def _face(z):
    """The pole's radius to a FACE at height ``z``: a part set against the
    pole is sunk from here, never from the corner radius, which would leave
    it hovering in front of a flat face (`prims.coincident_pairs` and the
    floater rule: a part either rests in what it joins or stands clear)."""
    return _r(z) * math.cos(math.pi / POLE_SIDES)


def lamp_head_y():
    """The cobra-head's near end (Y): the arm's tip, toward the road."""
    return -LAMP_ARM_L


def lens_point():
    """``(y, z)`` of the lens underside's centre, about the pole's axis at
    grade: where the light hangs (Lux's streetlight rig mounts at it)."""
    head_z = LAMP_MOUNT_Z + LAMP_RISE
    y = lamp_head_y() - HEAD_L * 0.55
    z = head_z - HEAD_H / 2.0 - LENS_GAP - LENS_T
    return (round(y, 6), round(z, 6))


def _draw(form):
    """The prims of one pole, laid out about its axis at (0, 0, 0). Every
    part that meets another is sunk `SINK` into it, so no two faces of the
    pole are left within the coincident-face tolerance."""
    out = []
    # the pole, and its number tag sunk into the pole's road-side face
    out.append(P.cyl("UtilityPole_Pole", "wood", (0.0, 0.0), POLE_D_BASE / 2.0,
                     0.0, POLE_H, segments=POLE_SIDES, r_top=POLE_D_TOP / 2.0))
    out.append(P.box("UtilityPole_Pole", "steel",
                     (-TAG_W / 2.0, -_face(TAG_Z) - TAG_T, TAG_Z - TAG_H / 2.0),
                     (TAG_W / 2.0, -_face(TAG_Z) + SINK, TAG_Z + TAG_H / 2.0)))
    # the crossarm, across the line (Y), and its two steel braces, each end
    # sunk in the pole and in the crossarm's underside
    out.append(P.box("UtilityPole_Pole", "wood",
                     (-ARM_W / 2.0, -ARM_L / 2.0, ARM_Z - ARM_H / 2.0),
                     (ARM_W / 2.0, ARM_L / 2.0, ARM_Z + ARM_H / 2.0)))
    for side in (-1.0, 1.0):
        zb = ARM_Z - BRACE_DROP
        out.append(P.rod("UtilityPole_Pole", "steel",
                         (0.0, side * (_face(zb) - SINK), zb),
                         (0.0, side * BRACE_Y, ARM_Z - ARM_H / 2.0 + SINK),
                         0.012, segments=4))
    # the primaries' pins, each poking into its insulator, and the insulators:
    # a skirt and a crown, the crown sunk into the skirt's top
    top = ARM_Z + ARM_H / 2.0
    skirt_top = top + PIN_H + INSULATOR_H * 0.45
    for y in INSULATOR_Y:
        out.append(P.cyl("UtilityPole_Pole", "steel", (0.0, y), 0.012,
                         top - 2.0 * SINK, top + PIN_H + SINK, segments=6))
        out.append(P.cyl("UtilityPole_Pole", "porcelain", (0.0, y),
                         INSULATOR_R[0], top + PIN_H, skirt_top,
                         segments=8, r_top=INSULATOR_R[1]))
        out.append(P.cyl("UtilityPole_Pole", "porcelain", (0.0, y),
                         INSULATOR_R[1] * 0.92, skirt_top - SINK,
                         top + PIN_H + INSULATOR_H, segments=8,
                         r_top=INSULATOR_R[1] * 0.6))
    # the neutral's and the secondary's spools, each resting in its bracket,
    # behind the pole (+Y)
    for z in (NEUTRAL_Z, SECONDARY_Z):
        z0 = z - SPOOL_H / 2.0
        out.append(P.box("UtilityPole_Pole", "steel",
                         (-0.03, _face(z) - 2.0 * SINK, z0 - 0.012),
                         (0.03, BACK_Y + SPOOL_R, z0)))
        out.append(P.cyl("UtilityPole_Pole", "porcelain", (0.0, BACK_Y), SPOOL_R,
                         z0 - SINK * 0.5, z + SPOOL_H / 2.0, segments=8))
    # the communication cables' bolts, through the pole
    for z in COMM_Z:
        out.append(P.rod("UtilityPole_Pole", "steel", (0.0, _face(z) - 2.0 * SINK, z),
                         (0.0, BACK_Y, z), 0.011, segments=6))
    # the cobra-head: its bracket sunk in the pole's road side, its arm
    # climbing from inside the bracket into the head, and the lens hung under
    # the head with a gap the floater rule calls hovering (>= 3 mm)
    head_z = LAMP_MOUNT_Z + LAMP_RISE
    fm = _face(LAMP_MOUNT_Z)
    out.append(P.box("UtilityPole_Pole", "steel",
                     (-0.05, -fm - 0.03, LAMP_MOUNT_Z - 0.12),
                     (0.05, -fm + 2.0 * SINK, LAMP_MOUNT_Z + 0.08)))
    out.append(P.rod("UtilityPole_Pole", "steel",
                     (0.0, -fm - 0.01, LAMP_MOUNT_Z),
                     (0.0, lamp_head_y() - 0.04, head_z), LAMP_ARM_D / 2.0, segments=8))
    out.append(P.box("UtilityPole_Pole", "steel",
                     (-HEAD_W / 2.0, lamp_head_y() - HEAD_L, head_z - HEAD_H / 2.0),
                     (HEAD_W / 2.0, lamp_head_y(), head_z + HEAD_H / 2.0)))
    ly, lz = lens_point()
    out.append(P.box("UtilityPole_Lens", "lens",
                     (-LENS_W / 2.0, ly - LENS_L / 2.0, lz),
                     (LENS_W / 2.0, ly + LENS_L / 2.0, lz + LENS_T)))
    if form == "transformer":
        # the can on its bracket behind the pole, its two bushings sunk in
        # its lid
        out.append(P.box("UtilityPole_Pole", "steel",
                         (-0.05, _face(CAN_TOP_Z) - 2.0 * SINK, CAN_TOP_Z - CAN_H * 0.7),
                         (0.05, CAN_Y - CAN_R + SINK, CAN_TOP_Z - CAN_H * 0.2)))
        out.append(P.cyl("UtilityPole_Pole", "steel", (0.0, CAN_Y), CAN_R,
                         CAN_TOP_Z - CAN_H, CAN_TOP_Z, segments=12))
        for dx in (-0.09, 0.09):
            out.append(P.cyl("UtilityPole_Pole", "porcelain", (dx, CAN_Y - 0.06),
                             BUSHING_R, CAN_TOP_Z - SINK, CAN_TOP_Z + BUSHING_H,
                             segments=6, r_top=BUSHING_R * 0.7))
    return out


def pick_form(form):
    """`auto` for a pole asked for nothing, the form for one that names one
    this species builds; anything else is a mistake and says so."""
    if form in (None, "", "auto"):
        return "auto"
    if form not in FORMS:
        raise ValueError(f"utility_pole has no form {form!r}: {FORMS}")
    return form


def _extents(form):
    lo, hi = P.bounds(_draw(form))
    return lo, hi


def module_dims(form):
    """(width, depth, height) of the module for ``form``: the drawing's own
    bounds, rounded to the millimetre Lot writes."""
    lo, hi = _extents(pick_form(form))
    return tuple(round(hi[a] - lo[a], 4) for a in range(3))


def pole_at(form):
    """Where the pole's axis stands in the module, ``(x, y)`` from its
    centre at grade, in the module frame (-Y toward the road)."""
    lo, hi = _extents(pick_form(form))
    # `+ 0.0` turns a rounded -0.0 into the 0.0 a mirror writes
    return (round(-(lo[0] + hi[0]) / 2.0, 4) + 0.0,
            round(-(lo[1] + hi[1]) / 2.0, 4) + 0.0)


#: THE NUMBERS LOT MIRRORS (`site_furniture.POLE_DIMS` and its neighbours),
#: pinned to literals by `test_the_numbers_lot_mirrors_are_these` so a
#: change here fails a test before it moves a level.
MODULE_DIMS = {f: module_dims(f) for f in FORMS}
POLE_AT = {f: pole_at(f) for f in FORMS}
LENS_AT = lens_point()


def wires():
    """Every wire's attachment on the pole, ``{name: (y, z)}`` about the
    axis at grade (X is along the line, so a span runs along X): the three
    primaries on their insulators' crowns, the neutral and secondary on
    their spools, the two communication cables on their bolts."""
    top = ARM_Z + ARM_H / 2.0 + PIN_H + INSULATOR_H
    out = {f"primary_{i}": (y, round(top, 4)) for i, y in enumerate(INSULATOR_Y)}
    out["neutral"] = (BACK_Y, NEUTRAL_Z)
    out["secondary"] = (BACK_Y, SECONDARY_Z)
    for i, z in enumerate(COMM_Z):
        out[f"comm_{i}"] = (BACK_Y, z)
    return out


WIRES = wires()


def plan(w, d, h, form=None):
    """The pole for ``form``, laid out about its axis and fitted to the slot
    exactly. Returns ``{prims, collision, form, overshoot_m, facts}``; the
    collision is the pole's own column, which a body walks into and nothing
    else on the module is."""
    built = pick_form(form)
    prims = _draw(built)
    lo, hi = P.bounds(prims)
    cx, cy = (lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0
    prims = [P.translate(p, (-cx, -cy, 0.0)) for p in prims]
    r = POLE_D_BASE / 2.0
    boxes = [((-r - cx, -r - cy, 0.0), (r - cx, r - cy, POLE_H))]
    dims = module_dims(built)
    overshoot = max(abs(dims[0] - w), abs(dims[1] - d), abs(dims[2] - h))
    prims, boxes = P.fit_exact(prims, (-w / 2.0, -d / 2.0, 0.0),
                               (w / 2.0, d / 2.0, h), boxes)
    return {"prims": prims, "collision": boxes, "form": built,
            "overshoot_m": round(overshoot, 6),
            "facts": {"tris": P.tri_count(prims), "lens_at": LENS_AT,
                      "pole_at": POLE_AT[built]}}
