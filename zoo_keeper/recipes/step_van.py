"""step_van recipe: the crew's getaway van (Zoo 1.82.0 and 1.83.0, roadmap 206).

The walker, 2026-10-07: "a Box Truck. Like a Chevrolet P30. Matte
Black....faded, with patina, like a worn in truck...that's been on many
jobs.... Our very own 'millenial falcon'" -- parked at the mission's spawn:
"you spawn, do the job, then return to the car". The comps, read for format
only, are docs/reference/GETAWAY_VAN_COMPS.md at the factory root; every
number below is `core.van_forms.layout`, which is pure and tested.

Length runs along Y, the nose at -Y, the kerb (passenger) side at -X; built
base-up (z 0 .. H) and re-centred by `build.build_module`, like `simple_car`.

WHAT A STEP VAN IS HERE, in the order the parts are built:

  * THE BOX: one loft of round-edged roof sections from the bulkhead behind
    the cab to the rear doors. Its bottom line rises over the rear axle, so
    the arch is in the silhouette and the tyres sit in it.
  * THE CAB'S LOWER BODY: one loft from the grille face to just inside the
    box -- the hood climbing to the windshield's base, then the doors' lower
    half at the belt line. It stands `CAB_INSET` inside the box's sides and
    above its bottom: the seam a P30's cab makes against its body, and the
    gap that keeps two solids off one plane. Its bottom rises over the front
    axle.
  * THE CAB'S UPPER is open, because a solid behind glass is a painted wall
    behind glass (simple_car 0.79.0): a header `van_forms.HEADER` deep
    riding over the box roof and running into it (1.83.0: the walker found
    1.82.0's glass ran too near the roof), a windshield frame on a raked
    plane (two A-pillars and a centre pillar), B-pillars, and glass in
    every opening.
    Behind the glass: a dash, an engine cover, two seats, a steering wheel,
    and the bulkhead with its door into the box.
  * THE DETAILS a street reads a step van by: round headlamps in square
    bezels, amber lamps over them, a plain grille (no maker's mark), heavy
    black bumpers, amber clearance lamps along the cab roof's edge, tall
    mirrors on tube arms, two ribs down the box, door seams, a louvred vent,
    rear doors, tail lamps and a Pennsylvania plate on the tail.
  * THE WHEELS: steel discs in tyres lathed like simple_car's, dual rears
    (`dual_rear`), the axle at `van_forms.axle_height` so the tread meets
    the ground at any segment count.
  * UNDER THE BODY (1.83.0): the chassis `van_forms.chassis` plans as
    prims -- frame rails, crossmembers, leaf springs, a front beam axle,
    the rear axle with its differential, the engine's sump, the
    transmission, the driveshaft, the exhaust and its muffler, the fuel
    tank -- drawn here face for face and painted on the body's material
    (`van_forms.chassis_rgb`: grime, and rust on the exhaust).

THE FINISH IS THE TRUCK'S HISTORY. The body is one material of the plan's
kind (`paint_matte`), white, with the colour carried per corner in `Wear` by
`geometry.tint_wear_by` and `van_forms.finish_rgb` over the plan's colour:
near-black low down, chalked toward charcoal on the roof and upper panels,
rust at the arches and the rocker, road dust on the lower third, one grey
primer patch on the kerb side. Deterministic from position alone: the same
van in every level.

THE GHOST (1.83.0, variant 1, the walker's to judge): the van's old life as
SKEEVY'S WOODER ICE, its vinyl peeled off and the letters left as unfaded
paint. One image (`van_forms.ghost_art`) under the same `Wear` colour on
the same material (`materials.make_wear_textured_material`), the box's
sides mapped into it by `van_forms.ghost_uv` and every other face sent to
its white margin: no submission more than the plain van.

NO TWO FACES SHARE A PLANE (tools/coplanar_probe.py, SAME and OPP): every
detail stands proud of its face by a named distance, and every part that
meets another runs into it.

THE SLOT IS EXACT: width is the mirror heads' outer faces, depth the
bumpers' outer faces, height the clearance lamps' tops. The collision is the
slot's box, the box the greybox site gives Laser Tag.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials
from ..core import van_forms
from .simple_car import _box, _hexa, _lathe_x, _loft, _torus

#: A flat detail (lamp, plate, seam) stands this far proud of its face;
#: tools/coplanar_probe.py reports coincidence within 2 mm.
PROUD = 0.004
#: A part that meets another runs this far into it.
INTO = 0.02
GLASS_INSET = 0.007
GLASS_T = 0.006
GLASS_OPACITY = 0.45
GLASS_TINT = (0.05, 0.07, 0.08)
#: The pillars' depth behind the windshield plane, and their faces' inset
#: inside the cab roof's side (so a pillar never shares the roof's plane).
PILLAR_D = 0.06
PILLAR_IN = 0.010
#: The shared painted material's per-part colours (simple_car 1.59.0's
#: pattern: one material, the colour in `Wear`). Brightwork is dulled: this
#: is a worn van, not a show truck.
TINTS = {"bright": (0.40, 0.40, 0.39), "lamp_head": (0.80, 0.80, 0.74),
         "lamp_amber": (0.72, 0.36, 0.05), "lamp_tail": (0.45, 0.04, 0.04),
         "plate": (0.82, 0.80, 0.66), "steel": (0.075, 0.075, 0.080)}


def _section(hw, zb, zt, rr, n_side, n_top, k_round):
    """A closed XZ outline at one station: flat bottom, straight sides, a
    round top edge. The point count depends only on the counts, so any two
    stations of one loft loft together."""
    rr = max(0.01, min(rr, (zt - zb) - 0.01))
    zs = zt - rr
    pts = [(-hw, zb), (hw, zb)]
    for i in range(1, n_side + 1):
        pts.append((hw, zb + (zs - zb) * i / n_side))
    for i in range(1, k_round + 1):
        a = 0.5 * math.pi * i / k_round
        pts.append((hw - rr + rr * math.cos(a), zs + rr * math.sin(a)))
    for i in range(1, n_top):
        pts.append(((hw - rr) - 2.0 * (hw - rr) * i / n_top, zt))
    for i in range(0, k_round):
        a = 0.5 * math.pi + 0.5 * math.pi * i / k_round
        pts.append((-hw + rr + rr * math.cos(a), zs + rr * math.sin(a)))
    for i in range(0, n_side):
        pts.append((-hw, zs - (zs - zb) * i / n_side))
    return pts


def _stations(y_a, y_b, step, extra):
    ys = sorted({round(y, 4) for y in [y_a, y_b] + list(extra) if y_a <= y <= y_b})
    out = []
    for a, b in zip(ys, ys[1:]):
        n = max(1, int(math.ceil((b - a) / step)))
        out.extend(a + (b - a) * i / n for i in range(n))
    out.append(ys[-1])
    return out


def _arch_bottom(y, ya, A, z_low, z_arch, ramp=0.03):
    d = abs(y - ya)
    if d <= A - ramp:
        return z_arch
    if d <= A:
        return z_low + (z_arch - z_low) * (A - d) / ramp
    return z_low


def build(plan, streams, collection):
    W = plan["dimensions"]["width"]
    L = plan["dimensions"]["depth"]
    H = plan["dimensions"]["height"]
    wear = plan["wear"]
    rng = streams.stream("wear")
    seg = int(plan["params"].get("wheel_segments", 14))
    dual = int(plan["params"].get("dual_rear", 1)) > 0
    ghost = int(plan["params"].get("variant", 0) or 0) == 1
    lay = van_forms.layout(W, L, H)
    hw, r, tw = lay["hw"], lay["r"], lay["tyre_w"]
    zr, zs, zb, zn = lay["z_roof"], lay["z_sill"], lay["z_belt"], lay["z_nose"]
    y0, yt, y_n, y_r = lay["y0"], lay["yt"], lay["y_n"], lay["y_r"]
    y_ws, y_wt, y_cab = lay["y_ws"], lay["y_wt"], lay["y_cab"]
    ya_f, ya_r, A, za = lay["ya_f"], lay["ya_r"], lay["arch"], lay["z_arch"]
    ci = van_forms.CAB_INSET
    z_head = lay["z_head"]                               # the glass's top, under the header

    groups = {k: geometry.new_bm() for k in (
        "paint", "trim", "tyres", "bright", "lamp_head", "lamp_amber",
        "lamp_tail", "plate", "steel", "interior", "chassis", "exhaust")}
    panes = []

    # --- the box: bulkhead to rear doors ------------------------------------
    # THE DENSITY IS FOR THE PAINT. The finish lives in per-corner colour, so a
    # panel can only change colour where it has vertices: 0.28 m stations and
    # seven side rows drew the primer patch as a blocky rectangle in the first
    # frames. 0.20 m and ten rows draw it, the sun's gradient and the rust's
    # edges, inside the genome's triangle budget.
    ys = _stations(y_cab, y_r, 0.20, (ya_r - A, ya_r - A + 0.03, ya_r + A - 0.03, ya_r + A))
    loops = []
    for y in ys:
        z_bot = _arch_bottom(y, ya_r, A, zs, za)
        loops.append([(x, y, z) for x, z in
                      _section(hw, z_bot, zr, van_forms.ROOF_ROUND, 10, 6, 3)])
    _loft(groups["paint"], loops)

    # --- the cab's lower body: grille face to just inside the box -----------
    def z_top_front(y):
        if y <= y_ws:
            return zn + (zb - zn) * (y - y_n) / (y_ws - y_n)
        return zb
    ys = _stations(y_n, y_cab + 0.06, 0.22,
                   (y_ws, ya_f - A, ya_f - A + 0.03, ya_f + A - 0.03, ya_f + A))
    loops = []
    for y in ys:
        z_bot = _arch_bottom(y, ya_f, A, zs + 0.006, za)
        loops.append([(x, y, z) for x, z in
                      _section(hw - ci, z_bot, z_top_front(y), 0.03, 6, 5, 2)])
    _loft(groups["paint"], loops)

    # --- the cab roof: windshield top to just inside the box ----------------
    ys = _stations(y_wt, y_cab + 0.05, 0.25, ())
    loops = [[(x, y, z) for x, z in
              _section(hw - van_forms.CAB_ROOF_INSET, z_head, zr + van_forms.CAB_ROOF_RISE,
                       van_forms.ROOF_ROUND, 1, 6, 3)]
             for y in ys]
    _loft(groups["paint"], loops)

    # --- the windshield: pillars and two panes on the raked plane -----------
    dy, dz = y_wt - y_ws, z_head - zb
    ln = math.hypot(dy, dz)
    uy, uz = dy / ln, dz / ln                         # up the windshield
    iy, iz = uz, -uy                                  # into the cab

    def raked(x, s, d):
        """A point on the windshield: `s` metres up its line from the base,
        `d` metres behind its plane."""
        return (x, y_ws + s * uy + d * iy, zb + s * uz + d * iz)

    def raked_block(bm, x0, x1, s0, s1, d0, d1):
        _hexa(bm, [raked(x, s, d) for s in (s0, s1)
                   for x, d in ((x0, d0), (x1, d0), (x1, d1), (x0, d1))])

    s_lo, s_hi = -0.03, ln + 0.03                     # run into the body and the roof
    xa = hw - PILLAR_IN                               # an A-pillar's outer face
    for sgn in (-1.0, 1.0):
        x_out, x_in = sgn * xa, sgn * (xa - 0.085)
        raked_block(groups["paint"], min(x_in, x_out), max(x_in, x_out),
                    s_lo, s_hi, 0.0, PILLAR_D)
    raked_block(groups["paint"], -0.035, 0.035, s_lo, s_hi, 0.0, PILLAR_D)
    for sgn in (-1.0, 1.0):
        bm = geometry.new_bm()
        xs = sorted((sgn * 0.025, sgn * (xa - 0.075)))
        raked_block(bm, xs[0], xs[1], -0.01, ln + 0.01, GLASS_INSET, GLASS_INSET + GLASS_T)
        panes.append(("StepVan_Windshield_" + ("R" if sgn < 0 else "L"), bm))

    # --- the cab's sides: B-pillars and glass --------------------------------
    for sgn in (-1.0, 1.0):
        # the B-pillar's face 14 mm in: at 10 mm it stood 2 mm off the rear door
        # seam where it runs down into the lower body
        xo = sgn * (hw - 0.014)
        xi = sgn * (hw - 0.07)
        _box(groups["paint"], (min(xo, xi), y_cab - 0.10, zb - 0.03),
             (max(xo, xi), y_cab + 0.03, z_head + INTO))
        bm = geometry.new_bm()
        g_out, g_in = sgn * (hw - 0.020), sgn * (hw - 0.026)
        z_lo, z_hi = zb - 0.02, z_head + 0.012

        def y_front(z):
            return y_ws + (z - zb) * dy / dz + 0.03
        pts = []
        for z in (z_lo, z_hi):
            for x, y in ((g_out, y_front(z)), (g_out, y_cab - 0.06),
                         (g_in, y_cab - 0.06), (g_in, y_front(z))):
                pts.append((x, y, z))
        _hexa(bm, pts)
        panes.append(("StepVan_SideGlass_" + ("R" if sgn < 0 else "L"), bm))

    # --- inside the cab --------------------------------------------------------
    # Every piece that meets another runs into it, and none shares a plane
    # with what it meets: the first probe read five pairs in here (a seat's
    # back flush with its base, the engine cover's face on the dash's).
    gi = groups["interior"]
    _box(gi, (-(hw - 0.12), y_ws + 0.06, zb - INTO), (hw - 0.12, y_ws + 0.40, zb + 0.20))
    _box(gi, (-0.24, y_ws + 0.38, zb - 0.012), (0.24, y_ws + 0.95, zb + 0.28))
    for sgn in (-1.0, 1.0):
        x0, x1 = sorted((sgn * 0.30, sgn * 0.82))
        _box(gi, (x0, y_cab - 0.75, zb - INTO), (x1, y_cab - 0.30, zb + 0.10))
        _box(gi, (x0 + 0.01, y_cab - 0.36, zb - 0.012), (x1 - 0.01, y_cab - 0.26, zb + 0.72))
    c = (0.56, y_ws + 0.50, zb + 0.42)                # the driver's wheel, +X
    a = math.radians(30.0)
    _torus(gi, c, (1.0, 0.0, 0.0), (0.0, math.cos(a), math.sin(a)),
           (0.0, -math.sin(a), math.cos(a)), 0.21, 0.02, seg=12, tube=4)
    _box(gi, (0.54, y_ws + 0.30, zb + 0.18), (0.58, y_ws + 0.52, zb + 0.44))
    _box(gi, (-0.32, y_cab - PROUD, zb + 0.05), (0.32, y_cab + INTO, z_head - 0.06))

    # --- the nose: grille, bezels, lamps, bumper -----------------------------
    _box(groups["trim"], (-0.40, y_n - 0.006, zs + 0.11), (0.40, y_n + INTO, zn - 0.10))
    for zc in (0.80, 0.895):
        # backs 3 mm from both the grille's face and the nose's: at 2 mm off the
        # nose the probe read them back to back, and its window is <= 2.0 mm
        _box(groups["bright"], (-0.38, y_n - 0.012, zc), (0.38, y_n - 0.003, zc + 0.025))
    zl = 0.5 * (zs + 0.11 + zn - 0.10)                # lamp centre height
    for sgn in (-1.0, 1.0):
        xc = sgn * 0.66
        _box(groups["bright"], (xc - 0.125, y_n - 0.005, zl - 0.125), (xc + 0.125, y_n + INTO, zl + 0.125))
        geometry.add_cylinder(groups["lamp_head"], (xc, y_n - 0.0085, zl), 0.088, 0.011,
                              segments=seg, axis="Y")
        _box(groups["lamp_amber"], (xc - 0.075, y_n - 0.006, zl + 0.145), (xc + 0.075, y_n + INTO, zl + 0.20))
    _box(groups["trim"], (-(hw - 0.05), y0, 0.38), (hw - 0.05, y_n + 0.05, zs + 0.04))

    # --- mirrors on tube arms ----------------------------------------------------
    for sgn in (-1.0, 1.0):
        for z_arm in (1.62, 2.08):
            xs = sorted((sgn * (hw - 0.05), sgn * (W / 2.0 - 0.04)))
            _box(groups["trim"], (xs[0], y_ws + 0.040, z_arm), (xs[1], y_ws + 0.064, z_arm + 0.025))
        xs = sorted((sgn * (W / 2.0 - 0.07), sgn * W / 2.0))
        _box(groups["trim"], (xs[0], y_ws - 0.01, 1.52), (xs[1], y_ws + 0.11, 2.16))

    # --- the clearance lamps: the slot's height is their tops -------------------
    for xc in (-(hw - 0.12), -0.18, 0.0, 0.18, hw - 0.12):
        _box(groups["lamp_amber"], (xc - 0.035, y_wt + 0.012, zr + ci - 0.01), (xc + 0.035, y_wt + 0.07, H))

    # --- down the sides: ribs, door seams, the vent ----------------------------
    for sgn in (-1.0, 1.0):
        for z0 in (zb + 0.14, za + 0.10):
            xs = sorted((sgn * (hw - 0.01), sgn * (hw + 0.006)))
            _box(groups["paint"], (xs[0], y_cab + 0.12, z0), (xs[1], y_r - 0.06, z0 + 0.035))
        xs = sorted((sgn * (hw - ci - 0.004), sgn * (hw - ci + 0.003)))
        for yd in (lay["y_door0"], lay["y_door1"]):
            _box(groups["trim"], (xs[0], yd - 0.005, zs + 0.06), (xs[1], yd + 0.005, zb - 0.004))
    xs = (hw - ci - 0.004, hw - ci + PROUD)
    for k in range(5):
        z0 = 1.05 + k * 0.045
        _box(groups["trim"], (xs[0], lay["y_door0"] + 0.08, z0), (xs[1], lay["y_door0"] + 0.30, z0 + 0.014))

    # --- the tail: door seams, handle, lamps, plate, bumper ---------------------
    # The seams' backs stand 4 mm off the lamps' and the plate's and 3 mm off
    # the top seam's (all run into the doors; the probe's window is <= 2.0 mm,
    # so the first fix, at exactly 2, still read), and the verticals run INTO
    # the top seam, which stands 3 mm prouder than they do: ending them on its
    # face was a back-to-back pair, and flush fronts would be a same-facing one.
    yf = y_r + 0.003                                   # a seam's face
    z_top_seam = zr - 0.126
    _box(groups["trim"], (-0.006, y_r - 0.006, zs + 0.06), (0.006, yf, z_top_seam + 0.006))
    for sgn in (-1.0, 1.0):
        xc = sgn * (hw - 0.09)
        _box(groups["trim"], (xc - 0.006, y_r - 0.006, zs + 0.06), (xc + 0.006, yf, z_top_seam + 0.006))
        xt = sgn * (hw - 0.12)
        _box(groups["lamp_tail"], (xt - 0.07, y_r - 0.01, 0.78), (xt + 0.07, y_r + 0.008, 0.98))
    _box(groups["trim"], (-(hw - 0.09), y_r - 0.009, z_top_seam), (hw - 0.09, yf + 0.003, zr - 0.114))
    _box(groups["bright"], (0.06, y_r - 0.01, 1.20), (0.18, y_r + 0.012, 1.235))
    _box(groups["plate"], (-0.152, y_r - 0.01, 0.69), (0.152, y_r + 0.006, 0.84))
    _box(groups["trim"], (-(hw - 0.05), y_r - 0.05, 0.40), (hw - 0.05, yt, zs + 0.04))

    # --- wheels: steel discs, dual rears ------------------------------------------
    # THE AXLE HEIGHT IS DERIVED (`van_forms.axle_height`), so the tread
    # touches the ground at any `wheel_segments`: at the default 14 an axle at
    # r left the van 10.3 mm off the ground, floating 5 mm once centred in
    # its slot. simple_car's default 12 hides the same arithmetic.
    za_x = van_forms.axle_height(r, seg)
    xo = hw - 0.03                                     # an outer tyre's outer face
    profile = [(0.62 * r, tw / 2.0), (0.86 * r, tw / 2.0), (r, tw / 2.0 - 0.03),
               (r, -tw / 2.0 + 0.03), (0.86 * r, -tw / 2.0), (0.62 * r, -tw / 2.0)]
    for ya, inner in ((ya_f, False), (ya_r, dual)):
        for sgn in (-1.0, 1.0):
            cx = sgn * (xo - tw / 2.0)
            _lathe_x(groups["tyres"], cx, ya, za_x, profile, seg, sgn)
            if inner:
                _lathe_x(groups["tyres"], cx - sgn * (tw + 0.02), ya, za_x, profile, seg, sgn)
            x_face, x_back = sgn * (xo - 0.022), sgn * (xo - tw + 0.03)
            geometry.add_cylinder(groups["steel"], ((x_face + x_back) / 2.0, ya, za_x), 0.645 * r,
                                  abs(x_face - x_back), segments=seg, axis="X")
            c_face, c_back = sgn * (xo - 0.005), sgn * (xo - 0.032)
            geometry.add_cylinder(groups["bright"], ((c_face + c_back) / 2.0, ya, za_x), 0.17 * r,
                                  abs(c_face - c_back), segments=8, axis="X")

    # --- under the body: the chassis (`van_forms.chassis`) ---------------------
    under = van_forms.chassis(lay, za_x)
    for p in under:
        bm = groups["chassis" if p["mat"] == "frame" else "exhaust"]
        vs = [bm.verts.new(v) for v in p["verts"]]
        for f in p["faces"]:
            bm.faces.new([vs[i] for i in f])

    # --- objects, materials, the finish ----------------------------------------
    objs, by_group = [], {}
    names = {"paint": "StepVan_Body", "trim": "StepVan_Trim", "tyres": "StepVan_Tyres",
             "bright": "StepVan_Bright", "lamp_head": "StepVan_Headlamps",
             "lamp_amber": "StepVan_AmberLamps", "lamp_tail": "StepVan_TailLamps",
             "plate": "StepVan_Plate", "steel": "StepVan_Wheels", "interior": "StepVan_Interior",
             "chassis": "StepVan_Chassis", "exhaust": "StepVan_Exhaust"}
    for key, bm in groups.items():
        if not bm.faces:
            bm.free()
            continue
        obj = geometry.bm_to_object(bm, names[key], collection, bevel=0.0, texel=1.0,
                                    rng=rng, wear=wear if key == "paint" else wear * 0.5)
        objs.append(obj)
        by_group[key] = obj
    glass_objs = []
    for name, bm in panes:
        obj = geometry.bm_to_object(bm, name, collection, bevel=0.0, texel=0.5,
                                    rng=rng, wear=0.0)
        objs.append(obj)
        glass_objs.append(obj)

    # The body's kind and base colour are the PLAN's (the genome's style),
    # so editing the genome repaints the van; the trim's kinds are constants,
    # the way the display case's aluminium frame is.
    base = tuple(float(c) for c in plan["color"][:3])
    art = None
    if ghost:
        art = van_forms.ghost_art()
        paint = materials.make_wear_textured_material(
            "M_Van_paint_ghost", materials.image_from_png(art["name"], art["png"]), plan["material"])
    else:
        paint = materials.make_material("M_Van_paint", [1.0, 1.0, 1.0], plan["material"])
    painted = materials.make_material("M_Van_painted", [1.0, 1.0, 1.0], "metal_painted")
    rubber = materials.make_material("M_Van_rubber", [0.030, 0.030, 0.032], "rubber")
    cloth = materials.make_material("M_Van_interior", [0.085, 0.080, 0.075], "canvas")
    for key, obj in by_group.items():
        if key in ("paint", "chassis", "exhaust"):
            materials.assign([obj], paint)
            if key == "paint":
                fn = (lambda co, n: van_forms.finish_rgb(co, n, lay, base))
            else:
                fn = (lambda co, n, part=("exhaust" if key == "exhaust" else "frame"):
                      van_forms.chassis_rgb(co, n, part))
            if not geometry.tint_wear_by(obj, fn):
                raise RuntimeError(f"step_van: {obj.name} has no Wear layer, so its paint would not land")
            if art is not None:
                uv = ((lambda co, n: van_forms.ghost_uv(co, n, lay)) if key == "paint"
                      else (lambda co, n: van_forms.GHOST_OUTSIDE))
                if not geometry.set_uv_by(obj, uv):
                    raise RuntimeError(f"step_van: {obj.name} has no UV layer, so the ghost would not land")
        elif key in TINTS:
            materials.assign([obj], painted)
            if not geometry.tint_wear(obj, TINTS[key]):
                raise RuntimeError(f"step_van: {obj.name} has no Wear layer, so its colour would not land")
        elif key == "interior":
            materials.assign([obj], cloth)
        else:
            materials.assign([obj], rubber)
    materials.assign(glass_objs, materials.make_see_through_material(
        "M_Van_glass", list(GLASS_TINT), GLASS_OPACITY))

    print(f"[van] dual_rear={dual} wheel_segments={seg} panes={len(glass_objs)} "
          f"chassis={len(under)} "
          f"ghost={art['name'] if art else 'none'} "
          f"cab={van_forms.CAB_LEN:.2f} box={y_r - y_cab:.2f} axles=({ya_f:.2f}, {ya_r:.2f})")
    return {"objects": objs,
            "collision_boxes": [((-W / 2.0, y0, 0.0), (W / 2.0, yt, H))],
            "attachments": {"ATT_roof": (0.0, (y_cab + y_r) / 2.0, zr),
                            "ATT_driver_seat": (0.56, y_cab - 0.5, zb + 0.10),
                            "ATT_side_door": (-hw, (lay["y_door0"] + lay["y_door1"]) / 2.0, zs)}}
