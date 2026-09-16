"""The invented card games, makers and teams, and the guard that no real
mark reaches the art.

Zoo 0.95.0. `core/card_brands.py` is the table and `core/card_art.py` paints
from it; these tests hold the mechanical rules of both. Every one of them
fails on 0.94.0, where neither module exists.

WHAT THE DENYLIST IS AND IS NOT, in the same words `club_names.py` uses: it
is a guard, not a proof. It lists the card games, publishers, graders,
leagues, clubs and players a writer reaches for without thinking; nobody has
searched a trademark register for the rest.
"""
from __future__ import annotations

import re

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import card_brands as CB
from zoo_keeper.core import pixel_type as pt


def _tokens(s):
    return set(re.findall(r"[A-Z0-9']+", s.upper()))


# --- the table ---------------------------------------------------------------


def test_the_tables_are_well_formed():
    assert len(CB.GAMES) >= 10
    ids = [g["id"] for g in CB.GAMES]
    assert len(ids) == len(set(ids)), ids
    assert set(CB.IDS) == set(CB.BY_ID)
    for g in CB.GAMES:
        assert g["kind"] in CB.KINDS, g
        for key in ("name", "short", "slogan", "border", "ground", "ink", "accent"):
            assert g[key], (g["id"], key)
        assert 3 <= len(g["short"]) <= 5, g["short"]
        for key in ("border", "ground", "ink", "accent"):
            assert re.fullmatch(r"#[0-9a-f]{6}", g[key]), (g["id"], key)
    assert all(len(t) == 3 for t in CB.TEAMS)
    assert len({t[0] for t in CB.TEAMS}) == len(CB.TEAMS)
    assert len({m["id"] for m in CB.MAKERS}) == len(CB.MAKERS)


def test_every_kind_is_actually_used():
    """A `kind` nothing carries is a branch of `card_art._figure` no frame
    ever shows -- the reference names four card frames and the table has to
    stock all four."""
    used = {g["kind"] for g in CB.GAMES}
    assert used == set(CB.KINDS), sorted(set(CB.KINDS) - used)


# --- the denylist ------------------------------------------------------------


def test_no_painted_string_carries_a_real_mark():
    """Held against what the ART can paint, not against the table: the two
    are the same set today and stop being the same set the moment somebody
    letters something new."""
    bad = []
    for s in CA.painted_strings():
        up = s.upper()
        for w in CB.DENY_WORDS:
            if w in _tokens(up):
                bad.append((s, "word", w))
        for part in CB.DENY_PARTS:
            if part in up:
                bad.append((s, "part", part))
    assert bad == [], bad


def test_the_denylist_can_actually_fail():
    """Falsification. A guard that cannot fire is indistinguishable from one
    that passed -- and this one is a loop over a list somebody could empty."""
    assert len(CA.painted_strings()) >= 40
    assert len(CB.DENY_WORDS) >= 30 and len(CB.DENY_PARTS) >= 20
    for probe, why in (("TOPPS DELCO", "word"), ("THE JAWN GATHERING", "word"),
                       ("UPPER DECK OF DARBY", "part"),
                       ("POKEJAWN BEASTS", "part")):
        hit = any(w in _tokens(probe) for w in CB.DENY_WORDS) or \
            any(p in probe for p in CB.DENY_PARTS)
        assert hit, (probe, why)


def test_the_changed_names_stayed_changed():
    """Three names were moved while the table was written and the module
    records why. A regression here is somebody putting one back."""
    names = {t[0] for t in CB.TEAMS} | {g["name"] for g in CB.GAMES}
    assert "FOLSOM FLOUNDERS" in names and "FOLSOM FLYERS" not in names
    assert "MACDADE MIDNIGHT" in names and "MACDADE MYSTICS" not in names
    slogans = " | ".join(g["slogan"] for g in CB.GAMES)
    assert "Collect the Whole Jawn." in slogans
    assert "COLLECT 'EM ALL" not in slogans.upper()


# --- the face ----------------------------------------------------------------


def test_every_painted_string_is_spellable_in_the_factory_face():
    """A glyph the face does not have renders as `?`, which is how a shop
    sign ends up saying JAWN BE?STS."""
    missing = {}
    for s in CA.painted_strings():
        for ch in s:
            if ch not in pt.GLYPHS:
                missing.setdefault(s, set()).add(ch)
    assert missing == {}, missing


# --- the art -----------------------------------------------------------------


def _px(m):
    return int(round(m * CA.TEXEL))


def test_the_atlas_is_deterministic_and_named_from_its_pixels():
    tiles = {f"box_{g['id']}": {"kind": "box", "game": g["id"],
                                "maker": CB.MAKERS[0]["id"],
                                "w_m": 0.135, "h_m": 0.092, "key": "t"}
             for g in CB.GAMES[:5]}
    a = CA.build_atlas(tiles, "t")
    b = CA.build_atlas(tiles, "t")
    assert a["name"] == b["name"]
    assert bytes(a["canvas"].buf) == bytes(b["canvas"].buf)
    assert a["canvas"].png()[:8] == b"\x89PNG\r\n\x1a\n"
    # a different game in the same slot is a different atlas
    tiles2 = dict(tiles)
    tiles2.pop(sorted(tiles2)[0])
    assert CA.build_atlas(tiles2, "t")["name"] != a["name"]


def test_every_tile_kind_paints_and_fills_its_box():
    specs = [
        {"kind": "box", "game": "jawn_beasts", "maker": "pike_press",
         "w_m": 0.27, "h_m": 0.18, "key": "k"},
        {"kind": "header", "game": "hexes_and_hoagies", "w_m": 0.9,
         "h_m": 0.18, "key": "k"},
        {"kind": "tin", "game": "blue_route_2099", "w_m": 0.2, "h_m": 0.135,
         "key": "k"},
        {"kind": "slab", "game": "delco_diamond", "w_m": 0.086, "h_m": 0.13,
         "key": "k"},
        {"kind": "card", "game": "nanas_grimoire", "w_m": 0.063, "h_m": 0.088,
         "key": "k"},
        {"kind": "label", "maker": "wooder_works", "says": CB.SHOP_SAYS[0],
         "w_m": 0.155, "h_m": 0.13, "key": "k"},
    ]
    for spec in specs:
        c = CA.paint(spec)
        assert c.w == _px(spec["w_m"]) and c.h == _px(spec["h_m"]), spec
        assert len({c.get(x, y) for y in range(c.h)
                    for x in range(0, c.w, 3)}) >= 3, spec


def test_a_box_front_at_ship_size_carries_its_game():
    """THE MEASUREMENT THAT SET `TEXEL`. At 160 px/m none of the twelve
    booster-box fronts could carry its short name over its figure, because
    the pixel face trims to `NAME_BAND` rows and a 0.18 m box is 29 of them.
    This asserts all twelve do -- by finding the name band's own ink, not by
    trusting the constant."""
    assert CA.NAME_BAND >= 8
    lettered = 0
    for g in CB.GAMES:
        c = CA.box_face(g, _px(0.27), _px(0.18), "k", CB.MAKERS[0])
        band = [c.get(x, y) for y in range(2, 2 + CA.NAME_BAND + 3)
                for x in range(c.w)]
        if len(set(band)) > 1:
            lettered += 1
    assert lettered == len(CB.GAMES), lettered


def test_a_card_face_is_never_lettered():
    """The walker's own framing: nobody reads a card face at play distance,
    and type nobody can resolve costs the same as type somebody can."""
    import inspect
    src = inspect.getsource(CA.card_face)
    assert "_stamp" not in src, "card_face grew lettering"


def test_the_orders_rotate_and_are_deterministic():
    a = CB.game_order("stem_one")
    assert a == CB.game_order("stem_one")
    assert len(a) == len(CB.GAMES) and len({g["id"] for g in a}) == len(a)
    # a rotation keeps the table's own order, which is how a shop stocks
    i = CB.GAMES.index(a[0])
    assert [g["id"] for g in a] == [CB.GAMES[(i + k) % len(CB.GAMES)]["id"]
                                    for k in range(len(CB.GAMES))]
    assert len({CB.game_order(f"s{k}")[0]["id"] for k in range(40)}) >= 4
    assert len({CB.team_order(f"s{k}")[0][0] for k in range(40)}) >= 4


ALL = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

if __name__ == "__main__":
    for fn in ALL:
        fn()
        print(f"[ok] {fn.__name__}")
    print(f"\n{len(ALL)} card_brands tests passed.")
