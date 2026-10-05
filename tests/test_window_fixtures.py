"""An Empty's window fixtures: an air conditioner, bars (1.69.0).

The walker's window photographs (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"): "window air conditioners
in nearly every photograph", standing out of the wall, so GEOMETRY; and bars
"proud of the frame on bolted straps", which were painted into the pane.
Patina (>= 0.26.0) orders both from the slot Deli Counter (>= 0.181.0)
marks; these are the parts, pure, in the cover-local frame every cover uses
(x along the wall, y out from the wall FACE, z up).
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dressing as D
from zoo_keeper.core import genome, window_panes

OW, OH = 0.95, 1.6          # an Empty rowhome's window opening (Deli Counter)


def _extent(parts, axis):
    lo = min(c[axis] - s[axis] / 2.0 for c, s in parts)
    hi = max(c[axis] + s[axis] / 2.0 for c, s in parts)
    return lo, hi


def test_the_unit_stands_on_the_sill_and_reaches_back_to_the_pane():
    """FAILS ON 1.68.0: nothing built a window unit."""
    parts = D.ac_parts(OW)
    cabinet = parts[0]
    (cx, cy, cz), (w, d, h) = cabinet
    assert w == pytest.approx(D.AC_W) and h == pytest.approx(D.AC_H)
    # out of the wall by AC_OUT, back through the reveal to the pane
    assert cy + d / 2.0 == pytest.approx(D.AC_OUT)
    assert cy - d / 2.0 == pytest.approx(-D.AC_BACK)
    # on the sill, lifted clear of it rather than coplanar with it
    assert 0.0 < cz - h / 2.0 < 0.005


def test_the_unit_stays_inside_its_opening():
    """Everything at the window plane or behind the face is inside the
    jambs; only the brackets go below the sill, flat on the wall."""
    for (x, y, z), (sx, sy, sz) in D.ac_parts(OW):
        assert abs(x) + sx / 2.0 <= OW / 2.0 + 1e-9, (x, sx)
        if z + sz / 2.0 <= 0.0:                      # below the sill: a bracket
            assert y - sy / 2.0 > 0.0                # off the wall face, not in it


def test_the_accordion_panels_close_the_sash_to_the_jambs():
    panels = [p for p in D.ac_parts(OW) if p[1][1] < 0.02 and p[0][1] < 0.0 and p[1][0] > 0.05]
    assert len(panels) == 2
    lo, hi = _extent(panels, 0)
    assert lo == pytest.approx(-OW / 2.0 + 0.01) and hi == pytest.approx(OW / 2.0 - 0.01)


def test_a_narrow_opening_takes_a_narrower_unit():
    (_c, (w, _d, _h)) = D.ac_parts(0.6)[0]
    assert w <= 0.6 - 0.2 + 1e-9


def test_bars_span_the_opening_and_run_past_it():
    parts = D.bar_parts(OW, OH)
    bars = [p for p in parts if p[1][2] > OH]        # the uprights
    assert len(bars) == 7
    for (x, y, z), (sx, sy, sz) in bars:
        assert abs(x) < OW / 2.0
        assert sz == pytest.approx(OH + 2 * D.BAR_REACH)
    # the straps reach past each jamb onto the brick, where they are bolted
    lo, hi = _extent([p for p in parts if p[1][0] > OW], 0)
    assert lo == pytest.approx(-OW / 2.0 - D.STRAP_REACH) and hi == pytest.approx(OW / 2.0 + D.STRAP_REACH)


def test_every_bar_part_stands_off_the_wall():
    """Nothing in the wall and nothing flush with its face: 1 mm clear."""
    for (_x, y, _z), (_sx, sy, _sz) in D.bar_parts(OW, OH):
        assert y - sy / 2.0 >= 0.001 - 1e-9


def _plan(cover):
    order = {"cover": cover, "pos": [0, 0, 0], "normal": [0, 1, 0], "size": OW, "size2": [OW, OH],
             "collision": "none", "seed_offset": 1}
    return D.dress_plan(order, genome.load_species("dress_cover"), "delco_1997",
                        "spec/Blender Z-up raw coords", TOOL_VERSION)


def test_the_unit_wears_the_gutters_white_and_the_bars_black_iron():
    """The unit shares the gutters' material, so it merges into a side's
    metal mesh at no extra draw; the bars are a second colour of the same
    painted metal -- one more surface on a side that has them."""
    gutter, unit, bars = _plan("gutter_run"), _plan("ac_unit"), _plan("window_bars")
    assert unit["material"] == gutter["material"] == "metal_painted"
    assert unit["color"] == gutter["color"]
    assert bars["material"] == "metal_painted" and bars["color"] == [round(c, 4) for c in D.IRON_COLOR]
    assert max(bars["color"]) < 0.15


def _cell(canvas, state):
    x0, y0, x1, y1 = window_panes.cell_rect(state)
    return [[canvas.get(x, y) for x in range(x0, x1)] for y in range(y0, y1)]


def test_a_barred_pane_paints_only_its_room():
    """The bars are geometry now, 3.5 cm off the wall with the pane 13 cm
    behind it; painted as well, they drew a second grid sliding against the
    real one. FAILS ON 1.68.0: the barred cells differed from their rooms."""
    albedo, emission = window_panes.atlas()
    for barred, room in (("dark_bars", "dark"), ("lit_bars", "lit")):
        assert _cell(albedo, barred) == _cell(albedo, room), barred
        assert _cell(emission, barred) == _cell(emission, room), barred
