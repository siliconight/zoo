"""planter recipe: a lobby's potted plant -- a square planter, its soil, a plant on a stem or two.

Zoo 1.136.0, from the walker's bank comps (the factory's docs/reference/BANK_INTERIOR_COMPS.md, 2026-10-27): plants in
planters by the windows and the counters in comps 1, 4, 5 and 6 -- a ficus or a dracaena in a square pot, the
furniture a lobby keeps green. Minted by `tools/new_species.py`; shaped here.

REFERENCE: the commercial interior planter of the 1980s-90s -- a square, slightly tapered box with a lip, soil a hand
under the lip, and a plant whose crown is a few rounded masses on a bare stem or two (a ficus) or tufts on canes (a
dracaena). The VARIANT is the plant (four): its stems, how many crowns, where they sit.

TWO MATERIALS: the planter (the plan's material) with its lip's shade as colour; and the plant, its soil, stems and
leaves' greens as COLOUR ONLY in the `Wear` vertex colour (`geometry.tint_wear`). Two submissions.

Recipe frame: centre pivot. The module is exactly (w, d, h): the planter's base is the footprint and stands on the
floor, the tallest crown's top is the slot's top.
"""
from __future__ import annotations

import random

from ..bpylayer import geometry, materials

POT_H_FRAC = 0.30        # the planter's height, of the slot's
POT_MAX_H = 0.55
TAPER = 0.85             # the planter's foot, of its top
LIP = 0.025              # the lip's height and how far it stands out
RIM_W = 0.05             # the rim's bars, inward from the footprint
RIM_STEP = 0.003         # the side bars this much lower at the top and higher at the foot than the long ones
SOIL_T = 0.012           # the soil's thickness, down into the pot
SOIL_PROUD = 0.004       # its surface this far above the pot's solid top
STEM_R = 0.018
STEM_ROOT = 0.012        # a stem's foot this far under the soil's surface, under the pot's top too
BURY = 0.006

LIP_RGB = (0.80, 0.78, 0.74)
SOIL_RGB = (0.22, 0.16, 0.10)
STEM_RGB = (0.35, 0.26, 0.16)
LEAF_RGB = ((0.16, 0.36, 0.12), (0.22, 0.44, 0.15), (0.12, 0.30, 0.10))
#: variant -> (stems, crowns a stem): a ficus on one stem, two, a dracaena's three canes, a low bush
PLANTS = ((1, 3), (2, 2), (3, 2), (1, 5))


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    variant = int(plan.get("variant") or (plan.get("params") or {}).get("variant") or 0)
    rng = streams.stream("wear")
    lay = random.Random("planter:%d" % variant)
    z0 = -h / 2.0
    pot_h = min(POT_MAX_H, h * POT_H_FRAC)
    pot_objs, plant_objs = [], []

    def obj(bm, name, rgb, into, bev=0.0):
        o = geometry.bm_to_object(bm, name, collection, bevel=bev, texel=1.2, rng=rng, wear=wear)
        geometry.tint_wear(o, rgb)
        into.append(o)

    # the planter: a tapered square whose solid stops at the soil, its foot TAPER of its top. The first cut capped it
    # with a solid lip the footprint wide, and the soil and the stems' feet were inside it: a block, not a pot.
    soil_z = z0 + pot_h - LIP                       # the soil's surface sits a lip under the rim
    bm = geometry.new_bm()
    verts = geometry.add_box(bm, (0.0, 0.0, (z0 + soil_z) / 2.0), (w - 2.0 * LIP, d - 2.0 * LIP, soil_z - z0))
    for v in verts:
        if v.co.z < (z0 + soil_z) / 2.0:
            v.co.x *= TAPER
            v.co.y *= TAPER
    obj(bm, "Planter_Pot", (1.0, 1.0, 1.0), pot_objs, bevel)
    # the rim: a ring of four bars the footprint wide, overhanging the pot by LIP, its foot a bury into the pot. The
    # side bars run between the long ones, into them by a bury, a few mm lower at top and foot so no two faces share
    # a plane at the corners.
    rz0, rz1 = soil_z - BURY, z0 + pot_h
    bm = geometry.new_bm()
    for s in (-1.0, 1.0):
        geometry.add_box(bm, (0.0, s * (d / 2.0 - RIM_W / 2.0), (rz0 + rz1) / 2.0), (w, RIM_W, rz1 - rz0))
        # its outer face RIM_STEP inside the long bars' ends, which share the footprint's edge
        geometry.add_box(bm, (s * (w / 2.0 - RIM_W / 2.0 - RIM_STEP), 0.0, (rz0 + rz1) / 2.0),
                         (RIM_W, d - 2.0 * RIM_W + 2.0 * BURY, rz1 - rz0 - 2.0 * RIM_STEP))
    obj(bm, "Planter_Lip", LIP_RGB, pot_objs)
    # the soil inside the ring, a hand of earth just proud of the pot's top and into the ring's bars
    bm = geometry.new_bm()
    sz0, sz1 = soil_z - SOIL_T, soil_z + SOIL_PROUD
    # twice a bury into the ring: at one, its edges were the side bars' ends (the census's second reading)
    geometry.add_box(bm, (0.0, 0.0, (sz0 + sz1) / 2.0),
                     (w - 2.0 * RIM_W + 4.0 * BURY, d - 2.0 * RIM_W + 4.0 * BURY, sz1 - sz0))
    obj(bm, "Planter_Soil", SOIL_RGB, plant_objs)
    soil_z = sz1
    # the plant: stems from the soil, crowns on them, the tallest crown's top the slot's top
    stems, crowns = PLANTS[variant % len(PLANTS)]
    top = h / 2.0
    spread = min(w, d) / 2.0 - LIP
    bm_stem, bm_leaf = geometry.new_bm(), geometry.new_bm()
    for s in range(stems):
        sx = (s - (stems - 1) / 2.0) * spread * 0.5 + (lay.random() - 0.5) * 0.05
        sy = (lay.random() - 0.5) * spread * 0.4
        crown_r = min(spread * 1.1, (top - soil_z) * 0.22)
        stem_top = top - crown_r * (1.0 + 0.6 * lay.random() * (s > 0))
        # rooted STEM_ROOT into the soil: at a bury, a stem's foot stood 2 mm under the pot's top (the census's third)
        geometry.add_cylinder(bm_stem, (sx, sy, (soil_z - STEM_ROOT + stem_top) / 2.0), STEM_R,
                              stem_top - soil_z + STEM_ROOT,
                              segments=6)
        for c in range(crowns):
            f = (c + 1.0) / crowns
            cz = soil_z + (stem_top - soil_z) * (0.45 + 0.55 * f)
            cr = crown_r * (0.65 + 0.35 * f)
            ox = (lay.random() - 0.5) * cr * 0.8
            oy = (lay.random() - 0.5) * cr * 0.8
            cx = max(-w / 2.0 + cr, min(w / 2.0 - cr, sx + ox))
            cy = max(-d / 2.0 + cr, min(d / 2.0 - cr, sy + oy))
            cz = min(cz, top - cr)
            verts = geometry.add_ellipsoid(bm_leaf, (cx, cy, cz), (cr, cr, cr * 0.85), u_seg=8, v_seg=5)
            geometry.jitter_verts(verts, rng, cr * 0.12)
    # THE CROWNS FILL THE SLOT AND STAY IN IT: jittered, a lump can stand past the slot or the tallest fall short of
    # its top, and a module is its slot exactly. Lift the crowns until the highest touches the top, then hold every
    # leaf inside the slot's box.
    lv = list(bm_leaf.verts)
    if lv:
        lift = top - max(v.co.z for v in lv)
        for v in lv:
            v.co.z = min(top, v.co.z + lift)
            v.co.x = max(-w / 2.0, min(w / 2.0, v.co.x))
            v.co.y = max(-d / 2.0, min(d / 2.0, v.co.y))
    obj(bm_stem, "Planter_Stems", STEM_RGB, plant_objs)
    o = geometry.bm_to_object(bm_leaf, "Planter_Leaves", collection, bevel=0.0, texel=1.2, rng=rng, wear=wear)
    geometry.tint_wear(o, LEAF_RGB[variant % len(LEAF_RGB)])
    plant_objs.append(o)
    pot = materials.make_material(f"M_Planter_{plan['material']}", plan["color"], plan["material"])
    leaves = materials.make_material("M_Planter_plant", (1.0, 1.0, 1.0), "plastic")
    materials.assign(pot_objs, pot)
    materials.assign(plant_objs, leaves)
    return {"objects": pot_objs + plant_objs,
            # the planter collides; a body brushes through the leaves
            "collision_boxes": [((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, z0 + pot_h))],
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
