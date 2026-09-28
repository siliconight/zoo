"""1.10.0 -- more than one pixel face, and a mint that refuses a missing glyph.

docs/proposals/CC0_FONTS.md, steps A and B, taken up 2026-09-28 ("start on
the font proposal as well"): `pixel_type` takes ``face=`` and the mint mints
every face in its `FACES`; the mint reads each font's own character map and
refuses a character the face lacks rather than minting PIL's `.notdef` box.

Pure half: the default face is exactly what every recipe had, each face
loads with the whole charset, an unknown face fails. Pixelcoat-and-PIL half
(skipped without them): the character map is read right, the mint refuses a
missing character, the two instruments agree on what "missing" draws, every
table matches its TTF, and no face kerns -- the property that makes a table
of bitmaps lossless.
"""
from __future__ import annotations

import importlib.util
import os
import sys

import pytest

from zoo_keeper.core import pixel_type as pt
from zoo_keeper.core import pixel_type_glyphs as BOLD

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = ("WOODER", "IGGLES TEARS", "Tastes Like the Boulevard at 2 AM.", "75¢", "FLAPPHAS")


def _mint():
    spec = importlib.util.spec_from_file_location("mint", os.path.join(_ZOO, "tools", "mint_pixel_type.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _pixelcoat():
    p = os.environ.get("PIXELCOAT_DIR") or os.path.join(os.path.dirname(_ZOO), "pixelcoat")
    return p if os.path.isdir(os.path.join(p, "assets", "fonts", "pixel_operator")) else None


def test_the_default_face_is_the_one_every_recipe_had():
    assert pt.LINE == pt.line() == pt.line("bold") == BOLD.ASCENT + BOLD.DESCENT
    for s in SAMPLES:
        for scale in (1, 2):
            assert pt.render(s, scale) == pt.render(s, scale, face="bold")
            assert pt.width(s, scale) == pt.width(s, scale, face="bold")
    assert pt.fit_scale("COFFEE", 200) == pt.fit_scale("COFFEE", 200, face="bold")


@pytest.mark.parametrize("face", pt.FACES)
def test_every_face_loads_with_the_whole_charset(face):
    m = _mint()
    t = pt._table(face)
    assert set(m.CHARSET) <= set(t.GLYPHS), set(m.CHARSET) - set(t.GLYPHS)
    assert pt.line(face) == t.ASCENT + t.DESCENT > 0
    mask = pt.render("FLAPPHAS 99¢", 1, face)
    assert len(mask) == pt.line(face) and any(any(r) for r in mask)
    assert tuple(m.FACES) == tuple(sorted(m.FACES, key=list(pt.FACES).index))


def test_the_faces_are_different_faces():
    masks = {f: [bytes(r) for r in pt.render("Delco Reds 75¢", 1, f)] for f in pt.FACES}
    assert len(set(map(tuple, masks.values()))) == len(pt.FACES)
    # the 8 px face is the small print: a shorter line than the 16 px faces
    assert pt.line("small") < pt.line("regular")


def test_an_unknown_face_fails_by_name():
    with pytest.raises(ValueError, match="no pixel face 'comic_sans'"):
        pt.render("X", 1, face="comic_sans")


# --------------------------------------------------------------------------- #
# Against the TTFs Pixelcoat vendors
# --------------------------------------------------------------------------- #

def _need_pixelcoat():
    pc = _pixelcoat()
    if pc is None:
        pytest.skip("Pixelcoat not found (set PIXELCOAT_DIR)")
    pytest.importorskip("PIL.Image")
    sys.dont_write_bytecode = True
    return pc


def test_the_character_map_is_read_from_the_font():
    pc = _need_pixelcoat()
    m = _mint()
    cps = m.cmap_codepoints(m.face_path(pc, "bold"))
    assert all(ord(c) in cps for c in m.CHARSET)
    assert 0x2603 not in cps and 0xE123 not in cps          # a snowman, a private-use point


def test_the_mint_refuses_a_character_the_face_lacks():
    """Before 1.10.0 this minted the `.notdef` box for the snowman and passed."""
    pc = _need_pixelcoat()
    m = _mint()
    with pytest.raises(SystemExit, match="not in the font's character map: '☃'"):
        m.render_table(pc, face="bold", charset="AB☃")


def test_the_two_instruments_agree_on_what_missing_draws():
    """The failure the character map check stops is real: PIL draws a
    character the map lacks as the same box it draws for any other."""
    pc = _need_pixelcoat()
    from PIL import ImageFont
    m = _mint()
    f = ImageFont.truetype(m.face_path(pc, "bold"), 16)
    a, b, c = f.getmask("☃"), f.getmask(""), f.getmask("A")
    assert a.size == b.size and bytes(a) == bytes(b)
    assert bytes(a) != bytes(c)


@pytest.mark.parametrize("face", pt.FACES)
def test_every_table_matches_its_ttf(face):
    pc = _need_pixelcoat()
    m = _mint()
    have = open(m.out_path(face), encoding="utf-8").read()
    assert m.emit(m.render_table(pc, face=face)) == have


@pytest.mark.parametrize("face", pt.FACES)
def test_no_face_kerns_so_a_table_loses_nothing(face):
    """A string PIL sets equals the face's glyphs laid at their advances --
    measured for Bold in 0.87.0, now for every face."""
    pc = _need_pixelcoat()
    from PIL import Image, ImageDraw, ImageFont
    m = _mint()
    px = m.FACES[face][1]
    font = ImageFont.truetype(m.face_path(pc, face), px)
    for s in SAMPLES:
        w = pt.width(s, 1, face) + 8
        img = Image.new("L", (w, pt.line(face)), 0)
        ImageDraw.Draw(img).text((0, pt.ascent(face)), s, fill=255, font=font, anchor="ls")
        ref = [[1 if img.getpixel((x, y)) else 0 for x in range(w)] for y in range(pt.line(face))]
        ours = pt.render(s, 1, face)
        ours = [list(r) + [0] * (w - len(r)) for r in ours]
        assert ours == ref, (face, s)
