"""What a chain-link fence run is, in numbers: ONE place, no bpy.

The walker, 2026-10-04, on the fenced vacant lot in
`docs/findings/backdrop_mock/` at the factory root: "I like the idea of a
fence between playable areas and non playable areas, thats good feedback to
the player". The fabric is Pixelcoat's `chain_link` kind (0.56.0): a 1 m
alpha-cut tile of 16 diamonds. This module says where the steel stands.

REFERENCE: the common US commercial fence (ASTM F1043 framework, F668 /
F392 fabric), in the sizes a 1990s Delaware County lot would have been
fenced with:

  * LINE POSTS no more than 10 ft (3.05 m) apart, 1-7/8 in (47.6 mm) OD;
  * TERMINAL POSTS at each end of a run, 2-3/8 in (60.3 mm) OD;
  * a TOP RAIL, 1-5/8 in (41.3 mm) OD, through the line posts' loop caps and
    into the terminals' rail-end cups;
  * the FABRIC hung about 2 in (51 mm) above grade, tied to the top rail,
    with a TENSION WIRE along its bottom edge;
  * 6 ft (1.83 m) fabric is the commercial default.

Drawn at real size except the tension wire: at 4.5 mm it would be under a
pixel at any distance a player reads it from, so it is drawn at twice that,
as the antenna's tubes are, "as the gutter's sheet is" (Zoo 1.74.0).

THE EXTENTS ARE EXACT. A terminal post's outer face is the run's end and its
top is the run's top, so the module's bounds are (width, TERMINAL_OD,
height) and Lot's slot is exactly what stands.
"""
from __future__ import annotations

import math

MAX_SPAN = 3.05            # m, line post to line post (10 ft)
LINE_OD = 0.0476           # m, 1-7/8 in
TERMINAL_OD = 0.0603       # m, 2-3/8 in
RAIL_OD = 0.0413           # m, 1-5/8 in
GROUND_GAP = 0.051         # m, fabric above grade (2 in)
WIRE_OD = 0.009            # m, a 4.5 mm tension wire drawn at twice size
FABRIC_T = 0.004           # m, the fabric card's thickness
POST_SIDES = 8             # a 5 cm tube needs no more
WIRE_SIDES = 6


def posts(width):
    """``[(x, od), ...]`` along a run of ``width`` centred on 0: a terminal
    post at each end with its outer face on the run's end, and line posts
    evenly between them, no span longer than `MAX_SPAN`."""
    width = float(width)
    if width < 2.0 * TERMINAL_OD:
        raise ValueError(f"a run of {width} m cannot stand two terminal posts")
    x0 = -width / 2.0 + TERMINAL_OD / 2.0
    x1 = width / 2.0 - TERMINAL_OD / 2.0
    spans = max(1, math.ceil((x1 - x0) / MAX_SPAN - 1e-9))
    out = []
    for i in range(spans + 1):
        x = x0 + (x1 - x0) * i / spans
        out.append((round(x, 6), TERMINAL_OD if i in (0, spans) else LINE_OD))
    return out


def rail_z(height):
    """The top rail's centre, in the module frame (centre pivot, so the
    ground is ``-height/2``): its top flush with the terminals' tops."""
    return height / 2.0 - RAIL_OD / 2.0


def fabric_z(height):
    """``(bottom, top)`` of the fabric card in the module frame: from the
    ground gap up to the top rail's centre, where it is tied."""
    return -height / 2.0 + GROUND_GAP, rail_z(height)


def fabric_y():
    """The fabric hangs on one face of the line posts, as it is stretched
    on a real fence; the module's depth is the terminal post's, so it stays
    inside the slot."""
    return LINE_OD / 2.0 + FABRIC_T / 2.0


def wire_z(height):
    """The tension wire's centre: ON the fabric's bottom edge, woven through
    its knuckles as a real one is. MEASURED by `tools/coplanar_census.py`:
    with the wire resting on the edge instead (centre half its OD above it),
    its flat underside hung 0.6 mm over the card's for the run's whole
    length -- 357 cm2 of near-coincident faces at the default 9 m."""
    return fabric_z(height)[0]


def wire_length(width):
    """Terminal centre to centre and a quarter of a terminal into each: the
    wire's end caps stand inside the posts, never flush with the fabric's
    ends (the census's other two pairs, 0.3 cm2 each)."""
    return width - TERMINAL_OD + TERMINAL_OD / 2.0
