"""trash_bags recipe: a heap of filled garbage bags (Zoo 1.93.0, roadmap 219 note 11).

The walker, 2026-10-09: "need filled black garbage bags stacked near the garbage bins". Lot stands
one heap beside each building's dumpster. Every decision is `core.trash_bag_forms`, which is pure
and tested: which bags a heap has, where each sits, and how each is pushed out of its ellipsoid --
pressed flat where it sits, spread at the belly, lumpy, gathered at the top into a neck -- with a
knot and its two ears tied on top.

ONE OBJECT AND ONE MATERIAL, so one draw a heap: the genome's plastic in the style's colour, and
each bag's colour in `Wear` by the bag it belongs to -- mostly black, the odd white kitchen bag or
green contractor bag. The style's colour is white, so every bag lands as `COLOURS` says; a theme
that gives another colour tints the whole heap. Under a skin library the delco plastic pack is
tintable and near white (0.93 mean albedo, Pixelcoat 0.61.0), and the `Wear` multiply is wired on
the textured path too, so the black stays black.

THE SLOT IS EXACT: the heap is built where `heap` puts it and then fitted to the slot's box, so its
outermost bag faces are the slot's faces whatever the lumps did. The collision is the slot's box:
a heap of bags is soft, and a body still does not walk through it.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials
from ..core import trash_bag_forms as TB

#: The knot and its two ears, metres: the bag's own plastic tied off at the neck.
KNOT = (0.034, 0.030, 0.028)
EAR = (0.050, 0.014, 0.034)


def _hex(c):
    return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c[:3])


def build(plan, streams, collection):
    from mathutils import Euler, Vector
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    rng = streams.stream("wear")
    params = plan.get("params") or {}
    variant = int(params.get("variant", 0) or 0)
    bags = TB.heap(w, d, h, variant)

    bm = geometry.new_bm()
    # EACH PIECE'S OWN VERTICES, as `add_ellipsoid` returns them. RETRACTED, kept: the first build
    # took `bm.verts[n0:]` after each ellipsoid as "the ones just made". The sequence is not in
    # creation order after the helper's operators, so the shaping moved the wrong vertices -- a
    # body left unshaped at the origin, a knot spanning half a metre -- and the heap grew blades
    # half a metre long, which the fit to the slot then paid for by shrinking every bag.
    pieces = []                                       # (bag index, its vertices)
    for i, bag in enumerate(bags):
        rot = Euler((math.radians(bag["lean"]), 0.0, math.radians(bag["yaw"])), "XYZ").to_matrix()
        c = Vector(bag["centre"])
        body = list(geometry.add_ellipsoid(bm, (0.0, 0.0, 0.0), bag["radii"], u_seg=14, v_seg=9))
        for v in body:
            v.co = rot @ Vector(TB.shape(tuple(v.co), bag["radii"], bag["seed"])) + c
        # the knot on the neck, and its two ears flared either side of it
        top = rot @ Vector((0.0, 0.0, bag["radii"][2] * 1.12)) + c
        parts = body + list(geometry.add_ellipsoid(bm, tuple(top), KNOT, u_seg=8, v_seg=5))
        for side in (-1.0, 1.0):
            ear = rot @ Vector((side * 0.045, 0.0, bag["radii"][2] * 1.16)) + c
            parts += list(geometry.add_ellipsoid(bm, tuple(ear), EAR, u_seg=8, v_seg=4))
        pieces.append((i, parts))

    # FIT TO THE SLOT: the lumps and the leans move the heap's extent a few centimetres, and the
    # slot is exact. One affine map, so every bag keeps its shape within a few per cent.
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    lo = Vector((min(xs), min(ys), min(zs)))
    span = Vector((max(xs) - lo.x, max(ys) - lo.y, max(zs) - lo.z))
    for v in bm.verts:
        v.co = Vector(((v.co.x - lo.x) / span.x * w - w / 2.0,
                       (v.co.y - lo.y) / span.y * d - d / 2.0,
                       (v.co.z - lo.z) / span.z * h))
    bm.verts.ensure_lookup_table()
    # each corner takes its bag's colour, looked up by where its vertex stands: a table built
    # here, for this heap, after the fit -- not carried between builds
    def _key(co):
        return (round(co[0], 5), round(co[1], 5), round(co[2], 5))

    lut = {_key(v.co): TB.COLOURS[bags[i]["colour"]] for i, parts in pieces for v in parts}
    obj = geometry.bm_to_object(bm, "TrashBags_Heap", collection, bevel=0.0, texel=1.0,
                                rng=rng, wear=0.0)
    mesh = obj.data
    if not geometry.tint_wear_by(obj, lambda co, n: lut.get(_key(co), TB.COLOURS["black"])):
        raise RuntimeError("trash_bags: the heap has no Wear layer, so its colours would not land")
    rgb = list(plan["color"])
    kind = plan["material"]
    plastic = materials.make_material(f"M_TrashBags_{kind}_{_hex(rgb)}", rgb, kind)
    materials.assign([obj], plastic)
    print(f"[trash_bags] {w:.2f} x {d:.2f} x {h:.2f} variant={variant} bags={len(bags)} "
          f"({', '.join(b['colour'] for b in bags)}) {len(mesh.polygons)} faces, 1 material")
    return {"objects": [obj], "collision_boxes": [((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h))],
            "attachments": {}}
