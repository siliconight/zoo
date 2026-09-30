"""The pin-up figure (1.31.0; three poses 1.32.0): built the way a figure is
drawn, and held to what the walker asked of it.

  * both ends of the value range: "using whites and blacks for depth is
    essential" (the walker, 2026-09-30) -- a near-black and a near-white in
    every figure, not a mid-tone ramp;
  * a final line round the figure;
  * THE SILHOUETTE TEST (the walker's figure guide): each pose keeps the gaps
    it declares -- elbow off the waist, ground between the legs -- at every
    height a poster draws it; 1.31.0's one pose did not;
  * the height asked for, and the same figure mirrored;
  * PG-13 by the walker's comp (Duke Nukem 3D's club dancer): the swimsuit is
    there across the chest and the hips, built as clothing -- cups, straps,
    ties (the clothing guide) -- with a little cleavage above the top.
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import pixel_figure as PF
from zoo_keeper.core.vending_forms import Canvas

GROUND = (0, 90, 0)                  # a colour no ramp holds
TOP = 12
#: The heights the club painter draws a figure at (`poster_art.club`: 0.47,
#: 0.56 and 0.62 of a 164 px sheet), and one either side.
HEIGHTS = (60, 77, 92, 101, 120)


def _paint(height, mirror=False, pose="behind_head"):
    c = Canvas(90, 150, GROUND)
    f = PF.pinup(PF.Figure(), 45, TOP, height, mirror=mirror, pose=pose)
    box = f.paint(c)
    return c, box, f


def _colours(c, box, rows=None):
    x0, y0, x1, y1 = box
    ys = rows if rows is not None else range(y0, y1)
    return {c.get(x, y) for y in ys for x in range(x0, x1)}


def _rows(height, y0, y1):
    k = height / PF.POSE_HEIGHT
    return range(TOP + int(y0 * k), TOP + int(y1 * k) + 1)


@pytest.mark.parametrize("pose", PF.POSES)
@pytest.mark.parametrize("height", [60, 90, 120])
def test_the_figure_carries_black_and_white(pose, height):
    c, box, _f = _paint(height, pose=pose)
    got = _colours(c, box)
    assert got & {r[0] for r in (PF.SKIN, PF.HAIR, PF.SUIT)}, "no near-black value"
    assert got & {r[4] for r in (PF.SKIN, PF.HAIR, PF.SUIT)}, "no near-white value"


def test_the_ramps_span_the_value_range():
    """Each ramp spans two of `poster_checks`' value groups, dark core to
    specular, and climbs in value step by step."""
    from zoo_keeper.core import poster_checks as K
    luma = lambda p: 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
    for ramp in (PF.SKIN, PF.HAIR, PF.SUIT, PF.POLE):
        assert luma(ramp[4]) - luma(ramp[0]) >= 2 * K.MASS_SPREAD, ramp
        assert [luma(v) for v in ramp] == sorted(luma(v) for v in ramp), ramp


@pytest.mark.parametrize("pose", PF.POSES)
def test_a_final_line_rings_the_figure(pose):
    """Every body pixel's empty neighbour is line: near-black, or on a lit
    edge the form's own second value -- never the ground."""
    _c, _box, f = _paint(90, pose=pose)
    c = Canvas(90, 150, GROUND)
    f.paint(c)
    for (x, y) in PF._ring(f.body):
        assert c.get(x, y) != GROUND, (x, y)
    lines = {c.get(x, y) for (x, y) in PF._ring(f.body)}
    assert PF.OUTLINE in lines and len(lines) > 1, "every edge the same line"


# --- the silhouette test ------------------------------------------------------------------


@pytest.mark.parametrize("pose", PF.POSES)
@pytest.mark.parametrize("height", HEIGHTS)
@pytest.mark.parametrize("mirror", [False, True])
def test_each_pose_keeps_its_gaps(pose, height, mirror):
    """The figure guide: "If two shapes merge, change the pose." Measured on
    1.31.0's pose at 77 and 101 px: legs 0.10 and 0.31, the near arm 0.14
    and 0.78. Every declared gap here must split at least 80% of its rows."""
    _c, _box, f = _paint(height, mirror, pose)
    got = PF.gaps(f, TOP, height, pose)
    assert set(got) == set(PF.GAPS[pose])
    assert all(v >= 0.8 for v in got.values()), (pose, height, got)


def test_the_gap_measure_can_fail():
    """A figure whose legs are one column splits no row of its legs band."""
    f = PF.Figure()
    f.capsule((45.0, TOP), (45.0, TOP + 90.0), 6.0, 6.0, PF.SKIN)
    assert PF.gaps(f, TOP, 90, "behind_head")["legs"] == 0.0


def test_no_gap_is_a_pole():
    """The pole stands behind the body and is not its silhouette: a gap the
    pole made would pass a merged figure."""
    _c, _box, f = _paint(90, pose="pole")
    assert f.back
    assert f.silhouette() == set(f.body) | PF._ring(f.body)


@pytest.mark.parametrize("pose", PF.POSES)
@pytest.mark.parametrize("mirror", [False, True])
def test_the_height_asked_for(pose, mirror):
    for height in (60, 90, 120):
        _c, (x0, y0, x1, y1), _f = _paint(height, mirror, pose)
        # 60 units head to heel; the pole grip reaches a unit and a half over
        # the head, and the outline adds a pixel a side
        assert height - 3 <= y1 - y0 <= height * 1.04 + 3, (pose, height, y1 - y0)
        assert (y1 - y0) / (x1 - x0) > 2.5, "a figure, not a lump"


@pytest.mark.parametrize("pose", PF.POSES)
def test_mirrored_is_the_same_figure(pose):
    _a, ba, _f = _paint(90, pose=pose)
    _b, bb, _g = _paint(90, mirror=True, pose=pose)
    assert abs((ba[2] - ba[0]) - (bb[2] - bb[0])) <= 1 and abs((ba[3] - ba[1]) - (bb[3] - bb[1])) <= 1


# --- PG-13, and the swimsuit as clothing --------------------------------------------------


@pytest.mark.parametrize("pose", PF.POSES)
@pytest.mark.parametrize("height", [60, 90, 120])
def test_the_swimsuit_is_there(pose, height):
    """PG-13 (the walker's comp): swimwear and a pose, no more -- the top
    across the chest and the bottom across the hips, every pose, every size."""
    c, box, _f = _paint(height, pose=pose)
    suit = set(PF.SUIT)
    for band in ((15.8, 17.6), (25.4, 27.4)):           # the cups; the bottom
        assert _colours(c, box, _rows(height, *band)) & suit, (pose, height, band)


@pytest.mark.parametrize("pose", PF.POSES)
@pytest.mark.parametrize("height", [77, 101])
def test_a_little_cleavage(pose, height):
    """The walker: "a little cleavage like in the duke nukem 3d comp". The
    cleft is a vertical run of the skin ramp's near-black on the centre line,
    between the bust masses and down into the top; the first cut began it
    lower and the cups hid it.

    Counted as a RUN, not as pixels: the bust's own core shadow puts 2-7
    near-black pixels in the same window with no cleft drawn, and a pixel
    count passed that. Measured at these heights: the longest run is 4-6 with
    the cleft and at most 2 without."""
    c, box, _f = _paint(height, pose=pose)
    k = height / PF.POSE_HEIGHT
    rows = list(_rows(height, 12.5, 16.5))
    best = 0
    for x in range(45 - int(2 * k), 45 + int(2 * k) + 1):
        n = 0
        for y in rows:
            n = n + 1 if c.get(x, y) == PF.SKIN[0] else 0
            best = max(best, n)
    assert best >= 3, (pose, height, best)


@pytest.mark.parametrize("pose", PF.POSES)
def test_the_straps_reach_the_neck(pose):
    """The clothing guide: a top is held up by something. The halter straps
    are the suit's dark value between the cups and the neck."""
    c, box, _f = _paint(101, pose=pose)
    got = _colours(c, box, _rows(101, 8.5, 13.0))
    assert PF.SUIT[1] in got, pose


def test_an_unknown_pose_is_refused():
    with pytest.raises(ValueError):
        PF.pinup(PF.Figure(), 45, TOP, 90, pose="split")


def test_the_same_figure_every_time():
    a, _, _f = _paint(90, pose="pole")
    b, _, _g = _paint(90, pose="pole")
    assert bytes(a.buf) == bytes(b.buf)
