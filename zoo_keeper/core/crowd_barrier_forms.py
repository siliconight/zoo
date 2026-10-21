"""What a steel crowd-control barricade is, in numbers: ONE place, no bpy.

Factory roadmap 267, the walker's look review of 2026-10-20: arena_a02's four barriers -- Deli Counter volumes of
3.0 x 0.8 x 1.2 m that built as plain boxes -- are to be "Crowd rails (a new model)", not the concrete jersey barrier.
This draws one panel of the interlocking barricade crowds are lined up behind at an arena's gates and a parade's kerb:
a welded tube frame on two flat feet, vertical pickets between its rails, hooks at one end that drop over the next
panel's leg.

REFERENCE, the common sizes as fabricators list them (not a standard's; no code governs a barricade's dimensions):
a panel about 7.5 ft long and 43 in tall on flat steel feet about 24 in long; a frame of 1-1/2 in tube with 1-1/4 in
rails, 3/4 in tube pickets, about fourteen to a 7.5 ft panel, the bottom rail about 8 in off the ground; hot-dip
galvanised. The genome's defaults are those sizes and its ranges hold arena_a02's slot.
  * `LEG_R`, `RAIL_R`, `PICKET_R`: the tubes' radii, 1-1/2, 1-1/4 and 3/4 in across;
  * `PICKET_CLEAR`: the clear between pickets, 5-1/4 in -- the clear of fourteen pickets in a 7.5 ft frame;
  * `BOTTOM_Z`: the bottom rail's centre 8 in over the floor;
  * `FOOT_W`, `FOOT_T`: 2 in flat bar, drawn 3/8 in thick where the steel is 1/4, so it holds a pixel a few metres out
    (as the stoop railing's pickets and the fence's tension wire are drawn heavier than they are);
  * `HOOK_R`, `HOOK_CLEAR`, `HOOK_DROP`: 5/8 in rod bent out and down, its opening just over a leg's width, so it
    could drop over the next panel's leg.

THE FRAME is the module's own: X along the panel, the hooks at +X; Y across, the feet's length; Z up. Centre pivot, and
the extents are exactly the slot's (w, d, h): the -X foot's outer edge and the hooks' outer face are the box's ends,
the feet are its depth, the feet's undersides its bottom and the legs' capped tops its top.

EVERY TUBE HAS EIGHT SIDES. Zoo's export keeps a fold under 50 degrees smooth (`geometry.SMOOTH_ANGLE_DEG`): eight
sides fold at 45 and read round; six fold at 60 and read as hexagonal bar.

NO FACE OF ONE PART LIES ON ANOTHER'S, so `prims.coincident_pairs` reads none before Blender does. The pickets turn by
`PICKET_PHASE` and the hooks' arms by `HOOK_PHASE`, so no picket's facet is parallel to a leg's and no arm's to a
rail's; a box's faces are axis-aligned and no tube's facet is. A TUBE END HIDDEN INSIDE ANOTHER MEMBER IS LEFT OPEN,
and every such end is narrower than the member's inscribed radius (an eight-sided ring's flats are cos 22.5 = 0.924 of
its corners), so no opening shows: a leg's foot inside its foot plate, a rail's ends inside the legs, a picket's ends on
the rails' centre lines, a hook's arm inside its leg and its drop. What shows is closed: the legs' tops are capped,
`LEG_PROUD` over the top rail, and each hook's drop is capped at both ends.

COLLISION: the panel -- the frame's thickness, leg to leg, floor to top. The feet stay out of it: a 3/8 in plate is
under any step. Deli Counter writes its volume's own collider in the greybox the graders walk (arena_a02's is the
convex 3.0 x 0.8 x 1.2 box the barriers always were); this one is the module's, for a panel standing anywhere else.
"""
from __future__ import annotations

import math

from . import prims

IN = 0.0254
LEG_R = round(0.75 * IN, 5)           # 1-1/2 in tube
RAIL_R = round(0.625 * IN, 5)         # 1-1/4 in tube
PICKET_R = round(0.375 * IN, 5)       # 3/4 in tube
PICKET_CLEAR = round(5.25 * IN, 5)    # fourteen pickets to a 7.5 ft panel
BOTTOM_Z = round(8 * IN, 4)           # the bottom rail's centre over the floor
FOOT_W = round(2 * IN, 4)             # flat bar across X
FOOT_T = round(0.375 * IN, 4)         # its thickness, drawn heavier than the 1/4 in steel
HOOK_R = round(0.3125 * IN, 5)        # 5/8 in rod: the drop
ARM_R = round(HOOK_R * 0.9, 5)        # the arm, narrower than the drop's flats so its end hides in it
HOOK_CLEAR = round(1.75 * IN, 4)      # the opening between the leg and the drop: over a 1-1/2 in leg
HOOK_DROP = round(1.5 * IN, 4)        # how far the drop hangs below the arm
#: the hooks' arms over the bottom rail and under the top rail
HOOK_INSET = 0.08
#: a leg's capped top over the top rail's, so the two are never one plane
LEG_PROUD = 0.01
#: a leg's open foot inside its foot plate
SINK = 0.004
SIDES = 8
PICKET_PHASE = math.pi / 16
HOOK_PHASE = math.pi / 16
#: inscribed / circumscribed radius of an eight-sided ring
FLAT = math.cos(math.pi / SIDES)
MAT = "steel"
PART = "CrowdBarrier_Steel"


def _open(p, keep=()):
    """``p`` with its two end caps (faces 0 and 1 of `prims.cyl` and `prims.rod`) dropped, but those in ``keep``."""
    q = dict(p)
    q["faces"] = [f for i, f in enumerate(p["faces"]) if i >= 2 or i in keep]
    return q


def frame_x(w):
    """``(x_lo_leg, x_hi_leg, x_drop)`` -- the two legs' centres and the hooks' drops' -- for a panel ``w`` long.

    The -X foot's outer edge is -w/2; the hooks' drops' outer faces are +w/2, `HOOK_CLEAR` clear of the +X leg."""
    x_lo = -w / 2.0 + FOOT_W / 2.0
    x_drop = w / 2.0 - HOOK_R
    x_hi = x_drop - HOOK_R - HOOK_CLEAR - LEG_R
    return x_lo, x_hi, x_drop


def picket_xs(x0, x1):
    """Picket centres between the legs' inner faces ``x0`` and ``x1``: as few as keep every clear gap at most
    `PICKET_CLEAR`, the gaps equal."""
    width = 2 * PICKET_R
    span = x1 - x0
    n = max(0, math.ceil((span - PICKET_CLEAR) / (width + PICKET_CLEAR) - 1e-9))
    if n == 0:
        return []
    gap = (span - n * width) / (n + 1)
    return [x0 + gap * (i + 1) + width * (i + 0.5) for i in range(n)]


def plan(w, d, h):
    """The barricade for a slot of ``w`` x ``d`` x ``h`` (X along the panel, the hooks at +X): ``{prims, collision,
    facts}``."""
    w, d, h = float(w), float(d), float(h)
    z0, z1 = -h / 2.0, h / 2.0
    x_lo, x_hi, x_drop = frame_x(w)
    z_top = z1 - LEG_PROUD - RAIL_R           # the top rail's centre
    z_bot = z0 + BOTTOM_Z                     # the bottom rail's centre
    # the frame stands, and its two hooks hang one above the other between its rails
    if x_hi - LEG_R <= x_lo + LEG_R or z_top - HOOK_INSET - HOOK_DROP <= z_bot + HOOK_INSET + HOOK_R:
        raise ValueError("a crowd barrier %.3f x %.3f x %.3f m cannot hold its frame" % (w, d, h))
    if d < 2 * LEG_R:
        raise ValueError("a crowd barrier %.4f m deep cannot stand its legs on its feet" % d)
    out = []
    # the two flat feet, the panel's depth long, under the legs
    for x in (x_lo, x_hi):
        out.append(prims.box(PART, MAT, (x - FOOT_W / 2, -d / 2, z0), (x + FOOT_W / 2, d / 2, z0 + FOOT_T)))
    # the legs: open at the foot (inside the plate), capped at the top
    for x in (x_lo, x_hi):
        out.append(_open(prims.cyl(PART, MAT, (x, 0.0), LEG_R, z0 + FOOT_T - SINK, z1, segments=SIDES), keep=(1,)))
    # the rails, leg centre to leg centre, both ends inside the legs
    for z in (z_bot, z_top):
        out.append(_open(prims.rod(PART, MAT, (x_lo, 0.0, z), (x_hi, 0.0, z), RAIL_R, segments=SIDES)))
    # the pickets, rail centre to rail centre
    xs = picket_xs(x_lo + LEG_R, x_hi - LEG_R)
    for x in xs:
        out.append(_open(prims.cyl(PART, MAT, (x, 0.0), PICKET_R, z_bot, z_top, segments=SIDES,
                                   phase=PICKET_PHASE)))
    # the hooks: an arm out of the +X leg into a drop that hangs below it
    for z in (z_bot + HOOK_INSET, z_top - HOOK_INSET):
        out.append(_open(prims.rod(PART, MAT, (x_hi, 0.0, z), (x_drop, 0.0, z), ARM_R, segments=SIDES,
                                   phase=HOOK_PHASE)))
        out.append(prims.cyl(PART, MAT, (x_drop, 0.0), HOOK_R, z - HOOK_DROP, z + HOOK_R, segments=SIDES))
    boxes = [((x_lo - LEG_R, -LEG_R, z0), (x_hi + LEG_R, LEG_R, z1))]
    out, boxes = prims.fit_exact(out, (-w / 2, -d / 2, z0), (w / 2, d / 2, z1), boxes)
    facts = {"tris": prims.tri_count(out), "pickets": len(xs), "legs_x": [round(x_lo, 6), round(x_hi, 6)],
             "rails_z": [round(z_bot, 6), round(z_top, 6)]}
    return {"prims": out, "collision": boxes, "facts": facts}
