"""Smooth type: anti-aliased lettering from minted outline faces (1.46.0).

The walker, 2026-10-02: "this looks like it is made with a 90s GPU ... replace
the retro look". `pixel_type` sets a pixel face on its own grid, 0 or 255,
which is a CRT's letter; a printed marquee's letter has an outline. The faces
here are CC0 outline fonts rasterised ONCE, large, into coverage tables
(`tools/mint_smooth_type.py`, `smooth_faces/`); this module composes a line
of them at that master size and AREA-RESAMPLES it down to the size a tile
asks for. numpy, no PIL: it runs inside Blender.

A line's size is its CAP HEIGHT in pixels, because that is what a designer
means by "this tall" and it does not move with a face's ascender.

    cov = coverage("JAWN JACKPOT", 40, "highway_bold")   # uint8, rows x cols
    w = width("JAWN JACKPOT", 40, "highway_bold")

No kerning (see the mint tool). An unknown face or a character the face does
not have raises, naming what there is.
"""
from __future__ import annotations

import importlib

import numpy as np

FACES = ("highway", "highway_bold", "highway_cond", "minisystem")
_TABLES = {}
_MASTERS = {}


def _table(face):
    t = _TABLES.get(face)
    if t is None:
        if face not in FACES:
            raise ValueError(f"no smooth face {face!r}; the faces are {', '.join(FACES)}")
        t = importlib.import_module(f".smooth_faces.{face}", __package__)
        _TABLES[face] = t
    return t


def _glyph(face, ch):
    key = (face, ch)
    g = _MASTERS.get(key)
    if g is None:
        t = _table(face)
        if ch not in t.GLYPHS:
            raise ValueError(f"smooth face {face!r} has no {ch!r}")
        adv, xo, yo, w, h, hx = t.GLYPHS[ch]
        a = (np.frombuffer(bytes.fromhex(hx), dtype=np.uint8).reshape(h, w) if w and h
             else np.zeros((0, 0), dtype=np.uint8))
        g = (float(adv), int(xo), int(yo), a)
        _MASTERS[key] = g
    return g


def _master(text, face, tracking):
    """The line at master size: float coverage 0..1, the line box tall."""
    t = _table(face)
    pen, places = 0.0, []
    for ch in text:
        adv, xo, yo, a = _glyph(face, ch)
        places.append((int(round(pen)) + xo, yo, a))
        pen += adv + tracking * t.EM
    left = min([x for x, _y, a in places if a.size] + [0])
    right = max([x + a.shape[1] for x, _y, a in places if a.size] + [int(np.ceil(pen))])
    top = min([y for _x, y, a in places if a.size] + [0])
    foot = max([y + a.shape[0] for _x, y, a in places if a.size] + [t.ASCENT + t.DESCENT])
    out = np.zeros((foot - top, right - left), dtype=np.float32)
    for x, y, a in places:
        if not a.size:
            continue
        h, w = a.shape
        view = out[y - top:y - top + h, x - left:x - left + w]
        np.maximum(view, a.astype(np.float32) / 255.0, out=view)
    return out


def _weights(n_in, n_out):
    """An (n_out, n_in) matrix that area-averages ``n_in`` samples into
    ``n_out``: each output pixel is the mean of the span of input it covers,
    partial pixels by their share."""
    m = np.zeros((n_out, n_in), dtype=np.float32)
    step = n_in / float(n_out)
    for i in range(n_out):
        a, b = i * step, (i + 1) * step
        j0, j1 = int(np.floor(a)), min(n_in, int(np.ceil(b)))
        for j in range(j0, j1):
            m[i, j] = min(b, j + 1) - max(a, j)
        m[i] /= max(step, 1e-9)
    return m


def resample(a, new_w, new_h):
    """``a`` (rows x cols, float) area-resampled to ``new_h`` x ``new_w``."""
    h, w = a.shape
    if h == 0 or w == 0 or new_w <= 0 or new_h <= 0:
        return np.zeros((max(0, new_h), max(0, new_w)), dtype=np.float32)
    return _weights(h, new_h) @ a @ _weights(w, new_w).T


def coverage(text, cap_px, face="highway", tracking=0.0, trim=True):
    """``text`` set with capitals ``cap_px`` tall: uint8 coverage, rows x
    cols. ``trim`` crops to the ink (an empty string is one empty pixel)."""
    t = _table(face)
    m = _master(str(text), face, tracking)
    if trim:
        ys = np.where(m.max(axis=1) > 0)[0]
        xs = np.where(m.max(axis=0) > 0)[0]
        if not len(ys):
            return np.zeros((1, 1), dtype=np.uint8)
        m = m[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]
    k = float(cap_px) / float(t.CAP)
    new_w = max(1, int(round(m.shape[1] * k)))
    new_h = max(1, int(round(m.shape[0] * k)))
    out = resample(m, new_w, new_h)
    return np.clip(np.rint(out * 255.0), 0, 255).astype(np.uint8)


def width(text, cap_px, face="highway", tracking=0.0):
    """The ink's width in pixels at ``cap_px``."""
    return int(coverage(text, cap_px, face, tracking).shape[1])


def fit_cap(text, max_w, max_cap, face="highway", min_cap=5, tracking=0.0):
    """The largest whole cap height, ``max_cap`` down to ``min_cap``, at
    which ``text`` is no wider than ``max_w``; None when not even the least
    fits -- a line that does not set is a defect to report, not to crop."""
    t = _table(face)
    full = _master(str(text), face, tracking)
    xs = np.where(full.max(axis=0) > 0)[0]
    ink_w = (xs[-1] - xs[0] + 1) if len(xs) else 1
    for cap in range(int(max_cap), int(min_cap) - 1, -1):
        if ink_w * cap / float(t.CAP) <= max_w:
            return cap
    return None
