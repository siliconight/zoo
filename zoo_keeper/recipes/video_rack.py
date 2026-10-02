"""video_rack recipe: the video store's tape racks -- wall, island, back room.

Zoo 1.43.0. Planned in pure Python by `core.video_rack_forms` -- the frame,
every shelf, lip, box and genre board, and the art on them -- and executed
here, the snack gondola's way.

TWO SUBMISSIONS WHATEVER THE LENGTH. Every structural part builds with one
painted-steel material and carries its colour in its `Wear` attribute
(`geometry.tint_wear`), so `merge.pack_by_material` packs them into one
mesh; every box and every genre board is ONE object on ONE painted image
(``M_VideoRack_<art>``), its front mapped to its tile and every other face
to its colour block.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import video_rack_forms as VR


def _art(prims, art, mat, collection, streams):
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
    geometry.wear_colors(bm, streams.stream("video_boxes"), 0.0)
    obj = geometry.bm_to_object(bm, "VideoRack_Art", collection, finish=False)
    obj.data.materials.append(mat)
    return obj


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    key, variant, form = VR.resolve(plan)
    got = VR.plan(w, d, h, form, variant, key)
    f = got["facts"]
    rng = streams.stream("wear")
    objs = []
    steel = [p for p in got["prims"] if p["mat"] != "art"]
    for mk in sorted({p["mat"] for p in steel}):
        kind, factor = VR.vertex_tint(mk, f["unit"])
        built = prim_mesh.build([p for p in steel if p["mat"] == mk], collection, plan, rng,
                                {mk: ("M_VideoRack_steel", list(VR.KIND_BASE[kind]), kind)}, texel=1.0)
        for o in built:
            geometry.tint_wear(o, factor)
        objs.extend(built)
    A = VR.rack_art()
    paint = materials.make_painted_material(
        f"M_VideoRack_{A['name']}", materials.image_from_png(A["name"], A["canvas"].png()), 0.45)
    objs.append(_art([p for p in got["prims"] if p["mat"] == "art"], A, paint, collection, streams))
    print(f"[video_rack] form={form} bays={f['bays']} shelves={f['shelves']} tapes={f['tapes']} "
          f"genres={','.join(f['genres'])} art={A['name']}")
    return {"objects": objs, "collision_boxes": [f["collision"]], "attachments": {},
            "video_rack": {"form": form, "bays": f["bays"], "tapes": f["tapes"], "genres": f["genres"]}}
