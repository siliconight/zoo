"""vault_door recipe: a round bank vault door, one module per interactive state.

Deli Counter's `vault_door` machine (interactives.py) names four states --
locked, unlocked, open, breached -- and this species builds each of them from
the slot's own dims and authored aperture. The state rides in on
``plan["module"]["state"]`` (None is the default, locked).

What a person should read, state by state:

* locked -- a riveted steel wall in a strap grid; a stepped round frame; a
  thick round leaf with an eight-spoke wheel in a riveted ring, five locking
  bars running out to keepers on the frame, a combination dial with a small
  spoked handle, a U pull; two massive hinge barrels on the left.
* unlocked -- the same door with the wheel turned a sixteenth, the bars drawn
  back out of their keepers, the dial and handle turned.
* open -- the leaf swung about its hinge axis, its stepped edge and a ring of
  extended bolts showing; bolt ports in the frame lining; the passage clear.
* breached -- the leaf torn off its hinges, over-swung and leaning, scorched
  round the lock; the wheel blown onto the floor; sheared bars on the leaf and
  sheared bolt blocks left in the keepers; steel shards on the floor.

Every position comes from `core.vault_forms`, which is pure and tested. This
file only turns those numbers into meshes, which is also why no part here is
placed by eye: a bolt that looked right would not be guaranteed to stay out
of the passage the collision leaves open.

THE CLOSED DOOR FITS ITS SLOT EXACTLY. The open and breached leaf cannot -- a
2.5 m leaf swung 100 degrees stands 2.5 m in front of the wall -- so those
states return ``fit_objects``: the frame, which fits the slot exactly, and
which `bpylayer.build` measures the fit and the pivot on. The leaf's reach is
recorded as overhang, not hidden and not squeezed.
"""
from __future__ import annotations

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from ..bpylayer import geometry, materials
from ..core import arch
from ..core import vault_forms as vf

#: Bars run out from the wheel ring at these angles (degrees, 0 = +x, CCW in
#: x/z): up, and toward the hinges -- upper-left, left, lower-left as the
#: viewer sees them, because +x is the viewer's left (vault_forms,
#: HANDEDNESS) -- and down. The dial and the pull sit on the viewer's right.
BAR_ANGLES = (90.0, 45.0, 0.0, -45.0, 270.0)

#: Lathe segments per full turn. The portal-scale rings read round at 40
#: while every facet stays visible under the theme's flat banded light.
N_BIG, N_MID, N_SMALL = 40, 24, 12

#: Crease threshold for curved parts. A 40-segment ring's neighbouring facets
#: meet at 9 degrees and blend; a step's 90-degree corner stays hard.
SMOOTH_CURVED = 30.0

#: How deep each detail's hidden back face sits below the surface it stands
#: on, in metres. EVERY ENTRY IS 4 MM FROM ITS NEIGHBOURS -- two share a
#: value only where the parts can never overlap (the dial and the pull's
#: posts) -- and that is the whole point of the table.
#: `tools/coplanar_probe.py` reports any two
#: parallel same-facing faces within 2 mm that overlap in projection, and the
#: first build of this door had nine such pairs -- all of them buried inside
#: other solids, all of them 0-2 mm apart because each offset had been picked
#: where the part was written. The worst was a hinge arm whose back
#: (f - 1.5 * rb = 0.0777) landed 0.28 mm from the frame's buried face plane
#: (y_pan - 0.012 = 0.0780): two formulas with nothing in common agreeing to
#: a quarter of a millimetre. One table, one spacing, no coincidences.
LEAF_BACK = {           # below the leaf face, y_door
    "bars": 0.004, "dial": 0.008, "posts": 0.008, "wheel_hub": 0.016,
    "spinner_hub": 0.020, "bezel": 0.012, "blocks": 0.024,
    "face_ring": 0.028, "band": 0.032, "marker": 0.036, "char": 0.040,
}
PANEL_BACK = {          # below the surround face, y_pan
    "strap_v": 0.003, "strap_h": 0.007, "strap_border": 0.011,
    "strap_top": 0.015, "hinge_plate": 0.019,
}
PANEL_FRONT = {         # proud of the surround face, y_pan
    "strap_h": 0.008, "strap_v": 0.012, "strap_border": 0.016,
    "strap_top": 0.021,
}


def _add(bm, verts, faces, matrix=None):
    vs = []
    for co in verts:
        p = Vector(co)
        if matrix is not None:
            p = matrix @ p
        vs.append(bm.verts.new(p))
    for f in faces:
        bm.faces.new([vs[i] for i in f])
    return vs


def _lathe(bm, profile, cz, z_min, n, closed=True, cx=0.0):
    verts, faces = vf.cut_lathe(profile, cz, z_min, n, closed=closed, cx=cx)
    return _add(bm, verts, faces)


def _ring(bm, cx, cz, r0, r1, y0, y1, n):
    """An uncut annulus about the y axis through (cx, cz)."""
    return _lathe(bm, [(r0, y0), (r1, y0), (r1, y1), (r0, y1)], cz, -1e6, n,
                  closed=True, cx=cx)


def _prism(bm, outer, holes, y0, y1):
    """Extrude an (x, z) outline with holes between two y planes."""
    front_edges, back_edges = [], []
    for loop in [outer] + list(holes):
        fv = [bm.verts.new((x, y1, z)) for x, z in loop]
        bv = [bm.verts.new((x, y0, z)) for x, z in loop]
        k = len(loop)
        for i in range(k):
            j = (i + 1) % k
            bm.faces.new((fv[i], fv[j], bv[j], bv[i]))
        for i in range(k):
            j = (i + 1) % k
            front_edges.append(bm.edges.get((fv[i], fv[j])))
            back_edges.append(bm.edges.get((bv[i], bv[j])))
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False,
                            edges=front_edges, normal=(0.0, 1.0, 0.0))
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False,
                            edges=back_edges, normal=(0.0, -1.0, 0.0))


def _obox(bm, c, ax, ay, az, sx, sy, sz):
    """A box centred on ``c`` with edges along unit vectors ax, ay, az."""
    c, ax, ay, az = Vector(c), Vector(ax), Vector(ay), Vector(az)
    vs = []
    for i in (-1, 1):
        for j in (-1, 1):
            for k in (-1, 1):
                vs.append(bm.verts.new(c + ax * (i * sx / 2.0)
                                       + ay * (j * sy / 2.0)
                                       + az * (k * sz / 2.0)))
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6),
              (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([vs[i] for i in f])
    return vs


def _box(bm, lo, hi):
    c = [(lo[i] + hi[i]) / 2.0 for i in range(3)]
    s = [hi[i] - lo[i] for i in range(3)]
    return _obox(bm, c, (1, 0, 0), (0, 1, 0), (0, 0, 1), *s)


def _radial_box(bm, cx, cz, ang, r_mid, radial, tang, y0, y1):
    """A box lying on the face, long axis radial at ``ang`` (radians)."""
    u = (math.cos(ang), 0.0, math.sin(ang))
    t = (-math.sin(ang), 0.0, math.cos(ang))
    c = (cx + r_mid * u[0], (y0 + y1) / 2.0, cz + r_mid * u[2])
    return _obox(bm, c, u, (0, 1, 0), t, radial, y1 - y0, tang)


def _cyl(bm, p0, p1, r, n, cap0=True, cap1=True, phase=0.0):
    """A cylinder from p0 to p1 of radius r."""
    p0, p1 = Vector(p0), Vector(p1)
    axis = p1 - p0
    a = axis.normalized()
    ref = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    e1 = a.cross(ref).normalized()
    e2 = a.cross(e1).normalized()
    r0, r1 = [], []
    for i in range(n):
        t = phase + 2.0 * math.pi * i / n
        off = e1 * (r * math.cos(t)) + e2 * (r * math.sin(t))
        r0.append(bm.verts.new(p0 + off))
        r1.append(bm.verts.new(p1 + off))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    if cap0:
        bm.faces.new(list(reversed(r0)))
    if cap1:
        bm.faces.new(r1)


def _stud(bm, x, y, z, r0, r1, height, n=6, embed=0.002, sign=1.0):
    """A rivet or bolt head on a face looking along ``sign`` * y: a frustum
    with no hidden base."""
    base = [bm.verts.new((x + r0 * math.cos(2 * math.pi * i / n + 0.26),
                          y - sign * embed,
                          z + r0 * math.sin(2 * math.pi * i / n + 0.26)))
            for i in range(n)]
    top = [bm.verts.new((x + r1 * math.cos(2 * math.pi * i / n + 0.26),
                         y + sign * height,
                         z + r1 * math.sin(2 * math.pi * i / n + 0.26)))
           for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((base[i], base[j], top[j], top[i]))
    bm.faces.new(top)


def _petal(bm, base, radial, normal, length, width, bend, thick=0.012,
           sink=0.012):
    """One torn tongue of plate peeled back out of a blast hole: a thin
    wedge rooted ``sink`` inside the face, bent ``bend`` radians up off it."""
    base, radial, normal = Vector(base), Vector(radial), Vector(normal)
    tangent = normal.cross(radial).normalized()
    tipdir = radial * math.cos(bend) + normal * math.sin(bend)
    pn = normal * math.cos(bend) - radial * math.sin(bend)
    root = base - normal * sink
    tri = [root - tangent * (width / 2.0), root + tangent * (width / 2.0),
           base + tipdir * length]
    lo = [bm.verts.new(p - pn * (thick / 2.0)) for p in tri]
    hi = [bm.verts.new(p + pn * (thick / 2.0)) for p in tri]
    bm.faces.new(lo)
    bm.faces.new(list(reversed(hi)))
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))


def _rosette(char, petals_bm, cx, cz, yface, sign, rng, r_core=0.15, n=9):
    """A blast hole: a charred core and torn plate peeled out of it."""
    _cyl(char, (cx, yface - sign * 0.004, cz),
         (cx, yface + sign * 0.006, cz), r_core, 12)
    for k in range(n):
        a = 2.0 * math.pi * k / n + rng.random() * 0.35
        radial = (math.cos(a), 0.0, math.sin(a))
        base = (cx + 0.8 * r_core * radial[0], yface,
                cz + 0.8 * r_core * radial[2])
        _petal(petals_bm, base, radial, (0.0, sign, 0.0),
               0.14 + rng.random() * 0.16, 0.07 + rng.random() * 0.06,
               math.radians(28.0 + rng.random() * 42.0))


def _scorch(obj, centre, radius, strength):
    """Darken the exported wear colour toward a blast centre."""
    me = obj.data
    attr = me.color_attributes.get(geometry.WEAR_LAYER)
    if attr is None:
        return
    c = Vector(centre)
    for li, loop in enumerate(me.loops):
        co = me.vertices[loop.vertex_index].co
        dist = (co - c).length
        k = 1.0 - strength * math.exp(-(dist / radius) ** 2)
        col = attr.data[li].color
        attr.data[li].color = (col[0] * k, col[1] * k * 0.97,
                               col[2] * k * 0.94, col[3])


def build(plan, streams, collection):
    dims = plan["dimensions"]
    w, d, h = dims["width"], dims["depth"], dims["height"]
    params = plan.get("params", {})
    state = (plan.get("module") or {}).get("state") or "locked"
    if state not in vf.STATES:
        state = "locked"
    slot_w, slot_h = w, h
    scale = vf.fit_scale(w, d, h, params.get("opening"), params)
    if scale < 1.0:
        # built whole at a slot that holds the aperture, scaled to this one
        w, h = w / scale, h / scale
    v = vf.plan_vault(w, d, h, params.get("opening"), params,
                      unit=1.0 / scale)
    g = v["unit"]                         # a real millimetre, in built units
    cut = v["cut"]
    if scale < 1.0:
        print("[zoo] VAULT_PORTAL_UNDERSIZED slot %.2f x %.2f cannot hold the "
              "authored %.2f x %.2f aperture (needs %.2f x %.2f); the door is "
              "built at x%.3f across and up, so its clear width at the sill "
              "is %.2f m -- narrower than the aperture Deli Counter gated"
              % (slot_w, slot_h, v["opening"]["width"],
                 v["opening"]["height"], v["required"]["width"],
                 v["required"]["height"], scale,
                 2.0 * v["half_clear"] * scale))

    rng = streams.stream("wear")
    wear = plan["wear"]
    ambient = plan.get("ambient", 0.0)
    style = plan.get("style_block") or {}
    # THE STEEL IS THE SPECIES', NOT THE WALL'S. `resolve_module_plan` lets
    # a slot's material override the genome's so a wall run can be brick or
    # drywall -- and a vault door set in a concrete partition would come out
    # a concrete door. The style block's kind is what the genome says the
    # door is made of; the slot's own kind is only the fallback.
    kind = style.get("material") or plan["material"]
    steel = list(plan["color"])
    root = arch.root_name("vault_door")

    def mat(tag, color, k=kind):
        return materials.make_material(f"M_VaultDoor_{k}_{tag}", color, k)

    # PAINTED plates and BARE hardware (vault_forms.HARDWARE_KIND, and the
    # refutation above it: a bare-metal surround wore the pack's glossy
    # roughness bars as black streaks across 3.6 m of plate)
    bright = style.get("bright", [min(1.0, c * 1.35) for c in steel])
    m_steel = mat("steel", steel)
    m_bright = mat("bright", bright)
    m_dark = mat("dark", style.get("dark", [c * 0.45 for c in steel]))
    # the strap grid a shade under the plates, so the seams read at distance
    m_strap = mat("strap", [c * 0.78 for c in steel])
    m_hw = mat("bright", bright, vf.HARDWARE_KIND)
    m_brass = mat("brass", style.get("accent", [0.72, 0.55, 0.26]),
                  vf.HARDWARE_KIND)

    fit_objs, leaf_objs, loose_objs = [], [], []

    # the finish table is vault_forms'; a part wired to the other finish is a
    # defect here, not a look (undecidable only if the genome's kind were the
    # hardware's own, when the two finishes are one material)
    hardware = ({m_hw.name, m_brass.name} if kind != vf.HARDWARE_KIND
                else None)

    def emit(bm, name, material, group, smooth=0.0, texel=1.0):
        if hardware is not None:
            assert (name in vf.HARDWARE_PARTS) == (material.name in hardware), (
                name, material.name)
        if not bm.verts:
            bm.free()
            return None
        obj = geometry.bm_to_object(bm, f"{root}_{name}", collection,
                                    bevel=0.0, texel=texel, rng=rng,
                                    wear=wear, ambient=ambient,
                                    smooth_angle=smooth)
        materials.assign([obj], material)
        group.append(obj)
        return obj

    y = v["y"]
    u, f = y["u"], y["f"]
    hw, hh = v["hw"], v["hh"]
    zc, r, fw, rb = v["zc"], v["r"], v["fw"], v["rb"]
    z_cut = v["z_cut"]
    hg = v["hinge"]
    rd = v["rd"]
    wr = v["wheel_r"]
    closed = state in vf.CLOSED_STATES
    turned = state != "locked"            # the unlocked pose, and after it

    # ---------------------------------------------------------- the frame
    bm = geometry.new_bm()
    outer, holes = vf.surround_outline(hw, hh, zc, r + vf.BODY_HOLE,
                                       z_cut + cut["body"], N_BIG)
    _prism(bm, outer, holes, y["body_back"], y["y_pan"])
    emit(bm, "Surround", m_steel, fit_objs)

    bm = geometry.new_bm()
    _lathe(bm, vf.frame_profile(v), zc, z_cut + cut["frame"], N_BIG)
    emit(bm, "Frame", m_steel, fit_objs, smooth=SMOOTH_CURVED)

    chord = math.sqrt(max(0.0, (r + fw) ** 2 - (zc - z_cut) ** 2))
    bm = geometry.new_bm()
    _box(bm, (-(chord + 0.02), -d / 2.0 + 0.004, z_cut + cut["th_bottom"]),
         (chord + 0.02, min(y["y_inner"] + 0.03, f - 0.003),
          z_cut + cut["th_top"]))
    emit(bm, "Threshold", m_dark, fit_objs)

    # hinge barrels, knuckles and pins (the frame half of the hinge)
    # 0.40 u: a pure multiple of u, so it can never cross the frame's own
    # steps (0.26 u, 0.48 u) at any wall thickness, and at the thinnest
    # (u = 0.08) it still clears the proudest strap by 11 mm
    plate_hi = y["y_pan"] + 0.40 * u
    plate_x0 = hg["x"] + 0.2 * rb
    plate_x1 = min(hg["x"] + rb + 0.20, hw - 0.02)
    bm = geometry.new_bm()
    bolts = geometry.new_bm()
    for i, hz in enumerate(hg["z"]):
        half = hg["len"] / 2.0
        top = hz + half
        if state == "breached" and i == 0:
            top = hz + 0.15 * half           # the lower barrel is torn short
        _cyl(bm, (hg["x"], hg["y"], hz - half), (hg["x"], hg["y"], top),
             rb, N_SMALL)
        for zend, sgn in ((hz - half, -1.0), (top, 1.0)):
            _cyl(bm, (hg["x"], hg["y"], zend - sgn * 0.02),
                 (hg["x"], hg["y"], zend + sgn * 0.015), rb * vf.KNUCKLE,
                 N_SMALL)
            _cyl(bm, (hg["x"], hg["y"], zend + sgn * 0.012),
                 (hg["x"], hg["y"], zend + sgn * 0.05), rb * 0.45, 8)
        _box(bm, (plate_x0, y["y_pan"] - PANEL_BACK["hinge_plate"],
                  hz - 0.42 * hg["len"]),
             (plate_x1, plate_hi, hz + 0.42 * hg["len"]))
        for bx in (plate_x1 - 0.05, (plate_x0 + plate_x1) / 2.0):
            for bz in (hz - 0.30 * hg["len"], hz + 0.30 * hg["len"]):
                _stud(bolts, bx, plate_hi, bz, 0.024, 0.019, 0.014)
        if state == "breached":
            # a torn stub of the leaf's arm left in the barrel
            # stays 3 cm under a torn barrel's knuckle ring, whose top
            # a 0.12 len stub once met to 0.56 mm
            _box(bm, (hg["x"] - rb - 0.14, hg["y"] - 0.4 * rb,
                      hz - 0.2 * hg["len"]),
                 (hg["x"], hg["y"] + 0.4 * rb,
                  min(hz + 0.12 * hg["len"], top - 0.03)))
    emit(bm, "Hinges", m_steel, fit_objs, smooth=SMOOTH_CURVED)

    # keepers on the frame at each bar's end
    keeper_angles = []
    for deg in BAR_ANGLES:
        a = math.radians(deg)
        rk = r + 0.12
        lowest = zc + rk * math.sin(a) - 0.12
        if lowest < z_cut + 0.05:
            continue                          # it would stand in the floor
        keeper_angles.append(a)
    bm = geometry.new_bm()
    # REFUTED, kept: y_inner + 0.22 u. Its bolt heads (0.014 m) then topped
    # out at y_pan + 0.92 u + 0.014, past the face plane whenever u < 0.175 --
    # a 0.3 m slot built 5.6 mm deep over, inside the fit check's 2 cm.
    keeper_front = min(y["y_inner"] + 0.22 * u, f - 0.020)
    for a in keeper_angles:
        _radial_box(bm, 0.0, zc, a, r + 0.12, 0.20, 0.18,
                    y["y_outer"] - 0.004, keeper_front)
        for off in (-0.05, 0.05):
            px = (r + 0.12 + off) * math.cos(a)
            pz = zc + (r + 0.12 + off) * math.sin(a)
            _stud(bolts, px, keeper_front, pz, 0.024, 0.019, 0.014)
        if state == "breached":
            # the bolt block sheared off its bar, left in the keeper
            _radial_box(bm, 0.0, zc, a, r + 0.06, 0.10, 0.13,
                        y["y_inner"] - 0.01, keeper_front + 0.008)
    emit(bm, "Keepers", m_steel, fit_objs)

    # bolt ports in the lining, where the bolts live when the door is shut
    t_leaf = y["y_door"] - y["y_leaf_back"]
    y_bolt = y["y_leaf_back"] + 0.75 * t_leaf
    if not closed:
        bm = geometry.new_bm()
        r_port = vf.lining_radius_at(v, y_bolt)
        for a in vf.port_angles(v, y_bolt):
            ca, sa = math.cos(a), math.sin(a)
            _cyl(bm, ((r_port + 0.03) * ca, y_bolt, zc + (r_port + 0.03) * sa),
                 ((r_port - 0.006) * ca, y_bolt, zc + (r_port - 0.006) * sa),
                 0.042, 10)
        emit(bm, "BoltPorts", m_dark, fit_objs, smooth=SMOOTH_CURVED)

    # ------------------------------------------------ the riveted surround
    sw = 0.075 * g
    # the grid and the rivet pitch are counted in the SLOT's metres: an
    # undersized slot is built large and scaled down, and a 9 m tall built
    # surround gridded at 1 m came out 11,376 triangles of 4 mm rivets
    ncol = max(2, int(round(slot_w / 1.1)))
    nrow = max(2, int(round(slot_h / 1.0)))
    r_clip = r + 0.45 * fw
    xs = [-hw + w * k / ncol for k in range(1, ncol)]
    zs = [-hh + h * k / nrow for k in range(1, nrow)]

    def clip(c0, near, lo, hi):
        """Segments of a strap line [lo, hi] that stay out of the frame."""
        if near >= r_clip:
            return [(lo, hi)]
        reach = math.sqrt(r_clip * r_clip - near * near)
        segs = []
        if c0 - reach > lo + 0.05:
            segs.append((lo, c0 - reach))
        if c0 + reach < hi - 0.05:
            segs.append((c0 + reach, hi))
        return segs

    straps = geometry.new_bm()
    rivets = geometry.new_bm()
    pitch = 0.16 / scale
    plate_rects = [(plate_x0 - 0.03, plate_x1 + 0.03,
                    hz - 0.42 * hg["len"] - 0.03, hz + 0.42 * hg["len"] + 0.03)
                   for hz in hg["z"]]

    def free_of_plates(x, z):
        return not any(a <= x <= b and c <= z <= e
                       for a, b, c, e in plate_rects)

    def rivet_run(fixed, lo, hi, vertical, yface, avoid):
        n = int((hi - lo - 0.08) / pitch)
        for k in range(n + 1):
            s = lo + 0.04 + (hi - lo - 0.08) * (k / n if n else 0.5)
            if any(abs(s - q) < sw / 2.0 + 0.03 for q in avoid):
                continue
            x, z = (fixed, s) if vertical else (s, fixed)
            if free_of_plates(x, z):
                _stud(rivets, x, yface, z, 0.016, 0.010, 0.010)

    y_v, y_h_s, y_b, y_t = (y["y_pan"] + PANEL_FRONT["strap_v"],
                            y["y_pan"] + PANEL_FRONT["strap_h"],
                            y["y_pan"] + PANEL_FRONT["strap_border"],
                            y["y_pan"] + PANEL_FRONT["strap_top"])
    # the strap ends' offsets from the module edges are gaps, in real mm
    e4, e6, e9, e14 = 0.004 * g, 0.006 * g, 0.009 * g, 0.014 * g
    z_lo_v, z_hi_v = -hh + e4, hh - e14
    for x0 in xs:
        for a, b in clip(zc, max(0.0, abs(x0) - sw / 2.0), z_lo_v, z_hi_v):
            _box(straps, (x0 - sw / 2.0, y["y_pan"] - PANEL_BACK["strap_v"],
                          a),
                 (x0 + sw / 2.0, y_v, b))
            rivet_run(x0, a, b, True, y_v, zs + [hh - e9 - sw / 2.0])
    x_lo_h, x_hi_h = -hw + e14, hw - e14
    for z0 in zs:
        for a, b in clip(0.0, max(0.0, abs(z0 - zc) - sw / 2.0),
                         x_lo_h, x_hi_h):
            _box(straps, (a, y["y_pan"] - PANEL_BACK["strap_h"],
                          z0 - sw / 2.0),
                 (b, y_h_s, z0 + sw / 2.0))
            rivet_run(z0, a, b, False, y_h_s,
                      xs + [-(hw - e6 - sw / 2.0), hw - e6 - sw / 2.0])
    for sgn in (-1.0, 1.0):
        xa, xb = sorted((sgn * (hw - e6 - sw), sgn * (hw - e6)))
        _box(straps, (xa, y["y_pan"] - PANEL_BACK["strap_border"],
                      -hh + e4),
             (xb, y_b, hh - e6))
        rivet_run((xa + xb) / 2.0, -hh + e4, hh - e6, True, y_b,
                  zs + [hh - e9 - sw / 2.0])
    _box(straps, (-hw + e9, y["y_pan"] - PANEL_BACK["strap_top"],
                  hh - e9 - sw),
         (hw - e9, y_t, hh - e9))
    rivet_run(hh - e9 - sw / 2.0, -hw + e9, hw - e9, False, y_t,
              xs + [-(hw - e6 - sw / 2.0), hw - e6 - sw / 2.0])
    emit(straps, "Straps", m_strap, fit_objs)
    emit(rivets, "Rivets", m_bright, fit_objs)

    # brass bolts round the frame's outer step
    r_bolt_ring = r + 0.81 * fw
    n_ring = max(12, int(2.0 * math.pi * r_bolt_ring / 0.20))
    for k in range(n_ring):
        a = 2.0 * math.pi * (k + 0.5) / n_ring
        x = r_bolt_ring * math.cos(a)
        z = zc + r_bolt_ring * math.sin(a)
        if z < z_cut + 0.07:
            continue
        if any(abs(x - hg["x"]) < rb + 0.08 and abs(z - hz) < hg["len"] / 2.0 + 0.08
               for hz in hg["z"]):
            continue
        if any(abs(math.atan2(math.sin(a - ka), math.cos(a - ka))) * r_bolt_ring < 0.16
               for ka in keeper_angles):
            continue
        _stud(bolts, x, y["y_outer"], z, 0.034, 0.026, 0.020)
    emit(bolts, "BoltHeads", m_brass, fit_objs)

    # ------------------------------------------------------------- the leaf
    lg = leaf_objs if not closed else fit_objs
    bm = geometry.new_bm()
    _lathe(bm, vf.leaf_profile(v), zc, z_cut + cut["leaf"], N_BIG,
           closed=False)
    emit(bm, "Leaf", m_steel, lg, smooth=SMOOTH_CURVED)

    # the boltwork boss on the back of the leaf, seen when it swings open
    back = geometry.new_bm()
    back_studs = geometry.new_bm()
    boss_r = 0.62 * r
    y_boss = -f + vf.BOSS_BACK
    if zc - boss_r > z_cut + cut["leaf"] + 0.02:
        _lathe(back, [(0.0, y_boss), (boss_r, y_boss),
                      (boss_r, y["y_leaf_back"] + 0.01),
                      (0.0, y["y_leaf_back"] + 0.01)],
               zc, -1e6, N_BIG, closed=False)
        _box(back, (-0.17, y_boss - 0.014, zc - 0.13),
             (0.17, y_boss + 0.006, zc + 0.13))
        # rods: back 6 mm off the housing's, front 4 mm off it and 10 mm
        # inside the boss, so no pair of their faces is within the probe's
        # 2 mm tolerance of another
        for k in range(4):
            a = math.pi / 4.0 + k * math.pi / 2.0
            _radial_box(back, 0.0, zc, a, (0.2 + boss_r - 0.1) / 2.0,
                        boss_r - 0.3, 0.06, y_boss - 0.008, y_boss + 0.010)
        n_bs = 18
        for k in range(n_bs):
            a = 2.0 * math.pi * (k + 0.5) / n_bs
            _stud(back_studs, (boss_r - 0.06) * math.cos(a), y_boss,
                  zc + (boss_r - 0.06) * math.sin(a), 0.022, 0.016, 0.011,
                  sign=-1.0)
        for sx_ in (-0.13, 0.13):
            for sz_ in (-0.09, 0.09):
                _stud(back_studs, sx_, y_boss - 0.014, zc + sz_, 0.018,
                      0.013, 0.004, sign=-1.0)

    face = geometry.new_bm()
    # a raised band round the leaf's edge, cut flat with the leaf
    band_front = y["y_door"] + 0.10 * u
    try:
        _lathe(face, [(rd - 0.17, y["y_door"] - LEAF_BACK["band"]),
                      (rd - 0.05, y["y_door"] - LEAF_BACK["band"]),
                      (rd - 0.05, band_front), (rd - 0.17, band_front)],
               zc, z_cut + cut["leaf"] + 0.004 * g, N_BIG)
    except ValueError:
        pass                       # the leaf is too flat-bottomed for a band
    ring_r0, ring_r1 = wr + 0.03, wr + 0.13
    ring_front = y["y_door"] + 0.12 * u
    if zc - ring_r1 > z_cut + cut["leaf"] + 0.02:
        _ring(face, 0.0, zc, ring_r0, ring_r1,
              y["y_door"] - LEAF_BACK["face_ring"],
              ring_front, N_MID)
    leaf_bolts = geometry.new_bm()
    # sixteen at a half-step off the spokes: 11.25 degrees from every spoke
    # in both the locked pose and the turned one. REFUTED, kept: twelve at
    # (k + 0.5) * 30 put one at 45 degrees, under a locked spoke, and on a
    # 0.3 m wall its head met the spoke's back to 0.35 mm.
    for k in range(16):
        a = 2.0 * math.pi * (k + 0.5) / 16
        _stud(leaf_bolts, (wr + 0.08) * math.cos(a), ring_front,
              zc + (wr + 0.08) * math.sin(a), 0.018, 0.012, 0.011)

    # locking bars and their end blocks
    bars = geometry.new_bm()
    bar_front = y["y_door"] + 0.25 * u
    block_front = y["y_door"] + 0.40 * u
    # 1.5 cm past where the wheel's knobs begin (wr + 0.05): a bar starting
    # there shared the knob's inner end plane, and on a thin wall the two
    # overlap in depth
    r0 = wr + 0.065
    for deg in BAR_ANGLES:
        a = math.radians(deg)
        r1 = rd - 0.10 - (0.12 if turned else 0.0)
        # keep the end block on the leaf above its flat bottom
        while r1 > r0 + 0.1 and (zc + (r1 + 0.07) * math.sin(a)
                                 - 0.08 * abs(math.cos(a))
                                 < z_cut + cut["leaf"] + 0.03):
            r1 -= 0.02
        if state == "breached":
            r1 = r0 + 0.35 * (r1 - r0)       # sheared off
        _radial_box(bars, 0.0, zc, a, (r0 + r1) / 2.0, r1 - r0, 0.11,
                    y["y_door"] - LEAF_BACK["bars"], bar_front)
        if state != "breached":
            _radial_box(bars, 0.0, zc, a, r1, 0.16, 0.20,
                        y["y_door"] - LEAF_BACK["blocks"], block_front)

    # arms: the leaf half of each hinge, from the barrel axis over the lip
    # inside the barrel's radius of its axis, so it stays in the barrel
    # however far the leaf swings
    # ... and 18 mm under the face plane, so its 14 mm bolt heads stay in
    arm_front = min(y["y_inner"] + 0.18 * u, hg["y"] + 0.9 * rb, f - 0.018)
    arm_x1 = rd - 0.30
    for hz in hg["z"]:
        x_from = hg["x"] if state != "breached" else rd + 0.02
        # the arm's back 2 cm over the leaf's rim band (front y_door +
        # 0.10 u, which a fixed 2 cm met to 1 mm at u = 0.21): clear of
        # every buried plane in LEAF_BACK and of the frame's
        _box(bars, (arm_x1, y["y_door"] + 0.10 * u + 0.02,
                    hz - 0.36 * hg["len"]),
             (x_from, arm_front, hz + 0.36 * hg["len"]))
        n_ab = 3
        for k in range(n_ab):
            bx = x_from + (arm_x1 - x_from) * (k + 0.5) / n_ab
            _stud(leaf_bolts, bx, arm_front, hz, 0.024, 0.019, 0.014)

    # dial, its small spoked handle, and the U pull
    hard = geometry.new_bm()
    char = geometry.new_bm()
    x_d, z_d = -0.55 * r, zc + 0.10 * r
    x_s, z_s = x_d, z_d - 0.30
    if state != "breached":
        # at least 4 cm proud: at 0.26 u a thin wall's dial stood 27 mm
        dial_front = y["y_door"] + max(0.26 * u, 0.04)
        _ring(leaf_bolts, x_d, z_d, 0.085, 0.125,
              y["y_door"] - LEAF_BACK["bezel"],
              y["y_door"] + 0.16 * u, 20)
        _cyl(hard, (x_d, y["y_door"] - LEAF_BACK["dial"], z_d),
             (x_d, dial_front, z_d),
             0.095, 20)
        knob_front = min(dial_front + 0.05, f - 0.008)
        _cyl(hard, (x_d, dial_front - 0.003, z_d), (x_d, knob_front, z_d),
             0.035, 12)
        tick = math.radians(90.0 if not turned else 200.0)
        _radial_box(hard, x_d, z_d, tick, 0.06, 0.05, 0.014,
                    dial_front - 0.005, dial_front + 0.006)
        _box(leaf_bolts, (x_d - 0.01, y["y_door"] - LEAF_BACK["marker"],
                          z_d + 0.14),
             (x_d + 0.01, y["y_door"] + 0.03, z_d + 0.18))
        # at least 5 cm proud, so the ball ends' backs stay over the face:
        # at 0.30 u on a 0.3 m wall they sank to 0.5 mm off the bezel's back
        spin_front = y["y_door"] + max(0.30 * u, 0.05)
        _cyl(hard, (x_s, y["y_door"] - LEAF_BACK["spinner_hub"], z_s),
             (x_s, spin_front, z_s),
             0.04, 12)
        for k in range(3):
            a = math.radians((90.0 if not turned else 150.0) + 120.0 * k)
            _radial_box(hard, x_s, z_s, a, 0.09, 0.14, 0.024,
                        spin_front - 0.034, spin_front - 0.012)
            _radial_box(hard, x_s, z_s, a, 0.165, 0.04, 0.04,
                        spin_front - 0.044, spin_front - 0.004)
    else:
        # the charge went in at the lock: the dial and its handle are gone,
        # and the plate is torn open on both faces where they were
        brng = streams.stream("breach")
        petals = geometry.new_bm()
        _rosette(char, petals, x_d, z_d - 0.12, y["y_door"], 1.0, brng)
        _rosette(char, petals, x_d, z_d - 0.12, y_boss, -1.0, brng,
                 r_core=0.19, n=11)
        emit(petals, "TornPlate", m_dark, lg)
    x_u = -0.80 * r
    y_g = min(f - 0.03, y["y_door"] + 0.55 * u + 0.04)
    _cyl(hard, (x_u, y_g, zc - 0.22), (x_u, y_g, zc + 0.22), 0.028, 10)
    for dzp in (-0.18, 0.18):
        _cyl(hard, (x_u, y["y_door"] - LEAF_BACK["posts"], zc + dzp),
             (x_u, y_g + 0.01, zc + dzp), 0.024, 10)

    # the wheel: hub, eight spokes through a rim, knobs on the spoke ends
    wheel = geometry.new_bm()
    spin = math.radians(22.5 if turned else 0.0)
    _cyl(hard, (0.0, y["y_door"] - LEAF_BACK["wheel_hub"], zc),
         (0.0, f - 0.012, zc), 0.085,
         N_SMALL)
    if state != "breached":
        _cyl(hard, (0.0, f - 0.015, zc), (0.0, f - 0.004, zc), 0.05, N_SMALL)
    def _wheel_into(target, cx, cy, cz, ang0):
        _ring(target, cx, cz, wr - 0.045, wr, cy - 0.055, cy, N_MID)
        for k in range(8):
            a = ang0 + math.pi * k / 4.0
            _radial_box(target, cx, cz, a, (0.06 + wr + 0.07) / 2.0,
                        wr + 0.01, 0.034, cy - 0.045, cy - 0.018)
            _radial_box(target, cx, cz, a, wr + 0.075, 0.05, 0.05,
                        cy - 0.050, cy - 0.006)

    if state != "breached":
        _wheel_into(wheel, 0.0, f, zc, spin)
    else:
        _wheel_into(wheel, 0.0, 0.0, 0.0, spin)

    emit(face, "FaceRing", m_bright, lg, smooth=SMOOTH_CURVED)
    emit(bars, "Bars", m_steel, lg)
    emit(hard, "Hardware", m_hw, lg, smooth=SMOOTH_CURVED)
    emit(leaf_bolts, "LeafBolts", m_brass, lg)
    emit(back, "Boss", m_steel, lg, smooth=SMOOTH_CURVED)
    emit(back_studs, "BossBolts", m_hw, lg)
    m_char = mat("char", [0.035, 0.032, 0.03])
    emit(char, "Char", m_char, lg)

    # bolts standing off the edge once the leaf is out of the frame
    if not closed:
        bm = geometry.new_bm()
        length = v["params"]["bolt_length"] if state == "open" else 0.03
        for a in vf.bolt_angles(v):
            ca, sa = math.cos(a), math.sin(a)
            _cyl(bm, ((rd - 0.03) * ca, y_bolt, zc + (rd - 0.03) * sa),
                 ((rd + length) * ca, y_bolt, zc + (rd + length) * sa),
                 0.052, 12)
        emit(bm, "Bolts", m_hw, lg, smooth=SMOOTH_CURVED)

    if state != "breached":
        wobj = emit(wheel, "Wheel", m_hw, lg, smooth=SMOOTH_CURVED)
    else:
        wobj = None

    # ------------------------------------------------------ breach damage
    blast = (-0.55 * r, f, zc)
    if state == "breached":
        # REFUTED, kept: radius 0.65 r at strength 0.80 did reach the export
        # (Hardware COLOR_0 mean 0.26 against 0.83 open) and could not be
        # seen -- it darkened the lock hardware, which faces away once the
        # leaf has swung, and the frame sits just outside that radius.
        back_blast = (blast[0], y_boss, blast[2])
        for obj in fit_objs:
            _scorch(obj, blast, 1.0 * r, 0.90)
        for obj in leaf_objs:
            _scorch(obj, blast, 0.75 * r, 0.90)
            _scorch(obj, back_blast, 0.60 * r, 0.85)

    m_leaf = vf.leaf_matrix(v, state)
    if not closed:
        mm = Matrix(m_leaf)
        for obj in leaf_objs:
            obj.data.transform(mm)
            obj.data.update()

    if state == "breached":
        # the wheel, blown off, lying face up on the floor in front
        wobj = emit(wheel, "Wheel", m_hw, loose_objs, smooth=SMOOTH_CURVED)
        if wobj is not None:
            # lying on its rim face, tipped 2.5 degrees onto a spoke knob:
            # (rim 0.055 m) + 2 * wr * sin(2.5) stays under the 0.1025 m a
            # body walks over (agent_contract unassisted_step_max_m)
            tip = math.radians(2.5)
            tilt = Matrix.Rotation(tip, 4, "Y")
            lay = Matrix.Rotation(math.radians(-90.0), 4, "X")
            place = Matrix.Translation((-0.35 * r, d / 2.0 + 0.95,
                                        -hh + 0.002 + wr * math.sin(tip)))
            wobj.data.transform(place @ tilt @ lay)
            wobj.data.update()
        srng = streams.stream("shards")
        shards = geometry.new_bm()
        for k in range(11):
            sx = 0.06 + srng.random() * 0.12
            sy = 0.05 + srng.random() * 0.10
            sz = 0.014 + srng.random() * 0.03
            cx = -1.1 + srng.random() * 2.0
            cy = d / 2.0 + 0.15 + srng.random() * 1.4
            # ONE BMESH PER SHARD. REFUTED, kept: fracturing each shard in
            # the shared bmesh and moving the vert list `fracture` returned
            # left the verts its cuts made behind at the module origin, 1.65 m
            # up -- the first breached render stood a sheaf of black spikes
            # in the doorway. Everything in a shard's own bmesh is the shard.
            sb = bmesh.new()
            vs = _obox(sb, (0.0, 0.0, 0.0), (1, 0, 0), (0, 1, 0), (0, 0, 1),
                       sx, sy, sz)
            vs = geometry.subdivide(sb, vs, cuts=1)
            geometry.fracture(sb, vs, srng, cuts=2, near=0.2, far=0.7,
                              radius=max(sx, sy) / 2.0, steep=0.7)
            live = list(sb.verts)
            low = min(p.co.z for p in live)
            geometry.place(live, (cx, cy, -hh - low - 0.003),
                           rot_z=srng.random() * 6.283)
            tmp = bpy.data.meshes.new("VaultShardTmp")
            sb.to_mesh(tmp)
            sb.free()
            shards.from_mesh(tmp)
            bpy.data.meshes.remove(tmp)
        emit(shards, "Shards", m_dark, loose_objs)

    objects = fit_objs + leaf_objs + loose_objs
    boxes = vf.state_collision(v, state)
    if scale < 1.0:
        squash = Matrix.Diagonal((scale, 1.0, scale, 1.0))
        for obj in objects:
            obj.data.transform(squash)
            obj.data.update()
        boxes = [((lo[0] * scale, lo[1], lo[2] * scale),
                  (hi[0] * scale, hi[1], hi[2] * scale)) for lo, hi in boxes]
    result = {
        "objects": objects,
        "collision_boxes": boxes,
        "attachments": {},
        "vault": {"state": state, "portal_radius": round(r * scale, 4),
                  "portal_radius_wanted": round(v["r_want"], 4),
                  "scaled_by": round(scale, 4),
                  "clear_width_at_sill": round(2.0 * v["half_clear"] * scale,
                                               4),
                  "required": v["required"]},
    }
    if not closed:
        result["fit_objects"] = fit_objs
    return result
