"""An Empty's stone lintels and sills (1.71.0).

The walker's South Philly photograph (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"): "white stone lintels and
sills over and under every window". Patina (>= 0.27.0) orders a lintel at
each opening's head and a sill at each window's sill line; these are the
parts, pure, in the cover-local frame (x along the wall, y out from the wall
FACE, z up from the order's line).
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dressing as D
from zoo_keeper.core import genome

OW, OH = 0.95, 1.6


def _box(parts):
    (c, s), = parts
    return [c[i] - s[i] / 2.0 for i in range(3)], [c[i] + s[i] / 2.0 for i in range(3)]


def test_a_lintel_stands_on_the_head_and_bears_past_both_jambs():
    """FAILS ON 1.70.0: nothing built a lintel."""
    lo, hi = _box(D.lintel_parts(OW))
    assert lo[0] == pytest.approx(-OW / 2.0 - D.LINTEL_BEAR) and hi[0] == pytest.approx(OW / 2.0 + D.LINTEL_BEAR)
    assert lo[2] == pytest.approx(0.0) and hi[2] == pytest.approx(D.LINTEL_H)
    assert lo[1] == pytest.approx(0.001) and hi[1] == pytest.approx(0.001 + D.LINTEL_PROUD)


def test_the_lintel_stays_behind_the_bars():
    """Bars run up past the head 3.1 cm off the wall (1.69.0); a lintel
    proud of that would swallow their tops."""
    _lo, hi = _box(D.lintel_parts(OW))
    assert hi[1] < D.BAR_PROUD - D.BAR / 2.0


def test_a_sill_hangs_below_the_sill_line_and_projects():
    lo, hi = _box(D.sill_parts(OW))
    assert hi[2] == pytest.approx(0.0) and lo[2] == pytest.approx(-D.SILL_H)
    assert hi[1] == pytest.approx(0.001 + D.SILL_PROUD) and hi[1] > D.LINTEL_PROUD
    assert lo[0] == pytest.approx(-OW / 2.0 - D.SILL_BEAR)


def _plan(cover):
    order = {"cover": cover, "pos": [0, 0, 0], "normal": [0, 1, 0], "size": OW, "size2": [OW, OH],
             "collision": "none", "seed_offset": 1}
    return D.dress_plan(order, genome.load_species("dress_cover"), "delco_1997",
                        "spec/Blender Z-up raw coords", TOOL_VERSION)


def test_lintels_and_sills_are_stone_coloured_plaster():
    """`plaster` -- Pixelcoat's `plaster_delco`, cream and matte -- is the
    nearest skin to the photograph's white stone that a cover already
    offers. One more material on a side that has openings."""
    for cover in ("lintel", "window_sill"):
        assert _plan(cover)["material"] == "plaster"
    assert _plan("edge_strip")["material"] == "concrete"
