"""Shelf stock (0.78.0): "nothing in the cabinets" (the walker). The planner
is pure Python; these check the rules its docstring promises -- nothing
overhangs, nothing shares a plane, same seed same shelf, and every finish
contrasts with every shelving style."""
from __future__ import annotations

import itertools
import json
import os
import random

import pytest

from zoo_keeper.core import skins
from zoo_keeper.recipes import _shelf_stock as ss

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GENOME = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "shelving.json")

#: (x0, x1, y_front, y_back, z0, clear): a 2 m stockroom bay at 0.4 m deep,
#: a 1.2 m gondola at 0.5, a squat 0.6 m unit, a deep 1.4 m rack, a 2.4 m bay
SPANS = [
    (-0.95, 0.95, -0.192, 0.172, 0.038, 0.549),
    (-0.55, 0.55, -0.24, 0.222, 0.038, 0.552),
    (-0.25, 0.25, -0.144, 0.126, 0.038, 0.251),
    (-7.975, -5.775, -0.672, 0.672, 0.038, 1.419),
    (-1.15, 1.15, -0.24, 0.222, 1.2, 0.30),
]
SEEDS = range(40)


def _plan(seed, span):
    return ss.plan_shelf(random.Random(seed), *span)


def _overlap(a0, a1, b0, b1):
    return min(a1, b1) - max(a0, b0)


@pytest.mark.parametrize("span", SPANS)
def test_nothing_overhangs(span):
    x0, x1, yf, yb, z0, clear = span
    for seed in SEEDS:
        for it in _plan(seed, span):
            lo, hi = it["min"], it["max"]
            assert lo[0] >= x0 + ss.EDGE - 1e-9 and hi[0] <= x1 - ss.EDGE + 1e-9, it
            assert lo[1] >= yf + ss.EDGE - 1e-9 and hi[1] <= yb - ss.BACK_GAP + 1e-9, it
            assert hi[2] <= z0 + clear - ss.HEADROOM + 1e-9, it
            assert lo[2] >= z0 - ss.SINK - 1e-9, it


@pytest.mark.parametrize("span", SPANS)
def test_no_two_faces_share_a_plane(span):
    """Across every pair of items AND each item against the board it stands
    on: no two axis-aligned faces within 2 mm of one plane where their other
    two extents overlap. Cans are judged by their bounding box, which is
    exact for their caps and conservative for their sides."""
    tol = 0.002
    x0, x1, yf, yb, z0, clear = span
    board = {"min": (x0 - 1, yf - 1, z0 - 0.035), "max": (x1 + 1, yb + 1, z0)}
    for seed in SEEDS:
        items = _plan(seed, span)
        for a, b in itertools.combinations(items + [board], 2):
            for k in range(3):
                o = [m for m in range(3) if m != k]
                ov0 = _overlap(a["min"][o[0]], a["max"][o[0]],
                               b["min"][o[0]], b["max"][o[0]])
                ov1 = _overlap(a["min"][o[1]], a["max"][o[1]],
                               b["min"][o[1]], b["max"][o[1]])
                if ov0 <= 1e-6 or ov1 <= 1e-6:
                    continue
                for fa in (a["min"][k], a["max"][k]):
                    for fb in (b["min"][k], b["max"][k]):
                        assert abs(fa - fb) >= tol, (seed, k, a, b)


@pytest.mark.parametrize("span", SPANS)
def test_items_side_by_side_never_interpenetrate(span):
    """Two items whose volumes overlap must be a stack: the upper one sunk
    SINK into the one below and inside it by at least 3 mm on every side.

    The floor is a literal, not `ss.STACK_STEP`: asserted against the
    module's own constant this passed with STACK_STEP set to 0, which is the
    defect it exists to catch."""
    step = 0.003
    assert ss.STACK_STEP >= step
    for seed in SEEDS:
        items = _plan(seed, span)
        for a, b in itertools.combinations(items, 2):
            ov = [_overlap(a["min"][k], a["max"][k], b["min"][k], b["max"][k])
                  for k in range(3)]
            if min(ov) <= 0:
                continue
            lower, upper = (a, b) if a["min"][2] < b["min"][2] else (b, a)
            assert abs(upper["min"][2] - (lower["max"][2] - ss.SINK)) < 1e-9, (seed, a, b)
            for k in (0, 1):
                assert upper["min"][k] >= lower["min"][k] + step - 1e-9
                assert upper["max"][k] <= lower["max"][k] - step + 1e-9


def test_same_seed_same_shelf_and_seeds_differ():
    span = SPANS[0]
    assert _plan(7, span) == _plan(7, span)
    assert len({json.dumps(_plan(s, span)) for s in SEEDS}) == len(SEEDS)


def test_a_shelf_is_actually_stocked():
    """The complaint was empty shelves: a 2 m bay should be mostly used."""
    x0, x1 = SPANS[0][0], SPANS[0][1]
    for seed in SEEDS:
        items = _plan(seed, SPANS[0])
        assert len(items) >= 4, seed
        base = [it for it in items if abs(it["min"][2] - (SPANS[0][4] - ss.SINK)) < 1e-9]
        used = sum(it["max"][0] - it["min"][0] for it in base)
        assert used / (x1 - x0) >= 0.3, (seed, used)


def test_a_shelf_too_low_or_too_shallow_stays_empty():
    assert ss.plan_shelf(random.Random(1), -0.5, 0.5, -0.2, 0.2, 0.0, 0.05) == []
    assert ss.plan_shelf(random.Random(1), -0.5, 0.5, -0.03, 0.03, 0.0, 0.5) == []


def _lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def test_every_finish_contrasts_with_every_shelf_style():
    """Linear-RGB relative luminance ratio >= 1.4 against each style's board
    colour and its frame (0.7 x, `shelving._darker`)."""
    g = json.load(open(_GENOME, encoding="utf-8"))
    greys = []
    for st in g["styles"].values():
        greys.append(st["color"])
        greys.append([v * 0.7 for v in st["color"]])
    assert len(greys) >= 10
    for finish, (colour, _kind) in ss.PALETTE.items():
        for grey in greys:
            hi, lo = sorted((_lum(colour), _lum(grey)), reverse=True)
            assert (hi + 0.05) / (lo + 0.05) >= 1.4, (finish, grey)


def test_every_finish_kind_is_known():
    for finish, (_colour, kind) in ss.PALETTE.items():
        assert kind in skins.KNOWN_KINDS, (finish, kind)
