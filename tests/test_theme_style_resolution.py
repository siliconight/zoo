"""A theme name reaches the style a species already carries.

`build.py` asked `if theme in genome["styles"]` and treated a miss as "no
style at all", so a theme Zoo did not carry VERBATIM produced nothing and the
prop came out flat. The prompt path never had that problem -- `_pick_style`
has resolved era, then style tags, then default, since it was written.

WHAT IT COST. Zoo carries `delco` on 39 of 56 species and `1990s` on 14.
`delco_1997` is those two axes in one string, a place and a period, and it
resolved on ZERO. The look was authored; only the spelling was missing. Found
on cold run 9003, where the Pixelcoat half of the same theme gap stopped the
art pass outright and this half was the quieter failure beside it -- a
missing Pixelcoat profile is a wall, a missing Zoo style is a disappointment
(`level_factory/packages/tools/themes.py`).
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from zoo_keeper.core.dna import theme_style

_SPECIES = os.path.join(os.path.dirname(__file__), "..", "zoo_keeper",
                        "genome", "species")


def _genomes():
    out = {}
    for path in sorted(glob.glob(os.path.join(_SPECIES, "*.json"))):
        with open(path, encoding="utf-8") as f:
            g = json.load(f)
        out[g["species"]] = g
    return out


def _one_with(style):
    for name, g in _genomes().items():
        if style in (g.get("styles") or {}):
            return g
    raise AssertionError("no species carries %s" % style)


# ---- resolution order ------------------------------------------------------

def test_an_exact_name_still_wins():
    """Every theme that worked before must resolve identically, or this is a
    behaviour change wearing a bug fix's clothes."""
    g = _one_with("rockay")
    name, block = theme_style(g, "rockay")
    assert name == "rockay"
    assert block == g["styles"]["rockay"]


def test_a_qualified_name_falls_back_to_its_place():
    g = _one_with("delco")
    assert "delco_1997" not in g["styles"]
    name, block = theme_style(g, "delco_1997")
    assert name == "delco"
    assert block == g["styles"]["delco"]


def test_a_year_falls_back_to_its_decade_when_the_place_is_absent():
    """`briefcase` carries `1990s` and no `delco`, so the year is the only
    thing in `delco_1997` it can answer."""
    g = _genomes()["briefcase"]
    assert "delco" not in g["styles"] and "1990s" in g["styles"]
    name, _ = theme_style(g, "delco_1997")
    assert name == "1990s"


def test_a_theme_with_nothing_behind_it_returns_none():
    """None, not a guess. The caller keeps whatever `resolve_plan` chose,
    which is a real answer and is not the same as flat colour."""
    g = _one_with("delco")
    assert theme_style(g, "nonesuch_theme") is None
    assert theme_style(g, "") is None
    assert theme_style(g, None) is None
    assert theme_style({}, "delco") is None


def test_a_non_year_suffix_is_not_read_as_a_decade():
    g = _one_with("delco")
    assert theme_style(g, "delco_99") is None or theme_style(g, "delco_99")[0] == "delco"


# ---- the corpus ------------------------------------------------------------

#: Species that cannot reach `delco_1997`. EMPTY, and it stays empty: three
#: species -- boots, condiment_bottle, helmet -- carried `center_city`,
#: `industrial_flats` and `rockay` but no `delco` and no `1990s`, so the
#: resolver had nothing to fall back to and they were authored a `delco`
#: style. `condiment_bottle` was the pointed one: the brief that exposed all
#: of this is a restaurant row.
_NO_DELCO_1997: set[str] = set()


def test_delco_1997_reaches_every_species():
    """0 of 56 before the resolver, 53 after it, 56 after the three styles."""
    missing = {n for n, g in _genomes().items() if theme_style(g, "delco_1997") is None}
    assert missing == _NO_DELCO_1997, sorted(missing ^ _NO_DELCO_1997)
    assert len(_genomes()) == 56, len(_genomes())


def test_every_shipped_style_name_still_resolves_to_itself():
    """The regression guard for the whole change: resolution must not move any
    theme that already had an exact match."""
    for name, g in _genomes().items():
        for style in (g.get("styles") or {}):
            got = theme_style(g, style)
            assert got is not None and got[0] == style, (name, style, got)
