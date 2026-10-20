"""hole_kit recipe: the crew's kit beside a hole they broke through (Zoo 1.114.0; the factory's
roadmap 265).

Who made the hole, said by what they left: a blue poly tarp the slot's whole size, a cut-off saw on
it nearest the hole, a toolbag with an extension cord coiled by it, a pry bar along the back, and a
work light on a stand aimed down into the opening. The light is the signal the walker asked for --
diegetic, and it points at the hole -- and it is drawn, not lit: a lamp here would be one more light
on every client for a prop. Every decision is `core.hole_forms.kit_plan`, which is pure and tested.

Local +Y faces the hole: Deli Counter turns the slot so. The tarp is the slot's width and depth and
the lamp head's top is its height, so the bounds are the slot's by construction. The saw, the bag
and the light stand solid -- "if I see collision, I expect collision" -- and the tarp, the cord and
the bar lie under the unassisted step and do not. The slot's bottom is `SKIRT` under the visible
floor, so the tarp sinks that far into it.

Plastic parts share one material, tinted in `Wear` (the tarp blue, the saw orange, the lamp yellow,
the cord orange, the lens white); steel shares another; the bag's canvas and the handles' rubber a
third -- three materials, so three draws for the kit.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials
from ..core import hole_forms as HF


def _rod(bm, p0, p1, r, segments=8):
    """A cylinder from point `p0` to `p1`."""
    from mathutils import Matrix, Vector
    a, b = Vector(p0), Vector(p1)
    axis = b - a
    length = axis.length
    verts = geometry.add_cylinder(bm, (0.0, 0.0, 0.0), r, length, segments=segments)
    rot = Vector((0.0, 0.0, 1.0)).rotation_difference(axis.normalized()).to_matrix().to_4x4()
    m = Matrix.Translation((a + b) / 2.0) @ rot
    for v in verts:
        v.co = m @ v.co
    return verts


def _torus(bm, cx, cy, cz, big, small, u=18, v=6):
    """A ring lying flat, centre (cx, cy, cz)."""
    rows = []
    for i in range(u):
        a = 2.0 * math.pi * i / u
        row = []
        for j in range(v):
            b = 2.0 * math.pi * j / v
            rr = big + small * math.cos(b)
            row.append(bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a),
                                     cz + small * math.sin(b))))
        rows.append(row)
    for i in range(u):
        for j in range(v):
            bm.faces.new((rows[i][j], rows[(i + 1) % u][j], rows[(i + 1) % u][(j + 1) % v],
                          rows[i][(j + 1) % v]))
    return [vv for row in rows for vv in row]


def _turn(verts, cx, cy, yaw):
    geometry.place(verts, (cx, cy, 0.0), rot_z=yaw)


def _bounds(verts):
    xs = [v.co.x for v in verts]
    ys = [v.co.y for v in verts]
    zs = [v.co.z for v in verts]
    return ((min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs)))


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    variant = int(params.get("variant", 0) or 0)
    rng = streams.stream("wear")
    wear, ambient = plan["wear"], plan.get("ambient", 0.0)
    kp = HF.kit_plan(w, d, h, params.get("form", "auto"), variant)
    C = HF.COLOURS
    bms = {}

    def bm_for(key):
        if key not in bms:
            bms[key] = geometry.new_bm()
        return bms[key]

    cboxes = []
    # THE TARP: the slot's width and depth, a fold of it turned back along the far edge
    t = kp["tarp"]["t"]
    geometry.add_box(bm_for("tarp"), (0.0, 0.0, t / 2.0), (w, d, t))
    fold = kp["tarp"]["fold"]
    # A FOLDED DROP CLOTH 12 mm thick, so its layers can stand apart by more than the census's 2 mm:
    # the fold (8 mm) sinks 3 mm into the tarp's top and what stands on the tarp sinks 6 mm -- 3 mm
    # under the fold's underside and 6 mm over the tarp's own
    geometry.add_box(bm_for("tarp"), (0.0, -d / 2.0 + fold / 2.0 + 0.004, t - 0.003 + 0.004),
                     (w - 0.02, fold, 0.008))
    base = t - 0.006

    # THE SAW: housing, arm, blade and its guard, two handles -- in its own frame, nose at +X
    s = kp["saw"]
    r = s["blade_r"]
    parts = []
    parts += geometry.add_box(bm_for("saw"), (-0.06, 0.0, base + 0.10), (0.34, 0.18, 0.20))
    # the arm stands 5 mm proud of the housing's side, so the two faces never share a plane
    parts += geometry.add_box(bm_for("saw"), (0.10, 0.075, base + r), (0.22, 0.04, 0.06))
    blade = geometry.add_cylinder(bm_for("steel"), (0.20, 0.11, base + r), r, 0.004, segments=24,
                                  axis="Y")
    guard = geometry.add_cylinder(bm_for("saw"), (0.20, 0.115, base + r + 0.05), r + 0.015, 0.03,
                                  segments=20, axis="Y")
    # the rear handle's posts and the front bar's two stands sink 5 mm into the housing's top
    grips = []
    # a bar is 6 mm deeper than the posts it joins and the rod stops inside its stands, so no
    # face of one lies on a face of the other
    for gx in (-0.21, -0.15):
        grips += geometry.add_box(bm_for("rubber"), (gx, 0.0, base + 0.255), (0.025, 0.03, 0.12))
    grips += geometry.add_box(bm_for("rubber"), (-0.18, 0.0, base + 0.32), (0.09, 0.036, 0.025))
    for gy in (-0.075, 0.075):
        grips += geometry.add_box(bm_for("rubber"), (0.02, gy, base + 0.23), (0.025, 0.025, 0.07))
    grips += _rod(bm_for("rubber"), (0.02, -0.08, base + 0.262), (0.02, 0.08, base + 0.262), 0.012)
    saw = parts + list(blade) + list(guard) + grips
    _turn(saw, s["cx"], s["cy"], s["yaw"])
    cboxes.append(_bounds(saw))

    # THE BAG and its handles, the cord coiled beside it, the bar along the back
    b = kp["bag"]
    bag = list(geometry.add_box(bm_for("bag"), (0.0, 0.0, base + b["sz"] / 2.0),
                                (b["sx"], b["sy"], b["sz"])))
    # the posts run 8 mm up into the bar and the bar reaches 3 mm past them, each way
    for hx in (-0.09, 0.09):
        bag += geometry.add_box(bm_for("rubber"), (hx, 0.0, base + b["sz"] + 0.040),
                                (0.02, 0.02, 0.086))
    bag += geometry.add_box(bm_for("rubber"), (0.0, 0.0, base + b["sz"] + 0.085), (0.206, 0.026, 0.02))
    _turn(bag, b["cx"], b["cy"], b["yaw"])
    cboxes.append(_bounds(bag))
    # the cord coiled flat: concentric turns, each clear of the next by 3 mm, all on the tarp
    c = kp["coil"]
    for k in range(c["turns"]):
        _torus(bm_for("cord"), c["cx"], c["cy"], base + c["tube"],
               c["r"] - k * (2.0 * c["tube"] + 0.003), c["tube"])
    bar = kp["bar"]
    _rod(bm_for("steel"), (bar["cx"] - bar["len"] / 2.0, bar["cy"], base + bar["r"] - 0.002),
         (bar["cx"] + bar["len"] / 2.0, bar["cy"], base + bar["r"] - 0.002), bar["r"], 8)

    # THE WORK LIGHT: three legs splayed from a hub, a pole, a head tilted at the hole, its top at h
    L = kp["light"]
    hw, hd, hh = L["head"]
    tilt = math.radians(L["tilt_deg"])
    # the head built at the origin, its back on the pole's axis, then tilted toward +Y
    head = list(geometry.add_box(bm_for("lamp"), (0.0, hd / 2.0, 0.0), (hw, hd, hh)))
    # the lens sinks 4 mm into the head, so its back is no face the head's front shares
    lens = list(geometry.add_box(bm_for("lens"), (0.0, hd + 0.002, 0.0), (hw - 0.03, 0.012, hh - 0.03)))
    c_, s_ = math.cos(tilt), math.sin(tilt)
    for v in head + lens:
        y, z = v.co.y, v.co.z
        v.co.y, v.co.z = y * c_ + z * s_, -y * s_ + z * c_
    lift = h - max(v.co.z for v in head + lens)
    for v in head + lens:
        v.co.x += L["cx"]
        v.co.y += L["cy"]
        v.co.z += lift
    # the pole meets the tilted head where the head crosses the pole's own axis: along that line
    # the head reaches down to hh / (2 cos tilt) below its centre, and the pole runs 2 cm into it
    pole_top = lift - hh / (2.0 * c_) + 0.02
    hub_z = 0.30
    light = head + lens
    light += _rod(bm_for("steel"), (L["cx"], L["cy"], hub_z), (L["cx"], L["cy"], pole_top), 0.011)
    for k in range(3):
        a = 2.0 * math.pi * k / 3.0 + 0.4
        foot = (L["cx"] + L["foot"] * math.cos(a), L["cy"] + L["foot"] * math.sin(a), base)
        light += _rod(bm_for("steel"), (L["cx"], L["cy"], hub_z), foot, 0.008, 6)
    cboxes.append(_bounds(light))

    looks = {"tarp": ("plastic", C["tarp"]), "saw": ("plastic", C["saw"]),
             "lamp": ("plastic", C["light"]), "lens": ("plastic", C["lens"]),
             "cord": ("plastic", C["cord"]), "steel": ("metal", C["steel"]),
             "rubber": ("canvas", C["rubber"]), "bag": ("canvas", C["bag"])}
    white = (1.0, 1.0, 1.0)
    # THE BODY is the genome's material: the plastic every coloured part rides on in `Wear`
    body = plan["material"]
    objs = []
    for key in sorted(bms):
        kind, rgb = looks[key]
        # plastic is one material, white, each part's colour in `Wear`; the others are their colour
        obj = geometry.bm_to_object(bms[key], f"HoleKit_{key}", collection,
                                    bevel=0.002 if key in ("saw", "bag", "lamp") else 0.0,
                                    texel=1.5, rng=rng, wear=wear, ambient=ambient)
        if kind == "plastic":
            geometry.tint_wear(obj, rgb)
            mat = materials.make_material(f"M_HoleKit_{body}", white, body)
        elif kind == "canvas":
            # the bag's canvas and the handles' rubber are one dark material, the rubber darker
            geometry.tint_wear(obj, tuple(a / b for a, b in zip(rgb, C["bag"])))
            mat = materials.make_material("M_HoleKit_canvas", C["bag"], "canvas")
        else:
            mat = materials.make_material(f"M_HoleKit_{kind}", rgb, kind)
        materials.assign([obj], mat)
        objs.append(obj)
    print(f"[hole_kit] {w:.2f} x {d:.2f} x {h:.3f} variant={variant} parts={sorted(bms)} "
          f"solids={len(cboxes)}")
    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
