"""The window neon's three fixes (1.158.0), from the walker's look at the first renders: "fix those three first".

1. "Scrapple Stout" read "Jcrapple Flout": Deftone Stylus's and Dyspepsia's S thin to a J. A name needing a face's
   illegible capital is set in the next script (`neon_forms.ILLEGIBLE_CAPS`, `window_face`).
2. The loops read as polygons: every traced stroke is corner-cut (`neon_stroke.SMOOTH_PASSES`).
3. Wooder Ice and Shoobie Suds read as blocks: the tube is 0.03 of a cap (`SCRIPT_TUBE_OF_CAP`), not 0.045.
FAILS ON 1.157.0: no `window_face`, no smoothing, the thicker tube.
"""
import math

from zoo_keeper.core import club_names as CN
from zoo_keeper.core import neon_forms as NF
from zoo_keeper.core import neon_stroke as NS
from zoo_keeper.core import prims as P


def test_no_beer_is_set_in_a_face_whose_capital_it_needs_cannot_be_read():
    for v, name in enumerate(CN.WINDOW_NAMES):
        face = NF.window_face(v, name)
        caps = {w[:1] for w in name.split(" ")}
        assert not caps & set(NF.ILLEGIBLE_CAPS.get(face, "")), (name, face)
    assert NF.window_face(4, "SCRAPPLE STOUT") == "sloe_gin"
    assert NF.window_face(1, "JAWN LITE") == "deftone"           # a name its own face can set keeps it


def _turns(polylines):
    out = []
    for pl in polylines:
        for a, b, c in zip(pl, pl[1:], pl[2:]):
            u = (b[0] - a[0], b[1] - a[1])
            w = (c[0] - b[0], c[1] - b[1])
            nu, nw = math.hypot(*u), math.hypot(*w)
            if nu < 1e-9 or nw < 1e-9:
                continue
            out.append(math.degrees(math.acos(max(-1.0, min(1.0, (u[0] * w[0] + u[1] * w[1]) / (nu * nw))))))
    return sorted(out)


def test_a_traced_stroke_bends_rather_than_joints(monkeypatch):
    """Corner-cut once, a stroke turns in more, gentler steps: measured on Jawn Lite in Deftone, the median turn
    between two segments 46 degrees unsmoothed and 18 smoothed, the 90th percentile 85 and 40. A script's cusps (the
    top of an n) stay sharp, so the bound is on the typical turn, not the largest."""
    monkeypatch.setattr(NS, "SMOOTH_PASSES", 0)
    raw = _turns(NS.strokes("Jawn Lite", "deftone")[0])
    monkeypatch.setattr(NS, "SMOOTH_PASSES", 1)
    smooth = _turns(NS.strokes("Jawn Lite", "deftone")[0])
    assert smooth[len(smooth) // 2] < 0.6 * raw[len(raw) // 2]
    assert smooth[int(len(smooth) * 0.9)] < 0.6 * raw[int(len(raw) * 0.9)]


def test_the_tube_is_a_neon_tube_and_the_sign_stays_inside_its_budget():
    from zoo_keeper.core import genome
    budget = genome.load_species("neon_sign")["budgets"]["tris_lod0"]
    assert NF.SCRIPT_TUBE_OF_CAP <= 0.03
    for v in range(len(CN.WINDOW_NAMES)):
        got = NF.plan_sign(1.4, 0.1, 0.6, v, form="window")
        assert got["tube_r"] <= NF.SCRIPT_TUBE_OF_CAP * got["pitch"] + 1e-9
        assert P.tri_count(got["prims"]) <= budget
