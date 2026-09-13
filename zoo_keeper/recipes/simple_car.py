"""Simple car recipe: a 1990s American street car. Length runs along Y, the
nose at -Y; built base-up (z 0 .. h) and re-centred by `build.build_module`.

REWRITTEN AGAIN, 0.79.0, after the walker walked a street of them: "we need
our cars to upgrade quite a bit. missing a lot of detail, side windows,
transparency, etc etc". What 0.78.0 built is measured at the top of
`core/car_forms.py`: one opaque cabin box, side panes buried inside it, and a
glass material the delco skin exported OPAQUE.

WHAT A CAR IS HERE, in the order the parts are built:

  * THE LOWER BODY is one loft of cross-sections along the length. Each
    section is a rocker tucked under a vertical door skin, a shoulder rolling
    in to the belt line, and on top either a crowned hood / deck or -- inside
    the cabin -- the open tub the doors make: door tops at the belt, inner
    door walls, a floor. The bottom line of the sections runs up and over
    each axle, so the ARCHES are in the silhouette: the tyre sits in them.
  * THE GREENHOUSE is not a solid. A solid behind glass is a painted wall
    behind glass. It is a hull -- windshield plane, side planes with
    tumblehome, rear plane -- and on that hull: a roof slab, pillars as
    strips standing `PILLAR_INSET` inside it, and one pane per opening
    standing `GLASS_INSET` inside that. The body style decides where the hull
    starts and ends (`car_forms.FORMS`); the doors decide the pillars.
  * THE INTERIOR is what the glass shows: dashboard, instrument hood,
    steering wheel on the driver's side, front seats, a rear bench, door
    cards and a floor mat. Low, and inside the tub.
  * THE DETAILS a street reads a car by: shaped bumpers front and rear,
    grille, headlamps and corner lamps on the nose face, tail lamps and a
    plate on the tail (Pennsylvania plates the rear only), mirrors, door
    handles, door seams, a side moulding, wipers, and on an SUV a roof rack
    and two-tone lower cladding.

NO TWO FACES SHARE A PLANE. Every detail on a face stands proud of it by a
named distance above tools/coplanar_probe.py's 2 mm window, and every part
that must meet another runs INTO it rather than stopping at its face. The
glass is a transparent surface, which makes a coincident face worse, not
better: nothing in the depth buffer decides which of two blended faces
draws.

THE SLOT IS EXACT. Width is the mirror heads' outer faces, depth the
bumpers' outer faces, height the roof (or the roof rack's rails). The body
side stands `mirror_out` inside the slot's half-width.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials
from ..core import car_forms

#: How far a flat detail (lamp, plate, handle) stands proud of its face.
#: tools/coplanar_probe.py reports coincidence within 2 mm; 4 mm is the
#: FACE_PROUD stop_sign.py settled on for the same reason.
DETAIL_PROUD = 0.004
#: A strip that should read as trim rather than a sticker: mouldings,
#: cladding. Its end faces stand clear of the skin by this much.
TRIM_PROUD = 0.006
#: Door seams: a dark line, just proud enough to leave the probe's window.
SEAM_PROUD = 0.003
#: Pillars stand this far inside the greenhouse hull, so the roof slab's
#: side and front faces -- which ARE the hull -- never lie in their plane.
PILLAR_INSET = 0.003
PILLAR_T = 0.045
#: The panes stand this far inside the hull: 4 mm behind the pillars' outer
#: faces, so glass reads as glass in an aperture and never as a sticker.
GLASS_INSET = 0.007
GLASS_T = 0.006
#: WHEEL_TUCK, ARCH_GAP and BUMPER_BURY are `car_forms`' (the layout that
#: the dims-contract tests read); imported, never restated.
WHEEL_TUCK = car_forms.WHEEL_TUCK
ARCH_GAP = car_forms.ARCH_GAP
BUMPER_BURY = car_forms.BUMPER_BURY
#: The arch lip's run along Y: the lip is this steep a face, not a step.
ARCH_LIP = 0.012
#: Degrees per section over an arch.
ARCH_STEP_DEG = 45
#: Outside an arch the well is a notch this tall, so every section has the
#: same points and the loft never needs a zero-length edge.
WELL_NOTCH = 0.012
#: The well's inner wall stands this far inboard of the tyre's inner face.
WELL_CLEAR = 0.05
ROCKER_TUCK = 0.055      # rocker bottom inboard of the door skin
ROCKER_H = 0.09          # door skin's lower edge above the rocker bottom
SHOULDER_IN = 0.045      # belt line inboard of the door skin
SHOULDER_H = 0.055       # height of the shoulder roll
DOOR_T = 0.075           # door wall thickness inside the shoulder
HOOD_CROWN = 0.018
BUMPER_BACK = 0.05       # the bumper runs this far behind the nose face
#: How deep each strip on the door skin runs INTO the body. Strips cross
#: (a seam through a moulding, a pinstripe on the cladding), so their buried
#: faces are kept 3 mm or more apart: pinstripe 18 mm against cladding 16 mm
#: was measured as a SAME pair at 2.0 mm before these were spread.
SKIN_DEPTH = {"seam": 0.008, "moulding": 0.012, "handle": 0.015,
              "cladding": 0.018, "pinstripe": 0.024}
#: Transition sections are this far apart: a firewall is a steep face, and
#: two sections at one Y would be a zero-area face.
STEP = 0.012
GLASS_OPACITY = 0.38
GLASS_TINT = (0.06, 0.09, 0.10)


def _lerp(a, b, t):
    return a + (b - a) * t


def _hexa(bm, pts):
    """Closed six-faced solid from 8 points: a bottom quad then the top quad
    over it, both in the same winding. Normals are recalculated later."""
    v = [bm.verts.new(p) for p in pts]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5),
              (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([v[i] for i in f])


def _loft(bm, loops):
    """Quads between consecutive loops of equal length, capped at both ends."""
    rows = [[bm.verts.new(p) for p in loop] for loop in loops]
    k = len(rows[0])
    for a, b in zip(rows, rows[1:]):
        for i in range(k):
            j = (i + 1) % k
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new(rows[0])
    bm.faces.new(list(reversed(rows[-1])))


def _box(bm, lo, hi):
    geometry.add_box(bm, tuple((a + b) / 2.0 for a, b in zip(lo, hi)),
                     tuple(max(1e-4, b - a) for a, b in zip(lo, hi)))


def _lathe_x(bm, cx, cy, cz, profile, seg, sign):
    """Revolve a closed (radius, dx) profile about an axis parallel to X
    through (cx, cy, cz). ``sign`` mirrors dx for the car's left side."""
    rows = []
    for k in range(seg):
        a = 2.0 * math.pi * k / seg
        ca, sa = math.cos(a), math.sin(a)
        rows.append([bm.verts.new((cx + sign * dx, cy + r * ca, cz + r * sa))
                     for r, dx in profile])
    n = len(profile)
    for k in range(seg):
        a, b = rows[k], rows[(k + 1) % seg]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))


def _torus(bm, c, u, v, n, major, minor, seg=10, tube=4):
    """A low ring in the plane of unit vectors u, v (n its normal)."""
    rows = []
    for i in range(seg):
        a = 2.0 * math.pi * i / seg
        d = [u[k] * math.cos(a) + v[k] * math.sin(a) for k in range(3)]
        ring = [c[k] + major * d[k] for k in range(3)]
        row = []
        for j in range(tube):
            b = 2.0 * math.pi * j / tube
            row.append(bm.verts.new(tuple(
                ring[k] + minor * (d[k] * math.cos(b) + n[k] * math.sin(b))
                for k in range(3))))
        rows.append(row)
    for i in range(seg):
        a, b = rows[i], rows[(i + 1) % seg]
        for j in range(tube):
            jj = (j + 1) % tube
            bm.faces.new((a[j], a[jj], b[jj], b[j]))


def _norm(v):
    m = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / m for c in v)


def _sub(p, n, d):
    return tuple(p[k] - n[k] * d for k in range(3))


def build(plan, streams, collection):
    W = plan["dimensions"]["width"]
    L = plan["dimensions"]["depth"]
    H = plan["dimensions"]["height"]
    wear = plan["wear"]
    # plan["bevel"] (the style blocks' `bevel`) is NOT applied, on purpose:
    # the chamfers a car reads by -- shoulder roll, hood crown, bumper slope,
    # tyre shoulders -- are modelled in the sections, and `bevel_edges` on
    # every sharp edge is what took 0.78.0's 12-tri boxes to 44 tris each
    # (measured on walk 9048's shipped car). Every part is built bevel 0.
    rng = streams.stream("wear")
    seg = int(plan["params"].get("wheel_segments", 12))
    f = car_forms.resolve(plan, streams)
    style = f["style"]
    trunk = f["trough"] == "backlight"
    width_k = W / 1.75

    groups = {k: geometry.new_bm() for k in (
        "body", "trim", "tyres", "chrome", "lamp_head", "lamp_tail",
        "lamp_amber", "plate", "interior", "cladding", "bumper_grey")}
    panes = []

    # --- the numbers, in metres (car_forms.layout: pure, and tested) -------
    lay = car_forms.layout(f, W, L, H)
    zr = lay["zr"]                                # roof top
    wheel_r, clear, belt = lay["wheel_r"], lay["clear"], lay["belt"]
    fascia, hood = lay["fascia"], lay["hood"]
    deck, tail = lay["deck"], lay["tail"]
    hw = lay["hw"]                                # the door skin's plane
    tyre_w = lay["tyre_w"]
    yF0, yR0 = lay["yF0"], lay["yR0"]
    y0, yt = lay["y0"], lay["yt"]                 # nose face, tail face
    ya_f, ya_r, R = lay["ya_f"], lay["ya_r"], lay["R"]
    y_bl, y_rr, y_ws, y_rf = lay["y_bl"], lay["y_rr"], lay["y_ws"], lay["y_rf"]
    roll, y_te, tail_roll = lay["roll"], lay["y_te"], lay["tail_roll"]

    def z_top(y):
        if y <= y0 + roll:
            return _lerp(fascia, hood, max(0.0, (y - y0) / roll))
        if y <= y_ws:
            return _lerp(hood, belt, (y - y0 - roll) / max(1e-6, y_ws - y0 - roll))
        if trunk:
            if y <= y_bl:
                return belt
            if y <= yt - roll:
                return _lerp(belt, deck, (y - y_bl) / max(1e-6, yt - roll - y_bl))
            return _lerp(deck, tail, min(1.0, (y - (yt - roll)) / roll))
        if y <= tail_roll:
            return belt
        return _lerp(belt, tail, min(1.0, (y - tail_roll) / max(1e-6, yt - tail_roll)))

    def z_base(y):
        """The underside: clearance, rising a little under the overhangs."""
        z = clear
        end = 0.25
        if y < y0 + end:
            z = max(z, clear + 0.06 * (1.0 - (y - y0) / end))
        if y > yt - end:
            z = max(z, clear + 0.06 * (1.0 - (yt - y) / end))
        return z

    def z_well(y):
        """The wheel well's roof: a round arch over each axle, and a notch
        `WELL_NOTCH` deep everywhere else so every section keeps one shape."""
        z = z_base(y) + WELL_NOTCH
        for ya in (ya_f, ya_r):
            dy = abs(y - ya)
            if dy <= R + 1e-9:
                z = max(z, wheel_r + math.sqrt(max(0.0, R * R - dy * dy)))
            elif dy < R + ARCH_LIP - 1e-9:
                z = max(z, wheel_r)
        return z

    def half_w(y):
        zone = 0.30
        k = 1.0
        if y < y0 + zone:
            t = (y0 + zone - y) / zone
            k -= f["pinch_front"] * t * t
        if y > yt - zone:
            t = (y - (yt - zone)) / zone
            k -= f["pinch_rear"] * t * t
        return hw * k

    def cabin(y):
        return y_ws + STEP * 0.5 <= y <= y_te + STEP * 0.5

    floor_z = clear + 0.13
    xw = hw - WHEEL_TUCK - tyre_w - WELL_CLEAR     # wheel well's inner wall
    xi = hw - SHOULDER_IN - DOOR_T                 # inner face of the door walls
    xtub = min(xw - 0.03, xi - 0.01)               # the tub's inner wall

    def section(y):
        """One cross-section, ten points a side from the underside up.

        Outside the cabin the top is a crowned hood or deck. Inside it the
        top is the open tub: door top, inner door wall, a ledge (over an
        arch, the wheel tub the well pushes into the cabin) and the floor.
        The arch is a WELL notched into the outer underside, not a tunnel
        through the whole width, so the floor stays a floor."""
        hwy = half_w(y)
        zb = z_base(y)
        zwl = z_well(y)
        cab = cabin(y)
        zt = belt if cab else z_top(y)
        z1 = max(zb + ROCKER_H, zwl + 0.012)
        z2 = max(z1 + 0.01, zt - SHOULDER_H)
        x3 = hwy - SHOULDER_IN
        right = [(xw, zb), (xw, zwl), (hwy - ROCKER_TUCK, zwl), (hwy, z1),
                 (hwy, z2), (x3, zt)]
        if cab:
            ledge = max(floor_z + 0.03, zwl + 0.03)
            xin = x3 - DOOR_T
            right += [(xin, zt), (xin, ledge), (min(xtub, xin - 0.01), ledge),
                      (min(xtub, xin - 0.01), floor_z)]
        else:
            right += [(x3 * 0.78, zt + HOOD_CROWN * 0.40),
                      (x3 * 0.55, zt + HOOD_CROWN * 0.72),
                      (x3 * 0.32, zt + HOOD_CROWN * 0.90),
                      (x3 * 0.10, zt + HOOD_CROWN)]
        left = [(-x, z) for x, z in reversed(right)]
        return [(x, y, z) for x, z in right + left]

    # --- stations along the body ------------------------------------------
    # Only where the section CHANGES: the hood and deck are linear in Y
    # between their end stations, so a midpoint station bought 40 tris and no
    # shape (measured: Car_Body 1,344 of 2,980 tris on the 2.0 x 5.2 x 1.75
    # SUV before these were dropped and the arch step went from 30 to 45).
    ys = [y0, y0 + roll, y0 + 0.30,
          y_ws, y_ws + STEP, y_te, y_te + STEP, tail_roll, yt - 0.30, yt]
    for ya in (ya_f, ya_r):
        for deg in range(0, 181, ARCH_STEP_DEG):
            ys.append(ya + R * math.cos(math.radians(deg)))
        ys += [ya - R - ARCH_LIP, ya + R + ARCH_LIP]
    ys = sorted(y for y in ys if y0 - 1e-9 <= y <= yt + 1e-9)
    stations = []
    for y in ys:
        if not stations or y - stations[-1] > 0.004:
            stations.append(y)
    _loft(groups["body"], [section(y) for y in stations])

    # --- greenhouse hull -----------------------------------------------------
    zb_h = belt
    dz = zr - zb_h
    hw_gb = hw - SHOULDER_IN - 0.004
    hw_gr = min(hw * f["roof_w"], hw_gb - 0.02)
    k_side = (hw_gr - hw_gb) / dz
    m_f = (y_rf - y_ws) / dz
    m_r = (y_rr - y_bl) / dz
    roof_t = 0.05
    s_rb = 1.0 - roof_t / dz
    s_ru = 1.0 - 0.022 / dz
    s_bot = -0.07
    s_top = 1.0 - 0.025 / dz
    s_glass_lo = -0.04
    s_glass_hi = 1.0 - 0.03 / dz

    def zs(s):
        return zb_h + s * dz

    def hwg(s):
        return hw_gb + (hw_gr - hw_gb) * s

    def yF(s):
        return y_ws + (y_rf - y_ws) * s

    def yR(s):
        return y_bl + (y_rr - y_bl) * s

    def n_side(sign):
        return _norm((sign, 0.0, -k_side))

    n_front = _norm((0.0, -1.0, m_f))
    n_rear = _norm((0.0, 1.0, -m_r))

    def P_side(sign, y, s, d):
        return _sub((sign * hwg(s), y, zs(s)), n_side(sign), d)

    def P_front(x, s, d):
        return _sub((x, yF(s), zs(s)), n_front, d)

    def P_rear(x, s, d):
        return _sub((x, yR(s), zs(s)), n_rear, d)

    # roof slab: its sides and ends ARE the hull
    def roof_loop(yfun):
        pts = [(-hwg(s_rb), s_rb), (-hwg(s_ru), s_ru), (-0.55 * hwg(1.0), 1.0),
               (0.55 * hwg(1.0), 1.0), (hwg(s_ru), s_ru), (hwg(s_rb), s_rb)]
        return [(x, yfun(s), zs(s)) for x, s in pts]
    _loft(groups["body"], [roof_loop(yF), roof_loop(yR)])

    # side openings: edges as (y at the belt, y at the roof)
    a_side_b, a_side_r = y_ws + car_forms.A_SIDE_BELT, y_rf + 0.065
    if trunk:
        end_b = y_rr + (0.24 if f["quarter_glass"] else -0.02)
        end_r = y_rr - 0.10
    else:
        end_b, end_r = y_bl - 0.13, y_rr - 0.10
    split = car_forms.door_split(f)
    total = sum(w for _k, w in split)
    acc = 0.0
    mids = []
    for i, (kind, w) in enumerate(split[:-1]):
        acc += w
        yb = _lerp(a_side_b, end_b, acc / total)
        yr = min(max(yb + 0.03, a_side_r + 0.15), end_r - 0.12)
        mids.append((yb, yr))
    #: the pillar BEHIND an opening: B behind the front door, C (or the
    #: quarter's front frame) behind the rear door
    pillar_w = {"door_f": 0.075, "door_r": 0.085, "quarter": 0.06}
    openings = []
    prev = (a_side_b, a_side_r)
    for i, (kind, _w) in enumerate(split):
        if i < len(mids):
            pw = pillar_w[kind]
            yb, yr = mids[i]
            nxt = (yb - pw / 2.0, yr - pw / 2.0)
            openings.append((kind, prev, nxt))
            prev = (yb + pw / 2.0, yr + pw / 2.0)
        else:
            openings.append((kind, prev, (end_b, end_r)))

    def side_strip(sign, e0, e1, bm):
        """A pillar on a side plane between two (belt, roof) edge lines."""
        pts = []
        for s in (s_bot, s_top):
            t = s
            ya = _lerp(e0[0], e0[1], t)
            yb = _lerp(e1[0], e1[1], t)
            pts += [P_side(sign, ya, s, PILLAR_INSET),
                    P_side(sign, yb, s, PILLAR_INSET),
                    P_side(sign, yb, s, PILLAR_INSET + PILLAR_T),
                    P_side(sign, ya, s, PILLAR_INSET + PILLAR_T)]
        _hexa(bm, pts)

    def inside_both(e, a, b, t):
        """The point `t` inside both planes through edge point `e` (unit
        normals a, b): e - t / (1 + a.b) * (a + b).

        NOT e - t*a - t*b, which is what this was first. The hull's planes are
        not square to each other (tumblehome, rake), so that point sits
        t * (1 + a.b) inside each -- and the L-section's outer faces, joining
        it to points exactly t inside, came out as twisted quads whose two
        triangles lay 0.3 to 2.6 mm off the 3 mm inset. tools/coplanar_probe.py
        counted them against the roof slab's side face as SAME pairs at
        1.85-1.87 mm (0.66 and 24.16 cm2 a side, the 2.0 x 5.2 x 1.75 SUV)."""
        k = t / (1.0 + sum(a[i] * b[i] for i in range(3)))
        return tuple(e[i] - k * (a[i] + b[i]) for i in range(3))

    def corner_pillar(sign, front, strip_edge, face_w, bm):
        """A corner pillar: a strip on the side plane and a strip on the
        windshield (front) or rear plane, one L-section solid."""
        loops = []
        for s in (s_bot, s_top):
            ns = n_side(sign)
            nf = n_front if front else n_rear
            Pf = P_front if front else P_rear
            yedge = yF(s) if front else yR(s)
            e = (sign * hwg(s), yedge, zs(s))
            E = inside_both(e, ns, nf, PILLAR_INSET)
            Ci = inside_both(e, ns, nf, PILLAR_INSET + PILLAR_T)
            # The strip is never narrower than the inner corner is deep. On a
            # raked windshield the inner corner moves back along Y AND down,
            # and the strip's edge runs back as it drops; with the strip at its
            # nominal width the inner corner landed on the edge line and the
            # inner face folded into a bow-tie -- two triangles of one quad
            # face to face (OPP, 0.00 mm, 7-20 cm2 on every hatchback at
            # 1.75 x 4.30 x 1.45 and 5.2 m). The first clamp compared Y at the
            # loop's own height, never bound, and changed nothing: the edge
            # has to be read at the corner's height.
            ys_ = _lerp(strip_edge[0], strip_edge[1], s)
            slope = (strip_edge[1] - strip_edge[0]) / dz      # Y per metre of Z
            at_corner = ys_ - slope * (zs(s) - Ci[2])
            if front and at_corner < Ci[1] + 0.02:
                ys_ += Ci[1] + 0.02 - at_corner
            elif not front and at_corner > Ci[1] - 0.02:
                ys_ -= at_corner - (Ci[1] - 0.02)
            So = P_side(sign, ys_, s, PILLAR_INSET)
            Si = P_side(sign, ys_, s, PILLAR_INSET + PILLAR_T)
            xf = sign * (hwg(s) - face_w)
            Fi = Pf(xf, s, PILLAR_INSET + PILLAR_T)
            Fo = Pf(xf, s, PILLAR_INSET)
            loops.append([E, So, Si, Ci, Fi, Fo])
        _loft(bm, loops)

    def pane(name, corners_outer, normal):
        bm = geometry.new_bm()
        outer = [_sub(p, normal, 0.0) for p in corners_outer]
        inner = [_sub(p, normal, GLASS_T) for p in corners_outer]
        _hexa(bm, outer + inner)
        panes.append((name, bm))

    blackout = groups["trim"] if f["blackout_b"] else groups["body"]
    a_face_w, r_face_w = 0.075, 0.08
    # pane names come from car_forms.pane_names: side panes L (+X) then R, in
    # door_split order -- the order `openings` was built in
    pane_names = car_forms.pane_names(f)
    side_names = iter(pane_names[1:-1])
    for sign in (1.0, -1.0):
        corner_pillar(sign, True, (a_side_b, a_side_r), a_face_w, groups["body"])
        corner_pillar(sign, False, (end_b, end_r), r_face_w, groups["body"])
        for i in range(len(openings) - 1):
            e0 = openings[i][2]
            e1 = openings[i + 1][1]
            side_strip(sign, e0, e1, blackout)
        for kind, e0, e1 in openings:
            corners = []
            for s, lo_hi in ((s_glass_lo, 0), (s_glass_lo, 1), (s_glass_hi, 1),
                             (s_glass_hi, 0)):
                if lo_hi == 0:
                    y = _lerp(e0[0], e0[1], s) - 0.012
                else:
                    y = _lerp(e1[0], e1[1], s) + 0.012
                corners.append(P_side(sign, y, s, GLASS_INSET))
            pane(next(side_names), corners, n_side(sign))

    ws = []
    for s in (s_glass_lo, s_glass_hi):
        xin = hwg(s) - a_face_w + 0.012
        ws.append((P_front(-xin, s, GLASS_INSET), P_front(xin, s, GLASS_INSET)))
    pane(pane_names[0], [ws[0][0], ws[0][1], ws[1][1], ws[1][0]], n_front)
    bl = []
    for s in (s_glass_lo, s_glass_hi):
        xin = hwg(s) - r_face_w + 0.012
        bl.append((P_rear(-xin, s, GLASS_INSET), P_rear(xin, s, GLASS_INSET)))
    pane(pane_names[-1], [bl[0][0], bl[0][1], bl[1][1], bl[1][0]], n_rear)
    if [n for n, _bm in panes] != pane_names[1:-1] + [pane_names[0], pane_names[-1]]:
        raise RuntimeError("simple_car: panes built %s, car_forms.pane_names %s"
                           % ([n for n, _bm in panes], pane_names))

    # --- bumpers --------------------------------------------------------------
    bz0 = clear + 0.03
    bz1 = min(fascia - 0.19, clear + 0.30)
    lamp_z0, lamp_z1 = bz1 + 0.04, fascia - 0.03
    bumper_bm = {"body": groups["body"], "black": groups["trim"],
                 "grey": groups["bumper_grey"]}[f["bumper_kind"]]
    for sy, y_face, y_body in ((-1.0, yF0, y0), (1.0, yR0, yt)):
        xb = half_w(y_body - sy * BUMPER_BACK) + 0.012
        xa = xb - 0.06
        y_back = y_body - sy * BUMPER_BACK
        # lower band: the rub strip, the full depth to the slot's end
        mid = _lerp(bz0, bz1, 0.42)
        _hexa(groups["trim"] if f["bumper_kind"] != "black" else bumper_bm, [
            (-xa, y_face, bz0), (xa, y_face, bz0), (xb, y_back, bz0), (-xb, y_back, bz0),
            (-xa, y_face, mid), (xa, y_face, mid), (xb, y_back, mid), (-xb, y_back, mid)])
        # upper band in the bumper's colour, set back so the strip reads;
        # its back face stops short of the strip's so the two buried backs
        # are not one plane
        yu = y_face - sy * 0.012
        top_back = yu - sy * 0.035
        yub = y_back - sy * 0.012
        _hexa(bumper_bm, [
            (-xa, yu, mid - 0.02), (xa, yu, mid - 0.02), (xb, yub, mid - 0.02),
            (-xb, yub, mid - 0.02),
            (-xa + 0.02, top_back, bz1), (xa - 0.02, top_back, bz1),
            (xb - 0.01, yub, bz1), (-xb + 0.01, yub, bz1)])

    # --- nose: lamps and grille on the nose face --------------------------------
    # Planes in front of the nose face, nearest first: lamp housing 4 mm,
    # lamps 8 mm, grille 12 mm, grille bars 17 mm. Each back face is buried a
    # different depth behind the face for the same reason.
    hwn = half_w(y0)
    yin = y0 + 0.02
    grille_x = hwn * (0.36 if style == "suv" else 0.30)
    for sx in (-1.0, 1.0):
        xa, xb = grille_x + 0.02, hwn - (0.16 if style != "hatchback" else 0.13)
        xd = hwn - 0.045
        # a dark housing round the lamp pair, so a lens reads on white paint;
        # kept inside the nose face's outline where the shoulder rolls in
        _box(groups["trim"], (min(sx * (xa - 0.012), sx * (xd + 0.010)), y0 - DETAIL_PROUD,
                              lamp_z0 - 0.014),
             (max(sx * (xa - 0.012), sx * (xd + 0.010)), y0 + 0.012, lamp_z1 + 0.008))
        yl = y0 - 2.0 * DETAIL_PROUD
        _box(groups["lamp_head"], (min(sx * xa, sx * xb), yl, lamp_z0),
             (max(sx * xa, sx * xb), yin, lamp_z1))
        xc = xb + 0.012
        _box(groups["lamp_amber"], (min(sx * xc, sx * xd), yl, lamp_z0),
             (max(sx * xc, sx * xd), yin, lamp_z1 - 0.012))
    g_z0, g_z1 = lamp_z0 + 0.008, lamp_z1 - 0.02
    gy = y0 - 3.0 * DETAIL_PROUD
    _box(groups["trim"], (-grille_x, gy, g_z0), (grille_x, y0 + 0.016, g_z1))
    bars = 3 if style == "suv" else 2
    for i in range(bars):
        zc = _lerp(g_z0, g_z1, (i + 1.0) / (bars + 1.0))
        # the bars' back face: gy + 0.01 was tried first and landed 2.0 mm in
        # front of the nose face, back to back (OPP, 152 cm2 on the sedan)
        _box(groups["chrome"], (-grille_x + 0.015, gy - 0.005, zc - 0.009),
             (grille_x - 0.015, y0 + 0.008, zc + 0.009))

    # wipers on the cowl, flat on the hood's back edge
    for x0, x1 in ((-0.52 * hw, -0.06), (0.02 * hw, 0.46 * hw)):
        _box(groups["trim"], (x0, y_ws - 0.075, belt - 0.022),
             (x1, y_ws - 0.045, belt + 0.016))

    # --- tail: lamps, plate recess and plate ------------------------------------
    # Planes behind the tail face, as at the nose: housing 4 mm, lamp 10 mm,
    # reverse lamp 14 mm; plate frame 4 mm and plate 9 mm between the lamps.
    # The housing is what makes a red lens read on a red or maroon car
    # (rendered without it: the lamps disappeared into the paint).
    hwt = half_w(yt)
    ytl = yt + 0.010
    ytin = yt - 0.02
    t_z0, t_z1 = bz1 + 0.05, tail - 0.03
    for sx in (-1.0, 1.0):
        if style in ("sedan", "coupe"):
            xa, xb = 0.24, hwt - 0.045
            za, zb_ = max(t_z0, t_z1 - 0.13), t_z1
        elif style == "hatchback":
            xa, xb = hwt - 0.26, hwt - 0.045
            za, zb_ = t_z0 + 0.05, t_z1
        else:
            xa, xb = hwt - 0.16, hwt - 0.045
            za, zb_ = t_z0, t_z1
        _box(groups["trim"], (min(sx * (xa - 0.012), sx * (xb + 0.010)), yt - 0.012, za - 0.012),
             (max(sx * (xa - 0.012), sx * (xb + 0.010)), yt + DETAIL_PROUD, zb_ + 0.010))
        _box(groups["lamp_tail"], (min(sx * xa, sx * xb), ytin, za),
             (max(sx * xa, sx * xb), ytl, zb_))
        if style in ("sedan", "coupe"):
            ra, rb, rza, rzb = xa + 0.015, xa + 0.10, za + 0.015, zb_ - 0.015
        else:
            ra, rb, rza, rzb = xa + 0.015, xb - 0.015, za + 0.015, za + 0.10
        # The reverse lamp's buried back face sits 6 mm behind the tail face,
        # clear of every plane in the ladder. At yt + 0.006 it was exactly
        # 2 mm off the housing's front, back to back, and the probe counted it
        # on 19 of 150 random slot sizes -- all under 4.0 m long, where float
        # rounding at that Y put 2 mm inside its window (OPP, 144-315 cm2).
        _box(groups["lamp_head"], (min(sx * ra, sx * rb), yt - 0.006, rza),
             (max(sx * ra, sx * rb), yt + 0.014, rzb))
    plate_zc = (t_z0 + t_z1) / 2.0 - (0.05 if style in ("sedan", "coupe") else 0.0)
    _box(groups["trim"], (-0.19, ytin, plate_zc - 0.10),
         (0.19, yt + DETAIL_PROUD, plate_zc + 0.10))
    _box(groups["plate"], (-0.1525, ytin + 0.005, plate_zc - 0.076),
         (0.1525, yt + DETAIL_PROUD + 0.005, plate_zc + 0.076))

    # --- sides: seams, moulding, handles, mirrors, cladding ---------------------
    # Every strip on the door skin runs INTO the body by its own depth, so the
    # buried back faces of two strips that cross are never one plane either.
    z2_at = belt - SHOULDER_H
    door_edges = [openings[0][1][0] - 0.08]
    for kind, e0, e1 in openings:
        if kind in ("door_f", "door_r"):
            door_edges.append(e1[0] + 0.04)
    handle_ys = [e - 0.22 for e in door_edges[1:]]

    def on_skin(bm, sign, depth, proud, ya_, yb_, za, zb2):
        x0, x1 = sign * (hw - depth), sign * (hw + proud)
        _box(bm, (min(x0, x1), ya_, za), (max(x0, x1), yb_, zb2))

    for sign in (-1.0, 1.0):
        for ye in door_edges:
            z_lo = max(z_base(ye) + ROCKER_H, z_well(ye) + 0.012) + 0.02
            on_skin(groups["trim"], sign, SKIN_DEPTH["seam"], SEAM_PROUD, ye - 0.004,
                    ye + 0.004, z_lo, z2_at - 0.01)
        for yh in handle_ys:
            on_skin(groups["trim"], sign, SKIN_DEPTH["handle"], 0.012, yh - 0.08, yh + 0.08,
                    z2_at - 0.075, z2_at - 0.04)
        if f["moulding"]:
            zm = _lerp(clear + ROCKER_H, z2_at, 0.42)

            def clear_of_seams(yy):
                # A moulding end that lands within a seam's reach ends in the
                # seam's middle. Unguarded, the hatchback at 1.75 x 4.30 x 1.45
                # (style 2) ended its moulding 0.31 mm from a seam's face, back
                # to back (OPP, 10.56 cm2).
                for ye in door_edges:
                    if abs(yy - ye) < 0.012:
                        return ye
                return yy

            for ya_, yb_ in ((y0 + 0.30, ya_f - R - 0.03),
                             (ya_f + R + 0.03, ya_r - R - 0.03),
                             (ya_r + R + 0.03, yt - 0.30)):
                ya_, yb_ = clear_of_seams(ya_), clear_of_seams(yb_)
                if yb_ - ya_ >= 0.1:
                    on_skin(groups["trim"], sign, SKIN_DEPTH["moulding"], TRIM_PROUD, ya_, yb_,
                            zm - 0.024, zm + 0.024)
        if f["two_tone"]:
            zc1 = clear + ROCKER_H + 0.20 * H / 1.73
            for ya_, yb_ in ((y0 + 0.30, ya_f - R - 0.02),
                             (ya_f + R + 0.02, ya_r - R - 0.02),
                             (ya_r + R + 0.02, yt - 0.30)):
                if yb_ - ya_ < 0.1:
                    continue
                on_skin(groups["cladding"], sign, SKIN_DEPTH["cladding"], TRIM_PROUD, ya_, yb_,
                        clear + ROCKER_H - 0.005, zc1)
                # the pinstripe's buried face: 0.018 was tried first and sat
                # 2.0 mm from the cladding's 0.016 (SAME, 14.66 cm2 a side,
                # the probe on the 1.75 x 4.30 x 1.45 SUV); see SKIN_DEPTH
                on_skin(groups["chrome"], sign, SKIN_DEPTH["pinstripe"], TRIM_PROUD + 0.004,
                        ya_ + 0.01, yb_ - 0.01, zc1 - 0.006, zc1 + 0.004)
        # mirror: a stalk from the door top, a head whose outer face IS the slot
        ym = y_ws + 0.13
        mirror = groups["trim"] if f["mirror_black"] else groups["body"]
        x0, x1 = sign * (hw - 0.07), sign * (W / 2.0 - 0.06)
        _box(mirror, (min(x0, x1), ym - 0.02, belt - 0.02),
             (max(x0, x1), ym + 0.02, belt + 0.075))
        x0, x1 = sign * (W / 2.0 - 0.105), sign * (W / 2.0)
        _box(mirror, (min(x0, x1), ym - 0.035, belt + 0.03),
             (max(x0, x1), ym + 0.035, belt + 0.155))

    # --- roof rack ----------------------------------------------------------------
    if f["rack"]:
        xr = hwg(1.0) * 0.72
        yr0, yr1 = yF(1.0) + 0.12, yR(1.0) - 0.10
        for sx in (-1.0, 1.0):
            _box(groups["trim"], (sx * xr - 0.016, yr0, H - 0.026),
                 (sx * xr + 0.016, yr1, H))
            for yy in (yr0 + 0.04, (yr0 + yr1) / 2.0, yr1 - 0.04):
                _box(groups["trim"], (sx * xr - 0.02, yy - 0.03, zr - 0.02),
                     (sx * xr + 0.02, yy + 0.03, H - 0.012))
        for yy in (yr0 + 0.30, yr1 - 0.35):
            _box(groups["trim"], (-xr, yy - 0.02, H - 0.019),
                 (xr, yy + 0.02, H - 0.006))

    # --- wheels -------------------------------------------------------------------
    r = wheel_r
    xo = lay["tyre_outer_x"]                      # tyre outer face
    cxw = xo - tyre_w / 2.0
    profile = [(0.62 * r, tyre_w / 2.0), (0.86 * r, tyre_w / 2.0),
               (r, tyre_w / 2.0 - 0.03), (r, -tyre_w / 2.0 + 0.03),
               (0.86 * r, -tyre_w / 2.0), (0.62 * r, -tyre_w / 2.0)]
    kind = f["wheel_kind"]
    recess = {"hubcap": 0.012, "steel": 0.022, "alloy": 0.030}[kind]
    # a steel wheel is painted grey, not the tyre's black: rendered in the
    # trim rubber it read as a black disc on a black tyre
    disc = {"hubcap": groups["chrome"], "steel": groups["bumper_grey"],
            "alloy": groups["trim"]}[kind]
    for ya in (ya_f, ya_r):
        for sign in (-1.0, 1.0):
            _lathe_x(groups["tyres"], sign * cxw, ya, r, profile, seg, sign)
            x_face = sign * (xo - recess)
            x_back = sign * (xo - tyre_w + 0.03)
            xc = (x_face + x_back) / 2.0
            geometry.add_cylinder(disc, (xc, ya, r), 0.645 * r,
                                  abs(x_face - x_back), segments=seg, axis="X")
            cap_r = 0.20 * r if kind == "alloy" else 0.17 * r
            cap_face = sign * (xo - 0.005)
            cap_back = sign * (xo - recess - 0.01)
            geometry.add_cylinder(groups["chrome"], ((cap_face + cap_back) / 2.0, ya, r),
                                  cap_r, abs(cap_face - cap_back), segments=8, axis="X")
            if kind == "alloy":
                sf, sb = sign * (xo - 0.010), sign * (xo - recess - 0.004)
                for k in range(5):
                    a = 2.0 * math.pi * k / 5.0 + math.pi / 2.0
                    ca, sa = math.cos(a), math.sin(a)
                    pa, pb = cap_r * 0.85, 0.58 * r
                    hwd = 0.02 * width_k
                    quad = []
                    for xx in (sb, sf):
                        for rr, ss in ((pa, -hwd), (pb, -hwd), (pb, hwd), (pa, hwd)):
                            quad.append((xx, ya + rr * ca - ss * sa, r + rr * sa + ss * ca))
                    _hexa(groups["chrome"], quad)

    # --- interior -------------------------------------------------------------------
    # Door cards cover the door walls BETWEEN the wheel tubs, never over one.
    # Run the whole cabin, the card's inner face sat over the rear wheel, and
    # on the 1.60 x 3.80 x 1.40 hatchback that face was 0.29 mm from the hub
    # disc's back face (SAME, 193 cm2 a side) -- a size the min / default /
    # max probe matrix never built; the exported GLB's probe found it.
    card_spans = [(max(y_ws + 0.06, ya_f + R + 0.02), min(y_te - 0.06, ya_r - R - 0.02)),
                  (ya_r + R + 0.02, y_te - 0.06)]
    for sign in (-1.0, 1.0):
        x0, x1 = sign * (xi - 0.012), sign * (xi + 0.006)
        for ca, cb in card_spans:
            if cb - ca >= 0.15:
                _box(groups["interior"], (min(x0, x1), ca, floor_z + 0.05),
                     (max(x0, x1), cb, belt - 0.012))
    _box(groups["interior"], (-(xtub - 0.01), y_ws + 0.05, floor_z - 0.01),
         (xtub - 0.01, y_te - 0.05, floor_z + 0.012))
    # dashboard: its top edge stays behind the windshield's inner face
    dash_back = y_ws + 0.42
    _hexa(groups["trim"], [
        (-(xi - 0.005), y_ws + 0.02, belt - 0.20), ((xi - 0.005), y_ws + 0.02, belt - 0.20),
        ((xi - 0.005), dash_back, belt - 0.20), (-(xi - 0.005), dash_back, belt - 0.20),
        (-(xi - 0.005), y_ws + 0.11, belt + 0.026), ((xi - 0.005), y_ws + 0.11, belt + 0.026),
        ((xi - 0.005), dash_back - 0.03, belt + 0.021), (-(xi - 0.005), dash_back - 0.03, belt + 0.021)])
    xd = xi * 0.48                                # driver: +X, the car's left
    _box(groups["trim"], (xd - 0.19, dash_back - 0.16, belt + 0.01),
         (xd + 0.19, dash_back - 0.05, belt + 0.068))
    # steering wheel, facing the driver, tilted back
    tilt = math.radians(28.0)
    nrm = (0.0, math.cos(tilt), math.sin(tilt))
    u = (1.0, 0.0, 0.0)
    v = (0.0, -math.sin(tilt), math.cos(tilt))
    wc = (xd, dash_back + 0.10, belt - 0.02)
    _torus(groups["trim"], wc, u, v, nrm, 0.18, 0.017, seg=10, tube=4)
    _box(groups["trim"], (xd - 0.025, dash_back - 0.02, belt - 0.07),
         (xd + 0.025, wc[1] + 0.01, belt - 0.02))
    seat_z = clear + 0.36
    back_top = min(belt + 0.19, zr - 0.33)
    y_b_pillar = openings[0][2][0]
    y_fs = min(y_b_pillar - 0.30, dash_back + 0.55)
    # a front seat stops 15 mm inside the wheel-tub ledge: at 0.48 m wide it
    # met the ledge wall 1.66 mm apart, back to back, on 1.85 m hatchbacks
    # (OPP, 96 cm2; 3 of 250 random slot sizes)
    seat_w = min(0.48, xi * 0.9, 2.0 * (xtub - 0.015 - xd))
    for sx in (-1.0, 1.0):
        xc = sx * xd
        _box(groups["interior"], (xc - seat_w / 2.0, y_fs - 0.24, floor_z + 0.02),
             (xc + seat_w / 2.0, y_fs + 0.24, seat_z))
        _hexa(groups["interior"], [
            (xc - seat_w / 2.0, y_fs + 0.16, seat_z - 0.06), (xc + seat_w / 2.0, y_fs + 0.16, seat_z - 0.06),
            (xc + seat_w / 2.0, y_fs + 0.28, seat_z - 0.06), (xc - seat_w / 2.0, y_fs + 0.28, seat_z - 0.06),
            (xc - seat_w / 2.0 + 0.02, y_fs + 0.29, back_top), (xc + seat_w / 2.0 - 0.02, y_fs + 0.29, back_top),
            (xc + seat_w / 2.0 - 0.02, y_fs + 0.39, back_top), (xc - seat_w / 2.0 + 0.02, y_fs + 0.39, back_top)])
        _box(groups["interior"], (xc - 0.13, y_fs + 0.31, back_top - 0.03),
             (xc + 0.13, y_fs + 0.39, back_top + 0.15))
    # the rear seat: behind the front seat backs, in front of the tub's end
    # (a coupe's short greenhouse put it past `y_te` at a fixed 0.95 m)
    y_rs = min(y_fs + 0.95, y_te - 0.42)
    if y_rs - 0.24 > y_fs + 0.40:
        xb_ = xtub - 0.02                          # between the wheel tubs
        _box(groups["interior"], (-xb_, y_rs - 0.24, floor_z + 0.02),
             (xb_, y_rs + 0.24, seat_z - 0.02))
        rb_top = min(back_top - 0.03, zr - 0.36)
        _hexa(groups["interior"], [
            (-xb_, y_rs + 0.16, seat_z - 0.08), (xb_, y_rs + 0.16, seat_z - 0.08),
            (xb_, y_rs + 0.28, seat_z - 0.08), (-xb_, y_rs + 0.28, seat_z - 0.08),
            (-(xb_ - 0.02), y_rs + 0.30, rb_top), ((xb_ - 0.02), y_rs + 0.30, rb_top),
            ((xb_ - 0.02), y_rs + 0.40, rb_top), (-(xb_ - 0.02), y_rs + 0.40, rb_top)])

    # --- objects and materials ------------------------------------------------------
    objs = []
    by_group = {}
    names = {"body": "Car_Body", "trim": "Car_Trim", "tyres": "Car_Tyres",
             "chrome": "Car_Chrome", "lamp_head": "Car_Lamp_Head",
             "lamp_tail": "Car_Lamp_Tail", "lamp_amber": "Car_Lamp_Amber",
             "plate": "Car_Plate", "interior": "Car_Interior",
             "cladding": "Car_Cladding", "bumper_grey": "Car_Grey_Paint"}
    for key, bm in groups.items():
        if not bm.verts:
            bm.free()
            continue
        obj = geometry.bm_to_object(bm, names[key], collection, bevel=0.0,
                                    texel=0.5 if key == "body" else 1.0,
                                    rng=rng, wear=wear if key in ("body", "trim", "tyres", "cladding", "bumper_grey") else 0.0)
        objs.append(obj)
        by_group[key] = obj
    glass_objs = []
    for name, bm in panes:
        obj = geometry.bm_to_object(bm, name, collection, bevel=0.0,
                                    texel=0.5, rng=rng, wear=0.0)
        objs.append(obj)
        glass_objs.append(obj)

    kind_paint = plan["material"] if plan["material"] != "glass" else "metal_painted"
    hexcol = "".join("%02x" % max(0, min(255, int(round(c * 255)))) for c in f["paint"])
    mats = {
        "body": materials.make_material(f"M_Car_paint_{hexcol}", list(f["paint"]), kind_paint),
        "trim": materials.make_material("M_Car_trim_rubber", [0.035, 0.035, 0.037], "rubber"),
        "tyres": materials.make_material("M_Car_trim_rubber", [0.035, 0.035, 0.037], "rubber"),
        "chrome": materials.make_material("M_Car_brightwork", [0.66, 0.67, 0.68], "metal_painted"),
        # Lamps are ready to light and unlit: plain lenses whose names do NOT
        # end `_Lens` / `_Diffuser` / `_Face`, the suffixes Lux's emissive
        # binder claims. A night street that wants them lit renames these.
        "lamp_head": materials.make_material("M_Car_headlamp", [0.86, 0.88, 0.87], "metal_painted"),
        "lamp_tail": materials.make_material("M_Car_taillamp", [0.50, 0.03, 0.03], "metal_painted"),
        "lamp_amber": materials.make_material("M_Car_cornerlamp", [0.80, 0.38, 0.03], "metal_painted"),
        "plate": materials.make_material("M_Car_plate", [0.80, 0.78, 0.62], "metal_painted"),
        "interior": materials.make_material(
            f"M_Car_interior_{f['interior']}", list(car_forms.INTERIOR[f["interior"]]), "canvas"),
        "cladding": materials.make_material(
            f"M_Car_cladding_{f['cladding']}", list(car_forms.CLADDING[f["cladding"]]), "metal_painted"),
        "bumper_grey": materials.make_material(
            "M_Car_bumper_grey", list(car_forms.CLADDING["grey"]), "metal_painted"),
    }
    for key, obj in by_group.items():
        materials.assign([obj], mats[key])
    glass = materials.make_see_through_material("M_Car_glass", list(GLASS_TINT), GLASS_OPACITY)
    materials.assign(glass_objs, glass)

    print(f"[car] style={style} ({f['style_how']}) doors={f['doors']} "
          f"paint={f['paint_name']} wheels={f['wheel_kind']} bumpers={f['bumper_kind']} "
          f"rack={f['rack']} two_tone={f['two_tone']} quarter={f['quarter_glass']} "
          f"panes={len(glass_objs)} stations={len(stations)}")

    cboxes = [((-W / 2.0, yF0, clear), (W / 2.0, yR0, belt)),
              ((-hw_gb, y_ws, belt), (hw_gb, y_bl, zr))]
    return {"objects": objs, "collision_boxes": cboxes,
            "form": {k: v for k, v in f.items() if not isinstance(v, tuple)},
            "attachments": {"ATT_roof": (0.0, (y_rf + y_rr) / 2.0, zr),
                            "ATT_driver_seat": (xd, y_fs, seat_z),
                            "ATT_trunk": (0.0, (y_bl + yt) / 2.0 if trunk else yt, deck)}}
