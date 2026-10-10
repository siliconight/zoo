"""box_truck recipe: a 1990s cab-over delivery truck in an invented Delco fleet (Zoo 1.92.0).

Roadmap 219 note 5. The walker, walking club_block_014 on 2026-10-09: "i dont know what this giant
grey box is". It was this species' PLACEHOLDER SILHOUETTE, minted 2026-09-12: one solid box, parked
by Lot as cover between buildings (roadmap 22). Every number below is `core.box_truck_forms`, which
is pure and tested.

Length runs along Y, the nose at -Y, the kerb side at -X (the driver sits at +X); built base-up
(z 0 .. H) and re-centred by `build.build_module`, like `step_van` and `simple_car`.

WHAT A BOX TRUCK IS HERE, in the order the parts are built:

  * THE BOX: one loft from its front to its rear frame, the roof's edges rounded a little, on the
    frame. Aluminium corner caps on its four vertical edges, a rail along the top and the foot of
    each side, clearance lamps on the roof's front edge and identification lamps over the door.
  * THE ROLL-UP DOOR: the box's rear face, its slat seams standing proud across it, a handle at
    its foot, a header and a sill; the step bumper under it with the tail lamps and the plate.
  * THE CAB-OVER: the lower body one loft from the face to the back wall, its plan corners round
    and its bottom rising over the front axle, so the arch is in the silhouette. Above the belt
    line it is open, because a solid behind glass is a painted wall behind glass (simple_car
    0.79.0): a roof, raked A-pillars and B-pillars, a back wall to the box, and glass in the
    windshield and both doors. Behind the glass: a dash, two seats and the wheel.
  * THE FACE: a slatted grille with no maker's mark, rectangular headlamps and amber turn lamps
    wrapping the corners, a black bumper, tall mirrors on arms, door seams and handles, and the
    entry steps behind the front wheels, where a cab-over's are.
  * THE WHEELS: `step_van`'s -- lathed tyres on `van_forms.tyre_profile`, steel discs, hubs, lug
    nuts and caps -- single at the front and dual at the rear, the axle at
    `van_forms.axle_height` so the tread meets the ground.
  * UNDER IT: two frame rails, the box's crossmembers on them, the axles, an aluminium fuel tank on
    the kerb side and mud flaps behind the rear pair.

THE FLEET IS THE PAINT. The body is one material of the plan's kind, carrying the fleet's livery
(`box_truck_forms.livery_art`) mapped onto the box's sides, and the colour in `Wear` per corner
(`finish_rgb`): the box white, the cab the fleet's colour, road grime low down and streaks under
the roof. `variant` picks one of four fleets (`FLEETS`); the genome's `module_variants` says four.

FIVE MATERIALS, five draws a truck: the paint, one painted material for every tinted part, rubber,
the cab's cloth and its glass -- `step_van`'s set.

NO TWO FACES SHARE A PLANE (tools/coplanar_probe.py): every detail stands proud of its face by a
named distance, and every part that meets another runs into it.

THE SLOT IS EXACT: width is the mirror heads' outer faces, depth the front bumper's face and the
tail lamps', height the clearance lamps' tops. The collision is the slot's box: six metres of solid
across a lane, as roadmap 22 wants, taller than 1.3 m all along.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials
from ..core import box_truck_forms as BT
from ..core import van_forms
from .simple_car import _box, _hexa, _lathe_x, _loft, _torus
from .step_van import _arch_bottom, _section, _stations

#: A flat detail (lamp, plate, seam) stands this far proud of its face; tools/coplanar_probe.py
#: reports coincidence within 2 mm.
PROUD = 0.004
#: A part that meets another runs this far into it.
INTO = 0.02
#: Trim that should read as metal and not a sticker: the box's caps; its rails stand half as far.
TRIM_PROUD = 0.010
RAIL_PROUD = 0.005
#: The roof's sides stand this far inside the cab's lower body; the glass and the pillars stand
#: further in, each a named distance from the next, so no two of them are within the probe's
#: window: the A-pillar 4 mm inside the roof, the door glass 12 mm, the B-pillar 24 mm.
ROOF_IN = 0.006
A_PILLAR_IN = 0.010
GLASS_IN = 0.018
B_PILLAR_IN = 0.030
GLASS_INSET = 0.007
GLASS_T = 0.006
GLASS_OPACITY = 0.45
GLASS_TINT = (0.05, 0.07, 0.08)
PILLAR_D = 0.06
#: The shared painted material's per-part colours (simple_car 1.59.0's pattern: one material, the
#: colour in `Wear`). A working truck's brightwork is dulled; its steel wheels are white.
TINTS = {"bright": (0.52, 0.52, 0.50), "lamp_head": (0.80, 0.80, 0.74),
         "lamp_amber": (0.72, 0.36, 0.05), "lamp_tail": (0.45, 0.04, 0.04),
         "plate": (0.82, 0.80, 0.66), "steel": (0.62, 0.62, 0.60)}


def build(plan, streams, collection):
    W = plan["dimensions"]["width"]
    L = plan["dimensions"]["depth"]
    H = plan["dimensions"]["height"]
    wear = plan["wear"]
    rng = streams.stream("wear")
    params = plan.get("params") or {}
    seg = int(params.get("wheel_segments", 14))
    variant = int(params.get("variant", 0) or 0)
    lay = BT.layout(W, L, H)
    hb, hc, r, tw = lay["hb"], lay["hc"], lay["r"], lay["tyre_w"]
    zf, zb0, zb1 = lay["z_frame"], lay["z_box0"], lay["z_box1"]
    zc0, zc1, zbl, zh = lay["z_cab0"], lay["z_cab1"], lay["z_belt"], lay["z_head"]
    y0, yt, yn, yc, yb, yr = lay["y0"], lay["yt"], lay["y_n"], lay["y_c"], lay["y_b"], lay["y_r"]
    yws, ywt = lay["y_ws"], lay["y_wt"]
    yd0, yd1 = lay["y_door0"], lay["y_door1"]
    yaf, yar, A, za = lay["ya_f"], lay["ya_r"], lay["arch"], lay["z_arch"]

    groups = {k: geometry.new_bm() for k in (
        "paint", "trim", "tyres", "bright", "lamp_head", "lamp_amber", "lamp_tail", "plate",
        "steel", "interior", "chassis")}
    panes = []

    def z_bottom(y):
        """The cab's underside at ``y``: its skirt, rising over the front axle."""
        return _arch_bottom(y, yaf, A, zc0, za)

    # --- the box: its front to its rear frame, on the frame ----------------------------------
    # THE DENSITY IS FOR THE PAINT: the grime and the streaks are per-corner colour, so the side
    # has rows enough for a gradient and stations every 0.25 m.
    ys = _stations(yb, yr, 0.25, ())
    _loft(groups["paint"], [[(x, y, z) for x, z in _section(hb, zb0, zb1, BT.BOX_ROUND, 8, 6, 2)]
                            for y in ys])
    for sgn in (-1.0, 1.0):
        # the corner caps, wrapping side and end by TRIM_PROUD, front and rear
        xc = sorted((sgn * (hb - 0.07), sgn * (hb + TRIM_PROUD)))
        _box(groups["bright"], (xc[0], yb - TRIM_PROUD, zb0 - 0.03), (xc[1], yb + 0.07, zb1 + 0.006))
        _box(groups["bright"], (xc[0], yr - 0.07, zb0 - 0.03), (xc[1], yr + TRIM_PROUD, zb1 + 0.006))
        # the rails along the top and the foot of the side, their ends inside the caps
        xr = sorted((sgn * (hb - 0.02), sgn * (hb + RAIL_PROUD)))
        _box(groups["bright"], (xr[0], yb + 0.04, zb1 - 0.10), (xr[1], yr - 0.04, zb1 - 0.035))
        _box(groups["bright"], (xr[0], yb + 0.04, zb0 - 0.02), (xr[1], yr - 0.04, zb0 + 0.09))
    # the clearance lamps on the roof's front edge: their tops are the slot's height
    for xl in (-(hb - 0.14), -0.28, 0.0, 0.28, hb - 0.14):
        _box(groups["lamp_amber"], (xl - 0.045, yb + 0.03, zb1 - 0.012), (xl + 0.045, yb + 0.09, H))

    # --- the roll-up door, its frame, the step bumper ----------------------------------------
    for i in range(1, 11):
        zs = zb0 + 0.10 + (zb1 - 0.32 - zb0) * i / 11.0
        _box(groups["trim"], (-(hb - 0.10), yr - INTO, zs - 0.006), (hb - 0.10, yr + PROUD, zs + 0.006))
    # the header and the sill run into the corner caps and stand 6 mm proud of them
    y_frame = yr + TRIM_PROUD + 0.006
    _box(groups["bright"], (-(hb - 0.05), yr - INTO, zb1 - 0.20), (hb - 0.05, y_frame, zb1 - 0.10))
    _box(groups["bright"], (-(hb - 0.05), yr - INTO, zb0 - 0.02), (hb - 0.05, y_frame, zb0 + 0.07))
    _box(groups["bright"], (-0.16, yr - INTO, zb0 + 0.12), (0.16, yr + 0.012, zb0 + 0.16))
    for xl in (-0.15, 0.0, 0.15):
        _box(groups["lamp_tail"], (xl - 0.03, y_frame - 0.012, zb1 - 0.17), (xl + 0.03, y_frame + 0.012, zb1 - 0.13))
    z_bump0, z_bump1 = max(0.30, zf - 0.30), max(0.45, zf - 0.12)
    # THE TAIL LAMPS ARE THE SLOT'S REAR: the bumper stands PROUD short of it, so nothing passes
    # the slot's depth and the lamps' faces are not the bumper's plane
    _box(groups["trim"], (-(hb - 0.04), yr - 0.30, z_bump0), (hb - 0.04, yt - PROUD, z_bump1))
    for sgn in (-1.0, 1.0):
        # the bumper's brackets run up into the frame rails
        xs = sorted((sgn * 0.42, sgn * 0.52))
        # never shorter than 5 cm: on the smallest slot the frame sits so low that the bracket's
        # top fell under its bottom and it inverted to a 0.1 mm sliver
        _box(groups["trim"], (xs[0], yr - 0.28, z_bump1 - INTO),
             (xs[1], yr - 0.18, max(zf - 0.10, z_bump1 + 0.05)))
        xt = sorted((sgn * (hb - 0.10), sgn * (hb - 0.32)))
        _box(groups["lamp_tail"], (xt[0], yt - INTO, z_bump0 + 0.03), (xt[1], yt, z_bump1 - 0.03))
    # the plate, on a backer standing on the bumper
    _box(groups["trim"], (-0.17, yt - 0.10, z_bump1 - INTO), (0.17, yt - 0.03, z_bump1 + 0.19))
    _box(groups["plate"], (-0.152, yt - 0.05, z_bump1 + 0.02), (0.152, yt - 0.012, z_bump1 + 0.17))

    # --- the cab-over's lower body: face to back wall, round in plan, the front arch cut ---
    ys = _stations(yn, yc, 0.20, (yn + 0.03, yn + 0.06, yn + 0.09, yn + BT.CAB_ROUND,
                                  yaf - A, yaf - A + 0.03, yaf + A - 0.03, yaf + A))
    _loft(groups["paint"], [[(x, y, z) for x, z in
                             _section(BT.cab_half_width(lay, y), z_bottom(y), zbl, 0.03, 5, 5, 2)]
                            for y in ys])

    # --- the cab roof: the windshield's top to the back wall ---------------------------------
    ys = _stations(ywt, yc, 0.25, ())
    _loft(groups["paint"], [[(x, y, z) for x, z in
                             _section(BT.cab_half_width(lay, y) - ROOF_IN, zh, zc1, 0.08, 1, 6, 3)]
                            for y in ys])
    # the back wall, above the belt, its back 4 mm inside the roof's end and the body's
    _box(groups["paint"], (-(hc - 0.012), yc - 0.06, zbl - INTO), (hc - 0.012, yc - PROUD, zh + INTO))

    # --- the windshield: raked A-pillars, the pane, the wipers -------------------------------
    dy, dz = ywt - yws, zh - zbl
    ln = math.hypot(dy, dz)
    uy, uz = dy / ln, dz / ln                         # up the windshield
    iy, iz = uz, -uy                                  # into the cab

    def raked(x, s, d):
        return (x, yws + s * uy + d * iy, zbl + s * uz + d * iz)

    def raked_block(bm, x0, x1, s0, s1, d0, d1):
        _hexa(bm, [raked(x, s, d) for s in (s0, s1)
                   for x, d in ((x0, d0), (x1, d0), (x1, d1), (x0, d1))])

    xa = hc - A_PILLAR_IN                             # an A-pillar's outer face
    for sgn in (-1.0, 1.0):
        x0_, x1_ = sorted((sgn * xa, sgn * (xa - 0.09)))
        raked_block(groups["paint"], x0_, x1_, -0.03, ln + 0.03, 0.0, PILLAR_D)
    bm = geometry.new_bm()
    raked_block(bm, -(xa - 0.08), xa - 0.08, -0.01, ln + 0.01, GLASS_INSET, GLASS_INSET + GLASS_T)
    panes.append(("BoxTruck_Windshield", bm))
    for xp in (-0.36, 0.30):
        raked_block(groups["trim"], xp - 0.012, xp + 0.012, 0.02, 0.60, -0.012, -0.004)

    # --- the doors' glass and the B-pillars --------------------------------------------------
    yg0, yg1 = yws + 0.03, yd1 - 0.06                 # the glass runs into both pillars
    for sgn in (-1.0, 1.0):
        xb_ = sorted((sgn * (hc - B_PILLAR_IN), sgn * (hc - B_PILLAR_IN - 0.06)))
        _box(groups["paint"], (xb_[0], yg1, zbl - INTO - 0.01), (xb_[1], yc - 0.04, zh + INTO + 0.01))
        bm = geometry.new_bm()
        xg = sorted((sgn * (hc - GLASS_IN), sgn * (hc - GLASS_IN - GLASS_T)))
        _box(bm, (xg[0], yg0, zbl - 0.01), (xg[1], yg1 + 0.01, zh + 0.01))
        panes.append(("BoxTruck_DoorGlass_" + ("L" if sgn > 0 else "R"), bm))

    # --- what the glass shows: the dash, the seats (the driver's at +X) and the wheel ---------
    _box(groups["interior"], (-(hc - 0.10), yws + 0.20, zbl - INTO), (hc - 0.10, yws + 0.48, zbl + 0.16))
    # the seats stand clear of the B-pillars' inner faces however narrow the cab: on the genome's
    # smallest slot a seat at 0.52 m shared a pillar's plane
    x_seat = min(0.52, hc - 0.36)
    for xs_c in (-x_seat, x_seat):
        _box(groups["interior"], (xs_c - 0.24, yc - 0.62, zbl - INTO), (xs_c + 0.24, yc - 0.18, zbl + 0.08))
        _box(groups["interior"], (xs_c - 0.23, yc - 0.20, zbl - INTO - 0.01), (xs_c + 0.23, yc - 0.10, zbl + 0.66))
    _torus(groups["interior"], (x_seat, yws + 0.62, zbl + 0.30), (1.0, 0.0, 0.0), (0.0, 0.42, 0.91),
           (0.0, 0.91, -0.42), 0.19, 0.018, seg=12, tube=4)

    # --- the face: grille, lamps, bumper -----------------------------------------------------
    yface = yn - PROUD
    _box(groups["trim"], (-0.46, yface, zbl - 0.46), (0.46, yn + INTO, zbl - 0.10))
    for k in range(4):
        zz = zbl - 0.42 + k * 0.085
        _box(groups["bright"], (-0.43, yface - 0.004, zz), (0.43, yn + INTO - 0.01, zz + 0.022))
    for sgn in (-1.0, 1.0):
        xh = sorted((sgn * 0.52, sgn * (hc - 0.20)))
        _box(groups["lamp_head"], (xh[0], yface, zbl - 0.42), (xh[1], yn + INTO, zbl - 0.24))
        xt = sorted((sgn * (hc - 0.18), sgn * (hc - 0.08)))
        _box(groups["lamp_amber"], (xt[0], yface, zbl - 0.42), (xt[1], yn + INTO, zbl - 0.24))
    _box(groups["trim"], (-(hc - 0.02), y0, zc0 - 0.12), (hc - 0.02, yn + INTO, zc0 + 0.12))

    # --- the mirrors, the steps, the door seams and handles ----------------------------------
    for sgn in (-1.0, 1.0):
        # the head is the slot's width; its arm runs from the body's side, under the belt, up
        # into the head's foot
        xh = sorted((sgn * (W / 2.0 - 0.07), sgn * (W / 2.0)))
        _box(groups["trim"], (xh[0], yn + 0.14, zbl - 0.05), (xh[1], yn + 0.21, zbl + 0.48))
        xa_ = sorted((sgn * (hc - INTO), sgn * (W / 2.0 - 0.07 + INTO)))
        _box(groups["trim"], (xa_[0], yn + 0.16, zbl - 0.09), (xa_[1], yn + 0.19, zbl - 0.04))
        # the step behind the front wheel, and the bracket that hangs it from the skirt
        ys0, ys1 = yaf + A + 0.03, yd1 - 0.04
        xs = sorted((sgn * (hc - 0.22), sgn * (hc + 0.05)))
        _box(groups["trim"], (xs[0], ys0, zc0 - 0.22), (xs[1], ys1, zc0 - 0.18))
        xk = sorted((sgn * (hc - 0.20), sgn * (hc - 0.12)))
        _box(groups["trim"], (xk[0], ys0 + 0.03, zc0 - 0.20), (xk[1], ys1 - 0.03, zc0 + INTO))
        # the door's seams, from just over the body's underside there to the belt
        xo_ = sorted((sgn * (hc - INTO), sgn * (hc + PROUD)))
        for yy in (yd0, yd1):
            _box(groups["trim"], (xo_[0], yy - 0.004, z_bottom(yy) + 0.04), (xo_[1], yy + 0.004, zbl - 0.02))
        xh_ = sorted((sgn * (hc - INTO), sgn * (hc + 0.012)))
        _box(groups["bright"], (xh_[0], yd1 - 0.24, zbl - 0.16), (xh_[1], yd1 - 0.12, zbl - 0.12))

    # --- the wheels: steel discs, dual rears -------------------------------------------------
    za_x = van_forms.axle_height(r, seg)
    profile = van_forms.tyre_profile(r, tw)
    for ya, xo, dual in ((yaf, hc - 0.03, False), (yar, hb - 0.03, True)):
        for sgn in (-1.0, 1.0):
            cx = sgn * (xo - tw / 2.0)
            _lathe_x(groups["tyres"], cx, ya, za_x, profile, seg, sgn)
            if dual:
                _lathe_x(groups["tyres"], cx - sgn * (tw + 0.02), ya, za_x, profile, seg, sgn)
            x_face, x_back = sgn * (xo - 0.022), sgn * (xo - tw + 0.03)
            geometry.add_cylinder(groups["steel"], ((x_face + x_back) / 2.0, ya, za_x), van_forms.DISC_R * r,
                                  abs(x_face - x_back), segments=seg, axis="X")
            h_back, h_face = x_face - sgn * 0.01, x_face + sgn * 0.025
            geometry.add_cylinder(groups["steel"], ((h_back + h_face) / 2.0, ya, za_x), van_forms.HUB_R * r,
                                  abs(h_face - h_back), segments=seg, axis="X")
            n_back, n_face = h_face - sgn * 0.005, h_face + sgn * 0.015
            for k in range(6):
                a = 2.0 * math.pi * (k + 0.5) / 6.0
                geometry.add_cylinder(groups["bright"],
                                      ((n_back + n_face) / 2.0, ya + van_forms.LUG_CIRCLE * r * math.cos(a),
                                       za_x + van_forms.LUG_CIRCLE * r * math.sin(a)),
                                      van_forms.LUG_R, abs(n_face - n_back), segments=6, axis="X")
            c_face = h_face + sgn * 0.02
            geometry.add_cylinder(groups["bright"], ((n_back + c_face) / 2.0, ya, za_x), van_forms.CAP_R * r,
                                  abs(c_face - n_back), segments=12, axis="X")
        # the axle, between the innermost tyres and running into them
        x_inner = xo - (2.0 * tw + 0.02 if dual else tw)
        _box(groups["chassis"], (-(x_inner + 0.05), ya - 0.045, za_x - 0.045),
             (x_inner + 0.05, ya + 0.045, za_x + 0.045))
        if dual:
            for sgn in (-1.0, 1.0):
                xs = sorted((sgn * (x_inner - van_forms.TYRE_BULGE), sgn * xo))
                _box(groups["trim"], (xs[0], ya + A + 0.03, 0.14), (xs[1], ya + A + 0.042, zb0 + INTO))

    # --- under it: the rails, the box's crossmembers, the fuel tank --------------------------
    for sgn in (-1.0, 1.0):
        xs = sorted((sgn * 0.43, sgn * 0.51))
        _box(groups["chassis"], (xs[0], yn + 0.15, zf - 0.22), (xs[1], yr - 0.05, zf))
    n_x = max(2, int((yr - yb) / 0.55))
    for i in range(n_x + 1):
        yy = yb + 0.10 + (yr - yb - 0.20) * i / n_x
        _box(groups["chassis"], (-(hb - 0.06), yy - 0.035, zf - INTO), (hb - 0.06, yy + 0.035, zb0 + INTO))
    t_y0, t_y1 = yc + 0.25, min(yc + 1.05, yar - A - 0.10)
    # the tank hangs outside the kerb-side rail: on a narrow slot it would cut through it
    x_tank = max(0.51 + 0.02 + 0.20, hb - 0.30)
    geometry.add_cylinder(groups["bright"], (-x_tank, (t_y0 + t_y1) / 2.0, zf - 0.20), 0.20,
                          max(0.30, t_y1 - t_y0), segments=12, axis="Y")
    for yy in (t_y0 + 0.08, t_y1 - 0.08):
        _box(groups["chassis"], (-(hb - 0.08), yy - 0.02, zf - 0.42), (-0.43 + INTO, yy + 0.02, zf - 0.02))

    # --- objects, materials, the finish ------------------------------------------------------
    objs, by_group = [], {}
    names = {"paint": "BoxTruck_Body", "trim": "BoxTruck_Trim", "tyres": "BoxTruck_Tyres",
             "bright": "BoxTruck_Bright", "lamp_head": "BoxTruck_Headlamps",
             "lamp_amber": "BoxTruck_AmberLamps", "lamp_tail": "BoxTruck_TailLamps",
             "plate": "BoxTruck_Plate", "steel": "BoxTruck_Wheels", "interior": "BoxTruck_Interior",
             "chassis": "BoxTruck_Chassis"}
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
        obj = geometry.bm_to_object(bm, name, collection, bevel=0.0, texel=0.5, rng=rng, wear=0.0)
        objs.append(obj)
        glass_objs.append(obj)

    art = BT.livery_art(variant)
    paint = materials.make_wear_textured_material(
        "M_BoxTruck_paint_" + BT.fleet(variant)["id"],
        materials.image_from_png(art["name"], art["png"]), plan["material"])
    painted = materials.make_material("M_BoxTruck_painted", [1.0, 1.0, 1.0], "metal_painted")
    rubber = materials.make_material("M_BoxTruck_rubber", [0.030, 0.030, 0.032], "rubber")
    cloth = materials.make_material("M_BoxTruck_interior", [0.085, 0.080, 0.075], "canvas")
    for key, obj in by_group.items():
        if key in ("paint", "chassis"):
            materials.assign([obj], paint)
            if key == "paint":
                fn = (lambda co, n: BT.finish_rgb(co, n, lay, variant))
            else:
                fn = (lambda co, n: BT.CHASSIS_RGB)
            if not geometry.tint_wear_by(obj, fn):
                raise RuntimeError(f"box_truck: {obj.name} has no Wear layer, so its paint would not land")
            uv = ((lambda co, n: BT.livery_uv(co, n, lay)) if key == "paint"
                  else (lambda co, n: BT.LIVERY_OUTSIDE))
            if not geometry.set_uv_by(obj, uv):
                raise RuntimeError(f"box_truck: {obj.name} has no UV layer, so the livery would not land")
        elif key in TINTS:
            materials.assign([obj], painted)
            if not geometry.tint_wear(obj, TINTS[key]):
                raise RuntimeError(f"box_truck: {obj.name} has no Wear layer, so its colour would not land")
        elif key == "interior":
            materials.assign([obj], cloth)
        else:
            materials.assign([obj], rubber)
    materials.assign(glass_objs, materials.make_see_through_material(
        "M_BoxTruck_glass", list(GLASS_TINT), GLASS_OPACITY))

    print(f"[box_truck] fleet={BT.fleet(variant)['id']} wheel_segments={seg} panes={len(glass_objs)} "
          f"cab={BT.CAB_LEN:.2f} box={yr - yb:.2f} axles=({yaf:.2f}, {yar:.2f}) art={art['name']}")
    return {"objects": objs,
            "collision_boxes": [((-W / 2.0, y0, 0.0), (W / 2.0, yt, H))],
            "attachments": {"ATT_roof": (0.0, (yb + yr) / 2.0, zb1),
                            "ATT_rear_door": (0.0, yt, zb0)}}
