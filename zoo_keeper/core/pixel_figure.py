"""A human figure in pixel art, built the way a figure is drawn.

Zoo 1.31.0. The walker, 2026-09-30, on the club posters: "add silhouettes,
keep it PG-13", Duke Nukem 3D's (1996) club dancer as the comp for how far
suggestive goes, "using more color and depth"; with two figure references --
Lizet Dingemans' "How to draw figures without a model" (Artists &
Illustrators, 2026) and Andrew Loomis's *Fun with a Pencil* (1939) -- and the
art-direction feedback's "draw or edit the important silhouette by hand".

What was taken from them, and how it lands in pixels:

  * EIGHT HEADS, THREE MASSES (Dingemans): skull one head, ribcage one and a
    half, pelvis one; the figure is built on them, not outlined.
  * THE FRAMEWORK FIRST, THEN THE PARTS, THEN THE FINAL LINES (Loomis's
    "Doohinkus"): a joint table, authored by hand -- that is the drawing --
    then shaded masses on it, then a dark pixel outline round the whole.
  * OPPOSED TILTS, WEIGHT OVER THE STANDING LEG (Loomis, p. 55): the hip rides
    high on the standing side and that shoulder drops; the standing ankle is
    under the pit of the neck; the free knee crosses in.
  * A LIGHT SOURCE (Dingemans): every mass is shaded as a form lit from the
    upper left, then banded into a handful of values -- Duke's clusters, not
    a gradient -- and the far limbs sit a step darker.

A first cut drew the figure as flat procedural blobs and read as a lump; a
second, hand-typed as pixels, read as a doll -- six heads, no gesture. This
is the third. Pure Python; it paints onto a `vending_forms.Canvas`.
"""
from __future__ import annotations

import math

_L = (-0.55, -0.62, 0.56)
_n = math.sqrt(sum(v * v for v in _L))
LIGHT = tuple(v / _n for v in _L)

#: Five values a ramp: a near-BLACK core shadow, three body tones, a near-
#: WHITE specular. The walker, 2026-09-30: "using whites and blacks for depth
#: is essential" -- Duke's sprites carry both ends of the value range, and a
#: four-step ramp without them read soft at a distance.
SKIN = ((34, 12, 12), (120, 48, 38), (206, 116, 82), (248, 178, 136), (255, 238, 222))
HAIR = ((18, 6, 6), (62, 18, 14), (138, 44, 24), (206, 90, 44), (250, 186, 130))
SUIT = ((30, 2, 18), (104, 8, 56), (196, 32, 110), (246, 96, 170), (255, 226, 240))
OUTLINE = (30, 8, 10)
LIPS = (196, 34, 56)
FAR = 0.72
#: A pose is drawn in these units: y down from the top of the head, x off
#: the centre line, the figure 60 tall (eight heads of 7.5).
POSE_HEIGHT = 60.0


def _band(b, ramp, dim=1.0):
    b *= dim
    return ramp[0 if b < 0.10 else 1 if b < 0.30 else 2 if b < 0.62 else 3 if b < 0.93 else 4]


class Figure:
    """Pixels keyed (x, y) in painter's order: later parts cover earlier."""

    def __init__(self):
        self.px = {}

    def capsule(self, a, b, r0, r1, ramp, dim=1.0):
        (ax, ay), (bx, by) = a, b
        L = math.hypot(bx - ax, by - ay) or 1e-6
        ux, uy = (bx - ax) / L, (by - ay) / L
        px_, py_ = -uy, ux
        rmax = max(r0, r1)
        for y in range(int(math.floor(min(ay, by) - rmax)) - 1, int(max(ay, by) + rmax) + 2):
            for x in range(int(math.floor(min(ax, bx) - rmax)) - 1, int(max(ax, bx) + rmax) + 2):
                cx, cy = x + 0.5 - ax, y + 0.5 - ay
                t = max(0.0, min(1.0, (cx * ux + cy * uy) / L))
                r = r0 + (r1 - r0) * t
                qx, qy = cx - ux * t * L, cy - uy * t * L
                if math.hypot(qx, qy) > r:
                    continue
                s = (qx * px_ + qy * py_) / r
                k = math.sqrt(max(0.0, 1.0 - s * s))
                bright = max(0.0, px_ * s * LIGHT[0] + py_ * s * LIGHT[1] + k * LIGHT[2])
                self.px[(x, y)] = _band(bright, ramp, dim)

    def ellipsoid(self, c, rx, ry, ramp, tilt=0.0, dim=1.0):
        cx0, cy0 = c
        ca, sa = math.cos(tilt), math.sin(tilt)
        R = max(rx, ry)
        for y in range(int(math.floor(cy0 - R)) - 1, int(cy0 + R) + 2):
            for x in range(int(math.floor(cx0 - R)) - 1, int(cx0 + R) + 2):
                dx, dy = x + 0.5 - cx0, y + 0.5 - cy0
                u = (dx * ca + dy * sa) / rx
                v = (-dx * sa + dy * ca) / ry
                q = u * u + v * v
                if q > 1.0:
                    continue
                k = math.sqrt(1.0 - q)
                nx, ny = u * ca - v * sa, u * sa + v * ca
                bright = max(0.0, nx * LIGHT[0] + ny * LIGHT[1] + k * LIGHT[2])
                self.px[(x, y)] = _band(bright, ramp, dim)

    def dot(self, x, y, rgb):
        self.px[(int(math.floor(x)), int(math.floor(y)))] = rgb

    def paint(self, c, outline=OUTLINE):
        """Onto a Canvas: the figure, then its final line -- every empty pixel
        that touches it. Returns the drawn box (x0, y0, x1, y1)."""
        for (x, y), rgb in self.px.items():
            c.px(x, y, rgb)
        ring = set()
        for (x, y) in self.px:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in self.px:
                    ring.add(q)
        for (x, y) in ring:
            c.px(x, y, outline)
        xs = [x for x, _ in ring]
        ys = [y for _, y in ring]
        return (min(xs), min(ys), max(xs) + 1, max(ys) + 1) if xs else None


def pinup(fig, cx, top, height, mirror=False, suit=SUIT, hair=HAIR, skin=SKIN):
    """THE POSE, authored: contrapposto, the weight on the figure's left leg
    (+x, or -x mirrored), the other hand behind the head. ``top`` is the top
    of the head, ``height`` the figure's height in pixels."""
    k = height / POSE_HEIGHT
    sx = -1.0 if mirror else 1.0

    def P(x, y):
        return (cx + sx * x * k, top + y * k)

    def cap(a, b, r0, r1, ramp, dim=1.0):
        fig.capsule(P(*a), P(*b), r0 * k, r1 * k, ramp, dim)

    tilt = lambda t: t * sx
    # far arm behind the head, and the hair falling behind
    cap((-4.6, 11.2), (-6.6, 3.0), 1.35, 1.1, skin, FAR)
    cap((-6.6, 3.0), (-2.4, 1.6), 1.05, 0.85, skin, FAR)
    cap((1.2, 3.0), (2.6, 12.5), 3.2, 1.6, hair)
    # far leg, free: the knee crosses in, the heel lifts
    cap((-2.6, 30.2), (0.2, 43.4), 2.4, 1.6, skin, FAR)
    cap((0.2, 43.4), (-3.4, 55.6), 1.6, 0.9, skin, FAR)
    cap((-3.4, 55.6), (-2.8, 58.4), 0.9, 0.7, suit, FAR)
    # neck; ribcage (its shoulder low on the standing side); waist; pelvis (high there)
    cap((0.2, 6.8), (0.4, 10.0), 1.35, 1.45, skin)
    fig.ellipsoid(P(0.2, 15.2), 4.3 * k, 5.6 * k, skin, tilt=tilt(-0.16))
    cap((0.4, 19.4), (1.0, 24.0), 3.0, 2.8, skin)
    fig.ellipsoid(P(1.2, 27.0), 5.2 * k, 4.0 * k, skin, tilt=tilt(0.24))
    cap((-4.6, 11.0), (4.8, 12.6), 1.4, 1.4, skin)
    # standing leg: the ankle under the pit of the neck
    cap((3.4, 28.6), (2.4, 44.2), 2.6, 1.7, skin)
    cap((2.4, 44.2), (0.9, 56.8), 1.7, 0.95, skin)
    cap((0.9, 56.8), (2.4, 59.0), 0.95, 0.8, suit)
    # near arm, the hand on the high hip
    cap((4.8, 12.6), (7.0, 19.4), 1.35, 1.1, skin)
    cap((7.0, 19.4), (5.2, 25.2), 1.05, 0.8, skin)
    # head, three quarters, and its hair
    fig.ellipsoid(P(0.0, 3.9), 2.9 * k, 3.7 * k, skin, tilt=tilt(0.12))
    fig.ellipsoid(P(0.6, 2.2), 3.4 * k, 2.6 * k, hair, tilt=tilt(0.2))
    fig.dot(*P(-1.2, 4.0), OUTLINE)
    fig.dot(*P(0.9, 4.0), OUTLINE)
    fig.dot(*P(-0.3, 6.0), LIPS)
    fig.dot(*P(0.4, 6.0), LIPS)
    # the swimsuit: PG-13 by the walker's comp -- swimwear and a pose, no more
    cap((-3.6, 15.9), (3.9, 14.8), 1.5, 1.5, suit)
    cap((-3.4, 27.4), (5.4, 25.4), 1.25, 1.25, suit)
    cap((0.2, 27.2), (1.6, 29.6), 1.5, 0.9, suit)
    return fig
