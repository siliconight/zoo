"""cash_register recipe: a 1997 till, with the green display lit.

Planned in pure Python by `core.register_forms` -- every face, every digit
and every pixel. Since 1.46.0 (the real look) every face is a quad naming a
tile in the register's one image, so this file builds exactly two objects.

TWO MATERIALS OFF ONE IMAGE, which is `vending_machine`'s split and made for
the same reason:

  * ``M_Register_<art>_Face`` is BACKLIT -- the customer display's green type
    is its own light, and the ``_Face`` suffix is what Lux's emissive binder
    cuts with the building's power. It is a MATERIAL and not a lamp: nothing
    here adds a Light3D, because Compatibility allows 8 lights on one mesh
    and the package this ships into already carries 84;
  * ``M_Register_<art>_Panel`` is PAINTED -- the body, the drawer, the keys,
    the paper and the operator's LCD, which is reflective (dark type on a
    green-grey ground: what the reference shows). `make_backlit_material` at
    strength 0 is not this and was not used for it; see that function.

TWO DRAWS where 1.0.0 was six: the case, the trim, the lock and the paper
were each a flat material of their own. Both materials sample with filtering
(``smooth``), and faces are smoothed only across less than 30 degrees, so a
broken corner still catches its own light.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import register_forms as RF


def _art_object(quads, name, collection, atlas, mat, streams, stream):
    """Build art quads carrying their own UVs into ONE object with ONE
    material. Empty list -> no object, and no draw call for it."""
    if not quads:
        return []
    size = atlas["size"]
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    for q in quads:
        rect = atlas["rects"].get(q["tile"])
        if rect is None:
            raise KeyError(f"cash_register: quad {q['part']} names tile "
                           f"{q['tile']!r}, which the atlas does not hold")
        u0, v0, u1, v1 = RF.uv(rect, size)
        vs = [bm.verts.new(v) for v in q["verts"]]
        for face, corners in zip(q["faces"], q["uvs"]):
            f = bm.faces.new([vs[i] for i in face])
            for loop, c in zip(f.loops, corners):
                loop[uv].uv = (u0 + (u1 - u0) * c[0], v0 + (v1 - v0) * c[1])
    bm.normal_update()
    geometry.shade_by_angle(bm, 30.0)
    # a painted or lit face does not grime, and a white COLOR_0 is what makes
    # it arrive as painted through Level Factory's import (the `crt_tv` rule)
    geometry.wear_colors(bm, streams.stream(stream), 0.0)
    obj = geometry.bm_to_object(bm, name, collection, finish=False)
    materials.assign([obj], mat)
    return [obj]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    module = plan.get("module") or {}
    stem = module.get("stem") or "cash_register"
    price = RF.pick_price(plan, streams)
    # the slot's colour is LINEAR, as every Zoo material's is; the atlas is
    # painted in the 8-bit sRGB it is stored in
    got = RF.plan(w, d, h, params, int(module.get("variant") or 0),
                  price=price, key=stem, rgb=RF.srgb8(plan["color"]))
    prims = got["prims"]

    A = got["art"]
    image = materials.image_from_png(A["name"], A["canvas"].png())
    # `lit` 0 is a register with its plug pulled: the same artwork, no glow.
    # `vending_machine`'s switch, and the tag on the material name is what
    # keeps a lit and an unlit machine from sharing one cached material.
    lit_on = float(params.get("lit", 1)) > 0.0
    tag = A["name"] if lit_on else A["name"] + "_unlit"
    face = materials.make_backlit_material(
        f"M_Register_{tag}_Face", image,
        RF.SCREEN_EMISSION if lit_on else 0.0, RF.SCREEN_ALBEDO, smooth=True)
    panel = materials.make_painted_material(
        f"M_Register_{A['name']}_Panel", image, 0.40, smooth=True)
    objs = _art_object([q for q in prims if q.get("lit")], "Register_Screen",
                       collection, A, face, streams, "register_screen")
    objs += _art_object([q for q in prims if not q.get("lit")], "Register_Art",
                        collection, A, panel, streams, "register_art")

    f = got["facts"]
    print(f"[cash_register] {w:.2f} x {d:.2f} x {h:.2f} price={f['price']} "
          f"digits={f['digits']} cap={f['digit_cap_px']}px "
          f"digit_h={f['digit_h_m'] * 1000:.1f}mm screen={f['screen_m'][0]:.3f}"
          f"x{f['screen_m'][1]:.3f} m art={f['art']} "
          f"{f['tris']} tris of {f['budget']}, 2 materials")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": got["attachments"],
            "register": {"price": f["price"], "digits": f["digits"],
                         "art": f["art"], "tris": f["tris"]}}
