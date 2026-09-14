"""Vault door forms (pure): the numbers a round bank vault door is built from.

`recipes/vault_door.py` turns these into bmesh; everything that decides WHERE
something is -- the portal circle, the stepped frame, the leaf's swing, the
collision a state advises -- lives here so it can be tested without Blender.

FRAME AND UNITS. Module-local, centre pivot, metres: x across the slot
(width), y through the wall (thickness, +y is the FACE the approach sees),
z up. The module's floor is z = -h/2. Deli Counter's slot transform owns
which world direction +y points.

HANDEDNESS. Standing in front of the face and looking at it (along -y), +x
is on the viewer's LEFT. The references hang the hinges on the left, so the
hinges are at +x and the dial and pull at -x. The first render had them the
other way round -- every position was self-consistent and the whole door
was a mirror image -- which is why this is written down.

THE PORTAL CIRCUMSCRIBES THE AUTHORED APERTURE. Deli Counter writes the
opening it gated -- `{"kind": "vault", "width", "height", "sill"}` -- and its
nav and clearance checks were run against that rectangle. A round door that
fitted INSIDE the rectangle would silently shrink a passage somebody already
measured, so the circle is drawn through the rectangle's four corners instead:

    zc = sill + height / 2          R = hypot(width / 2, height / 2)

The circle then dips below the sill line, and the portal is cut flat there.
At the cut the chord is exactly the authored width, so the clear passage is
never narrower than the rectangle at any height inside it. The flat is what
lets a body walk through: a full circle standing on the floor has a chord of
zero at the floor.

THE MODULE MUST BE WIDER THAN THE APERTURE. The frame, the hinges and the
riveted surround need room outside the circle. `required_size` says how much.
A slot smaller than that still builds -- the whole door at a slot that holds
the aperture, scaled uniformly across and up to the real one (`fit_scale`) --
and the recipe prints `VAULT_PORTAL_UNDERSIZED` with the clear width that
is left. That result no longer honours the authored clearance, and says so.
"""
from __future__ import annotations

import math

#: The states Deli Counter's `vault_door` machine carries (interactives.py).
STATES = ("locked", "unlocked", "open", "breached")
#: The door is in its frame; the slot is solid.
CLOSED_STATES = ("locked", "unlocked")

#: Aperture used when a slot describes none (a standalone build). The body
#: contract's clearances: `min_door_width_m` 1.25 rounded up, 2.1 m against
#: `min_headroom_m` 2.0. See deli_counter/agent_contract.json.
DEFAULT_OPENING = {"width": 1.3, "height": 2.1, "sill": 0.0}

DEFAULTS = {
    "frame_frac": 0.22,       # frame radial width as a fraction of R
    "margin": 0.10,           # surround left beyond the frame and hinges
    "open_swing_deg": 100.0,  # leaf rotation about the hinge axis when open
    "breach_swing_deg": 122.0,
    "breach_tilt_deg": 13.0,  # blown leaf leans off its hinges
    "bolts": 16,              # locking bolts round the leaf edge
    "bolt_length": 0.16,      # how far an extended bolt stands off the edge
    "collision_bands": 6,     # boxes the passage is tiled with
}

#: Clearances between parts that share a plane, in metres. Each is a gap that
#: exists only so two faces do not coincide (zoo/tools/coplanar_probe.py);
#: none of them is meant to be seen.
CUT_BODY = 0.0        # the surround is cut exactly at the sill plane
#: REFUTED, kept: 0.003 / 0.001 / 0.012 / 0.018. The probe's tolerance is
#: 2 mm, so the plate's underside 1 mm off the surround's and 2 mm off the
#: frame's feet were two coincident pairs of 1988 and 1455 cm2.
CUT_FRAME = 0.009     # frame feet sit 9 mm above the sill plane
THRESHOLD_BOTTOM = 0.005
THRESHOLD_TOP = 0.016  # a 16 mm plate: under agent_contract unassisted 0.1025
CUT_LEAF = 0.022      # the leaf clears the threshold plate by 6 mm
DOOR_GAP = 0.012      # radial gap between leaf and frame lining
LINING = 0.09         # frame lining thickness inside the wall
BODY_HOLE = 0.10      # the surround's hole is this much larger than R
#: The lining steps OUT twice toward the vault side -- the stepped jamb of a
#: real round vault door. Out, never in: the portal radius R is the clearance
#: and nothing inside the wall may be narrower than the lip.
JAMB_STEPS = ((0.62, 0.03), (0.33, 0.06))   # (fraction back->lip, extra r)
KNUCKLE = 1.12        # knuckle ring radius over barrel radius
BOSS_BACK = 0.02      # the leaf's back boss stands this far inside the slot
BOSS_DEPTH = 0.04     # and this far proud of the plug's back face

#: WHAT THE DOOR IS MADE OF. The plates, straps, rivets, frame, leaf, bars,
#: hinges and boss are PAINTED steel -- the genome's kind, `metal_painted` --
#: and only the hand-worn and machined hardware is bare: the wheel, the dial
#: and pull, the locking bolts and the brass bolt heads. `HARDWARE_KIND` is a
#: constant, as the fire hydrant's chains are, because one object with two
#: finishes is not a species offering two materials.
#:
#: REFUTED, kept: 0.83.0 skinned the WHOLE door `metal_bare`. Godot 4.7
#: frames of bank_branch_a02 showed the 3.6 x 3.3 m surround and the leaf
#: covered in long horizontal black streaks where the walker's references
#: show a clean riveted painted face. Measured, in order:
#:   * UVs first, and not the cause: every triangle of every part of the
#:     locked and open GLBs maps 1.000 UV units per metre along both of its
#:     in-plane axes (0 m2 with a singular value under 0.25);
#:   * the delco_1997 `metal_bare_neutral` pack's roughness map is two values
#:     in horizontal bars, 42 and 85 of 255 (0.165 and 0.333; the dark bars
#:     27% of the tile), row-mean std 14.3 against column-mean 2.8, at one
#:     128 px tile per metre -- and the material is metallic 0.9, so the
#:     glossy bars mirror the dark room;
#:   * the same GLBs with ONLY that map's green channel flattened to its mean
#:     (73) photographed at the same Godot station lost every streak.
#: The pack's grain is Pixelcoat's to judge; painting a painted door is Zoo's.
HARDWARE_KIND = "metal_bare"
HARDWARE_PARTS = ("BoltHeads", "LeafBolts", "Hardware", "BossBolts", "Bolts",
                  "Wheel")


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


# --------------------------------------------------------------------- sizing

def portal_radius(ow: float, oh: float) -> float:
    """Radius of the circle through an ow x oh rectangle's corners."""
    return math.hypot(ow / 2.0, oh / 2.0)


def frame_width(r: float, frac: float = DEFAULTS["frame_frac"]) -> float:
    return _clamp(frac * r, 0.16, 0.34)


def hinge_radius(r: float) -> float:
    # REFUTED, kept: 0.09 * r (clamped 0.07..0.13) rendered 0.22 m barrels
    # beside a 2.5 m door, which read as door hinges, not vault hinges.
    return _clamp(0.12 * r, 0.09, 0.16)


def required_size(ow: float, oh: float, sill: float = 0.0,
                  params: dict | None = None) -> dict:
    """The smallest slot (width, height) that builds this aperture unshrunk.

    Deli Counter needs this before it lays the wall run out, because the
    module replaces the whole slot and the slot is what it sizes. Width is the
    circle, the frame, the hinge barrels standing outside the frame and a
    margin of surround each side; height is the sill, the circle's top, the
    frame and the margin.
    """
    p = dict(DEFAULTS)
    p.update(params or {})
    r = portal_radius(ow, oh)
    fw = frame_width(r, p["frame_frac"])
    rb = hinge_radius(r)
    return {"width": round(2.0 * (r + fw + 1.25 * rb + p["margin"]), 4),
            "height": round(sill + oh / 2.0 + r + fw + p["margin"], 4),
            "portal_radius": round(r, 4)}


def fit_scale(w: float, d: float, h: float, opening: dict | None = None,
              params: dict | None = None) -> float:
    """The uniform x/z scale an undersized slot is built at; 1.0 when the
    slot holds the aperture unshrunk.

    An undersized slot is built as the whole door at ``(w / s, h / s)`` --
    a slot that DOES hold the aperture -- and then scaled by ``s`` across and
    up, so it stays round, fits exactly, and keeps every proportion. REFUTED,
    kept: shrinking only the portal radius inside the real slot left the
    wheel, its knobs and the bars at their minimum sizes, and Deli Counter's
    own 1.4 m vault slot built 3.499 m tall in a 3.3 m slot. The clearance is
    lost either way; this loses it without breaking the fit, and says by how
    much.
    """
    v = plan_vault(w, d, h, opening, params)
    if v["shortfall"] <= 0.005:
        return 1.0
    need = v["required"]
    return min(1.0, w / need["width"], h / need["height"])


def depth_allocation(t: float) -> dict:
    """Where each face of the closed door sits through the wall, by y.

    One unit `u` of proud relief is carved out of the slot's own depth, so
    the closed module fits its slot exactly: hinge barrels and the wheel
    rim reach the face plane `f`, the surround panels sit one `u` behind it,
    and the frame steps and the leaf face fall between. A thin partition
    gets a shallow door; a vault wall authored thick gets a thick one.
    """
    u = _clamp(0.35 * t, 0.08, 0.22)
    f = t / 2.0
    y_pan = f - u
    return {
        "u": u, "f": f, "back": -f,
        "y_pan": y_pan,
        "body_back": -f + min(0.03, 0.1 * t),
        "y_outer": y_pan + 0.26 * u,     # frame outer step
        "y_mid": y_pan + 0.48 * u,       # frame middle step
        "y_inner": y_pan + 0.70 * u,     # frame inner step (the lip)
        "y_door": y_pan + 0.35 * u,      # leaf face, recessed below the lip
        # the plug's back face; its boltwork boss stands BOSS_DEPTH behind it
        "y_leaf_back": -f + BOSS_BACK + BOSS_DEPTH,
    }


def plan_vault(w: float, d: float, h: float, opening: dict | None = None,
               params: dict | None = None, unit: float = 1.0) -> dict:
    """Every size and position the recipe and the collision derive from.

    ``unit`` is built metres per real metre across and up -- ``1 / s`` for a
    door built large and scaled by `fit_scale`'s ``s``. The gaps that exist
    only to keep faces apart (``v["cut"]``) are multiplied by it, so they
    come out of the scale at their real size. REFUTED, kept: unscaled, a
    0.36 scale turned every 4 mm gap into 1.44 mm and the probe found 7
    same-facing pairs on Deli Counter's own 1.4 m slot.
    """
    p = dict(DEFAULTS)
    p.update({k: v for k, v in (params or {}).items() if k in DEFAULTS})
    op = dict(DEFAULT_OPENING)
    for k in ("width", "height", "sill"):
        val = (opening or {}).get(k)
        if val is None:
            continue
        val = float(val)
        # a zero width or height describes no aperture; a zero sill is real
        if val > 0.0 or (k == "sill" and val == 0.0):
            op[k] = val
    hw, hh = w / 2.0, h / 2.0
    sill = _clamp(op["sill"], 0.0, 0.5 * h)
    ow = op["width"]
    oh = min(op["height"], h - sill - 0.05)
    z_cut = -hh + sill
    zc = z_cut + oh / 2.0
    r_want = portal_radius(ow, oh)
    fw = frame_width(r_want, p["frame_frac"])
    rb = hinge_radius(r_want)
    r_by_w = hw - p["margin"] - fw - 1.25 * rb
    r_by_h = hh - p["margin"] - fw - zc
    r = min(r_want, r_by_w, r_by_h)
    dz = zc - z_cut
    if r < dz + 0.06:
        # The slot cannot hold the circle at this centre. Lower the centre so
        # the portal still meets the sill with a usable chord; the clearance
        # the aperture asked for is gone either way, and `shortfall` says so.
        dz = max(0.05, r - 0.12)
        zc = z_cut + dz
    half_clear = math.sqrt(max(0.0, r * r - dz * dz))
    shortfall = round(max(0.0, r_want - r), 4)
    fw = frame_width(r, p["frame_frac"])
    # A BARREL MAY NOT BE DEEPER THAN THE WALL. Its knuckle rings are 1.12 rb
    # and the barrel's front is tangent to the face plane, so 2.24 rb must
    # fit in the slot depth. REFUTED, kept: sized from r alone, a 0.3 m slot
    # built 0.332 m deep -- rings 18 mm past the face and 14 mm past the
    # back -- and the 2 cm fit tolerance had hidden the same 18 mm at 0.6 m.
    rb = min(hinge_radius(r), d / 2.3)
    yy = depth_allocation(d)
    rd = r - DOOR_GAP
    # leaf steps: as deep as 0.10 m, but every stepped radius must still
    # cross the leaf's own cut line or the flat-bottomed lathe has no edge.
    cut = {"body": CUT_BODY * unit, "frame": CUT_FRAME * unit,
           "th_bottom": THRESHOLD_BOTTOM * unit,
           "th_top": THRESHOLD_TOP * unit, "leaf": CUT_LEAF * unit}
    dz_leaf = zc - (z_cut + cut["leaf"])
    step = min(0.10, 0.6 * (rd - dz_leaf))
    step = step if step >= 0.012 else 0.0
    # hinge barrels straddle the frame's outer rim, one above and one below
    # the portal centre
    hz = 0.52 * r
    lb = _clamp(0.28 * r, 0.25, 0.40)
    rim_x = math.sqrt(max(0.0, (r + fw) ** 2 - hz * hz))
    x_h = rim_x + 0.25 * rb              # viewer's left; see HANDEDNESS
    y_h = yy["f"] - KNUCKLE * rb         # the knuckle ring is tangent to f
    wheel_r = _clamp(0.30 * r, 0.25, 0.42)
    return {
        "w": w, "d": d, "h": h, "hw": hw, "hh": hh,
        "opening": {"width": ow, "height": oh, "sill": sill},
        "z_cut": z_cut, "zc": zc, "r": r, "r_want": r_want, "dz": dz,
        "half_clear": half_clear, "shortfall": shortfall,
        "required": required_size(ow, oh, sill, p),
        "fw": fw, "rb": rb, "rd": rd, "leaf_step": step,
        "hinge": {"x": x_h, "y": y_h, "z": (zc - hz, zc + hz), "len": lb,
                  "r": rb},
        "wheel_r": wheel_r,
        "y": yy,
        "unit": unit, "cut": cut,
        "params": p,
    }


# -------------------------------------------------------------- 2D outlines

def truncated_circle(cx: float, cz: float, r: float, z_min: float,
                     n: int = 32):
    """CCW (x, z) outline of the disc of radius ``r`` above ``z_min``.

    Returns ``(points, cut)``. Uncut, it is a plain n-gon. Cut, it runs from
    the right end of the chord over the top to the left end, both ends exactly
    on ``z_min``; the chord itself is the closing edge.
    """
    if z_min <= cz - r + 1e-9:
        return ([(cx + r * math.cos(2 * math.pi * k / n),
                  cz + r * math.sin(2 * math.pi * k / n)) for k in range(n)],
                False)
    s = (z_min - cz) / r
    if s >= 1.0 - 1e-9:
        raise ValueError("cut line %.4f is above the circle top" % z_min)
    t0 = math.asin(s)
    t1 = math.pi - t0
    m = max(2, int(math.ceil(n * (t1 - t0) / (2 * math.pi))))
    pts = []
    for i in range(m + 1):
        t = t0 + (t1 - t0) * i / m
        pts.append((cx + r * math.cos(t), cz + r * math.sin(t)))
    pts[0] = (pts[0][0], z_min)
    pts[-1] = (pts[-1][0], z_min)
    return pts, True


def polygon_area(pts) -> float:
    s = 0.0
    for k in range(len(pts)):
        x1, y1 = pts[k]
        x2, y2 = pts[(k + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def surround_outline(hw: float, hh: float, cz: float, r_hole: float,
                     z_cut: float, n: int = 32):
    """The riveted surround's face: the slot rectangle less the portal.

    Returns ``(outer, holes)`` in (x, z), both CCW. When the portal's flat
    bottom lies on the module floor the hole is not a hole but a notch, and
    the two outlines are merged into one horseshoe with no holes -- a hole
    touching its outer boundary is not something a fill can take.
    """
    rect = [(hw, -hh), (hw, hh), (-hw, hh), (-hw, -hh)]
    hole, cut = truncated_circle(0.0, cz, r_hole, z_cut, n)
    if cut and z_cut <= -hh + 1e-4:
        hole = [(x, -hh) if abs(z - z_cut) < 1e-9 else (x, z) for x, z in hole]
        return rect + list(reversed(hole)), []
    return rect, [hole]


# ---------------------------------------------------------------- lathe mesh

def cut_lathe(profile, cz: float, z_min: float, n: int = 32,
              closed: bool = True, cx: float = 0.0):
    """Revolve a (radius, y) profile about the y axis, cut flat at ``z_min``.

    ``closed=True``: the profile is a loop and the result a ring (a frame, a
    collar). ``closed=False``: the profile runs from the axis back out to the
    axis (first and last radius 0, each joined to its neighbour at the same
    y) and the result is a solid (a stepped leaf). Returns ``(verts, faces)``
    with verts as (x, y, z) and faces as index tuples, wound consistently.

    One closed manifold solid, not a stack of discs. Stacked discs of stepped
    radii all cut at one plane would lay their flat bottoms in that plane,
    facing the same way, and the depth buffer would decide between them.

    Every radius must cross the cut line, or none may: a profile straddling
    it would need a bottom face that is part chord and part arc, which this
    does not build. That is a planning error and it raises.
    """
    pts = [(float(r), float(y)) for r, y in profile]
    if not closed:
        if pts[0][0] != 0.0 or pts[-1][0] != 0.0:
            raise ValueError("an open profile starts and ends on the axis")
        if abs(pts[0][1] - pts[1][1]) > 1e-9 or abs(pts[-1][1] - pts[-2][1]) > 1e-9:
            raise ValueError("the axis joins must be flat caps")
        ring = pts[1:-1]
    else:
        ring = pts
    radii = [p[0] for p in ring]
    rmin, rmax = min(radii), max(radii)
    if rmin <= 0.0:
        raise ValueError("ring radii must be positive")
    dz = cz - z_min
    if z_min <= cz - rmax + 1e-9:
        cut = False
    elif rmin > dz + 1e-4:
        cut = True
    else:
        raise ValueError("profile straddles the cut: rmin %.4f vs %.4f"
                         % (rmin, dz))
    if cut:
        t0_of = [math.asin(-dz / rr) for rr in radii]
        span = max(math.pi - 2.0 * t for t in t0_of)
        m = max(2, int(math.ceil(n * span / (2.0 * math.pi))))
        samples = m + 1
    else:
        m = n
        samples = n
    verts = []
    index = []
    for k, (rr, yy) in enumerate(ring):
        row = []
        for i in range(samples):
            if cut:
                t0 = t0_of[k]
                t = t0 + (math.pi - 2.0 * t0) * i / m
                z = z_min if i in (0, m) else cz + rr * math.sin(t)
            else:
                t = 2.0 * math.pi * i / n
                z = cz + rr * math.sin(t)
            row.append(len(verts))
            verts.append((cx + rr * math.cos(t), yy, z))
        index.append(row)
    P = len(ring)
    faces = []

    def strip(a, b):
        for i in range(m if cut else n):
            i2 = i + 1 if cut else (i + 1) % n
            faces.append((index[a][i], index[a][i2], index[b][i2],
                          index[b][i]))

    if closed:
        for k in range(P):
            strip(k, (k + 1) % P)
        if cut:
            faces.append(tuple(index[k][0] for k in range(P)))
            faces.append(tuple(index[k][m] for k in reversed(range(P))))
    else:
        for k in range(P - 1):
            strip(k, k + 1)
        if cut:
            faces.append(tuple(reversed([index[0][i] for i in range(m + 1)])))
            faces.append(tuple(index[P - 1][i] for i in range(m + 1)))
            faces.append(tuple([index[k][0] for k in range(P)]
                               + [index[k][m] for k in reversed(range(P))]))
        else:
            faces.append(tuple(reversed(index[0])))
            faces.append(tuple(index[P - 1]))
    return verts, faces


def leaf_profile(v: dict, extra_front: float = 0.0):
    """The stepped leaf's (radius, y) profile, axis to axis."""
    y = v["y"]
    rd, step = v["rd"], v["leaf_step"]
    yb, yf = y["y_leaf_back"], y["y_door"] + extra_front
    t = yf - yb
    if step <= 0.0:
        return [(0.0, yb), (rd, yb), (rd, yf), (0.0, yf)]
    half = step / 2.0
    return [(0.0, yb), (rd - step, yb), (rd - step, yb + 0.25 * t),
            (rd - half, yb + 0.25 * t), (rd - half, yb + 0.5 * t),
            (rd, yb + 0.5 * t), (rd, yf), (0.0, yf)]


def jamb_steps(v: dict):
    """[(y_from, y_to, radius)] of the lining's inner surface, back to lip."""
    y = v["y"]
    back, lip, r = y["back"], y["y_inner"], v["r"]
    (f2, e2), (f1, e1) = JAMB_STEPS
    y1 = back + f1 * (lip - back)
    y2 = back + f2 * (lip - back)
    return [(back, y1, r + e1), (y1, y2, r + e2), (y2, lip, r)]


def lining_radius_at(v: dict, yy: float) -> float:
    for y0, y1, rr in jamb_steps(v):
        if y0 <= yy <= y1:
            return rr
    return v["r"]


def frame_profile(v: dict):
    """The frame ring's (radius, y) loop: back flange, a stepped lining
    through the wall, and three steps descending outward on the face."""
    y = v["y"]
    r, fw = v["r"], v["fw"]
    back = y["back"]
    flange_in = y["body_back"] + 0.012     # buried 12 mm in the surround
    face_in = y["y_pan"] - 0.012
    (b0, b1, rb_), (m0, m1, rm_), (_l0, _l1, _rl) = jamb_steps(v)
    return [(rb_, back), (rb_, b1), (rm_, b1), (rm_, m1), (r, m1),
            (r, y["y_inner"]),
            (r + 0.30 * fw, y["y_inner"]), (r + 0.30 * fw, y["y_mid"]),
            (r + 0.62 * fw, y["y_mid"]), (r + 0.62 * fw, y["y_outer"]),
            (r + fw, y["y_outer"]), (r + fw, face_in),
            (r + LINING, face_in), (r + LINING, flange_in),
            (r + 0.14, flange_in), (r + 0.14, back)]


# ------------------------------------------------------------ transforms

def mat_identity():
    return ((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0))


def mat_mul(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(4))
                       for j in range(4)) for i in range(4))


def mat_apply(m, p):
    x, y, z = p
    return (m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3],
            m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3],
            m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3])


def mat_axis_angle(point, axis, ang):
    """Rotation by ``ang`` radians about ``axis`` through ``point``
    (right hand rule)."""
    ax, ay, az = axis
    ln = math.sqrt(ax * ax + ay * ay + az * az)
    ax, ay, az = ax / ln, ay / ln, az / ln
    c, s = math.cos(ang), math.sin(ang)
    k = 1.0 - c
    rot = ((c + ax * ax * k, ax * ay * k - az * s, ax * az * k + ay * s),
           (ay * ax * k + az * s, c + ay * ay * k, ay * az * k - ax * s),
           (az * ax * k - ay * s, az * ay * k + ax * s, c + az * az * k))
    px, py, pz = point
    t = [point[i] - sum(rot[i][j] * (px, py, pz)[j] for j in range(3))
         for i in range(3)]
    return ((rot[0][0], rot[0][1], rot[0][2], t[0]),
            (rot[1][0], rot[1][1], rot[1][2], t[1]),
            (rot[2][0], rot[2][1], rot[2][2], t[2]),
            (0.0, 0.0, 0.0, 1.0))


def leaf_matrix(v: dict, state: str):
    """Where the leaf goes in each state, as a 4x4 row-major matrix.

    Closed: nowhere. Open: swung about the hinge axis (vertical, through the
    barrels at +x), clockwise seen from above, so the leaf travels toward +y
    and out of the wall rather than into it. Breached: swung further,
    then leaned away from its hinges about its own bottom edge on the vault
    side, so the edge stays on the floor and nothing rises into the passage.
    """
    hg = v["hinge"]
    p = v["params"]
    if state in CLOSED_STATES or state is None:
        return mat_identity()
    swing = p["open_swing_deg"] if state == "open" else p["breach_swing_deg"]
    phi = math.radians(swing)
    m = mat_axis_angle((hg["x"], hg["y"], 0.0), (0.0, 0.0, 1.0), -phi)
    if state != "breached":
        return m
    # the leaf's width direction after the swing; rotating about it by a
    # positive angle carries the leaf's top toward its own back face
    u_axis = (math.cos(phi), -math.sin(phi), 0.0)
    pivot = mat_apply(m, (0.0, v["y"]["y_leaf_back"],
                          v["z_cut"] + v["cut"]["leaf"]))
    tilt = mat_axis_angle(pivot, u_axis, math.radians(p["breach_tilt_deg"]))
    return mat_mul(tilt, m)


# ------------------------------------------------------------- collision

def passage_bands(v: dict):
    """Rectangles, in (x0, x1, z0, z1), tiling the portal from the sill up.

    Each band is as wide as the circle's chord at the band's edge FARTHEST
    from the centre, so every band sits inside the circle and collision never
    claims less than the visual frame does. The bottom band's half width is
    the chord at the sill, which is the authored width -- so the passage the
    collision leaves is never narrower than the aperture Deli Counter gated.
    """
    zc, r, z_cut = v["zc"], v["r"], v["z_cut"]
    # REFUTED, kept: the top was `zc + 0.8 * r`. For the default 1.3 x 2.1
    # aperture that is 0.99 m above the centre while the rectangle's top is
    # 1.05 m above it, so the passage stopped 6 cm short of the headroom Deli
    # Counter gated. The top is the rectangle's own top whenever that is
    # higher, which also makes the top band exactly the authored width.
    top = zc + min(0.95 * r, max(0.8 * r, v["dz"]))
    k = int(v["params"]["collision_bands"])
    edges = [z_cut + (top - z_cut) * i / k for i in range(k + 1)]
    out = []
    for i in range(k):
        za, zb = edges[i], edges[i + 1]
        far = max(abs(za - zc), abs(zb - zc))
        half = math.sqrt(max(0.0, r * r - far * far))
        out.append((-half, half, za, zb))
    return out


def frame_collision(v: dict):
    """AABBs of the frame with its passage open: the slot box less the bands,
    through the full slot depth."""
    hw, hh, t = v["hw"], v["hh"], v["d"]
    y0, y1 = -t / 2.0, t / 2.0
    boxes = []
    bands = passage_bands(v)
    z_bottom = bands[0][2]
    if z_bottom > -hh + 1e-4:
        boxes.append(((-hw, y0, -hh), (hw, y1, z_bottom)))
    for x0, x1, za, zb in bands:
        boxes.append(((-hw, y0, za), (x0, y1, zb)))
        boxes.append(((x1, y0, za), (hw, y1, zb)))
    z_top = bands[-1][3]
    if z_top < hh - 1e-4:
        boxes.append(((-hw, y0, z_top), (hw, y1, hh)))
    return boxes


def slot_collision(v: dict):
    """A closed door is the whole slot."""
    return [((-v["hw"], -v["d"] / 2.0, -v["hh"]),
             (v["hw"], v["d"] / 2.0, v["hh"]))]


def leaf_local_extent(v: dict, state: str):
    """(x0, x1, y0, y1, z0, z1) of everything that rides with the leaf, in
    its closed pose: the stepped plug, the hardware on its face, the hinge
    arms back to the barrel axis and any bolts standing off the edge."""
    bolt = v["params"]["bolt_length"] if state == "open" else 0.04
    rd = v["rd"] + bolt
    return (-rd, v["hinge"]["x"], v["y"]["y_leaf_back"], v["y"]["f"],
            v["z_cut"] + v["cut"]["leaf"], v["zc"] + rd)


def leaf_collision(v: dict, state: str, chunks: int = 4):
    """AABBs covering the leaf in its state's pose.

    The leaf is cut into ``chunks`` slices across its width, each slice's
    height taken from the circle over that slice, and each slice's eight
    corners carried through `leaf_matrix`. The boxes are a superset of the
    leaf -- an axis-aligned box round a turned slab always is -- and that is
    the conservative side for something a body should walk around.
    """
    if state in CLOSED_STATES:
        return []
    m = leaf_matrix(v, state)
    x0, x1, y0, y1, z0, z1 = leaf_local_extent(v, state)
    zc = v["zc"]
    rr = z1 - zc
    out = []
    for c in range(chunks):
        xa = x0 + (x1 - x0) * c / chunks
        xb = x0 + (x1 - x0) * (c + 1) / chunks
        near = 0.0 if xa <= 0.0 <= xb else min(abs(xa), abs(xb))
        top = zc + math.sqrt(max(0.0, rr * rr - near * near))
        top = max(top, v["hinge"]["z"][1] + v["hinge"]["len"] / 2.0)
        pts = [mat_apply(m, (x, y, z)) for x in (xa, xb) for y in (y0, y1)
               for z in (z0, top)]
        lo = tuple(min(p[i] for p in pts) for i in range(3))
        hi = tuple(max(p[i] for p in pts) for i in range(3))
        out.append((lo, hi))
    return out


def state_collision(v: dict, state: str):
    """The collision `interactives.py` advises per state, as AABBs:
    locked/unlocked solid, open and breached a passable frame with the leaf
    as a solid wherever it now stands."""
    if state in CLOSED_STATES or state is None:
        return slot_collision(v)
    return frame_collision(v) + leaf_collision(v, state)


def bolt_angles(v: dict):
    """Angles (radians, 0 = +x, CCW in x/z) of the locking bolts round the
    leaf edge, skipping the arc down by the flat bottom where the leaf has no
    edge to carry one.

    REFUTED, kept: the first cut skipped everything below 0.35 of the
    aperture height, so an open leaf showed four bolts along its top and the
    'ring of large bolts' in the reference read as a few pins."""
    n = int(v["params"]["bolts"])
    out = []
    for k in range(n):
        t = math.pi / 2.0 + 2.0 * math.pi * k / n
        z = v["zc"] + v["rd"] * math.sin(t)
        if z < v["z_cut"] + v["cut"]["leaf"] + 0.15:
            continue
        out.append(t)
    return out


def port_angles(v: dict, y_bolt: float, port_r: float = 0.042):
    """The bolt angles whose port -- standing 6 mm proud of the lining --
    keeps clear of every passage band. A port the collision leaves inside
    the passage would be a lump a body walks into and cannot see coming."""
    rr = lining_radius_at(v, y_bolt) - 0.006
    bands = passage_bands(v)
    out = []
    for t in bolt_angles(v):
        tx, tz = rr * math.cos(t), v["zc"] + rr * math.sin(t)
        # the port's inner cap is a disc of radius port_r about (tx, tz) in
        # the plane through the axis; its x/z reach is port_r either way
        if any(x0 - port_r < tx < x1 + port_r and za - port_r < tz < zb + port_r
               for x0, x1, za, zb in bands):
            continue
        out.append(t)
    return out


def boxes_overlap(a, b, eps: float = 1e-9) -> bool:
    return all(a[0][i] < b[1][i] - eps and b[0][i] < a[1][i] - eps
               for i in range(3))
