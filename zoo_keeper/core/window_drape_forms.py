"""Drapes drawn shut across a window: a den's window, hidden (1.91.0).

THE BRIEF. The walker, 2026-10-09, walking club_block_014 (roadmap 219,
note 2): "the windows in any 'den of sin' building should have curtains or
drapes or blinds So people outside can't see in, and you keep the
streetlight light out of the club", with a red drape as the comp. So: two
heavy velvet panels drawn shut across the window under a box pelmet, hung on
the ROOM side of the glass. Oxblood, the club chairs' velvet
(`club_forms.VELVETS`), deep vertical pleats a little fuller at the hem than
under the pelmet, where the rod gathers them. It is seen from the room at
fighting distance and from the street through the glass at night.
- **Excluded:** tie-backs (a den keeps them shut), a visible rod (the pelmet
  hides it), lace, sheers, anything a light shows through. Its job is to
  hide the room and stop the light.
- **Collision: none.** The window's own pane seals the opening.

THE FRAME, as every club piece's (`club_forms`): x along the window, the
front (the room) at -y, z up from the hem at 0 to the pelmet's top at ``h``;
`prims.fit_exact` makes the extents exactly ``w x d x h``.

THE PLEATS ARE GEOMETRY, AND THEIR FACET COUNT IS DERIVED. A pleat is a sine
across x, ``PLEAT_SAMPLES`` facets a pitch. Zoo smooths across an edge whose
faces meet under 50 degrees (`geometry.shade_by_angle`'s default, the one
the modern low-poly standard keeps), so the facet count and the swing are
chosen to keep every edge of a pleat under it: at 12 facets, a 3 cm swing
and a 12 cm pitch, the sharpest turn is at the crest, 43.8 degrees
(`max_facet_turn`, held by the tests). Eight facets turn 60.7 at the crest
and would split it into a ridge.

BOTH SIDES ARE CLOTH. A panel is a closed slab -- its pleated front, the same
sheet ``THICK`` behind it, its hem and its two side edges -- because the
street sees its back through the glass. Its top runs ``TUCK`` up into the
pelmet and is not closed: nothing sees it. The two panels share one phase
and the right one hangs ``STAGGER`` nearer the room, so where they cross at
the middle they are two parallel sheets, never one intersecting the other.
"""
from __future__ import annotations

import math

from . import club_forms as CF
from . import prims as P

#: oxblood, the club chairs' first velvet: the comp's red, darker, as a dim
#: room shows it
VELVET = list(CF.VELVETS[0][0])
#: the box valance across the head, hiding the rod
PELMET_H = 0.16
#: one pleat every 12 cm of hung width
PLEAT_PITCH = 0.12
#: facets a pleat (see the module's notes: 12 keeps every crest smooth)
PLEAT_SAMPLES = 12
#: the pleats' swing at the hem, either side of the panel's line
SWING = 0.03
#: the swing under the pelmet, as a share of the hem's: the rod gathers them
TOP_SWING = 0.6
#: the cloth and its lining
THICK = 0.012
#: the panels cross this far at the middle, so no slit shows the glass
OVERLAP = 0.05
#: the right panel hangs this much nearer the room than the left
STAGGER = 0.02
#: a panel's top runs this far up into the pelmet
TUCK = 0.02
#: a panel's outer edge stands this far inside the pelmet's end
SIDE_IN = 0.01


def _wave(x, amp):
    """The pleat's offset from its panel's line at ``x``, one phase for both
    panels."""
    return amp * math.sin(2.0 * math.pi * x / PLEAT_PITCH)


def max_facet_turn(amp=SWING):
    """The largest angle, in degrees, between two neighbouring facets of a
    pleat swinging ``amp``: the number `shade_by_angle` compares with 50."""
    step = PLEAT_PITCH / PLEAT_SAMPLES
    xs = [k * step for k in range(PLEAT_SAMPLES + 2)]
    angles = [math.atan2(_wave(b, amp) - _wave(a, amp), step) for a, b in zip(xs, xs[1:])]
    return max(abs(math.degrees(b - a)) for a, b in zip(angles, angles[1:]))


def _panel(part, x0, x1, y_line, z_top):
    """One closed pleated slab from ``x0`` to ``x1``, its front swinging about
    ``y_line``, from the hem at 0 to ``z_top``."""
    n = max(2, int(math.ceil((x1 - x0) / (PLEAT_PITCH / PLEAT_SAMPLES))))
    xs = [x0 + (x1 - x0) * k / n for k in range(n + 1)]
    verts = []
    # four rings of n + 1: front hem, front top, back hem, back top
    for z, amp in ((0.0, SWING), (z_top, SWING * TOP_SWING)):
        verts += [(x, y_line + _wave(x, amp), z) for x in xs]
    for z, amp in ((0.0, SWING), (z_top, SWING * TOP_SWING)):
        verts += [(x, y_line + _wave(x, amp) + THICK, z) for x in xs]
    m = n + 1
    fh, ft, bh, bt = 0, m, 2 * m, 3 * m
    faces = []
    for k in range(n):
        faces.append((fh + k, fh + k + 1, ft + k + 1, ft + k))     # the front, to -y
        faces.append((bh + k + 1, bh + k, bt + k, bt + k + 1))     # the back, to +y
        faces.append((fh + k + 1, fh + k, bh + k, bh + k + 1))     # the hem, down
    faces.append((fh, ft, bt, bh))                                  # the -x edge
    faces.append((fh + n, bh + n, bt + n, ft + n))                  # the +x edge
    return P.mesh(part, "velvet", verts, faces)


def plan_drape(w, d, h):
    """Two velvet panels drawn shut under a pelmet, ``w x d x h``, the room at
    -y: ``{"prims", "collision", "velvet_rgb"}``. No collision: the window's
    own pane seals the opening."""
    if h <= PELMET_H + 0.1:
        raise ValueError("window_drape: %.3f m is no taller than its pelmet" % h)
    if d < 2.0 * (SWING + THICK) + STAGGER:
        raise ValueError("window_drape: %.3f m is too shallow for its pleats" % d)
    prims = [P.box("Drape_Pelmet", "velvet", (-w / 2.0, -d / 2.0, h - PELMET_H),
                   (w / 2.0, d / 2.0, h))]
    z_top = h - PELMET_H + TUCK
    # both panels' fronts swing about lines a little behind the middle of the
    # depth, so the deepest pleat of the nearer one stays inside the front
    back_line = STAGGER / 2.0 - THICK / 2.0
    front_line = back_line - STAGGER
    prims.append(_panel("Drape_Panel", -w / 2.0 + SIDE_IN, OVERLAP / 2.0, back_line, z_top))
    prims.append(_panel("Drape_Panel", -OVERLAP / 2.0, w / 2.0 - SIDE_IN, front_line, z_top))
    prims, cboxes = P.fit_exact(prims, (-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h), [])
    return {"prims": prims, "collision": cboxes, "velvet_rgb": VELVET}
