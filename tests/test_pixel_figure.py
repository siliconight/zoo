"""The pin-up figure (1.31.0): built the way a figure is drawn, and held to
what the walker asked of it.

  * both ends of the value range: "using whites and blacks for depth is
    essential" (the walker, 2026-09-30) -- a near-black and a near-white in
    every figure, not a mid-tone ramp;
  * a final line: every pixel round the figure is the outline;
  * the height asked for, eight heads, and the same figure mirrored;
  * PG-13 by the walker's comp (Duke Nukem 3D's club dancer): the swimsuit
    is there across the chest and the hips at every size a poster draws.
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import pixel_figure as PF
from zoo_keeper.core.vending_forms import Canvas

GROUND = (0, 90, 0)                  # a colour no ramp holds


def _paint(height, mirror=False):
    c = Canvas(80, 140, GROUND)
    box = PF.pinup(PF.Figure(), 40, 6, height, mirror=mirror).paint(c)
    return c, box


def _colours(c, box, rows=None):
    x0, y0, x1, y1 = box
    ys = rows if rows is not None else range(y0, y1)
    return {c.get(x, y) for y in ys for x in range(x0, x1)}


@pytest.mark.parametrize("height", [60, 90, 120])
def test_the_figure_carries_black_and_white(height):
    c, box = _paint(height)
    got = _colours(c, box)
    darks = {r[0] for r in (PF.SKIN, PF.HAIR, PF.SUIT)}
    whites = {r[4] for r in (PF.SKIN, PF.HAIR, PF.SUIT)}
    assert got & darks, "no near-black value"
    assert got & whites, "no near-white value"


def test_the_ramps_span_the_value_range():
    """Each ramp spans two of `poster_checks`' value groups, dark core to
    specular, and climbs in value step by step."""
    from zoo_keeper.core import poster_checks as K
    luma = lambda p: 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
    for ramp in (PF.SKIN, PF.HAIR, PF.SUIT):
        assert luma(ramp[4]) - luma(ramp[0]) >= 2 * K.MASS_SPREAD, ramp
        assert [luma(v) for v in ramp] == sorted(luma(v) for v in ramp), ramp


def test_the_final_line_rings_the_figure():
    c, box = _paint(90)
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        row = [c.get(x, y) for x in range(x0, x1)]
        inked = [i for i, p in enumerate(row) if p != GROUND]
        if inked:
            assert row[inked[0]] == PF.OUTLINE and row[inked[-1]] == PF.OUTLINE, y


@pytest.mark.parametrize("mirror", [False, True])
def test_the_height_asked_for(mirror):
    for height in (60, 90, 120):
        _c, (x0, y0, x1, y1) = _paint(height, mirror)
        # the pose is 60 units head to heel; the outline adds a pixel a side
        assert abs((y1 - y0) - height) <= 3, (height, y1 - y0)
        assert (y1 - y0) / (x1 - x0) > 2.5, "a figure, not a lump"


def test_mirrored_is_the_same_figure():
    _a, ba = _paint(90)
    _b, bb = _paint(90, mirror=True)
    assert abs((ba[2] - ba[0]) - (bb[2] - bb[0])) <= 1 and abs((ba[3] - ba[1]) - (bb[3] - bb[1])) <= 1


@pytest.mark.parametrize("height", [60, 90, 120])
def test_the_swimsuit_is_there(height):
    """PG-13 (the walker's comp): swimwear and a pose, no more."""
    c, box = _paint(height)
    k = height / PF.POSE_HEIGHT
    suit = set(PF.SUIT)
    for band in ((14.8, 15.9), (25.4, 27.4)):            # the chest band; the hips
        rows = range(6 + int(band[0] * k), 6 + int(band[1] * k) + 1)
        assert _colours(c, box, rows) & suit, (height, band)


def test_the_same_figure_every_time():
    a, _ = _paint(90)
    b, _ = _paint(90)
    assert bytes(a.buf) == bytes(b.buf)
