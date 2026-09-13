"""street_tree recipe: a kerb tree in a grate -- trunk, branches, twigs,
leaf clusters, by species.

Roadmap 153, the tree. The walker, 2026-09-13, on the frames of cold run
9032: "trees usually have multiple branches that stem from the trunk and
those branches have twigs and depending on what species of tree
determines how that looks." So this recipe GROWS one: a tapered trunk, a
central leader, primary branches leaving the trunk at the angles the
species sets (`core.tree_forms`), twigs forking off each branch's outer
half, and a small faceted leaf cluster at every branch and twig tip --
the low-poly retro read the walker kept ("the mario64 trees looked nice
in their own retro way"), with the silhouette of a red maple, a pin oak,
a honey locust, a London plane or a callery pear. The genome names the
species (`params.form`); the default is the commonest on a Delco street.

`params.crown = "cards"` keeps the crossed cutout cards of 0.69.2 behind
the param, judged not ready on 9032.

WHAT COLLIDES, AND WHY ONLY THAT. The slot is the crown's footprint
(w x d) by the tree's height, because that is the space the tree takes;
a body walks under a crown and bumps a trunk, so the collision box is the
trunk alone. Lot draws the greybox box at the grate's footprint
(`site_furniture.FOOTPRINT`), never the crown's. Centre pivot like every
module: z runs -h/2 .. +h/2. THE SLOT IS EXACT: after growing, the whole
tree is scaled per axis to (w, d, h), so a form shapes and never sizes,
and Zoo's `fit_*` checks pass by construction.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials
from ..core import tree_forms

TRUNK_D = 0.30
GRATE = 1.2
GRATE_T = 0.03
CARD_T = 0.02
SEG = 6                # cylinder segments for limbs: low poly on purpose


def _limb(bm, a, b, r0, r1):
    """A tapered limb from point ``a`` to ``b`` (radius r0 -> r1): a cylinder
    built along Z, then turned to the segment."""
    ax, ay, az = a
    bx, by, bz = b
    dx, dy, dz = bx - ax, by - ay, bz - az
    length = math.sqrt(dx * dx + dy * dy + dz * dz) or 1e-6
    verts = geometry.add_cylinder(bm, (0.0, 0.0, length / 2.0), r0, length,
                                  segments=SEG, radius_top=r1)
    # rotate +Z onto the segment direction: tilt about Y by the polar angle,
    # then spin about Z by the azimuth
    polar = math.acos(max(-1.0, min(1.0, dz / length)))
    azim = math.atan2(dy, dx)
    cp, sp = math.cos(polar), math.sin(polar)
    ca, sa = math.cos(azim), math.sin(azim)
    for v in verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        # tilt about Y
        x, z = x * cp + z * sp, -x * sp + z * cp
        # spin about Z
        x, y = x * ca - y * sa, x * sa + y * ca
        v.co.x, v.co.y, v.co.z = x + ax, y + ay, z + az
    return verts


def _cluster(bm, centre, size):
    """A faceted leaf mass ``size`` wide and a quarter taller than wide:
    a narrow base widening to a full-width waist, a short full-width
    middle, and a cap narrowing to the top. Measured on the first build:
    two frustums meeting at a waist, as wide as tall, read as flat gems
    from the sidewalk below (the walker's eye is under the crown); the
    middle band and the extra height give the mass a side to see."""
    cx, cy, cz = centre
    s = size
    hh = s * 1.25
    lower = geometry.add_box(bm, (cx, cy, cz - hh * 0.30), (s, s, hh * 0.40))
    geometry.taper_z(lower, 1.0, 0.55)
    middle = geometry.add_box(bm, (cx, cy, cz + hh * 0.0), (s, s, hh * 0.20))
    upper = geometry.add_box(bm, (cx, cy, cz + hh * 0.30), (s, s, hh * 0.40))
    geometry.taper_z(upper, 0.45, 1.0)


def _fit(bm, w, d, h):
    """Scale the built tree per axis so its bounds are exactly (w, d, h),
    centred: the form shaped it, the slot sizes it."""
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    ex, ey, ez = (max(xs) - min(xs)) or 1e-6, (max(ys) - min(ys)) or 1e-6, (max(zs) - min(zs)) or 1e-6
    kx, ky, kz = w / ex, d / ey, h / ez
    cx, cy, cz = (max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0, (max(zs) + min(zs)) / 2.0
    for v in bm.verts:
        v.co.x = (v.co.x - cx) * kx
        v.co.y = (v.co.y - cy) * ky
        v.co.z = (v.co.z - cz) * kz


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    params = plan.get("params", {}) or {}
    objs, cboxes = [], []
    z0 = -h / 2.0

    def part(bm, name, texel=1.2, part_bevel=None, smooth=True, uv_offset=(0.0, 0.0, 0.0)):
        obj = geometry.bm_to_object(
            bm, name, collection, bevel=bevel if part_bevel is None else part_bevel,
            texel=texel, rng=rng, wear=wear, uv_offset=uv_offset,
            **({} if smooth else {"smooth_angle": 0.0}))
        objs.append(obj)
        return obj

    # grate at grade
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + GRATE_T / 2.0),
                     (min(GRATE, w), min(GRATE, d), GRATE_T))
    grate = part(bm, "StreetTree_Grate", part_bevel=0.0)

    style = str(params.get("crown", "volume"))
    if style == "cards":
        # 0.69.2's crossed cutout cards, behind the param (not ready, 9032)
        trunk_top = z0 + h * 0.4
        bm = geometry.new_bm()
        geometry.add_cylinder(bm, (0.0, 0.0, z0 + (trunk_top - z0) / 2.0),
                              TRUNK_D / 2.0, trunk_top - z0, segments=8,
                              radius_top=TRUNK_D * 0.4)
        trunk = part(bm, "StreetTree_Trunk")
        crown_h = h * 0.6
        crown_c = h / 2.0 - crown_h / 2.0
        bm = geometry.new_bm()
        span = max(w, d)
        for k in range(4):
            length = span if k % 2 == 0 else span * math.sqrt(2.0)
            verts = geometry.add_box(bm, (0.0, 0.0, crown_c), (length, CARD_T, crown_h))
            geometry.place(verts, (0.0, 0.0, 0.0), rot_z=math.radians(45.0 * k))
        crown = part(bm, "StreetTree_Crown", texel=1.0, part_bevel=0.0, smooth=False,
                     uv_offset=(0.0, 0.0, -crown_c))
        leaf_kind = "foliage"
        cboxes.append(((-TRUNK_D / 2.0, -TRUNK_D / 2.0, z0),
                       (TRUNK_D / 2.0, TRUNK_D / 2.0, trunk_top)))
    else:
        # GROWN BY SPECIES. The SKELETON is grown in its own proportions,
        # then fitted to the slot per axis (less a cluster's margin), and
        # only then are the leaf clusters placed at the fitted tips -- so
        # the clusters keep their own shape. Fitting the whole tree after
        # the clusters were on it squashed them into plates (the first
        # build: a 12 m skeleton pressed into 6 m).
        f = tree_forms.form(params.get("form"))
        n = int(f["branches"])
        first = z0 + h * f["first_branch"]
        leader_top = z0 + h * f["leader"]
        top = h / 2.0
        r_base, r_first, r_top = TRUNK_D / 2.0, TRUNK_D * 0.36, TRUNK_D * 0.12
        cluster = f["cluster"] * w
        golden = math.radians(137.5)
        spin = rng.random() * 6.2831853
        # limbs as (a, b, r0, r1); tips as (point, cluster size)
        limbs, tips = [], []
        limbs.append(((0.0, 0.0, z0), (0.0, 0.0, first), r_base, r_first))
        limbs.append(((0.0, 0.0, first), (0.0, 0.0, leader_top), r_first, r_top))
        tips.append(((0.0, 0.0, leader_top), cluster * 0.9))
        for k in range(n):
            t_k = k / max(1, n - 1)
            zb = first + (leader_top - first) * t_k * 0.9
            ang = math.radians(tree_forms.branch_angle(f, k, n))
            azim = spin + golden * k
            z01 = (zb - first) / max(1e-6, (top - first))
            reach = (w / 2.0) * f["reach"] * tree_forms.envelope(f, z01)
            horiz = max(0.35 * w, reach)
            length = horiz / max(0.25, math.sin(ang))
            tip = (math.cos(azim) * math.sin(ang) * length,
                   math.sin(azim) * math.sin(ang) * length,
                   zb + math.cos(ang) * length)
            limbs.append(((0.0, 0.0, zb), tip, r_first * 0.8, r_top * 0.8))
            tips.append((tip, cluster * (0.85 + 0.3 * rng.random())))
            for j in range(int(f["twigs"])):
                s = 0.55 + 0.35 * (j + 1) / (f["twigs"] + 1)
                base = (tip[0] * s, tip[1] * s, zb + (tip[2] - zb) * s)
                side = azim + (1 if j % 2 == 0 else -1) * math.radians(50 + 25 * rng.random())
                tl = length * (0.30 + 0.15 * rng.random())
                tang = ang - math.radians(10)
                ttip = (base[0] + math.cos(side) * math.sin(tang) * tl,
                        base[1] + math.sin(side) * math.sin(tang) * tl,
                        base[2] + math.cos(tang) * tl)
                limbs.append((base, ttip, r_top * 0.9, r_top * 0.4))
                tips.append((ttip, cluster * (0.55 + 0.25 * rng.random())))
        # fit the skeleton: the tips' extents to the slot less half a
        # cluster each side, the trunk's base staying on the grate
        xs = [p[0] for p, _c in tips]; ys = [p[1] for p, _c in tips]
        zs = [p[2] for p, _c in tips]
        margin = cluster * 0.5
        ex = max(1e-6, max(xs) - min(xs)); ey = max(1e-6, max(ys) - min(ys))
        ez = max(1e-6, max(zs) - z0)
        kx = (w - 2 * margin) / ex
        ky = (d - 2 * margin) / ey
        kz = (h - margin * 1.2) / ez
        cx, cy = (max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0

        def _fitp(p):
            return ((p[0] - cx) * kx, (p[1] - cy) * ky, z0 + (p[2] - z0) * kz)

        wood = geometry.new_bm()
        for a, b, r0, r1 in limbs:
            _limb(wood, _fitp(a), _fitp(b), r0, r1)
        leaves = geometry.new_bm()
        for p, c in tips:
            q = _fitp(p)
            _cluster(leaves, (q[0], q[1], q[2] + c * 0.2), c)
        # the exact slot: a last per-axis correction of both meshes, small
        # now that the skeleton fits, so a cluster keeps its shape
        xs, ys, zs = [], [], []
        for bmx in (wood, leaves):
            xs += [v.co.x for v in bmx.verts]
            ys += [v.co.y for v in bmx.verts]
            zs += [v.co.z for v in bmx.verts]
        ex = (max(xs) - min(xs)) or 1e-6
        ey = (max(ys) - min(ys)) or 1e-6
        ez = (max(zs) - z0) or 1e-6
        kx, ky, kz = w / ex, d / ey, h / ez
        cx, cy = (max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0
        for bmx in (wood, leaves):
            for v in bmx.verts:
                v.co.x = (v.co.x - cx) * kx
                v.co.y = (v.co.y - cy) * ky
                v.co.z = z0 + (v.co.z - z0) * kz
        trunk_top_z = z0 + (first - z0)
        trunk = part(wood, "StreetTree_Wood", texel=1.5)
        crown = part(leaves, "StreetTree_Crown", texel=0.6, part_bevel=0.0)
        leaf_kind = "vegetation"
        cboxes.append(((-TRUNK_D / 2.0, -TRUNK_D / 2.0, z0),
                       (TRUNK_D / 2.0, TRUNK_D / 2.0, trunk_top_z)))

    bark = materials.make_material(
        f"M_StreetTree_{plan['material']}", plan["color"], plan["material"])
    leaf = materials.make_material(f"M_StreetTree_{leaf_kind}",
                                   [0.30, 0.45, 0.20], leaf_kind)
    iron = materials.make_material("M_StreetTree_metal_bare", [0.2, 0.2, 0.21],
                                   "metal_bare")
    materials.assign([trunk], bark)
    materials.assign([crown], leaf)
    materials.assign([grate], iron)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
