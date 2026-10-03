"""roller_grill recipe: the convenience store's hot dog roller grill.

Planned in pure Python by `core.roller_grill_forms` -- the bun cabinet, the
grill and its rollers, the dogs, the tags, the hood and the painted image --
and executed here. See that module for the references and what was measured.

FOUR SUBMISSIONS WHATEVER THE WIDTH. Every chrome part builds with one
`metal_bare` material and every painted part with one `metal_painted`
material, each part's colour in its `Wear` attribute (`geometry.tint_wear`)
-- a roller's grease is its tint -- so `merge.pack_by_material` packs each
kind into one mesh; the ROLLERS and the DOGS are two turning kinds of their
own (1.55.0, `RG.turn_rates`): each prim carries its axle, `prim_mesh`
writes it into a second UV set and the material's name carries the rate,
for Level Factory's import to turn them; the glass is one see-through
material (built under a placeholder name first: `make_see_through_material` returns any material
already carrying its name); and the buns panel, the control panel and the
tags are ONE object on ONE painted image, ``M_Roller_<art>``. Nothing
glows: a roller grill is lit by the room.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import roller_grill_forms as RG


def _kind_material_name(kind):
    # a turning kind's name carries its axis and rate (1.55.0, `RG.material_name`)
    return RG.material_name(kind)


def _build_solid(prims, plan, rng, collection):
    out = []
    for mk in sorted({p["mat"] for p in prims}):
        # a part is named for its key: two keys under one part came back from
        # Blender as `<part>.001` (the slush machine's first build)
        mine = [dict(p, part=f"{p['part']}_{mk.replace('.', '_')}") for p in prims if p["mat"] == mk]
        if mk == "lamp":
            # the heat lamp's element, a lit face (1.57.0): `prim_mesh` builds
            # an emissive entry with no wear and a white COLOR_0, and the
            # name ends `_Face` so Lux's binder cuts it with the power
            out.extend(prim_mesh.build(mine, collection, plan, rng,
                                       {mk: ("M_Roller_Lamp_Face", list(RG.HEAT_LAMP_RGB),
                                             "emissive", RG.HEAT_LAMP_GLOW)}, texel=1.0))
            continue
        kind, factor = RG.vertex_tint(mk)
        mname = _kind_material_name(kind) + ("_build" if kind == "glass" else "")
        built = prim_mesh.build(mine, collection, plan, rng,
                                {mk: (mname, list(RG.KIND_BASE[kind]), kind)}, texel=1.0)
        if kind == "glass":
            materials.assign(built, materials.make_see_through_material(
                _kind_material_name("glass"), list(RG.KIND_BASE["glass"]), RG.GLASS_OPACITY))
        for o in built:
            geometry.tint_wear(o, factor)
        out.extend(built)
    return out


def _painted(prims, art, mat, collection, streams):
    """Every painted part as one object: a face corner is ``(region, u, v)``
    into that rect of the image, or ``(region,)`` for its centre."""
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
    geometry.shade_by_angle(bm, 1.0)
    geometry.wear_colors(bm, streams.stream("roller_paint"), 0.0)
    obj = geometry.bm_to_object(bm, "Roller_Panel", collection, finish=False)
    obj.data.materials.append(mat)
    return obj


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    variant = RG.resolve(plan)
    got = RG.plan(w, d, h, variant)
    f = got["facts"]
    rng = streams.stream("wear")
    objs = _build_solid([p for p in got["prims"] if p["mat"] != "paint"], plan, rng, collection)
    A = RG.art(w, d, h, variant)
    paint = materials.make_painted_material(
        f"M_Roller_{A['name']}", materials.image_from_png(A["name"], A["canvas"].png()), 0.5,
        smooth=True)
    objs.append(_painted([p for p in got["prims"] if p["mat"] == "paint"], A, paint, collection, streams))
    print(f"[roller_grill] rollers={f['rollers']} columns={f['columns']} kinds={f['kinds']} "
          f"dogs={f['dogs']} buns={f['buns']} art={A['name']}")
    # the heat lamp's marker (1.57.0): an attachment becomes an empty in the
    # GLB, `LuxEmit_heat_lamp`, which the fixture spawner reads by name
    return {"objects": objs, "collision_boxes": [f["collision"]], "attachments": dict(f["attachments"]),
            "roller_grill": {"rollers": f["rollers"], "kinds": f["kinds"], "dogs": f["dogs"],
                             "shelf": f["shelf"], "art": A["name"], "turn": f["turn"],
                             "heat_lamp": f["heat_lamp"]}}
