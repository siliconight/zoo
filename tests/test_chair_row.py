"""The chair row: no two faces share a plane, and a wall slot cannot hide the back.

0.81.0. Cold run 9052, `bank_branch_a02` lobby: "z fighting on the [chairs]
on the steel" (the walker). tools/coplanar_probe.py over the walk copy's
placed nodes: each 2.4 m row's four back panels lay SAME-facing, gap 0.00 mm,
on the wall's inner face (1.04 m2 a row), because Deli Counter 0.127.0's
`_wall_slots` stands a piece's back plane 0.03 m inside a 0.30 m wall and the
back panel was 0.03 m thick and flush with that plane. The layout is pure
(`recipes._chair_row`), so these run without Blender; the built GLB was
probed in Blender 5.1 for the release.
"""
from __future__ import annotations

import os
import re

from zoo_keeper.core import genome
from zoo_keeper.recipes import _chair_row as row

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "chair.py")

#: tools/coplanar_probe.py's default window.
PROBE_TOL = 0.002
#: Deli Counter 0.127.0 `level_design._wall_slots`: back plane at centreline
#: + 0.12; `spec_types` wall_thick 0.30, so the inner face is at + 0.15.
DC_0127_BURIAL = 0.15 - 0.12


def _sizes():
    d = genome.load_species("chair")["dimensions"]
    out = [tuple(d[a][k] for a in ("width", "depth", "height"))
           for k in ("min", "default", "max")]
    # the rows cold run 9052 shipped, and the library's waiting_seats shape
    return out + [(2.4, 0.6, 0.9), (0.5, 0.5, 0.9), (0.55, 0.55, 0.9),
                  (5.0, 2.0, 0.6), (2.8, 1.0, 0.9)]


def _layouts():
    bay_max = genome.load_species("chair")["params"]["bay_max"]
    for w, d, h in _sizes():
        for legs in (3, 4):
            for arms in (False, True):
                yield (w, d, h, legs, arms), row.layout(w, d, h, bay_max, legs, arms)


def _boxes(lay):
    out = []
    for name, boxes in lay["parts"]:
        for k, (c, s) in enumerate(boxes):
            lo = tuple(c[i] - s[i] / 2.0 for i in range(3))
            hi = tuple(c[i] + s[i] / 2.0 for i in range(3))
            out.append((f"{name}#{k}", lo, hi))
    return out


def _faces(box):
    """(axis, sign, plane, lo, hi) for the six faces of an AABB."""
    name, lo, hi = box
    for ax in range(3):
        yield ax, -1, lo[ax], lo, hi
        yield ax, +1, hi[ax], lo, hi


def _overlap(ax, alo, ahi, blo, bhi):
    area = 1.0
    for q in range(3):
        if q == ax:
            continue
        e = min(ahi[q], bhi[q]) - max(alo[q], blo[q])
        if e <= 1e-9:
            return 0.0
        area *= e
    return area


def test_no_two_faces_of_a_row_share_a_plane():
    """SAME or OPP, inside the probe's window, with any overlapping area."""
    for key, lay in _layouts():
        boxes = _boxes(lay)
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                for ax, sa, pa, alo, ahi in _faces(boxes[i]):
                    for bx, sb, pb, blo, bhi in _faces(boxes[j]):
                        if ax != bx or abs(pa - pb) > PROBE_TOL:
                            continue
                        area = _overlap(ax, alo, ahi, blo, bhi)
                        assert area < 1e-6, (key, boxes[i][0], boxes[j][0],
                                             ax, sa, sb, round(pa, 4), area)


def test_the_extents_are_the_slot():
    """`build_module` re-centres on the visual bounds; an inset that moved
    them would be halved and pushed onto the front. Without arms: an arm
    rail stands at seat + 0.22 m, above a 0.5 m chair's top, and did so
    before this release too (not this change)."""
    for (w, d, h, _l, arms), lay in _layouts():
        if arms:
            continue
        boxes = _boxes(lay)
        lo = [min(b[1][q] for b in boxes) for q in range(3)]
        hi = [max(b[2][q] for b in boxes) for q in range(3)]
        assert abs(lo[0] + w / 2) < 1e-9 and abs(hi[0] - w / 2) < 1e-9, (w, lo, hi)
        assert abs(lo[1] + d / 2) < 1e-9 and abs(hi[1] - d / 2) < 1e-9, (d, lo, hi)
        assert abs(lo[2]) < 1e-9 and abs(hi[2] - h) < 1e-9, (h, lo, hi)


def _room_facing(lay):
    """Every face that looks into the room (normal -y) with visible area."""
    for name, lo, hi in _boxes(lay):
        area = (hi[0] - lo[0]) * (hi[2] - lo[2])
        yield name, lo[1], area


def test_a_wall_slot_does_not_put_the_wall_face_on_a_chair_face():
    """The wall's inner face looks into the room too, so a room-facing chair
    face on its plane is the SAME-facing pair the walker saw. Checked at the
    flush placement a slot should give and at the 0.03 m burial Deli Counter
    0.127.0 gives -- the second is a record of today's defect, not a promise
    about every burial (Deli Counter's to fix)."""
    for (w, d, h, _l, _a), lay in _layouts():
        for burial in (0.0, DC_0127_BURIAL):
            wall = d / 2.0 - burial
            for name, y, area in _room_facing(lay):
                assert abs(y - wall) > PROBE_TOL, (w, d, h, burial, name, y, area)


def test_neighbouring_chairs_stand_apart():
    bay_max = genome.load_species("chair")["params"]["bay_max"]
    lay = row.layout(2.4, 0.6, 0.9, bay_max)
    seats = sorted((b for b in _boxes(lay) if b[0].startswith("Chair_Seat")),
                   key=lambda b: b[1][0])
    assert len(seats) == 4
    for a, b in zip(seats, seats[1:]):
        gap = b[1][0] - a[2][0]
        # a gap a person reads as two chairs, and well outside the probe
        assert abs(gap - row.BAY_GAP) < 1e-9 and gap >= 0.01, gap


def test_the_shipped_row_is_what_the_probe_measured():
    """The numbers the 9052 GLB was probed at, so the record above can be
    re-derived: a 0.03 m panel flush with the back plane met a 0.03 m burial.
    Now the panel's front face stands BACK_INSET proud of that wall face."""
    bay_max = genome.load_species("chair")["params"]["bay_max"]
    lay = row.layout(2.4, 0.6, 0.9, bay_max)
    backs = [b for b in _boxes(lay) if b[0].startswith("Chair_Back")]
    assert len(backs) == 4
    for _n, lo, hi in backs:
        assert abs(hi[1] - (0.3 - row.BACK_INSET)) < 1e-9
        front_to_wall = (0.3 - DC_0127_BURIAL) - lo[1]
        assert abs(front_to_wall - row.BACK_INSET) < 1e-9
        # twice the probe's window either way the slot is corrected
        assert front_to_wall >= 2 * PROBE_TOL and 0.3 - hi[1] >= 2 * PROBE_TOL


def test_the_recipe_builds_that_layout():
    """A constant nothing reads is not a fix (CLAUDE.md, the null-result rule)."""
    src = open(_RECIPE, encoding="utf-8").read()
    assert re.search(r"from \._chair_row import layout", src)
    assert re.search(r"lay = layout\(w, d, h, bay_max_of\(plan\)", src)
    assert re.search(r'for name, boxes in lay\["parts"\]:', src)
    assert re.search(r'"collision_boxes": list\(lay\["collision"\]\)', src)
    assert "add_box" in src and "SEAT_T" not in src
