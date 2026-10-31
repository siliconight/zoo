"""A window neon's beer bent in a script (1.156.0).

The walker, 2026-10-31: "Neon is also fun", "liquor store should have neon beer company signs". The window form's
tubes followed the 5 x 7 skeleton, so a beer read as dot-matrix capitals. Its name is now set in title case in a sign
face (`neon_forms.WINDOW_FACES`), its centrelines found (`neon_stroke`), and a tube bent along each.
FAILS ON 1.155.0: there is no `neon_stroke`, and a window sign's lettering is the pixel skeleton's capitals.
"""
import math

import numpy as np
import pytest

from zoo_keeper.core import club_names as CN
from zoo_keeper.core import neon_forms as NF
from zoo_keeper.core import neon_stroke as NS
from zoo_keeper.core import prims as P
from zoo_keeper.core import smooth_type as ST


@pytest.mark.parametrize("v", range(len(CN.WINDOW_NAMES)))
def test_the_strokes_lie_on_the_letters_and_lose_none(v):
    """Every stroke point lies on the face's ink, and nine tenths of the ink lies within a stroke's half-width of a
    stroke: no letter and no loop was pruned away."""
    face = NF.WINDOW_FACES[v % len(NF.WINDOW_FACES)]
    text = NF.title_case(CN.WINDOW_NAMES[v])
    cov = ST.coverage(text, NS.CAP_PX, face)
    ink = cov >= 128
    h, w = cov.shape
    polylines, _w, _h = NS.strokes(text, face)
    pts = []
    for pl in polylines:
        for (x0, z0), (x1, z1) in zip(pl, pl[1:]):
            n = max(1, int(math.dist((x0, z0), (x1, z1)) * NS.CAP_PX))
            pts += [(x0 + (x1 - x0) * k / n, z0 + (z1 - z0) * k / n) for k in range(n + 1)]
    rc = np.array([((h - 1) - z * NS.CAP_PX, x * NS.CAP_PX) for x, z in pts])
    on = [ink[max(0, min(h - 1, int(round(r)))), max(0, min(w - 1, int(round(c))))] or
          ink[max(0, int(r) - 2):int(r) + 3, max(0, int(c) - 2):int(c) + 3].any() for r, c in rc]
    assert np.mean(on) > 0.97, (text, np.mean(on))
    yy, xx = np.nonzero(ink)
    reach = 0.09 * NS.CAP_PX
    near = 0
    for y, x in zip(yy[::7], xx[::7]):
        if (np.hypot(rc[:, 0] - y, rc[:, 1] - x) <= reach).any():
            near += 1
    assert near / len(yy[::7]) > 0.9, (text, near / len(yy[::7]))


def test_a_window_sign_sets_its_beer_in_a_script_and_title_case():
    for v in range(len(CN.WINDOW_NAMES)):
        got = NF.plan_sign(1.4, 0.1, 0.6, v, form="window")
        assert got["text"] == CN.WINDOW_NAMES[v]                     # the beer is the table's
        assert " ".join(got["lines"]) == NF.title_case(CN.WINDOW_NAMES[v])
    assert NF.title_case("COLD ONE HON") == "Cold One Hon"
    assert len(set(NF.WINDOW_FACES)) == 3 and all(f in ST.FACES for f in NF.WINDOW_FACES)


def test_the_script_is_tube_not_pixel_and_inside_the_budget():
    """A script's tubes are many short bends, not a handful of straight runs; the wall form keeps the skeleton."""
    from zoo_keeper.core import genome
    budget = genome.load_species("neon_sign")["budgets"]["tris_lod0"]
    for v in range(len(CN.WINDOW_NAMES)):
        got = NF.plan_sign(1.4, 0.1, 0.6, v, form="window")
        tubes = [p for p in got["prims"] if p["part"] == "NeonSign_Tubes"]
        assert len(tubes) > 40, (v, len(tubes))
        assert P.tri_count(got["prims"]) <= budget
    wall = NF.plan_sign(1.4, 0.1, 0.6, 3)
    assert wall["lines"] and wall["lines"] == [ln.upper() for ln in wall["lines"]]
