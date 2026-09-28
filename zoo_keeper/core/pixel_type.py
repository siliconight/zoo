"""Text as pixel masks, in the factory's typeface, with no PIL.

Zoo 0.87.0. Pixelcoat sets every shop sign in Pixel Operator Bold
(`pixelcoat/core/signage.py`); `pixel_type_glyphs.py` is that face's 16 px
bitmaps, minted from the same TTF by `tools/mint_pixel_type.py`, and this
module lays them out. Pure Python, so it runs inside Blender (numpy, no PIL)
and in a plain test.

A MASK is a list of ``bytearray`` rows, 1 for ink. ``scale`` multiplies the
16 px grid by a whole number, which for this face is exact (see the mint
tool's docstring for the measurement), so scale 2 is the face at 32 px and
not a blurred 16.

MORE THAN ONE FACE (1.10.0, docs/proposals/CC0_FONTS.md). Every function
takes ``face=``, one of `FACES`: ``None`` or ``"bold"`` is Pixel Operator Bold,
the face every recipe used before, so a caller that names none gets exactly
what it always got; the others are the rest of Pixelcoat's vendored Pixel
Operator family, minted into `pixel_faces/`. A face's metrics differ -- the
8 px ``small`` face is an 8-row line against 13 -- so read them through
`line`, `ascent` and `descent` rather than the module constants, which are
Bold's. An unknown face raises, naming the faces there are.
"""
from __future__ import annotations

import importlib

from . import pixel_type_glyphs as _BOLD
from .pixel_type_glyphs import ASCENT, DESCENT, GLYPHS

#: Bold's metrics, as before 1.10.0; `line(face)` etc. for any face.
LINE = ASCENT + DESCENT
FALLBACK = "?"
#: The faces there are (tools/mint_pixel_type.py `FACES`, which mints them).
FACES = ("bold", "regular", "small_caps", "small_caps_bold", "mono", "small",
         "m5x7", "monogram", "monogram_italic")
_TABLES = {"bold": _BOLD}


def _table(face=None):
    name = face or "bold"
    t = _TABLES.get(name)
    if t is None:
        if name not in FACES:
            raise ValueError(f"no pixel face {name!r}; the faces are {', '.join(FACES)}")
        t = importlib.import_module(f".pixel_faces.{name}", __package__)
        _TABLES[name] = t
    return t


def line(face=None) -> int:
    """A line's height in pixels at scale 1, in ``face``."""
    t = _table(face)
    return t.ASCENT + t.DESCENT


def ascent(face=None) -> int:
    return _table(face).ASCENT


def descent(face=None) -> int:
    return _table(face).DESCENT


def _glyph(ch, face=None):
    g = _table(face).GLYPHS
    return g.get(ch) or g[FALLBACK]


def width(text: str, scale: int = 1, face=None) -> int:
    """Advance width in pixels (the last glyph's trailing space included,
    which is how the face measures itself)."""
    return sum(_glyph(c, face)[0] for c in text) * int(scale)


def ink_width(text: str, scale: int = 1, face=None) -> int:
    """Width of the INK: the advance less the last glyph's trailing space."""
    if not text:
        return 0
    adv = sum(_glyph(c, face)[0] for c in text[:-1])
    last = _glyph(text[-1], face)[1]
    right = max((r.rfind("#") + 1 for r in last), default=0)
    return (adv + right) * int(scale)


def render(text: str, scale: int = 1, face=None) -> list:
    """The line's mask, ``line(face) * scale`` rows by ``width * scale``
    columns, baseline at row ``ascent(face) * scale``."""
    s = int(scale)
    w = width(text, 1, face)
    rows = [bytearray(w) for _ in range(line(face))]
    x = 0
    for c in text:
        adv, glyph = _glyph(c, face)
        for y, r in enumerate(glyph):
            row = rows[y]
            for i, ch in enumerate(r):
                if ch == "#" and x + i < w:
                    row[x + i] = 1
        x += adv
    if s == 1:
        return rows
    out = []
    for r in rows:
        wide = bytearray(len(r) * s)
        for i, v in enumerate(r):
            if v:
                wide[i * s:(i + 1) * s] = b"\x01" * s
        for _ in range(s):
            out.append(bytearray(wide))
    return out


def trim(mask: list) -> list:
    """The mask cropped to its ink (empty -> one empty pixel), the same crop
    Pixelcoat's `_render_ttf` makes, so the two can be compared."""
    ys = [y for y, r in enumerate(mask) if any(r)]
    if not ys:
        return [bytearray(1)]
    xs = [x for r in mask for x, v in enumerate(r) if v]
    x0, x1 = min(xs), max(xs) + 1
    return [bytearray(mask[y][x0:x1]) for y in range(ys[0], ys[-1] + 1)]


def wrap(text: str, max_px: int, scale: int = 1, face=None):
    """Greedy word wrap to lines whose INK fits ``max_px``, or None when a
    single word does not fit at this scale (the caller tries a smaller one;
    a word is never broken)."""
    lines, cur = [], ""
    for word in text.split():
        if ink_width(word, scale, face) > max_px:
            return None
        trial = (cur + " " + word) if cur else word
        if ink_width(trial, scale, face) <= max_px:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_scale(text: str, max_px: int, cap: int = 16, face=None) -> int:
    """The largest whole scale whose ink fits ``max_px`` on one line; 0 if
    not even scale 1 does."""
    best = 0
    for s in range(1, cap + 1):
        if ink_width(text, s, face) <= max_px:
            best = s
        else:
            break
    return best
