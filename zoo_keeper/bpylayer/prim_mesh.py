"""Build `core.prims` primitive lists into Blender objects.

One object per ``part`` name, one material per object (the recipe maps each
primitive's ``mat`` key to a material). The vertices and faces are created
exactly as the pure lists give them, so the geometry a unit test measured is
the geometry exported -- `bm_to_object` then applies the usual finish
(bevel on the primitives that ask for it, normals, shading, UVs, wear).

A part mixing materials, or beveled and unbeveled primitives, is split into
one object per (material, bevel): the first keeps ``<part>``, the others are
``<part>_<mat>`` with ``_Detail`` on an unbeveled one. Bevel is a
whole-bmesh operation, and a 3 mm label chamfered at the recipe's 4 mm bevel
would be eaten.
"""
from __future__ import annotations

from . import geometry, materials


def build(prims, collection, plan, rng, mats, texel=1.2, ambient=None):
    """Turn ``prims`` into objects linked to ``collection``.

    ``mats`` maps a primitive's ``mat`` key to ``(name, colour, kind)``,
    or to ``(name, colour, "emissive", strength)`` for a lit surface (0.87.0:
    a rope light, a neon tube, a screen that is on) -- built with
    `materials.make_emissive_material` and painted with no wear and no
    ambient, so its COLOR_0 is white and Level Factory's import leaves its
    albedo alone ("all-white left off"). Name a lit material ``M_*_Face``:
    that suffix is what Lux's emissive binder cuts with the power.
    Returns the list of objects, in first-seen part order.
    """
    bevel = float(plan.get("bevel") or 0.0)
    wear = float(plan.get("wear") or 0.0)
    amb = float(plan.get("ambient") or 0.0) if ambient is None else ambient
    order, groups = [], {}
    for p in prims:
        key = (p["part"], bool(p.get("bevel")) and bevel > 0.0, p["mat"])
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(p)
    names_used = set()
    objs = []
    for part, bev, mat_key in order:
        name = part
        if name in names_used:
            name = f"{part}_{mat_key}" + ("" if bev else "_Detail")
        k = 2
        base = name
        while name in names_used:
            name = f"{base}_{k}"
            k += 1
        names_used.add(name)
        bm = geometry.new_bm()
        for p in groups[(part, bev, mat_key)]:
            vs = [bm.verts.new(v) for v in p["verts"]]
            for f in p["faces"]:
                bm.faces.new([vs[i] for i in f])
        # Faces made with `faces.new` carry a zero normal until this runs,
        # and `geometry.bevel_edges` picks edges by the angle between face
        # normals -- without it nothing was beveled: the first furnace
        # built at exactly its pure pre-bevel count, 372 tris.
        bm.normal_update()
        entry = mats[mat_key]
        lit = len(entry) == 4 and entry[2] == "emissive"
        obj = geometry.bm_to_object(bm, name, collection,
                                    bevel=bevel if (bev and not lit) else 0.0,
                                    texel=texel, rng=rng,
                                    wear=0.0 if lit else wear,
                                    ambient=0.0 if lit else amb)
        if lit:
            mname, colour, _kind, strength = entry
            materials.assign([obj], materials.make_emissive_material(
                mname, colour, strength))
        else:
            mname, colour, kind = entry
            materials.assign([obj], materials.make_material(mname, colour, kind))
        objs.append(obj)
    return objs


def build_stock(plan, streams, collection, regions, host_rgb):
    """The surface stock a host recipe's ``stock`` param asks for, built.

    ``regions`` is ``[(x0, x1, y0, y1, z0, facing, clear, keep_out), ...]``,
    one per bay of the host's top (see `_surface_stock.plan_surface`).
    Returns the objects -- or ``[]`` WITHOUT TOUCHING ``streams`` when the
    flavour is ``none``: a host with no stock draws nothing from a "stock"
    stream, so its geometry and its wear are what they were before stock
    existed.

    THE TEXTURED PATH (0.98.0), which is finding 5 of the card-shop
    reference. A flavour may return ``tiles`` beside its prims, and the
    prims that name one are built through `recipes/_card_atlas.py` into ONE
    mesh carrying ONE painted material -- so a play table's printed
    playmats are one extra draw call for the whole top however many mats
    are on it. `_surface_stock`'s own 0.95.0 docstring recorded the absence
    of this path as the reason a mat shipped as a flat colour.

    A FLAVOUR WITH NO TILES TAKES EXACTLY THE OLD ROAD, and that matters
    more than the new one: `tiles` is empty for office, bar, kitchen,
    vault, storage and bar_dense, the atlas is never built, the "card_art"
    stream is never drawn from, and every one of those hosts ships the
    geometry and the wear it shipped before.
    """
    from ..recipes import _surface_stock
    flavour = (plan.get("params") or {}).get("stock") or "none"
    if flavour == "none":
        return []
    srng = streams.stream("stock")
    prims, mats, tiles = [], {}, {}
    for x0, x1, y0, y1, z0, facing, clear, keep_out in regions:
        got = _surface_stock.plan_surface(srng, flavour, x0, x1, y0, y1, z0,
                                          host_rgb=host_rgb, facing=facing,
                                          clear=clear, keep_out=keep_out)
        prims += got["prims"]
        mats.update(got["materials"])
        tiles.update(got.get("tiles") or {})
    if not prims:
        return []
    table = {k: (f"M_Stock_{k}_{kind}", list(rgb), kind)
             for k, (rgb, kind) in mats.items()}
    solid = [p for p in prims if not p.get("tile")]
    objs = build(solid, collection, dict(plan, bevel=0.0),
                 streams.stream("stock_wear"), table, texel=1.0)
    if tiles:
        from ..core import flat_art as FA
        from ..recipes._card_atlas import build_art
        art, _atlas = build_art(prims, collection,
                                dict(plan, _tiles=tiles), streams, "Stock",
                                roughness=FA.MAT_ROUGHNESS)
        objs += art
    return objs
