"""Build a card-shop planner's art quads into one textured object.

Zoo 0.95.0. `display_case` and `pack_wall` both plan ART QUADS -- a single
quad naming a tile in `core.card_art`'s atlas -- and both need the same
thing done with them: paint the atlas, pack it once, and build every quad
into ONE mesh carrying ONE painted material.

ONE MESH AND ONE MATERIAL, and that is the whole reason this file exists
rather than a quad per object. A display case stocked to its caps plans 78
art quads; as separate objects that is 78 draws of two triangles each, on
every client, every frame, and the walker's standing call is performance
over look when the two compete. Joined, the same art is 156 triangles in one
draw. The quads share a material because they share an atlas, which is why
the planners name tiles instead of images.

The material is `materials.make_painted_material` -- paint, not light. A
booster box on a shelf is lit by the room; a backlit one would glow in a
shop with the power cut, which is what `M_*_Face` means downstream and is
not what a cardboard box does.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import card_art as CA


def build_art(prims, collection, plan, streams, name, roughness=None):
    """Build every prim carrying a ``tile`` into one object.

    ``prims`` is the planner's whole list; the art quads are the ones with a
    ``tile``, and the caller keeps the rest for `prim_mesh.build`. Returns
    ``(objects, atlas)`` -- objects is empty when the plan has no art, and
    `atlas` is None with it.
    """
    quads = [p for p in prims if p.get("tile")]
    if not quads:
        return [], None
    tiles = plan.get("_tiles") or {}
    atlas = CA.build_atlas(tiles, name)
    size = atlas["size"]
    image = materials.image_from_png(atlas["name"], atlas["canvas"].png())
    mat = materials.make_painted_material(
        f"M_{name}_{atlas['name']}_Art", image,
        CA.BOX_ROUGHNESS if roughness is None else roughness)

    out = []
    for group, above in ((False, False), (True, True)):
        part = [q for q in quads if bool(q.get("above")) == above]
        if not part:
            continue
        bm = geometry.new_bm()
        uv = bm.loops.layers.uv.new("UVMap")
        for q in part:
            rect = atlas["rects"].get(q["tile"])
            if rect is None:
                raise KeyError(f"{name}: art quad {q['part']} names tile "
                               f"{q['tile']!r}, which the atlas does not hold")
            u0, v0, u1, v1 = CA.uv_rect(rect, size)
            vs = [bm.verts.new(v) for v in q["verts"]]
            for face, corners in zip(q["faces"], q["uvs"]):
                f = bm.faces.new([vs[i] for i in face])
                for loop, c in zip(f.loops, corners):
                    loop[uv].uv = (u0 + (u1 - u0) * c[0], v0 + (v1 - v0) * c[1])
        bm.normal_update()
        geometry.shade_by_angle(bm, 1.0)
        # the art is not grimed and the painted material reads COLOR_0, so a
        # white one is what makes it arrive as painted (the `crt_tv` rule)
        geometry.wear_colors(bm, streams.stream("card_art"), 0.0)
        obj = geometry.bm_to_object(bm, f"{name}_Art" + ("_Above" if above else ""),
                                    collection, finish=False)
        obj.data.materials.append(mat)
        out.append(obj)
    return out, atlas
