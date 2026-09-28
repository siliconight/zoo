"""snack_gondola recipe: the convenience store's island snack gondola.

Planned in pure Python by `core.snack_gondola_forms` -- the frame, every
shelf, price strip and chip bag, and the bags' printed fronts -- and executed
here. See that module for what the walker asked for and what it measured.

TWO SUBMISSIONS WHATEVER THE LENGTH. Every structural part and price strip
builds with one painted-steel material and carries its colour in its `Wear`
attribute (`geometry.tint_wear`), so `merge.pack_by_material` packs them
into one mesh; every bag is ONE object on ONE painted image
(``M_Snack_<art>``), its puffed front mapped to its brand's tile and every
other face to its brand's colour block.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import snack_gondola_forms as SG


def _bags(prims, art, mat, collection, streams):
    W, H = art["size"]
    cache = {}

    def region(name):
        if name not in cache:
            x0, y0, x1, y1 = art["rects"][name]
            cache[name] = (x0 / W, 1.0 - y1 / H, x1 / W, 1.0 - y0 / H)
        return cache[name]
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    for p in prims:
        vs = [bm.verts.new(v) for v in p["verts"]]
        for f, corners in zip(p["faces"], p["uvs"]):
            face = bm.faces.new([vs[i] for i in f])
            for loop, c in zip(face.loops, corners):
                r = region(c[0])
                if len(c) == 1:                      # a solid block: its centre
                    loop[uv].uv = ((r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0)
                else:
                    loop[uv].uv = (r[0] + (r[2] - r[0]) * c[1], r[1] + (r[3] - r[1]) * c[2])
    bm.normal_update()
    geometry.shade_by_angle(bm, 30.0)
    geometry.wear_colors(bm, streams.stream("snack_bags"), 0.0)
    obj = geometry.bm_to_object(bm, "Snack_Bag", collection, finish=False)
    obj.data.materials.append(mat)
    return obj


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    key, variant = SG.resolve(plan)
    got = SG.plan(w, d, h, key, variant)
    f = got["facts"]
    rng = streams.stream("wear")
    objs = []
    steel = [p for p in got["prims"] if p["mat"] != "bag"]
    for mk in sorted({p["mat"] for p in steel}):
        kind, factor = SG.vertex_tint(mk)
        built = prim_mesh.build([p for p in steel if p["mat"] == mk], collection, plan, rng,
                                {mk: ("M_Snack_steel", list(SG.KIND_BASE[kind]), kind)}, texel=1.0)
        for o in built:
            geometry.tint_wear(o, factor)
        objs.extend(built)
    A = SG.bag_art()
    paint = materials.make_painted_material(
        f"M_Snack_{A['name']}", materials.image_from_png(A["name"], A["canvas"].png()), 0.35)
    objs.append(_bags([p for p in got["prims"] if p["mat"] == "bag"], A, paint, collection, streams))
    print(f"[snack_gondola] bays={f['bays']} shelves={f['shelves']} end_caps={f['end_caps']} "
          f"bags={f['bags']} art={A['name']}")
    return {"objects": objs, "collision_boxes": [f["collision"]], "attachments": {},
            "snack_gondola": {"bays": f["bays"], "bags": f["bags"], "end_caps": f["end_caps"]}}
