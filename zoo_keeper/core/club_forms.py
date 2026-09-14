"""The club species, planned in pure Python: a 1997 Delaware County strip
club's stage, its cocktail tables, tub chairs and bar stools.

REFERENCE (the walker, with two GTA IV Triangle Club frames, and a local
comparison used for layout only): "strip clubs should have a dingy lived in
feel, dark with colored lights, couches and bars". A round raised stage with
a centre pole, a padded rail on brass posts round its edge and a warm rope
light along the lip and the step nosings; a stage that is the middle of the
bar, stools pulled up to a padded bar rail round it; small round tables in
floor-length cloths with a bottle and an ashtray on them; low tub chairs in
worn velvet; chrome stools with a footring. PRE-RENOVATION: nothing here is
a modern refit -- the only light in the furniture is a plain warm rope
light and the neon on the wall (`neon_forms`).

  * ``club_stage`` -- `plan_stage`, forms ``round`` (an ellipse that fills
    the slot, steps at the front), ``runway`` (a platform with a round far
    end and the pole there, steps at the near end) and ``bar_stage`` (an
    oval bar counter whose middle is a raised deck with one or two poles).
  * ``cocktail_table`` -- `plan_table`, forms ``cloth`` and ``bare``.
  * ``club_chair`` -- `plan_chair`, a barrel-backed tub chair.
  * ``bar_stool`` -- `plan_stool`.

THE RULES every planner here keeps (the interior species' rules, see
`booth_forms`): extents exactly w x d x h (`prims.fit_exact` takes a
detail's overshoot back out); parts that meet overlap by a few mm; no two
faces within 2 mm of one plane where they overlap (`prims.coincident_pairs`,
over sizes, forms and seeds, in the tests); deterministic from the rng
passed in.

TUBES AND COINCIDENT FACES. Every rail, rope light and footring is a chain
of `prims.rod` segments with EIGHT sides. A horizontal eight-sided rod has
no face whose normal is vertical (its facets sit 22.5 degrees off the
vertical), so two consecutive segments that overlap at a joint -- whose
facets are otherwise turned apart by the bend -- can never share their top
or bottom plane. Six sides were not used for exactly that reason: a
six-sided horizontal rod has a flat top, and every joint of a ring of them
would be one SAME pair.

Frame: metres, Z up, base-up, length along x, the front toward -Y.
"""
from __future__ import annotations

import math

from . import prims as P

# --- shared outline helpers ---------------------------------------------------


def ellipse_poly(cx, cy, rx, ry, n, phase=0.0):
    """A CCW n-gon whose vertices lie on the ellipse."""
    return [(cx + rx * math.cos(phase + 2.0 * math.pi * k / n),
             cy + ry * math.sin(phase + 2.0 * math.pi * k / n)) for k in range(n)]


def stadium_poly(x0, x1, y0, y1, n_end):
    """A CCW stadium filling the rectangle: the long axis straight, both
    short ends semicircles of ``n_end`` segments."""
    w, d = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    out = []
    if w >= d:
        r = d / 2.0
        for k in range(n_end + 1):          # right end, -90 .. 90
            a = -math.pi / 2.0 + math.pi * k / n_end
            out.append((x1 - r + r * math.cos(a), cy + r * math.sin(a)))
        for k in range(n_end + 1):          # left end, 90 .. 270
            a = math.pi / 2.0 + math.pi * k / n_end
            out.append((x0 + r + r * math.cos(a), cy + r * math.sin(a)))
    else:
        r = w / 2.0
        for k in range(n_end + 1):          # top end, 0 .. 180
            a = math.pi * k / n_end
            out.append((cx + r * math.cos(a), y1 - r + r * math.sin(a)))
        for k in range(n_end + 1):          # bottom end, 180 .. 360
            a = math.pi + math.pi * k / n_end
            out.append((cx + r * math.cos(a), y0 + r + r * math.sin(a)))
    return _dedupe(out)


def runway_poly(x0, x1, y0, y1, n_end):
    """A CCW platform with square corners at ``x0`` and a semicircular end
    at ``x1`` (radius half the depth)."""
    d = y1 - y0
    r = d / 2.0
    cy = (y0 + y1) / 2.0
    out = [(x0, y0)]
    for k in range(n_end + 1):
        a = -math.pi / 2.0 + math.pi * k / n_end
        out.append((x1 - r + r * math.cos(a), cy + r * math.sin(a)))
    out.append((x0, y1))
    return _dedupe(out)


def runway_poly_y(x0, x1, y0, y1, n_end):
    """`runway_poly` turned to run along +Y: square corners at ``y0`` (the
    front, where the steps are) and a semicircular end at ``y1``."""
    w = x1 - x0
    r = w / 2.0
    cx = (x0 + x1) / 2.0
    out = [(x0, y0), (x1, y0)]
    for k in range(n_end + 1):
        a = math.pi * k / n_end
        out.append((cx + r * math.cos(a), y1 - r + r * math.sin(a)))
    return _dedupe(out)


def _dedupe(pts, eps=1e-9):
    out = []
    for p in pts:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > eps:
            out.append(p)
    if len(out) > 1 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= eps:
        out.pop()
    return out


def inset_poly(poly, dist):
    """A convex CCW polygon moved ``dist`` inward along its edge normals
    (negative grows it). Same vertex count, each vertex the meeting of its
    two offset edges."""
    n = len(poly)
    lines = []
    for k in range(n):
        (x0, y0), (x1, y1) = poly[k], poly[(k + 1) % n]
        ex, ey = x1 - x0, y1 - y0
        ln = math.hypot(ex, ey)
        nx, ny = -ey / ln, ex / ln               # left of a CCW edge: inside
        lines.append(((x0 + nx * dist, y0 + ny * dist), (ex / ln, ey / ln), (nx, ny)))
    out = []
    for k in range(n):
        (pa, da, na), (pb, db, nb) = lines[k - 1], lines[k]
        den = da[0] * db[1] - da[1] * db[0]
        if abs(den) < 1e-9:
            x, y = poly[k]
            out.append((x + nb[0] * dist, y + nb[1] * dist))
            continue
        t = ((pb[0] - pa[0]) * db[1] - (pb[1] - pa[1]) * db[0]) / den
        out.append((pa[0] + da[0] * t, pa[1] + da[1] * t))
    return out


def poly_width_at(poly, y):
    """(xmin, xmax) of a convex polygon's chord at height ``y``, or None."""
    xs = []
    n = len(poly)
    for k in range(n):
        (x0, y0), (x1, y1) = poly[k], poly[(k + 1) % n]
        if (y0 - y) * (y1 - y) <= 0.0 and abs(y1 - y0) > 1e-12:
            t = (y - y0) / (y1 - y0)
            xs.append(x0 + (x1 - x0) * t)
    if len(xs) < 2:
        return None
    return min(xs), max(xs)


def ring_solid(part, mat, outer, inner, z0, z1, bevel=False):
    """A closed annular solid between two CCW polygons of the same count."""
    n = len(outer)
    assert len(inner) == n
    verts = ([(x, y, z0) for x, y in outer] + [(x, y, z1) for x, y in outer]
             + [(x, y, z0) for x, y in inner] + [(x, y, z1) for x, y in inner])
    ob, ot, ib, it = 0, n, 2 * n, 3 * n
    faces = []
    for k in range(n):
        k1 = (k + 1) % n
        faces.append((ob + k, ob + k1, ot + k1, ot + k))         # outer wall
        faces.append((ib + k1, ib + k, it + k, it + k1))         # inner wall
        faces.append((ot + k, ot + k1, it + k1, it + k))         # top
        faces.append((ob + k1, ob + k, ib + k, ib + k1))         # bottom
    return P.mesh(part, mat, verts, faces, bevel)


def tube_path(part, mat, pts, r, closed=False, segments=8):
    """Rods along a 3D polyline, each segment its own eight-sided rod,
    lengthened at an inner joint by ``r * tan(bend / 2)`` plus 3 mm so the
    outside of the bend has no notch. Consecutive COLLINEAR points must have
    been merged by the caller (`merge_collinear`): two collinear rods of one
    phase lay their facets in one plane where they overlap."""
    n = len(pts)
    segs = [(k, (k + 1) % n) for k in range(n if closed else n - 1)]
    out = []
    for i, j in segs:
        a, b = pts[i], pts[j]
        d = _unit3(_sub3(b, a))
        ea = eb = 0.0
        if closed or i > 0:
            prev = pts[(i - 1) % n]
            ea = _joint_ext(_unit3(_sub3(a, prev)), d, r)
        if closed or j < n - 1:
            nxt = pts[(j + 1) % n]
            eb = _joint_ext(d, _unit3(_sub3(nxt, b)), r)
        p0 = (a[0] - d[0] * ea, a[1] - d[1] * ea, a[2] - d[2] * ea)
        p1 = (b[0] + d[0] * eb, b[1] + d[1] * eb, b[2] + d[2] * eb)
        out.append(P.rod(part, mat, p0, p1, r, segments=segments))
    return out


def merge_collinear(pts, closed=False, tol=1e-6):
    """Drop every point that lies on the straight line through its
    neighbours."""
    n = len(pts)
    keep = []
    for k in range(n):
        if not closed and (k == 0 or k == n - 1):
            keep.append(pts[k])
            continue
        a, b, c = pts[k - 1], pts[k], pts[(k + 1) % n]
        u, v = _unit3(_sub3(b, a)), _unit3(_sub3(c, b))
        cr = _cross3(u, v)
        if math.sqrt(sum(x * x for x in cr)) > tol:
            keep.append(b)
    return keep


def _joint_ext(d0, d1, r):
    cosb = max(-1.0, min(1.0, sum(a * b for a, b in zip(d0, d1))))
    bend = math.acos(cosb)
    return r * math.tan(min(bend, math.radians(80.0)) / 2.0) + 0.003


def _sub3(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross3(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit3(v):
    ln = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    return (v[0] / ln, v[1] / ln, v[2] / ln)


def _overshoot(prims, w, d, h):
    lo, hi = P.bounds(prims)
    return max(abs(lo[0] + w / 2), abs(hi[0] - w / 2), abs(lo[1] + d / 2),
               abs(hi[1] - d / 2), abs(lo[2]), abs(hi[2] - h))


def _finish(prims, cboxes, w, d, h):
    over = _overshoot(prims, w, d, h)
    prims, cboxes = P.fit_exact(prims, (-w / 2, -d / 2, 0.0), (w / 2, d / 2, h), cboxes)
    return prims, cboxes, over


# --- club_stage ------------------------------------------------------------------

STAGE_FORMS = ("round", "runway", "bar_stage")
#: ``auto`` is ``round`` up to this long-to-short ratio of the platform
#: (after the steps), ``runway`` past it. Never ``bar_stage``: a stage in the
#: middle of a bar is a different room, and only the room's author knows it.
AUTO_ROUND_ASPECT = 1.4

#: A stage slot no taller than this IS the platform (Deli Counter's strip
#: club volumes are 0.8 m today: `strip_club_a01` 8 x 4 x 0.8).
PLATFORM_MAX = 0.9
#: The platform when the slot is taller -- when the volume is authored to
#: the ceiling so the pole has somewhere to go. Deli Counter's own stage
#: height, so the greybox's collider and the deck agree.
PLATFORM_TALL = 0.8
#: The padded rail's top above the deck.
RAIL_RISE = 0.36
RAIL_R = 0.04            # padded rail tube radius
RAIL_IN = 0.12           # rail centre inside the platform edge
POST_R = 0.02
COLLAR_R = 0.035
POST_SPACING = 1.1

#: STEPS. The number is derived, not chosen: a smooth collider over them is
#: what a body walks (Deli Counter gives stairs a ramp, see the agent
#: contract's `agent_max_climb_derivation`), and a ramp is walkable only up to
#: `floor_max_angle`, 45 degrees. The ramp from the front of the lowest tread
#: to the platform edge rises ``p`` over ``n * TREAD``; n is the fewest steps
#: that keep it at or under MAX_PITCH_DEG, at most three.
TREAD = 0.34
MAX_PITCH_DEG = 44.0
MAX_STEPS = 3
STEP_W = 1.0

LIP_T = 0.06
CARPET_T = 0.03
ROPE_R = 0.01

POLE_R = 0.025
FLANGE_R = 0.075

#: bar_stage heights: a bar top at bar height and the deck a hand above it
BAR_DECK = 1.18
BAR_TOP_BELOW_DECK = 0.11
BAR_POLE_MIN = BAR_DECK + 0.3
BAR_BAND = 0.62          # armrest outer edge to the deck
ARM_R = 0.045            # padded armrest
FOOT_R = 0.022
FOOT_Z = 0.20
FASCIA_IN = 0.17
KICK_IN = 0.22
KICK_H = 0.105

#: material key -> (linear RGB, kind). "fascia" is the genome's colour and kind.
STAGE_MATERIALS = {
    "trim": ([0.06, 0.04, 0.028], "wood"),        # lip, kick, bar top edge
    "bartop": ([0.10, 0.06, 0.035], "wood"),
    "carpet": ([0.20, 0.035, 0.09], "carpet"),     # worn wine carpet
    "pad": ([0.19, 0.06, 0.05], "leather"),       # padded rail and armrest
    "brass": ([0.60, 0.43, 0.15], "metal_bare"),
    "chrome": ([0.78, 0.79, 0.80], "metal_bare"),
}
#: emissive key -> (linear RGB, strength): a plain warm rope light. REFUTED
#: FIRST at 3.0: the Godot walk's frames clipped it to a white line
STAGE_EMISSIVE = {"rope": ([1.0, 0.62, 0.28], 1.0)}


def stage_heights(h):
    """``(platform, rail_top or None, pole_top or None)`` for a slot ``h`` tall.

    * h <= PLATFORM_MAX: the slot is the platform; no rail, no pole.
    * up to PLATFORM_TALL + RAIL_RISE: the platform is h - RAIL_RISE and the
      rail's top is the slot's top; no pole.
    * taller: the platform is PLATFORM_TALL, the rail RAIL_RISE above it and
      the pole runs to the slot's top -- author the volume to the ceiling.
    """
    if h <= PLATFORM_MAX:
        return h, None, None
    if h <= PLATFORM_TALL + RAIL_RISE:
        return h - RAIL_RISE, h, None
    return PLATFORM_TALL, PLATFORM_TALL + RAIL_RISE, h


def n_steps(p):
    k = math.ceil(p / (TREAD * math.tan(math.radians(MAX_PITCH_DEG))) - 1e-9)
    return max(1, min(MAX_STEPS, int(k)))


def step_pitch_deg(p):
    return math.degrees(math.atan2(p, n_steps(p) * TREAD))


def pick_stage_form(form, w, d, h):
    if form in STAGE_FORMS:
        return form
    p = stage_heights(h)[0]
    deep = d - n_steps(p) * TREAD
    return "round" if max(w, deep) / max(1e-6, min(w, deep)) <= AUTO_ROUND_ASPECT else "runway"


def plan_stage(w, d, h, rng, form="auto"):
    """``{"prims", "collision", "form", "platform", "rail_top", "pole_top",
    "poles", "steps", "pitch_deg", "stock_regions", "overshoot_m"}``."""
    form = pick_stage_form(form, w, d, h)
    if form == "bar_stage":
        got = _bar_stage(w, d, h, rng)
    else:
        got = _platform_stage(w, d, h, rng, form)
    prims, cboxes, over = _finish(got["prims"], got["collision"], w, d, h)
    got.update(prims=prims, collision=cboxes, form=form, overshoot_m=over)
    return got


def _post(prims, x, y, p, z_top, yaw):
    """A brass post and its collar, a VERTEX of each turned along the rail
    (``yaw``). REFUTED FIRST: posts at phase 0, whose facets face 22.5 + 45k
    degrees -- on a runway's round end a rail chord runs at 22.5 degrees and
    a rail segment's end cap lay 0.44 mm from a post facet."""
    prims.append(P.cyl("Stage_RailPosts", "brass", (x, y), POST_R, p - 0.012, z_top,
                       segments=8, phase=yaw))
    prims.append(P.cyl("Stage_RailPosts", "brass", (x, y), COLLAR_R, p - 0.003, p + 0.05,
                       segments=8, phase=yaw + math.pi / 8.0))


def _pole(prims, x, y, z0, z1):
    prims.append(P.cyl("Stage_Pole", "chrome", (x, y), FLANGE_R, z0 - 0.004, z0 + 0.012,
                       segments=16))
    prims.append(P.cyl("Stage_Pole", "chrome", (x, y), POLE_R, z0 - 0.02, z1 - 0.004,
                       segments=12))
    prims.append(P.cyl("Stage_Pole", "chrome", (x, y), FLANGE_R, z1 - 0.014, z1,
                       segments=16))


def _open_rail(poly, excluded):
    """The kept edges of a closed polygon as one open polyline, starting
    after the first excluded run. ``excluded(k)`` says whether edge k (from
    vertex k to k + 1) carries no rail."""
    n = len(poly)
    flags = [bool(excluded(k)) for k in range(n)]
    if all(flags):
        return []
    if not any(flags):
        return list(poly) + [poly[0]]
    start = next(k for k in range(n) if flags[k - 1] and not flags[k])
    path = [poly[start]]
    k = start
    while not flags[k % n]:
        path.append(poly[(k + 1) % n])
        k += 1
        if k - start >= n:
            break
    return path


def _clip_front(poly, x_lo, x_hi, y_mid):
    """Split every front edge (below ``y_mid``) of a polygon at x_lo and
    x_hi, so an excluded gap can be exactly the steps' width."""
    out = []
    n = len(poly)
    for k in range(n):
        a, b = poly[k], poly[(k + 1) % n]
        out.append(a)
        if a[1] < y_mid and b[1] < y_mid:
            cuts = []
            for xc in (x_lo, x_hi):
                if (a[0] - xc) * (b[0] - xc) < 0.0:
                    t = (xc - a[0]) / (b[0] - a[0])
                    cuts.append((t, (xc, a[1] + (b[1] - a[1]) * t)))
            for _t, c in sorted(cuts):
                out.append(c)
    return out


def _posts_along(path, spacing):
    """Post positions along an open polyline: both ends, and evenly between
    at no more than ``spacing``; each ``(x, y, yaw)``, the yaw the rail's
    direction there (the mean of both segments' at a joint)."""
    lengths = [math.hypot(path[k + 1][0] - path[k][0], path[k + 1][1] - path[k][1])
               for k in range(len(path) - 1)]
    total = sum(lengths)
    if total <= 1e-9:
        return [(path[0][0], path[0][1], 0.0)]
    count = max(1, int(math.ceil(total / spacing)))
    out = []
    for i in range(count + 1):
        s = total * i / count
        acc = 0.0
        for k, ln in enumerate(lengths):
            if s <= acc + ln + 1e-9 or k == len(lengths) - 1:
                t = 0.0 if ln <= 1e-12 else min(1.0, max(0.0, (s - acc) / ln))
                a, b = path[k], path[k + 1]
                yaw = math.atan2(b[1] - a[1], b[0] - a[0])
                if t >= 1.0 - 1e-9 and k + 1 < len(lengths):
                    c = path[k + 2]
                    yaw2 = math.atan2(c[1] - b[1], c[0] - b[0])
                    yaw = yaw + math.atan2(math.sin(yaw2 - yaw), math.cos(yaw2 - yaw)) / 2
                elif t <= 1e-9 and k > 0:
                    z = path[k - 1]
                    yaw0 = math.atan2(a[1] - z[1], a[0] - z[0])
                    yaw = yaw0 + math.atan2(math.sin(yaw - yaw0), math.cos(yaw - yaw0)) / 2
                out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, yaw))
                break
            acc += ln
    return out


def _platform_stage(w, d, h, rng, form):
    p, rail_top, pole_top = stage_heights(h)
    n = n_steps(p)
    run = n * TREAD
    y0 = -d / 2 + run
    deep = d - run
    cy = y0 + deep / 2
    sw = min(STEP_W, 0.5 * w)
    if form == "round":
        outline = ellipse_poly(0.0, cy, w / 2, deep / 2, 32)
        step_cx = 0.0
        pole_xy = [(0.0, cy)]
    elif deep <= w:
        n_end = 12
        outline = runway_poly(-w / 2, w / 2, y0, d / 2, n_end)
        step_cx = -w / 2 + min(0.35, 0.1 * w) + sw / 2
        pole_xy = [(w / 2 - deep / 2, cy)]
    else:
        # A RUNWAY RUNS ALONG THE SLOT'S LONG AXIS. REFUTED FIRST: always
        # along x, which in a 2 x 8 m slot gave the round end a 3.5 m radius
        # in a 2 m width -- 2.27 m outside the slot before the fit
        n_end = 12
        outline = runway_poly_y(-w / 2, w / 2, y0, d / 2, n_end)
        step_cx = 0.0
        pole_xy = [(0.0, d / 2 - w / 2)]
    along_y = form == "runway" and deep > w
    prims, cboxes = [], []
    # the body: a recessed fascia, an overhanging lip and a carpeted top
    prims.append(P.prism("Stage_Fascia", "fascia", inset_poly(outline, 0.04), 0.0,
                         p - LIP_T - 0.01, bevel=False))
    prims.append(P.prism("Stage_Lip", "trim", outline, p - LIP_T - 0.015, p - 0.015))
    prims.append(P.prism("Stage_Carpet", "carpet", inset_poly(outline, 0.035),
                         p - CARPET_T, p))
    # the rope light under the lip, 8 mm proud of the fascia
    rope = inset_poly(outline, 0.04 - 0.008)
    zr = p - LIP_T - 0.015 - ROPE_R - 0.012
    prims += tube_path("Stage_RopeLight", "rope",
                       merge_collinear([(x, y, zr) for x, y in rope], closed=True),
                       ROPE_R, closed=True)
    # steps, each a block from the one below to its own tread, reaching past
    # the platform's front; widths and back faces staggered 4 mm per step
    y_back_base = max(front_y_at(outline, step_cx + s * sw / 2) for s in (-1, 0, 1)) + 0.06
    riser = p / (n + 1)
    for k in range(1, n + 1):
        top = k * riser
        # the first step stands 4 mm off the floor: at 0 its bottom lay in
        # the fascia's bottom plane where it reaches under the lip (measured,
        # one SAME pair at every size)
        bottom = 0.004 if k == 1 else (k - 1) * riser - 0.005
        yf = -d / 2 + (k - 1) * TREAD
        half = sw / 2 - 0.004 * (k - 1)
        prims.append(P.box("Stage_Steps", "fascia", (step_cx - half, yf, bottom),
                           (step_cx + half, y_back_base + 0.004 * k, top)))
        prims += tube_path("Stage_RopeLight", "rope",
                           [(step_cx - half + 0.02, yf + ROPE_R - 0.002, top - ROPE_R - 0.004),
                            (step_cx + half - 0.02, yf + ROPE_R - 0.002, top - ROPE_R - 0.004)],
                           ROPE_R)
        cboxes.append(((step_cx - half, yf, 0.0), (step_cx + half, y_back_base, top)))
    # the platform's collider: bands inscribed in the outline
    lo_y, hi_y = min(v[1] for v in outline), max(v[1] for v in outline)
    bands = 5
    for b in range(bands):
        ya, yb = lo_y + (hi_y - lo_y) * b / bands, lo_y + (hi_y - lo_y) * (b + 1) / bands
        ca, cb = poly_width_at(outline, ya + 1e-6), poly_width_at(outline, yb - 1e-6)
        if ca and cb:
            cboxes.append(((max(ca[0], cb[0]), ya, 0.0), (min(ca[1], cb[1]), yb, p)))
    # the padded rail on brass posts, open where the steps come up
    rail_pts, posts = [], []
    if rail_top is not None:
        rail_poly = inset_poly(outline, RAIL_IN)
        gap_lo, gap_hi = step_cx - sw / 2 - 0.22, step_cx + sw / 2 + 0.22
        rail_poly = _clip_front(rail_poly, gap_lo, gap_hi, cy)
        m = len(rail_poly)

        def excluded(k):
            a, b = rail_poly[k], rail_poly[(k + 1) % m]
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            if my < cy and gap_lo < mx < gap_hi:
                return True
            if along_y:
                # the square end is the front, where the steps come up
                return my < y0 + RAIL_IN + 1e-6
            if form == "runway":
                # no rail on the square end (the curtain side), nor on the
                # front before the steps
                if abs(a[0] - b[0]) < 1e-6 and mx < 0.0:
                    return True
                if my < cy and mx <= gap_lo:
                    return True
            return False
        path = _open_rail(rail_poly, excluded)
        zc = rail_top - RAIL_R
        if len(path) >= 2:
            rail_pts = merge_collinear([(x, y, zc) for x, y in path])
            prims += tube_path("Stage_Rail", "pad", rail_pts, RAIL_R)
            posts = _posts_along(path, POST_SPACING)
            for x, y, yaw in posts:
                _post(prims, x, y, p, zc, yaw)
            for (x0, y0_, _z0), (x1, y1, _z1) in zip(rail_pts, rail_pts[1:]):
                segs = max(1, int(math.ceil(math.hypot(x1 - x0, y1 - y0_) / 0.35)))
                for s in range(segs):
                    ax, ay = x0 + (x1 - x0) * s / segs, y0_ + (y1 - y0_) * s / segs
                    bx, by = x0 + (x1 - x0) * (s + 1) / segs, y0_ + (y1 - y0_) * (s + 1) / segs
                    cboxes.append(((min(ax, bx) - RAIL_R, min(ay, by) - RAIL_R, p),
                                   (max(ax, bx) + RAIL_R, max(ay, by) + RAIL_R, rail_top)))
    poles = []
    if pole_top is not None:
        for x, y in pole_xy:
            _pole(prims, x, y, p, pole_top)
            poles.append((x, y))
    return {"prims": prims, "collision": cboxes, "platform": p, "rail_top": rail_top,
            "pole_top": pole_top, "poles": poles, "steps": n, "pitch_deg": step_pitch_deg(p),
            "posts": len(posts), "stock_regions": [], "bar_top": None}


def front_y_at(poly, x):
    """The lowest y where the vertical line at ``x`` meets a convex polygon
    (its front edge there), or the polygon's lowest y when it misses."""
    ys = []
    n = len(poly)
    for k in range(n):
        (x0, y0), (x1, y1) = poly[k], poly[(k + 1) % n]
        if (x0 - x) * (x1 - x) <= 0.0 and abs(x1 - x0) > 1e-12:
            ys.append(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
    return min(ys) if ys else min(v[1] for v in poly)


def _bar_stage(w, d, h, rng):
    # a slot up to BAR_POLE_MIN tall is all counter and deck; taller, the deck
    # is BAR_DECK and the poles run to the slot's top. REFUTED FIRST: a pole
    # only past deck + 0.5, which left a 1.5 m slot 0.32 m short and
    # `fit_exact` stretched the whole bar 27 % taller to fill it
    if h <= BAR_POLE_MIN:
        deck, pole_top = h, None
    else:
        deck, pole_top = BAR_DECK, h
    top = deck - min(BAR_TOP_BELOW_DECK, 0.25 * deck)
    short = min(w, d)
    band = max(0.3, min(BAR_BAND, (short - 0.9) / 2.0))
    n_end = 10
    outer = stadium_poly(-w / 2, w / 2, -d / 2, d / 2, n_end)
    prims, cboxes = [], []
    prims.append(P.prism("Bar_Kick", "trim", inset_poly(outer, KICK_IN), 0.0, KICK_H))
    prims.append(P.prism("Bar_Fascia", "fascia", inset_poly(outer, FASCIA_IN), 0.10,
                         top - 0.04))
    prims.append(ring_solid("Bar_Top", "bartop", inset_poly(outer, 0.02),
                            inset_poly(outer, band), top - 0.045, top))
    arm = inset_poly(outer, ARM_R)
    prims += tube_path("Bar_Armrest", "pad",
                       merge_collinear([(x, y, top + ARM_R - 0.012) for x, y in arm],
                                       closed=True), ARM_R, closed=True)
    foot = inset_poly(outer, 0.12)
    prims += tube_path("Bar_FootRail", "brass",
                       merge_collinear([(x, y, FOOT_Z) for x, y in foot], closed=True),
                       FOOT_R, closed=True)
    # foot rail brackets at every other edge's middle, along the edge normal
    fas = inset_poly(outer, FASCIA_IN)
    m = len(fas)
    for k in range(0, m, 2):
        (ax, ay), (bx, by) = fas[k], fas[(k + 1) % m]
        mx, my = (ax + bx) / 2, (ay + by) / 2
        ex, ey = bx - ax, by - ay
        ln = math.hypot(ex, ey)
        nx, ny = ey / ln, -ex / ln                  # outward
        prims.append(P.rod("Bar_FootRail", "brass", (mx - nx * 0.01, my - ny * 0.01, FOOT_Z),
                           (mx + nx * (FASCIA_IN - 0.12), my + ny * (FASCIA_IN - 0.12), FOOT_Z),
                           0.012, segments=8))
    # the deck: its body from under the bar top, a lip, a carpet, a rope light
    deck_poly = inset_poly(outer, band - 0.012)
    prims.append(P.prism("Stage_Lip", "trim", deck_poly, top - 0.06, deck - 0.012))
    prims.append(P.prism("Stage_Carpet", "carpet", inset_poly(outer, band - 0.012 + 0.03),
                         deck - CARPET_T, deck))
    rope = inset_poly(outer, band - 0.012 - 0.008)
    zr = top + (deck - 0.012 - top) / 2.0
    prims += tube_path("Stage_RopeLight", "rope",
                       merge_collinear([(x, y, zr) for x, y in rope], closed=True),
                       ROPE_R, closed=True)
    # poles along the deck's long axis
    long_ax = 0 if w >= d else 1
    inner_len = (max(w, d) - 2 * band)
    along = [0.0] if inner_len < 3.0 else [-inner_len / 4, inner_len / 4]
    poles = []
    if pole_top is not None:
        for s in along:
            x, y = (s, 0.0) if long_ax == 0 else (0.0, s)
            _pole(prims, x, y, deck, pole_top)
            poles.append((x, y))
    # colliders: the counter as a centre box and banded ends, the deck box
    half_straight = max(w, d) / 2 - short / 2
    if long_ax == 0:
        cboxes.append(((-half_straight, -d / 2, 0.0), (half_straight, d / 2, top)))
        for sx in (-1, 1):
            for b in range(3):
                ya, yb = -d / 2 + d * b / 6, -d / 2 + d * (b + 1) / 6
                c = min(abs(ya), abs(yb))
                ext = math.sqrt(max(0.0, (short / 2) ** 2 - max(abs(ya), abs(yb)) ** 2))
                del c
                x_in, x_out = sorted((sx * half_straight, sx * (half_straight + ext)))
                cboxes.append(((x_in, ya, 0.0), (x_out, yb, top)))
                ya2, yb2 = -ya, -yb
                cboxes.append(((x_in, min(ya2, yb2), 0.0), (x_out, max(ya2, yb2), top)))
        cboxes.append(((-half_straight, -d / 2 + band, top),
                       (half_straight, d / 2 - band, deck)))
    else:
        cboxes.append(((-w / 2, -half_straight, 0.0), (w / 2, half_straight, top)))
        cboxes.append(((-w / 2 + band, -half_straight, top),
                       (w / 2 - band, half_straight, deck)))
    # bar-top stock on the straight runs, facing whoever sits there
    regions = []
    if long_ax == 0 and half_straight > 0.25:
        yi0, yi1 = -d / 2 + 2 * ARM_R + 0.01, -d / 2 + band - 0.03
        if yi1 - yi0 > 0.16:
            regions.append((-half_straight, half_straight, yi0, yi1, top, 0.0))
            regions.append((-half_straight, half_straight, -yi1, -yi0, top, math.pi))
    return {"prims": prims, "collision": cboxes, "platform": deck, "rail_top": None,
            "pole_top": pole_top, "poles": poles, "steps": 0, "pitch_deg": None,
            "posts": 0, "stock_regions": regions, "bar_top": top}


# --- cocktail_table --------------------------------------------------------------

TABLE_FORMS = ("cloth", "bare")
TABLE_TOP_T = 0.03
#: floor-length cloths: burgundy, black, deep green, and a stained cream
CLOTHS = (([0.26, 0.03, 0.05], 3.0), ([0.02, 0.02, 0.025], 2.0),
          ([0.03, 0.12, 0.08], 1.5), ([0.55, 0.47, 0.34], 1.5))
TABLE_MATERIALS = {
    "iron": ([0.03, 0.03, 0.03], "metal_painted"),
}


def pick_table_form(form):
    return form if form in TABLE_FORMS else "cloth"


def plan_table(w, d, h, rng, form="auto"):
    """``{"prims", "collision", "form", "cloth_rgb", "top_z", "top_radius",
    "stock_regions", "overshoot_m"}``; ``stock_regions`` are the two halves
    of the square inscribed in the round top, ``(x0, x1, y0, y1, z0)`` each.

    TWO HALVES, NOT ONE SQUARE: `_surface_stock` sets about one cluster per
    0.22 m2 of bar top, and a 0.75 m table's inscribed square is 0.20 m2 --
    measured over 12 seeds it carried one group every time (a lone ashtray,
    a lone knot of bottles). Split, the same tops carry two groups on 9 of
    12 seeds at 0.75 m, and nothing can cross the split: each half keeps its
    items 2 cm inside its own edges."""
    form = pick_table_form(form)
    rx, ry = w / 2, d / 2
    prims, cboxes = [], []
    pick = rng.uniform(0.0, sum(wt for _c, wt in CLOTHS))
    cloth = CLOTHS[-1][0]
    for c, wt in CLOTHS:
        pick -= wt
        if pick <= 0.0:
            cloth = c
            break
    if form == "bare":
        top = P.cyl("Table_Top", "top", (0.0, 0.0), 1.0, h - TABLE_TOP_T, h, segments=20)
        top["verts"] = [(v[0] * rx, v[1] * ry, v[2]) for v in top["verts"]]
        prims.append(top)
        # an apron ring under the top
        prims.append(_scaled_cyl("Table_Top", "top", 0.78 * rx, 0.78 * ry,
                                 h - TABLE_TOP_T - 0.04, h - TABLE_TOP_T + 0.004, 20,
                                 math.pi / 20))
        # the column starts inside the hub, 6 mm over the base plate's top.
        # REFUTED FIRST: at 0.02 its bottom lay exactly 2.0 mm over that top,
        # which the pure probe passed and Blender's float32 export did not
        prims.append(P.cyl("Table_Base", "iron", (0.0, 0.0), 0.032, 0.024,
                           h - TABLE_TOP_T - 0.036, segments=8))
        base = min(rx, ry) * 0.72
        prims.append(P.cyl("Table_Base", "iron", (0.0, 0.0), base, 0.0, 0.018, segments=16,
                           r_top=base * 0.86))
        prims.append(P.cyl("Table_Base", "iron", (0.0, 0.0), 0.07, 0.014, 0.07, segments=8,
                           phase=math.pi / 8, r_top=0.04))
        top_r = min(rx, ry)
        cboxes.append(((-rx * 0.7, -ry * 0.7, h - TABLE_TOP_T), (rx * 0.7, ry * 0.7, h)))
        cboxes.append(((-0.04, -0.04, 0.0), (0.04, 0.04, h - TABLE_TOP_T)))
    else:
        # the cloth: a flat top, a roll over the table's edge, a skirt that
        # flares to a folded hem on the floor
        n = 24
        flare = 0.035
        fold = 0.014
        r_top_x, r_top_y = rx - flare - fold, ry - flare - fold
        rim = 0.02
        verts = [(0.0, 0.0, h)]
        rings = []
        # ring 0: the top edge; ring 1: over the roll; ring 2: the hem
        for j, (sx, sy, z) in enumerate(((r_top_x, r_top_y, h),
                                         (r_top_x + 0.012, r_top_y + 0.012, h - rim),
                                         (None, None, 0.0))):
            ring = []
            for k in range(n):
                a = 2.0 * math.pi * k / n + math.pi / n
                if j < 2:
                    x, y = sx * math.cos(a), sy * math.sin(a)
                else:
                    f = fold * (1.0 if k % 2 == 0 else -1.0) * rng.uniform(0.55, 1.0)
                    x = (rx - fold + f) * math.cos(a)
                    y = (ry - fold + f) * math.sin(a)
                ring.append(len(verts))
                verts.append((x, y, z))
            rings.append(ring)
        faces = []
        for k in range(n):
            k1 = (k + 1) % n
            faces.append((0, rings[0][k], rings[0][k1]))
            for j in range(2):
                a0, a1 = rings[j][k], rings[j][k1]
                b0, b1 = rings[j + 1][k], rings[j + 1][k1]
                faces.append((a0, b0, b1))
                faces.append((a0, b1, a1))
        # the hem turned under, so the skirt is a closed solid: an inner
        # ring 6 mm in, back up 2 cm, closed to the top's underside
        inner = []
        for k in range(n):
            x, y, _z = verts[rings[2][k]]
            ln = math.hypot(x, y)
            inner.append(len(verts))
            verts.append((x - 0.006 * x / ln, y - 0.006 * y / ln, 0.0))
        for k in range(n):
            k1 = (k + 1) % n
            faces.append((rings[2][k], inner[k], inner[k1]))
            faces.append((rings[2][k], inner[k1], rings[2][k1]))
        up = []
        for k in range(n):
            x, y, _z = verts[inner[k]]
            up.append(len(verts))
            verts.append((x, y, 0.02))
        for k in range(n):
            k1 = (k + 1) % n
            faces.append((inner[k], up[k], up[k1]))
            faces.append((inner[k], up[k1], inner[k1]))
        centre_under = len(verts)
        verts.append((0.0, 0.0, 0.02))
        for k in range(n):
            k1 = (k + 1) % n
            faces.append((up[k], centre_under, up[k1]))
        prims.append(P.mesh("Table_Cloth", "cloth", verts, faces))
        top_r = min(r_top_x, r_top_y)
        cboxes.append(((-rx, -ry, 0.0), (rx, ry, h)))
    half = top_r / math.sqrt(2.0) * 0.96
    prims, cboxes, over = _finish(prims, cboxes, w, d, h)
    return {"prims": prims, "collision": cboxes, "form": form, "cloth_rgb": cloth,
            "top_z": h, "top_radius": top_r,
            "stock_regions": [(-half, 0.0, -half, half, h), (0.0, half, -half, half, h)],
            "overshoot_m": over}


def _scaled_cyl(part, mat, rx, ry, z0, z1, n, phase=0.0):
    c = P.cyl(part, mat, (0.0, 0.0), 1.0, z0, z1, segments=n, phase=phase)
    c["verts"] = [(v[0] * rx, v[1] * ry, v[2]) for v in c["verts"]]
    return c


# --- club_chair ------------------------------------------------------------------

#: worn velvet: oxblood, plum, teal, bottle green -- the art direction's
#: accents, darker, as a dim room shows them
VELVETS = (([0.22, 0.025, 0.04], 3.0), ([0.12, 0.03, 0.12], 2.0),
           ([0.02, 0.10, 0.10], 1.5), ([0.03, 0.09, 0.04], 1.0))
CHAIR_MATERIALS = {"piping": ([0.05, 0.03, 0.02], "leather")}
CHAIR_SEAT_H = 0.42
BACK_T = 0.13
ARM_FRONT_DEG = 35.0      # how far past the sides the barrel wraps forward


def _weighted(rng, table):
    pick = rng.uniform(0.0, sum(wt for _c, wt in table))
    for c, wt in table:
        pick -= wt
        if pick <= 0.0:
            return c
    return table[-1][0]


def plan_chair(w, d, h, rng):
    """A barrel-backed tub chair facing -Y: short wood feet, an upholstered
    drum, a crowned D-shaped seat, and a back that wraps round the sides and
    slopes down to the arm fronts. ``{"prims", "collision", "velvet_rgb",
    "seat_z", "arm_z", "overshoot_m"}``."""
    rx, ry = w / 2, d / 2
    velvet = _weighted(rng, VELVETS)
    prims, cboxes = [], []
    seat_z = min(CHAIR_SEAT_H, 0.62 * h)
    arm_z = min(h - 0.06, max(seat_z + 0.16, 0.8 * h))
    # feet under the drum
    for ang in (45.0, 135.0, 225.0, 315.0):
        a = math.radians(ang)
        prims.append(P.cyl("ClubChair_Feet", "feet",
                           ((rx - 0.09) * math.cos(a), (ry - 0.09) * math.sin(a)),
                           0.022, 0.0, 0.062, segments=8, r_top=0.018))
    # the drum
    prims.append(_scaled_cyl("ClubChair_Base", "velvet", rx - 0.03, ry - 0.03, 0.055,
                             seat_z - 0.12, 20, math.pi / 20))
    # the seat: a crowned disc, its back tucked under the barrel
    # its front is the slot's front; its back half reaches 12 mm under the
    # barrel's inner wall. REFUTED FIRST: one ellipse inside the barrel, whose
    # front stood 33 mm short of the slot, which `fit_exact` then stretched
    # the whole chair by 4 % to cover
    n = 20
    sx = rx - BACK_T + 0.012
    sy_front, sy_back = ry, ry - BACK_T + 0.012
    z0, z1 = seat_z - 0.12 - 0.003, seat_z - 0.014
    ring = []
    for k in range(n):
        a = 2.0 * math.pi * k / n + math.pi / n
        s = math.sin(a)
        ring.append((sx * math.cos(a), (sy_front if s < 0 else sy_back) * s))
    sv = [(0.0, (sy_back - sy_front) / 2.0, seat_z)]
    sv += [(x, y, z1) for x, y in ring]
    sv += [(x, y, z0) for x, y in ring]
    sf = []
    for k in range(n):
        k1 = (k + 1) % n
        sf.append((0, 1 + k, 1 + k1))
        sf.append((1 + k, 1 + n + k, 1 + n + k1, 1 + k1))
    sf.append(tuple(1 + n + k for k in reversed(range(n))))
    prims.append(P.mesh("ClubChair_Seat", "velvet", sv, sf))
    # the barrel: sampled round the back from one arm front to the other
    a0 = math.radians(-ARM_FRONT_DEG)
    a1 = math.radians(180.0 + ARM_FRONT_DEG)
    m = 24
    samples = []
    for k in range(m + 1):
        a = a0 + (a1 - a0) * k / m
        ox, oy = rx * math.cos(a), ry * math.sin(a)
        nx, ny = ox / (rx * rx), oy / (ry * ry)          # ellipse normal
        ln = math.hypot(nx, ny)
        nx, ny = nx / ln, ny / ln
        # the top: full height across the back, falling to arm height as
        # the sample comes round past the sides (sin < 0 is the front half)
        s = math.sin(a)
        t = max(0.0, min(1.0, (s + math.sin(math.radians(ARM_FRONT_DEG))) /
                         (1.0 + math.sin(math.radians(ARM_FRONT_DEG)))))
        zt = arm_z + (h - arm_z) * (t ** 1.5)
        samples.append((ox, oy, nx, ny, zt))
    bv, bf = [], []
    zb = 0.075
    roll = 0.035
    for ox, oy, nx, ny, zt in samples:
        ix, iy = ox - nx * BACK_T, oy - ny * BACK_T
        mx, my = ox - nx * BACK_T / 2, oy - ny * BACK_T / 2
        bv += [(ox, oy, zb), (ox, oy, zt - roll), (mx, my, zt), (ix, iy, zt - roll),
               (ix, iy, zb)]
    for k in range(m):
        a, b = 5 * k, 5 * (k + 1)
        # outer wall (vertical, planar)
        bf.append((a + 0, b + 0, b + 1, a + 1))
        # the rolled top, two facets each side of the crown, as triangles
        bf.append((a + 1, b + 1, b + 2))
        bf.append((a + 1, b + 2, a + 2))
        bf.append((a + 2, b + 2, b + 3))
        bf.append((a + 2, b + 3, a + 3))
        # inner wall
        bf.append((a + 3, b + 3, b + 4, a + 4))
        # bottom
        bf.append((a + 4, b + 4, b + 0, a + 0))
    # end caps at the arm fronts (convex pentagons in the normal's plane)
    bf.append((0, 1, 2, 3, 4))
    e = 5 * m
    bf.append((e + 4, e + 3, e + 2, e + 1, e + 0))
    back = P.mesh("ClubChair_Back", "velvet", bv, bf)
    # the barrel's winding: outer walls face out when samples run CCW; the
    # face lists above are written for that and the test holds the volume
    prims.append(back)
    # piping: a cord along the crown of the barrel
    # its top 1 mm under the crown: at 4 mm under, its 8 mm cord stood 4 mm
    # over the slot and `fit_exact` lowered the whole chair to fit it
    crown = [(ox - nx * BACK_T / 2, oy - ny * BACK_T / 2, zt - 0.009)
             for ox, oy, nx, ny, zt in samples]
    for i in range(m):
        prims.append(P.rod("ClubChair_Piping", "piping", crown[i], crown[i + 1], 0.008,
                           segments=6))
    cboxes.append(((-rx, -ry, 0.0), (rx, ry, seat_z)))
    cboxes.append(((-rx, 0.0, seat_z), (rx, ry, h)))
    prims, cboxes, over = _finish(prims, cboxes, w, d, h)
    return {"prims": prims, "collision": cboxes, "velvet_rgb": velvet, "seat_z": seat_z,
            "arm_z": arm_z, "overshoot_m": over}


# --- bar_stool -------------------------------------------------------------------

SEATS = (([0.20, 0.02, 0.03], 3.0), ([0.02, 0.02, 0.02], 2.5), ([0.10, 0.04, 0.12], 1.0))
STOOL_MATERIALS = {"seatpan": ([0.04, 0.04, 0.04], "metal_painted")}


def plan_stool(w, d, h, rng):
    """A padded round seat on a chrome column with a footring and a domed
    base. ``{"prims", "collision", "seat_rgb", "ring_z", "overshoot_m"}``."""
    rx, ry = w / 2, d / 2
    seat = _weighted(rng, SEATS)
    prims, cboxes = [], []
    base_r = 0.86
    prims.append(_scaled_cyl("BarStool_Base", "column", rx * base_r, ry * base_r, 0.0,
                             0.022, 16))
    dome = _scaled_cyl("BarStool_Base", "column", rx * base_r * 0.9, ry * base_r * 0.9,
                       0.018, 0.06, 16, math.pi / 16)
    dome["verts"] = [(v[0] * (0.35 if v[2] > 0.05 else 1.0), v[1] * (0.35 if v[2] > 0.05 else 1.0),
                      v[2]) for v in dome["verts"]]
    prims.append(dome)
    cushion_t = 0.075
    pan_t = 0.03
    col_top = h - cushion_t - pan_t + 0.006
    prims.append(P.cyl("BarStool_Column", "column", (0.0, 0.0), 0.028, 0.05, col_top,
                       segments=12))
    ring_z = max(0.18, min(0.34 * h, h - 0.35))
    rr = 0.84
    ring = [(rx * rr * math.cos(2 * math.pi * k / 12 + math.pi / 12),
             ry * rr * math.sin(2 * math.pi * k / 12 + math.pi / 12), ring_z) for k in range(12)]
    prims += tube_path("BarStool_Footring", "column", ring, 0.012, closed=True)
    for k in range(3):
        a = 2 * math.pi * k / 3 + math.pi / 6
        prims.append(P.rod("BarStool_Footring", "column",
                           (0.02 * math.cos(a), 0.02 * math.sin(a), ring_z),
                           (rx * rr * 0.985 * math.cos(a), ry * rr * 0.985 * math.sin(a), ring_z),
                           0.008, segments=8))
    # the seat pan and the padded seat, crowned
    pan = _scaled_cyl("BarStool_Pan", "seatpan", rx * 0.78, ry * 0.78, h - cushion_t - pan_t,
                      h - cushion_t + 0.004, 16, math.pi / 16)
    pan["verts"] = [(v[0] * (0.7 if v[2] < h - cushion_t - 0.01 else 1.0),
                     v[1] * (0.7 if v[2] < h - cushion_t - 0.01 else 1.0), v[2])
                    for v in pan["verts"]]
    prims.append(pan)
    n = 20
    z0, z1 = h - cushion_t, h - 0.018
    sv = [(0.0, 0.0, h)]
    for k in range(n):
        a = 2 * math.pi * k / n
        sv.append((rx * 0.96 * math.cos(a), ry * 0.96 * math.sin(a), z1))
    for k in range(n):
        a = 2 * math.pi * k / n
        sv.append((rx * math.cos(a), ry * math.sin(a), z1 - 0.022))
    for k in range(n):
        a = 2 * math.pi * k / n
        sv.append((rx * 0.94 * math.cos(a), ry * 0.94 * math.sin(a), z0))
    sf = []
    for k in range(n):
        k1 = (k + 1) % n
        sf.append((0, 1 + k, 1 + k1))
        sf.append((1 + k, 1 + n + k, 1 + n + k1, 1 + k1))
        sf.append((1 + n + k, 1 + 2 * n + k, 1 + 2 * n + k1, 1 + n + k1))
    sf.append(tuple(1 + 2 * n + k for k in reversed(range(n))))
    prims.append(P.mesh("BarStool_Seat", "seat", sv, sf))
    cboxes.append(((-rx * 0.8, -ry * 0.8, 0.0), (rx * 0.8, ry * 0.8, h)))
    prims, cboxes, over = _finish(prims, cboxes, w, d, h)
    return {"prims": prims, "collision": cboxes, "seat_rgb": seat, "ring_z": ring_z,
            "overshoot_m": over}
