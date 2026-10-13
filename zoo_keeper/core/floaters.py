"""Floaters: details laid ON a surface, not cut into it (1.106.0, factory roadmap 234; the README's "Floaters").

The README names the rule; this is its arithmetic, so a recipe asks one place where a detail goes instead of
choosing its own number. Each species so far chose: `flat_forms.JOIN` and `pack_wall_forms.JOIN` bury 4 mm,
`back_bar_forms.JOIN` and `crt_forms.STAND_BURY` 6 mm, `counter_register.PROUD` and
`dartboard_forms.RING_PROUD` stand 3 mm off, `flat_forms.ART_PROUD` 5 mm.

A floater is built in its OWN frame: Z up, its base at z = 0. `frame` carries that frame onto a host: +Z
along the host face's normal, turned about it, its origin on the host point, moved along the normal by an
offset. A SOLID floater rests, lowered `FLOATER_SKIRT` into its host (`solid_frame`); a FLAT floater hovers,
one-sided, `FLOATER_PROUD` off it (`flat_quad`).

PURE PYTHON, so the suite checks it without Blender. `bpylayer.geometry.add_floater` and `add_flat_floater`
build with it.
"""
from __future__ import annotations

import math

#: The coplanar census's window (`tools/coplanar_probe.py`'s --tol, `tests/test_coincident_faces.PROBE_TOL`):
#: two faces nearer than this are a coincident pair.
PROBE_WINDOW = 0.002
#: A SOLID FLOATER RESTS: only a skirt goes below the host plane -- past the census's window, and as little more
#: as covers the junction. Zoo's JOIN.
FLOATER_SKIRT = 0.004
#: A FLAT FLOATER HOVERS this far off its host. Godot's default 24-bit depth buffer, near 0.05 and far 4000,
#: resolves a gap g out to sqrt(g x 838,871) metres (`tests/test_coincident_faces.fight_distance_m`), so 3 mm
#: fights only beyond 50 m, where a prop-sized detail is a pixel or two. Flatter than this is texture.
FLOATER_PROUD = 0.003
#: How near (|cos|) world X may lie to the normal before the frame is begun from world Y instead, so it never
#: crosses a vector with itself.
_PARALLEL = 0.9


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    if n < 1e-12:
        raise ValueError("a floater needs its host's normal, not a zero vector: %r" % (v,))
    return tuple(c / n for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def basis(normal, spin=0.0):
    """``(x, y, z)``: a right-handed orthonormal frame whose z is the unit `normal`, its x and y turned `spin`
    radians about it. Deterministic: the unturned x is world X with its part along the normal taken out, or
    world Y where the normal lies near X."""
    z = _unit(normal)
    ref = (1.0, 0.0, 0.0) if abs(z[0]) < _PARALLEL else (0.0, 1.0, 0.0)
    d = _dot(ref, z)
    x = _unit(tuple(r - d * c for r, c in zip(ref, z)))
    y = _cross(z, x)
    c, s = math.cos(spin), math.sin(spin)
    return (tuple(c * a + s * b for a, b in zip(x, y)),
            tuple(c * b - s * a for a, b in zip(x, y)), z)


def frame(point, normal, spin=0.0, offset=0.0):
    """The 4 x 4 matrix, as rows, that carries a floater's own frame onto its host: its +Z along the host's
    `normal`, turned `spin` radians about it, its origin at `point` moved `offset` along the normal -- out of
    the host when positive, into it when negative."""
    x, y, z = basis(normal, spin)
    t = tuple(p + offset * c for p, c in zip(point, z))
    return [[x[0], y[0], z[0], t[0]],
            [x[1], y[1], z[1], t[1]],
            [x[2], y[2], z[2], t[2]],
            [0.0, 0.0, 0.0, 1.0]]


def apply(m, p):
    """`p`, a point in a floater's own frame, in its host's."""
    return tuple(m[r][0] * p[0] + m[r][1] * p[1] + m[r][2] * p[2] + m[r][3] for r in range(3))


def solid_frame(point, normal, spin=0.0, skirt=FLOATER_SKIRT):
    """`frame` for a SOLID floater: its base, z = 0 in its own frame, lowered `skirt` into the host."""
    if skirt < 0.0:
        raise ValueError("a skirt goes into the host, not out of it: %r" % skirt)
    return frame(point, normal, spin, -float(skirt))


def flat_quad(point, normal, w, h, spin=0.0, proud=FLOATER_PROUD):
    """A FLAT floater's four corners: a `w` x `h` quad centred on `point` and standing `proud` off the host
    along `normal`, its width along the turned x. Wound counter-clockwise seen from the normal's side, so the
    face made from them faces along `normal`."""
    if proud <= 0.0:
        raise ValueError("a flat floater stands off its host: %r" % proud)
    m = frame(point, normal, spin, float(proud))
    hw, hh = 0.5 * float(w), 0.5 * float(h)
    return [apply(m, c) for c in ((-hw, -hh, 0.0), (hw, -hh, 0.0), (hw, hh, 0.0), (-hw, hh, 0.0))]
