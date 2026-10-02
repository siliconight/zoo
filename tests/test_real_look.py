"""1.46.0 -- the real look's three tools: smooth type, painted shading, and
the parts a machine is made of.

The walker, 2026-10-02: "this looks like it is made with a 90s GPU ...
replace the retro look". The species that use these have their own suites
(`test_video_poker`, `test_atm`, `test_cash_register`,
`test_counter_register`); this holds the tools themselves. Pure: no bpy.
"""
from __future__ import annotations

import numpy as np
import pytest

from tests import _machine_faces as MF
from zoo_keeper.core import card_art as CA
from zoo_keeper.core import machine_parts as MP
from zoo_keeper.core import paint as PT
from zoo_keeper.core import prims as P
from zoo_keeper.core import smooth_type as ST


# --- smooth type ----------------------------------------------------------------------


@pytest.mark.parametrize("face", ST.FACES)
def test_a_line_is_as_tall_as_it_was_asked_to_be(face):
    """A size is a CAP HEIGHT: a capital with a flat top and foot is that
    many pixels tall. Blue Highway lands on it to the pixel; Minisystem's
    own H is a tenth short of the cap height its font declares (measured:
    43 px asked 47) while its digits run a little over, so a tenth is the
    tolerance and `register_forms.DIGIT_MIN_M` is asked of digits."""
    for cap in (8, 20, 47):
        cov = ST.coverage("H", cap, face)
        assert abs(cov.shape[0] - cap) <= max(1, round(cap * 0.1)), (face, cap, cov.shape)
        if face == "minisystem":
            assert ST.coverage("8", cap, face).shape[0] >= cap - 1, (cap,)
        assert cov.dtype == np.uint8
        # a hairline face (Minisystem) at 8 px never fills a pixel; at 20 it does
        assert cov.max() > (200 if cap >= 20 else 60), (face, cap, cov.max())


def test_type_is_anti_aliased_and_the_same_bytes_twice():
    cov = ST.coverage("JAWN 24.99", 22, "highway_bold")
    partial = int(((cov > 0) & (cov < 255)).sum())
    assert partial > 50, "an outline face resampled down has soft edges"
    assert ST.coverage("JAWN 24.99", 22, "highway_bold").tobytes() == cov.tobytes()


def test_fit_cap_is_the_largest_that_fits_and_none_when_nothing_does():
    cap = ST.fit_cap("SURCHARGE", 120, 40, "highway")
    assert cap is not None and ST.width("SURCHARGE", cap, "highway") <= 120
    assert cap == 40 or ST.width("SURCHARGE", cap + 1, "highway") > 120 - 1
    assert ST.fit_cap("SURCHARGE", 6, 40, "highway") is None


def test_an_unknown_face_or_glyph_is_refused_by_name():
    with pytest.raises(ValueError, match="no smooth face"):
        ST.coverage("A", 10, "comic")
    with pytest.raises(ValueError, match="has no"):
        ST.coverage("☃", 10, "highway")


# --- paint ----------------------------------------------------------------------------


def test_an_image_becomes_the_canvas_everything_else_takes():
    im = PT.Img(12, 8, (10, 20, 30))
    im.rect((2, 2, 6, 6), (200, 100, 50))
    c = im.to_canvas()
    assert (c.w, c.h) == (12, 8)
    assert c.get(0, 0) == (10, 20, 30) and c.get(3, 3) == (200, 100, 50)
    assert c.png()[:8] == b"\x89PNG\r\n\x1a\n"


def test_a_line_that_does_not_set_is_reported_and_not_cropped():
    im = PT.Img(20, 12, (0, 0, 0))
    assert im.text("NO FEE ATM THIS AINT", (0, 0, 20, 12), (255, 255, 255)) is None
    assert im.unset == ["NO FEE ATM THIS AINT"] and im.to_canvas().unset == im.unset
    assert im.a.max() == 0.0, "nothing was drawn"
    assert im.text("A", (0, 0, 20, 12), (255, 255, 255)) is not None


def test_shading_darkens_the_rim_and_a_grade_runs_top_to_foot():
    im = PT.Img(40, 40, (100, 100, 100))
    im.edge_dark((0, 0, 40, 40), 8, 0.4)
    assert im.a[0, 20, 0] < im.a[20, 20, 0] == 100.0
    im.vgrad((0, 0, 40, 40), (200, 200, 200), (50, 50, 50))
    assert im.a[0, 5, 0] == 200.0 and im.a[39, 5, 0] == 50.0
    a = PT.Img(30, 30, (90, 90, 90))
    b = PT.Img(30, 30, (90, 90, 90))
    a.grain((0, 0, 30, 30), 3.0, 7)
    b.grain((0, 0, 30, 30), 3.0, 7)
    assert a.a.tobytes() == b.a.tobytes() and a.a.std() > 1.0


# --- the atlas a filtered sampler needs -----------------------------------------------


def test_a_bleeding_atlas_fills_its_gutter_with_each_tile_s_own_edge():
    """A linear sample at a tile's edge reads half a texel past it and each
    mip twice as far. Without bleed that is the atlas's dark ground, and
    every tile wears a dark hairline at a distance."""
    red = PT.Img(20, 10, (200, 0, 0)).to_canvas()
    blue = PT.Img(20, 10, (0, 0, 200)).to_canvas()
    A = CA.atlas([("red", red), ("blue", blue)], "t", gutter=CA.SMOOTH_GUTTER, bleed=True)
    half = CA.SMOOTH_GUTTER // 2
    for key, rgb in (("red", (200, 0, 0)), ("blue", (0, 0, 200))):
        x0, y0, x1, y1 = A["rects"][key]
        for px, py in ((x0 - half, y0), (x1 - 1 + half, y1 - 1), (x0, y0 - half), (x0 - half, y0 - half)):
            assert A["canvas"].get(px, py) == rgb, (key, px, py)
    # the default is the pixel-art atlas every other species has
    B = CA.atlas([("red", red)], "t")
    x0, y0, _x1, _y1 = B["rects"]["red"]
    assert B["canvas"].get(x0 - 1, y0) != (200, 0, 0)


# --- the parts ------------------------------------------------------------------------


def test_a_chamfered_body_is_eight_walls_and_a_top_all_facing_out():
    parts = MP.cbody("T", -0.3, 0.3, -0.2, 0.2, 0.0, 1.0, 0.02)
    assert len(parts) == 9 and P.tri_count(parts) == 8 * 2 + 6
    assert MF.check(parts) >= {"Chamfer", "front", "back", "left", "right", "top"}
    lo, hi = P.bounds(parts)
    assert lo == (-0.3, -0.2, 0.0) and hi == (0.3, 0.2, 1.0)
    assert {p["tile"] for p in parts} == {"side", "edge", "top"}
    skipped = MP.cbody("T", -0.3, 0.3, -0.2, 0.2, 0.0, 1.0, 0.02, skip=("front", "top"))
    assert len(skipped) == 7 and not [p for p in skipped if p["part"] in ("T_front", "T_top")]
    assert P.coincident_pairs(parts) == []


def test_a_surround_slopes_in_and_the_tube_bulges_only_in_its_middle():
    hole, screen = (-0.2, 0.2, 0.5, 0.8), (-0.18, 0.18, 0.52, 0.78)
    wells = MP.wells("T", hole, screen, -0.3, -0.28)
    assert MF.check(wells) == {"Well_B", "Well_T", "Well_L", "Well_R"}
    tube = MP.curved_screen("T_Screen", screen, -0.28, 0.008, (6, 4))
    ys = [v[1] for v in tube["verts"]]
    assert min(ys) == pytest.approx(-0.288) and max(ys) == pytest.approx(-0.28)
    edge = [v for v in tube["verts"] if v[0] in (screen[0], screen[1]) or v[2] in (screen[2], screen[3])]
    assert all(v[1] == pytest.approx(-0.28) for v in edge), "the rim sits in its surround"
    assert len(tube["uvs"]) == len(tube["faces"]) == 24


def test_a_cap_stands_off_a_sloped_deck_with_its_foot_inside_it():
    deck = (-0.3, 0.9, -0.1, 1.0)                        # near edge low, far edge high
    cap = MP.cap("T_Key", "key", 0.0, 0.5, deck, (0.05, 0.04, 0.01))
    n = MF.normal(cap)
    assert n[1] < -0.3 and n[2] > 0.3
    assert len(cap["faces"]) == 5 and cap["uvs"][0][2] == (1.0, 1.0)
    # every side shows the tile's lowest strip, not the whole face
    assert all(max(v for _u, v in f) <= 0.12 for f in cap["uvs"][1:])
