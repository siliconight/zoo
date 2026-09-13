"""Faceted sign lettering: a word as flat 2D cells, for a recipe to extrude.

Pure Python (no bpy), so the layout is unit-testable.

WHY CELLS AND NOT A FONT. A sign legend has to read at 10-20 m and cost a few
hundred triangles. Each glyph is a small grid whose rows and columns are sized
as STROKE or COUNTER, and each cell is full, empty, or a triangle with one
corner cut. A cut corner cell is always stroke x stroke, so every chamfer is
45 degrees -- the octagonal O and the angular S of a low-poly Highway Gothic.
Neighbouring cells share their corner vertices, so a glyph is one connected
flat mesh with no overlapping faces and nothing to z-fight within itself.

The cell codes, per row, left to right:

    #   full cell
    .   empty
    a   top-left corner cut      (keeps bottom-left, bottom-right, top-right)
    b   top-right corner cut     (keeps top-left, bottom-left, bottom-right)
    c   bottom-left corner cut   (keeps top-left, top-right, bottom-right)
    d   bottom-right corner cut  (keeps top-left, top-right, bottom-left)

Column and row spans use ``S`` (stroke), ``g`` (the counter between two
strokes), ``m`` (the half-height between three horizontal strokes), ``a``
(the arm either side of a centred stem) and ``r`` (the remainder under one
stroke). All are fractions of the legend HEIGHT.

PROPORTIONS. MUTCD R1-1: a 30 in stop sign carries a 10 in legend, one third
of the sign's flats-to-flats width, centred. Letter width, stroke and spacing
are chosen here, not taken from the Standard Highway Signs tables, and are
recorded as such: width 0.52 h, stroke 0.15 h, gap 0.08 h, which puts the
word at 2.32 h = 0.77 of the sign's width -- inside the red face at every
width the stop_sign genome allows (the face is the width less 2 x 0.035 m).
"""
from __future__ import annotations

#: One third of the sign's flats-to-flats width (MUTCD R1-1, 10 in on 30 in).
LEGEND_H_OF_WIDTH = 1.0 / 3.0
STROKE = 0.15         # stroke width, fraction of legend height
LETTER_W = 0.52       # glyph advance width, fraction of legend height
GAP = 0.08            # space between glyphs, fraction of legend height

GLYPHS = {
    "S": ("SgS", "SmSmS", ("a##",
                           "#..",
                           "c#b",
                           "..#",
                           "##d")),
    "T": ("aSa", "Sr", ("###",
                        ".#.")),
    "O": ("SgS", "SmSmS", ("a#b",
                           "#.#",
                           "#.#",
                           "#.#",
                           "c#d")),
    "P": ("SgS", "SmSmS", ("##b",
                           "#.#",
                           "##d",
                           "#..",
                           "#..")),
}

# corner order in a cell: 0 bottom-left, 1 bottom-right, 2 top-right, 3 top-left
# (counter-clockwise seen from the FRONT, x right and z up)
_KEEP = {"#": (0, 1, 2, 3), "a": (0, 1, 2), "b": (0, 1, 3),
         "c": (1, 2, 3), "d": (0, 2, 3)}


def _spans(code, letter_w):
    t = STROKE
    size = {"S": t, "g": letter_w - 2.0 * t, "m": (1.0 - 3.0 * t) / 2.0,
            "a": (letter_w - t) / 2.0, "r": 1.0 - t}
    return [size[c] for c in code]


def glyph_cells(ch, letter_w=LETTER_W):
    """``(verts, faces)`` for one glyph in units of legend height, origin at
    its bottom-left. ``verts`` are ``(x, z)``; ``faces`` index them CCW as
    seen from the front."""
    cols_code, rows_code, rows = GLYPHS[ch]
    cols = _spans(cols_code, letter_w)
    heights = _spans(rows_code, letter_w)
    if len(rows) != len(heights) or any(len(r) != len(cols) for r in rows):
        raise ValueError(f"glyph {ch!r}: cell map does not match its spans")
    xs = [0.0]
    for c in cols:
        xs.append(xs[-1] + c)
    # rows are authored top to bottom; z grows upward
    zs = [1.0]
    for hgt in heights:
        zs.append(zs[-1] - hgt)
    index = {}
    verts = []

    def vid(i, j):
        key = (i, j)
        if key not in index:
            index[key] = len(verts)
            verts.append((xs[i], zs[j]))
        return index[key]

    faces = []
    for r, row in enumerate(rows):
        for c, code in enumerate(row):
            if code == ".":
                continue
            if code not in _KEEP:
                raise ValueError(f"glyph {ch!r}: unknown cell code {code!r}")
            # the cell's corners: bottom row j = r + 1, top row j = r
            corners = (vid(c, r + 1), vid(c + 1, r + 1),
                       vid(c + 1, r), vid(c, r))
            faces.append(tuple(corners[k] for k in _KEEP[code]))
    return verts, faces


def legend(text, height, letter_w=LETTER_W, gap=GAP):
    """A word laid out centred on the origin, in metres.

    Returns ``[(verts, faces), ...]`` one per glyph, verts as ``(x, z)``, and
    the overall ``(width, height)``. Glyph meshes are kept apart so a recipe
    can build each as its own closed solid.
    """
    n = len(text)
    total_w = (n * letter_w + (n - 1) * gap) * height
    out = []
    x0 = -total_w / 2.0
    for k, ch in enumerate(text):
        verts, faces = glyph_cells(ch, letter_w)
        ox = x0 + k * (letter_w + gap) * height
        out.append(([(ox + x * height, -height / 2.0 + z * height)
                     for x, z in verts], faces))
    return out, (total_w, height)
