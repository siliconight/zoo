"""The flat-top grill measures exactly its slot (Zoo 1.80.0).

Cold runs 9132, 9179 and 9185 each logged `ZOO_PARTIAL_BUILD` for this species:
`fit_depth` 0.935 m against an exact 0.900 m, because the knobs hung 35 mm past
a cabinet built at the full depth. The layout is pure, so it is tested here
without Blender, at the genome's default and at both ends of its ranges.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from zoo_keeper.core import flat_top_grill_forms as g  # noqa: E402

DIMS = [(1.2, 0.9, 1.05), (0.9, 0.7, 0.98), (1.6, 1.0, 1.15), (1.6, 0.7, 0.98)]


def test_the_extents_are_exactly_the_slot():
    for w, d, h in DIMS:
        for knobs in (2, 3, 4):
            lo, hi = g.bounds(g.layout(w, d, h, knobs))
            for got, want in zip(lo + hi, (-w / 2, -d / 2, 0.0, w / 2, d / 2, h)):
                assert abs(got - want) < 1e-9, ((w, d, h, knobs), lo, hi)


def test_the_knobs_end_on_the_front_face():
    w, d, h = 1.2, 0.9, 1.05
    parts = g.layout(w, d, h, 3)
    knobs = [p for p in parts if p[0].startswith("Grill_Knob_")]
    body = [p for p in parts if p[0] == "Grill_Body"][0]
    assert len(knobs) == 3
    for _n, _s, c, (r, length, axis) in knobs:
        assert axis == "Y"
        assert abs((c[1] - length / 2) - (-d / 2)) < 1e-9
    face = body[2][1] - body[3][1] / 2
    assert abs(face - (-d / 2 + g.KNOB_PROUD)) < 1e-9


def test_the_recipe_builds_from_the_layout():
    """Read as source: the Blender-bound recipe draws the parts the layout
    returns and carries no geometry of its own."""
    path = os.path.join(os.path.dirname(HERE), "zoo_keeper", "recipes",
                        "flat_top_grill.py")
    src = open(path, encoding="utf-8").read()
    assert "grill_forms.layout(w, d, h, n_knobs)" in src
    assert "-d / 2 - 0.02" not in src
