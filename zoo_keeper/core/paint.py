"""Painting with shading in it: a float image and the handful of moves that
make a flat tile read as a made thing (1.46.0).

The walker, 2026-10-02: "this looks like it is made with a 90s GPU". A tile
painted as flat fills is half of that. A real surface is not one colour: it
is darker where two faces meet and where a hand never cleans, lighter along
an edge that catches the light, graded from top to bottom under a ceiling
fixture, and glass has a streak of the room across it. All of that can be
PAINTED -- once, at build time -- and costs a frame nothing.

`Img` is rows x cols x 3, float32, sRGB 0..255, row 0 at the top (the
`Canvas` convention). numpy only: it runs inside Blender. `to_canvas()` hands
the result to everything that already takes a `Canvas`.

Every move takes a pixel box ``(x0, y0, x1, y1)`` and clips to the image.
"""
from __future__ import annotations

import numpy as np

from . import smooth_type as ST
from .vending_forms import Canvas


class Img:
    def __init__(self, w, h, rgb=(0, 0, 0)):
        self.w, self.h = int(w), int(h)
        self.a = np.empty((self.h, self.w, 3), dtype=np.float32)
        self.a[:] = np.asarray(rgb, dtype=np.float32)
        #: every line `text` was asked to set and could not
        self.unset = []

    # --- plumbing -------------------------------------------------------------------
    def _box(self, box):
        x0, y0, x1, y1 = box
        return (max(0, int(round(x0))), max(0, int(round(y0))),
                min(self.w, int(round(x1))), min(self.h, int(round(y1))))

    def to_canvas(self):
        c = Canvas(self.w, self.h)
        c.buf = bytearray(np.clip(np.rint(self.a), 0, 255).astype(np.uint8).tobytes())
        c.unset = list(self.unset)
        return c

    def _mix(self, box, rgb, alpha):
        """``rgb`` over the box at ``alpha`` (a scalar or a rows x cols array)."""
        x0, y0, x1, y1 = self._box(box)
        if x1 <= x0 or y1 <= y0:
            return
        view = self.a[y0:y1, x0:x1]
        al = alpha if np.isscalar(alpha) else np.asarray(alpha, dtype=np.float32)[..., None]
        view += (np.asarray(rgb, dtype=np.float32) - view) * al

    # --- fills ----------------------------------------------------------------------
    def rect(self, box, rgb, alpha=1.0):
        self._mix(box, rgb, float(alpha))

    def vgrad(self, box, top, foot):
        """A fill graded from ``top`` to ``foot``: light falls from above."""
        x0, y0, x1, y1 = self._box(box)
        if x1 <= x0 or y1 <= y0:
            return
        t = np.linspace(0.0, 1.0, y1 - y0, dtype=np.float32)[:, None, None]
        self.a[y0:y1, x0:x1] = (np.asarray(top, dtype=np.float32) * (1.0 - t)
                                + np.asarray(foot, dtype=np.float32) * t)

    def _rr_alpha(self, w, h, r):
        """Anti-aliased coverage of a rounded rectangle ``w`` x ``h``."""
        r = max(0.0, min(float(r), w / 2.0, h / 2.0))
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        dx = np.maximum(np.abs(xs + 0.5 - w / 2.0) - (w / 2.0 - r), 0.0)
        dy = np.maximum(np.abs(ys + 0.5 - h / 2.0) - (h / 2.0 - r), 0.0)
        return np.clip(r - np.sqrt(dx * dx + dy * dy) + 0.5, 0.0, 1.0)

    def rrect(self, box, radius, rgb, alpha=1.0):
        """A rounded rectangle, its corners anti-aliased."""
        x0, y0, x1, y1 = [int(round(v)) for v in box]
        cov = self._rr_alpha(x1 - x0, y1 - y0, radius) * float(alpha)
        cx0, cy0, cx1, cy1 = self._box((x0, y0, x1, y1))
        if cx1 <= cx0 or cy1 <= cy0:
            return
        self._mix((cx0, cy0, cx1, cy1), rgb, cov[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0])

    def disc(self, cx, cy, r, rgb, alpha=1.0):
        self.rrect((cx - r, cy - r, cx + r, cy + r), r, rgb, alpha)

    def _shape(self, box, cover, rgb, alpha):
        """``rgb`` over the box where ``cover(xs, ys)`` -- pixel centres,
        image coordinates -- says how much of each pixel is inside (0..1)."""
        x0, y0, x1, y1 = self._box(box)
        if x1 <= x0 or y1 <= y0:
            return
        ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        self._mix((x0, y0, x1, y1), rgb, np.clip(cover(xs + 0.5, ys + 0.5), 0.0, 1.0) * float(alpha))

    def diamond(self, cx, cy, r, rgb, alpha=1.0):
        """A square stood on its corner, ``r`` from centre to point."""
        self._shape((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1),
                    lambda xs, ys: (r - np.abs(xs - cx) - np.abs(ys - cy)) * 0.7071 + 0.5, rgb, alpha)

    def tri_down(self, cx, y0, half, depth, rgb, alpha=1.0):
        """A triangle hanging from a ``2 * half`` wide top edge at ``y0`` to
        a point ``depth`` below it: a notch cut into a card's top."""
        self._shape((cx - half - 1, y0, cx + half + 1, y0 + depth),
                    lambda xs, ys: half * (1.0 - (ys - y0) / float(depth)) - np.abs(xs - cx) + 0.5,
                    rgb, alpha)

    # --- shading --------------------------------------------------------------------
    def shade(self, box, k):
        """Multiply the box by ``k`` (a scalar or rows x cols): darker under 1."""
        x0, y0, x1, y1 = self._box(box)
        if x1 <= x0 or y1 <= y0:
            return
        kk = k if np.isscalar(k) else np.asarray(k, dtype=np.float32)[..., None]
        self.a[y0:y1, x0:x1] *= kk

    def edge_dark(self, box, depth, strength=0.35, radius=0.0):
        """Contact darkening: the box's rim is ``strength`` darker, fading
        over ``depth`` px toward its middle -- where two surfaces meet and
        where grime stays."""
        x0, y0, x1, y1 = self._box(box)
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            return
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        d = np.minimum(np.minimum(xs + 0.5, w - xs - 0.5), np.minimum(ys + 0.5, h - ys - 0.5))
        if radius > 0:
            dx = np.maximum(np.abs(xs + 0.5 - w / 2.0) - (w / 2.0 - radius), 0.0)
            dy = np.maximum(np.abs(ys + 0.5 - h / 2.0) - (h / 2.0 - radius), 0.0)
            d = np.minimum(d, radius - np.sqrt(dx * dx + dy * dy))
        t = np.clip(d / max(1.0, float(depth)), 0.0, 1.0)
        self.shade((x0, y0, x1, y1), 1.0 - strength * (1.0 - t) ** 2)

    def bevel(self, box, width, light=40.0, dark=40.0, raised=True):
        """A bevelled rim: a raised panel is lit along its top and left and
        dark along its foot and right; a sunken one the other way."""
        x0, y0, x1, y1 = self._box(box)
        w = max(1, int(round(width)))
        hi, lo = (light, -dark) if raised else (-dark, light)
        for i in range(w):
            f = 1.0 - i / float(w)
            self.a[y0 + i:y0 + i + 1, x0 + i:x1 - i] += hi * f
            self.a[y0 + i:y1 - i, x0 + i:x0 + i + 1] += hi * f * 0.7
            self.a[y1 - i - 1:y1 - i, x0 + i:x1 - i] += lo * f
            self.a[y0 + i:y1 - i, x1 - i - 1:x1 - i] += lo * f * 0.7

    def gloss(self, box, strength=0.18, slope=0.6, at=0.3, wide=0.22):
        """A streak of the room across glass: a soft diagonal band, added."""
        x0, y0, x1, y1 = self._box(box)
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            return
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        u = xs / max(1.0, w) + slope * ys / max(1.0, h)
        band = np.exp(-((u - at * (1.0 + slope)) / wide) ** 2)
        band += 0.5 * np.exp(-((u - (at + 0.42) * (1.0 + slope)) / (wide * 0.45)) ** 2)
        self.a[y0:y1, x0:x1] += (255.0 * strength * band)[..., None]

    def vignette(self, box, strength=0.45):
        """Darker toward the corners: a tube's face, a lit panel's falloff."""
        x0, y0, x1, y1 = self._box(box)
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            return
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        r2 = ((xs + 0.5) / w * 2.0 - 1.0) ** 2 + ((ys + 0.5) / h * 2.0 - 1.0) ** 2
        self.shade((x0, y0, x1, y1), 1.0 - strength * np.clip(r2 / 2.0, 0.0, 1.0))

    def scanlines(self, box, period=3, strength=0.22):
        x0, y0, x1, y1 = self._box(box)
        for y in range(y0, y1, max(2, int(period))):
            self.a[y:y + 1, x0:x1] *= (1.0 - strength)

    def grain(self, box, amount=3.0, seed=1):
        """Fine value noise, the same for the same seed: nothing printed or
        moulded is one flat value."""
        x0, y0, x1, y1 = self._box(box)
        if x1 <= x0 or y1 <= y0:
            return
        rng = np.random.RandomState(int(seed) & 0x7FFFFFFF)
        n = rng.standard_normal((y1 - y0, x1 - x0)).astype(np.float32)
        self.a[y0:y1, x0:x1] += (n * float(amount))[..., None]

    def blur(self, box, radius):
        """A box blur run three times: near enough a Gaussian."""
        x0, y0, x1, y1 = self._box(box)
        r = int(radius)
        if r <= 0 or x1 <= x0 or y1 <= y0:
            return
        v = self.a[y0:y1, x0:x1]
        for _ in range(3):
            for axis in (0, 1):
                pad = [(0, 0)] * 3
                pad[axis] = (r, r)
                p = np.pad(v, pad, mode="edge")
                c = np.cumsum(p, axis=axis, dtype=np.float64)
                n = v.shape[axis]
                hi = np.take(c, np.arange(2 * r, 2 * r + n), axis=axis)
                lo = np.take(c, np.arange(0, n), axis=axis) - np.take(p, np.arange(0, n), axis=axis)
                v = ((hi - lo) / (2 * r + 1)).astype(np.float32)
        self.a[y0:y1, x0:x1] = v

    def glow(self, box, radius, strength=0.6):
        """What is bright in the box spills: the box plus a blurred copy of
        itself, added -- phosphor, a backlit panel, a lit cap."""
        x0, y0, x1, y1 = self._box(box)
        if x1 <= x0 or y1 <= y0:
            return
        keep = self.a[y0:y1, x0:x1].copy()
        self.blur((x0, y0, x1, y1), radius)
        self.a[y0:y1, x0:x1] = keep + self.a[y0:y1, x0:x1] * float(strength)

    # --- lettering ------------------------------------------------------------------
    def mask(self, cov, x, y, rgb, alpha=1.0):
        """Coverage (uint8 rows x cols) at (x, y) in ``rgb``."""
        h, w = cov.shape
        x, y = int(round(x)), int(round(y))
        x0, y0, x1, y1 = self._box((x, y, x + w, y + h))
        if x1 <= x0 or y1 <= y0:
            return
        part = cov[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32) / 255.0 * float(alpha)
        self._mix((x0, y0, x1, y1), rgb, part)

    def text(self, text, box, rgb, face="highway", cap=None, min_cap=5, align="centre",
             shadow=None, tracking=0.0):
        """``text`` in the box, its capitals as tall as fit -- ``cap`` at
        most, the box's height at most -- centred up and down. Returns the
        ink's pixel box, or None (and notes the line in ``unset``) when it
        does not set at ``min_cap``."""
        x0, y0, x1, y1 = [int(round(v)) for v in box]
        most = int(min(cap if cap else y1 - y0, y1 - y0))
        got = ST.fit_cap(text, x1 - x0, most, face, min_cap, tracking)
        if got is None:
            self.unset.append(text)
            return None
        cov = ST.coverage(text, got, face, tracking)
        h, w = cov.shape
        tx = {"centre": x0 + (x1 - x0 - w) // 2, "left": x0, "right": x1 - w}[align]
        ty = y0 + (y1 - y0 - h) // 2
        if shadow is not None:
            self.mask(cov, tx + max(1, got // 12), ty + max(1, got // 12), shadow, 0.7)
        self.mask(cov, tx, ty, rgb)
        return (tx, ty, tx + w, ty + h)
