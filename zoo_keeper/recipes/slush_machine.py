"""slush_machine recipe: the convenience store's frozen drink station.

Planned in pure Python by `core.slush_machine_forms` -- the stand, the cup
tubes, the syrup rail, the twin-hopper machine and the glow's art -- and
executed here. See that module for what the walker's references asked for.

THREE SUBMISSIONS WHATEVER THE WIDTH. The opaque parts build with one
painted-metal material, each carrying its colour in its `Wear` attribute
(`geometry.tint_wear`), so `merge.pack_by_material` packs them into one mesh;
the barrels and cup tubes are one see-through material (built under a
placeholder name first: `make_see_through_material` returns any material
already carrying its name, and `prim_mesh.build` makes an opaque one -- Zoo
1.9.0's coffee island measured that as solid glass); and everything that
glows -- topper, mascot panel, instruction panel, flavour strip and the
slush itself -- is ONE object on ONE backlit image, ``M_Slush_<art>_Face``,
which Lux's power cut takes.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import slush_machine_forms as SM


def _kind_material_name(kind):
    return f"M_Slush_{kind}"


def _build_steel_and_glass(prims, plan, rng, collection):
    out = []
    for mk in sorted({p["mat"] for p in prims}):
        kind, factor = SM.vertex_tint(mk)
        mname = _kind_material_name(kind) + ("_build" if kind == "glass" else "")
        # A PART IS NAMED FOR ITS KEY, ``<part>_<key>``, the coffee island's
        # rule: a barrel is glass and a white lid under one part, and two
        # objects of one name came back from Blender as `Slush_Barrel.001`
        mine = [dict(p, part=f"{p['part']}_{mk}") for p in prims if p["mat"] == mk]
        built = prim_mesh.build(mine, collection, plan, rng,
                                {mk: (mname, list(SM.KIND_BASE[kind]), kind)}, texel=1.0)
        if kind == "glass":
            materials.assign(built, materials.make_see_through_material(
                _kind_material_name("glass"), list(SM.KIND_BASE["glass"]), SM.GLASS_OPACITY))
        for o in built:
            geometry.tint_wear(o, factor)
        out.extend(built)
    return out


def _glow(prims, art, mat, collection, streams):
    """Every glowing part as one object: each face corner is ``(region, u,
    v)`` into that rect of the glow image, or ``(region,)`` for its centre.
    White `Wear`, no wear: the art is the light."""
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
                if len(c) == 1:
                    loop[uv].uv = ((r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0)
                else:
                    loop[uv].uv = (r[0] + (r[2] - r[0]) * c[1], r[1] + (r[3] - r[1]) * c[2])
    bm.normal_update()
    # the slush barrels are round and the boxes are not: 30 degrees smooths
    # a 16-sided barrel and keeps every box edge hard
    geometry.shade_by_angle(bm, 30.0)
    geometry.wear_colors(bm, streams.stream("slush_glow"), 0.0)
    obj = geometry.bm_to_object(bm, "Slush_Glow", collection, finish=False)
    obj.data.materials.append(mat)
    return obj


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    key, variant = SM.resolve(plan)
    got = SM.plan(w, d, h, key, variant)
    f = got["facts"]
    rng = streams.stream("wear")
    solid = [p for p in got["prims"] if p["mat"] != "glow"]
    objs = _build_steel_and_glass(solid, plan, rng, collection)
    A = SM.glow_art(w, f["bowls"], f["flavours"], f["rail"], key, variant)
    image = materials.image_from_png(A["name"], A["canvas"].png())
    glow = materials.make_backlit_material(f"M_Slush_{A['name']}_Face", image,
                                           SM.GLOW_EMISSION, SM.GLOW_ALBEDO, smooth=True)
    objs.append(_glow([p for p in got["prims"] if p["mat"] == "glow"], A, glow, collection, streams))
    print(f"[slush_machine] bowls={f['bowls']} flavours={f['flavours']} rail={f['rail']} "
          f"bowl_h={f['bowl_height']:.2f} art={A['name']}")
    return {"objects": objs, "collision_boxes": [f["collision"]], "attachments": {},
            "slush_machine": {"bowls": f["bowls"], "flavours": f["flavours"], "rail": f["rail"],
                              "art": A["name"]}}
