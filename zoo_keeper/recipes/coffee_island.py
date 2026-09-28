"""coffee_island recipe: the convenience store's self-serve coffee island.

Planned in pure Python by `core.coffee_island_forms` -- the island, the
brewer stations, every carafe, the cup and syrup ends and the sign's art --
and executed here. See that module for what the walker's references asked
for and what the layout measured.

FIVE SUBMISSIONS, WHATEVER THE SIZE (Zoo 1.9.0; the service counter's 1.8.0
merge is the reason it is built this way from the start). Every primitive's
``mat`` key belongs to one surface KIND; each kind builds with ONE material,
and each part multiplies its own colour into its `Wear` attribute
(`geometry.tint_wear`), so `merge.pack_by_material` packs a kind into one
mesh: wood, bare steel, plastic. The glass -- carafes and syrup bottles --
is one see-through material; the sign is one painted image on both faces.

A PART IS NAMED FOR ITS KEY, ``<part>_<key>`` (``Coffee_Carafe_lid_decaf``),
because a carafe is glass, coffee, a lid and a handle -- four keys under one
part -- and each is built and tinted on its own. The genome's part name is
the prefix, which is how every report matches them.

The island's top IS the slot's footprint and height, so the module fits its
slot exactly; everything standing on it is returned as ``dressing_objects``,
the rule the counter's register and a desk's monitor already follow.
Collision is the island box.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import coffee_island_forms as CI


def _kind_material_name(kind):
    return f"M_Coffee_{kind}"


def _build_pool(pool, plan, rng, collection):
    """Every primitive in ``pool`` but the sign, one key at a time, each
    part renamed ``<part>_<key>`` and tinted to its key's colour."""
    out = []
    for mk in sorted({p["mat"] for p in pool if p["mat"] != "sign"}):
        kind, factor = CI.vertex_tint(mk)
        prims = [dict(p, part=f"{p['part']}_{mk}") for p in pool if p["mat"] == mk]
        # GLASS IS BUILT UNDER ANOTHER NAME, then given the see-through one.
        # `make_see_through_material` returns any material already carrying
        # its name, and `prim_mesh.build` makes one -- opaque -- for every
        # key it builds. Measured: with both named `M_Coffee_glass` the
        # carafes exported with no alphaMode, solid.
        mname = _kind_material_name(kind) + ("_build" if kind == "glass" else "")
        built = prim_mesh.build(prims, collection, plan, rng,
                                {mk: (mname, list(CI.KIND_BASE[kind]), kind)}, texel=1.0)
        if kind == "glass":
            materials.assign(built, materials.make_see_through_material(
                _kind_material_name("glass"), list(CI.KIND_BASE["glass"]), CI.GLASS_OPACITY))
        for o in built:
            geometry.tint_wear(o, factor)
        out.extend(built)
    return out


def _painted(prims, art, mat, collection, streams):
    """The sign and every brewer's badge as ONE object on ONE painted image:
    each face's corners are ``("art", u, v)`` (the disc), ``("badge", u,
    v)`` (the plaque) or ``("dark",)``, mapped into that region of
    `sign_art`'s raster. Painted, not lit, with a white `Wear` so the
    import leaves the paint alone."""
    W, H = art["size"]

    def region(name):
        x0, y0, x1, y1 = art["rects"][name]
        return (x0 / W, 1.0 - y1 / H, x1 / W, 1.0 - y0 / H)
    rects = {k: region(k) for k in ("art", "badge")}
    d = region("dark")
    dark_uv = ((d[0] + d[2]) / 2.0, (d[1] + d[3]) / 2.0)
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    for p in prims:
        vs = [bm.verts.new(v) for v in p["verts"]]
        for f, corners in zip(p["faces"], p["uvs"]):
            face = bm.faces.new([vs[i] for i in f])
            for loop, c in zip(face.loops, corners):
                if c[0] == "dark":
                    loop[uv].uv = dark_uv
                else:
                    r = rects[c[0]]
                    loop[uv].uv = (r[0] + (r[2] - r[0]) * c[1], r[1] + (r[3] - r[1]) * c[2])
    bm.normal_update()
    geometry.shade_by_angle(bm, 1.0)
    geometry.wear_colors(bm, streams.stream("coffee_sign"), 0.0)
    obj = geometry.bm_to_object(bm, "Coffee_Sign", collection, finish=False)
    obj.data.materials.append(mat)
    return obj


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    key, variant = CI.resolve(plan)
    got = CI.plan(w, d, h, key, variant)
    rng = streams.stream("wear")
    island = _build_pool(got["island"], plan, rng, collection)
    dressing = _build_pool(got["dressing"], plan, rng, collection)

    A = CI.sign_art(variant)
    paint = materials.make_painted_material(
        f"M_Coffee_Sign_{A['name']}", materials.image_from_png(A["name"], A["canvas"].png()), 0.5)
    dressing.append(_painted([p for p in got["dressing"] if p["mat"] == "sign"], A, paint,
                             collection, streams))

    f = got["facts"]
    print(f"[coffee_island] stations={len(f['stations'])} front_row={f['front_row']} "
          f"carafes={f['carafes']} decaf={f['decaf']} sign={A['name']}")
    return {"objects": island + dressing, "dressing_objects": dressing,
            "collision_boxes": [f["collision"]], "attachments": {},
            "coffee_island": {"stations": len(f["stations"]), "carafes": f["carafes"],
                              "decaf": f["decaf"], "sign": A["name"]}}
