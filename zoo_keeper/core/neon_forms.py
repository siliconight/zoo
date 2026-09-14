"""neon_sign, planned in pure Python: lit glass tube lettering on a dark
backer, the club's name from `club_names`.

THE LETTERING IS THE FACTORY'S OWN. Pixelcoat draws every shop sign from a
built-in 5 x 7 bitmap (`pixelcoat/core/signage.py`, `_FONT`) and Zoo's
stop sign from `recipes/_legend.py`'s cell grid. The cell grid cannot draw
a diagonal stroke (K M N V W X Y Z are left out of it on purpose), and a
club name needs all of them, so this uses the bitmap. `FONT_5X7` is a COPY
of `_FONT` -- Zoo does not import Pixelcoat, which needs numpy and PIL
inside Blender -- and `tests/test_neon_sign.py` compares the copy against
the Pixelcoat source, read as text, whenever that repo sits beside this one.

A BITMAP IS NOT A TUBE. A neon letter is glass bent along the strokes, so a
glyph is turned into its SKELETON: every lit pixel is joined to each lit
neighbour across an edge, and to a lit diagonal neighbour only when neither
pixel of the corner between them is lit (otherwise the corner is already
drawn by the two straight strokes, and a diagonal as well would double it).
Joins in one direction are merged into maximal straight runs, each run is
one eight-sided `prims.rod` lengthened past its end pixels by
END_EXT x the tube radius so a bend reads as a bend, and a lit pixel with
no neighbour (the dot of an ``!``) is a short upright stub.

WHY RUNS, AND WHY EIGHT SIDES. Two collinear rods of the same phase that
overlap at a shared pixel lay their facets in one plane, and every joint of
a stem drawn pixel by pixel was a SAME pair; a maximal run has no collinear
neighbour. And no rod here has a facet whose normal is along X, Y or Z: an
eight-sided rod's facets sit 22.5 degrees off its frame's axes (see
`club_forms`), so a run's end cap -- normal along X for a horizontal run,
Z for an upright -- can never lie in a facet of the run it ends inside.

LAYOUT. The name is broken into one to three lines, whichever gives the
largest pixel pitch in the sign's lettering area; every glyph advances six
pixels (five and a gap) and lines are ten apart (seven and three). A border
tube with cut corners runs round the lettering in the palette's second
colour.

Frame: metres, Z up, base-up, the lettering facing -Y and the backer's back
the slot's +Y face (the wall).
"""
from __future__ import annotations

import math

from . import club_forms as CF
from . import club_names
from . import prims as P

#: COPY of pixelcoat/pixelcoat/core/signage.py `_FONT` (Pixelcoat 0.41.0),
#: rows top to bottom, "1" lit.
FONT_5X7 = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["11111", "00001", "00001", "00001", "10001", "10001", "01110"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10101", "10011", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "11111"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00000", "00100"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    "/": ["00001", "00001", "00010", "00100", "01000", "10000", "10000"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
}
GW, GH = 5, 7
ADVANCE = GW + 1
LINE = GH + 3
MAX_LINES = 3

#: how far a run's tube reaches past its end pixel, in tube radii
END_EXT = 0.9
#: tube radius as a fraction of the pixel pitch, and its bounds in metres
TUBE_OF_PITCH = 0.16
TUBE_MIN, TUBE_MAX = 0.0025, 0.012

BACKER_T = 0.025
MATERIALS = {
    # standoffs: the clear glass tube supports, read as grey plastic
    "standoff": ([0.30, 0.30, 0.32], "plastic"),
}

_DIRS = ((1, 0), (0, 1), (1, 1), (1, -1))    # (col, row) steps; row grows DOWN


def glyph_runs(ch):
    """``(runs, dots)`` in pixel coordinates (col, row; row 0 is the top):
    runs ``((c0, r0), (c1, r1))`` maximal in one of four directions, dots the
    lit pixels no run touches."""
    rows = FONT_5X7[ch]
    lit = {(c, r) for r in range(GH) for c in range(GW) if rows[r][c] == "1"}
    edges = {d: set() for d in _DIRS}
    for c, r in lit:
        for dc, dr in _DIRS:
            q = (c + dc, r + dr)
            if q not in lit:
                continue
            if dc and dr and ((c + dc, r) in lit or (c, r + dr) in lit):
                continue
            edges[(dc, dr)].add((c, r))
    runs = []
    touched = set()
    for d, starts in edges.items():
        dc, dr = d
        for p in sorted(starts):
            if (p[0] - dc, p[1] - dr) in starts:
                continue                       # not the start of a run
            q = p
            while q in starts:
                touched.add(q)
                q = (q[0] + dc, q[1] + dr)
            touched.add(q)
            runs.append((p, q))
    dots = sorted(lit - touched)
    return sorted(runs), dots


def layout_lines(text, max_lines=MAX_LINES):
    """Every way to break ``text`` at spaces into 1..max_lines lines, the
    most balanced first for each count: ``{n: [line, ...]}``."""
    words = text.split(" ")
    out = {1: [text]}
    n = len(words)
    for lines in range(2, max_lines + 1):
        best = None
        if n < lines:
            break

        def splits(i, left):
            if left == 1:
                yield [" ".join(words[i:])]
                return
            for j in range(i + 1, n - left + 2):
                for rest in splits(j, left - 1):
                    yield [" ".join(words[i:j])] + rest
        for cand in splits(0, lines):
            key = (max(len(s) for s in cand), cand)
            if best is None or key < best:
                best = key
        out[lines] = best[1]
    return out


def plan_layout(text, aw, ah):
    """``(lines, pitch)``: the line break giving the largest pitch that fits
    ``aw`` x ``ah`` metres (fewer lines on a tie)."""
    best = None
    for n, lines in sorted(layout_lines(text).items()):
        cols = max(len(s) for s in lines) * ADVANCE - 1
        rows = n * LINE - 3
        pitch = min(aw / cols, ah / rows)
        if best is None or pitch > best[1] + 1e-9:
            best = (lines, pitch)
    return best


def plan_sign(w, d, h, variant=0):
    """``{"prims", "collision", "text", "lines", "pitch", "tube_r",
    "colours", "overshoot_m"}``. Keys "text" and "border" are emissive
    materials; "backer" is the genome's."""
    text = club_names.name_for(variant)
    text_rgb, border_rgb = club_names.palette_for(variant)
    margin = max(0.05, 0.12 * min(w, h))
    lines, pitch = plan_layout(text, w - 2.4 * margin, h - 2.4 * margin)
    r = max(TUBE_MIN, min(TUBE_MAX, TUBE_OF_PITCH * pitch))
    # the tube plane: the tubes' fronts are the slot's front
    yt = -d / 2 + r
    back_front = d / 2 - min(BACKER_T, 0.3 * d)
    prims = [P.box("NeonSign_Backer", "backer", (-w / 2, back_front, 0.0), (w / 2, d / 2, h))]
    n = len(lines)
    block_h = (n * LINE - 3 - 1) * pitch
    top_z = h / 2 + block_h / 2
    for li, line in enumerate(lines):
        cols = len(line) * ADVANCE - 1
        x0 = -(cols - 1) * pitch / 2
        z0 = top_z - li * LINE * pitch
        for ci, ch in enumerate(line):
            if ch == " ":
                continue
            ox = x0 + ci * ADVANCE * pitch
            runs, dots = glyph_runs(ch)
            longest = None
            for (c0, r0), (c1, r1) in runs:
                a = (ox + c0 * pitch, yt, z0 - r0 * pitch)
                b = (ox + c1 * pitch, yt, z0 - r1 * pitch)
                ln = math.dist(a, b)
                u = tuple((b[k] - a[k]) / ln for k in range(3))
                e = END_EXT * r
                prims.append(P.rod("NeonSign_Tubes", "text",
                                   tuple(a[k] - u[k] * e for k in range(3)),
                                   tuple(b[k] + u[k] * e for k in range(3)), r, segments=8))
                if longest is None or ln > longest[0]:
                    longest = (ln, a, b)
            for c0, r0 in dots:
                cz = z0 - r0 * pitch
                prims.append(P.rod("NeonSign_Tubes", "text", (ox + c0 * pitch, yt, cz - 0.35 * pitch),
                                   (ox + c0 * pitch, yt, cz + 0.35 * pitch), r, segments=8))
            if longest is not None:
                _ln, a, b = longest
                mx, mz = (a[0] + b[0]) / 2, (a[2] + b[2]) / 2
                prims.append(P.rod("NeonSign_Standoffs", "standoff", (mx, yt, mz),
                                   (mx, back_front + 0.005, mz), max(0.003, 0.45 * r),
                                   segments=8))
    # the border tube: a rectangle with 45-degree cut corners
    bx, bz0, bz1 = w / 2 - margin * 0.5, margin * 0.5, h - margin * 0.5
    cut = min(0.06, 0.25 * (bz1 - bz0), 0.25 * bx)
    br = max(TUBE_MIN, min(TUBE_MAX, 0.8 * r))
    ring = [(-bx + cut, yt, bz0), (bx - cut, yt, bz0), (bx, yt, bz0 + cut), (bx, yt, bz1 - cut),
            (bx - cut, yt, bz1), (-bx + cut, yt, bz1), (-bx, yt, bz1 - cut), (-bx, yt, bz0 + cut)]
    prims += CF.tube_path("NeonSign_Border", "border", ring, br, closed=True)
    for x in (-bx, bx):
        prims.append(P.rod("NeonSign_Standoffs", "standoff", (x, yt, h / 2),
                           (x, back_front + 0.005, h / 2), max(0.003, 0.45 * br), segments=8))
    over = CF._overshoot(prims, w, d, h)
    prims, _cb = P.fit_exact(prims, (-w / 2, -d / 2, 0.0), (w / 2, d / 2, h))
    return {"prims": prims, "collision": [], "text": text, "lines": lines, "pitch": pitch,
            "tube_r": r, "colours": {"text": text_rgb, "border": border_rgb},
            "overshoot_m": over}
