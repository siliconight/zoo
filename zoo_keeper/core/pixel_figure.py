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

1.32.0, by the walker's figure guide (root repo docs/reference/
Drawing_Humans_and_Humanlike_Figures_for_Poster_Art.md) and their direction
"some thigh/waist curves, and a little cleavage like in the duke nukem 3d
comp":

  * THE SILHOUETTE TEST, filled black at poster size, found 1.31.0's one pose
    merged in two places -- the hand-on-hip elbow into the waist, the legs
    into one column (the crossed free knee closed the wedge between them).
    Each pose now DECLARES the gaps it must keep (`GAPS`) and `gaps()`
    measures them on the silhouette as it is drawn, outline included.
  * THREE POSES, not one "stamped from one mold": the hand behind the head
    (the 1.31.0 pose, its elbow out and its legs opened); the pole lean, one
    hand on the pole and the free knee lifted out; hands on hips, both elbows
    out. The poster chooses by what its headline says.
  * CURVES: a narrower waist, a wider pelvis and fuller thighs, so the
    contour goes in and out; the bust as two masses over the ribcage with a
    cleft between them above a two-cup top. Swimwear and a pose, no more.
  * THE SWIMSUIT AS CLOTHING, by the walker's clothing guide (docs/reference/
    Drawing_Clothing_Layers_on_the_Figure.md: "show how the top and bottom
    are separate pieces ... establish bands, straps, seams"): two cups and a
    gore, halter straps to the neck, a bottom whose band follows the pelvis's
    tilt and ties at the hips. One pixel each; the construction, not texture.
  * NOT EVERY EDGE THE SAME LINE: the outline stays near-black where it meets
    a form's shadow side and softens to that form's own dark where the form is
    lit (the guide: "lit edges can disappear").
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
#: The pole: brass, the same five steps.
POLE = ((30, 20, 6), (110, 78, 24), (196, 150, 56), (240, 206, 110), (255, 246, 214))
OUTLINE = (30, 8, 10)
LIPS = (196, 34, 56)
FAR = 0.72
#: A pose is drawn in these units: y down from the top of the head, x off
#: the centre line, the figure 60 tall (eight heads of 7.5).
POSE_HEIGHT = 60.0


def _band(b, dim=1.0):
    b *= dim
    return 0 if b < 0.10 else 1 if b < 0.30 else 2 if b < 0.62 else 3 if b < 0.93 else 4


class Figure:
    """Pixels keyed (x, y) in painter's order: later parts cover earlier.
    ``body`` is the figure, the silhouette `gaps` measures; ``back`` is what
    stands behind it (a pole), painted first and outlined on its own."""

    def __init__(self):
        self.body = {}
        self.back = {}
        self._into = self.body

    # 1.31.0's name for the body's pixels
    @property
    def px(self):
        return self.body

    def behind(self):
        self._into = self.back
        return self

    def front(self):
        self._into = self.body
        return self

    def _put(self, x, y, ramp, i):
        self._into[(x, y)] = (ramp, i)

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
                self._put(x, y, ramp, _band(bright, dim))

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
                self._put(x, y, ramp, _band(bright, dim))

    def dot(self, x, y, rgb):
        self._into[(int(math.floor(x)), int(math.floor(y)))] = ((rgb,) * 5, 0)

    def silhouette(self):
        """The body's pixels and its final line: what a black fill shows."""
        return set(self.body) | _ring(self.body)

    def paint(self, c, outline=OUTLINE):
        """Onto a Canvas: what stands behind, then the figure, each with its
        final line -- near-black against a form's shadow side, the form's own
        dark against its lit side. Returns the body's drawn box (x0, y0, x1,
        y1), outline included."""
        for layer in (self.back, self.body):
            for (x, y), (ramp, i) in layer.items():
                c.px(x, y, ramp[i])
            for (x, y) in _ring(layer):
                c.px(x, y, _line_at(layer, x, y, outline))
        ring = _ring(self.body)
        xs = [x for x, _ in ring]
        ys = [y for _, y in ring]
        return (min(xs), min(ys), max(xs) + 1, max(ys) + 1) if xs else None


_N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _ring(layer):
    ring = set()
    for (x, y) in layer:
        for dx, dy in _N4:
            q = (x + dx, y + dy)
            if q not in layer:
                ring.add(q)
    return ring


def _line_at(layer, x, y, outline):
    """Near-black unless every form this line pixel touches is lit (band 3 or
    4); then that form's own second value, so a lit edge reads as the form
    turning rather than as a drawn border."""
    touching = [layer[(x + dx, y + dy)] for dx, dy in _N4 if (x + dx, y + dy) in layer]
    if touching and all(i >= 3 for _r, i in touching):
        return touching[0][0][1]
    return outline


# --- the poses ---------------------------------------------------------------------------
#
# Each is a joint table in pose units, drawn back to front. What they share --
# the torso's curves, the bust and its cleft, the two-cup top, the head -- is
# `_torso` and `_head`, placed by the pose.

def _torso(cap, ell, dot, k, ribs, pelvis, lean, hip_tilt, shoulders, suit, skin):
    """The three masses with their curves: ribcage, a narrow waist, a wide
    pelvis; the bust as two masses, the cleft between them, then the top.
    ``ribs``/``pelvis`` are centres; ``lean`` tilts the ribcage, ``hip_tilt``
    the pelvis (the opposed tilts); ``shoulders`` the two shoulder points."""
    (rx, ry), (px, py) = ribs, pelvis
    ell((rx, ry), 4.0, 5.4, skin, lean)
    cap((rx + 0.2, ry + 4.0), (px - 0.2, py - 3.4), 2.4, 2.3, skin)        # the waist, narrow
    ell((px, py), 5.9, 4.2, skin, hip_tilt)                                  # the pelvis, wide
    (sax, say), (sbx, sby) = shoulders
    cap((sax, say), (sbx, sby), 1.4, 1.4, skin)
    # the bust: two masses, the far one a touch lower with the shoulder line
    drop = (sby - say) * 0.2
    lx, rx2 = rx - 2.0, rx + 2.2
    ell((lx, ry + 0.2 - drop), 2.25, 2.0, skin)
    ell((rx2, ry + 0.2 + drop), 2.25, 2.0, skin)
    # the cleft: a short dark line between them, from where the masses meet
    # down into the top (a first cut began it lower and the cups hid it)
    cx = (lx + rx2) / 2.0
    y = ry - 1.7
    while y < ry + 0.9:
        dot(cx, y, skin[0])
        y += 1.0 / k
    # the top: two cups and the gore between, over the lower half of the bust
    cap((lx - 1.8, ry + 1.6 - drop), (lx + 1.3, ry + 1.8 - drop), 1.3, 1.2, suit)
    cap((rx2 - 1.3, ry + 1.8 + drop), (rx2 + 1.8, ry + 1.6 + drop), 1.2, 1.3, suit)
    # the bottoms, following the pelvis's tilt
    t = math.tan(hip_tilt)
    cap((px - 4.6, py + 0.4 - 4.6 * t), (px + 4.2, py - 0.6 + 4.2 * t), 1.25, 1.25, suit)
    cap((px - 0.6, py + 0.4), (px + 0.6, py + 2.8), 1.5, 0.9, suit)


def _line(dot, a, b, k, rgb):
    """A one-pixel line in pose units: a strap, a tie."""
    (ax, ay), (bx, by) = a, b
    n = max(1, int(math.ceil(math.hypot(bx - ax, by - ay) * k)))
    for i in range(n + 1):
        t = i / n
        dot(ax + (bx - ax) * t, ay + (by - ay) * t, rgb)


def _straps(dot, k, ribs, pelvis, hip_tilt, shoulders, neck, suit):
    """The halter: each cup's strap up to the side of the neck; the bottom's
    ties at the hips, where its band ends. Drawn after the head, so a strap
    passes over the neck rather than under it."""
    (rx, ry), (px, py), (nx, ny) = ribs, pelvis, neck
    (sax, say), (sbx, sby) = shoulders
    drop = (sby - say) * 0.2
    lx, rx2 = rx - 2.0, rx + 2.2
    _line(dot, (lx - 0.6, ry - 0.4 - drop), (nx - 1.0, ny + 1.4), k, suit[1])
    _line(dot, (rx2 + 0.6, ry - 0.4 + drop), (nx + 1.2, ny + 1.4), k, suit[1])
    t = math.tan(hip_tilt)
    for side, x in ((-1, px - 4.8), (1, px + 4.4)):
        y = py + 0.4 - 4.8 * t if side < 0 else py - 0.6 + 4.4 * t
        _line(dot, (x, y), (x + 0.5 * side, y + 1.6), k, suit[1])


def _head(cap, ell, dot, neck, head, turn, hair, skin):
    (nx, ny) = neck
    (hx, hy) = head
    cap((nx, ny), (nx + 0.2, ny + 3.2), 1.3, 1.45, skin)
    ell((hx, hy), 2.9, 3.7, skin, turn)
    ell((hx + 0.6, hy - 1.7), 3.4, 2.6, hair, turn + 0.08)
    dot(hx - 1.2, hy + 0.1, OUTLINE)
    dot(hx + 0.9, hy + 0.1, OUTLINE)
    dot(hx - 0.3, hy + 2.1, LIPS)
    dot(hx + 0.4, hy + 2.1, LIPS)


def _behind_head(cap, ell, dot, k, suit, hair, skin):
    """1.31.0's pose, reopened: contrapposto, the weight on the +x leg, the
    far hand behind the head, the near hand on the high hip -- its elbow now
    well out from the waist -- and the free leg's knee turned in but its
    shin angled away, so a wedge of ground shows between the legs."""
    cap((-4.6, 11.2), (-6.6, 3.0), 1.35, 1.1, skin, FAR)                  # far arm, up
    cap((-6.6, 3.0), (-2.4, 1.6), 1.05, 0.85, skin, FAR)
    cap((1.2, 3.0), (2.6, 12.5), 3.2, 1.6, hair)                          # hair behind
    cap((-2.8, 30.0), (-1.4, 43.4), 2.7, 1.6, skin, FAR)                  # free leg
    cap((-1.4, 43.4), (-5.2, 55.0), 1.6, 0.9, skin, FAR)
    cap((-5.2, 55.0), (-4.8, 57.8), 0.9, 0.7, suit, FAR)                  # its heel, lifted
    _torso(cap, ell, dot, k, (0.2, 15.2), (1.2, 27.0), -0.16, 0.24,
           ((-4.6, 11.0), (4.8, 12.6)), suit, skin)
    cap((3.4, 28.6), (2.8, 44.0), 3.0, 1.7, skin)                         # standing leg
    cap((2.8, 44.0), (1.6, 56.8), 1.7, 0.95, skin)
    cap((1.6, 56.8), (3.0, 59.0), 0.95, 0.8, suit)
    cap((4.8, 12.6), (9.0, 18.8), 1.35, 1.1, skin)                        # near arm, elbow OUT
    cap((9.0, 18.8), (6.0, 25.0), 1.05, 0.8, skin)
    _head(cap, ell, dot, (0.2, 6.8), (0.0, 3.9), 0.12, hair, skin)
    _straps(dot, k, (0.2, 15.2), (1.2, 27.0), 0.24, ((-4.6, 11.0), (4.8, 12.6)), (0.2, 6.8), suit)


def _pole(cap, ell, dot, k, suit, hair, skin, fig, pole_top=-8.0):
    """The pole lean: the far hand high on the pole, the weight on the far
    leg beside it, the near knee lifted out to the side and its foot tucked
    to the standing knee -- a triangle of ground between the legs that reads
    at any size -- and the near hand on the lifted thigh."""
    fig.behind()
    cap((-7.6, pole_top), (-7.6, 59.6), 0.8, 0.8, POLE)                  # to the stage
    fig.front()
    cap((-4.4, 11.6), (-7.0, 5.0), 1.35, 1.1, skin, FAR)                  # far arm up the pole
    cap((-7.0, 5.0), (-7.4, -0.6), 1.05, 0.85, skin, FAR)
    ell((-7.4, -0.8), 1.1, 1.0, skin, 0.0, FAR)                           # the grip
    cap((-2.4, 3.2), (-3.4, 12.0), 3.0, 1.5, hair)                        # hair falling to the pole side
    cap((-3.2, 28.8), (-2.8, 44.0), 3.0, 1.7, skin, FAR)                  # standing leg, by the pole
    cap((-2.8, 44.0), (-2.2, 56.8), 1.7, 0.95, skin, FAR)
    cap((-2.2, 56.8), (-0.8, 59.0), 0.95, 0.8, suit, FAR)
    _torso(cap, ell, dot, k, (-0.4, 15.2), (-0.6, 27.0), 0.14, -0.22,
           ((-4.4, 12.4), (4.6, 11.4)), suit, skin)
    cap((3.0, 29.4), (8.0, 38.4), 2.9, 1.8, skin)                         # near thigh, lifted out
    cap((8.0, 38.4), (0.6, 45.8), 1.7, 1.0, skin)                         # shin back to the standing knee
    cap((0.6, 45.8), (-0.8, 47.2), 0.95, 0.8, suit)                       # the heel
    cap((4.6, 11.4), (8.6, 17.8), 1.35, 1.1, skin)                        # near arm, down to the thigh
    cap((8.6, 17.8), (8.4, 26.8), 1.05, 0.85, skin)
    _head(cap, ell, dot, (-0.2, 6.8), (0.2, 3.9), -0.14, hair, skin)
    _straps(dot, k, (-0.4, 15.2), (-0.6, 27.0), -0.22, ((-4.4, 12.4), (4.6, 11.4)), (-0.2, 6.8), suit)


def _akimbo(cap, ell, dot, k, suit, hair, skin):
    """Hands on hips, both elbows out -- two triangles of ground at the waist
    -- feet apart, the hip cocked to the standing side and the head tilted
    against it. The elbows sit at different heights so the arms are not a
    pair of brackets (the guide: "make the two sides do different jobs")."""
    cap((1.0, 3.0), (2.4, 12.0), 3.2, 1.6, hair)                          # hair behind
    cap((-4.6, 11.4), (-9.0, 16.4), 1.35, 1.1, skin, FAR)                 # far arm, elbow out and high
    cap((-9.0, 16.4), (-5.2, 24.2), 1.05, 0.8, skin, FAR)
    cap((-2.8, 30.0), (-4.8, 43.8), 2.9, 1.6, skin, FAR)                  # free leg, out
    cap((-4.8, 43.8), (-5.4, 55.4), 1.6, 0.9, skin, FAR)
    cap((-5.4, 55.4), (-4.4, 57.8), 0.9, 0.7, suit, FAR)
    _torso(cap, ell, dot, k, (0.0, 15.2), (0.8, 27.0), -0.10, 0.26,
           ((-4.6, 11.2), (4.8, 12.4)), suit, skin)
    cap((3.4, 28.6), (4.2, 44.0), 3.0, 1.7, skin)                         # standing leg
    cap((4.2, 44.0), (4.0, 56.8), 1.7, 0.95, skin)
    cap((4.0, 56.8), (5.4, 59.0), 0.95, 0.8, suit)
    cap((4.8, 12.4), (9.6, 19.4), 1.35, 1.1, skin)                        # near arm, elbow out and low
    cap((9.6, 19.4), (5.8, 25.6), 1.05, 0.8, skin)
    _head(cap, ell, dot, (0.0, 6.8), (-0.3, 3.9), -0.18, hair, skin)
    _straps(dot, k, (0.0, 15.2), (0.8, 27.0), 0.26, ((-4.6, 11.2), (4.8, 12.4)), (0.0, 6.8), suit)


POSES = ("behind_head", "pole", "akimbo")

#: The gaps each pose must keep, as bands of pose rows (y from the top of the
#: head, 60 to the heel) in which the black silhouette splits into two or more
#: runs: the ground seen between an elbow and the waist, or between the legs.
#: The figure guide's silhouette test, made a measurement.
GAPS = {
    "behind_head": {"near arm": (17.5, 23.0), "legs": (47.0, 55.0)},
    "pole": {"near arm": (17.0, 24.0), "legs": (33.0, 43.0)},
    "akimbo": {"elbows": (16.5, 22.5), "legs": (44.0, 55.0)},
}


def pinup(fig, cx, top, height, mirror=False, suit=SUIT, hair=HAIR, skin=SKIN, pose="behind_head",
          pole_from=None):
    """THE POSE, authored. ``top`` is the top of the head, ``height`` the
    figure's height in pixels; ``pose`` one of `POSES`. ``pole_from`` is the
    canvas row a pole starts at (a poster passes the foot of its headline, so
    the pole never crosses the title); by default a little over the head."""
    if pose not in POSES:
        raise ValueError(f"no pose {pose!r}; the poses are {', '.join(POSES)}")
    k = height / POSE_HEIGHT
    sx = -1.0 if mirror else 1.0

    def P(x, y):
        return (cx + sx * x * k, top + y * k)

    def cap(a, b, r0, r1, ramp, dim=1.0):
        fig.capsule(P(*a), P(*b), r0 * k, r1 * k, ramp, dim)

    def ell(c, rx, ry, ramp, tilt=0.0, dim=1.0):
        fig.ellipsoid(P(*c), rx * k, ry * k, ramp, tilt=tilt * sx, dim=dim)

    def dot(x, y, rgb):
        fig.dot(*P(x, y), rgb)

    if pose == "pole":
        _pole(cap, ell, dot, k, suit, hair, skin, fig,
              -8.0 if pole_from is None else min(-2.0, (pole_from - top) / k))
    elif pose == "akimbo":
        _akimbo(cap, ell, dot, k, suit, hair, skin)
    else:
        _behind_head(cap, ell, dot, k, suit, hair, skin)
    return fig


def gaps(fig, top, height, pose):
    """``{gap name: fraction of its band's rows where the silhouette splits}``
    for a figure `pinup` drew with this ``top``, ``height`` and ``pose``. A
    measurement; it passes nothing."""
    sil = fig.silhouette()
    k = height / POSE_HEIGHT
    out = {}
    for name, (y0, y1) in GAPS[pose].items():
        rows = range(int(math.ceil(top + y0 * k)), int(math.floor(top + y1 * k)) + 1)
        split = 0
        for y in rows:
            xs = sorted(x for (x, yy) in sil if yy == y)
            runs = 1 + sum(1 for a, b in zip(xs, xs[1:]) if b - a > 1) if xs else 0
            split += runs >= 2
        out[name] = round(split / max(1, len(rows)), 3)
    return out
