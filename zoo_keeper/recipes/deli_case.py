"""deli_case recipe: the corner deli's service case.

Planned in pure Python by `core.deli_case_forms` -- the base and its trim,
the curved glass and the end panes, the top and the tube, the doors behind,
the deck a bay at a time and the logs and blocks on it, and the glow's art --
and executed here. See that module for the brief and what was measured.

THREE SUBMISSIONS WHATEVER THE LENGTH, as the cooler wall's. The enamel,
steel and black parts build with one painted-metal material, each carrying
its colour in its `Wear` attribute (`geometry.tint_wear`), so
`merge.pack_by_material` packs them into one mesh -- the accent band's colour
follows the variant there, not in a material of its own. The glass is one
see-through material (built under a placeholder name first:
`make_see_through_material` returns any material already carrying its name,
and `prim_mesh.build` makes an opaque one). Everything that glows -- the
deck, the tube, every log and block -- is ONE object on ONE backlit image,
``M_DeliCase_<art>_Face``, which Lux's power cut takes.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import deli_case_forms as DC


def _kind_material_name(kind):
    return f"M_DeliCase_{kind}"


def _build_metal_and_glass(prims, plan, rng, collection, variant):
    out = []
    for mk in sorted({p["mat"] for p in prims}):
        kind, factor = DC.vertex_tint(mk, variant)
        mname = _kind_material_name(kind) + ("_build" if kind == "glass" else "")
        built = prim_mesh.build([p for p in prims if p["mat"] == mk], collection, plan, rng,
                                {mk: (mname, list(DC.KIND_BASE[kind]), kind)}, texel=1.0)
        if kind == "glass":
            materials.assign(built, materials.make_see_through_material(
                _kind_material_name("glass"), list(DC.KIND_BASE["glass"]), DC.GLASS_OPACITY))
        for o in built:
            geometry.tint_wear(o, factor)
        out.extend(built)
    return out


def _glow(prims, art, mat, collection, streams):
    """Every glowing part as one object. A face corner is ``("dark",)``,
    ``("solid", region)`` -- that rect's centre, for a casing or the tube --
    or ``(region, u, v)``, mapped into the rect. White `Wear`, no wear: the
    art is the light."""
    W, H = art["size"]
    rects = {}

    def rect(name):
        if name not in rects:
            x0, y0, x1, y1 = art["rects"][name]
            rects[name] = (x0 / W, 1.0 - y1 / H, x1 / W, 1.0 - y0 / H)
        return rects[name]

    def centre(name):
        r = rect(name)
        return ((r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0)
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    for p in prims:
        vs = [bm.verts.new(v) for v in p["verts"]]
        for f, corners in zip(p["faces"], p["uvs"]):
            face = bm.faces.new([vs[i] for i in f])
            for loop, c in zip(face.loops, corners):
                if c[0] == "dark":
                    loop[uv].uv = centre("dark")
                elif c[0] == "solid":
                    loop[uv].uv = centre(c[1])
                else:
                    r = rect(c[0])
                    loop[uv].uv = (r[0] + (r[2] - r[0]) * c[1], r[1] + (r[3] - r[1]) * c[2])
    bm.normal_update()
    geometry.shade_by_angle(bm, 1.0)
    geometry.wear_colors(bm, streams.stream("deli_case_glow"), 0.0)
    obj = geometry.bm_to_object(bm, "DeliCase_Glow", collection, finish=False)
    obj.data.materials.append(mat)
    return obj


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    key, variant = DC.resolve(plan)
    got = DC.plan(w, d, h, key, variant)
    f = got["facts"]
    rng = streams.stream("wear")
    solid = [p for p in got["prims"] if p["mat"] != "glow"]
    objs = _build_metal_and_glass(solid, plan, rng, collection, variant)
    A = DC.glow_art(w, d, h, key, variant)
    image = materials.image_from_png(A["name"], A["canvas"].png())
    glow = materials.make_backlit_material(f"M_DeliCase_{A['name']}_Face", image,
                                           DC.GLOW_EMISSION, DC.GLOW_ALBEDO, smooth=True)
    objs.append(_glow([p for p in got["prims"] if p["mat"] == "glow"], A, glow, collection, streams))
    print(f"[deli_case] {w:.3f} x {d:.2f} x {h:.2f} bays={f['bays']} "
          f"bay_w={f['bay_width']:.3f} tiles={f['tiles']} pieces={len(f['pieces'])} "
          f"art={A['name']}")
    return {"objects": objs, "collision_boxes": [f["collision"]], "attachments": {},
            "deli_case": {"bays": f["bays"], "pieces": f["pieces"], "art": A["name"]}}
