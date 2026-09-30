"""The art guide's three tests, as measurements of a painted poster.

Zoo 1.30.0. `docs/reference/Making_Strong_2D_Poster_Art_With_Procedural_Tools.md`,
section 1: "Thumbnail test ... Grayscale test ... Blur test. If a poster fails
one of these, fix the composition before adding detail." Written as code so
they run on every poster the factory paints, not as a reviewer's habit -- the
first measure of "good" rather than "works" (roadmap 18).

THIS MODULE MEASURES AND STOPS (CLAUDE.md: "a probe prints what it measured
and stops"). `measure` returns numbers; `test_poster_wall.py` holds them to
the thresholds below, each stated with where it comes from.

  thumbnail  the poster scaled to what it covers on screen at `READ_M` in the
             walk camera (`look_shots`: 75 degrees vertical over 900 px), and
             the HEADLINE's contrast there: the WCAG relative-luminance ratio
             between the bright and dark ends of its box (10th / 90th
             percentile). Held to `TITLE_RATIO`, WCAG 2's 3:1 for large text
             -- an external standard, not a number chosen here.
  grayscale  full size, luma only: the FOCAL image's mean, over the box it
             was inked in, against the GROUND the painter laid under it.
             REFUTED, kept: the first cut measured against a ring round the
             box, and a ring beside a bar bill's black title band read the
             band as ground -- tightening the box to the ink made the step
             SMALLER (24 -> 10), which is the instrument's fault, not the
             poster's. Held to `FOCAL_STEP`, half of one of the art
             guide's three value groups (255 / 3 / 2). THAT HALF IS A CHOICE:
             the guide says "separate by value" and does not say by how much.
  blur       box-blurred by a tenth of the long edge, the spread (5th to 95th
             percentile luma) of what is left. Held to `MASS_SPREAD`, one
             whole value group (255 / 3): a blurred poster that no longer
             spans two groups is "an even field of noise".
"""
from __future__ import annotations

import math

#: The walk camera (`tools/look_shots.gd`): 75 degrees vertical over 900 px.
CAMERA_VFOV_DEG = 75.0
CAMERA_ROWS = 900
#: The distance the headline is asked to read at, in metres: "readable at
#: play distance" -- the card shop's titles failed at 5 m (2026-09-29).
READ_M = 5.0
TITLE_RATIO = 3.0
FOCAL_STEP = 255.0 / 3.0 / 2.0
MASS_SPREAD = 255.0 / 3.0


def screen_px_per_m(dist_m=READ_M):
    """Pixels a metre covers on the walk camera's screen at ``dist_m``."""
    return CAMERA_ROWS / (2.0 * dist_m * math.tan(math.radians(CAMERA_VFOV_DEG) / 2.0))


def _srgb_lin(v):
    v = v / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def rel_lum(rgb):
    """WCAG relative luminance of an sRGB triple, 0..1."""
    r, g, b = (_srgb_lin(x) for x in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _luma(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def _pixels(canvas):
    w, h = canvas.w, canvas.h
    return [[canvas.get(x, y) for x in range(w)] for y in range(h)]


def _downscale(px, k):
    """Box-filter a pixel grid by ``k`` (0 < k <= 1)."""
    h, w = len(px), len(px[0])
    nw, nh = max(1, int(round(w * k))), max(1, int(round(h * k)))
    out = []
    for y in range(nh):
        ya, yb = int(y * h / nh), max(int(y * h / nh) + 1, int((y + 1) * h / nh))
        row = []
        for x in range(nw):
            xa, xb = int(x * w / nw), max(int(x * w / nw) + 1, int((x + 1) * w / nw))
            n = (yb - ya) * (xb - xa)
            s = [0, 0, 0]
            for yy in range(ya, yb):
                for xx in range(xa, xb):
                    p = px[yy][xx]
                    s[0] += p[0]; s[1] += p[1]; s[2] += p[2]
            row.append((s[0] / n, s[1] / n, s[2] / n))
        out.append(row)
    return out


def _pct(vals, q):
    v = sorted(vals)
    return v[min(len(v) - 1, max(0, int(round(q * (len(v) - 1)))))]


def measure(canvas, info, texel):
    """``{"title_ratio", "focal_step", "mass_spread", "screen_scale"}`` for a
    painted poster; ``texel`` is the painter's pixels a metre. A figure is
    None when the painter placed no such region (the checks treat that as a
    failure, not a pass)."""
    px = _pixels(canvas)
    h, w = len(px), len(px[0])
    out = {}
    # thumbnail: the poster as the walk camera sees it at READ_M
    k = min(1.0, screen_px_per_m() / float(texel))
    out["screen_scale"] = round(k, 4)
    t = info.get("title")
    if t:
        small = _downscale(px, k)
        sh, sw = len(small), len(small[0])
        x0, y0 = int(t[0] * k), int(t[1] * k)
        x1, y1 = max(x0 + 1, int(math.ceil(t[2] * k))), max(y0 + 1, int(math.ceil(t[3] * k)))
        lums = [rel_lum(small[y][x]) for y in range(max(0, y0), min(sh, y1))
                for x in range(max(0, x0), min(sw, x1))]
        lo, hi = _pct(lums, 0.10), _pct(lums, 0.90)
        out["title_ratio"] = round((hi + 0.05) / (lo + 0.05), 3)
    else:
        out["title_ratio"] = None
    # grayscale: the focal image against the ring of ground round it
    f = info.get("focal")
    if f:
        fx0, fy0, fx1, fy1 = [int(v) for v in f]
        inner = [_luma(px[y][x]) for y in range(max(0, fy0), min(h, fy1))
                 for x in range(max(0, fx0), min(w, fx1))]
        ground = info.get("ground")
        out["focal_step"] = (round(abs(sum(inner) / len(inner) - _luma(ground)), 2)
                             if inner and ground else None)
    else:
        out["focal_step"] = None
    # blur: a strong box blur, a tenth of the long edge
    r = max(1, max(w, h) // 10)
    lum = [[_luma(p) for p in row] for row in px]
    blurred = []
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            ys, xs = range(max(0, y - r), min(h, y + r + 1)), range(max(0, x - r), min(w, x + r + 1))
            blurred.append(sum(lum[yy][xx] for yy in ys for xx in xs) / (len(ys) * len(xs)))
    out["mass_spread"] = round(_pct(blurred, 0.95) - _pct(blurred, 0.05), 2)
    return out
