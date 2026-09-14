"""fire_hydrant recipe: an American dry-barrel fire hydrant.

REBUILT, 0.85.0. The walker, in the walk copies, asked about "white boxes at
the foot of the stop signs": slot `cover_81` in walk 9052_rain, the minting
placeholder -- one bevelled box, 44 tris, on a near-white tintable metal pack
tinted grey. `core/hydrant_forms.py` records that measurement and decides
every size and colour below; this file only executes it.

WHAT IS BUILT, in the module frame (Z up, metres, centre pivot, grade at
-h/2, the pumper outlet toward -Y):

  * `FireHydrant_Collar`: the ground collar, the body's paint gone to grime;
  * `FireHydrant_Barrel`: the traffic flange, the tapered lower barrel, the
    upper barrel flange, the nozzle section, and a chain eye under each
    outlet;
  * `FireHydrant_Nuts`: six hex nuts on each barrel flange;
  * `FireHydrant_HoseNozzles`, `FireHydrant_PumperNozzle`: the outlet stubs;
  * `FireHydrant_HoseCaps`, `FireHydrant_PumperCap`: caps with a chain lug
    under each and a pentagonal nut on each end;
  * `FireHydrant_Bonnet`: the bonnet flange with its five nuts, the faceted
    dome and the hold-down disc; `FireHydrant_OperatingNut`: the pentagon on
    top;
  * `FireHydrant_Chains`: galvanised links from each cap lug to its eye.

Body parts wear the scheme's body paint, the bonnet, caps and nuts its top
paint (`hydrant_forms.pick_scheme`), the chains `metal_bare`.

FACETED ON PURPOSE. Every edge is hard (`shade_by_angle(bm, 1.0)`), so a
12-sided barrel reads as twelve faces under a sun and not as a smoothed tube.

Collision is the slot's box, as it was: Lot's greybox and navmesh already
carve that box, and a body walks round a hydrant, not between its caps.
"""
from __future__ import annotations

import math

import bmesh
from mathutils import Vector

from ..bpylayer import geometry, materials
from ..core import hydrant_forms as hf

UP = Vector((0.0, 0.0, 1.0))
#: Grime rises this far off grade (metres), darkest at the ground.
GRIME_RISE = 0.25
GRIME = 0.55


def _lathe(bm, profile, n, xform, rot=None):
    """A closed n-gon solid through ``profile`` [(apothem, local z)], built in
    a local frame and placed by ``xform`` (local Vector -> world Vector)."""
    rings = []
    for a, zz in profile:
        rings.append([bm.verts.new(xform(Vector((x, y, zz))))
                      for x, y in hf.prism_ring(n, a, rot)])
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])


def _upright(cx, cy):
    return lambda v: Vector((cx + v.x, cy + v.y, v.z))


def _outlet_frame(origin, a):
    """Local z along the outlet direction ``a``, local y up, local x across."""
    a = Vector(a).normalized()
    b = a.cross(UP)
    o = Vector(origin)
    return lambda v: o + a * v.z + b * v.x + UP * v.y


def _oriented_box(bm, centre, axes, half):
    """A box with half-extents ``half`` along the three unit ``axes``."""
    c = Vector(centre)
    verts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                verts.append(bm.verts.new(c + axes[0] * (sx * half[0])
                                          + axes[1] * (sy * half[1])
                                          + axes[2] * (sz * half[2])))
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6),
              (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([verts[i] for i in f])


def _nut_ring(bm, L, key, z_seat, ya):
    ring = L[key]
    bury = L["bury"]
    for ang in ring["angles"]:
        cx, cy = ring["ring"] * math.cos(ang), ya + ring["ring"] * math.sin(ang)
        apothem = ring["r"] * math.cos(math.pi / hf.NUT_SIDES)
        _lathe(bm, [(apothem, z_seat - bury), (apothem, z_seat + ring["h"])],
               hf.NUT_SIDES, _upright(cx, cy), rot=ang + ring["twist"])


def _wear(bm, rng, wear, ambient, z0):
    """The existing wear pass (`geometry.wear_colors`: concavity and seeded
    grime, the style's ambient), then darker toward grade."""
    geometry.wear_colors(bm, rng, wear, ambient=ambient)
    layer = bm.loops.layers.color.get(geometry.WEAR_LAYER)
    w = max(0.0, min(1.0, float(wear)))
    for f in bm.faces:
        for loop in f.loops:
            up = max(0.0, 1.0 - (loop.vert.co.z - z0) / GRIME_RISE)
            g = 1.0 - w * GRIME * up
            c = loop[layer]
            loop[layer][:] = (c[0] * g, c[1] * g, c[2] * g, 1.0)


def build(plan, streams, collection):
    L = hf.resolve(plan, streams)
    paint = L["paint"]
    w, d, h = L["w"], L["d"], L["h"]
    z0, ya, bury, n = L["z0"], L["y_axis"], L["bury"], L["segments"]
    wear = plan["wear"]
    ambient = plan.get("ambient", 0.0)
    rng = streams.stream("hydrant_wear")
    axis = _upright(0.0, ya)

    B = {k: geometry.new_bm() for k in (
        "collar", "barrel", "nuts", "hose_nozzles", "pumper_nozzle", "hose_caps",
        "pumper_cap", "bonnet", "op_nut", "chains")}

    # --- the column, bottom to top --------------------------------------------
    c0, c1 = L["collar"]
    _lathe(B["collar"], [(L["collar_a"], c0), (L["collar_a"], c1)], n, axis)
    f0, f1 = L["flange"]
    _lathe(B["barrel"], [(L["flange_a"], c1 - bury), (L["flange_a"], f1)], n, axis)
    l0, l1 = L["lower"]
    a_bot, a_top = L["lower_a"]
    lz0, lz1 = f1 - bury, l1 + bury
    bands = [lz0 + (lz1 - lz0) * t for t in (0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0)]
    _lathe(B["barrel"], [(a_bot + (a_top - a_bot) * (zz - lz0) / (lz1 - lz0), zz)
                         for zz in bands], n, axis)
    u0, u1 = L["upper_flange"]
    _lathe(B["barrel"], [(L["upper_flange_a"], u0), (L["upper_flange_a"], u1)], n, axis)
    s0, s1 = L["section"]
    zo = L["outlet_z"]
    _lathe(B["barrel"], [(L["section_a"], u1 - bury), (L["section_a"], zo),
                         (L["section_a"], s1 + bury)], n, axis)
    b0, b1 = L["bonnet_flange"]
    _lathe(B["bonnet"], [(L["bonnet_flange_a"], b0), (L["bonnet_flange_a"], b1)], n, axis)
    dome = list(L["dome"])
    dome[0] = (dome[0][0], dome[0][1] - bury)
    _lathe(B["bonnet"], dome, n, axis)
    h0, h1 = L["hold_down"]
    _lathe(B["bonnet"], [(L["hold_down_a"], h0 - bury), (L["hold_down_a"], h1)], n, axis)
    o0, o1 = L["op_nut"]
    op_a = L["op_nut_r"] * math.cos(math.pi / hf.PENTAGON)
    # a corner toward -Y, the pumper's side
    _lathe(B["op_nut"], [(op_a, o0 - bury), (op_a, o1)], hf.PENTAGON, axis,
           rot=-math.pi / 2.0)

    _nut_ring(B["nuts"], L, "flange_nuts", f1, ya)
    _nut_ring(B["nuts"], L, "upper_nuts", u1, ya)
    # the bonnet's nuts are painted with the bonnet
    _nut_ring(B["bonnet"], L, "bonnet_nuts", b1, ya)

    # --- outlets, caps, lugs, eyes and chains -------------------------------------
    R = L["section_a"]
    ch = L["chain"]
    for key, (dx, dy) in L["outlet_dirs"].items():
        o = L["outlets"]["pumper" if key == "pumper" else "hose"]
        a = Vector((dx, dy, 0.0))
        across = a.cross(UP)
        xf = _outlet_frame((0.0, ya, zo), a)
        nozzle = B["pumper_nozzle" if key == "pumper" else "hose_nozzles"]
        caps = B["pumper_cap" if key == "pumper" else "hose_caps"]
        _lathe(nozzle, [(o["stub_r"], R * 0.5), (o["stub_r"], o["cap0"] + bury)], n, xf)
        _lathe(caps, [(o["cap_r"], o["cap0"]), (o["cap_r"], o["cap1"])], n, xf)
        nut_a = o["nut_r"] * math.cos(math.pi / hf.PENTAGON)
        _lathe(caps, [(nut_a, o["cap1"] - bury), (nut_a, o["tip"])], hf.PENTAGON, xf,
               rot=math.pi / 2.0)
        hw = hf.outlet_hardware(L, key)
        _oriented_box(caps, hw["lug"][0], (a, across, UP), hw["lug"][1])
        _oriented_box(B["barrel"], hw["eye"][0], (a, across, UP), hw["eye"][1])
        links = hw["links"]
        lw, ll, lt = ch["link"][1], ch["link"][0], ch["link"][2]
        for i, (c, t) in enumerate(links):
            t = Vector(t)
            side = t.cross(UP)
            side = side.normalized() if side.length > 1e-6 else across.copy()
            normal = t.cross(side).normalized()
            wide, thin = (side, normal) if i % 2 == 0 else (normal, side)
            _oriented_box(B["chains"], c, (t, wide, thin), (ll / 2.0, lw / 2.0, lt / 2.0))

    # --- objects and materials ----------------------------------------------------
    kind = plan["material"]

    def hexof(c):
        return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c)

    body = materials.make_material(f"M_FireHydrant_body_{hexof(paint['body'])}",
                                   list(paint["body"]), kind)
    top = materials.make_material(f"M_FireHydrant_top_{hexof(paint['top'])}",
                                  list(paint["top"]), kind)
    base = materials.make_material(f"M_FireHydrant_base_{hexof(paint['base'])}",
                                   list(paint["base"]), kind)
    chain = materials.make_material(f"M_FireHydrant_chain_{hexof(paint['chain'])}",
                                    list(paint["chain"]), "metal_bare")
    names = {"collar": ("FireHydrant_Collar", base),
             "barrel": ("FireHydrant_Barrel", body),
             "nuts": ("FireHydrant_Nuts", body),
             "hose_nozzles": ("FireHydrant_HoseNozzles", body),
             "pumper_nozzle": ("FireHydrant_PumperNozzle", body),
             "hose_caps": ("FireHydrant_HoseCaps", top),
             "pumper_cap": ("FireHydrant_PumperCap", top),
             "bonnet": ("FireHydrant_Bonnet", top),
             "op_nut": ("FireHydrant_OperatingNut", top),
             "chains": ("FireHydrant_Chains", chain)}
    objs = []
    for key, bm in B.items():
        name, mat = names[key]
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        geometry.shade_by_angle(bm, 1.0)
        geometry.cube_project_uv(bm, 1.0)
        _wear(bm, rng, wear * (0.5 if key == "chains" else 1.0), ambient, z0)
        obj = geometry.bm_to_object(bm, name, collection, finish=False)
        materials.assign([obj], mat)
        objs.append(obj)

    print(f"[hydrant] scheme={paint['name']} flow={paint['flow']} k={L['k']:.3f} "
          f"hose_stub={L['outlets']['hose']['stub']:.3f} "
          f"pumper_stub={L['outlets']['pumper']['stub']:.3f} "
          f"outlet_z={zo - z0:.3f} above grade")

    return {"objects": objs,
            "collision_boxes": [((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, h / 2.0))],
            "attachments": {"ATT_top": (0.0, ya, h / 2.0),
                            "ATT_pumper": (0.0, ya - L["outlets"]["pumper"]["tip"], zo)}}
