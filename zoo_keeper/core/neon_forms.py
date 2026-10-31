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
from . import neon_stroke
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
    # Pixelcoat 0.61.0's: WOODER ICE & HOAGIES and SCRAPPLE & SONS DELI
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
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

#: THE TUBES SIT A FINGER OFF THE CAN. 0.88.0 put the tubes at the slot's
#: front and a 25 mm backer at its back, so on Deli Counter's 0.10 m sign
#: the glass stood 60-70 mm proud of the face it was mounted on. Under the
#: walk's ceiling light every word threw a second, dark copy of itself onto
#: the backer, offset by that gap -- double vision. It is the tubes' CAST
#: SHADOW, not geometry: `plan_sign` draws no dark lettering, and in a
#: two-sign lab (Godot 4.7, GL Compatibility, one omni lamp above and in
#: front) the 0.88.0 sign's backer held 12,576 pixels darker than its median
#: by 20 with the lamp's shadow on and 3 with it off; the sign built this way
#: held 0 either way, under the same lamp in the same frame (0.89.0
#: CHANGELOG). A real sign's tube is held 15-25 mm off the can by its glass
#: standoffs, and its shadow is a tight halo under the tube. So: the tubes
#: keep the slot's front, the backer's face is one standoff behind them and
#: the backer takes the rest of the depth -- it is the can.
TUBE_STANDOFF = 0.02
#: the least the can may be; a slot shallower than tubes + standoff + this
#: gives up standoff first
BACKER_T_MIN = 0.012
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


#: THE WINDOW FORM (1.27.0): a sign HUNG in a store's window, facing the
#: street -- a beer (`club_names.WINDOW_NAMES`) in red or blue. What a window
#: neon hangs on is a clear sheet, not a painted can, so the backer is the
#: same box the wall form's can is -- everything behind the standoffs, which
#: is what fills the slot's depth and keeps `fit_exact` at a scale of 1 --
#: stopped short of the top by HANG_FRAC of the height, and the recipe gives
#: it a see-through material. Two chains rise from the sheet's top to the
#: slot's top, where the sign hangs; they share the standoffs' material, so
#: the window form adds a part and no material.
#:
#: REFUTED, kept above what replaced it: the first draft dropped the backer
#: and stood the tubes in the slot's middle plane. `fit_exact` maps the
#: prims' bounds onto the slot per axis, so with nothing but tubes spanning
#: the depth it would have stretched a 2r-deep tube ~3x into the slot's
#: 0.06 m -- flat ovals, and a fit check that passed.
FORMS = ("wall", "window")
HANG_FRAC = 0.12
#: The sheet: clear acrylic, as nearly invisible as storefront glass
#: (`arch.SF_GLASS_OPACITY`, 0.12) -- the tubes are the sign.
SHEET_TINT = (0.85, 0.90, 0.92)
SHEET_OPACITY = 0.12


#: A WINDOW NEON'S BEER IS BENT IN A SCRIPT (1.156.0). The walker, 2026-10-31: "Neon is also fun", "liquor store
#: should have neon beer company signs" -- and its comps' window neon is a brand's script in glass, which the 5 x 7
#: skeleton drew as dot-matrix capitals. The window form now sets its beer in title case in one of `WINDOW_FACES`
#: (by variant), finds the tubes' centrelines (`neon_stroke`), and bends a tube along each (`club_forms.tube_path`),
#: `SCRIPT_TUBE_OF_CAP` of a cap thick and `SCRIPT_SEGMENTS`-sided. The wall form -- a club's name -- is unchanged.
WINDOW_FACES = ("dyspepsia", "deftone", "sloe_gin")
#: A TUBE A NEON'S WIDTH (1.158.0): 0.045 of a cap filled a condensed script's letters -- Wooder Ice and Shoobie Suds
#: read as blocks (the walker, of the first renders). 0.03 is a real tube's 8-15 mm on a window sign's lettering.
SCRIPT_TUBE_OF_CAP = 0.03
#: A FACE'S CAPITALS THAT DO NOT SURVIVE TRACING (1.158.0), judged from the renders: Deftone Stylus's and Dyspepsia's
#: S thin to a J -- "Scrapple Stout" read "Jcrapple Flout". A name needing one is set in the next of `WINDOW_FACES`.
ILLEGIBLE_CAPS = {"deftone": "S", "dyspepsia": "S"}


def window_face(variant, text):
    """The script a window beer is set in: `WINDOW_FACES` from the variant's own, the first whose illegible capitals
    the name does not need (title case: each word's first letter)."""
    caps = {w[:1].upper() for w in str(text).split(" ") if w}
    n = len(WINDOW_FACES)
    for k in range(n):
        face = WINDOW_FACES[(int(variant) + k) % n]
        if not caps & set(ILLEGIBLE_CAPS.get(face, "")):
            return face
    return WINDOW_FACES[int(variant) % n]
SCRIPT_SEGMENTS = 6
#: lines of a script stand this many caps apart, foot to the next line's top
SCRIPT_LINE_GAP = 0.25


def title_case(text):
    """A sign painter's upper and lower case: each word's first letter up, the rest down ("Cold One Hon")."""
    return " ".join(w[:1].upper() + w[1:].lower() for w in text.split(" "))


def script_layout(text, face, aw, ah):
    """``(scale, lines, sets)``: the line break of ``text`` in ``face`` that sets largest inside ``aw`` x ``ah``
    metres -- ``scale`` metres to the cap, ``sets`` each line's `neon_stroke.strokes`."""
    best = None
    for n, lines in sorted(layout_lines(text).items()):
        sets = [neon_stroke.strokes(ln, face) for ln in lines]
        bw = max(s[1] for s in sets)
        bh = sum(s[2] for s in sets) + SCRIPT_LINE_GAP * (n - 1)
        scale = min(aw / bw, ah / bh)
        if best is None or scale > best[0] + 1e-9:
            best = (scale, lines, sets)
    return best


#: each rod of a script's tubes turned by this fraction of a facet more than the last (the golden ratio's): two
#: strokes that run side by side -- a script's loops, a junction's meeting strokes -- would otherwise present parallel
#: facets a fraction of a millimetre apart, the coincident pair every species here is held clear of
SCRIPT_PHASE_STEP = 0.6180339887


def _phased_tube(pts, r, closed, first):
    """`club_forms.tube_path`'s rods along ``pts``, each lengthened at its joints the same way, the k-th turned by
    ``(first + k) * SCRIPT_PHASE_STEP`` of a facet."""
    n = len(pts)
    segs = [(k, (k + 1) % n) for k in range(n if closed else n - 1)]
    facet = 2.0 * math.pi / SCRIPT_SEGMENTS
    out = []
    for idx, (i, j) in enumerate(segs):
        a, b = pts[i], pts[j]
        dv = CF._unit3(CF._sub3(b, a))
        # an open stroke runs `END_EXT` radii past its ends, as the pixel lettering's runs do: two strokes ending on
        # one junction then cross into each other's tube, where their caps would otherwise face across a hair's gap
        ea = eb = END_EXT * r
        if closed or i > 0:
            ea = CF._joint_ext(CF._unit3(CF._sub3(a, pts[(i - 1) % n])), dv, r)
        if closed or j < n - 1:
            eb = CF._joint_ext(dv, CF._unit3(CF._sub3(pts[(j + 1) % n], b)), r)
        p0 = tuple(a[k] - dv[k] * ea for k in range(3))
        p1 = tuple(b[k] + dv[k] * eb for k in range(3))
        phase = (((first + idx) * SCRIPT_PHASE_STEP) % 1.0) * facet
        out.append(P.rod("NeonSign_Tubes", "text", p0, p1, r, segments=SCRIPT_SEGMENTS, phase=phase))
    return out


#: a script's tube that lies coincident with one already laid -- two strokes overlapping along a stretch -- is slimmed
#: by this factor about its own axis, at most twice, which moves every facet plane off its neighbour's; one still
#: coincident is left out (the stroke it overlaps carries the light there)
SCRIPT_SLIM = 0.94


def _slim(q, f):
    """``q`` (a `prims.rod`: two rings of equal count) with its radius scaled by ``f`` about its own axis."""
    v = q["verts"]
    n = len(v) // 2
    c0 = tuple(sum(p[k] for p in v[:n]) / n for k in range(3))
    c1 = tuple(sum(p[k] for p in v[n:]) / n for k in range(3))
    out = []
    for i, p in enumerate(v):
        c = c0 if i < n else c1
        out.append(tuple(c[k] + (p[k] - c[k]) * f for k in range(3)))
    return dict(q, verts=out)


def _near(a, b, pad=0.003):
    (alo, ahi), (blo, bhi) = P.bounds([a]), P.bounds([b])
    return all(alo[k] - pad <= bhi[k] and blo[k] - pad <= ahi[k] for k in range(3))


def _clear_coincident(tubes):
    kept = []
    for q in tubes:
        for attempt in range(3):
            if not any(_near(q, k) and P.coincident_pairs([q, k]) for k in kept):
                kept.append(q)
                break
            q = _slim(q, SCRIPT_SLIM)
    return kept


def _script_tubes(prims, sets, scale, hs, yt, r, back_front):
    """Every line's tubes, the block centred on the sheet; standoffs under the three longest strokes."""
    first_tube = len(prims)
    n = len(sets)
    bh = (sum(s[2] for s in sets) + SCRIPT_LINE_GAP * (n - 1)) * scale
    top = hs / 2 + bh / 2
    strokes = []
    for polylines, lw, lh in sets:
        foot = top - lh * scale
        x0 = -lw * scale / 2
        for pl in polylines:
            raw = [(x0 + x * scale, yt, foot + z * scale) for x, z in pl]
            # a point a traced path repeats (a loop's close, a junction's centre on its neighbour) is a zero-length
            # segment the tube cannot bend round: dropped at a tenth of a millimetre
            pts = []
            for q in raw:
                if not pts or math.dist(q, pts[-1]) > 1e-4:
                    pts.append(q)
            closed = len(pts) > 3 and math.dist(pts[0], pts[-1]) < 1e-3
            if closed:
                pts = pts[:-1]
            if len(pts) < 2:
                cx, _y, cz = raw[0]
                prims.append(P.rod("NeonSign_Tubes", "text", (cx, yt, cz - r), (cx, yt, cz + r), r,
                                   segments=SCRIPT_SEGMENTS))
                continue
            pts = CF.merge_collinear(pts, closed=closed)
            # a path that doubles back on itself (A, B, A) is "collinear" to the merge and leaves A, A
            kept = []
            for q in pts:
                if not kept or math.dist(q, kept[-1]) > 1e-4:
                    kept.append(q)
            if closed and len(kept) > 1 and math.dist(kept[0], kept[-1]) <= 1e-4:
                kept.pop()
            pts = kept
            if len(pts) < 2 or (closed and len(pts) < 3):
                continue
            prims += _phased_tube(pts, r, closed, len(prims))
            strokes.append((sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)), pts))
        top = foot - SCRIPT_LINE_GAP * scale
    # a turned tube seldom puts a vertex on the front plane exactly: the script's tubes move the last fraction of a
    # micron forward so their fronts are the slot's front, as the pixel lettering's are (`fit_exact` at a scale of 1)
    tubes = _clear_coincident([q for q in prims[first_tube:] if q["part"] == "NeonSign_Tubes"])
    prims[first_tube:] = [q for q in prims[first_tube:] if q["part"] != "NeonSign_Tubes"] + tubes
    mine = tubes
    if mine:
        dy = (yt - r) - min(v[1] for q in mine for v in q["verts"])
        for q in mine:
            q["verts"] = [(v[0], v[1] + dy, v[2]) for v in q["verts"]]
    for _ln, pts in sorted(strokes, key=lambda s: -s[0])[:3]:
        mx, _y, mz = pts[len(pts) // 2]
        prims.append(P.rod("NeonSign_Standoffs", "standoff", (mx, yt, mz), (mx, back_front + 0.005, mz),
                           max(0.003, 0.45 * r), segments=8))


def plan_sign(w, d, h, variant=0, form="wall"):
    """``{"prims", "collision", "text", "lines", "pitch", "tube_r",
    "colours", "overshoot_m"}``. Keys "text" and "border" are emissive
    materials; "backer" is the genome's -- or, ``form`` "window" (1.27.0),
    the clear sheet a hung window sign's tubes stand on."""
    window = form == "window"
    if window:
        text = club_names.window_name_for(variant)
        text_rgb, border_rgb = club_names.window_palette_for(variant)
    else:
        text = club_names.name_for(variant)
        text_rgb, border_rgb = club_names.palette_for(variant)
    # a hung sign's sheet stops HANG_FRAC short of the top; the chains are there
    hs = h * (1.0 - HANG_FRAC) if window else h
    margin = max(0.05, 0.12 * min(w, hs))
    if window:
        # in a script, found from the face's strokes (1.156.0)
        face = window_face(variant, text)
        pitch, lines, sets = script_layout(title_case(text), face, w - 2.4 * margin, hs - 2.4 * margin)
        r = max(TUBE_MIN, min(TUBE_MAX, SCRIPT_TUBE_OF_CAP * pitch))
    else:
        lines, pitch = plan_layout(text, w - 2.4 * margin, hs - 2.4 * margin)
        r = max(TUBE_MIN, min(TUBE_MAX, TUBE_OF_PITCH * pitch))
    # the tube plane: the tubes' fronts are the slot's front
    yt = -d / 2 + r
    # the can's face is one standoff behind the tubes' backs, and the can
    # is everything from there to the wall; a shallow slot shortens the
    # standoff before it thins the can below BACKER_T_MIN
    standoff = max(0.004, min(TUBE_STANDOFF, d - 2 * r - BACKER_T_MIN))
    back_front = yt + r + standoff
    prims = [P.box("NeonSign_Backer", "backer", (-w / 2, back_front, 0.0), (w / 2, d / 2, hs))]
    if window:
        _script_tubes(prims, sets, pitch, hs, yt, r, back_front)
        lines = []                      # the pixel lettering below draws nothing for a script
    n = len(lines)
    block_h = (n * LINE - 3 - 1) * pitch
    top_z = hs / 2 + block_h / 2
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
    bx, bz0, bz1 = w / 2 - margin * 0.5, margin * 0.5, hs - margin * 0.5
    cut = min(0.06, 0.25 * (bz1 - bz0), 0.25 * bx)
    br = max(TUBE_MIN, min(TUBE_MAX, 0.8 * r))
    ring = [(-bx + cut, yt, bz0), (bx - cut, yt, bz0), (bx, yt, bz0 + cut), (bx, yt, bz1 - cut),
            (bx - cut, yt, bz1), (-bx + cut, yt, bz1), (-bx, yt, bz1 - cut), (-bx, yt, bz0 + cut)]
    prims += CF.tube_path("NeonSign_Border", "border", ring, br, closed=True)
    for x in (-bx, bx):
        prims.append(P.rod("NeonSign_Standoffs", "standoff", (x, yt, hs / 2),
                           (x, back_front + 0.005, hs / 2), max(0.003, 0.45 * br), segments=8))
    if window:
        # two chains, sunk 5 mm into the sheet's top, up to the slot's top
        yc = (back_front + d / 2) / 2
        for x in (-bx + cut, bx - cut):
            prims.append(P.rod("NeonSign_Chain", "standoff", (x, yc, hs - 0.005),
                               (x, yc, h), max(0.002, 0.3 * br), segments=6))
    over = CF._overshoot(prims, w, d, h)
    prims, _cb = P.fit_exact(prims, (-w / 2, -d / 2, 0.0), (w / 2, d / 2, h))
    if window:
        lines = [ln for ln in script_layout(title_case(text), face, w - 2.4 * margin, hs - 2.4 * margin)[1]]
    return {"prims": prims, "collision": [], "text": text, "lines": lines, "pitch": pitch,
            "tube_r": r, "colours": {"text": text_rgb, "border": border_rgb},
            "overshoot_m": over}
