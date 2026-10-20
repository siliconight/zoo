"""A desk's computer is on (1.115.0; the factory's roadmap 148).

The walker's look review, 2026-10-19: "computer screens hsould be on...bring life to this dead world". Every desk
monitor showed the dark ``screen`` finish. `core.desk_screens` paints six 1997 office screens; `_surface_stock._monitor`
puts an art quad in front of the glass; `plan_surface` names its app from where the monitor stands and asks the atlas
for every app; `prim_mesh.build_stock` builds the screens on a backlit `_Face` material.

FAIL ON 1.114.1: there is no `desk_screens`, a monitor has no art quad, and an office top plans no tiles.
"""
import random
import re
import zlib

import pytest

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import desk_screens as DS
from zoo_keeper.recipes import _surface_stock as SS

SPEC = {"kind": "desk_screen", "w_m": 0.258, "h_m": 0.198}


def _lumas(c):
    b = c.buf
    return [0.2126 * b[3 * i] + 0.7152 * b[3 * i + 1] + 0.0722 * b[3 * i + 2] for i in range(c.w * c.h)]


@pytest.mark.parametrize("app", DS.APPS)
def test_every_app_paints_the_same_bytes_every_time(app):
    a = DS.paint(dict(SPEC, app=app))
    b = DS.paint(dict(SPEC, app=app))
    assert (a.w, a.h) == (b.w, b.h) and bytes(a.buf) == bytes(b.buf)
    # 4:3-ish, as the screen it is painted for
    assert a.w == DS.W and abs(a.h / a.w - SPEC["h_m"] / SPEC["w_m"]) < 0.01


def test_the_apps_differ_and_read_as_on():
    """Six pictures, no two alike, each with something lit on it; the three with a lit ground (a blue page, a white
    sheet, a teal desktop) bright over the whole face. The terminals and the screensaver are dark by nature -- a few
    lines or stars on black -- and are held only to their brightest pixels."""
    seen = set()
    for app in DS.APPS:
        c = DS.paint(dict(SPEC, app=app))
        seen.add(zlib.crc32(bytes(c.buf)))
        lum = _lumas(c)
        assert max(lum) > 100.0, app
        if app in ("word", "sheet", "desk"):
            assert sum(lum) / len(lum) > 40.0, app
    assert len(seen) == len(DS.APPS)


def test_an_unknown_app_refuses_by_name():
    with pytest.raises(ValueError, match="the apps are"):
        DS.paint(dict(SPEC, app="excel"))


#: Real software, publishers and platforms of the time: none is painted.
DENY = ("wordperfect", "word perfect", "microsoft", "excel", "lotus", "1-2-3", "quattro", "windows", "ms-dos",
        "msdos", "ibm", "apple", "macintosh", "norton", "aol", "prodigy", "compuserve", "netscape", "after dark",
        "flying toaster", "novell", "wordstar")


def test_no_real_product_is_painted():
    """Whole words: SCRAPPLE is not APPLE."""
    for s in DS.painted_strings():
        low = s.lower()
        assert not any(re.search(r"\b" + re.escape(d) + r"\b", low) for d in DENY), s


def test_the_card_atlas_paints_a_desk_screen():
    c = CA.paint(dict(SPEC, app="term"))
    assert bytes(c.buf) == bytes(DS.paint(dict(SPEC, app="term")).buf)


def test_where_a_monitor_stands_decides_its_app_and_spreads_them():
    assert DS.pick_app(1.234, -0.5) == DS.pick_app(1.234, -0.5)
    shown = {DS.pick_app(x * 0.37, y * 0.91) for x in range(12) for y in range(4)}
    assert shown == set(DS.APPS)


def test_a_monitor_carries_a_screen_quad_in_front_of_its_glass():
    prims = SS._monitor(random.Random(1))
    art = [p for p in prims if p.get("tile") == SS.SCREEN_TILE]
    assert len(art) == 1
    q = art[0]
    ys = {round(v[1], 6) for v in q["verts"]}
    assert ys == {round(-0.19 - SS.DETAIL - SS.SCREEN_PROUD, 6)}
    # more than 2 mm in front of the glass's face, so the coincident-face rule holds
    assert SS.SCREEN_PROUD > 0.002
    # the winding faces -Y: ascending X along the bottom edge
    (x0, _y0, z0), (x1, _y1, z1) = q["verts"][0], q["verts"][1]
    assert x1 > x0 and z1 == z0


def test_naming_the_screen_draws_nothing_from_the_stock_stream():
    """The app comes from where the monitor stands, so every item placed after a monitor stays where it was."""
    SS._screen_art()                      # builds with no stream at all
    rng = random.Random(7)
    before = rng.getstate()
    SS._screen_art()
    assert rng.getstate() == before


def test_an_office_top_lights_its_screens_from_one_atlas():
    """Every office top with a monitor asks for every app's tile -- one image, one lit material for every desk -- and
    each screen quad names the app where it stands."""
    got = SS.plan_surface(random.Random(3), "office", -0.8, 0.8, -0.4, 0.4, 0.75, host_rgb=(0.4, 0.3, 0.2),
                          facing=0.0, clear=0.8)
    screens = [p for p in got["prims"] if str(p.get("tile", "")).startswith(SS.SCREEN_TILE + "_")]
    assert screens, "an office top this size places a workstation"
    assert sorted(got["tiles"]) == sorted(f"{SS.SCREEN_TILE}_{a}" for a in DS.APPS)
    for q in screens:
        assert re.fullmatch(SS.SCREEN_TILE + "_(" + "|".join(DS.APPS) + ")", q["tile"])


#: Tops an office stock is planned on: a desk's (1.6 x 0.8), a small one, and a long cubicle work surface.
TOPS = [(-0.8, 0.8, -0.4, 0.4), (-0.45, 0.45, -0.3, 0.3), (-1.2, 1.2, -0.35, 0.35)]


@pytest.mark.parametrize("seed", range(10))
@pytest.mark.parametrize("top", TOPS)
@pytest.mark.parametrize("facing", [0.0, None])
def test_the_screens_move_nothing_else_on_a_top(monkeypatch, seed, top, facing):
    """1.114.1's top, its screens added and nothing else moved: every other prim and every item where it was.

    The screen's art stands SCREEN_PROUD in front of the glass, and the first build counted it in the monitor's
    footprint: 2.5 mm deeper, every anchor and jitter drawn from the stream after it landed elsewhere, and in the kit
    A/B against 1.114.1 a cubicle bank's top lost a workstation (six monitors to five). The 1.114.1 arm here is the
    same planner with the art quad taken off the monitor."""
    def plan():
        return SS.plan_surface(random.Random(seed), "office", *top, 0.75, host_rgb=(0.4, 0.3, 0.2), facing=facing,
                               clear=0.8)

    got = plan()
    real = SS._monitor
    monkeypatch.setattr(SS, "_monitor", lambda rng: [p for p in real(rng) if p.get("tile") != SS.SCREEN_TILE])
    was = plan()
    assert [p for p in got["prims"] if not str(p.get("tile", "")).startswith(SS.SCREEN_TILE)] == was["prims"]
    assert got["items"] == was["items"]
