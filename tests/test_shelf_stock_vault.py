"""1.142.0 -- a bank vault's rack carries the money (the factory's roadmap 321).

The walker, of the bank's vault: "we need to make the cash! in the vault room!". The vault held a cash cart, two
safes and a count table with a few bundles on it, each bundle a note's size and invisible at a room's distance.
`shelving`'s ``vault`` stock puts brick rows -- ten straps of a hundred notes, banded by denomination -- and deposit
bags on a vault rack's shelves (`_shelf_stock.plan_vault_shelf`). These check the rules the planner keeps: nothing
overhangs, nothing shares a plane with anything (a band and its own row included), a stacked row stands off the one
under it, every band wraps its own row, the colours read, and the back office's stock is what it was.
"""
from __future__ import annotations

import itertools
import json
import os
import random

import pytest

from zoo_keeper.core import genome, skins
from zoo_keeper.recipes import _shelf_stock as ss

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GENOME = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "shelving.json")

#: (x0, x1, y_front, y_back, z0, clear): the spans `shelving.build` gives Deli Counter's two `shelf_cash` sizes'
#: bays (1.8 x 0.5 x 1.9 and 1.2 x 0.5 x 1.8, four shelves), a deep 2.4 m bay, and two too small for a brick
SPANS = [
    (-0.85, 0.85, -0.24, 0.226, 0.038, 0.588),
    (-0.55, 0.55, -0.24, 0.226, 0.643, 0.555),
    (-1.15, 1.15, -0.288, 0.276, 0.038, 0.655),
    (-0.95, 0.95, -0.216, 0.201, 0.038, 0.549),
]
SEEDS = range(40)


def _plan(seed, span):
    return ss.plan_vault_shelf(random.Random(seed), *span)


def _overlap(a0, a1, b0, b1):
    return min(a1, b1) - max(a0, b0)


def _rows(items):
    """[(row, band)]: `_bricks` writes a row and then its band."""
    out = []
    for i, it in enumerate(items):
        if it["finish"] == ss.NOTES:
            out.append((it, items[i + 1]))
    return out


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
    """`test_shelf_stock`'s rule, every pair of items and each against its board, and stricter than that module's
    stock needs: a band overlaps its own row by design, so its faces are held off the row's too."""
    tol = 0.002
    x0, x1, yf, yb, z0, clear = span
    board = {"min": (x0 - 1, yf - 1, z0 - 0.035), "max": (x1 + 1, yb + 1, z0)}
    for seed in SEEDS[:15]:
        items = _plan(seed, span)
        for a, b in itertools.combinations(items + [board], 2):
            for k in range(3):
                o = [m for m in range(3) if m != k]
                if (_overlap(a["min"][o[0]], a["max"][o[0]], b["min"][o[0]], b["max"][o[0]]) <= 1e-6
                        or _overlap(a["min"][o[1]], a["max"][o[1]], b["min"][o[1]], b["max"][o[1]]) <= 1e-6):
                    continue
                for fa in (a["min"][k], a["max"][k]):
                    for fb in (b["min"][k], b["max"][k]):
                        assert abs(fa - fb) >= tol, (seed, k, a, b)


@pytest.mark.parametrize("span", SPANS)
def test_a_row_is_a_brick_long_and_bricks_deep_and_its_band_wraps_it(span):
    for seed in SEEDS:
        for row, band in _rows(_plan(seed, span)):
            assert band["finish"].startswith("band_"), band
            lo, hi = row["min"], row["max"]
            assert hi[0] - lo[0] == pytest.approx(ss.BRICK_X)
            deep = (hi[1] - lo[1]) / ss.BRICK_Y
            assert deep == pytest.approx(round(deep)) and round(deep) >= 1
            assert hi[2] - lo[2] == pytest.approx(ss.BRICK_H)
            # the band: across the row's middle, proud of its front, back and top, its foot inside the row
            assert (band["min"][0] + band["max"][0]) / 2 == pytest.approx((lo[0] + hi[0]) / 2)
            assert band["max"][0] - band["min"][0] == pytest.approx(ss.BAND_W)
            assert band["min"][1] == pytest.approx(lo[1] - ss.BAND_PROUD)
            assert band["max"][1] == pytest.approx(hi[1] + ss.BAND_PROUD)
            assert band["max"][2] == pytest.approx(hi[2] + ss.BAND_PROUD)
            assert lo[2] < band["min"][2] < hi[2]


@pytest.mark.parametrize("span", SPANS)
def test_rows_side_by_side_never_meet_and_a_stacked_row_stands_off_the_one_under_it(span):
    for seed in SEEDS:
        rows = [r for r, _b in _rows(_plan(seed, span))]
        bags = [it for it in _plan(seed, span) if it["finish"] in ss.BAGS]
        for a, b in itertools.combinations(rows + bags, 2):
            ov = [_overlap(a["min"][k], a["max"][k], b["min"][k], b["max"][k]) for k in range(3)]
            if min(ov) <= 0:
                continue
            lower, upper = (a, b) if a["min"][2] < b["min"][2] else (b, a)
            assert abs(upper["min"][2] - (lower["max"][2] - ss.SINK)) < 1e-9, (seed, a, b)
            for k in (0, 1):
                assert abs(upper["min"][k] - lower["min"][k]) >= ss.STACK_STEP - 1e-9, (seed, a, b)
                assert abs(upper["max"][k] - lower["max"][k]) >= ss.STACK_STEP - 1e-9, (seed, a, b)


def test_a_vault_shelf_is_money():
    """The complaint was a vault with no money in it: a Deli Counter rack's bay is mostly brick rows."""
    x0, x1 = SPANS[0][0], SPANS[0][1]
    for seed in SEEDS:
        items = _plan(seed, SPANS[0])
        rows = [it for it in items if it["finish"] == ss.NOTES]
        assert len(rows) >= 6, seed
        base = [it for it in items if abs(it["min"][2] - (SPANS[0][4] - ss.SINK)) < 1e-9]
        used = sum(it["max"][0] - it["min"][0] for it in base)
        assert used / (x1 - x0) >= 0.4, (seed, used)
    bands = {it["finish"] for s in SEEDS for it in _plan(s, SPANS[0]) if it["finish"].startswith("band_")}
    assert bands == {b for b, _w in ss.BANDS}


def test_same_seed_same_shelf_and_seeds_differ():
    assert _plan(7, SPANS[0]) == _plan(7, SPANS[0])
    assert len({json.dumps(_plan(s, SPANS[0])) for s in SEEDS}) == len(SEEDS)


def test_a_shelf_too_low_or_too_shallow_stays_empty():
    assert ss.plan_vault_shelf(random.Random(1), -0.5, 0.5, -0.2, 0.2, 0.0, 0.05) == []
    assert ss.plan_vault_shelf(random.Random(1), -0.5, 0.5, -0.03, 0.03, 0.0, 0.5) == []


def _lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _ratio(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_the_money_reads():
    """`test_shelf_stock`'s 1.4 against every shelving style's board and frame for the notes and the bags, and the
    same 1.4 between each band and the notes it is wrapped round: the band is how a rack reads as money."""
    g = json.load(open(_GENOME, encoding="utf-8"))
    greys = []
    for st in g["styles"].values():
        greys += [st["color"], [v * 0.7 for v in st["color"]]]
    for finish in (ss.NOTES,) + ss.BAGS:
        for grey in greys:
            assert _ratio(ss.VAULT_PALETTE[finish], grey) >= 1.4, (finish, grey)
    for band, _w in ss.BANDS:
        assert _ratio(ss.VAULT_PALETTE[band], ss.VAULT_PALETTE[ss.NOTES]) >= 1.4, band
    assert set(ss.VAULT_PALETTE) == {ss.NOTES} | {b for b, _w in ss.BANDS} | set(ss.BAGS)
    assert ss.VAULT_KIND in skins.KNOWN_KINDS


def test_shelving_honours_the_vault_stock_and_nothing_else_moves():
    from zoo_keeper.core import kit
    g = genome.load_species("shelving")
    assert g["params"]["stock"] == ["none", "vault"]
    slot = {"slot_id": "s", "role": "shelving", "species": "shelving", "stock": "vault"}
    dress, dropped = kit.honour_dressing(slot, "shelving")
    assert dress["stock"] == "vault" and dropped == []
    # an unstocked rack asks for nothing, and a flavour shelving has no rule for drops all of it
    assert kit.honour_dressing({"slot_id": "s"}, "shelving") == ({"form": None, "stock": None, "variant": None}, [])
    assert kit.honour_dressing(dict(slot, stock="bar"), "shelving")[1]
    # the back office's planner is untouched: the same seed draws the same shelf it always did
    assert ss.plan_shelf(random.Random(3), -0.95, 0.95, -0.192, 0.172, 0.038, 0.549) == \
        ss.plan_shelf(random.Random(3), -0.95, 0.95, -0.192, 0.172, 0.038, 0.549)
