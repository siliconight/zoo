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
"""
from __future__ import annotations

from .pixel_type_glyphs import ASCENT, DESCENT, GLYPHS

LINE = ASCENT + DESCENT
FALLBACK = "?"


def _glyph(ch):
    return GLYPHS.get(ch) or GLYPHS[FALLBACK]


def width(text: str, scale: int = 1) -> int:
    """Advance width in pixels (the last glyph's trailing space included,
    which is how the face measures itself)."""
    return sum(_glyph(c)[0] for c in text) * int(scale)


def ink_width(text: str, scale: int = 1) -> int:
    """Width of the INK: the advance less the last glyph's trailing space."""
    if not text:
        return 0
    adv = sum(_glyph(c)[0] for c in text[:-1])
    last = _glyph(text[-1])[1]
    right = max((r.rfind("#") + 1 for r in last), default=0)
    return (adv + right) * int(scale)


def render(text: str, scale: int = 1) -> list:
    """The line's mask, ``LINE * scale`` rows by ``width * scale`` columns,
    baseline at row ``ASCENT * scale``."""
    s = int(scale)
    w = width(text, 1)
    rows = [bytearray(w) for _ in range(LINE)]
    x = 0
    for c in text:
        adv, glyph = _glyph(c)
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


def wrap(text: str, max_px: int, scale: int = 1):
    """Greedy word wrap to lines whose INK fits ``max_px``, or None when a
    single word does not fit at this scale (the caller tries a smaller one;
    a word is never broken)."""
    lines, cur = [], ""
    for word in text.split():
        if ink_width(word, scale) > max_px:
            return None
        trial = (cur + " " + word) if cur else word
        if ink_width(trial, scale) <= max_px:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_scale(text: str, max_px: int, cap: int = 16) -> int:
    """The largest whole scale whose ink fits ``max_px`` on one line; 0 if
    not even scale 1 does."""
    best = 0
    for s in range(1, cap + 1):
        if ink_width(text, s) <= max_px:
            best = s
        else:
            break
    return best
