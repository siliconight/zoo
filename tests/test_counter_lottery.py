"""1.47.0 -- the instant-ticket dispensers on a store counter.

Three flat red boxes until now. Cold run 9135's frames put them beside a till
that had just been given a made body, and the store had two looks in one
room. `core/counter_lottery.py` builds each as an acrylic case on a black
foot showing a different ticket, painted into the till's image -- so they
ride in the till's draw, and the counter's shared plastic, which held
nothing else, is gone. Pure half; the built half is
`test_service_counter.py`'s material count.
"""
from __future__ import annotations

import re

import pytest

from tests import _machine_faces as MF
from tests.test_service_counter import _fit
from zoo_keeper.core import card_brands as CB
from zoo_keeper.core import counter_lottery as CL
from zoo_keeper.core import counter_register as CREG
from zoo_keeper.core import prims as P
from zoo_keeper.core import service_counter_forms as S


def _row(n=3, h=1.1):
    out = []
    for i in range(n):
        out += CL.dispenser(0.3 + i * S.LOTTO_PITCH, -0.38, h, i, CREG.PAINT)
    return out


def test_a_row_is_three_different_games_in_identical_cases():
    """One manufactured unit bought three times, a different game in each:
    the cases match to the millimetre and only the ticket differs."""
    assert len(CL.GAMES) == S.LOTTO_MAX == 3
    assert len({g[:2] for g in CL.GAMES}) == 3 and len({g[2] for g in CL.GAMES}) == 3
    units = [CL.dispenser(0.0, -0.38, 1.1, i, CREG.PAINT) for i in range(3)]
    assert [p["verts"] for p in units[0]] == [p["verts"] for p in units[1]] == [p["verts"] for p in units[2]]
    tickets = [next(p["tile"] for p in u if p["part"] == "Counter_Lottery_Ticket") for u in units]
    assert tickets == ["lot_ticket_0", "lot_ticket_1", "lot_ticket_2"]
    lo, hi = P.bounds(units[0])
    assert hi[2] - 1.1 == pytest.approx(CL.H) and hi[0] - lo[0] == pytest.approx(CL.W)
    assert hi[1] - lo[1] == pytest.approx(CL.D)


def test_every_face_points_out_and_the_ticket_leans_back_to_the_customer_s_eyes():
    unit = CL.dispenser(0.0, -0.38, 1.1, 0, CREG.PAINT)
    ticket, = [p for p in unit if p["part"] == "Counter_Lottery_Ticket"]
    seen = MF.check([p for p in unit if p is not ticket])
    assert {"Chamfer", "front", "back", "top", "SideL", "SideR"} <= seen
    n = MF.normal(ticket)
    assert n[1] < -0.9 and 0.02 < n[2] < 0.3, n            # at the customer, tipped up a little
    assert abs(n[0]) < 1e-9


def test_a_row_shares_no_plane_and_every_face_names_a_tile_the_till_s_image_holds():
    row = _row()
    assert P.coincident_pairs(row, tol=0.0022) == []
    A = CREG.paint_art()
    assert A["unset"] == []
    for p in row:
        assert p["mat"] == CREG.PAINT and p["tile"] in A["rects"], p["part"]
        assert len(p["uvs"]) == len(p["faces"])
    # the foot wears the till's own dark plastic: no tile of its own
    assert {p["tile"] for p in row if "_Foot_" in p["part"]} == {"head_side", "head_edge", "head_top"}


def test_the_ticket_is_the_loud_part_and_the_case_is_quiet():
    """The brief, measured: a ticket's field is saturated and the acrylic is
    not. Saturation is (max - min) / max over a tile's mean colour."""
    def sat(c):
        px = [c.get(x, y) for y in range(c.h) for x in range(c.w)]
        m = [sum(p[k] for p in px) / len(px) for k in range(3)]
        return (max(m) - min(m)) / max(m)
    for i in range(3):
        assert sat(CL.paint_ticket(i)) > 0.35, i
    for quiet in (CL.paint_side(), CL.paint_back(), CL.paint_top()):
        assert sat(quiet) < 0.12


def test_every_painted_string_is_invented_and_clears_both_denylists():
    strings = CL.painted_strings()
    assert len(strings) == 4 * len(CL.GAMES)
    for s in strings:
        up = s.upper()
        toks = set(re.findall(r"[A-Z0-9']+", up))
        assert not (toks & set(CB.DENY_WORDS)), s
        assert not [p for p in CB.DENY_PARTS if p in up], s
        assert "LOTTERY" not in up and "LOTTO" not in up, s


def test_the_service_counter_stands_them_and_its_plastic_is_gone():
    _in, on_top, facts, _tw = _fit(6.0, 0.9, 1.1)
    units = [p for p in on_top if p["part"].startswith("Counter_Lottery")]
    assert len(units) == len(facts["lottery"]) * 14
    assert {p["mat"] for p in units} == {CREG.PAINT}
    assert "lotto" not in S.MATERIALS and "plastic" not in S.KIND_BASE
    assert not [p for p in on_top if p["mat"] == "lotto"]
    assert P.coincident_pairs(list(on_top), tol=0.0022) == []
